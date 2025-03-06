"""
Combined Relationship Extractor module for the Knowledge Extraction Pipeline.

This module provides functionality for combining multiple relationship extractors
to provide comprehensive relationship extraction capabilities.
"""

from typing import Dict, List, Optional, Set, Any, Tuple
import logging

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import Entity
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship_extractor import RelationshipExtractor, Relationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CombinedRelationshipExtractor(RelationshipExtractor):
    """
    Relationship extractor that combines multiple specialized extractors to provide
    comprehensive relationship extraction capabilities.
    """
    
    def __init__(self, extractors: List[RelationshipExtractor], 
                 config_path: Optional[str] = None):
        """
        Initialize the combined relationship extractor.
        
        Args:
            extractors: List of relationship extractors to combine
            config_path: Path to configuration file
        """
        # Get combined relation types from all extractors
        all_relation_types = []
        for extractor in extractors:
            all_relation_types.extend(extractor.relation_types)
        
        # Remove duplicates
        unique_relation_types = list(set(all_relation_types))
        
        # Initialize parent class
        super().__init__(unique_relation_types, config_path)
        
        # Store extractors
        self.extractors = extractors
        
        logger.info(f"Initialized combined relationship extractor with {len(extractors)} extractors")
        logger.info(f"Supporting {len(unique_relation_types)} relation types: {', '.join(unique_relation_types)}")
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract relationships using all extractors.
        
        Args:
            text: The text to analyze
            entities: List of entities to find relationships between
            
        Returns:
            List of extracted relationships
        """
        all_relationships = []
        
        # Run all extractors
        for extractor in self.extractors:
            try:
                relationships = extractor.extract_relationships(text, entities)
                all_relationships.extend(relationships)
                logger.debug(f"Extractor {type(extractor).__name__} found {len(relationships)} relationships")
            except Exception as e:
                logger.error(f"Error running extractor {type(extractor).__name__}: {e}")
        
        # Remove duplicate relationships
        unique_relationships = self._remove_duplicate_relationships(all_relationships)
        
        logger.info(f"Combined extractor found {len(unique_relationships)} unique relationships")
        
        return unique_relationships
    
    def _remove_duplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """
        Remove duplicate relationships, keeping the one with the highest confidence.
        
        Args:
            relationships: List of relationships
            
        Returns:
            List of unique relationships
        """
        unique_relationships = {}
        
        for relationship in relationships:
            # Create a key for the relationship
            key = (relationship.source_entity.id, relationship.target_entity.id, relationship.relation_type)
            
            # Check if we've seen this relationship before
            if key in unique_relationships:
                # Keep the relationship with the highest confidence
                if relationship.confidence > unique_relationships[key].confidence:
                    unique_relationships[key] = relationship
            else:
                unique_relationships[key] = relationship
        
        return list(unique_relationships.values())
    
    def get_relation_type_distribution(self) -> Dict[str, int]:
        """
        Get the distribution of relation types across all extractors.
        
        Returns:
            Dictionary mapping relation types to counts
        """
        distribution = {}
        
        for extractor in self.extractors:
            for relation_type in extractor.relation_types:
                if relation_type in distribution:
                    distribution[relation_type] += 1
                else:
                    distribution[relation_type] = 1
        
        return distribution
    
    def add_extractor(self, extractor: RelationshipExtractor):
        """
        Add a new extractor to the combined extractor.
        
        Args:
            extractor: The relationship extractor to add
        """
        self.extractors.append(extractor)
        
        # Update relation types
        for relation_type in extractor.relation_types:
            if relation_type not in self.relation_types:
                self.relation_types.append(relation_type)
        
        logger.info(f"Added {type(extractor).__name__} to combined extractor")
        logger.info(f"Now supporting {len(self.relation_types)} relation types")
    
    def get_extractor_by_type(self, extractor_type: str) -> Optional[RelationshipExtractor]:
        """
        Get an extractor by its type.
        
        Args:
            extractor_type: The type of extractor to get
            
        Returns:
            The extractor with the matching type, or None if not found
        """
        for extractor in self.extractors:
            if extractor_type.lower() in type(extractor).__name__.lower():
                return extractor
        
        return None
    
    def filter_relationships_by_types(self, relationships: List[Relationship], 
                                    types: List[str]) -> List[Relationship]:
        """
        Filter relationships by their types.
        
        Args:
            relationships: List of relationships to filter
            types: List of relationship types to keep
            
        Returns:
            Filtered list of relationships
        """
        return [r for r in relationships if r.relation_type in types]
    
    def group_relationships_by_type(self, relationships: List[Relationship]) -> Dict[str, List[Relationship]]:
        """
        Group relationships by their types.
        
        Args:
            relationships: List of relationships to group
            
        Returns:
            Dictionary mapping relationship types to lists of relationships
        """
        grouped = {}
        
        for relationship in relationships:
            if relationship.relation_type not in grouped:
                grouped[relationship.relation_type] = []
            grouped[relationship.relation_type].append(relationship)
        
        return grouped
    
    def analyze_entity_relationship_network(self, relationships: List[Relationship]) -> Dict[str, Dict[str, int]]:
        """
        Analyze the network of entity relationships.
        
        Args:
            relationships: List of relationships to analyze
            
        Returns:
            Dictionary mapping source entity types to dictionaries of target entity types and counts
        """
        network = {}
        
        for relationship in relationships:
            source_type = relationship.source_entity.type
            target_type = relationship.target_entity.type
            
            if source_type not in network:
                network[source_type] = {}
            
            if target_type not in network[source_type]:
                network[source_type][target_type] = 0
            
            network[source_type][target_type] += 1
        
        return network