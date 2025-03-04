"""
Combined Entity Recognizer for the Research Orchestration Framework.

This module provides a combined entity recognizer that integrates multiple
specialized recognizers to provide comprehensive entity recognition.
"""

from typing import List, Dict, Any, Optional, Set, Type
import logging

from .base_recognizer import EntityRecognizer
from .entity import Entity, EntityType

logger = logging.getLogger(__name__)


class CombinedEntityRecognizer(EntityRecognizer):
    """Entity recognizer that combines multiple specialized recognizers.
    
    This recognizer delegates entity recognition to specialized recognizers
    and merges their results, resolving conflicts and overlaps.
    """
    
    def __init__(
        self, 
        recognizers: List[EntityRecognizer],
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the Combined Entity Recognizer.
        
        Args:
            recognizers: List of specialized recognizers to use
            config: Configuration dictionary that can include conflict resolution
                   strategies and entity prioritization
        """
        super().__init__(config)
        self.recognizers = recognizers
        
        # Entity type priorities for conflict resolution
        # Higher priority types override lower priority types in case of conflicts
        self.type_priorities = self._get_type_priorities()
    
    def _get_type_priorities(self) -> Dict[EntityType, int]:
        """Get entity type priorities from configuration or use defaults.
        
        Returns:
            Dictionary mapping entity types to priority values (higher = more priority)
        """
        # Default priorities (can be overridden in config)
        defaults = {
            # Higher priority for specific entity types
            EntityType.MODEL: 100,
            EntityType.DATASET: 90,
            EntityType.ALGORITHM: 85,
            EntityType.METRIC: 80,
            EntityType.ARCHITECTURE: 75,
            EntityType.FRAMEWORK: 70,
            EntityType.LIBRARY: 65,
            
            EntityType.THEORY: 60,
            EntityType.CONCEPT: 55,
            EntityType.METHODOLOGY: 50,
            EntityType.FINDING: 45,
            EntityType.HYPOTHESIS: 40,
            
            # Lower priority for generic entity types
            EntityType.AUTHOR: 30,
            EntityType.INSTITUTION: 25,
            EntityType.FIELD: 20,
            
            # Lowest priority for the unknown type
            EntityType.UNKNOWN: 0
        }
        
        # Override with config values if provided
        config_priorities = self.config.get("type_priorities", {})
        for type_str, priority in config_priorities.items():
            entity_type = EntityType.from_string(type_str)
            defaults[entity_type] = priority
        
        # Fill in any missing entity types with a default priority of 10
        for entity_type in EntityType:
            if entity_type not in defaults:
                defaults[entity_type] = 10
        
        return defaults
    
    def _initialize_from_config(self) -> None:
        """Initialize based on configuration."""
        # There's no specific initialization needed for the combined recognizer itself
        pass
    
    def recognize(self, text: str) -> List[Entity]:
        """Recognize entities in the provided text using all recognizers.
        
        Args:
            text: The text to analyze for entities
            
        Returns:
            A list of recognized entities from all recognizers, with conflicts resolved
        """
        all_entities = []
        
        # Collect entities from all recognizers
        for recognizer in self.recognizers:
            entities = recognizer.recognize(text)
            all_entities.extend(entities)
        
        # Resolve conflicts between entity types
        resolved_entities = self._resolve_conflicts(all_entities)
        
        # Save the entities for later use
        self.entities = resolved_entities
        
        return resolved_entities
    
    def _resolve_conflicts(self, entities: List[Entity]) -> List[Entity]:
        """Resolve conflicts between entities from different recognizers.
        
        This method handles the case where different recognizers identify
        the same span of text as different entity types.
        
        Args:
            entities: List of entities from all recognizers
            
        Returns:
            List of entities with conflicts resolved
        """
        if not entities:
            return []
        
        # First group entities by their exact spans
        span_groups: Dict[tuple, List[Entity]] = {}
        
        for entity in entities:
            if entity.start_pos is not None and entity.end_pos is not None:
                span_key = (entity.start_pos, entity.end_pos)
                if span_key not in span_groups:
                    span_groups[span_key] = []
                span_groups[span_key].append(entity)
        
        # Resolve conflicts within each span group
        resolved_entities = []
        
        for span, span_entities in span_groups.items():
            if len(span_entities) == 1:
                # No conflict for this span
                resolved_entities.append(span_entities[0])
            else:
                # Sort by confidence and type priority
                sorted_entities = sorted(
                    span_entities,
                    key=lambda e: (e.confidence, self.type_priorities.get(e.type, 0)),
                    reverse=True
                )
                
                # Create a merged entity with the highest confidence type
                # but combine metadata from all entities
                best_entity = sorted_entities[0]
                
                # Merge metadata from all entities for this span
                combined_metadata = {}
                for entity in span_entities:
                    combined_metadata.update(entity.metadata)
                
                # Add alternative types to metadata
                alt_types = [str(e.type) for e in sorted_entities[1:]]
                if alt_types:
                    combined_metadata["alternative_types"] = alt_types
                
                # Create the merged entity
                merged_entity = Entity(
                    text=best_entity.text,
                    type=best_entity.type,
                    confidence=best_entity.confidence,
                    start_pos=best_entity.start_pos,
                    end_pos=best_entity.end_pos,
                    metadata=combined_metadata
                )
                
                resolved_entities.append(merged_entity)
        
        # Handle entities without position information
        for entity in entities:
            if entity.start_pos is None or entity.end_pos is None:
                resolved_entities.append(entity)
        
        # Handle overlapping (but not identical) spans using the base class method
        return self.merge_overlapping_entities(resolved_entities)
    
    def get_recognizer_by_type(self, recognizer_type: Type[EntityRecognizer]) -> Optional[EntityRecognizer]:
        """Get a recognizer instance by its type.
        
        Args:
            recognizer_type: The class of the recognizer to retrieve
            
        Returns:
            The recognizer instance of the specified type, or None if not found
        """
        for recognizer in self.recognizers:
            if isinstance(recognizer, recognizer_type):
                return recognizer
        return None