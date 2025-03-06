"""
Relationship Extractor module for the Knowledge Extraction Pipeline.

This module provides functionality for identifying and extracting relationships
between entities in research documents.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
import re
import json
import logging
from pathlib import Path

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import Entity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """Represents a relationship between two entities."""
    
    id: str
    source_entity: Entity
    target_entity: Entity
    relation_type: str
    confidence: float
    context: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary."""
        return {
            "id": self.id,
            "source_entity": self.source_entity.to_dict(),
            "target_entity": self.target_entity.to_dict(),
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "context": self.context,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a relationship from a dictionary."""
        return cls(
            id=data["id"],
            source_entity=Entity.from_dict(data["source_entity"]),
            target_entity=Entity.from_dict(data["target_entity"]),
            relation_type=data["relation_type"],
            confidence=data["confidence"],
            context=data["context"],
            metadata=data.get("metadata", {})
        )


class RelationshipExtractor:
    """
    Base relationship extractor class that provides methods for identifying
    and extracting relationships between entities in research text.
    """
    
    def __init__(self, relation_types: Optional[List[str]] = None,
                 config_path: Optional[str] = None):
        """
        Initialize the relationship extractor.
        
        Args:
            relation_types: List of relationship types to extract
            config_path: Path to configuration file
        """
        self.relation_types = relation_types or []
        self.config = self._load_config(config_path) if config_path else {}
        
        # Initialize resources
        self._initialize_resources()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def _initialize_resources(self):
        """Initialize resources needed for relationship extraction."""
        pass
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract relationships between entities in the given text.
        
        Args:
            text: The text to analyze
            entities: List of entities to find relationships between
            
        Returns:
            List of extracted relationships
        """
        # This is a base method that should be overridden by child classes
        raise NotImplementedError("Subclasses must implement extract_relationships")
    
    def filter_relationships(self, relationships: List[Relationship],
                           min_confidence: float = 0.0,
                           relation_types: Optional[List[str]] = None) -> List[Relationship]:
        """
        Filter relationships based on confidence score and type.
        
        Args:
            relationships: List of relationships to filter
            min_confidence: Minimum confidence score to keep a relationship
            relation_types: Types of relationships to keep (if None, keep all)
            
        Returns:
            Filtered list of relationships
        """
        filtered = [r for r in relationships if r.confidence >= min_confidence]
        
        if relation_types:
            filtered = [r for r in filtered if r.relation_type in relation_types]
            
        return filtered
    
    def save_relationships(self, relationships: List[Relationship], output_path: str):
        """
        Save relationships to a file.
        
        Args:
            relationships: List of relationships to save
            output_path: Path to save the relationships
        """
        try:
            with open(output_path, 'w') as f:
                json.dump([r.to_dict() for r in relationships], f, indent=2)
            logger.info(f"Saved {len(relationships)} relationships to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save relationships to {output_path}: {e}")
    
    def load_relationships(self, input_path: str) -> List[Relationship]:
        """
        Load relationships from a file.
        
        Args:
            input_path: Path to load relationships from
            
        Returns:
            List of loaded relationships
        """
        try:
            with open(input_path, 'r') as f:
                relationships_data = json.load(f)
            relationships = [Relationship.from_dict(r) for r in relationships_data]
            logger.info(f"Loaded {len(relationships)} relationships from {input_path}")
            return relationships
        except Exception as e:
            logger.error(f"Failed to load relationships from {input_path}: {e}")
            return []
    
    def get_entity_pair_context(self, text: str, entity1: Entity, entity2: Entity, 
                               window_size: int = 100) -> str:
        """
        Get the context surrounding a pair of entities.
        
        Args:
            text: The text to extract context from
            entity1: The first entity
            entity2: The second entity
            window_size: The size of the context window (characters)
            
        Returns:
            The context string
        """
        # Determine the start and end positions
        if entity1.start_pos <= entity2.start_pos:
            start_entity, end_entity = entity1, entity2
        else:
            start_entity, end_entity = entity2, entity1
        
        # Calculate context boundaries
        context_start = max(0, start_entity.start_pos - window_size)
        context_end = min(len(text), end_entity.end_pos + window_size)
        
        # Extract the context
        context = text[context_start:context_end]
        
        return context
    
    def find_entity_pairs(self, entities: List[Entity], 
                         max_distance: int = 200) -> List[Tuple[Entity, Entity]]:
        """
        Find pairs of entities that are close to each other in the text.
        
        Args:
            entities: List of entities to pair
            max_distance: Maximum distance between entities to consider them related
            
        Returns:
            List of entity pairs
        """
        pairs = []
        
        # Sort entities by their start position
        sorted_entities = sorted(entities, key=lambda e: e.start_pos)
        
        # Find pairs of entities that are close to each other
        for i, entity1 in enumerate(sorted_entities):
            for entity2 in sorted_entities[i+1:]:
                # Calculate the distance between the entities
                distance = entity2.start_pos - entity1.end_pos
                
                # If the distance is within the threshold, add the pair
                if distance <= max_distance:
                    pairs.append((entity1, entity2))
                # If the distance is too large, break the inner loop
                # This works because entities are sorted by start position
                else:
                    break
        
        return pairs