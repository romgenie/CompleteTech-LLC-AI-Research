"""
Entity Recognizer module for the Knowledge Extraction Pipeline.

This module provides functionality for identifying and categorizing entities within
research documents, with a focus on AI research concepts, methodologies, and results.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
import re
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an entity extracted from text."""
    
    id: str
    text: str
    type: str
    confidence: float
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "confidence": self.confidence,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create an entity from a dictionary."""
        return cls(
            id=data["id"],
            text=data["text"],
            type=data["type"],
            confidence=data["confidence"],
            start_pos=data["start_pos"],
            end_pos=data["end_pos"],
            metadata=data.get("metadata", {})
        )


class EntityRecognizer:
    """
    Base entity recognizer class that provides methods for identifying
    and extracting entities from research text.
    """
    
    def __init__(self, entity_types: Optional[List[str]] = None, 
                 config_path: Optional[str] = None):
        """
        Initialize the entity recognizer.
        
        Args:
            entity_types: List of entity types to recognize
            config_path: Path to configuration file
        """
        self.entity_types = entity_types or []
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
        """Initialize resources needed for entity recognition."""
        pass
    
    def recognize_entities(self, text: str) -> List[Entity]:
        """
        Recognize entities in the given text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of recognized entities
        """
        # This is a base method that should be overridden by child classes
        raise NotImplementedError("Subclasses must implement recognize_entities")
    
    def filter_entities(self, entities: List[Entity], 
                       min_confidence: float = 0.0,
                       entity_types: Optional[List[str]] = None) -> List[Entity]:
        """
        Filter entities based on confidence score and type.
        
        Args:
            entities: List of entities to filter
            min_confidence: Minimum confidence score to keep an entity
            entity_types: Types of entities to keep (if None, keep all)
            
        Returns:
            Filtered list of entities
        """
        filtered = [e for e in entities if e.confidence >= min_confidence]
        
        if entity_types:
            filtered = [e for e in filtered if e.type in entity_types]
            
        return filtered
    
    def merge_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Merge overlapping entities, keeping the one with higher confidence.
        
        Args:
            entities: List of entities to merge
            
        Returns:
            List of merged entities
        """
        if not entities:
            return []
        
        # Sort by start position and then by confidence (descending)
        sorted_entities = sorted(entities, key=lambda e: (e.start_pos, -e.confidence))
        
        merged = [sorted_entities[0]]
        
        for current in sorted_entities[1:]:
            previous = merged[-1]
            
            # Check if entities overlap
            if current.start_pos <= previous.end_pos:
                # If current entity has higher confidence, replace previous
                if current.confidence > previous.confidence:
                    merged[-1] = current
            else:
                merged.append(current)
        
        return merged
    
    def save_entities(self, entities: List[Entity], output_path: str):
        """
        Save entities to a file.
        
        Args:
            entities: List of entities to save
            output_path: Path to save the entities
        """
        try:
            with open(output_path, 'w') as f:
                json.dump([e.to_dict() for e in entities], f, indent=2)
            logger.info(f"Saved {len(entities)} entities to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save entities to {output_path}: {e}")
    
    def load_entities(self, input_path: str) -> List[Entity]:
        """
        Load entities from a file.
        
        Args:
            input_path: Path to load entities from
            
        Returns:
            List of loaded entities
        """
        try:
            with open(input_path, 'r') as f:
                entities_data = json.load(f)
            entities = [Entity.from_dict(e) for e in entities_data]
            logger.info(f"Loaded {len(entities)} entities from {input_path}")
            return entities
        except Exception as e:
            logger.error(f"Failed to load entities from {input_path}: {e}")
            return []