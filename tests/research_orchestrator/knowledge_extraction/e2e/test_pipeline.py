"""
End-to-end tests for the knowledge extraction pipeline.

This module contains tests that validate the full knowledge extraction pipeline,
from document processing to knowledge graph creation, ensuring all components
work together correctly with realistic inputs.
"""

import pytest

# Mark all tests in this module as e2e tests and knowledge graph related tests
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.knowledge_graph,
    pytest.mark.document,
    pytest.mark.entity,
    pytest.mark.relationship,
    pytest.mark.slow
]
import os
import json
import tempfile
from unittest.mock import patch

from research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import RelationType


def test_full_extraction_pipeline_text(e2e_document_directory, e2e_output_directory, real_knowledge_extractor):
    """Test the full extraction pipeline with a text document."""
    # Get the path to the test paper text file
    text_file_path = os.path.join(e2e_document_directory, "paper.txt")
    
    # Run the extraction process
    result = real_knowledge_extractor.extract_from_document(text_file_path)
    
    # Check the result structure
    assert "document_id" in result
    assert "document_type" in result
    assert "extraction_time" in result
    assert "entity_count" in result
    assert "relationship_count" in result
    
    # Check that entities and relationships were found
    assert result["entity_count"] > 0, "No entities were extracted"
    assert result["relationship_count"] >= 0, "Error in relationship extraction"
    
    # Save the results to the output directory
    output_dir = real_knowledge_extractor.save_extraction_results(e2e_output_directory, text_file_path)
    
    # Check that the output files were created
    assert os.path.exists(os.path.join(output_dir, "entities.json"))
    assert os.path.exists(os.path.join(output_dir, "relationships.json"))
    assert os.path.exists(os.path.join(output_dir, "knowledge_graph.json"))
    
    # Load and check entities
    with open(os.path.join(output_dir, "entities.json"), "r") as f:
        entities = json.load(f)
    
    # Check for expected entities
    entity_texts = {e["text"].lower() for e in entities}
    expected_models = ["gpt-4", "palm", "claude"]
    found_models = [model for model in expected_models if model in entity_texts]
    assert len(found_models) > 0, f"None of the expected models {expected_models} were found"
    
    # Check for expected benchmarks
    expected_benchmarks = ["mmlu", "humaneval", "gsm8k"]
    found_benchmarks = [benchmark for benchmark in expected_benchmarks 
                       if any(benchmark.lower() in e["text"].lower() for e in entities 
                              if e["type"] == "benchmark")]
    assert len(found_benchmarks) > 0, f"None of the expected benchmarks {expected_benchmarks} were found"
    
    # Load and check knowledge graph
    with open(os.path.join(output_dir, "knowledge_graph.json"), "r") as f:
        graph_data = json.load(f)
    
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert "metadata" in graph_data
    assert len(graph_data["nodes"]) > 0
    
    # Verify that we have the expected node types
    node_types = {node["type"] for node in graph_data["nodes"].values()}
    expected_types = ["model", "organization", "benchmark", "metric"]
    found_types = [t for t in expected_types if any(t.lower() in nt.lower() for nt in node_types)]
    assert len(found_types) > 0, f"None of the expected node types {expected_types} were found"


def test_full_extraction_pipeline_html(e2e_document_directory, e2e_output_directory, real_knowledge_extractor):
    """Test the full extraction pipeline with an HTML document."""
    # Get the path to the test article HTML file
    html_file_path = os.path.join(e2e_document_directory, "article.html")
    
    # Run the extraction process
    result = real_knowledge_extractor.extract_from_document(html_file_path)
    
    # Check the result structure
    assert result["document_type"] == "html"
    assert result["entity_count"] > 0
    
    # Save the results to the output directory
    output_dir = real_knowledge_extractor.save_extraction_results(e2e_output_directory, html_file_path)
    
    # Load and check entities
    with open(os.path.join(output_dir, "entities.json"), "r") as f:
        entities = json.load(f)
    
    # Check for expected entities
    entity_texts = {e["text"].lower() for e in entities}
    expected_entities = ["bert", "gpt-3", "llama", "falcon"]
    found_entities = [entity for entity in expected_entities if any(entity.lower() in et for et in entity_texts)]
    assert len(found_entities) > 0, f"None of the expected entities {expected_entities} were found"
    
    # Check for expected organizations
    expected_orgs = ["google", "openai", "meta"]
    found_orgs = [org for org in expected_orgs 
                 if any(org.lower() in e["text"].lower() for e in entities 
                        if e["type"] == "organization")]
    assert len(found_orgs) > 0, f"None of the expected organizations {expected_orgs} were found"


