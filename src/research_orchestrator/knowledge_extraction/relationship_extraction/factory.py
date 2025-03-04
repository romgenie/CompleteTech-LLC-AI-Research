"""
Relationship Extractor Factory for the Research Orchestration Framework.

This module provides a factory for creating and configuring different types
of relationship extractors based on configuration.
"""

from typing import Dict, Any, List, Optional, Union, Type
import logging
import os
import yaml

from .base_extractor import RelationshipExtractor
from .pattern_extractor import PatternRelationshipExtractor
from .ai_extractor import AIRelationshipExtractor
from .combined_extractor import CombinedRelationshipExtractor

logger = logging.getLogger(__name__)


class RelationshipExtractorFactory:
    """Factory for creating and configuring relationship extractors.
    
    This factory can create various types of relationship extractors with
    appropriate configuration, and handles loading configuration from files.
    """
    
    EXTRACTOR_TYPES = {
        "pattern": PatternRelationshipExtractor,
        "ai": AIRelationshipExtractor,
        "combined": CombinedRelationshipExtractor
    }
    
    @classmethod
    def create_extractor(
        cls, 
        extractor_type: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> RelationshipExtractor:
        """Create a relationship extractor of the specified type.
        
        Args:
            extractor_type: Type of extractor to create ('pattern', 'ai', or 'combined')
            config: Configuration dictionary for the extractor
            
        Returns:
            Configured relationship extractor instance
            
        Raises:
            ValueError: If the extractor type is unknown
        """
        config = config or {}
        
        if extractor_type not in cls.EXTRACTOR_TYPES:
            raise ValueError(f"Unknown extractor type: {extractor_type}")
        
        extractor_class = cls.EXTRACTOR_TYPES[extractor_type]
        
        if extractor_type == "combined":
            # Special handling for combined extractor which needs sub-extractors
            sub_extractors = cls._create_sub_extractors(config.get("extractors", []))
            return extractor_class(extractors=sub_extractors, config=config)
        else:
            # Standard extractor creation
            return extractor_class(config=config)
    
    @classmethod
    def _create_sub_extractors(
        cls, 
        extractor_configs: List[Dict[str, Any]]
    ) -> List[RelationshipExtractor]:
        """Create sub-extractors for a combined extractor.
        
        Args:
            extractor_configs: List of extractor configurations
            
        Returns:
            List of configured extractor instances
        """
        sub_extractors = []
        
        for ext_config in extractor_configs:
            ext_type = ext_config.pop("type", None)
            if not ext_type:
                logger.warning("Skipping sub-extractor with missing type")
                continue
            
            try:
                extractor = cls.create_extractor(ext_type, ext_config)
                sub_extractors.append(extractor)
            except Exception as e:
                logger.error(f"Failed to create sub-extractor of type {ext_type}: {e}")
        
        return sub_extractors
    
    @classmethod
    def from_config_file(cls, config_path: str) -> RelationshipExtractor:
        """Create a relationship extractor from a configuration file.
        
        Args:
            config_path: Path to a YAML configuration file
            
        Returns:
            Configured relationship extractor instance
            
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
        
        extractor_type = config.pop("type", None)
        if not extractor_type:
            raise ValueError("Configuration must specify an extractor type")
        
        return cls.create_extractor(extractor_type, config)
    
    @classmethod
    def create_pattern_extractor(cls, **kwargs) -> PatternRelationshipExtractor:
        """Create a pattern-based relationship extractor.
        
        Args:
            **kwargs: Configuration options
            
        Returns:
            Configured pattern relationship extractor
        """
        return cls.create_extractor("pattern", kwargs)
    
    @classmethod
    def create_ai_extractor(cls, **kwargs) -> AIRelationshipExtractor:
        """Create an AI-specific relationship extractor.
        
        Args:
            **kwargs: Configuration options
            
        Returns:
            Configured AI relationship extractor
        """
        return cls.create_extractor("ai", kwargs)
    
    @classmethod
    def create_default_extractor(cls) -> CombinedRelationshipExtractor:
        """Create a default combined extractor with standard configuration.
        
        This method provides a convenient way to create a fully configured
        combined extractor with both pattern and AI sub-extractors.
        
        Returns:
            Configured combined relationship extractor
        """
        # Create pattern extractor with default settings
        pattern_extractor = PatternRelationshipExtractor()
        
        # Create AI extractor with default settings
        ai_extractor = AIRelationshipExtractor()
        
        # Create combined extractor
        return CombinedRelationshipExtractor(
            extractors=[pattern_extractor, ai_extractor],
            config={}
        )