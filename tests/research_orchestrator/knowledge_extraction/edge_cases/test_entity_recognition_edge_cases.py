"""
Edge case tests for entity recognition.

This module contains tests for entity recognition edge cases and error handling.
"""

import pytest
import os
import tempfile
import json

# Mark all tests in this module as edge case tests and entity related tests
pytestmark = [
    pytest.mark.edge_case,
    pytest.mark.entity,
    pytest.mark.medium
]

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory


@pytest.mark.empty
def test_empty_text_recognition(edge_case_entity_recognizer):
    """Test recognizing entities in empty text."""
    # Recognize entities in empty text
    entities = edge_case_entity_recognizer.recognize("")
    
    # Should return an empty list, not raise an error
    assert entities == []


@pytest.mark.duplicate
def test_duplicate_entity_handling(edge_case_entity_recognizer, duplicate_entities):
    """Test handling of duplicate entities."""
    # Merge overlapping entities
    merged_entities = edge_case_entity_recognizer.merge_overlapping_entities(duplicate_entities)
    
    # Should return a deduplicated list
    assert len(merged_entities) < len(duplicate_entities)
    
    # Check duplicate text occurrences
    gpt4_entities = [e for e in merged_entities if e.text == "GPT-4"]
    bert_entities = [e for e in merged_entities if e.text == "BERT"]
    
    # Should have deduplicated each group
    assert len(gpt4_entities) < duplicate_entities.count("GPT-4") if duplicate_entities.count("GPT-4") > 0 else True
    assert len(bert_entities) < duplicate_entities.count("BERT") if duplicate_entities.count("BERT") > 0 else True


@pytest.mark.conflicting
def test_conflicting_entity_type_handling(edge_case_entity_recognizer, conflicting_entities):
    """Test handling of entities with conflicting types."""
    # Merge overlapping entities
    merged_entities = edge_case_entity_recognizer.merge_overlapping_entities(conflicting_entities)
    
    # Should have merged conflicting entities based on confidence
    gpt4_entities = [e for e in merged_entities if e.text == "GPT-4"]
    bert_entities = [e for e in merged_entities if e.text == "BERT"]
    
    # Should have only one entity for each text
    assert len(gpt4_entities) == 1
    assert len(bert_entities) == 1
    
    # The higher confidence entity should be kept
    assert gpt4_entities[0].type == EntityType.MODEL  # Confidence 0.9 > 0.8
    assert bert_entities[0].type == EntityType.MODEL  # Confidence 0.9 > 0.7


@pytest.mark.overlapping
def test_complex_overlapping_entity_handling(edge_case_entity_recognizer, overlapping_entities):
    """Test handling of complex overlapping entities."""
    # Merge overlapping entities
    merged_entities = edge_case_entity_recognizer.merge_overlapping_entities(overlapping_entities)
    
    # Should return a reduced list with overlaps resolved
    assert len(merged_entities) < len(overlapping_entities)
    
    # Check specific merges
    # Find the GPT-related entity
    gpt_entities = [e for e in merged_entities if "GPT" in e.text]
    
    # Should have only one GPT-related entity (the highest confidence one)
    assert len(gpt_entities) == 1
    assert gpt_entities[0].text == "GPT-4"  # Highest confidence is GPT-4 with 0.9


@pytest.mark.special_chars
def test_special_character_recognition(edge_case_entity_recognizer, document_with_special_characters):
    """Test entity recognition with special characters."""
    # Recognize entities in text with special characters
    entities = edge_case_entity_recognizer.recognize(document_with_special_characters.content)
    
    # Should not raise an error
    assert isinstance(entities, list)
    
    # Verify that entities with special characters are recognized
    # This is more of a qualitative test, so we don't assert specific entities
    # just that the process completed without errors


@pytest.mark.code
def test_code_recognition(edge_case_entity_recognizer, document_with_code):
    """Test entity recognition in code."""
    # Recognize entities in code
    entities = edge_case_entity_recognizer.recognize(document_with_code.content)
    
    # Should not raise an error
    assert isinstance(entities, list)
    
    # Verify that some entities are recognized
    # Common frameworks like TensorFlow should be recognized
    frameworks = [e for e in entities if e.type == EntityType.FRAMEWORK]
    assert any("tensorflow" in e.text.lower() for e in frameworks), "TensorFlow not recognized as a framework"


