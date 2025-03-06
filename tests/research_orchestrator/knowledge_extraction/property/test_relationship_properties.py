"""
Property-based tests for the Relationship class and RelationshipExtractor.

This module contains property-based tests using hypothesis to validate
that the Relationship class and related functions maintain invariants and
properties across a wide range of inputs.
"""

import pytest
from hypothesis import given, strategies as st
import json

# Mark all tests in this module as property tests and relationship related tests
pytestmark = [
    pytest.mark.property,
    pytest.mark.relationship,
    pytest.mark.medium
]

from research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from research_orchestrator.knowledge_extraction.relationship_extraction.base_extractor import RelationshipExtractor
from research_orchestrator.knowledge_extraction.relationship_extraction.pattern_extractor import PatternRelationshipExtractor


# Helper strategy for generating entities
def entity_strategy():
    """Generate a random entity."""
    return st.builds(
        Entity,
        text=st.text(min_size=1, max_size=50),
        type=st.sampled_from(list(EntityType)),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        start_pos=st.integers(min_value=0, max_value=100),
        end_pos=st.integers(min_value=101, max_value=200),  # Ensure end_pos > start_pos
        metadata=st.fixed_dictionaries({}),
        id=st.text(min_size=1, max_size=20)
    )


class TestRelationshipProperties:
    """Property-based tests for the Relationship class."""

    @given(
        source=entity_strategy(),
        target=entity_strategy(),
        relation_type=st.sampled_from(list(RelationType)),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        context=st.text(min_size=0, max_size=200),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        ),
        id_=st.text(min_size=1, max_size=20)
    )
    def test_relationship_serialization_roundtrip(self, source, target, relation_type, confidence, context, metadata, id_):
        """Test that Relationship objects can be serialized to dict and back without data loss."""
        # Create a relationship
        relationship = Relationship(
            source=source,
            target=target,
            relation_type=relation_type,
            confidence=confidence,
            context=context,
            metadata=metadata,
            id=id_
        )
        
        # Convert to dict
        relationship_dict = relationship.to_dict()
        
        # Convert back to relationship
        relationship2 = Relationship.from_dict(relationship_dict)
        
        # Check that the relationship has the same properties after round trip
        assert relationship2.id == relationship.id
        assert relationship2.source.id == relationship.source.id
        assert relationship2.source.text == relationship.source.text
        assert relationship2.source.type == relationship.source.type
        assert relationship2.target.id == relationship.target.id
        assert relationship2.target.text == relationship.target.text
        assert relationship2.target.type == relationship.target.type
        assert relationship2.relation_type == relationship.relation_type
        assert relationship2.confidence == relationship.confidence
        assert relationship2.context == relationship.context
        assert relationship2.metadata == relationship.metadata
    
    @given(
        source=entity_strategy(),
        target=entity_strategy(),
        relation_type=st.sampled_from(list(RelationType)),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        context=st.text(min_size=0, max_size=200),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        ),
        id_=st.text(min_size=1, max_size=20)
    )
    def test_relationship_json_serialization(self, source, target, relation_type, confidence, context, metadata, id_):
        """Test that Relationship objects can be serialized to JSON and back without data loss."""
        # Create a relationship
        relationship = Relationship(
            source=source,
            target=target,
            relation_type=relation_type,
            confidence=confidence,
            context=context,
            metadata=metadata,
            id=id_
        )
        
        # Convert to dict then to JSON
        relationship_dict = relationship.to_dict()
        relationship_json = json.dumps(relationship_dict)
        
        # Convert back from JSON to dict to relationship
        relationship_dict2 = json.loads(relationship_json)
        relationship2 = Relationship.from_dict(relationship_dict2)
        
        # Check that the relationship has the same properties after JSON round trip
        assert relationship2.id == relationship.id
        assert relationship2.source.id == relationship.source.id
        assert relationship2.source.text == relationship.source.text
        assert relationship2.source.type == relationship.source.type
        assert relationship2.target.id == relationship.target.id
        assert relationship2.target.text == relationship.target.text
        assert relationship2.target.type == relationship.target.type
        assert relationship2.relation_type == relationship.relation_type
        assert relationship2.confidence == relationship.confidence
        assert relationship2.context == relationship.context
        assert relationship2.metadata == relationship.metadata
    
    @given(
        relationships=st.lists(
            st.builds(
                Relationship,
                source=entity_strategy(),
                target=entity_strategy(),
                relation_type=st.sampled_from(list(RelationType)),
                confidence=st.floats(min_value=0.0, max_value=1.0),
                context=st.text(min_size=0, max_size=200),
                metadata=st.fixed_dictionaries({}),
                id=st.text(min_size=1, max_size=20)
            ),
            min_size=0,
            max_size=10
        ),
        min_confidence=st.floats(min_value=0.0, max_value=1.0)
    )
    def test_relationship_filtering_by_confidence(self, relationships, min_confidence):
        """Test that filtering relationships by confidence works correctly."""
        # Create a mock relationship extractor
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        
        # Filter relationships
        filtered_relationships = extractor.filter_relationships(relationships, min_confidence=min_confidence)
        
        # Check that all filtered relationships have confidence >= min_confidence
        assert all(rel.confidence >= min_confidence for rel in filtered_relationships)
        
        # Check that all relationships with confidence >= min_confidence are included
        high_confidence_count = sum(1 for rel in relationships if rel.confidence >= min_confidence)
        assert len(filtered_relationships) == high_confidence_count
    
    @given(
        relationships=st.lists(
            st.builds(
                Relationship,
                source=entity_strategy(),
                target=entity_strategy(),
                relation_type=st.sampled_from(list(RelationType)),
                confidence=st.floats(min_value=0.0, max_value=1.0),
                context=st.text(min_size=0, max_size=200),
                metadata=st.fixed_dictionaries({}),
                id=st.text(min_size=1, max_size=20)
            ),
            min_size=0,
            max_size=10
        ),
        relation_types=st.lists(
            st.sampled_from(list(RelationType)),
            min_size=1,
            max_size=len(RelationType)
        )
    )
    def test_relationship_filtering_by_type(self, relationships, relation_types):
        """Test that filtering relationships by type works correctly."""
        # Create a mock relationship extractor
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        
        # Filter relationships
        filtered_relationships = extractor.filter_relationships(relationships, relation_types=relation_types)
        
        # Check that all filtered relationships have a relation_type in relation_types
        assert all(rel.relation_type in relation_types for rel in filtered_relationships)
        
        # Check that all relationships with relation_type in relation_types are included
        matching_type_count = sum(1 for rel in relationships if rel.relation_type in relation_types)
        assert len(filtered_relationships) == matching_type_count
    
    @given(
        relationships=st.lists(
            st.builds(
                Relationship,
                source=entity_strategy(),
                target=entity_strategy(),
                relation_type=st.sampled_from(list(RelationType)),
                confidence=st.floats(min_value=0.0, max_value=1.0),
                context=st.text(min_size=0, max_size=200),
                metadata=st.fixed_dictionaries({}),
                id=st.text(min_size=1, max_size=20)
            ),
            min_size=0,
            max_size=10
        ),
        min_confidence=st.floats(min_value=0.0, max_value=1.0),
        relation_types=st.lists(
            st.sampled_from(list(RelationType)),
            min_size=1,
            max_size=len(RelationType)
        )
    )
    def test_relationship_combined_filtering(self, relationships, min_confidence, relation_types):
        """Test that filtering relationships by both confidence and type works correctly."""
        # Create a mock relationship extractor
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        
        # Filter relationships
        filtered_relationships = extractor.filter_relationships(
            relationships, 
            min_confidence=min_confidence,
            relation_types=relation_types
        )
        
        # Check that all filtered relationships have a relation_type in relation_types and confidence >= min_confidence
        assert all(rel.relation_type in relation_types and rel.confidence >= min_confidence for rel in filtered_relationships)
        
        # Check that all relationships with relation_type in relation_types and confidence >= min_confidence are included
        matching_count = sum(1 for rel in relationships 
                            if rel.relation_type in relation_types and rel.confidence >= min_confidence)
        assert len(filtered_relationships) == matching_count


