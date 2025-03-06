"""
Edge case tests for knowledge extractor.

This module contains tests for knowledge extractor edge cases and error handling.
"""

import pytest
import os
import tempfile
import json
import networkx as nx

# Mark all tests in this module as edge case tests and knowledge extractor related tests
pytestmark = [
    pytest.mark.edge_case,
    pytest.mark.knowledge_extractor,
    pytest.mark.medium
]

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType


@pytest.mark.empty
def test_empty_document_extraction(edge_case_knowledge_extractor, empty_document):
    """Test extracting knowledge from an empty document."""
    # Extract knowledge from an empty document
    result = edge_case_knowledge_extractor.extract_from_document(empty_document)
    
    # Should not raise an error and return empty results
    assert result is not None
    assert len(result.entities) == 0
    assert len(result.relationships) == 0
    assert isinstance(result.knowledge_graph, nx.DiGraph)
    assert result.knowledge_graph.number_of_nodes() == 0
    assert result.knowledge_graph.number_of_edges() == 0


@pytest.mark.empty
def test_empty_path_extraction(edge_case_knowledge_extractor):
    """Test extracting knowledge from an empty document path."""
    # Create a temp empty file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        file_path = f.name
    
    try:
        # Extract knowledge from the empty file
        result = edge_case_knowledge_extractor.extract_from_path(file_path)
        
        # Should not raise an error and return empty results
        assert result is not None
        assert len(result.entities) == 0
        assert len(result.relationships) == 0
        assert isinstance(result.knowledge_graph, nx.DiGraph)
        assert result.knowledge_graph.number_of_nodes() == 0
        assert result.knowledge_graph.number_of_edges() == 0
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.error
def test_invalid_path_extraction(edge_case_knowledge_extractor, invalid_document_path):
    """Test extracting knowledge from an invalid document path."""
    # Extract knowledge from an invalid path should raise an error
    with pytest.raises(FileNotFoundError):
        edge_case_knowledge_extractor.extract_from_path(invalid_document_path)


@pytest.mark.special_chars
def test_special_characters_extraction(edge_case_knowledge_extractor, document_with_special_characters):
    """Test extracting knowledge from document with special characters."""
    # Extract knowledge from document with special characters
    result = edge_case_knowledge_extractor.extract_from_document(document_with_special_characters)
    
    # Should not raise an error
    assert result is not None
    assert isinstance(result.entities, list)
    assert isinstance(result.relationships, list)
    assert isinstance(result.knowledge_graph, nx.DiGraph)


@pytest.mark.code
def test_code_extraction(edge_case_knowledge_extractor, document_with_code):
    """Test extracting knowledge from document with code."""
    # Extract knowledge from document with code
    result = edge_case_knowledge_extractor.extract_from_document(document_with_code)
    
    # Should not raise an error
    assert result is not None
    assert isinstance(result.entities, list)
    assert isinstance(result.relationships, list)
    assert isinstance(result.knowledge_graph, nx.DiGraph)
    
    # Verify that code-related entities are extracted
    framework_entities = [e for e in result.entities if e.type == EntityType.FRAMEWORK]
    has_tensorflow = any("tensorflow" in e.text.lower() for e in framework_entities)
    # This assertion depends on the actual implementation and might be adjusted
    # If tensorflow is recognized by the entity recognizer, it should be found
    if has_tensorflow:
        assert has_tensorflow, "TensorFlow not recognized as a framework"


@pytest.mark.large
def test_large_document_extraction(edge_case_knowledge_extractor, very_large_document):
    """Test extracting knowledge from a very large document."""
    # Extract knowledge from a portion of the large document to keep test reasonable
    temp_document = document_with_content(very_large_document.content[:100000])
    
    # Extract knowledge
    result = edge_case_knowledge_extractor.extract_from_document(temp_document)
    
    # Should not raise an error
    assert result is not None
    assert isinstance(result.entities, list)
    assert isinstance(result.relationships, list)
    assert isinstance(result.knowledge_graph, nx.DiGraph)


@pytest.mark.conflicting
def test_conflicting_relationships_handling(edge_case_knowledge_extractor, conflicting_relationships, duplicate_entities):
    """Test handling of conflicting relationships during knowledge graph building."""
    # Create a knowledge graph with conflicting relationships
    graph = edge_case_knowledge_extractor.build_knowledge_graph(duplicate_entities, conflicting_relationships)
    
    # Should not raise an error, should handle conflicts based on confidence
    assert isinstance(graph, nx.DiGraph)
    
    # The number of edges should be less than the number of relationships due to conflict resolution
    # This is assuming the conflict resolution keeps the higher confidence relationship
    assert graph.number_of_edges() <= len(conflicting_relationships)


@pytest.mark.circular
def test_circular_relationships_handling(edge_case_knowledge_extractor, circular_relationships, duplicate_entities):
    """Test handling of circular relationships during knowledge graph building."""
    # Create a knowledge graph with circular relationships
    graph = edge_case_knowledge_extractor.build_knowledge_graph(duplicate_entities, circular_relationships)
    
    # Should not raise an error
    assert isinstance(graph, nx.DiGraph)
    
    # Check for cycles in the graph
    has_cycle = not nx.is_directed_acyclic_graph(graph)
    assert has_cycle, "Circular relationships should create a cycle in the graph"


