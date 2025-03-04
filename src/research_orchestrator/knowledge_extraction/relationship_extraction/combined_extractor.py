"""
Combined relationship extractor for the Research Orchestration Framework.

This module provides a relationship extractor that combines multiple specialized
extractors to provide comprehensive relationship extraction capabilities.
"""

from typing import List, Dict, Any, Optional, Set, Type
import logging
from collections import defaultdict

from ..entity_recognition.entity import Entity
from .base_extractor import RelationshipExtractor
from .relationship import Relationship, RelationType

logger = logging.getLogger(__name__)


class CombinedRelationshipExtractor(RelationshipExtractor):
    """Relationship extractor that combines multiple specialized extractors.
    
    This extractor delegates relationship extraction to specialized extractors
    and merges their results, resolving conflicts and overlaps.
    """
    
    def __init__(
        self, 
        extractors: List[RelationshipExtractor],
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the Combined Relationship Extractor.
        
        Args:
            extractors: List of specialized extractors to use
            config: Configuration dictionary that can include conflict resolution
                   strategies and relationship prioritization
        """
        # Initialize instance variables
        self.extractors = extractors
        
        # Relationship type priorities for conflict resolution
        # Higher priority types override lower priority types in case of conflicts
        self.type_priorities = {}
        
        # Now call the parent constructor which will call _initialize_from_config
        super().__init__(config)
    
    def _initialize_from_config(self) -> None:
        """Initialize based on configuration."""
        # Set relationship type priorities from config or use defaults
        self.type_priorities = self._get_type_priorities()
    
    def _get_type_priorities(self) -> Dict[RelationType, int]:
        """Get relationship type priorities from configuration or use defaults.
        
        Returns:
            Dictionary mapping relationship types to priority values (higher = more priority)
        """
        # Default priorities (can be overridden in config)
        defaults = {
            # Higher priority for specific relationship types
            RelationType.TRAINED_ON: 100,
            RelationType.EVALUATED_ON: 95,
            RelationType.ACHIEVES: 90,
            RelationType.OUTPERFORMS: 85,
            RelationType.BASED_ON: 80,
            RelationType.IMPLEMENTED_IN: 75,
            RelationType.USES: 70,
            
            # Middle priority for general relationship types
            RelationType.IS_A: 65,
            RelationType.PART_OF: 60,
            RelationType.COMPOSED_OF: 55,
            RelationType.APPLIED_TO: 50,
            
            # Lower priority for scientific relationship types
            RelationType.HYPOTHESIZES: 45,
            RelationType.PROVES: 40,
            RelationType.DISPROVES: 35,
            RelationType.CITES: 30,
            
            # Lowest priority for the unknown type
            RelationType.UNKNOWN: 0
        }
        
        # Override with config values if provided
        config_priorities = self.config.get("type_priorities", {})
        for type_str, priority in config_priorities.items():
            entity_type = RelationType.from_string(type_str)
            defaults[entity_type] = priority
        
        # Fill in any missing relationship types with a default priority of 10
        for rel_type in RelationType:
            if rel_type not in defaults:
                defaults[rel_type] = 10
        
        return defaults
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships using all specialized extractors.
        
        Args:
            text: The text to analyze for relationships
            entities: List of entities to find relationships between
            
        Returns:
            A list of detected relationships, with conflicts resolved
        """
        all_relationships = []
        
        # Extract relationships using each specialized extractor
        for extractor in self.extractors:
            relationships = extractor.extract_relationships(text, entities)
            all_relationships.extend(relationships)
        
        # Resolve conflicts and remove duplicates
        resolved_relationships = self._resolve_conflicts(all_relationships)
        
        # Store the relationships
        self.relationships = resolved_relationships
        
        return resolved_relationships
    
    def _resolve_conflicts(self, relationships: List[Relationship]) -> List[Relationship]:
        """Resolve conflicts between relationships from different extractors.
        
        This method handles the case where different extractors identify
        the same entity pair with different relationship types.
        
        Args:
            relationships: List of relationships from all extractors
            
        Returns:
            List of relationships with conflicts resolved
        """
        if not relationships:
            return []
        
        # Group relationships by source and target entities
        entity_pair_groups: Dict[tuple, List[Relationship]] = defaultdict(list)
        
        for rel in relationships:
            if rel.source and rel.target:
                pair_key = (rel.source.id, rel.target.id)
                entity_pair_groups[pair_key].append(rel)
        
        # Resolve conflicts within each entity pair group
        resolved_relationships = []
        
        for pair, pair_relationships in entity_pair_groups.items():
            if len(pair_relationships) == 1:
                # No conflict for this entity pair
                resolved_relationships.append(pair_relationships[0])
            else:
                # Group by relationship type
                type_groups: Dict[RelationType, List[Relationship]] = defaultdict(list)
                for rel in pair_relationships:
                    type_groups[rel.relation_type].append(rel)
                
                # If only one relationship type, merge relationships
                if len(type_groups) == 1:
                    rel_type = next(iter(type_groups))
                    # Use the relationship with the highest confidence
                    best_rel = max(type_groups[rel_type], key=lambda r: r.confidence)
                    resolved_relationships.append(best_rel)
                else:
                    # Multiple relationship types between the same entities
                    # Resolve based on priority and confidence
                    selected_rels = self._select_best_relationships(type_groups)
                    resolved_relationships.extend(selected_rels)
        
        return resolved_relationships
    
    def _select_best_relationships(
        self, type_groups: Dict[RelationType, List[Relationship]]
    ) -> List[Relationship]:
        """Select the best relationships when multiple types exist for the same entity pair.
        
        Args:
            type_groups: Dictionary mapping relationship types to lists of relationships
            
        Returns:
            List of selected relationships
        """
        selected = []
        
        # Check if any relationship types are compatible
        # Some relationships can coexist (e.g., TRAINED_ON and EVALUATED_ON)
        compatible_types = {
            (RelationType.TRAINED_ON, RelationType.EVALUATED_ON),
            (RelationType.USES, RelationType.IMPLEMENTED_IN),
            (RelationType.IS_A, RelationType.PART_OF),
        }
        
        # Convert to set for easier lookup
        type_set = set(type_groups.keys())
        
        # Check for compatible pairs
        for type1, type2 in compatible_types:
            if type1 in type_set and type2 in type_set:
                # These types can coexist, select the best of each
                best1 = max(type_groups[type1], key=lambda r: r.confidence)
                best2 = max(type_groups[type2], key=lambda r: r.confidence)
                selected.append(best1)
                selected.append(best2)
                
                # Remove these types from further consideration
                type_set.discard(type1)
                type_set.discard(type2)
        
        # For remaining types, select based on priority and confidence
        remaining_types = sorted(
            list(type_set),
            key=lambda t: (self.type_priorities.get(t, 0), max(r.confidence for r in type_groups[t])),
            reverse=True
        )
        
        # Take the highest priority relationship type
        if remaining_types:
            best_type = remaining_types[0]
            best_rel = max(type_groups[best_type], key=lambda r: r.confidence)
            selected.append(best_rel)
            
            # If confidence is low, also include the second-best type if available
            if best_rel.confidence < 0.7 and len(remaining_types) > 1:
                second_type = remaining_types[1]
                second_rel = max(type_groups[second_type], key=lambda r: r.confidence)
                if second_rel.confidence > 0.6:  # Only include if confidence is decent
                    selected.append(second_rel)
        
        return selected
    
    def get_extractor_by_type(self, extractor_type: Type[RelationshipExtractor]) -> Optional[RelationshipExtractor]:
        """Get an extractor instance by its type.
        
        Args:
            extractor_type: The class of the extractor to retrieve
            
        Returns:
            The extractor instance of the specified type, or None if not found
        """
        for extractor in self.extractors:
            if isinstance(extractor, extractor_type):
                return extractor
        return None
    
    def add_extractor(self, extractor: RelationshipExtractor) -> None:
        """Add a new extractor to the combined extractor.
        
        Args:
            extractor: The extractor instance to add
        """
        if extractor not in self.extractors:
            self.extractors.append(extractor)
    
    def filter_relationships_by_source_type(
        self, source_type: EntityType, relationships: Optional[List[Relationship]] = None
    ) -> List[Relationship]:
        """Filter relationships by the source entity type.
        
        Args:
            source_type: Type of source entity to filter for
            relationships: List of relationships to filter (defaults to self.relationships)
            
        Returns:
            Filtered list of relationships
        """
        relationships = relationships or self.relationships
        return [rel for rel in relationships if rel.source and rel.source.type == source_type]
    
    def filter_relationships_by_target_type(
        self, target_type: EntityType, relationships: Optional[List[Relationship]] = None
    ) -> List[Relationship]:
        """Filter relationships by the target entity type.
        
        Args:
            target_type: Type of target entity to filter for
            relationships: List of relationships to filter (defaults to self.relationships)
            
        Returns:
            Filtered list of relationships
        """
        relationships = relationships or self.relationships
        return [rel for rel in relationships if rel.target and rel.target.type == target_type]
    
    def analyze_entity_relationship_network(self) -> Dict[str, Any]:
        """Analyze the network of entities and their relationships.
        
        This method provides statistics and analysis of the relationship network,
        including the most connected entities, relationship type distribution, etc.
        
        Returns:
            Dictionary of analysis results
        """
        if not self.relationships:
            return {"total_relationships": 0}
        
        # Count relationships per entity
        entity_connections = defaultdict(int)
        for rel in self.relationships:
            if rel.source:
                entity_connections[rel.source.id] += 1
            if rel.target:
                entity_connections[rel.target.id] += 1
        
        # Get top connected entities
        top_entities = sorted(
            entity_connections.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10
        
        # Get entity texts for display
        entity_map = {}
        for rel in self.relationships:
            if rel.source:
                entity_map[rel.source.id] = rel.source.text
            if rel.target:
                entity_map[rel.target.id] = rel.target.text
        
        # Count relationship types
        rel_type_counts = defaultdict(int)
        for rel in self.relationships:
            rel_type_counts[str(rel.relation_type)] += 1
        
        # Calculate average confidence
        avg_confidence = sum(rel.confidence for rel in self.relationships) / len(self.relationships)
        
        return {
            "total_relationships": len(self.relationships),
            "unique_entities": len(entity_connections),
            "relationship_types": dict(rel_type_counts),
            "average_confidence": avg_confidence,
            "top_connected_entities": [
                {"id": entity_id, "text": entity_map.get(entity_id, "Unknown"), "connections": count}
                for entity_id, count in top_entities
            ]
        }
    
    def group_relationships_by_source(
        self, relationships: Optional[List[Relationship]] = None
    ) -> Dict[str, List[Relationship]]:
        """Group relationships by their source entity.
        
        Args:
            relationships: List of relationships to group (defaults to self.relationships)
            
        Returns:
            Dictionary mapping source entity IDs to lists of relationships
        """
        relationships = relationships or self.relationships
        grouped = defaultdict(list)
        
        for rel in relationships:
            if rel.source:
                grouped[rel.source.id].append(rel)
        
        return dict(grouped)
    
    def find_connected_entities(
        self, entity: Entity, max_depth: int = 2
    ) -> Dict[int, List[Entity]]:
        """Find entities connected to the given entity within N relationship steps.
        
        Args:
            entity: Starting entity
            max_depth: Maximum relationship path length
            
        Returns:
            Dictionary mapping path length to lists of connected entities
        """
        if not self.relationships:
            return {}
        
        # Track visited entities to avoid cycles
        visited = set([entity.id])
        connected = {i: [] for i in range(1, max_depth + 1)}
        
        def find_neighbors(current_id, depth=1):
            if depth > max_depth:
                return
                
            # Find relationships where current entity is the source
            outgoing = [rel for rel in self.relationships if rel.source and rel.source.id == current_id]
            for rel in outgoing:
                if rel.target and rel.target.id not in visited:
                    connected[depth].append(rel.target)
                    visited.add(rel.target.id)
                    find_neighbors(rel.target.id, depth + 1)
            
            # Find relationships where current entity is the target
            incoming = [rel for rel in self.relationships if rel.target and rel.target.id == current_id]
            for rel in incoming:
                if rel.source and rel.source.id not in visited:
                    connected[depth].append(rel.source)
                    visited.add(rel.source.id)
                    find_neighbors(rel.source.id, depth + 1)
        
        # Start search from the input entity
        find_neighbors(entity.id)
        
        return connected