class TestRelationshipExtractorProperties:
    """Property-based tests for the RelationshipExtractor class."""
    
    @given(
        text=st.text(min_size=10, max_size=1000),
        entity1=entity_strategy(),
        entity2=entity_strategy()
    )
    def test_get_entity_pair_context(self, text, entity1, entity2):
        """Test that get_entity_pair_context correctly extracts context between entities."""
        # Create a mock relationship extractor
        class TestExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = TestExtractor()
        
        # Get context
        context = extractor.get_entity_pair_context(text, entity1, entity2)
        
        # Context should be a string
        assert isinstance(context, str)
        
        # If text contains both entity texts, they should be in the context
        if entity1.text in text and entity2.text in text:
            assert entity1.text in context
            assert entity2.text in context
    
    @given(
        text=st.text(min_size=50, max_size=1000),
        patterns=st.dictionaries(
            keys=st.sampled_from(list(RelationType)),
            values=st.lists(
                st.text(min_size=1, max_size=20),
                min_size=1,
                max_size=3
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_pattern_extractor_custom_patterns(self, text, patterns):
        """Test that PatternRelationshipExtractor correctly uses custom patterns."""
        # Create a pattern extractor with custom patterns
        extractor = PatternRelationshipExtractor()
        
        # Add custom patterns
        for relation_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                extractor.add_pattern(relation_type, pattern)
        
        # Check that the patterns were added
        for relation_type in patterns:
            assert relation_type in extractor.patterns
            
            # The extractor compiles patterns, so we can't directly check string equality
            # Instead, check that the pattern count is at least the number we added
            assert len(extractor.patterns[relation_type]) >= len(patterns[relation_type])