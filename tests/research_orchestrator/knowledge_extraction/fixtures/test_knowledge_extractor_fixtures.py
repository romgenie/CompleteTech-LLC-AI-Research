"""
Tests for the Knowledge Extractor module using pytest fixtures.
"""

import pytest
import os
import json
from unittest.mock import patch, Mock

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor


def test_process_document(knowledge_extractor, mock_document_processor):
    """Test processing a document."""
    content_dict = {
        "content": "GPT-4 was trained on a large dataset and evaluated on MMLU benchmark. "
                 "The model achieves 86.4% accuracy, outperforming previous models like GPT-3."
    }
    mock_document_processor.process_document.return_value = content_dict
    
    # Process the document
    content = knowledge_extractor.document_processor.process_document("test.pdf")
    
    # Verify results
    mock_document_processor.process_document.assert_called_once_with("test.pdf")
    assert content["content"] == content_dict["content"]


def test_extract_entities(knowledge_extractor, sample_entities):
    """Test extracting entities from text."""
    text = "Sample text"
    entities = knowledge_extractor.entity_recognizer.recognize(text)
    
    # Verify results
    knowledge_extractor.entity_recognizer.recognize.assert_called_once_with(text)
    assert entities == sample_entities


def test_extract_relationships(knowledge_extractor, sample_entities, sample_relationships):
    """Test extracting relationships from text and entities."""
    text = "Sample text"
    relationships = knowledge_extractor.relationship_extractor.extract_relationships(text, sample_entities)
    
    # Verify results
    knowledge_extractor.relationship_extractor.extract_relationships.assert_called_once_with(text, sample_entities)
    assert relationships == sample_relationships


def test_create_knowledge_graph(knowledge_extractor, sample_entities, sample_relationships):
    """Test creating a knowledge graph from entities and relationships."""
    doc_id = "test_doc"
    knowledge_graph = knowledge_extractor._create_knowledge_graph(
        sample_entities, sample_relationships, doc_id
    )
    
    # Verify graph structure
    assert "nodes" in knowledge_graph
    assert "edges" in knowledge_graph
    assert len(knowledge_graph["nodes"]) == len(sample_entities)
    assert len(knowledge_graph["edges"]) == len(sample_relationships)
    
    # Verify node properties
    for entity_id, node in knowledge_graph["nodes"].items():
        assert "id" in node
        assert "label" in node
        assert "type" in node
        assert "confidence" in node
    
    # Verify edge properties
    for rel_id, edge in knowledge_graph["edges"].items():
        assert "id" in edge
        assert "source" in edge
        assert "target" in edge
        assert "type" in edge
        assert "confidence" in edge


def test_save_results(knowledge_extractor, sample_entities, sample_relationships, temp_directory):
    """Test saving results to output directory."""
    doc_id = "test_doc"
    
    # Create knowledge graph
    knowledge_graph = knowledge_extractor._create_knowledge_graph(
        sample_entities, sample_relationships, doc_id
    )
    
    # Setup test data in the extractor
    knowledge_extractor.entities[doc_id] = sample_entities
    knowledge_extractor.relationships[doc_id] = sample_relationships
    knowledge_extractor.knowledge_graph[doc_id] = knowledge_graph
    
    # Add document to documents dictionary
    mock_doc = Mock()
    mock_doc.document_type = "pdf"
    knowledge_extractor.documents[doc_id] = mock_doc
    
    # Save the results
    result_dir = knowledge_extractor.save_extraction_results(temp_directory, doc_id)
    
    # Verify files were created
    stats_path = os.path.join(temp_directory, "extraction_statistics.json")
    test_dir = os.path.join(temp_directory, doc_id)
    
    assert os.path.exists(stats_path)
    assert os.path.exists(test_dir)
    assert os.path.exists(os.path.join(test_dir, "entities.json"))
    assert os.path.exists(os.path.join(test_dir, "relationships.json"))
    assert os.path.exists(os.path.join(test_dir, "knowledge_graph.json"))
    
    # Verify file contents
    with open(os.path.join(test_dir, "entities.json"), "r") as f:
        entities_data = json.load(f)
        assert len(entities_data) == len(sample_entities)
    
    with open(os.path.join(test_dir, "relationships.json"), "r") as f:
        relationships_data = json.load(f)
        assert len(relationships_data) == len(sample_relationships)
    
    with open(os.path.join(test_dir, "knowledge_graph.json"), "r") as f:
        graph_data = json.load(f)
        assert len(graph_data["nodes"]) == len(sample_entities)
        assert len(graph_data["edges"]) == len(sample_relationships)


