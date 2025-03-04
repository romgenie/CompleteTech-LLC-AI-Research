"""
Base relationship extractor class for the Research Orchestration Framework.

This module provides an abstract base class for relationship extractors that can
identify relationships between entities in research documents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set, Tuple, Iterator
import logging
from collections import defaultdict
import copy

from ..entity_recognition.entity import Entity
from .relationship import Relationship, RelationType

logger = logging.getLogger(__name__)


class RelationshipExtractor(ABC):
    """Abstract base class for relationship extractors.
    
    This class defines the interface for all relationship extractors and provides
    common functionality for relationship handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the relationship extractor with optional configuration.
        
        Args:
            config: Configuration dictionary for the extractor
        """
        self.config = config or {}
        self.relationships: List[Relationship] = []
        self._initialize_from_config()
    
    def _initialize_from_config(self) -> None:
        """Initialize the extractor based on configuration."""
        # Default implementation does nothing, to be overridden by subclasses
        pass
    
    @abstractmethod
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships between entities in the provided text.
        
        Args:
            text: The text to analyze for relationships
            entities: List of entities to find relationships between
            
        Returns:
            A list of detected relationships
        """
        pass
    
    def filter_relationships(
        self, 
        relationships: List[Relationship], 
        min_confidence: float = 0.0,
        relation_types: Optional[Set[RelationType]] = None
    ) -> List[Relationship]:
        """Filter relationships based on confidence score and type.
        
        Args:
            relationships: List of relationships to filter
            min_confidence: Minimum confidence threshold (0.0-1.0)
            relation_types: Set of relationship types to include (None for all)
            
        Returns:
            Filtered list of relationships
        """
        filtered = relationships
        
        # Filter by confidence
        if min_confidence > 0.0:
            filtered = [r for r in filtered if r.confidence >= min_confidence]
        
        # Filter by relationship type
        if relation_types:
            filtered = [r for r in filtered if r.relation_type in relation_types]
        
        return filtered
    
    def group_relationships_by_type(
        self, relationships: List[Relationship]
    ) -> Dict[RelationType, List[Relationship]]:
        """Group relationships by their type.
        
        Args:
            relationships: List of relationships to group
            
        Returns:
            Dictionary mapping relationship types to lists of relationships
        """
        grouped = defaultdict(list)
        for relationship in relationships:
            grouped[relationship.relation_type].append(relationship)
        return dict(grouped)
    
    def find_entity_pairs(
        self, 
        entities: List[Entity], 
        max_distance: Optional[int] = None
    ) -> List[Tuple[Entity, Entity]]:
        """Find potential entity pairs for relationship extraction.
        
        This method identifies pairs of entities that might have a relationship
        based on their proximity in the text.
        
        Args:
            entities: List of entities to pair
            max_distance: Maximum token distance between entities (optional)
            
        Returns:
            List of entity pairs (source, target)
        """
        # Remove entities without position information
        positioned_entities = [
            e for e in entities 
            if e.start_pos is not None and e.end_pos is not None
        ]
        
        # Sort entities by their position in the text
        sorted_entities = sorted(
            positioned_entities, 
            key=lambda e: e.start_pos
        )
        
        pairs = []
        
        # Create pairs of entities
        for i, entity1 in enumerate(sorted_entities):
            for j in range(i + 1, len(sorted_entities)):
                entity2 = sorted_entities[j]
                
                # Skip if too far apart
                if max_distance is not None:
                    distance = entity2.start_pos - entity1.end_pos
                    if distance > max_distance:
                        continue
                
                # Create pairs in both directions
                pairs.append((entity1, entity2))
                pairs.append((entity2, entity1))
        
        return pairs
    
    def get_entity_pair_context(
        self, 
        text: str, 
        entity1: Entity, 
        entity2: Entity, 
        window_size: int = 100
    ) -> str:
        """Get the surrounding context between two entities in the text.
        
        Args:
            text: The full text
            entity1: First entity
            entity2: Second entity
            window_size: Additional context to include before and after (characters)
            
        Returns:
            Text context surrounding the entity pair
        """
        # Ensure entities have position information
        if entity1.start_pos is None or entity1.end_pos is None or \
           entity2.start_pos is None or entity2.end_pos is None:
            return ""
        
        # Determine the order of entities in the text
        if entity1.start_pos < entity2.start_pos:
            first, second = entity1, entity2
        else:
            first, second = entity2, entity1
        
        # Define context window
        start = max(0, first.start_pos - window_size)
        end = min(len(text), second.end_pos + window_size)
        
        # Get context
        context = text[start:end]
        
        return context
    
    def add_inverse_relationships(
        self, relationships: List[Relationship]
    ) -> List[Relationship]:
        """Add inverse relationships where applicable.
        
        For example, if A TRAINED_ON B exists, add B USED_TO_TRAIN A.
        
        Args:
            relationships: Original list of relationships
            
        Returns:
            Extended list including inverse relationships
        """
        extended = copy.copy(relationships)
        
        for rel in relationships:
            inverse = rel.get_inverse()
            if inverse:
                extended.append(inverse)
        
        return extended
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """Get statistics about the extracted relationships.
        
        Returns:
            Dictionary with relationship statistics
        """
        if not self.relationships:
            return {"total": 0}
        
        grouped = self.group_relationships_by_type(self.relationships)
        
        stats = {
            "total": len(self.relationships),
            "by_type": {str(t): len(r) for t, r in grouped.items()},
            "avg_confidence": sum(r.confidence for r in self.relationships) / len(self.relationships),
            "confidence_distribution": {
                "high": len([r for r in self.relationships if r.confidence >= 0.8]),
                "medium": len([r for r in self.relationships if 0.5 <= r.confidence < 0.8]),
                "low": len([r for r in self.relationships if r.confidence < 0.5])
            },
            "bidirectional": len([r for r in self.relationships if r.bidirectional])
        }
        
        return stats
    
    def find_relationships_involving_entity(
        self, entity: Entity, relationships: Optional[List[Relationship]] = None
    ) -> List[Relationship]:
        """Find all relationships that involve a specific entity.
        
        Args:
            entity: The entity to find relationships for
            relationships: List of relationships to search (defaults to self.relationships)
            
        Returns:
            List of relationships involving the entity
        """
        relationships = relationships or self.relationships
        
        # Compare by ID for proper entity matching
        entity_id = entity.id
        
        return [
            rel for rel in relationships
            if (rel.source and rel.source.id == entity_id) or 
               (rel.target and rel.target.id == entity_id)
        ]
    
    def find_relationship_chain(
        self, start_entity: Entity, max_depth: int = 3
    ) -> Dict[str, List[List[Relationship]]]:
        """Find chains of relationships starting from a given entity.
        
        This is useful for tracing relationship paths through the knowledge graph.
        
        Args:
            start_entity: Starting entity for the chain
            max_depth: Maximum chain length
            
        Returns:
            Dictionary mapping depth to lists of relationship chains
        """
        chains = {i: [] for i in range(1, max_depth + 1)}
        visited = set([start_entity.id])
        
        def build_chain(current, chain, depth):
            if depth > max_depth:
                return
            
            # Find all relationships where current entity is the source
            next_relations = [
                rel for rel in self.relationships
                if rel.source and rel.source.id == current.id
            ]
            
            for rel in next_relations:
                if rel.target and rel.target.id not in visited:
                    new_chain = chain + [rel]
                    chains[depth].append(new_chain)
                    
                    # Continue building the chain
                    visited.add(rel.target.id)
                    build_chain(rel.target, new_chain, depth + 1)
                    visited.remove(rel.target.id)
        
        # Start building chains from the start entity
        build_chain(start_entity, [], 1)
        
        return chains