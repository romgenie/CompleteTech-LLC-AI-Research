"""
Combined Entity Recognizer module for the Knowledge Extraction Pipeline.

This module provides functionality for combining multiple entity recognizers
to provide comprehensive entity recognition capabilities.
"""

from typing import Dict, List, Optional, Set, Any, Tuple
import logging

from research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import EntityRecognizer, Entity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CombinedEntityRecognizer(EntityRecognizer):
    """
    Entity recognizer that combines multiple specialized recognizers to provide
    comprehensive entity recognition capabilities.
    """
    
    def __init__(self, recognizers: List[EntityRecognizer], 
                 config_path: Optional[str] = None):
        """
        Initialize the combined entity recognizer.
        
        Args:
            recognizers: List of entity recognizers to combine
            config_path: Path to configuration file
        """
        # Get combined entity types from all recognizers
        all_entity_types = []
        for recognizer in recognizers:
            all_entity_types.extend(recognizer.entity_types)
        
        # Remove duplicates
        unique_entity_types = list(set(all_entity_types))
        
        # Initialize parent class
        super().__init__(unique_entity_types, config_path)
        
        # Store recognizers
        self.recognizers = recognizers
        
        logger.info(f"Initialized combined entity recognizer with {len(recognizers)} recognizers")
        logger.info(f"Supporting {len(unique_entity_types)} entity types: {', '.join(unique_entity_types)}")
    
    def recognize_entities(self, text: str) -> List[Entity]:
        """
        Recognize entities in the given text using all recognizers.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of recognized entities
        """
        all_entities = []
        
        # Run all recognizers
        for recognizer in self.recognizers:
            try:
                entities = recognizer.recognize_entities(text)
                all_entities.extend(entities)
                logger.debug(f"Recognizer {type(recognizer).__name__} found {len(entities)} entities")
            except Exception as e:
                logger.error(f"Error running recognizer {type(recognizer).__name__}: {e}")
        
        # Merge overlapping entities
        merged_entities = self.merge_overlapping_entities(all_entities)
        
        logger.info(f"Combined recognizer found {len(merged_entities)} unique entities")
        
        return merged_entities
    
    def merge_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Merge overlapping entities with custom logic for combined recognizers.
        
        This extends the base class method to handle cases where different recognizers
        identify the same entity with different types or confidence scores.
        
        Args:
            entities: List of entities to merge
            
        Returns:
            List of merged entities
        """
        if not entities:
            return []
        
        # First, group entities by exact text match
        entities_by_text = {}
        for entity in entities:
            key = (entity.text.lower(), entity.start_pos, entity.end_pos)
            if key not in entities_by_text:
                entities_by_text[key] = []
            entities_by_text[key].append(entity)
        
        # For each group, select the best entity based on confidence and source
        merged_exact_match = []
        for entity_group in entities_by_text.values():
            # If all entities have the same type, select the one with highest confidence
            if len(set(e.type for e in entity_group)) == 1:
                merged_exact_match.append(max(entity_group, key=lambda e: e.confidence))
            else:
                # If entities have different types, use a preference heuristic
                # In this case, we'll use a simple confidence-based approach
                merged_exact_match.append(max(entity_group, key=lambda e: e.confidence))
        
        # Now handle overlapping entities (partially overlapping text)
        # Sort by start position and then by confidence (descending)
        sorted_entities = sorted(merged_exact_match, key=lambda e: (e.start_pos, -e.confidence))
        
        merged = [sorted_entities[0]]
        
        for current in sorted_entities[1:]:
            previous = merged[-1]
            
            # Check if entities overlap
            if current.start_pos <= previous.end_pos:
                # Calculate overlap percentage
                overlap_start = max(current.start_pos, previous.start_pos)
                overlap_end = min(current.end_pos, previous.end_pos)
                overlap_length = overlap_end - overlap_start
                
                shorter_length = min(current.end_pos - current.start_pos, 
                                     previous.end_pos - previous.start_pos)
                
                overlap_percentage = overlap_length / shorter_length if shorter_length > 0 else 0
                
                # If overlap is significant (> 70%), keep entity with higher confidence
                if overlap_percentage > 0.7:
                    if current.confidence > previous.confidence:
                        merged[-1] = current
                else:
                    # If overlap is not significant, keep both entities
                    merged.append(current)
            else:
                # No overlap, add the current entity
                merged.append(current)
        
        return merged
    
    def get_entity_type_distribution(self) -> Dict[str, int]:
        """
        Get the distribution of entity types across all recognizers.
        
        Returns:
            Dictionary mapping entity types to counts
        """
        distribution = {}
        
        for recognizer in self.recognizers:
            for entity_type in recognizer.entity_types:
                if entity_type in distribution:
                    distribution[entity_type] += 1
                else:
                    distribution[entity_type] = 1
        
        return distribution
    
    def add_recognizer(self, recognizer: EntityRecognizer):
        """
        Add a new recognizer to the combined recognizer.
        
        Args:
            recognizer: The entity recognizer to add
        """
        self.recognizers.append(recognizer)
        
        # Update entity types
        for entity_type in recognizer.entity_types:
            if entity_type not in self.entity_types:
                self.entity_types.append(entity_type)
        
        logger.info(f"Added {type(recognizer).__name__} to combined recognizer")
        logger.info(f"Now supporting {len(self.entity_types)} entity types")
    
    def get_recognizer_by_type(self, recognizer_type: str) -> Optional[EntityRecognizer]:
        """
        Get a recognizer by its type.
        
        Args:
            recognizer_type: The type of recognizer to get
            
        Returns:
            The recognizer with the matching type, or None if not found
        """
        for recognizer in self.recognizers:
            if recognizer_type.lower() in type(recognizer).__name__.lower():
                return recognizer
        
        return None
    
    def filter_entities_by_types(self, entities: List[Entity], 
                                types: List[str]) -> List[Entity]:
        """
        Filter entities by their types.
        
        Args:
            entities: List of entities to filter
            types: List of entity types to keep
            
        Returns:
            Filtered list of entities
        """
        return [e for e in entities if e.type in types]
    
    def group_entities_by_type(self, entities: List[Entity]) -> Dict[str, List[Entity]]:
        """
        Group entities by their types.
        
        Args:
            entities: List of entities to group
            
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        grouped = {}
        
        for entity in entities:
            if entity.type not in grouped:
                grouped[entity.type] = []
            grouped[entity.type].append(entity)
        
        return grouped