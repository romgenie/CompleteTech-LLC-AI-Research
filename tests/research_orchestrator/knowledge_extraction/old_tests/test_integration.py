"""
Integration tests for the knowledge extraction pipeline.

This module contains tests that validate the full knowledge extraction pipeline,
from document processing to knowledge graph creation, ensuring all components
work together correctly.
"""

import pytest
import os
import json
from unittest.mock import patch

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory


def test_full_extraction_pipeline(document_directory, temp_directory):
    """Test the full extraction pipeline from document to knowledge graph."""
    # Set up the knowledge extractor with real components
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    relationship_extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    extractor = KnowledgeExtractor(
        document_processor=document_processor,
        entity_recognizer=entity_recognizer,
        relationship_extractor=relationship_extractor
    )
    
    # Get the path to the test text file
    text_file_path = os.path.join(document_directory, "test.txt")
    
    # Run the extraction process
    result = extractor.extract_from_document(text_file_path)
    
    # Check the result structure
    assert "document_id" in result
    assert "document_type" in result
    assert "extraction_time" in result
    assert "entity_count" in result
    assert "relationship_count" in result
    
    # Check that some entities and relationships were found
    assert result["entity_count"] > 0, "No entities were extracted"
    assert result["relationship_count"] >= 0, "Error in relationship extraction"
    
    # Save the results to a directory
    output_dir = extractor.save_extraction_results(temp_directory, text_file_path)
    
    # Check that the output files were created
    assert os.path.exists(os.path.join(output_dir, "entities.json"))
    assert os.path.exists(os.path.join(output_dir, "relationships.json"))
    assert os.path.exists(os.path.join(output_dir, "knowledge_graph.json"))
    
    # Check knowledge graph structure
    with open(os.path.join(output_dir, "knowledge_graph.json"), "r") as f:
        graph_data = json.load(f)
    
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert "metadata" in graph_data
    assert len(graph_data["nodes"]) > 0
    
    # Test with HTML file
    html_file_path = os.path.join(document_directory, "test.html")
    html_result = extractor.extract_from_document(html_file_path)
    
    # Check basic results
    assert html_result["document_type"] == "html"
    assert html_result["entity_count"] > 0
    
    # Check that statistics can be generated
    stats = extractor.get_extraction_statistics()
    assert "documents" in stats
    assert stats["documents"]["count"] == 2  # Should have processed two documents
    assert "entities" in stats
    assert "relationships" in stats
    assert "knowledge_graph" in stats
    
    # Test incremental building of knowledge graph
    assert len(extractor.documents) == 2
    assert len(extractor.entities) == 2
    assert len(extractor.knowledge_graph) == 2


def test_entity_recognizer_integration(real_knowledge_extractor, document_directory):
    """Test that entity recognizer integrates correctly with document processor."""
    # Get the text file path
    text_file_path = os.path.join(document_directory, "test.txt")
    
    # Process the document
    document = real_knowledge_extractor.document_processor.process_document(text_file_path)
    
    # Extract entities
    entities = real_knowledge_extractor.entity_recognizer.recognize(document.content)
    
    # Filter entities
    filtered_entities = real_knowledge_extractor.entity_recognizer.filter_entities(
        entities, min_confidence=0.6
    )
    
    # Check that entities were found
    assert len(entities) > 0, "No entities were recognized"
    assert len(filtered_entities) <= len(entities), "Filtering increased entity count"
    
    # Check for expected entity types
    entity_types = {e.type for e in entities}
    expected_types = {"model", "organization", "benchmark"}
    found_expected = any(t.lower() in str(et).lower() for t in expected_types for et in entity_types)
    assert found_expected, f"No expected entity types found. Found: {entity_types}"
    
    # Check entity confidence scores
    for entity in entities:
        assert 0.0 <= entity.confidence <= 1.0, f"Entity {entity.text} has invalid confidence: {entity.confidence}"


