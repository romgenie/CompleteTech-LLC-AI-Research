"""
Unit test fixtures for knowledge extraction components.

This module provides pytest fixtures specifically for unit testing the knowledge extraction
components, including mock objects and sample data structures.
"""

import pytest
from unittest.mock import MagicMock

from research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from research_orchestrator.knowledge_extraction.entity_recognition.base_recognizer import EntityRecognizer
from research_orchestrator.knowledge_extraction.document_processing.document_processor import Document


@pytest.fixture
def mock_document():
    """Return a mock document for testing."""
    return Document(
        content="This is a test document with GPT-4 and BERT mentioned.",
        document_type="text",
        path="/path/to/test.txt",
        metadata={"file_size": 100, "file_extension": ".txt", "line_count": 3}
    )


@pytest.fixture
def mock_entity_recognizer():
    """Return a mock entity recognizer for testing."""
    recognizer = MagicMock()
    recognizer.recognize.return_value = [
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=15, id="e1"),
        Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=20, end_pos=24, id="e2")
    ]
    return recognizer


@pytest.fixture
def mock_relationship_extractor():
    """Return a mock relationship extractor for testing."""
    extractor = MagicMock()
    extractor.extract_relationships.return_value = [
        Relationship(
            source=Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=15, id="e1"),
            target=Entity(text="OpenAI", type=EntityType.INSTITUTION, confidence=0.9, start_pos=30, end_pos=36, id="e3"),
            relation_type=RelationType.DEVELOPED_BY,
            confidence=0.85,
            context="GPT-4 was developed by OpenAI",
            id="r1"
        )
    ]
    return extractor


@pytest.fixture
def sample_unit_entities():
    """Return a list of sample entities for unit testing."""
    return [
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=0, end_pos=5, id="e1"),
        Entity(text="OpenAI", type=EntityType.INSTITUTION, confidence=0.9, start_pos=30, end_pos=36, id="e2"),
        Entity(text="transformer", type=EntityType.ARCHITECTURE, confidence=0.85, start_pos=45, end_pos=56, id="e3"),
        Entity(text="MMLU", type=EntityType.DATASET, confidence=0.8, start_pos=70, end_pos=74, id="e4")
    ]


@pytest.fixture
def sample_unit_relationships(sample_unit_entities):
    """Return a list of sample relationships for unit testing."""
    return [
        Relationship(
            source=sample_unit_entities[0],  # GPT-4
            target=sample_unit_entities[1],  # OpenAI
            relation_type=RelationType.DEVELOPED_BY,
            confidence=0.9,
            context="GPT-4 was developed by OpenAI",
            id="r1"
        ),
        Relationship(
            source=sample_unit_entities[0],  # GPT-4
            target=sample_unit_entities[2],  # transformer
            relation_type=RelationType.BASED_ON,
            confidence=0.85,
            context="GPT-4 is based on the transformer architecture",
            id="r2"
        ),
        Relationship(
            source=sample_unit_entities[0],  # GPT-4
            target=sample_unit_entities[3],  # MMLU
            relation_type=RelationType.EVALUATED_ON,
            confidence=0.8,
            context="GPT-4 was evaluated on MMLU",
            id="r3"
        )
    ]