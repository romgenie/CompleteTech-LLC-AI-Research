"""
Edge case tests for relationship extraction.

This module contains tests for relationship extraction edge cases and error handling.
"""

import pytest
import os
import tempfile
import json

# Mark all tests in this module as edge case tests and relationship related tests
pytestmark = [
    pytest.mark.edge_case,
    pytest.mark.relationship,
    pytest.mark.medium
]

from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
from research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType


@pytest.mark.empty
def test_empty_text_extraction(edge_case_relationship_extractor):
    """Test extracting relationships from empty text."""
    # Extract relationships from empty text with no entities
    relationships = edge_case_relationship_extractor.extract("", [])
    
    # Should return an empty list, not raise an error
    assert relationships == []


@pytest.mark.empty
def test_empty_entities_extraction(edge_case_relationship_extractor):
    """Test extracting relationships with no entities."""
    # Extract relationships from text but with no entities
    relationships = edge_case_relationship_extractor.extract(
        "GPT-4 outperforms previous models and was trained on a large dataset.",
        []
    )
    
    # Should return an empty list since there are no entities to relate
    assert relationships == []


@pytest.mark.circular
def test_circular_relationship_handling(edge_case_relationship_extractor, circular_relationships):
    """Test handling of circular relationships."""
    # Detect and handle circular relationships
    result = edge_case_relationship_extractor.detect_circular_relationships(circular_relationships)
    
    # Should detect the circular relationship
    assert result is not None
    assert len(result) > 0
    
    # Should have the path of the circle
    assert len(result[0]) == 3  # Three relationships in the circle
    
    # First source should be the same as last target
    first_source = result[0][0].source
    last_target = result[0][-1].target
    assert first_source.id == last_target.id


@pytest.mark.conflicting
def test_conflicting_relationship_handling(edge_case_relationship_extractor, conflicting_relationships):
    """Test handling of conflicting relationships."""
    # Detect conflicting relationships
    conflicts = edge_case_relationship_extractor.detect_conflicting_relationships(conflicting_relationships)
    
    # Should detect the conflict
    assert conflicts is not None
    assert len(conflicts) > 0
    
    # A conflict is a pair of relationships
    assert len(conflicts[0]) == 2
    
    # The relationships should have opposite directions for the same entities and relation type
    rel1, rel2 = conflicts[0]
    assert rel1.source.id == rel2.target.id
    assert rel1.target.id == rel2.source.id
    assert rel1.relation_type == rel2.relation_type


@pytest.mark.special_chars
def test_special_character_extraction(edge_case_relationship_extractor, document_with_special_characters):
    """Test relationship extraction with special characters."""
    # Create some sample entities with special characters
    entities = [
        Entity(text="∑∫√≤≥≠", type=EntityType.MODEL, confidence=0.9, start_pos=94, end_pos=100, id="e1"),
        Entity(text="😀🤣😎👍❤️🔥", type=EntityType.DATASET, confidence=0.9, start_pos=95, end_pos=101, id="e2")
    ]
    
    # Extract relationships from text with special characters
    relationships = edge_case_relationship_extractor.extract(document_with_special_characters.content, entities)
    
    # Should not raise an error
    assert isinstance(relationships, list)


@pytest.mark.code
def test_code_relationship_extraction(edge_case_relationship_extractor, document_with_code):
    """Test relationship extraction in code."""
    # Create some sample entities for code
    entities = [
        Entity(text="MyClass", type=EntityType.MODEL, confidence=0.9, start_pos=122, end_pos=129, id="e1"),
        Entity(text="tensorflow", type=EntityType.FRAMEWORK, confidence=0.9, start_pos=130, end_pos=140, id="e2"),
        Entity(text="keras", type=EntityType.FRAMEWORK, confidence=0.9, start_pos=132, end_pos=137, id="e3")
    ]
    
    # Extract relationships from code
    relationships = edge_case_relationship_extractor.extract(document_with_code.content, entities)
    
    # Should not raise an error
    assert isinstance(relationships, list)
    
    # If relationships are found, verify they involve the provided entities
    for rel in relationships:
        assert rel.source.id in ["e1", "e2", "e3"]
        assert rel.target.id in ["e1", "e2", "e3"]


@pytest.mark.large
def test_large_text_extraction(edge_case_relationship_extractor, very_large_document):
    """Test relationship extraction in very large text."""
    # Create some sample entities
    entities = [
        Entity(text="Sample", type=EntityType.MODEL, confidence=0.9, start_pos=1000, end_pos=1006, id="e1"),
        Entity(text="Test", type=EntityType.DATASET, confidence=0.9, start_pos=2000, end_pos=2004, id="e2")
    ]
    
    # Extract relationships from large text (using a smaller portion)
    relationships = edge_case_relationship_extractor.extract(very_large_document.content[:100000], entities)
    
    # Should not raise an error
    assert isinstance(relationships, list)


