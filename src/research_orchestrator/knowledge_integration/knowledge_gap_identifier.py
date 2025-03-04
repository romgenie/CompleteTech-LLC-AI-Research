"""
Knowledge Gap Identifier for the Knowledge Graph Integration.

This module provides the KnowledgeGapIdentifier class that analyzes the knowledge graph
to identify gaps, missing information, and research opportunities.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from collections import Counter, defaultdict
import math
import networkx as nx
import json
import os

logger = logging.getLogger(__name__)


class KnowledgeGapIdentifier:
    """
    Analyzes the knowledge graph to identify gaps, missing information, and research opportunities.
    
    This class implements various algorithms to identify different types of knowledge gaps:
    - Isolated nodes without connections
    - Sparse areas in the knowledge graph
    - Missing relationships between related entities
    - Incomplete entity information
    - Research fronts and emerging areas
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the knowledge gap identifier.
        
        Args:
            config: Configuration dictionary for gap identification
        """
        self.config = config or {}
        
        # Configure identification options
        self.min_entity_completeness = self.config.get("min_entity_completeness", 0.7)
        self.min_subgraph_density = self.config.get("min_subgraph_density", 0.3)
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.5)
        self.max_gaps_per_category = self.config.get("max_gaps_per_category", 20)
        
        # Required entity properties for different entity types
        self.required_properties = self.config.get("required_properties", {
            "Model": ["name", "description", "architecture", "parameters"],
            "Dataset": ["name", "description", "size", "domain"],
            "Algorithm": ["name", "description", "complexity", "pseudocode"],
            "Paper": ["title", "authors", "year", "abstract"],
            "Author": ["name", "affiliation"]
        })
        
        # Expected relationship types between entity types
        self.expected_relationships = self.config.get("expected_relationships", [
            {"from": "Model", "to": "Dataset", "types": ["TRAINED_ON", "EVALUATED_ON"]},
            {"from": "Model", "to": "Algorithm", "types": ["IMPLEMENTS", "USES"]},
            {"from": "Paper", "to": "Model", "types": ["INTRODUCES", "DESCRIBES"]},
            {"from": "Paper", "to": "Dataset", "types": ["USES", "INTRODUCES"]},
            {"from": "Paper", "to": "Algorithm", "types": ["INTRODUCES", "DESCRIBES"]},
            {"from": "Paper", "to": "Paper", "types": ["CITES"]}
        ])
        
        # Initialize storage for identified gaps
        self.identified_gaps = []
    
    def identify_gaps(self, 
                     entities: List[Dict[str, Any]], 
                     relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the knowledge graph to identify various types of knowledge gaps.
        
        Args:
            entities: List of entities in the knowledge graph
            relationships: List of relationships in the knowledge graph
            
        Returns:
            Dictionary containing identified knowledge gaps categorized by type
        """
        # Create NetworkX graph for analysis
        G = self._create_graph(entities, relationships)
        
        # Get lookup dictionaries for entities and relationships
        entity_by_id = {entity["id"]: entity for entity in entities}
        
        # Initialize gap categories
        gaps = {
            "isolated_entities": [],
            "incomplete_entities": [],
            "missing_relationships": [],
            "sparse_subgraphs": [],
            "research_fronts": [],
            "summary": {}
        }
        
        # Identify isolated entities
        isolated_entities = self._identify_isolated_entities(G, entity_by_id)
        gaps["isolated_entities"] = isolated_entities[:self.max_gaps_per_category]
        
        # Identify incomplete entities
        incomplete_entities = self._identify_incomplete_entities(entities)
        gaps["incomplete_entities"] = incomplete_entities[:self.max_gaps_per_category]
        
        # Identify missing relationships
        missing_relationships = self._identify_missing_relationships(G, entity_by_id, relationships)
        gaps["missing_relationships"] = missing_relationships[:self.max_gaps_per_category]
        
        # Identify sparse subgraphs
        sparse_subgraphs = self._identify_sparse_subgraphs(G, entity_by_id)
        gaps["sparse_subgraphs"] = sparse_subgraphs[:self.max_gaps_per_category]
        
        # Identify research fronts (emerging areas with recent activity)
        research_fronts = self._identify_research_fronts(G, entity_by_id, relationships)
        gaps["research_fronts"] = research_fronts[:self.max_gaps_per_category]
        
        # Generate gap summary
        gaps["summary"] = {
            "total_gaps": (len(isolated_entities) + len(incomplete_entities) + 
                          len(missing_relationships) + len(sparse_subgraphs) + 
                          len(research_fronts)),
            "isolated_entities_count": len(isolated_entities),
            "incomplete_entities_count": len(incomplete_entities),
            "missing_relationships_count": len(missing_relationships),
            "sparse_subgraphs_count": len(sparse_subgraphs),
            "research_fronts_count": len(research_fronts)
        }
        
        # Store all identified gaps
        self.identified_gaps = (
            isolated_entities + incomplete_entities + missing_relationships + 
            sparse_subgraphs + research_fronts
        )
        
        return gaps
    
    def _create_graph(self, 
                     entities: List[Dict[str, Any]], 
                     relationships: List[Dict[str, Any]]) -> nx.MultiDiGraph:
        """
        Create a NetworkX graph from the entities and relationships.
        
        Args:
            entities: List of entities in the knowledge graph
            relationships: List of relationships in the knowledge graph
            
        Returns:
            NetworkX MultiDiGraph representing the knowledge graph
        """
        # Use MultiDiGraph to allow multiple edges between the same nodes
        G = nx.MultiDiGraph()
        
        # Add entity nodes
        for entity in entities:
            entity_id = entity.get("id")
            if entity_id:
                # Extract basic properties for the node attributes
                name = entity.get("properties", {}).get("name", "Unknown")
                entity_type = None
                if "labels" in entity and entity["labels"]:
                    entity_type = entity["labels"][0]  # Use the first label as the primary type
                
                G.add_node(entity_id, name=name, type=entity_type, entity=entity)
        
        # Add relationship edges
        for relationship in relationships:
            source_id = relationship.get("source_id")
            target_id = relationship.get("target_id")
            rel_type = relationship.get("type")
            
            if source_id and target_id and source_id in G and target_id in G:
                # Add edge with the relationship properties
                G.add_edge(
                    source_id, 
                    target_id, 
                    type=rel_type, 
                    properties=relationship.get("properties", {}),
                    relationship=relationship
                )
        
        return G
    
    def _identify_isolated_entities(self, 
                                   G: nx.MultiDiGraph, 
                                   entity_by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify entities that have no connections to other entities.
        
        Args:
            G: NetworkX graph representing the knowledge graph
            entity_by_id: Dictionary mapping entity IDs to entity data
            
        Returns:
            List of identified isolated entities with gap information
        """
        isolated_entities = []
        
        # Find nodes with degree 0 (no connections)
        for node_id in G.nodes():
            if G.degree(node_id) == 0:
                entity = entity_by_id.get(node_id)
                if entity:
                    entity_name = entity.get("properties", {}).get("name", "Unknown")
                    entity_type = None
                    if "labels" in entity and entity["labels"]:
                        entity_type = entity["labels"][0]
                    
                    # Create gap information
                    gap = {
                        "type": "isolated_entity",
                        "entity_id": node_id,
                        "entity_name": entity_name,
                        "entity_type": entity_type,
                        "confidence": 1.0,  # High confidence for isolated entities
                        "description": f"Entity '{entity_name}' ({entity_type}) has no connections to other entities",
                        "suggestions": [
                            f"Find relationships connecting '{entity_name}' to other entities",
                            f"Research how '{entity_name}' relates to other {entity_type.lower()} entities",
                            f"Consider if '{entity_name}' is relevant to the knowledge domain"
                        ]
                    }
                    
                    isolated_entities.append(gap)
        
        return isolated_entities
    
    def _identify_incomplete_entities(self, 
                                    entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify entities with incomplete information based on their type.
        
        Args:
            entities: List of entities in the knowledge graph
            
        Returns:
            List of identified incomplete entities with gap information
        """
        incomplete_entities = []
        
        for entity in entities:
            entity_id = entity.get("id")
            entity_props = entity.get("properties", {})
            entity_name = entity_props.get("name", "Unknown")
            
            # Determine entity type
            entity_type = None
            if "labels" in entity and entity["labels"]:
                entity_type = entity["labels"][0]
            
            # Skip if no required properties for this entity type
            if not entity_type or entity_type not in self.required_properties:
                continue
            
            # Check for missing required properties
            required_props = self.required_properties[entity_type]
            missing_props = [prop for prop in required_props if prop not in entity_props or not entity_props[prop]]
            
            if missing_props:
                # Calculate completeness score
                completeness = 1 - (len(missing_props) / len(required_props))
                
                # Only flag if completeness is below threshold
                if completeness < self.min_entity_completeness:
                    gap = {
                        "type": "incomplete_entity",
                        "entity_id": entity_id,
                        "entity_name": entity_name,
                        "entity_type": entity_type,
                        "missing_properties": missing_props,
                        "completeness": completeness,
                        "confidence": 0.8,  # High confidence for missing properties
                        "description": f"Entity '{entity_name}' ({entity_type}) is missing required properties: {', '.join(missing_props)}",
                        "suggestions": [
                            f"Complete the {', '.join(missing_props)} information for '{entity_name}'",
                            f"Research {entity_type.lower()} '{entity_name}' to find missing property values",
                            f"Consider if the missing properties are applicable to this specific {entity_type.lower()}"
                        ]
                    }
                    
                    incomplete_entities.append(gap)
        
        # Sort by completeness (lowest first)
        incomplete_entities.sort(key=lambda x: x["completeness"])
        
        return incomplete_entities
    
    def _identify_missing_relationships(self, 
                                      G: nx.MultiDiGraph, 
                                      entity_by_id: Dict[str, Dict[str, Any]],
                                      relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify potential missing relationships between entities based on expected patterns.
        
        Args:
            G: NetworkX graph representing the knowledge graph
            entity_by_id: Dictionary mapping entity IDs to entity data
            relationships: List of existing relationships
            
        Returns:
            List of identified missing relationships with gap information
        """
        missing_relationships = []
        
        # Create lookup for existing relationships
        existing_relationships = set()
        for rel in relationships:
            source_id = rel.get("source_id")
            target_id = rel.get("target_id")
            rel_type = rel.get("type")
            
            if source_id and target_id and rel_type:
                existing_relationships.add((source_id, target_id, rel_type))
        
        # Check for missing expected relationships based on entity types
        for node1 in G.nodes():
            entity1 = entity_by_id.get(node1)
            if not entity1 or "labels" not in entity1 or not entity1["labels"]:
                continue
                
            entity1_type = entity1["labels"][0]
            entity1_name = entity1.get("properties", {}).get("name", "Unknown")
            
            for expected_rel in self.expected_relationships:
                # Skip if this entity type doesn't match the expected source
                if expected_rel["from"] != entity1_type:
                    continue
                    
                # Find all entities of the expected target type
                for node2 in G.nodes():
                    if node1 == node2:
                        continue
                        
                    entity2 = entity_by_id.get(node2)
                    if not entity2 or "labels" not in entity2 or not entity2["labels"]:
                        continue
                        
                    entity2_type = entity2["labels"][0]
                    entity2_name = entity2.get("properties", {}).get("name", "Unknown")
                    
                    # Skip if entity2 doesn't match the expected target type
                    if expected_rel["to"] != entity2_type:
                        continue
                    
                    # Check if any of the expected relationship types exist
                    has_expected_relationship = False
                    for rel_type in expected_rel["types"]:
                        if (node1, node2, rel_type) in existing_relationships:
                            has_expected_relationship = True
                            break
                    
                    # If no expected relationship exists, this could be a gap
                    if not has_expected_relationship:
                        # Calculate relevance score (can be refined with more sophisticated methods)
                        relevance = 0.7  # Default medium-high relevance
                        
                        # If entities are connected by other paths, increase relevance
                        try:
                            paths = list(nx.all_simple_paths(G, node1, node2, cutoff=2))
                            if paths:
                                relevance = min(0.9, relevance + 0.1 * len(paths))
                        except (nx.NetworkXNoPath, nx.NodeNotFound):
                            pass
                        
                        # If entities have similar connections, increase relevance
                        node1_neighbors = set(G.neighbors(node1))
                        node2_neighbors = set(G.neighbors(node2))
                        common_neighbors = node1_neighbors.intersection(node2_neighbors)
                        
                        if common_neighbors:
                            relevance = min(0.95, relevance + 0.05 * len(common_neighbors))
                        
                        # Create gap information
                        gap = {
                            "type": "missing_relationship",
                            "source_id": node1,
                            "source_name": entity1_name,
                            "source_type": entity1_type,
                            "target_id": node2,
                            "target_name": entity2_name,
                            "target_type": entity2_type,
                            "expected_relationship_types": expected_rel["types"],
                            "relevance": relevance,
                            "confidence": relevance,  # Use relevance as confidence
                            "description": f"Missing expected relationship between '{entity1_name}' ({entity1_type}) and '{entity2_name}' ({entity2_type})",
                            "suggestions": [
                                f"Investigate if '{entity1_name}' has a {' or '.join(expected_rel['types']).lower()} relationship with '{entity2_name}'",
                                f"Research connections between {entity1_type.lower()} '{entity1_name}' and {entity2_type.lower()} '{entity2_name}'",
                                f"Check literature for mentions of both '{entity1_name}' and '{entity2_name}' together"
                            ]
                        }
                        
                        missing_relationships.append(gap)
        
        # Sort by relevance (highest first)
        missing_relationships.sort(key=lambda x: x["relevance"], reverse=True)
        
        return missing_relationships
    
    def _identify_sparse_subgraphs(self, 
                                 G: nx.MultiDiGraph, 
                                 entity_by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify sparse areas in the knowledge graph that could benefit from more information.
        
        Args:
            G: NetworkX graph representing the knowledge graph
            entity_by_id: Dictionary mapping entity IDs to entity data
            
        Returns:
            List of identified sparse subgraphs with gap information
        """
        sparse_subgraphs = []
        
        # Find connected components
        components = list(nx.connected_components(G.to_undirected()))
        
        # Only analyze components with at least 3 nodes
        for component in components:
            if len(component) < 3:
                continue
                
            # Create subgraph for this component
            subgraph = G.subgraph(component)
            
            # Calculate density of the subgraph
            num_nodes = subgraph.number_of_nodes()
            num_edges = subgraph.number_of_edges()
            
            # Calculate maximum possible edges in a directed graph
            max_possible_edges = num_nodes * (num_nodes - 1)
            
            if max_possible_edges > 0:
                density = num_edges / max_possible_edges
                
                # Only report subgraphs with density below threshold
                if density < self.min_subgraph_density:
                    # Extract subgraph information
                    entity_types = defaultdict(int)
                    entity_names = []
                    
                    for node_id in subgraph.nodes():
                        entity = entity_by_id.get(node_id)
                        if entity:
                            entity_name = entity.get("properties", {}).get("name", "Unknown")
                            entity_names.append(entity_name)
                            
                            if "labels" in entity and entity["labels"]:
                                entity_type = entity["labels"][0]
                                entity_types[entity_type] += 1
                    
                    # Get the most common entity types in this subgraph
                    dominant_types = [et for et, count in 
                                     sorted(entity_types.items(), key=lambda x: x[1], reverse=True)[:2]]
                    
                    # Create gap information
                    gap = {
                        "type": "sparse_subgraph",
                        "component_size": num_nodes,
                        "node_ids": list(component),
                        "density": density,
                        "entity_types": dict(entity_types),
                        "dominant_types": dominant_types,
                        "sample_entities": entity_names[:5],  # Show up to 5 entity names
                        "confidence": 0.6 * (1 - density),  # Higher confidence for lower density
                        "description": f"Sparse subgraph with {num_nodes} entities primarily of types {', '.join(dominant_types)}, density: {density:.2f}",
                        "suggestions": [
                            f"Research additional connections between entities in this {'/'.join(dominant_types)} cluster",
                            f"Find more detailed relationships between {', '.join(entity_names[:3])} and other entities",
                            f"Explore literature focusing on this specific area to find missing connections"
                        ]
                    }
                    
                    sparse_subgraphs.append(gap)
        
        # Sort by density (lowest first)
        sparse_subgraphs.sort(key=lambda x: x["density"])
        
        return sparse_subgraphs
    
    def _identify_research_fronts(self, 
                                G: nx.MultiDiGraph, 
                                entity_by_id: Dict[str, Dict[str, Any]],
                                relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify potential research fronts (emerging areas) based on patterns in the knowledge graph.
        
        Args:
            G: NetworkX graph representing the knowledge graph
            entity_by_id: Dictionary mapping entity IDs to entity data
            relationships: List of existing relationships
            
        Returns:
            List of identified research fronts with gap information
        """
        research_fronts = []
        
        # Identify papers with recent timestamps
        recent_papers = []
        paper_years = {}
        
        for node_id in G.nodes():
            entity = entity_by_id.get(node_id)
            if entity and "labels" in entity and "Paper" in entity["labels"]:
                # Check for publication year
                year = entity.get("properties", {}).get("year")
                if year:
                    try:
                        year = int(year)
                        paper_years[node_id] = year
                        
                        # Consider papers from the last 3 years as recent
                        current_year = 2025  # Should ideally use the current year dynamically
                        if year >= current_year - 3:
                            recent_papers.append(node_id)
                    except (ValueError, TypeError):
                        pass
        
        # Skip if no recent papers
        if not recent_papers:
            return []
        
        # Find clusters of recent papers with similar topics
        paper_clusters = self._cluster_papers_by_citations(G, recent_papers)
        
        # Analyze each cluster
        for cluster in paper_clusters:
            if len(cluster) < 2:
                continue
                
            # Get entity information for papers in this cluster
            paper_data = []
            paper_topics = []
            paper_titles = []
            
            for paper_id in cluster:
                entity = entity_by_id.get(paper_id)
                if entity:
                    title = entity.get("properties", {}).get("title", "Unknown")
                    paper_titles.append(title)
                    
                    # Extract topics
                    topics = entity.get("properties", {}).get("topics", [])
                    if isinstance(topics, str):
                        topics = [t.strip() for t in topics.split(',')]
                    elif not isinstance(topics, list):
                        topics = []
                    
                    paper_topics.extend(topics)
                    
                    paper_data.append({
                        "id": paper_id,
                        "title": title,
                        "year": paper_years.get(paper_id, 0),
                        "topics": topics
                    })
            
            # Count topic frequencies
            topic_counter = Counter(paper_topics)
            common_topics = [topic for topic, count in topic_counter.most_common(3)]
            
            # Calculate growth rate based on publication years
            years = [paper_years.get(paper_id, 0) for paper_id in cluster]
            growth_rate = 0
            
            if years:
                # Simple growth rate: papers per year in this area
                year_counter = Counter(years)
                most_recent_year = max(years)
                papers_in_recent_year = year_counter.get(most_recent_year, 0)
                papers_in_previous_year = year_counter.get(most_recent_year - 1, 0)
                
                if papers_in_previous_year > 0:
                    growth_rate = papers_in_recent_year / papers_in_previous_year - 1  # As percentage
                else:
                    growth_rate = papers_in_recent_year  # New area
            
            # Create gap information
            gap = {
                "type": "research_front",
                "paper_ids": list(cluster),
                "common_topics": common_topics,
                "paper_count": len(cluster),
                "paper_titles": paper_titles[:5],  # Show up to 5 paper titles
                "growth_rate": growth_rate,
                "confidence": min(0.9, 0.5 + growth_rate/2),  # Higher confidence for higher growth rate
                "description": f"Emerging research area focused on {', '.join(common_topics)} with {len(cluster)} recent papers",
                "suggestions": [
                    f"Investigate the latest developments in {', '.join(common_topics)}",
                    f"Explore connections between papers in this emerging area",
                    f"Track new publications related to these topics",
                    f"Consider potential applications or extensions of this research area"
                ]
            }
            
            research_fronts.append(gap)
        
        # Sort by confidence (highest first)
        research_fronts.sort(key=lambda x: x["confidence"], reverse=True)
        
        return research_fronts
    
    def _cluster_papers_by_citations(self, 
                                   G: nx.MultiDiGraph, 
                                   paper_ids: List[str]) -> List[Set[str]]:
        """
        Cluster papers based on citation patterns and shared references.
        
        Args:
            G: NetworkX graph representing the knowledge graph
            paper_ids: List of paper IDs to cluster
            
        Returns:
            List of paper clusters (sets of paper IDs)
        """
        # Create a similarity graph for papers
        paper_similarity_graph = nx.Graph()
        
        # Add all papers as nodes
        for paper_id in paper_ids:
            paper_similarity_graph.add_node(paper_id)
        
        # Calculate similarity between papers
        for i, paper1 in enumerate(paper_ids):
            for paper2 in paper_ids[i+1:]:
                # Skip self-comparison
                if paper1 == paper2:
                    continue
                
                # Calculate similarity based on shared references
                similarity = self._calculate_paper_similarity(G, paper1, paper2)
                
                # If similarity is above threshold, add an edge
                if similarity > 0.2:  # Adjust threshold as needed
                    paper_similarity_graph.add_edge(paper1, paper2, weight=similarity)
        
        # Find connected components in the similarity graph
        clusters = list(nx.connected_components(paper_similarity_graph))
        
        return clusters
    
    def _calculate_paper_similarity(self, 
                                  G: nx.MultiDiGraph, 
                                  paper1_id: str, 
                                  paper2_id: str) -> float:
        """
        Calculate similarity between two papers based on citation patterns.
        
        Args:
            G: NetworkX graph representing the knowledge graph
            paper1_id: ID of the first paper
            paper2_id: ID of the second paper
            
        Returns:
            Similarity score between 0 and 1
        """
        # Get outgoing edges (papers cited by these papers)
        paper1_citations = set()
        paper2_citations = set()
        
        for _, target, data in G.out_edges(paper1_id, data=True):
            if data.get("type") == "CITES":
                paper1_citations.add(target)
        
        for _, target, data in G.out_edges(paper2_id, data=True):
            if data.get("type") == "CITES":
                paper2_citations.add(target)
        
        # Get incoming edges (papers citing these papers)
        paper1_cited_by = set()
        paper2_cited_by = set()
        
        for source, _, data in G.in_edges(paper1_id, data=True):
            if data.get("type") == "CITES":
                paper1_cited_by.add(source)
        
        for source, _, data in G.in_edges(paper2_id, data=True):
            if data.get("type") == "CITES":
                paper2_cited_by.add(source)
        
        # Calculate Jaccard similarity for both citation directions
        similarity = 0
        
        # Similarity based on shared references
        if paper1_citations or paper2_citations:
            shared_citations = paper1_citations.intersection(paper2_citations)
            citation_similarity = len(shared_citations) / len(paper1_citations.union(paper2_citations)) if paper1_citations.union(paper2_citations) else 0
            similarity += citation_similarity * 0.6  # Weight for shared references
        
        # Similarity based on being cited by the same papers
        if paper1_cited_by or paper2_cited_by:
            shared_cited_by = paper1_cited_by.intersection(paper2_cited_by)
            cited_by_similarity = len(shared_cited_by) / len(paper1_cited_by.union(paper2_cited_by)) if paper1_cited_by.union(paper2_cited_by) else 0
            similarity += cited_by_similarity * 0.4  # Weight for being cited by same papers
        
        return similarity
    
    def get_identified_gaps(self) -> List[Dict[str, Any]]:
        """
        Get all identified knowledge gaps.
        
        Returns:
            List of identified gaps from the last analysis
        """
        return self.identified_gaps
    
    def generate_research_opportunities(self, 
                                      top_n: int = 5, 
                                      min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Generate research opportunities based on identified knowledge gaps.
        
        Args:
            top_n: Number of top opportunities to return
            min_confidence: Minimum confidence threshold for opportunities
            
        Returns:
            List of research opportunities derived from knowledge gaps
        """
        # Filter gaps by confidence
        high_confidence_gaps = [gap for gap in self.identified_gaps 
                               if gap.get("confidence", 0) >= min_confidence]
        
        # Sort by confidence (highest first)
        high_confidence_gaps.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        # Convert gaps to research opportunities
        opportunities = []
        
        for gap in high_confidence_gaps[:top_n]:
            gap_type = gap.get("type", "")
            
            if gap_type == "isolated_entity":
                opportunity = {
                    "title": f"Explore connections for {gap.get('entity_name', 'Unknown')}",
                    "description": f"Research how {gap.get('entity_name', 'Unknown')} ({gap.get('entity_type', 'Entity')}) "
                                  f"relates to other entities in the knowledge graph.",
                    "source_gap": gap.get("description", ""),
                    "priority": gap.get("confidence", 0.5),
                    "topics": [gap.get('entity_type', 'Entity'), gap.get('entity_name', 'Unknown')],
                    "next_steps": gap.get("suggestions", [])
                }
            
            elif gap_type == "incomplete_entity":
                opportunity = {
                    "title": f"Complete information for {gap.get('entity_name', 'Unknown')}",
                    "description": f"Fill in missing details about {gap.get('entity_name', 'Unknown')} "
                                  f"({gap.get('entity_type', 'Entity')}), specifically: "
                                  f"{', '.join(gap.get('missing_properties', []))}.",
                    "source_gap": gap.get("description", ""),
                    "priority": gap.get("confidence", 0.5),
                    "topics": [gap.get('entity_type', 'Entity'), gap.get('entity_name', 'Unknown')],
                    "next_steps": gap.get("suggestions", [])
                }
            
            elif gap_type == "missing_relationship":
                opportunity = {
                    "title": f"Investigate relationship between {gap.get('source_name', 'Unknown')} "
                            f"and {gap.get('target_name', 'Unknown')}",
                    "description": f"Determine if there is a {' or '.join(gap.get('expected_relationship_types', ['relationship']))} "
                                  f"between {gap.get('source_name', 'Unknown')} and {gap.get('target_name', 'Unknown')}.",
                    "source_gap": gap.get("description", ""),
                    "priority": gap.get("confidence", 0.5),
                    "topics": [gap.get('source_type', 'Entity'), gap.get('target_type', 'Entity')],
                    "next_steps": gap.get("suggestions", [])
                }
            
            elif gap_type == "sparse_subgraph":
                opportunity = {
                    "title": f"Explore connections in {'/'.join(gap.get('dominant_types', ['Unknown']))} cluster",
                    "description": f"Research additional relationships within the cluster of "
                                  f"{gap.get('component_size', 0)} entities focused on "
                                  f"{', '.join(gap.get('dominant_types', ['Unknown']))}, "
                                  f"including {', '.join(gap.get('sample_entities', ['Unknown']))}.",
                    "source_gap": gap.get("description", ""),
                    "priority": gap.get("confidence", 0.5),
                    "topics": gap.get('dominant_types', ['Research Area']),
                    "next_steps": gap.get("suggestions", [])
                }
            
            elif gap_type == "research_front":
                opportunity = {
                    "title": f"Investigate emerging area: {', '.join(gap.get('common_topics', ['Unknown']))}",
                    "description": f"Explore the emerging research area focused on "
                                  f"{', '.join(gap.get('common_topics', ['Unknown']))} "
                                  f"with {gap.get('paper_count', 0)} recent publications, "
                                  f"including {', '.join(gap.get('paper_titles', ['Unknown'])[:3])}.",
                    "source_gap": gap.get("description", ""),
                    "priority": gap.get("confidence", 0.5),
                    "topics": gap.get('common_topics', ['Research Area']),
                    "next_steps": gap.get("suggestions", [])
                }
            
            else:
                # Generic opportunity for other gap types
                opportunity = {
                    "title": f"Address knowledge gap: {gap.get('description', 'Unknown gap')}",
                    "description": gap.get("description", ""),
                    "source_gap": gap.get("description", ""),
                    "priority": gap.get("confidence", 0.5),
                    "topics": [],
                    "next_steps": gap.get("suggestions", [])
                }
            
            opportunities.append(opportunity)
        
        return opportunities
    
    def save_gaps_to_file(self, file_path: str) -> None:
        """
        Save identified gaps to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
        """
        gaps_data = {
            "gaps": self.identified_gaps,
            "timestamp": self._get_timestamp(),
            "stats": {
                "total_gaps": len(self.identified_gaps),
                "gap_types": Counter(gap.get("type", "unknown") for gap in self.identified_gaps)
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(gaps_data, f, indent=2)
        
        logger.info(f"Saved {len(self.identified_gaps)} identified gaps to {file_path}")
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp as ISO format string."""
        from datetime import datetime
        return datetime.utcnow().isoformat()