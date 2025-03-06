"""
Relationship Extractor Factory module for the Knowledge Extraction Pipeline.

This module provides factory methods for creating and configuring
different types of relationship extractors based on the requirements.
"""

from typing import Dict, List, Optional, Any, Union
import logging

from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship_extractor import RelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.pattern_relationship_extractor import PatternRelationshipExtractor, DEFAULT_RELATION_TYPES
from src.research_orchestrator.knowledge_extraction.relationship_extraction.ai_relationship_extractor import AIRelationshipExtractor, AI_RELATION_TYPES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RelationshipExtractorFactory:
    """
    Factory class for creating and configuring relationship extractors.
    """
    
    @classmethod
    def create_extractor(cls, extractor_type: str, 
                         config: Optional[Dict[str, Any]] = None) -> RelationshipExtractor:
        """
        Create and configure a relationship extractor of the specified type.
        
        Args:
            extractor_type: Type of relationship extractor to create
            config: Configuration for the relationship extractor
            
        Returns:
            Configured relationship extractor instance
            
        Raises:
            ValueError: If the specified extractor type is not supported
        """
        config = config or {}
        
        if extractor_type.lower() == "pattern":
            return cls.create_pattern_extractor(**config)
        elif extractor_type.lower() == "ai":
            return cls.create_ai_extractor(**config)
        elif extractor_type.lower() == "combined":
            return cls.create_combined_extractor(**config)
        else:
            raise ValueError(f"Unsupported relationship extractor type: {extractor_type}")
    
    @classmethod
    def create_pattern_extractor(cls, 
                                relation_types: Optional[List[str]] = None,
                                config_path: Optional[str] = None,
                                custom_patterns: Optional[Dict[str, List[str]]] = None) -> PatternRelationshipExtractor:
        """
        Create and configure a pattern-based relationship extractor.
        
        Args:
            relation_types: List of relationship types to extract
            config_path: Path to configuration file
            custom_patterns: Custom patterns for extracting relationships
            
        Returns:
            Configured pattern-based relationship extractor instance
        """
        logger.info(f"Creating pattern-based relationship extractor with {len(relation_types or DEFAULT_RELATION_TYPES)} relation types")
        
        return PatternRelationshipExtractor(
            relation_types=relation_types,
            config_path=config_path,
            custom_patterns=custom_patterns
        )
    
    @classmethod
    def create_ai_extractor(cls,
                           relation_types: Optional[List[str]] = None,
                           config_path: Optional[str] = None,
                           custom_patterns: Optional[Dict[str, List[str]]] = None,
                           use_karma: bool = False,
                           karma_config: Optional[Dict[str, Any]] = None) -> AIRelationshipExtractor:
        """
        Create and configure an AI-specific relationship extractor.
        
        Args:
            relation_types: List of AI relationship types to extract
            config_path: Path to configuration file
            custom_patterns: Custom patterns for extracting relationships
            use_karma: Whether to use KARMA for relationship extraction
            karma_config: Configuration for KARMA adapter
            
        Returns:
            Configured AI-specific relationship extractor instance
        """
        logger.info(f"Creating AI-specific relationship extractor with {len(relation_types or AI_RELATION_TYPES)} relation types")
        
        return AIRelationshipExtractor(
            relation_types=relation_types,
            config_path=config_path,
            custom_patterns=custom_patterns,
            use_karma=use_karma,
            karma_config=karma_config
        )
    
    @classmethod
    def create_combined_extractor(cls, 
                                 pattern_config: Optional[Dict[str, Any]] = None,
                                 ai_config: Optional[Dict[str, Any]] = None) -> 'CombinedRelationshipExtractor':
        """
        Create a combined relationship extractor that uses multiple extractors.
        
        Args:
            pattern_config: Configuration for the pattern-based extractor
            ai_config: Configuration for the AI-specific extractor
            
        Returns:
            Configured combined relationship extractor instance
        """
        from src.research_orchestrator.knowledge_extraction.relationship_extraction.combined_relationship_extractor import CombinedRelationshipExtractor
        
        pattern_extractor = cls.create_pattern_extractor(**(pattern_config or {}))
        ai_extractor = cls.create_ai_extractor(**(ai_config or {}))
        
        logger.info(f"Creating combined relationship extractor with pattern-based and AI-specific extractors")
        
        return CombinedRelationshipExtractor(
            extractors=[pattern_extractor, ai_extractor]
        )
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> RelationshipExtractor:
        """
        Create a relationship extractor from a configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured relationship extractor instance
            
        Raises:
            ValueError: If the configuration is invalid
        """
        extractor_type = config.get("type")
        if not extractor_type:
            raise ValueError("Extractor type must be specified in the configuration")
        
        # Extract the extractor-specific configuration
        extractor_config = config.get("config", {})
        
        return cls.create_extractor(extractor_type, extractor_config)