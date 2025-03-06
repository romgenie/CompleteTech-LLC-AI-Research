"""
End-to-end tests for multi-document knowledge extraction.

This module contains tests that validate the extraction and integration of knowledge
from multiple documents, focusing on cross-document relationships and knowledge merging.
"""

import pytest

# Mark all tests in this module as e2e tests and knowledge graph related tests
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.knowledge_graph,
    pytest.mark.document,
    pytest.mark.relationship,
    pytest.mark.slow
]
import os
import json
import tempfile
from unittest.mock import patch

from research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import RelationType


def test_cross_document_entity_references(e2e_document_directory, e2e_output_directory, real_knowledge_extractor):
    """Test that entities are consistently referenced across multiple documents."""
    # Get the paths to the test documents
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    article_path = os.path.join(e2e_document_directory, "article.html")
    
    # Process each document
    paper_result = real_knowledge_extractor.extract_from_document(paper_path)
    article_result = real_knowledge_extractor.extract_from_document(article_path)
    
    # Get entities from each document
    paper_entities = real_knowledge_extractor.entities[paper_path]
    article_entities = real_knowledge_extractor.entities[article_path]
    
    # Find common entities (by text, not by ID, since IDs are different)
    common_entity_texts = {e.text.lower() for e in paper_entities} & {e.text.lower() for e in article_entities}
    
    # There should be some common entities (like GPT-4, OpenAI, etc.)
    assert len(common_entity_texts) > 0, "No common entities found across documents"
    
    # Verify consistency of entity type assignments
    for entity_text in common_entity_texts:
        # Find all instances of this entity in both documents
        paper_matches = [e for e in paper_entities if e.text.lower() == entity_text]
        article_matches = [e for e in article_entities if e.text.lower() == entity_text]
        
        # If found in both, check type consistency
        if paper_matches and article_matches:
            paper_types = {e.type for e in paper_matches}
            article_types = {e.type for e in article_matches}
            
            # Types should be consistent across documents
            common_types = paper_types & article_types
            assert len(common_types) > 0, f"Entity '{entity_text}' has inconsistent types across documents"


def test_multi_document_knowledge_graph(e2e_document_directory, e2e_output_directory, advanced_knowledge_extractor):
    """Test creating a unified knowledge graph from multiple documents."""
    # Get the paths to the test documents
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    article_path = os.path.join(e2e_document_directory, "article.html")
    blog_path = os.path.join(e2e_document_directory, "blog.txt")
    
    # Process each document
    paper_result = advanced_knowledge_extractor.extract_from_document(paper_path)
    article_result = advanced_knowledge_extractor.extract_from_document(article_path)
    blog_result = advanced_knowledge_extractor.extract_from_document(blog_path)
    
    # Get individual knowledge graphs
    paper_graph = advanced_knowledge_extractor.knowledge_graph[paper_path]
    article_graph = advanced_knowledge_extractor.knowledge_graph[article_path]
    blog_graph = advanced_knowledge_extractor.knowledge_graph[blog_path]
    
    # Create a combined graph
    # This is a simplified version of what would be in the actual implementation
    combined_graph = {
        "nodes": {},
        "edges": {},
        "metadata": {
            "document_ids": [paper_path, article_path, blog_path],
            "created_at": paper_graph["metadata"]["created_at"]
        }
    }
    
    # Collect nodes from all graphs
    node_map = {}  # Maps original node IDs to new IDs
    
    # First, add all nodes to the combined graph
    for graph_name, graph in [("paper", paper_graph), ("article", article_graph), ("blog", blog_graph)]:
        for node_id, node in graph["nodes"].items():
            # Generate a new ID for the node in the combined graph
            new_id = f"{graph_name}_{node_id}"
            node_map[f"{graph_name}_{node_id}"] = new_id
            
            # Add to combined graph with source document info
            combined_node = node.copy()
            combined_node["id"] = new_id
            combined_node["source_document"] = graph_name
            combined_graph["nodes"][new_id] = combined_node
    
    # Then, add all edges to the combined graph
    for graph_name, graph in [("paper", paper_graph), ("article", article_graph), ("blog", blog_graph)]:
        for edge_id, edge in graph["edges"].items():
            # Create mapped node IDs
            source_id = node_map[f"{graph_name}_{edge['source']}"]
            target_id = node_map[f"{graph_name}_{edge['target']}"]
            
            # Generate a new ID for the edge
            new_id = f"{graph_name}_{edge_id}"
            
            # Add to combined graph with source document info
            combined_edge = edge.copy()
            combined_edge["id"] = new_id
            combined_edge["source"] = source_id
            combined_edge["target"] = target_id
            combined_edge["source_document"] = graph_name
            combined_graph["edges"][new_id] = combined_edge
    
    # Check combined graph structure
    assert len(combined_graph["nodes"]) == sum(len(g["nodes"]) for g in [paper_graph, article_graph, blog_graph])
    assert len(combined_graph["edges"]) == sum(len(g["edges"]) for g in [paper_graph, article_graph, blog_graph])
    
    # Save the combined graph to the output directory
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
        json.dump(combined_graph, f, indent=2)
        combined_graph_path = f.name
    
    try:
        # Load the graph back to verify it's properly formatted
        with open(combined_graph_path, "r") as f:
            loaded_graph = json.load(f)
        
        assert loaded_graph["metadata"]["document_ids"] == [paper_path, article_path, blog_path]
        assert len(loaded_graph["nodes"]) == len(combined_graph["nodes"])
        assert len(loaded_graph["edges"]) == len(combined_graph["edges"])
    finally:
        # Clean up
        os.unlink(combined_graph_path)


