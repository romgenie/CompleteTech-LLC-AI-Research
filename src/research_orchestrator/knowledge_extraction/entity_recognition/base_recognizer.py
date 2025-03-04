"""
Base entity recognizer class for the Research Orchestration Framework.

This module provides an abstract base class for entity recognizers that can
identify various types of entities in research documents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set, Tuple
import json
import os
import logging
from collections import defaultdict

from .entity import Entity, EntityType

logger = logging.getLogger(__name__)


class EntityRecognizer(ABC):
    """Abstract base class for entity recognizers.
    
    This class defines the interface for all entity recognizers and provides
    common functionality for entity handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the entity recognizer with optional configuration.
        
        Args:
            config: Configuration dictionary for the recognizer
        """
        self.config = config or {}
        self.entities: List[Entity] = []
        self._initialize_from_config()
    
    def _initialize_from_config(self) -> None:
        """Initialize the recognizer based on configuration."""
        # Default implementation does nothing, to be overridden by subclasses
        pass
    
    @abstractmethod
    def recognize(self, text: str) -> List[Entity]:
        """Recognize entities in the provided text.
        
        Args:
            text: The text to analyze for entities
            
        Returns:
            A list of recognized entities
        """
        pass
    
    def filter_entities(
        self, 
        entities: List[Entity], 
        min_confidence: float = 0.0,
        entity_types: Optional[Set[EntityType]] = None
    ) -> List[Entity]:
        """Filter entities based on confidence score and type.
        
        Args:
            entities: List of entities to filter
            min_confidence: Minimum confidence threshold (0.0-1.0)
            entity_types: Set of entity types to include (None for all)
            
        Returns:
            Filtered list of entities
        """
        filtered = entities
        
        # Filter by confidence
        if min_confidence > 0.0:
            filtered = [e for e in filtered if e.confidence >= min_confidence]
        
        # Filter by entity type
        if entity_types:
            filtered = [e for e in filtered if e.type in entity_types]
        
        return filtered
    
    def merge_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge or resolve overlapping entities based on confidence.
        
        When entities overlap in the text, this method decides which entity
        to keep based on confidence scores and entity types.
        
        Args:
            entities: List of entities that may contain overlaps
            
        Returns:
            List of entities with overlaps resolved
        """
        if not entities:
            return []
        
        # Sort entities by start position and then by length (longer first for same start)
        sorted_entities = sorted(
            entities,
            key=lambda e: (e.start_pos if e.start_pos is not None else -1, 
                          -(e.end_pos - e.start_pos if e.start_pos is not None and e.end_pos is not None else 0))
        )
        
        result = []
        for entity in sorted_entities:
            # Check if this entity overlaps with any entity already in the result
            overlap = False
            for i, existing in enumerate(result):
                if entity.overlaps_with(existing):
                    # If current entity is contained within existing entity, skip it
                    if existing.contains(entity):
                        overlap = True
                        break
                    
                    # If existing entity is contained within current entity, replace it
                    elif entity.contains(existing):
                        if entity.confidence >= existing.confidence:
                            result[i] = entity
                        overlap = True
                        break
                    
                    # Partial overlap - keep the one with higher confidence
                    elif entity.confidence > existing.confidence:
                        result[i] = entity
                        overlap = True
                        break
                    else:
                        overlap = True
                        break
            
            if not overlap:
                result.append(entity)
        
        return result
    
    def group_entities_by_type(self, entities: List[Entity]) -> Dict[EntityType, List[Entity]]:
        """Group entities by their type.
        
        Args:
            entities: List of entities to group
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        grouped = defaultdict(list)
        for entity in entities:
            grouped[entity.type].append(entity)
        return dict(grouped)
    
    def save_entities(self, filepath: str) -> None:
        """Save recognized entities to a JSON file.
        
        Args:
            filepath: Path to the output JSON file
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                [entity.to_dict() for entity in self.entities],
                f,
                indent=2
            )
        logger.info(f"Saved {len(self.entities)} entities to {filepath}")
    
    def load_entities(self, filepath: str) -> None:
        """Load entities from a JSON file.
        
        Args:
            filepath: Path to the input JSON file
        """
        if not os.path.exists(filepath):
            logger.warning(f"Entity file {filepath} does not exist")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            entity_dicts = json.load(f)
        
        self.entities = [Entity.from_dict(e_dict) for e_dict in entity_dicts]
        logger.info(f"Loaded {len(self.entities)} entities from {filepath}")
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about the recognized entities.
        
        Returns:
            Dictionary with entity statistics
        """
        if not self.entities:
            return {"total": 0}
        
        grouped = self.group_entities_by_type(self.entities)
        
        stats = {
            "total": len(self.entities),
            "by_type": {str(t): len(e) for t, e in grouped.items()},
            "avg_confidence": sum(e.confidence for e in self.entities) / len(self.entities),
            "confidence_distribution": {
                "high": len([e for e in self.entities if e.confidence >= 0.8]),
                "medium": len([e for e in self.entities if 0.5 <= e.confidence < 0.8]),
                "low": len([e for e in self.entities if e.confidence < 0.5])
            }
        }
        
        return stats