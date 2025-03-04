"""
Knowledge Extraction Module for the Research Orchestration Framework.

This module provides components for extracting structured knowledge from various 
information sources, including academic papers, web content, and code repositories.
"""

# Import only components that are fully implemented
from src.research_orchestrator.knowledge_extraction.document_processing import DocumentProcessor

# Import entity recognition components
from src.research_orchestrator.knowledge_extraction.entity_recognition import (
    Entity, 
    EntityType,
    EntityRecognizer, 
    AIEntityRecognizer,
    ScientificEntityRecognizer,
    EntityRecognizerFactory,
    CombinedEntityRecognizer
)

# Relationship extraction will be imported when implemented
# from src.research_orchestrator.knowledge_extraction.relationship_extraction import RelationshipExtractor

__version__ = "0.1.0"