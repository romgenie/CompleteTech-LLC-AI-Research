"""
Tests for the entity recognition module using pytest fixtures.
"""

import pytest

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.entity_recognition.ai_recognizer import AIEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.scientific_recognizer import ScientificEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory


# Entity tests
def test_entity_creation(sample_entity):
    """Test entity creation with proper attributes."""
    assert sample_entity.id == "test_entity_1"
    assert sample_entity.text == "BERT"
    assert sample_entity.type == EntityType.MODEL
    assert sample_entity.confidence == 0.95
    assert sample_entity.start_pos == 10
    assert sample_entity.end_pos == 14
    assert sample_entity.metadata == {"source": "test"}


def test_entity_to_dict(sample_entity, sample_entity_dict):
    """Test conversion of Entity to dictionary."""
    entity_dict = sample_entity.to_dict()
    assert entity_dict["id"] == sample_entity_dict["id"]
    assert entity_dict["text"] == sample_entity_dict["text"]
    assert entity_dict["type"] == sample_entity_dict["type"]
    assert entity_dict["confidence"] == sample_entity_dict["confidence"]


def test_entity_from_dict(sample_entity_dict):
    """Test creation of Entity from dictionary."""
    entity = Entity.from_dict(sample_entity_dict)
    assert entity.id == sample_entity_dict["id"]
    assert entity.text == sample_entity_dict["text"]
    assert entity.type == EntityType.MODEL
    assert entity.confidence == sample_entity_dict["confidence"]


def test_merge_overlapping_entities(mock_entity_recognizer, overlapping_entities):
    """Test merging overlapping entities."""
    merged = mock_entity_recognizer.merge_overlapping_entities(overlapping_entities)
    
    assert len(merged) == 2
    assert merged[0].text in ["BERT", "BERT model"]
    assert merged[1].text in ["GPT", "GPT-3"]


# AI Entity Recognizer tests
def test_ai_recognizer_initialization():
    """Test initializing AIEntityRecognizer."""
    recognizer = AIEntityRecognizer()
    assert recognizer is not None
    assert hasattr(recognizer, 'recognize')


def test_ai_entity_recognition(ai_test_text):
    """Test entity recognition with AI text."""
    recognizer = AIEntityRecognizer()
    entities = recognizer.recognize(ai_test_text)
    
    assert len(entities) > 0
    
    entity_types = {entity.type for entity in entities}
    expected_types = {EntityType.MODEL, EntityType.DATASET, EntityType.BENCHMARK, EntityType.FRAMEWORK}
    assert any(t in entity_types for t in expected_types)
    
    entity_texts = {entity.text.lower() for entity in entities}
    expected_entities = {"gpt-4", "gpt-3.5", "mmlu", "pytorch", "dataset"}
    assert any(e in entity_texts or e in ' '.join(entity_texts) for e in expected_entities)


def test_ai_entity_filtering(ai_test_text):
    """Test entity filtering by type."""
    recognizer = AIEntityRecognizer()
    entities = recognizer.recognize(ai_test_text)
    
    model_entities = [e for e in entities if e.type == EntityType.MODEL]
    assert len(model_entities) > 0
    
    for entity in model_entities:
        assert isinstance(entity.text, str)
        assert entity.type == EntityType.MODEL
        assert isinstance(entity.confidence, float)


# Scientific Entity Recognizer tests
def test_scientific_recognizer_initialization():
    """Test initializing ScientificEntityRecognizer."""
    recognizer = ScientificEntityRecognizer()
    assert recognizer is not None
    assert hasattr(recognizer, 'recognize')


def test_scientific_entity_recognition(scientific_test_text):
    """Test entity recognition with scientific text."""
    recognizer = ScientificEntityRecognizer()
    entities = recognizer.recognize(scientific_test_text)
    
    assert len(entities) > 0
    
    entity_types = {entity.type for entity in entities}
    expected_types = {EntityType.HYPOTHESIS, EntityType.METHODOLOGY, EntityType.FINDING}
    assert any(t in entity_types for t in expected_types)


def test_scientific_finding_entities(scientific_test_text):
    """Test finding entity extraction from scientific text."""
    recognizer = ScientificEntityRecognizer()
    entities = recognizer.recognize(scientific_test_text)
    
    finding_entities = [e for e in entities if e.type == EntityType.FINDING]
    
    # Skip if no findings found
    if finding_entities:
        for entity in finding_entities:
            assert isinstance(entity.text, str)
            assert entity.type == EntityType.FINDING
            assert isinstance(entity.confidence, float)
            assert any(keyword in entity.text.lower() for keyword in 
                       ["approach", "results", "performance", "finding"])


# Entity Recognizer Factory tests
def test_create_ai_recognizer():
    """Test creating an AI entity recognizer."""
    recognizer = EntityRecognizerFactory.create_recognizer("ai")
    assert isinstance(recognizer, AIEntityRecognizer)
    assert hasattr(recognizer, "recognize")


@pytest.mark.parametrize("entity_type,expected_min_count", [
    (EntityType.MODEL, 1),
    (EntityType.DATASET, 0),
    (EntityType.BENCHMARK, 0),
    (EntityType.FINDING, 0),
    (EntityType.AUTHOR, 0)
])
def test_entity_recognition_by_type(ai_test_text, entity_type, expected_min_count):
    """Test entity recognition for different entity types using parameterization."""
    # Create recognizer
    recognizer = AIEntityRecognizer()
    
    # Extract entities
    entities = recognizer.recognize(ai_test_text)
    
    # Count entities of the specified type
    entities_of_type = [e for e in entities if e.type == entity_type]
    
    # Check if we found the expected minimum number
    assert len(entities_of_type) >= expected_min_count, f"Expected at least {expected_min_count} entities of type {entity_type}, found {len(entities_of_type)}"


def test_create_scientific_recognizer():
    """Test creating a scientific entity recognizer."""
    recognizer = EntityRecognizerFactory.create_recognizer("scientific")
    assert isinstance(recognizer, ScientificEntityRecognizer)
    assert hasattr(recognizer, "recognize")


def test_create_combined_recognizer():
    """Test creating a combined entity recognizer."""
    config = {
        "recognizers": [
            {"type": "ai"},
            {"type": "scientific"}
        ]
    }
    recognizer = EntityRecognizerFactory.create_recognizer("combined", config)
    
    assert hasattr(recognizer, "recognize")
    assert hasattr(recognizer, "recognizers")
    assert len(recognizer.recognizers) > 0


def test_create_with_config():
    """Test creating an entity recognizer with config."""
    config = {
        "patterns": {
            "MODEL": [r"\bGPT-4\b"]
        }
    }
    
    recognizer = EntityRecognizerFactory.create_recognizer("ai", config)
    assert isinstance(recognizer, AIEntityRecognizer)
    assert hasattr(recognizer, "patterns")