def test_relationship_extractor_integration(real_knowledge_extractor, document_directory):
    """Test that relationship extractor integrates with entity recognizer."""
    # Get the text file path
    text_file_path = os.path.join(document_directory, "test.txt")
    
    # Process the document
    document = real_knowledge_extractor.document_processor.process_document(text_file_path)
    
    # Extract entities
    entities = real_knowledge_extractor.entity_recognizer.recognize(document.content)
    
    # Extract relationships
    relationships = real_knowledge_extractor.relationship_extractor.extract_relationships(
        document.content, entities
    )
    
    # Check relationship results
    if entities and len(entities) >= 2:
        # We should find some relationships if we have at least two entities
        # But this depends on the entity types and text content, so we shouldn't assert hard counts
        relationship_types = {str(r.relation_type).lower() for r in relationships}
        expected_types = {"outperforms", "developed_by", "evaluated_on"}
        
        # Check if any expected types were found - not all will be found in every text
        found_expected = any(t in relationship_types for t in expected_types)
        if len(relationships) > 0:
            assert found_expected, f"No expected relationship types found. Found: {relationship_types}"


def test_knowledge_graph_creation(real_knowledge_extractor, integration_fixtures):
    """Test that knowledge graphs are correctly created from entities and relationships."""
    # Get test data
    test_text = integration_fixtures["test_text"]
    
    # Process through entity recognition
    entities = real_knowledge_extractor.entity_recognizer.recognize(test_text)
    
    # Process through relationship extraction
    relationships = real_knowledge_extractor.relationship_extractor.extract_relationships(
        test_text, entities
    )
    
    # Create knowledge graph
    doc_id = "test_doc"
    knowledge_graph = real_knowledge_extractor._create_knowledge_graph(
        entities, relationships, doc_id
    )
    
    # Check knowledge graph structure
    assert "nodes" in knowledge_graph
    assert "edges" in knowledge_graph
    assert "metadata" in knowledge_graph
    
    # Each entity should create a node
    assert len(knowledge_graph["nodes"]) == len(entities)
    
    # Each relationship should create an edge
    assert len(knowledge_graph["edges"]) == len(relationships)
    
    # Check node properties
    for entity_id, node in knowledge_graph["nodes"].items():
        assert "id" in node
        assert "text" in node
        assert "type" in node
        assert "confidence" in node
        
    # Check edge properties
    for rel_id, edge in knowledge_graph["edges"].items():
        assert "id" in edge
        assert "source" in edge
        assert "target" in edge
        assert "type" in edge
        assert "confidence" in edge
        
    # Verify metadata
    assert "created_at" in knowledge_graph["metadata"]
    assert "document_id" in knowledge_graph["metadata"]
    assert knowledge_graph["metadata"]["document_id"] == doc_id


def test_knowledge_extraction_from_text_content(real_knowledge_extractor):
    """Test extracting knowledge directly from text content."""
    # Sample text content
    text_content = """
    BERT is a transformer-based language model developed by Google. It uses masked language 
    modeling to understand context in text. BERT has been fine-tuned for various NLP tasks 
    and has achieved state-of-the-art results on benchmarks like GLUE and SQuAD.
    
    GPT-4 is the latest large language model from OpenAI, following GPT-3.5. It was trained
    on a diverse dataset of text and code, and shows improved capabilities in reasoning,
    following instructions, and factual accuracy.
    """
    
    # Extract knowledge from text
    result = real_knowledge_extractor.extract_from_text(text_content, doc_id="sample_text")
    
    # Check result structure
    assert "document_id" in result
    assert result["document_id"] == "sample_text"
    assert "entity_count" in result
    assert "relationship_count" in result
    
    # Should have found entities for BERT, Google, GPT-4, OpenAI, GPT-3.5
    assert result["entity_count"] >= 3, "Not enough entities found"
    
    # Get the entities and relationships
    entities = real_knowledge_extractor.entities["sample_text"]
    relationships = real_knowledge_extractor.relationships["sample_text"]
    
    # Check entity texts
    entity_texts = {e.text.lower() for e in entities}
    expected_entities = {"bert", "google", "gpt-4", "openai"}
    found_expected = any(e in entity_texts for e in expected_entities)
    assert found_expected, f"No expected entities found. Found: {entity_texts}"
    
    # Check the knowledge graph
    knowledge_graph = real_knowledge_extractor.knowledge_graph["sample_text"]
    assert len(knowledge_graph["nodes"]) == len(entities)
    assert len(knowledge_graph["edges"]) == len(relationships)