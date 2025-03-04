"""
Entity Recognizer Factory module for the Knowledge Extraction Pipeline.

This module provides factory methods for creating and configuring
different types of entity recognizers based on the requirements.
"""

from typing import Dict, List, Optional, Any, Union
import logging

from research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import EntityRecognizer
from research_orchestrator.knowledge_extraction.entity_recognition.ai_entity_recognizer import AIEntityRecognizer, AI_ENTITY_TYPES
from research_orchestrator.knowledge_extraction.entity_recognition.scientific_entity_recognizer import ScientificEntityRecognizer, SCIENTIFIC_ENTITY_TYPES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityRecognizerFactory:
    """
    Factory class for creating and configuring entity recognizers.
    """
    
    @classmethod
    def create_recognizer(cls, recognizer_type: str, 
                          config: Optional[Dict[str, Any]] = None) -> EntityRecognizer:
        """
        Create and configure an entity recognizer of the specified type.
        
        Args:
            recognizer_type: Type of entity recognizer to create
            config: Configuration for the entity recognizer
            
        Returns:
            Configured entity recognizer instance
            
        Raises:
            ValueError: If the specified recognizer type is not supported
        """
        config = config or {}
        
        if recognizer_type.lower() == "ai":
            return cls.create_ai_recognizer(**config)
        elif recognizer_type.lower() == "scientific":
            return cls.create_scientific_recognizer(**config)
        elif recognizer_type.lower() == "combined":
            return cls.create_combined_recognizer(**config)
        else:
            raise ValueError(f"Unsupported entity recognizer type: {recognizer_type}")
    
    @classmethod
    def create_ai_recognizer(cls, 
                            entity_types: Optional[List[str]] = None,
                            config_path: Optional[str] = None,
                            custom_patterns: Optional[Dict[str, List[str]]] = None,
                            use_karma: bool = False,
                            karma_config: Optional[Dict[str, Any]] = None) -> AIEntityRecognizer:
        """
        Create and configure an AI entity recognizer.
        
        Args:
            entity_types: List of AI entity types to recognize
            config_path: Path to configuration file
            custom_patterns: Custom regex patterns for entity types
            use_karma: Whether to use KARMA for entity recognition
            karma_config: Configuration for KARMA adapter
            
        Returns:
            Configured AI entity recognizer instance
        """
        logger.info(f"Creating AI entity recognizer with {len(entity_types or AI_ENTITY_TYPES)} entity types")
        
        return AIEntityRecognizer(
            entity_types=entity_types,
            config_path=config_path,
            custom_patterns=custom_patterns,
            use_karma=use_karma,
            karma_config=karma_config
        )
    
    @classmethod
    def create_scientific_recognizer(cls,
                                    entity_types: Optional[List[str]] = None,
                                    config_path: Optional[str] = None,
                                    custom_patterns: Optional[Dict[str, List[str]]] = None,
                                    use_karma: bool = False,
                                    karma_config: Optional[Dict[str, Any]] = None) -> ScientificEntityRecognizer:
        """
        Create and configure a scientific entity recognizer.
        
        Args:
            entity_types: List of scientific entity types to recognize
            config_path: Path to configuration file
            custom_patterns: Custom regex patterns for entity types
            use_karma: Whether to use KARMA for entity recognition
            karma_config: Configuration for KARMA adapter
            
        Returns:
            Configured scientific entity recognizer instance
        """
        logger.info(f"Creating scientific entity recognizer with {len(entity_types or SCIENTIFIC_ENTITY_TYPES)} entity types")
        
        return ScientificEntityRecognizer(
            entity_types=entity_types,
            config_path=config_path,
            custom_patterns=custom_patterns,
            use_karma=use_karma,
            karma_config=karma_config
        )
    
    @classmethod
    def create_combined_recognizer(cls, 
                                  ai_config: Optional[Dict[str, Any]] = None,
                                  scientific_config: Optional[Dict[str, Any]] = None) -> 'CombinedEntityRecognizer':
        """
        Create a combined entity recognizer that uses both AI and scientific recognizers.
        
        Args:
            ai_config: Configuration for the AI entity recognizer
            scientific_config: Configuration for the scientific entity recognizer
            
        Returns:
            Configured combined entity recognizer instance
        """
        from research_orchestrator.knowledge_extraction.entity_recognition.combined_entity_recognizer import CombinedEntityRecognizer
        
        ai_recognizer = cls.create_ai_recognizer(**(ai_config or {}))
        scientific_recognizer = cls.create_scientific_recognizer(**(scientific_config or {}))
        
        logger.info(f"Creating combined entity recognizer with AI and scientific recognizers")
        
        return CombinedEntityRecognizer(
            recognizers=[ai_recognizer, scientific_recognizer]
        )
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> EntityRecognizer:
        """
        Create an entity recognizer from a configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured entity recognizer instance
            
        Raises:
            ValueError: If the configuration is invalid
        """
        recognizer_type = config.get("type")
        if not recognizer_type:
            raise ValueError("Recognizer type must be specified in the configuration")
        
        # Extract the recognizer-specific configuration
        recognizer_config = config.get("config", {})
        
        return cls.create_recognizer(recognizer_type, recognizer_config)