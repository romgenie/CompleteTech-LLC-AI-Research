"""
Entity Recognizer Factory for the Research Orchestration Framework.

This module provides a factory for creating and configuring different types
of entity recognizers based on configuration.
"""

from typing import Dict, Any, List, Optional, Union, Type
import logging
import os
import yaml

from .base_recognizer import EntityRecognizer
from .ai_recognizer import AIEntityRecognizer
from .scientific_recognizer import ScientificEntityRecognizer
from .combined_recognizer import CombinedEntityRecognizer

logger = logging.getLogger(__name__)


class EntityRecognizerFactory:
    """Factory for creating and configuring entity recognizers.
    
    This factory can create various types of entity recognizers with
    appropriate configuration, and handles loading configuration from files.
    """
    
    RECOGNIZER_TYPES = {
        "ai": AIEntityRecognizer,
        "scientific": ScientificEntityRecognizer,
        "combined": CombinedEntityRecognizer
    }
    
    @classmethod
    def create_recognizer(
        cls, 
        recognizer_type: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> EntityRecognizer:
        """Create an entity recognizer of the specified type.
        
        Args:
            recognizer_type: Type of recognizer to create ('ai', 'scientific', or 'combined')
            config: Configuration dictionary for the recognizer
            
        Returns:
            Configured entity recognizer instance
            
        Raises:
            ValueError: If the recognizer type is unknown
        """
        config = config or {}
        
        if recognizer_type not in cls.RECOGNIZER_TYPES:
            raise ValueError(f"Unknown recognizer type: {recognizer_type}")
        
        recognizer_class = cls.RECOGNIZER_TYPES[recognizer_type]
        
        if recognizer_type == "combined":
            # Special handling for combined recognizer which needs sub-recognizers
            sub_recognizers = cls._create_sub_recognizers(config.get("recognizers", []))
            return recognizer_class(recognizers=sub_recognizers, config=config)
        else:
            # Standard recognizer creation
            return recognizer_class(config=config)
    
    @classmethod
    def _create_sub_recognizers(
        cls, 
        recognizer_configs: List[Dict[str, Any]]
    ) -> List[EntityRecognizer]:
        """Create sub-recognizers for a combined recognizer.
        
        Args:
            recognizer_configs: List of recognizer configurations
            
        Returns:
            List of configured recognizer instances
        """
        sub_recognizers = []
        
        for rec_config in recognizer_configs:
            rec_type = rec_config.pop("type", None)
            if not rec_type:
                logger.warning("Skipping sub-recognizer with missing type")
                continue
            
            try:
                recognizer = cls.create_recognizer(rec_type, rec_config)
                sub_recognizers.append(recognizer)
            except Exception as e:
                logger.error(f"Failed to create sub-recognizer of type {rec_type}: {e}")
        
        return sub_recognizers
    
    @classmethod
    def from_config_file(cls, config_path: str) -> EntityRecognizer:
        """Create an entity recognizer from a configuration file.
        
        Args:
            config_path: Path to a YAML configuration file
            
        Returns:
            Configured entity recognizer instance
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the configuration is invalid
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_path}: {e}")
        
        recognizer_type = config.pop("type", None)
        if not recognizer_type:
            raise ValueError("Configuration must specify a recognizer type")
        
        return cls.create_recognizer(recognizer_type, config)
    
    @classmethod
    def create_default_recognizer(cls) -> CombinedEntityRecognizer:
        """Create a default combined recognizer with standard configuration.
        
        This method provides a convenient way to create a fully configured
        combined recognizer with both AI and scientific sub-recognizers.
        
        Returns:
            Configured combined entity recognizer
        """
        # Create AI recognizer with default settings
        ai_recognizer = AIEntityRecognizer()
        
        # Create scientific recognizer with default settings
        scientific_recognizer = ScientificEntityRecognizer()
        
        # Create combined recognizer
        return CombinedEntityRecognizer(
            recognizers=[ai_recognizer, scientific_recognizer],
            config={
                "type_priorities": {
                    # Default priorities, can be adjusted as needed
                }
            }
        )