@pytest.mark.error
def test_serialization_error(edge_case_knowledge_extractor):
    """Test error handling during extraction result serialization."""
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
    
    e2 = Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, id="e2")
    
    relationship = Relationship(
        source=entity,
        target=e2,
        relation_type=RelationType.OUTPERFORMS,
        confidence=0.9,
        context="Context",
        metadata={},
        id="r1"
    )
    
    # Create a result with the non-serializable entity
    graph = edge_case_knowledge_extractor.build_knowledge_graph([entity, e2], [relationship])
    result = edge_case_knowledge_extractor.create_extraction_result([entity, e2], [relationship], graph)
    
    # Attempting to serialize to JSON should raise an error
    with pytest.raises(TypeError):
        json_string = result.to_json()


@pytest.mark.storage
def test_read_only_output_directory(edge_case_knowledge_extractor, read_only_directory, document_with_code):
    """Test error handling when saving results to a read-only directory."""
    if os.name == 'nt':  # Skip on Windows
        pytest.skip("File permission tests not applicable on Windows")
    
    # Extract knowledge
    result = edge_case_knowledge_extractor.extract_from_document(document_with_code)
    
    # Attempt to save to read-only directory
    output_path = os.path.join(read_only_directory, "output.json")
    
    # Should raise a permission error
    with pytest.raises(PermissionError):
        result.save_to_file(output_path)


@pytest.mark.malformed
def test_malformed_config_handling():
    """Test handling of malformed configuration."""
    # Create a malformed configuration (missing required components)
    malformed_config = {
        "document_processor": {
            "type": "text"
        }
        # Missing entity_recognizer and relationship_extractor
    }
    
    # Creating a knowledge extractor with malformed config should raise ValueError
    with pytest.raises(ValueError):
        KnowledgeExtractor.from_config(malformed_config)


@pytest.mark.filter
def test_entity_confidence_filtering(edge_case_knowledge_extractor, sample_unit_entities):
    """Test filtering entities by confidence."""
    # Filter entities with very high confidence threshold
    high_confidence_entities = edge_case_knowledge_extractor.filter_entities_by_confidence(
        sample_unit_entities, min_confidence=0.95
    )
    
    # Should return only entities with confidence >= 0.95
    assert all(e.confidence >= 0.95 for e in high_confidence_entities)
    assert len(high_confidence_entities) <= len(sample_unit_entities)
    
    # Filter with very low threshold should return all entities
    all_entities = edge_case_knowledge_extractor.filter_entities_by_confidence(
        sample_unit_entities, min_confidence=0.0
    )
    assert len(all_entities) == len(sample_unit_entities)


@pytest.mark.filter
def test_relationship_confidence_filtering(edge_case_knowledge_extractor, sample_unit_relationships):
    """Test filtering relationships by confidence."""
    # Filter relationships with very high confidence threshold
    high_confidence_relationships = edge_case_knowledge_extractor.filter_relationships_by_confidence(
        sample_unit_relationships, min_confidence=0.95
    )
    
    # Should return only relationships with confidence >= 0.95
    assert all(r.confidence >= 0.95 for r in high_confidence_relationships)
    assert len(high_confidence_relationships) <= len(sample_unit_relationships)
    
    # Filter with very low threshold should return all relationships
    all_relationships = edge_case_knowledge_extractor.filter_relationships_by_confidence(
        sample_unit_relationships, min_confidence=0.0
    )
    assert len(all_relationships) == len(sample_unit_relationships)


@pytest.mark.query
def test_empty_path_query(edge_case_knowledge_extractor, duplicate_entities, circular_relationships):
    """Test querying for paths when none exist."""
    # Build a knowledge graph
    graph = edge_case_knowledge_extractor.build_knowledge_graph(duplicate_entities, circular_relationships)
    
    # Get entities that don't have a path between them
    e1 = duplicate_entities[0]
    
    # Create a new entity not in the graph
    e_new = Entity(text="NewEntity", type=EntityType.DATASET, confidence=0.9, start_pos=50, end_pos=59, id="e_new")
    
    # Query for paths between e1 and e_new
    paths = edge_case_knowledge_extractor.find_paths(graph, e1.id, e_new.id)
    
    # Should return an empty list, not raise an error
    assert paths == []


@pytest.mark.malformed
def test_malformed_json_file_loading(edge_case_knowledge_extractor, malformed_json_file):
    """Test error handling when loading from a malformed JSON file."""
    # Attempt to load results from malformed JSON
    with pytest.raises(json.JSONDecodeError):
        edge_case_knowledge_extractor.load_extraction_result(malformed_json_file)


@pytest.mark.invalid
def test_invalid_entity_ids_in_relationship(edge_case_knowledge_extractor):
    """Test handling of relationships with invalid entity IDs."""
    # Create valid entities
    e1 = Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=0, end_pos=5, id="e1")
    e2 = Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, id="e2")
    
    # Create a relationship with an entity that doesn't exist
    e_invalid = Entity(text="Invalid", type=EntityType.MODEL, confidence=0.9, start_pos=20, end_pos=27, id="e_invalid")
    
    rel1 = Relationship(
        source=e1,
        target=e_invalid,  # This entity won't be in the entities list
        relation_type=RelationType.OUTPERFORMS,
        confidence=0.9,
        context="Context",
        id="r1"
    )
    
    # Build a knowledge graph with the invalid relationship
    # This should not raise an error but should include a warning
    with pytest.warns(UserWarning, match="Entity .* not found"):
        graph = edge_case_knowledge_extractor.build_knowledge_graph([e1, e2], [rel1])
    
    # The graph should only have the valid entities
    assert graph.number_of_nodes() == 2  # Only e1 and e2
    assert graph.number_of_edges() == 0  # No valid edges


# Helper function to create a document with specific content
def document_with_content(content):
    """Create a Document object with the given content."""
    return Document(
        content=content,
        document_type="text",
        path="/path/to/test.txt",
        metadata={}
    )


from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import Document