def test_multi_document_extraction(e2e_document_directory, e2e_output_directory, real_knowledge_extractor):
    """Test extracting knowledge from multiple documents and combining results."""
    # Get the paths to the test documents
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    article_path = os.path.join(e2e_document_directory, "article.html")
    blog_path = os.path.join(e2e_document_directory, "blog.txt")
    
    # Process each document
    paper_result = real_knowledge_extractor.extract_from_document(paper_path)
    article_result = real_knowledge_extractor.extract_from_document(article_path)
    blog_result = real_knowledge_extractor.extract_from_document(blog_path)
    
    # Check that all documents were processed
    assert paper_result["entity_count"] > 0
    assert article_result["entity_count"] > 0
    assert blog_result["entity_count"] > 0
    
    # Get extraction statistics
    stats = real_knowledge_extractor.get_extraction_statistics()
    
    # Check the statistics
    assert stats["documents"]["count"] == 3
    assert stats["entities"]["count"] > 0
    assert stats["relationships"]["count"] >= 0
    
    # Check that entity statistics include types
    assert "by_type" in stats["entities"]
    assert "by_type" in stats["relationships"]
    
    # Check entities by type
    entity_types = stats["entities"]["by_type"]
    expected_types = ["model", "organization", "benchmark", "framework"]
    found_types = [t for t in expected_types if any(t.lower() in et.lower() for et in entity_types.keys())]
    assert len(found_types) > 0, f"None of the expected entity types {expected_types} were found"
    
    # Save combined results
    combined_output_dir = os.path.join(e2e_output_directory, "combined")
    os.makedirs(combined_output_dir, exist_ok=True)
    
    # Save statistics
    with open(os.path.join(combined_output_dir, "statistics.json"), "w") as f:
        json.dump(stats, f, indent=2)
    
    # Verify that the combined knowledge is consistent
    # The total entity count should be at least the sum of the individual counts
    # (could be less if there are duplicates)
    total_entities = stats["entities"]["count"]
    individual_entity_sum = (paper_result["entity_count"] + 
                           article_result["entity_count"] + 
                           blog_result["entity_count"])
    
    assert total_entities <= individual_entity_sum, "Entity count inconsistency"


def test_knowledge_graph_structure(e2e_document_directory, advanced_knowledge_extractor):
    """Test the structure of the knowledge graph created from multiple documents."""
    # Get the paths to the test documents
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    
    # Extract from document
    result = advanced_knowledge_extractor.extract_from_document(paper_path)
    
    # Get the knowledge graph
    doc_id = paper_path
    knowledge_graph = advanced_knowledge_extractor.knowledge_graph[doc_id]
    
    # Check the structure
    assert "nodes" in knowledge_graph
    assert "edges" in knowledge_graph
    assert "metadata" in knowledge_graph
    
    # Check node properties
    for node_id, node in knowledge_graph["nodes"].items():
        assert "id" in node
        assert "text" in node
        assert "type" in node
        assert "confidence" in node
    
    # Check edge properties
    for edge_id, edge in knowledge_graph["edges"].items():
        assert "id" in edge
        assert "source" in edge
        assert "target" in edge
        assert "type" in edge
        assert "confidence" in edge
    
    # Check metadata
    assert "document_id" in knowledge_graph["metadata"]
    assert knowledge_graph["metadata"]["document_id"] == doc_id
    
    # Check for specific LLM relationships we expect to find
    edges = knowledge_graph["edges"].values()
    
    # Find the model nodes
    model_nodes = [node_id for node_id, node in knowledge_graph["nodes"].items() 
                  if node["type"].lower() == "model"]
    
    # Check for developed_by, outperforms, or evaluated_on relationships
    has_relationship = False
    expected_relationships = ["developed_by", "outperforms", "evaluated_on", "trained_on"]
    
    for edge in edges:
        if edge["source"] in model_nodes:
            if any(rel_type.lower() in edge["type"].lower() for rel_type in expected_relationships):
                has_relationship = True
                break
    
    assert has_relationship, f"No expected relationships found for model nodes: {expected_relationships}"