@pytest.mark.error
def test_relationship_serialization_error():
    """Test error handling during relationship serialization."""
    # Create entities
    e1 = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=0, end_pos=5, id="e1")
    e2 = Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, id="e2")
    
    # Create a relationship with a non-serializable object
    class NonSerializable:
        pass
    
    relationship = Relationship(
        source=e1,
        target=e2,
        relation_type=RelationType.OUTPERFORMS,
        confidence=0.9,
        context="Context",
        metadata={"non_serializable": NonSerializable()},
        id="r1"
    )
    
    # Attempting to convert to dict should raise an error
    with pytest.raises(TypeError):
        rel_dict = relationship.to_dict()


@pytest.mark.malformed
def test_malformed_relationship_loading(edge_case_relationship_extractor, malformed_json_file):
    """Test error handling when loading from a malformed JSON file."""
    # Attempt to load the malformed JSON
    with pytest.raises(json.JSONDecodeError):
        with open(malformed_json_file, 'r') as f:
            relationship_dict = json.load(f)


@pytest.mark.invalid
def test_invalid_relationship_type_handling():
    """Test handling of invalid relationship types."""
    # Create a relationship dict with an invalid type
    e1 = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=0, end_pos=5, id="e1")
    e2 = Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, id="e2")
    
    relationship_dict = {
        "id": "r1",
        "source": e1.to_dict(),
        "target": e2.to_dict(),
        "relation_type": "invalid_type",
        "confidence": 0.9,
        "context": "Context",
        "metadata": {}
    }
    
    # Creating a relationship from this dict should raise a ValueError
    with pytest.raises(ValueError):
        relationship = Relationship.from_dict(relationship_dict)


@pytest.mark.invalid
def test_invalid_extractor_type_handling():
    """Test handling of invalid extractor types."""
    # Attempting to create an extractor with an invalid type should raise a ValueError
    with pytest.raises(ValueError):
        extractor = RelationshipExtractorFactory.create_extractor("invalid_type")


@pytest.mark.invalid
def test_combined_extractor_with_invalid_config():
    """Test creating a combined extractor with invalid config."""
    # Create an invalid config
    invalid_config = {
        "extractors": [
            {"type": "invalid_type"},
            {"type": "pattern"}
        ]
    }
    
    # Attempting to create a combined extractor with an invalid config should raise a ValueError
    with pytest.raises(ValueError):
        extractor = RelationshipExtractorFactory.create_extractor("combined", invalid_config)


@pytest.mark.invalid
def test_relationship_with_invalid_confidence():
    """Test creating a relationship with invalid confidence."""
    # Create entities
    e1 = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=0, end_pos=5, id="e1")
    e2 = Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, id="e2")
    
    # Creating a relationship with confidence > 1.0 should raise a ValueError
    with pytest.raises(ValueError):
        relationship = Relationship(
            source=e1,
            target=e2,
            relation_type=RelationType.OUTPERFORMS,
            confidence=1.5,  # confidence > 1.0
            context="Context",
            metadata={},
            id="r1"
        )
    
    # Creating a relationship with confidence < 0.0 should raise a ValueError
    with pytest.raises(ValueError):
        relationship = Relationship(
            source=e1,
            target=e2,
            relation_type=RelationType.OUTPERFORMS,
            confidence=-0.5,  # confidence < 0.0
            context="Context",
            metadata={},
            id="r1"
        )


@pytest.mark.invalid
def test_relationship_with_same_source_and_target():
    """Test creating a relationship where source and target are the same entity."""
    # Create an entity
    e1 = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=0, end_pos=5, id="e1")
    
    # Creating a relationship where source and target are the same should raise a ValueError
    # (unless it's a self-relationship type)
    with pytest.raises(ValueError):
        relationship = Relationship(
            source=e1,
            target=e1,
            relation_type=RelationType.OUTPERFORMS,  # Not a self-relationship type
            confidence=0.9,
            context="Context",
            metadata={},
            id="r1"
        )


@pytest.mark.invalid
def test_relationship_with_incompatible_types():
    """Test creating a relationship with incompatible entity types."""
    # Create entities of different types
    e1 = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=0, end_pos=5, id="e1")
    e2 = Entity(text="John Smith", type=EntityType.AUTHOR, confidence=0.9, start_pos=10, end_pos=20, id="e2")
    
    # Creating a relationship with incompatible types for the given relation
    # Some relationship types have requirements for their source and target entity types
    # For example, TRAINED_ON typically requires MODEL -> DATASET
    extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    # This should warn about potentially incompatible types but not raise an error
    with pytest.warns(UserWarning, match="Potentially incompatible"):
        relationship = Relationship(
            source=e1,
            target=e2,
            relation_type=RelationType.TRAINED_ON,  # Typically MODEL -> DATASET
            confidence=0.9,
            context="Context",
            metadata={},
            id="r1"
        )


@pytest.mark.filter
def test_filter_by_nonexistent_relationship_type(edge_case_relationship_extractor, sample_unit_relationships):
    """Test filtering by a nonexistent relationship type."""
    # Create a custom relationship type that is not in the currently defined relationships
    non_existent_type = RelationType.COMPETES_WITH  # Assuming no COMPETES_WITH in the sample
    
    # Filter by this type
    filtered_relationships = edge_case_relationship_extractor.filter_relationships(
        sample_unit_relationships, 
        relation_types=[non_existent_type]
    )
    
    # Should return an empty list, not raise an error
    assert filtered_relationships == []