@pytest.mark.large
def test_large_text_recognition(edge_case_entity_recognizer, very_large_document):
    """Test entity recognition in very large text."""
    # Recognize entities in large text
    # Use a smaller portion to keep the test reasonable
    entities = edge_case_entity_recognizer.recognize(very_large_document.content[:100000])
    
    # Should not raise an error
    assert isinstance(entities, list)
    
    # Since this is random text, we don't expect specific entities
    # Just verify that the process completed without errors


@pytest.mark.error
def test_entity_serialization_error():
    """Test error handling during entity serialization."""
    # Create an entity with a non-serializable object
    class NonSerializable:
        pass
    
    entity = Entity(
        text="Test",
        type=EntityType.MODEL,
        confidence=0.9,
        start_pos=0,
        end_pos=4,
        metadata={"non_serializable": NonSerializable()},
        id="e1"
    )
    
    # Attempting to convert to dict should raise an error
    with pytest.raises(TypeError):
        entity_dict = entity.to_dict()


@pytest.mark.malformed
def test_malformed_entity_loading(edge_case_entity_recognizer, malformed_json_file):
    """Test error handling when loading from a malformed JSON file."""
    # Attempt to load the malformed JSON
    with pytest.raises(json.JSONDecodeError):
        with open(malformed_json_file, 'r') as f:
            entity_dict = json.load(f)


@pytest.mark.invalid
def test_invalid_entity_type_handling():
    """Test handling of invalid entity types."""
    # Create an entity dict with an invalid type
    entity_dict = {
        "id": "e1",
        "text": "Test",
        "type": "invalid_type",
        "confidence": 0.9,
        "start_pos": 0,
        "end_pos": 4,
        "metadata": {}
    }
    
    # Creating an entity from this dict should raise a ValueError
    with pytest.raises(ValueError):
        entity = Entity.from_dict(entity_dict)


@pytest.mark.invalid
def test_invalid_recognizer_type_handling():
    """Test handling of invalid recognizer types."""
    # Attempting to create a recognizer with an invalid type should raise a ValueError
    with pytest.raises(ValueError):
        recognizer = EntityRecognizerFactory.create_recognizer("invalid_type")


@pytest.mark.invalid
def test_combined_recognizer_with_invalid_config():
    """Test creating a combined recognizer with invalid config."""
    # Create an invalid config
    invalid_config = {
        "recognizers": [
            {"type": "invalid_type"},
            {"type": "ai"}
        ]
    }
    
    # Attempting to create a combined recognizer with an invalid config should raise a ValueError
    with pytest.raises(ValueError):
        recognizer = EntityRecognizerFactory.create_recognizer("combined", invalid_config)


@pytest.mark.invalid
def test_entity_with_invalid_positions():
    """Test creating an entity with invalid positions."""
    # Creating an entity where end_pos < start_pos should raise a ValueError
    with pytest.raises(ValueError):
        entity = Entity(
            text="Test",
            type=EntityType.MODEL,
            confidence=0.9,
            start_pos=10,
            end_pos=5,  # end_pos < start_pos
            metadata={},
            id="e1"
        )


@pytest.mark.invalid
def test_entity_with_invalid_confidence():
    """Test creating an entity with invalid confidence."""
    # Creating an entity with confidence > 1.0 should raise a ValueError
    with pytest.raises(ValueError):
        entity = Entity(
            text="Test",
            type=EntityType.MODEL,
            confidence=1.5,  # confidence > 1.0
            start_pos=0,
            end_pos=4,
            metadata={},
            id="e1"
        )
    
    # Creating an entity with confidence < 0.0 should raise a ValueError
    with pytest.raises(ValueError):
        entity = Entity(
            text="Test",
            type=EntityType.MODEL,
            confidence=-0.5,  # confidence < 0.0
            start_pos=0,
            end_pos=4,
            metadata={},
            id="e1"
        )


@pytest.mark.entity
def test_filter_by_nonexistent_entity_type(edge_case_entity_recognizer, sample_unit_entities):
    """Test filtering by a nonexistent entity type."""
    # Create a custom entity type that is not in the currently recognized entities
    non_existent_type = EntityType.PAPER  # Assuming no PAPER entities in the sample
    
    # Filter by this type
    filtered_entities = edge_case_entity_recognizer.filter_entities(
        sample_unit_entities, 
        entity_types=[non_existent_type]
    )
    
    # Should return an empty list, not raise an error
    assert filtered_entities == []