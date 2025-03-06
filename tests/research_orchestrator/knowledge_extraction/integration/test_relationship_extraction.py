"""
Integration tests for relationship extraction components.

This module contains tests that validate the extraction of relationships between
entities in text content, focusing on the integration points between entity
recognition and relationship extraction.
"""

import pytest

# Mark all tests in this module as integration tests and relationship related tests
pytestmark = [
    pytest.mark.integration,
    pytest.mark.relationship,
    pytest.mark.entity,
    pytest.mark.medium
]
import os
import json
import tempfile
from unittest.mock import patch

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import RelationType


def test_relationship_extraction_from_recognized_entities(integration_test_data, entity_recognizer, relationship_extractor):
    """Test extracting relationships from recognized entities."""
    # Get test data from fixtures
    test_text = integration_test_data["test_text"]
    expected_relationship_types = integration_test_data["expected_relationship_types"]
    
    # Recognize entities
    entities = entity_recognizer.recognize(test_text)
    
    # Verify entities were found
    assert len(entities) > 0, "No entities were recognized"
    
    # Extract relationships
    relationships = relationship_extractor.extract_relationships(test_text, entities)
    
    # Check that some relationships were found
    assert len(relationships) > 0, "No relationships were extracted"
    
    # Check that at least one of the expected relationship types was found
    found_types = {r.relation_type for r in relationships}
    assert any(t in found_types for t in expected_relationship_types), \
        f"None of the expected relationship types were found. Found: {found_types}"
    
    # Check that the relationships are between the recognized entities
    for relationship in relationships:
        assert relationship.source.id in {e.id for e in entities}
        assert relationship.target.id in {e.id for e in entities}
        
    # Check for specific model-organization relationships
    model_to_org_relationships = [r for r in relationships 
                                if r.source.type == EntityType.MODEL 
                                and r.target.type == EntityType.ORGANIZATION
                                and r.relation_type == RelationType.DEVELOPED_BY]
    
    # Should find relationships like "GPT-4 developed_by OpenAI" or "BERT developed_by Google"
    if model_to_org_relationships:
        for rel in model_to_org_relationships:
            print(f"Found relationship: {rel.source.text} {rel.relation_type} {rel.target.text}")
            
        # Check for specific expected relationships
        expected_pairs = [
            ("GPT", "OpenAI"),
            ("BERT", "Google")
        ]
        
        found_expected = False
        for expected_model, expected_org in expected_pairs:
            for rel in model_to_org_relationships:
                if (expected_model.lower() in rel.source.text.lower() and 
                    expected_org.lower() in rel.target.text.lower()):
                    found_expected = True
                    break
        
        assert found_expected, f"None of the expected model-organization pairs {expected_pairs} were found"


def test_combined_extractor_integration(integration_test_data, entity_recognizer, combined_relationship_extractor):
    """Test the combined relationship extractor with recognized entities."""
    # Get test data from fixtures
    test_text = integration_test_data["test_text"]
    
    # Recognize entities
    entities = entity_recognizer.recognize(test_text)
    
    # Extract relationships with combined extractor
    relationships = combined_relationship_extractor.extract_relationships(test_text, entities)
    
    # Verify relationships were found
    assert len(relationships) > 0, "No relationships were found by combined extractor"
    
    # Check relationship properties
    for relationship in relationships:
        # Basic validation
        assert relationship.id is not None
        assert relationship.source is not None
        assert relationship.target is not None
        assert relationship.relation_type is not None
        assert 0.0 <= relationship.confidence <= 1.0
        assert relationship.context is not None
        
        # Source and target should be from our entities
        assert relationship.source.id in {e.id for e in entities}
        assert relationship.target.id in {e.id for e in entities}
        
        # Context should contain both source and target
        assert relationship.source.text in relationship.context
        assert relationship.target.text in relationship.context