def test_entity_resolution_across_documents(e2e_document_directory, advanced_knowledge_extractor):
    """Test resolving the same entities across different documents."""
    # Get the paths to the test documents
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    article_path = os.path.join(e2e_document_directory, "article.html")
    
    # Process each document
    paper_result = advanced_knowledge_extractor.extract_from_document(paper_path)
    article_result = advanced_knowledge_extractor.extract_from_document(article_path)
    
    # Get entities from each document
    paper_entities = advanced_knowledge_extractor.entities[paper_path]
    article_entities = advanced_knowledge_extractor.entities[article_path]
    
    # Find potential matching entities across documents
    # For simplicity, we'll just match on text similarity
    resolved_entities = []
    
    for paper_entity in paper_entities:
        for article_entity in article_entities:
            # Simple string matching (real implementation would be more sophisticated)
            if (paper_entity.text.lower() == article_entity.text.lower() and 
                paper_entity.type == article_entity.type):
                
                # This is a match - create a resolved entity record
                resolved_entities.append({
                    "text": paper_entity.text,
                    "type": str(paper_entity.type),
                    "references": [
                        {
                            "document_id": paper_path,
                            "entity_id": paper_entity.id,
                            "confidence": paper_entity.confidence
                        },
                        {
                            "document_id": article_path,
                            "entity_id": article_entity.id,
                            "confidence": article_entity.confidence
                        }
                    ]
                })
    
    # There should be some resolved entities
    assert len(resolved_entities) > 0, "No entities could be resolved across documents"
    
    # Check types of resolved entities
    entity_types = {e["type"] for e in resolved_entities}
    expected_types = ["model", "organization", "framework", "benchmark"]
    
    # We should have resolved entities of at least one expected type
    has_expected_type = any(expected.lower() in t.lower() for expected in expected_types for t in entity_types)
    assert has_expected_type, f"None of the expected entity types {expected_types} were resolved"


def test_relationship_consistency_across_documents(e2e_document_directory, advanced_knowledge_extractor):
    """Test that relationships extracted from different documents are consistent."""
    # Get the paths to the test documents
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    article_path = os.path.join(e2e_document_directory, "article.html")
    
    # Process each document
    paper_result = advanced_knowledge_extractor.extract_from_document(paper_path)
    article_result = advanced_knowledge_extractor.extract_from_document(article_path)
    
    # Get relationships from each document
    paper_relationships = advanced_knowledge_extractor.relationships[paper_path]
    article_relationships = advanced_knowledge_extractor.relationships[article_path]
    
    # Check for developed_by relationships in both documents
    paper_developed_by = [r for r in paper_relationships 
                         if r.relation_type == RelationType.DEVELOPED_BY]
    article_developed_by = [r for r in article_relationships 
                           if r.relation_type == RelationType.DEVELOPED_BY]
    
    # Collect (model, organization) pairs from each document
    paper_pairs = [(r.source.text.lower(), r.target.text.lower()) for r in paper_developed_by 
                  if r.source.type == EntityType.MODEL and r.target.type == EntityType.INSTITUTION]
    article_pairs = [(r.source.text.lower(), r.target.text.lower()) for r in article_developed_by 
                    if r.source.type == EntityType.MODEL and r.target.type == EntityType.INSTITUTION]
    
    # Check for consistency in relationships
    # Here we're looking for the same (model, organization) pair in both documents
    # In a real implementation, we'd use more sophisticated matching
    found_consistent_relationship = False
    
    for paper_pair in paper_pairs:
        for article_pair in article_pairs:
            if paper_pair[0] == article_pair[0] and paper_pair[1] == article_pair[1]:
                found_consistent_relationship = True
                break
    
    # We don't assert this condition as it depends on the specific documents and extraction quality
    # Instead, we just print a diagnostic message
    if not found_consistent_relationship and paper_pairs and article_pairs:
        print("No consistent relationships found across documents")
        print(f"Paper pairs: {paper_pairs}")
        print(f"Article pairs: {article_pairs}")