def test_extract_from_document(knowledge_extractor, mock_document_processor):
    """Test extracting knowledge from a document."""
    # Configure the mock document processor to return a proper Document object
    from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import Document
    
    # Create a document with the test content
    test_content = "GPT-4 was trained on a large dataset and evaluated on MMLU benchmark."
    test_doc = Document(
        content=test_content,
        document_type="text",
        metadata={"author": "Test Author"},
        path="test.pdf"
    )
    
    # Have the mock return our document object
    mock_document_processor.process_document.return_value = test_doc
    
    # Patch the calls we want to skip testing
    with patch.object(knowledge_extractor.entity_recognizer, 'recognize') as mock_recognize, \
         patch.object(knowledge_extractor.entity_recognizer, 'filter_entities') as mock_filter_entities, \
         patch.object(knowledge_extractor.relationship_extractor, 'extract_relationships') as mock_extract_relationships, \
         patch.object(knowledge_extractor.relationship_extractor, 'filter_relationships') as mock_filter_relationships:
        
        # Configure mocks to return test data
        mock_recognize.return_value = []
        mock_filter_entities.return_value = []
        mock_extract_relationships.return_value = []
        mock_filter_relationships.return_value = []
        
        # Extract from document
        result = knowledge_extractor.extract_from_document("test.pdf")
        
        # Verify document processor was called
        mock_document_processor.process_document.assert_called_once_with("test.pdf")
        
        # Verify recognize was called with the document content
        mock_recognize.assert_called_once_with(test_content)
        
        # Verify result structure - basic validation
        assert "document_id" in result
        assert "document_type" in result
        assert "extraction_time" in result
        assert "entity_count" in result
        assert "relationship_count" in result
        
        # Verify the values match our expectations
        assert result["document_id"] == "test.pdf"
        assert result["document_type"] == "text"
        assert result["entity_count"] == 0
        assert result["relationship_count"] == 0


def test_get_extraction_statistics(knowledge_extractor, sample_entities, sample_relationships):
    """Test getting extraction statistics."""
    # Setup test data
    doc_id = "test_doc"
    knowledge_extractor.entities[doc_id] = sample_entities
    knowledge_extractor.relationships[doc_id] = sample_relationships
    knowledge_extractor.knowledge_graph[doc_id] = knowledge_extractor._create_knowledge_graph(
        sample_entities, sample_relationships, doc_id
    )
    
    # Add document to documents dictionary
    mock_doc = Mock()
    mock_doc.document_type = "pdf"
    knowledge_extractor.documents[doc_id] = mock_doc
    
    # Get statistics
    stats = knowledge_extractor.get_extraction_statistics()
    
    # Verify structure and counts
    for key in ["documents", "entities", "relationships", "knowledge_graph"]:
        assert key in stats
    
    assert stats["documents"]["count"] == 1
    assert stats["entities"]["count"] == len(sample_entities)
    assert stats["relationships"]["count"] == len(sample_relationships)
    
    assert "by_type" in stats["entities"]
    assert "by_type" in stats["relationships"]
    
    assert stats["entities"]["avg_confidence"] > 0
    assert stats["relationships"]["avg_confidence"] > 0


def test_create_knowledge_graph_empty(knowledge_extractor):
    """Test creating a knowledge graph with no entities or relationships."""
    # Create the knowledge graph with empty inputs
    doc_id = "test_doc"
    knowledge_graph = knowledge_extractor._create_knowledge_graph([], [], doc_id)
    
    # Check structure and counts
    assert "nodes" in knowledge_graph
    assert "edges" in knowledge_graph
    assert "metadata" in knowledge_graph
    
    assert len(knowledge_graph["nodes"]) == 0
    assert len(knowledge_graph["edges"]) == 0
    

def test_create_knowledge_graph_with_entities(knowledge_extractor, sample_entities):
    """Test creating a knowledge graph with entities."""
    # Use the sample_entities fixture instead of creating new entities
    
    # Create the knowledge graph
    doc_id = "test_doc"
    knowledge_graph = knowledge_extractor._create_knowledge_graph(sample_entities, [], doc_id)
    
    # Check basic structure
    assert "nodes" in knowledge_graph
    assert "edges" in knowledge_graph
    
    # Check node content
    assert len(knowledge_graph["nodes"]) == len(sample_entities)  # Should have one node for each entity
    assert len(knowledge_graph["edges"]) == 0  # No relationships means no edges
    
    # Check that node properties are correctly transferred from entities
    for entity in sample_entities:
        assert entity.id in knowledge_graph["nodes"]
        node = knowledge_graph["nodes"][entity.id]
        assert node["text"] == entity.text
        assert node["type"] == entity.type.value  # EntityType enum is converted to string value
        assert node["confidence"] == entity.confidence
        assert "metadata" in node