def test_relationship_filtering_integration(integration_test_data, entity_recognizer, relationship_extractor):
    """Test filtering relationships by confidence and type."""
    # Get test data from fixtures
    test_text = integration_test_data["test_text"]
    
    # Recognize entities
    entities = entity_recognizer.recognize(test_text)
    
    # Extract relationships
    relationships = relationship_extractor.extract_relationships(test_text, entities)
    
    # Verify relationships were found
    assert len(relationships) > 0, "No relationships were found"
    
    # Filter by confidence
    high_confidence = relationship_extractor.filter_relationships(relationships, min_confidence=0.8)
    low_confidence = relationship_extractor.filter_relationships(relationships, min_confidence=0.5)
    
    # High confidence should be a subset of low confidence
    assert len(high_confidence) <= len(low_confidence)
    
    # Filter by relationship type
    developed_by = relationship_extractor.filter_relationships(
        relationships, relation_types=[RelationType.DEVELOPED_BY]
    )
    
    # All filtered relationships should be of the specified type
    assert all(r.relation_type == RelationType.DEVELOPED_BY for r in developed_by)
    
    # Combined filtering
    high_confidence_developed_by = relationship_extractor.filter_relationships(
        relationships, 
        min_confidence=0.8, 
        relation_types=[RelationType.DEVELOPED_BY]
    )
    
    # Check that combined filtering works correctly
    assert all(r.relation_type == RelationType.DEVELOPED_BY and r.confidence >= 0.8 
              for r in high_confidence_developed_by)


def test_entity_pair_relationship_extraction(integration_test_data, entity_recognizer, relationship_extractor):
    """Test extracting relationships between specific entity pairs."""
    # Get test data from fixtures
    test_text = integration_test_data["test_text"]
    
    # Recognize entities
    entities = entity_recognizer.recognize(test_text)
    
    # Find model and organization entities
    models = [e for e in entities if e.type == EntityType.MODEL]
    organizations = [e for e in entities if e.type == EntityType.ORGANIZATION]
    
    # Skip test if we don't have both types
    if not models or not organizations:
        pytest.skip("Not enough entity types found for this test")
    
    # Get a model and an organization
    model = models[0]
    organization = organizations[0]
    
    # Get context between the entities
    context = relationship_extractor.get_entity_pair_context(test_text, model, organization)
    
    # Check that context contains both entities
    assert model.text in context
    assert organization.text in context
    
    # Find entity pairs by proximity
    pairs = relationship_extractor.find_entity_pairs(entities, max_distance=100)
    
    # Should find some pairs
    assert len(pairs) > 0, "No entity pairs found"
    
    # Extract relationships for just these pairs
    pair_relationships = []
    for source, target in pairs:
        # Get context for this pair
        pair_context = relationship_extractor.get_entity_pair_context(test_text, source, target)
        
        # Check for developed_by pattern (very simplified)
        if (source.type == EntityType.MODEL and 
            target.type == EntityType.ORGANIZATION and 
            "developed by" in pair_context.lower()):
            
            pair_relationships.append((source, target, RelationType.DEVELOPED_BY))
    
    # Test is informational - we don't assert on the results since it depends on the text
    if pair_relationships:
        print(f"Found {len(pair_relationships)} developed_by relationships from entity pairs")
        for source, target, rel_type in pair_relationships:
            print(f"  {source.text} {rel_type} {target.text}")


def test_relationship_serialization_integration(integration_test_data, entity_recognizer, relationship_extractor):
    """Test serialization and deserialization of extracted relationships."""
    # Get test data from fixtures
    test_text = integration_test_data["test_text"]
    
    # Recognize entities
    entities = entity_recognizer.recognize(test_text)
    
    # Extract relationships
    relationships = relationship_extractor.extract_relationships(test_text, entities)
    
    # Verify relationships were found
    assert len(relationships) > 0, "No relationships were found"
    
    # Create a temporary directory for serialization testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Serialize all relationships to JSON
        relationships_path = os.path.join(temp_dir, "relationships.json")
        with open(relationships_path, "w") as f:
            json.dump([r.to_dict() for r in relationships], f, indent=2)
        
        # Read relationships back from JSON
        with open(relationships_path, "r") as f:
            relationship_dicts = json.load(f)
        
        # Deserialize relationships
        from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship
        loaded_relationships = [Relationship.from_dict(r_dict) for r_dict in relationship_dicts]
        
        # Verify relationships were properly serialized and deserialized
        assert len(loaded_relationships) == len(relationships)
        
        # Compare a few key properties
        for i, relationship in enumerate(relationships):
            loaded = loaded_relationships[i]
            assert loaded.id == relationship.id
            assert loaded.relation_type == relationship.relation_type
            assert loaded.source.text == relationship.source.text
            assert loaded.target.text == relationship.target.text
            assert loaded.confidence == relationship.confidence