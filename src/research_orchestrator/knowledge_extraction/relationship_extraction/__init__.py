"""
Relationship Extraction module for the Research Orchestration Framework.

This module provides components for extracting relationships between entities
in research documents, such as which models were trained on which datasets,
which methods outperform others, etc.
"""

from .relationship import Relationship, RelationType
from .base_extractor import RelationshipExtractor
from .pattern_extractor import PatternRelationshipExtractor
from .ai_extractor import AIRelationshipExtractor
from .factory import RelationshipExtractorFactory
from .combined_extractor import CombinedRelationshipExtractor

__all__ = [
    'Relationship',
    'RelationType',
    'RelationshipExtractor',
    'PatternRelationshipExtractor',
    'AIRelationshipExtractor',
    'RelationshipExtractorFactory',
    'CombinedRelationshipExtractor'
]