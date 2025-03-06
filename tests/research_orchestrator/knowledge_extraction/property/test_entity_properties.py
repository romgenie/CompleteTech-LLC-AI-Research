"""
Property-based tests for the Entity class and EntityRecognizer.

This module contains property-based tests using hypothesis to validate
that the Entity class and related functions maintain invariants and
properties across a wide range of inputs.
"""

import pytest
from hypothesis import given, strategies as st
import json

# Mark all tests in this module as property tests and entity related tests
pytestmark = [
    pytest.mark.property,
    pytest.mark.entity,
    pytest.mark.medium
]

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.entity_recognition.base_recognizer import EntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.ai_recognizer import AIEntityRecognizer


class TestEntityProperties:
    """Property-based tests for the Entity class."""

    @given(
        text=st.text(min_size=1, max_size=100),
        type_=st.sampled_from(list(EntityType)),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        start_pos=st.integers(min_value=0, max_value=1000),
        end_pos=st.integers(min_value=0, max_value=1000),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        ),
        id_=st.text(min_size=1, max_size=20)
    )
    def test_entity_serialization_roundtrip(self, text, type_, confidence, start_pos, end_pos, metadata, id_):
        """Test that Entity objects can be serialized to dict and back without data loss."""
        # Deal with start_pos and end_pos relationship
        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos
        
        # Create an entity
        entity = Entity(
            text=text,
            type=type_,
            confidence=confidence,
            start_pos=start_pos,
            end_pos=end_pos,
            metadata=metadata,
            id=id_
        )
        
        # Convert to dict
        entity_dict = entity.to_dict()
        
        # Convert back to entity
        entity2 = Entity.from_dict(entity_dict)
        
        # Check that the entity has the same properties after round trip
        assert entity2.id == entity.id
        assert entity2.text == entity.text
        assert entity2.type == entity.type
        assert entity2.confidence == entity.confidence
        assert entity2.start_pos == entity.start_pos
        assert entity2.end_pos == entity.end_pos
        assert entity2.metadata == entity.metadata
    
    @given(
        text=st.text(min_size=1, max_size=100),
        type_=st.sampled_from(list(EntityType)),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        start_pos=st.integers(min_value=0, max_value=1000),
        end_pos=st.integers(min_value=0, max_value=1000),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        ),
        id_=st.text(min_size=1, max_size=20)
    )
    def test_entity_json_serialization(self, text, type_, confidence, start_pos, end_pos, metadata, id_):
        """Test that Entity objects can be serialized to JSON and back without data loss."""
        # Deal with start_pos and end_pos relationship
        if start_pos > end_pos:
            start_pos, end_pos = end_pos, start_pos
        
        # Create an entity
        entity = Entity(
            text=text,
            type=type_,
            confidence=confidence,
            start_pos=start_pos,
            end_pos=end_pos,
            metadata=metadata,
            id=id_
        )
        
        # Convert to dict then to JSON
        entity_dict = entity.to_dict()
        entity_json = json.dumps(entity_dict)
        
        # Convert back from JSON to dict to entity
        entity_dict2 = json.loads(entity_json)
        entity2 = Entity.from_dict(entity_dict2)
        
        # Check that the entity has the same properties after JSON round trip
        assert entity2.id == entity.id
        assert entity2.text == entity.text
        assert entity2.type == entity.type
        assert entity2.confidence == entity.confidence
        assert entity2.start_pos == entity.start_pos
        assert entity2.end_pos == entity.end_pos
        assert entity2.metadata == entity.metadata
    
    @given(
        entities=st.lists(
            st.builds(
                Entity,
                text=st.text(min_size=1, max_size=50),
                type=st.sampled_from(list(EntityType)),
                confidence=st.floats(min_value=0.0, max_value=1.0),
                start_pos=st.integers(min_value=0, max_value=100),
                end_pos=st.integers(min_value=101, max_value=200),  # Ensure end_pos > start_pos
                metadata=st.fixed_dictionaries({}),
                id=st.text(min_size=1, max_size=20)
            ),
            min_size=0,
            max_size=10
        ),
        min_confidence=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_entity_filtering_by_confidence(self, entities, min_confidence):
        """Test that filtering entities by confidence works correctly."""
        # Create a mock entity recognizer
        class TestRecognizer(EntityRecognizer):
            def recognize(self, text):
                return []
        
        recognizer = TestRecognizer()
        
        # Filter entities
        filtered_entities = recognizer.filter_entities(entities, min_confidence=min_confidence)
        
        # Check that all filtered entities have confidence >= min_confidence
        assert all(entity.confidence >= min_confidence for entity in filtered_entities)
        
        # Check that all entities with confidence >= min_confidence are included
        high_confidence_count = sum(1 for entity in entities if entity.confidence >= min_confidence)
        assert len(filtered_entities) == high_confidence_count
    
    @given(
        entities=st.lists(
            st.builds(
                Entity,
                text=st.text(min_size=1, max_size=50),
                type=st.sampled_from(list(EntityType)),
                confidence=st.floats(min_value=0.0, max_value=1.0),
                start_pos=st.integers(min_value=0, max_value=100),
                end_pos=st.integers(min_value=101, max_value=200),  # Ensure end_pos > start_pos
                metadata=st.fixed_dictionaries({}),
                id=st.text(min_size=1, max_size=20)
            ),
            min_size=0,
            max_size=10
        ),
        entity_types=st.lists(
            st.sampled_from(list(EntityType)),
            min_size=1,
            max_size=len(EntityType)
        )
    )
    def test_entity_filtering_by_type(self, entities, entity_types):
        """Test that filtering entities by type works correctly."""
        # Create a mock entity recognizer
        class TestRecognizer(EntityRecognizer):
            def recognize(self, text):
                return []
        
        recognizer = TestRecognizer()
        
        # Filter entities
        filtered_entities = recognizer.filter_entities(entities, entity_types=entity_types)
        
        # Check that all filtered entities have a type in entity_types
        assert all(entity.type in entity_types for entity in filtered_entities)
        
        # Check that all entities with type in entity_types are included
        matching_type_count = sum(1 for entity in entities if entity.type in entity_types)
        assert len(filtered_entities) == matching_type_count
    
    @given(
        entities=st.lists(
            st.builds(
                Entity,
                text=st.text(min_size=1, max_size=50),
                type=st.sampled_from(list(EntityType)),
                confidence=st.floats(min_value=0.0, max_value=1.0),
                start_pos=st.integers(min_value=0, max_value=50),
                end_pos=st.integers(min_value=51, max_value=100),  # Ensure end_pos > start_pos
                metadata=st.fixed_dictionaries({}),
                id=st.text(min_size=1, max_size=20)
            ),
            min_size=2,
            max_size=10
        )
    )
    def test_merge_overlapping_entities_identity(self, entities):
        """Test that merge_overlapping_entities doesn't change non-overlapping entities."""
        # Create a mock entity recognizer
        class TestRecognizer(EntityRecognizer):
            def recognize(self, text):
                return []
        
        recognizer = TestRecognizer()
        
        # Since our strategy ensures no overlap, merged should be same as original
        merged_entities = recognizer.merge_overlapping_entities(entities)
        
        # Check that the merged list has the same entities (ignore order)
        assert sorted(merged_entities, key=lambda e: e.id) == sorted(entities, key=lambda e: e.id)


class TestEntityRecognizerProperties:
    """Property-based tests for the EntityRecognizer class."""
    
    @given(
        text=st.text(min_size=1, max_size=1000),
        min_confidence=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_ai_recognizer_confidence_filtering(self, text, min_confidence):
        """Test that AIEntityRecognizer correctly filters entities by confidence."""
        # Create an AI entity recognizer
        recognizer = AIEntityRecognizer()
        
        # Extract entities
        entities = recognizer.recognize(text)
        
        # Filter entities
        filtered_entities = recognizer.filter_entities(entities, min_confidence=min_confidence)
        
        # Check that all filtered entities have confidence >= min_confidence
        assert all(entity.confidence >= min_confidence for entity in filtered_entities)
        
        # Check that all entities with confidence >= min_confidence are included
        high_confidence_count = sum(1 for entity in entities if entity.confidence >= min_confidence)
        assert len(filtered_entities) == high_confidence_count