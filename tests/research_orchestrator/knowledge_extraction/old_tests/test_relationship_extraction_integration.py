"""
Integration tests for the relationship extraction components.

This module contains tests that validate the extraction of relationships between
entities in text content, focusing on the integration points between:
1. Multiple relationship extractor types
2. Entity recognition and relationship extraction
3. Extraction and filtering capabilities
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
from src.research_orchestrator.knowledge_extraction.relationship_extraction.base_extractor import RelationshipExtractor


def test_pattern_extractor_integration(integration_fixtures):
    """Test that pattern extractor can identify basic relationships from text."""
    # Get test data from fixtures
    test_text = integration_fixtures["test_text"]
    test_entities = integration_fixtures["test_entities"]
    expected_relationship_types = integration_fixtures["expected_relationship_types"]
    
    # Create pattern extractor
    extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    # Extract relationships
    relationships = extractor.extract_relationships(test_text, test_entities)
    
    # Check that some relationships were found
    assert len(relationships) > 0, "No relationships were found by the pattern extractor"
    
    # Check that at least one of the expected relationship types was found
    found_types = {r.relation_type for r in relationships}
    assert any(t in found_types for t in expected_relationship_types), \
        f"None of the expected relationship types were found. Found: {found_types}"


def test_ai_extractor_integration(integration_fixtures):
    """Test that AI extractor can identify domain-specific relationships."""
    # Get test data from fixtures
    test_text = integration_fixtures["test_text"]
    test_entities = integration_fixtures["test_entities"]
    expected_relationship_types = integration_fixtures["expected_relationship_types"]
    
    # Create AI relationship extractor
    extractor = RelationshipExtractorFactory.create_extractor("ai")
    
    # Extract relationships
    relationships = extractor.extract_relationships(test_text, test_entities)
    
    # Check that some relationships were found
    assert len(relationships) > 0, "No relationships were found by the AI extractor"
    
    # Check found relationship types
    found_types = {r.relation_type for r in relationships}
    assert any(t in found_types for t in expected_relationship_types), \
        f"None of the expected relationship types were found. Found: {found_types}"
    
    # Check that the relationships are between the correct entities
    for rel in relationships:
        # Verify that source and target are from our test entities
        assert rel.source.id in [e.id for e in test_entities]
        assert rel.target.id in [e.id for e in test_entities]


def test_combined_extractor_integration(integration_fixtures):
    """Test that combined extractor integrates results from multiple extractors."""
    # Get test data from fixtures
    test_text = integration_fixtures["test_text"]
    test_entities = integration_fixtures["test_entities"]
    
    # Create extractors
    pattern_extractor = RelationshipExtractorFactory.create_extractor("pattern")
    ai_extractor = RelationshipExtractorFactory.create_extractor("ai")
    
    # Extract relationships with individual extractors
    pattern_relationships = pattern_extractor.extract_relationships(test_text, test_entities)
    ai_relationships = ai_extractor.extract_relationships(test_text, test_entities)
    
    # Create combined extractor with both extractors
    combined_extractor = RelationshipExtractorFactory.create_extractor(
        "combined", 
        config={"extractors": [
            {"type": "pattern"},
            {"type": "ai"}
        ]}
    )
    
    # Extract with combined extractor
    combined_relationships = combined_extractor.extract_relationships(test_text, test_entities)
    
    # Check that combined extractor found relationships
    assert len(combined_relationships) > 0, "No relationships found by combined extractor"
    
    # The combined extractor should find at least as many unique relationships as the best individual extractor
    # We compare by unique source-target-type combinations to account for potential duplicates
    def relationship_key(rel):
        return (rel.source.id, rel.target.id, rel.relation_type)
    
    unique_pattern = {relationship_key(r) for r in pattern_relationships}
    unique_ai = {relationship_key(r) for r in ai_relationships}
    unique_combined = {relationship_key(r) for r in combined_relationships}
    
    best_individual_count = max(len(unique_pattern), len(unique_ai))
    assert len(unique_combined) >= best_individual_count, \
        f"Combined extractor found {len(unique_combined)} unique relationships, " \
        f"but best individual extractor found {best_individual_count}"


def test_relationship_filtering(integration_fixtures):
    """Test filtering relationships by confidence and type."""
    # Get test entities
    test_entities = integration_fixtures["test_entities"]
    
    # Create relationships with different confidence scores and types
    relationships = [
        Relationship(
            source=test_entities[0],  # GPT-4
            target=test_entities[1],  # OpenAI
            relation_type=RelationType.DEVELOPED_BY,
            confidence=0.9,
            context="GPT-4 is developed by OpenAI",
            id="r1"
        ),
        Relationship(
            source=test_entities[0],  # GPT-4
            target=test_entities[2],  # GPT-3.5
            relation_type=RelationType.OUTPERFORMS,
            confidence=0.7,
            context="GPT-4 outperforms GPT-3.5",
            id="r2"
        ),
        Relationship(
            source=test_entities[0],  # GPT-4
            target=test_entities[3],  # MMLU
            relation_type=RelationType.EVALUATED_ON,
            confidence=0.5,
            context="GPT-4 was evaluated on MMLU",
            id="r3"
        )
    ]
    
    # Create a relationship extractor for filtering
    extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    # Test filtering by confidence
    high_confidence = extractor.filter_relationships(relationships, min_confidence=0.8)
    assert len(high_confidence) == 1
    assert high_confidence[0].id == "r1"
    
    medium_confidence = extractor.filter_relationships(relationships, min_confidence=0.6)
    assert len(medium_confidence) == 2
    assert {r.id for r in medium_confidence} == {"r1", "r2"}
    
    # Test filtering by relationship type
    developed_by = extractor.filter_relationships(relationships, relation_types=[RelationType.DEVELOPED_BY])
    assert len(developed_by) == 1
    assert developed_by[0].relation_type == RelationType.DEVELOPED_BY
    
    performance = extractor.filter_relationships(relationships, 
                                                relation_types=[RelationType.OUTPERFORMS, RelationType.EVALUATED_ON])
    assert len(performance) == 2
    assert {r.relation_type for r in performance} == {RelationType.OUTPERFORMS, RelationType.EVALUATED_ON}
    
    # Test combined filtering
    filtered = extractor.filter_relationships(relationships, 
                                            min_confidence=0.7, 
                                            relation_types=[RelationType.DEVELOPED_BY, RelationType.OUTPERFORMS])
    assert len(filtered) == 2
    assert {r.id for r in filtered} == {"r1", "r2"}


def test_entity_pair_relationship_extraction(integration_fixtures):
    """Test extracting relationships between specific entity pairs."""
    # Get test data
    test_text = integration_fixtures["test_text"]
    test_entities = integration_fixtures["test_entities"]
    
    # Get specific entity pairs we want to test
    gpt4 = test_entities[0]  # GPT-4
    openai = test_entities[1]  # OpenAI
    gpt35 = test_entities[2]  # GPT-3.5
    
    # Create extractor
    extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    # Get context between GPT-4 and OpenAI
    gpt4_openai_context = extractor.get_entity_pair_context(test_text, gpt4, openai)
    assert "GPT-4" in gpt4_openai_context
    assert "OpenAI" in gpt4_openai_context
    
    # Get context between GPT-4 and GPT-3.5
    gpt4_gpt35_context = extractor.get_entity_pair_context(test_text, gpt4, gpt35)
    assert "GPT-4" in gpt4_gpt35_context
    assert "GPT-3.5" in gpt4_gpt35_context
    assert "outperforms" in gpt4_gpt35_context.lower()
    
    # Test finding entity pairs by proximity
    pairs = extractor.find_entity_pairs(test_entities, max_distance=100)
    # Should include at least the GPT-4→OpenAI and GPT-4→GPT-3.5 pairs
    assert len(pairs) >= 2
    
    # Check for specific pairs
    gpt4_openai_found = False
    gpt4_gpt35_found = False
    
    for source, target in pairs:
        if source.text == "GPT-4" and target.text == "OpenAI":
            gpt4_openai_found = True
        elif source.text == "GPT-4" and target.text == "GPT-3.5":
            gpt4_gpt35_found = True
            
    assert gpt4_openai_found, "GPT-4→OpenAI pair not found"
    assert gpt4_gpt35_found, "GPT-4→GPT-3.5 pair not found"


def test_relationship_serialization(integration_fixtures):
    """Test serialization and deserialization of relationships."""
    # Get test entities
    test_entities = integration_fixtures["test_entities"]
    
    # Create a relationship
    relationship = Relationship(
        source=test_entities[0],  # GPT-4
        target=test_entities[1],  # OpenAI
        relation_type=RelationType.DEVELOPED_BY,
        confidence=0.9,
        context="GPT-4 is developed by OpenAI",
        id="r1"
    )
    
    # Serialize to dictionary
    relationship_dict = relationship.to_dict()
    
    # Check dictionary contents
    assert relationship_dict["id"] == "r1"
    assert relationship_dict["relation_type"] == "developed_by"
    assert relationship_dict["confidence"] == 0.9
    assert relationship_dict["context"] == "GPT-4 is developed by OpenAI"
    assert relationship_dict["source"]["text"] == "GPT-4"
    assert relationship_dict["target"]["text"] == "OpenAI"
    
    # Deserialize back to relationship
    new_relationship = Relationship.from_dict(relationship_dict)
    
    # Verify the round trip
    assert new_relationship.id == relationship.id
    assert new_relationship.relation_type == relationship.relation_type
    assert new_relationship.confidence == relationship.confidence
    assert new_relationship.context == relationship.context
    assert new_relationship.source.text == relationship.source.text
    assert new_relationship.target.text == relationship.target.text
    
    # Test serialization to JSON
    with tempfile.TemporaryDirectory() as temp_dir:
        json_path = os.path.join(temp_dir, "relationship.json")
        
        # Write to JSON
        with open(json_path, "w") as f:
            json.dump(relationship_dict, f)
        
        # Read from JSON
        with open(json_path, "r") as f:
            loaded_dict = json.load(f)
        
        # Create relationship from loaded data
        loaded_relationship = Relationship.from_dict(loaded_dict)
        
        # Verify
        assert loaded_relationship.id == relationship.id
        assert loaded_relationship.relation_type == relationship.relation_type
        assert loaded_relationship.source.text == relationship.source.text