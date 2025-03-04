"""
Entity Recognition module for the Research Orchestration Framework.

This module provides components for identifying entities (concepts, models, 
algorithms, datasets, etc.) in research documents.
"""

from .entity import Entity, EntityType
from .base_recognizer import EntityRecognizer
from .ai_recognizer import AIEntityRecognizer
from .scientific_recognizer import ScientificEntityRecognizer
from .factory import EntityRecognizerFactory
from .combined_recognizer import CombinedEntityRecognizer

__all__ = [
    'Entity', 
    'EntityType',
    'EntityRecognizer', 
    'AIEntityRecognizer',
    'ScientificEntityRecognizer',
    'EntityRecognizerFactory',
    'CombinedEntityRecognizer'
]