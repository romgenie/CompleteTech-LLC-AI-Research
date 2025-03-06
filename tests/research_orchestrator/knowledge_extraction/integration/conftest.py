"""
Integration test fixtures for knowledge extraction components.

This module provides pytest fixtures specifically for integration testing 
the knowledge extraction components, focusing on interaction between components.
"""

import pytest
import tempfile
import os
import shutil

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory


@pytest.fixture
def integration_document_directory():
    """Create a directory with test documents for integration testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a text file
    with open(os.path.join(temp_dir, "integration_test.txt"), "w") as f:
        f.write("This is an integration test document with AI content.\n")
        f.write("GPT-4 is a large language model developed by OpenAI.\n")
        f.write("It outperforms previous models like GPT-3 on various benchmarks like MMLU.\n")
        f.write("The model was trained on a diverse dataset and uses the transformer architecture.\n")
    
    # Create an HTML file
    with open(os.path.join(temp_dir, "integration_test.html"), "w") as f:
        f.write("<html><head><title>Integration Test</title></head><body>\n")
        f.write("<h1>AI Research Integration Test</h1>\n")
        f.write("<p>BERT is a transformer model developed by Google.</p>\n")
        f.write("<p>It uses bidirectional training for language representations.</p>\n")
        f.write("<p>PyTorch is a popular framework for implementing machine learning models.</p>\n")
        f.write("</body></html>")
    
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def integration_test_data():
    """Return test data for integration testing."""
    return {
        "test_text": (
            "GPT-4 is a large language model developed by OpenAI. It was trained on a massive dataset "
            "of text and code, and it outperforms previous models like GPT-3.5 on many benchmarks. "
            "The model was evaluated on tasks such as the MMLU benchmark, where it achieved "
            "86.4% accuracy. BERT is a transformer-based model developed by Google that revolutionized NLP. "
            "PyTorch and TensorFlow are popular frameworks for implementing these models."
        ),
        "expected_entities": [
            {"text": "GPT-4", "type": EntityType.MODEL},
            {"text": "OpenAI", "type": EntityType.ORGANIZATION},
            {"text": "GPT-3.5", "type": EntityType.MODEL},
            {"text": "MMLU", "type": EntityType.BENCHMARK},
            {"text": "BERT", "type": EntityType.MODEL},
            {"text": "Google", "type": EntityType.ORGANIZATION},
            {"text": "PyTorch", "type": EntityType.FRAMEWORK},
            {"text": "TensorFlow", "type": EntityType.FRAMEWORK}
        ],
        "expected_relationship_types": [
            RelationType.DEVELOPED_BY, 
            RelationType.TRAINED_ON,
            RelationType.OUTPERFORMS,
            RelationType.EVALUATED_ON
        ]
    }


@pytest.fixture
def document_processor():
    """Return a real document processor for integration testing."""
    return DocumentProcessor()


@pytest.fixture
def entity_recognizer():
    """Return a real entity recognizer for integration testing."""
    return EntityRecognizerFactory.create_recognizer("ai")


@pytest.fixture
def relationship_extractor():
    """Return a real relationship extractor for integration testing."""
    return RelationshipExtractorFactory.create_extractor("pattern")


@pytest.fixture
def combined_relationship_extractor():
    """Return a combined relationship extractor for integration testing."""
    return RelationshipExtractorFactory.create_extractor(
        "combined", 
        config={"extractors": [
            {"type": "pattern"},
            {"type": "ai"}
        ]}
    )