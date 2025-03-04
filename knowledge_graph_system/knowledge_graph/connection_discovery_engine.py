"""
Connection Discovery Engine for finding relationships between entities in the knowledge graph.
"""
from typing import Dict, List, Optional, Set, Tuple, Any
import logging
from pathlib import Path
import json
import itertools

class ConnectionDiscoveryEngine:
    """
    Discovers and analyzes connections between entities in the knowledge graph.
    
    This class provides functionality for identifying potential relationships between
    entities, analyzing connection patterns, and suggesting new connections based on
    various discovery strategies.
    """
    
    def __init__(self, graph_manager, config_path: Optional[Path] = None):
        """
        Initialize the ConnectionDiscoveryEngine with a graph manager and optional configuration.
        
        Args:
            graph_manager: The knowledge graph manager instance
            config_path: Optional path to a configuration file
        """
        self.graph_manager = graph_manager
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.config = {
            'path_max_length': 3,              # Maximum path length for connection discovery
            'similarity_threshold': 0.7,        # Threshold for considering entities similar
            'min_common_connections': 2,        # Minimum common connections for suggesting relationships
            'citation_weight': 1.5,             # Weight multiplier for citation relationships
            'coauthor_weight': 1.2,             # Weight multiplier for co-authorship relationships
            'enable_embeddings': True,          # Whether to use embeddings for similarity
            'enable_citation_analysis': True,   # Whether to analyze citation patterns
            'enable_time_analysis': True        # Whether to analyze temporal patterns
        }
        
        # Load custom configuration if provided
        if config_path:
            self._load_config(config_path)
            
        # Initialize discovery strategies
        self.discovery_strategies = {
            'common_neighbors': self._find_common_neighbors,
            'path_based': self._find_path_based_connections,
            'embedding_similarity': self._find_similar_embeddings,
            'temporal_patterns': self._find_temporal_patterns,
            'citation_patterns': self._find_citation_patterns,
            'attribute_similarity': self._find_attribute_similarities
        }
    
    def _load_config(self, config_path: Path) -> None:
        """
        Load custom configuration for connection discovery.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Update configuration with provided values
            for key, value in config.items():
                if key in self.config:
                    self.config[key] = value
                    
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def discover_connections(
        self, 
        entity_ids: Optional[List[str]] = None, 
        entity_types: Optional[List[str]] = None,
        strategies: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Discover potential connections between entities.
        
        Args:
            entity_ids: Optional list of entity IDs to focus on
            entity_types: Optional list of entity types to focus on
            strategies: Optional list of discovery strategies to use
            limit: Maximum number of connections to return
            
        Returns:
            List of potential connections with metadata
        """
        # Determine which strategies to use
        if strategies is None:
            strategies = list(self.discovery_strategies.keys())
        
        # Validate strategies
        valid_strategies = [s for s in strategies if s in self.discovery_strategies]
        
        # Get entities to analyze
        entities = self._get_entities_for_analysis(entity_ids, entity_types)
        
        # Apply each selected strategy and collect results
        connections = []
        for strategy in valid_strategies:
            strategy_func = self.discovery_strategies[strategy]
            strategy_connections = strategy_func(entities)
            
            for conn in strategy_connections:
                conn['discovery_method'] = strategy
                connections.append(conn)
        
        # Sort by confidence and limit results
        connections.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return connections[:limit]
    
    def _get_entities_for_analysis(
        self, 
        entity_ids: Optional[List[str]], 
        entity_types: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Get entities for connection analysis based on filters.
        
        Args:
            entity_ids: Optional list of entity IDs to focus on
            entity_types: Optional list of entity types to focus on
            
        Returns:
            List of entities for analysis
        """
        if entity_ids:
            # Get specific entities by ID
            entities = []
            for entity_id in entity_ids:
                entity = self.graph_manager.get_entity(entity_id)
                if entity:
                    entities.append(entity)
        elif entity_types:
            # Get entities by type
            entities = []
            for entity_type in entity_types:
                type_entities = self.graph_manager.get_entities_by_type(entity_type)
                entities.extend(type_entities)
        else:
            # Get a sample of entities if no specific filter
            entities = self.graph_manager.get_entities(limit=1000)
        
        return entities
    
    def _find_common_neighbors(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potential connections based on common neighbors.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of potential connections with confidence scores
        """
        connections = []
        
        # Create pairs of entities to analyze
        entity_pairs = list(itertools.combinations(entities, 2))
        
        for entity1, entity2 in entity_pairs:
            # Skip if already directly connected
            if self.graph_manager.check_direct_connection(entity1['id'], entity2['id']):
                continue
                
            # Get neighbors for both entities
            neighbors1 = self.graph_manager.get_neighbors(entity1['id'])
            neighbors2 = self.graph_manager.get_neighbors(entity2['id'])
            
            # Find common neighbors
            neighbor_ids1 = {n['id'] for n in neighbors1}
            neighbor_ids2 = {n['id'] for n in neighbors2}
            common_neighbors = neighbor_ids1.intersection(neighbor_ids2)
            
            # If enough common connections, suggest a relationship
            if len(common_neighbors) >= self.config['min_common_connections']:
                # Calculate confidence score based on proportion of common neighbors
                total_neighbors = len(neighbor_ids1.union(neighbor_ids2))
                confidence = len(common_neighbors) / total_neighbors if total_neighbors > 0 else 0
                
                connections.append({
                    'source_id': entity1['id'],
                    'source_type': entity1.get('type', 'Unknown'),
                    'source_name': entity1.get('name', entity1['id']),
                    'target_id': entity2['id'],
                    'target_type': entity2.get('type', 'Unknown'),
                    'target_name': entity2.get('name', entity2['id']),
                    'relationship_type': 'RELATED_TO',
                    'confidence': confidence,
                    'common_neighbors': list(common_neighbors),
                    'evidence': f"Entities share {len(common_neighbors)} common connections"
                })
        
        return connections
    
    def _find_path_based_connections(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potential connections based on paths between entities.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of potential connections with confidence scores
        """
        connections = []
        max_length = self.config['path_max_length']
        
        # Create pairs of entities to analyze
        entity_pairs = list(itertools.combinations(entities, 2))
        
        for entity1, entity2 in entity_pairs:
            # Skip if already directly connected
            if self.graph_manager.check_direct_connection(entity1['id'], entity2['id']):
                continue
                
            # Find paths between the entities
            paths = self.graph_manager.find_paths(
                entity1['id'], 
                entity2['id'], 
                max_length=max_length
            )
            
            if paths:
                # Calculate confidence based on path length and count
                # Shorter paths and more paths increase confidence
                shortest_path_length = min(len(path) for path in paths)
                path_count = len(paths)
                
                # Higher confidence for shorter paths and more paths
                path_length_factor = 1 / shortest_path_length if shortest_path_length > 0 else 0
                path_count_factor = min(1.0, path_count / 5)  # Cap at 1.0 at 5 paths
                
                confidence = 0.5 * path_length_factor + 0.5 * path_count_factor
                
                # Determine most appropriate relationship type based on paths
                relationship_type = self._infer_relationship_type(paths, entity1['type'], entity2['type'])
                
                connections.append({
                    'source_id': entity1['id'],
                    'source_type': entity1.get('type', 'Unknown'),
                    'source_name': entity1.get('name', entity1['id']),
                    'target_id': entity2['id'],
                    'target_type': entity2.get('type', 'Unknown'),
                    'target_name': entity2.get('name', entity2['id']),
                    'relationship_type': relationship_type,
                    'confidence': confidence,
                    'path_count': path_count,
                    'shortest_path_length': shortest_path_length,
                    'evidence': f"Found {path_count} paths with shortest length {shortest_path_length}"
                })
        
        return connections
    
    def _infer_relationship_type(
        self, 
        paths: List[List[Dict[str, Any]]], 
        source_type: str, 
        target_type: str
    ) -> str:
        """
        Infer the most appropriate relationship type based on paths and entity types.
        
        Args:
            paths: List of paths between entities
            source_type: Type of the source entity
            target_type: Type of the target entity
            
        Returns:
            Inferred relationship type
        """
        # Count relationship types in paths
        relationship_counts = {}
        
        for path in paths:
            for step in path:
                rel_type = step.get('relationship_type')
                if rel_type:
                    relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
        
        # Get most common relationship type in paths
        most_common_rel = max(relationship_counts.items(), key=lambda x: x[1])[0] if relationship_counts else None
        
        # Define type-specific relationships
        type_specific_relationships = {
            ('Paper', 'Paper'): 'CITES',
            ('Paper', 'AIModel'): 'INTRODUCES',
            ('AIModel', 'Dataset'): 'TRAINED_ON',
            ('AIModel', 'AIModel'): 'DERIVED_FROM',
            ('Researcher', 'Paper'): 'AUTHORED',
            ('Researcher', 'AIModel'): 'CREATED',
            ('Algorithm', 'AIModel'): 'IMPLEMENTED_IN',
            ('Task', 'AIModel'): 'ADDRESSED_BY',
            ('Metric', 'AIModel'): 'EVALUATED_BY'
        }
        
        # Check if we have a type-specific relationship
        type_pair = (source_type, target_type)
        if type_pair in type_specific_relationships:
            return type_specific_relationships[type_pair]
        
        # Fallback to most common relationship in paths, or generic RELATED_TO
        return most_common_rel if most_common_rel else 'RELATED_TO'
    
    def _find_similar_embeddings(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potential connections based on embedding similarity.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of potential connections with confidence scores
        """
        # Skip if embeddings disabled
        if not self.config['enable_embeddings']:
            return []
            
        connections = []
        threshold = self.config['similarity_threshold']
        
        # Filter entities that have embeddings
        entities_with_embeddings = [
            entity for entity in entities 
            if 'embedding' in entity and entity['embedding'] is not None
        ]
        
        # Create pairs of entities to analyze
        entity_pairs = list(itertools.combinations(entities_with_embeddings, 2))
        
        for entity1, entity2 in entity_pairs:
            # Skip if already directly connected
            if self.graph_manager.check_direct_connection(entity1['id'], entity2['id']):
                continue
                
            # Calculate embedding similarity
            similarity = self.graph_manager.calculate_embedding_similarity(
                entity1['embedding'], 
                entity2['embedding']
            )
            
            # If similarity above threshold, suggest a relationship
            if similarity >= threshold:
                connections.append({
                    'source_id': entity1['id'],
                    'source_type': entity1.get('type', 'Unknown'),
                    'source_name': entity1.get('name', entity1['id']),
                    'target_id': entity2['id'],
                    'target_type': entity2.get('type', 'Unknown'),
                    'target_name': entity2.get('name', entity2['id']),
                    'relationship_type': 'RELATED_TO',
                    'confidence': similarity,
                    'similarity_score': similarity,
                    'evidence': f"Embedding similarity: {similarity:.2f}"
                })
        
        return connections
    
    def _find_temporal_patterns(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potential connections based on temporal patterns.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of potential connections with confidence scores
        """
        # Skip if time analysis disabled
        if not self.config['enable_time_analysis']:
            return []
            
        connections = []
        
        # Filter entities with timestamp information
        entities_with_time = [
            entity for entity in entities 
            if 'timestamp' in entity and entity['timestamp'] is not None
        ]
        
        # Sort entities by timestamp
        entities_with_time.sort(key=lambda x: x['timestamp'])
        
        # Look for sequences of entities with similar attributes
        for i in range(len(entities_with_time) - 1):
            entity1 = entities_with_time[i]
            
            # Look at subsequent entities within a reasonable time window
            for j in range(i + 1, min(i + 10, len(entities_with_time))):
                entity2 = entities_with_time[j]
                
                # Skip if already directly connected
                if self.graph_manager.check_direct_connection(entity1['id'], entity2['id']):
                    continue
                
                # If same type, look for progression or iteration patterns
                if entity1.get('type') == entity2.get('type'):
                    # Check for naming patterns suggesting iteration (v1 -> v2, etc.)
                    name_similarity = self._check_versioning_pattern(
                        entity1.get('name', ''), 
                        entity2.get('name', '')
                    )
                    
                    if name_similarity > 0:
                        connections.append({
                            'source_id': entity1['id'],
                            'source_type': entity1.get('type', 'Unknown'),
                            'source_name': entity1.get('name', entity1['id']),
                            'target_id': entity2['id'],
                            'target_type': entity2.get('type', 'Unknown'),
                            'target_name': entity2.get('name', entity2['id']),
                            'relationship_type': 'SUCCEEDED_BY',
                            'confidence': name_similarity,
                            'evidence': f"Temporal sequence and naming pattern suggests versioning"
                        })
        
        return connections
    
    def _check_versioning_pattern(self, name1: str, name2: str) -> float:
        """
        Check if two entity names suggest a versioning pattern.
        
        Args:
            name1: Name of the first entity
            name2: Name of the second entity
            
        Returns:
            Confidence score for versioning pattern (0-1)
        """
        import re
        
        # Convert to lowercase for comparison
        name1 = name1.lower()
        name2 = name2.lower()
        
        # Common versioning patterns
        patterns = [
            # v1 -> v2, version 1 -> version 2
            (r'([a-z]+)[\s-]?v(\d+)', r'([a-z]+)[\s-]?v(\d+)'),
            (r'([a-z]+)[\s-]?version[\s-]?(\d+)', r'([a-z]+)[\s-]?version[\s-]?(\d+)'),
            # model1 -> model2
            (r'([a-z]+)(\d+)', r'([a-z]+)(\d+)'),
            # name 2020 -> name 2021 (year patterns)
            (r'([a-z\s]+)[\s-]?(20\d\d)', r'([a-z\s]+)[\s-]?(20\d\d)')
        ]
        
        for pattern1, pattern2 in patterns:
            match1 = re.match(pattern1, name1)
            match2 = re.match(pattern2, name2)
            
            if match1 and match2:
                # Check if base name is the same
                if match1.group(1) == match2.group(1):
                    # Check if version number increased
                    try:
                        version1 = int(match1.group(2))
                        version2 = int(match2.group(2))
                        if version2 > version1:
                            # Higher confidence for sequential versions
                            return 0.9 if version2 == version1 + 1 else 0.7
                    except ValueError:
                        pass
        
        # Check for simple name similarity (base name + different suffix)
        words1 = set(name1.split())
        words2 = set(name2.split())
        common_words = words1.intersection(words2)
        
        if common_words and len(common_words) >= 2:
            similarity = len(common_words) / max(len(words1), len(words2))
            if similarity >= 0.5:
                return 0.5 * similarity
        
        return 0.0
    
    def _find_citation_patterns(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potential connections based on citation patterns.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of potential connections with confidence scores
        """
        # Skip if citation analysis disabled
        if not self.config['enable_citation_analysis']:
            return []
            
        connections = []
        
        # Filter paper entities
        papers = [entity for entity in entities if entity.get('type') == 'Paper']
        
        # Create pairs of papers to analyze
        paper_pairs = list(itertools.combinations(papers, 2))
        
        for paper1, paper2 in paper_pairs:
            # Skip if already directly connected
            if self.graph_manager.check_direct_connection(paper1['id'], paper2['id']):
                continue
                
            # Get citations for both papers
            citations1 = self.graph_manager.get_outgoing_relationships(paper1['id'], 'CITES')
            citations2 = self.graph_manager.get_outgoing_relationships(paper2['id'], 'CITES')
            
            # Find common citations
            cited_by1 = {rel['target_id'] for rel in citations1}
            cited_by2 = {rel['target_id'] for rel in citations2}
            common_citations = cited_by1.intersection(cited_by2)
            
            # If papers cite similar papers, they might be related
            if common_citations:
                # Calculate confidence based on proportion of common citations
                total_citations = len(cited_by1.union(cited_by2))
                proportion = len(common_citations) / total_citations if total_citations > 0 else 0
                confidence = min(0.9, proportion * self.config['citation_weight'])
                
                # Papers with many common citations might be addressing similar topics
                connections.append({
                    'source_id': paper1['id'],
                    'source_type': 'Paper',
                    'source_name': paper1.get('name', paper1['id']),
                    'target_id': paper2['id'],
                    'target_type': 'Paper',
                    'target_name': paper2.get('name', paper2['id']),
                    'relationship_type': 'RELATED_TOPIC',
                    'confidence': confidence,
                    'common_citations': len(common_citations),
                    'evidence': f"Papers share {len(common_citations)} common citations"
                })
                
            # Get citations for both papers (incoming)
            cited_in1 = self.graph_manager.get_incoming_relationships(paper1['id'], 'CITES')
            cited_in2 = self.graph_manager.get_incoming_relationships(paper2['id'], 'CITES')
            
            # Find papers that cite both
            cites1 = {rel['source_id'] for rel in cited_in1}
            cites2 = {rel['source_id'] for rel in cited_in2}
            co_cited_by = cites1.intersection(cites2)
            
            # If papers are co-cited, they might be related
            if co_cited_by:
                total_citers = len(cites1.union(cites2))
                proportion = len(co_cited_by) / total_citers if total_citers > 0 else 0
                confidence = min(0.9, proportion * self.config['citation_weight'])
                
                connections.append({
                    'source_id': paper1['id'],
                    'source_type': 'Paper',
                    'source_name': paper1.get('name', paper1['id']),
                    'target_id': paper2['id'],
                    'target_type': 'Paper',
                    'target_name': paper2.get('name', paper2['id']),
                    'relationship_type': 'RELATED_TOPIC',
                    'confidence': confidence,
                    'co_cited_by': len(co_cited_by),
                    'evidence': f"Papers are co-cited by {len(co_cited_by)} other papers"
                })
        
        return connections
    
    def _find_attribute_similarities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find potential connections based on similar attributes.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of potential connections with confidence scores
        """
        connections = []
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity.get('type', 'Unknown')
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        # Analyze entities of the same type
        for entity_type, type_entities in entities_by_type.items():
            # Create pairs of entities to analyze
            entity_pairs = list(itertools.combinations(type_entities, 2))
            
            for entity1, entity2 in entity_pairs:
                # Skip if already directly connected
                if self.graph_manager.check_direct_connection(entity1['id'], entity2['id']):
                    continue
                
                # Calculate attribute similarity
                similarity_score, matching_attrs = self._calculate_attribute_similarity(entity1, entity2)
                
                if similarity_score >= self.config['similarity_threshold']:
                    # Relationship type depends on entity type
                    relationship_type = self._get_relationship_for_similar_entities(entity_type)
                    
                    connections.append({
                        'source_id': entity1['id'],
                        'source_type': entity_type,
                        'source_name': entity1.get('name', entity1['id']),
                        'target_id': entity2['id'],
                        'target_type': entity_type,
                        'target_name': entity2.get('name', entity2['id']),
                        'relationship_type': relationship_type,
                        'confidence': similarity_score,
                        'matching_attributes': matching_attrs,
                        'evidence': f"Entities share similar attributes: {', '.join(matching_attrs)}"
                    })
        
        return connections
    
    def _calculate_attribute_similarity(
        self, 
        entity1: Dict[str, Any], 
        entity2: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """
        Calculate similarity between entities based on their attributes.
        
        Args:
            entity1: First entity
            entity2: Second entity
            
        Returns:
            Tuple of (similarity_score, list_of_matching_attributes)
        """
        # Important attributes to compare (type-specific)
        entity_type = entity1.get('type', 'Unknown')
        
        # Define key attributes by entity type
        key_attributes = {
            'Paper': ['keywords', 'domain', 'journal', 'year', 'abstract'],
            'AIModel': ['architecture', 'tasks', 'datasets', 'framework'],
            'Dataset': ['domain', 'task_type', 'size', 'features'],
            'Researcher': ['institutions', 'research_areas', 'keywords'],
            'Algorithm': ['complexity', 'approach', 'tasks'],
            'Concept': ['domain', 'related_terms']
        }
        
        # Use default attributes if type not recognized
        attributes_to_check = key_attributes.get(
            entity_type, 
            ['name', 'description', 'tags', 'keywords']
        )
        
        matching_attributes = []
        total_matches = 0
        total_comparisons = 0
        
        for attr in attributes_to_check:
            if attr in entity1 and attr in entity2:
                attr1 = entity1[attr]
                attr2 = entity2[attr]
                
                # Handle different attribute types
                if isinstance(attr1, list) and isinstance(attr2, list):
                    # List attributes - check overlap
                    set1 = set(attr1)
                    set2 = set(attr2)
                    if set1 and set2:  # Non-empty sets
                        overlap = len(set1.intersection(set2))
                        total = len(set1.union(set2))
                        if overlap > 0:
                            match_score = overlap / total
                            total_matches += match_score
                            matching_attributes.append(attr)
                        total_comparisons += 1
                        
                elif isinstance(attr1, str) and isinstance(attr2, str):
                    # String attributes - check basic similarity
                    if attr1 and attr2:  # Non-empty strings
                        # Simple string similarity
                        words1 = set(attr1.lower().split())
                        words2 = set(attr2.lower().split())
                        if words1 and words2:
                            overlap = len(words1.intersection(words2))
                            total = len(words1.union(words2))
                            if overlap > 0:
                                match_score = overlap / total
                                total_matches += match_score
                                matching_attributes.append(attr)
                            total_comparisons += 1
                            
                elif attr1 == attr2:
                    # Direct equality for other types
                    total_matches += 1
                    matching_attributes.append(attr)
                    total_comparisons += 1
        
        # Calculate overall similarity score
        similarity_score = total_matches / total_comparisons if total_comparisons > 0 else 0
        
        return similarity_score, matching_attributes
    
    def _get_relationship_for_similar_entities(self, entity_type: str) -> str:
        """
        Get appropriate relationship type for similar entities of a given type.
        
        Args:
            entity_type: Type of entities
            
        Returns:
            Relationship type
        """
        # Define appropriate relationships by entity type
        relationships = {
            'Paper': 'RELATED_RESEARCH',
            'AIModel': 'SIMILAR_ARCHITECTURE',
            'Dataset': 'SIMILAR_DATASET',
            'Researcher': 'POTENTIAL_COLLABORATOR',
            'Algorithm': 'RELATED_ALGORITHM',
            'Concept': 'RELATED_CONCEPT'
        }
        
        return relationships.get(entity_type, 'RELATED_TO')
    
    def suggest_new_connections(
        self, 
        limit: int = 10, 
        min_confidence: float = 0.6, 
        exclude_existing: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Suggest new connections to add to the knowledge graph.
        
        Args:
            limit: Maximum number of suggestions to return
            min_confidence: Minimum confidence threshold for suggestions
            exclude_existing: Whether to exclude suggestions that already exist as relationships
            
        Returns:
            List of connection suggestions
        """
        # Get a sample of entities from the graph
        entities = self.graph_manager.get_entities(limit=300)
        
        # Discover potential connections
        connections = self.discover_connections(entities=entities)
        
        # Filter by confidence
        high_confidence = [
            conn for conn in connections 
            if conn.get('confidence', 0) >= min_confidence
        ]
        
        # Filter out existing connections if requested
        if exclude_existing:
            filtered_connections = []
            for conn in high_confidence:
                source_id = conn['source_id']
                target_id = conn['target_id']
                
                # Check if relationship already exists
                if not self.graph_manager.check_direct_connection(source_id, target_id):
                    filtered_connections.append(conn)
            
            high_confidence = filtered_connections
        
        # Sort by confidence and return top suggestions
        high_confidence.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return high_confidence[:limit]
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about connections in the knowledge graph.
        
        Returns:
            Dictionary of connection statistics
        """
        stats = {}
        
        # Get total entity and relationship counts
        stats['total_entities'] = self.graph_manager.count_entities()
        stats['total_relationships'] = self.graph_manager.count_relationships()
        
        # Get counts by entity type
        entity_type_counts = self.graph_manager.count_entities_by_type()
        stats['entity_type_counts'] = entity_type_counts
        
        # Get counts by relationship type
        relationship_type_counts = self.graph_manager.count_relationships_by_type()
        stats['relationship_type_counts'] = relationship_type_counts
        
        # Calculate connectivity metrics
        stats['avg_connections_per_entity'] = (
            stats['total_relationships'] / stats['total_entities']
            if stats['total_entities'] > 0 else 0
        )
        
        # Calculate type-specific connectivity
        type_connectivity = {}
        for entity_type in entity_type_counts:
            outgoing = self.graph_manager.count_outgoing_relationships_by_type(entity_type)
            incoming = self.graph_manager.count_incoming_relationships_by_type(entity_type)
            
            type_connectivity[entity_type] = {
                'outgoing': outgoing,
                'incoming': incoming,
                'total': sum(outgoing.values()) + sum(incoming.values()),
                'avg_per_entity': (
                    (sum(outgoing.values()) + sum(incoming.values())) / 
                    entity_type_counts[entity_type]
                    if entity_type_counts[entity_type] > 0 else 0
                )
            }
        
        stats['type_connectivity'] = type_connectivity
        
        return stats