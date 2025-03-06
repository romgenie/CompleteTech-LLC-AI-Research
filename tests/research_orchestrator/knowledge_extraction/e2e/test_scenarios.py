"""
End-to-end tests for real-world knowledge extraction scenarios.

This module contains tests that validate the knowledge extraction pipeline
using realistic scenarios and data sources, focusing on the quality and
usefulness of the extracted knowledge.
"""

import pytest

# Mark all tests in this module as e2e tests and knowledge graph related tests
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.knowledge_graph,
    pytest.mark.document,
    pytest.mark.entity,
    pytest.mark.relationship,
    pytest.mark.slow,
    pytest.mark.unstable
]
import os
import json
import tempfile
from unittest.mock import patch

from research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import RelationType


def test_research_paper_extraction(e2e_document_directory, e2e_output_directory, advanced_knowledge_extractor):
    """Test extracting knowledge from a research paper."""
    # Get the path to the test paper
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    
    # Run the extraction process
    result = advanced_knowledge_extractor.extract_from_document(paper_path)
    
    # Check that entities and relationships were found
    assert result["entity_count"] > 0, "No entities were extracted from the research paper"
    assert result["relationship_count"] > 0, "No relationships were extracted from the research paper"
    
    # Get the extracted entities and relationships
    entities = advanced_knowledge_extractor.entities[paper_path]
    relationships = advanced_knowledge_extractor.relationships[paper_path]
    
    # Check for specific entities we expect to find in a research paper
    entity_types = {e.type for e in entities}
    expected_entity_types = {
        EntityType.MODEL,
        EntityType.INSTITUTION,
        EntityType.BENCHMARK,
        EntityType.ARCHITECTURE,
        EntityType.FRAMEWORK
    }
    
    # We should find at least some of these entity types
    common_types = entity_types & expected_entity_types
    assert len(common_types) > 0, f"No expected entity types found in research paper. Found: {entity_types}"
    
    # Check for specific relationships we expect to find in a research paper
    relationship_types = {r.relation_type for r in relationships}
    expected_relationship_types = {
        RelationType.DEVELOPED_BY,
        RelationType.OUTPERFORMS,
        RelationType.EVALUATED_ON,
        RelationType.BASED_ON,
        RelationType.IMPLEMENTED_IN
    }
    
    # We should find at least some of these relationship types
    common_rel_types = relationship_types & expected_relationship_types
    assert len(common_rel_types) > 0, f"No expected relationship types found in research paper. Found: {relationship_types}"
    
    # Check for specific model-benchmark relationships
    model_benchmark_relationships = [r for r in relationships 
                                    if r.source.type == EntityType.MODEL 
                                    and r.target.type == EntityType.BENCHMARK
                                    and r.relation_type == RelationType.EVALUATED_ON]
    
    if model_benchmark_relationships:
        # This is more of a qualitative check, so we print the found relationships
        print("\nModel-Benchmark relationships found:")
        for r in model_benchmark_relationships:
            print(f"  {r.source.text} evaluated_on {r.target.text} (confidence: {r.confidence:.2f})")
    
    # Save the extraction results
    output_dir = advanced_knowledge_extractor.save_extraction_results(e2e_output_directory, paper_path)
    
    # Save a report of the findings
    report_path = os.path.join(output_dir, "report.json")
    with open(report_path, "w") as f:
        json.dump({
            "document_id": paper_path,
            "document_type": "research_paper",
            "entity_count": result["entity_count"],
            "entity_types": [str(t) for t in entity_types],
            "relationship_count": result["relationship_count"],
            "relationship_types": [str(t) for t in relationship_types],
            "models": [e.text for e in entities if e.type == EntityType.MODEL],
            "benchmarks": [e.text for e in entities if e.type == EntityType.BENCHMARK],
            "organizations": [e.text for e in entities if e.type == EntityType.INSTITUTION]
        }, f, indent=2)


def test_technical_blog_extraction(e2e_document_directory, e2e_output_directory, advanced_knowledge_extractor):
    """Test extracting knowledge from a technical blog post."""
    # Get the path to the test blog post
    blog_path = os.path.join(e2e_document_directory, "article.html")
    
    # Run the extraction process
    result = advanced_knowledge_extractor.extract_from_document(blog_path)
    
    # Check that entities and relationships were found
    assert result["entity_count"] > 0, "No entities were extracted from the blog post"
    
    # Get the extracted entities and relationships
    entities = advanced_knowledge_extractor.entities[blog_path]
    relationships = advanced_knowledge_extractor.relationships[blog_path]
    
    # Check for specific entities we expect to find in a technical blog
    model_entities = [e for e in entities if e.type == EntityType.MODEL]
    framework_entities = [e for e in entities if e.type == EntityType.FRAMEWORK]
    organization_entities = [e for e in entities if e.type == EntityType.INSTITUTION]
    
    # We should find some models
    assert len(model_entities) > 0, "No model entities found in blog post"
    
    # Print found models for informational purposes
    print("\nModels found in blog post:")
    for model in model_entities:
        print(f"  {model.text} (confidence: {model.confidence:.2f})")
    
    # If frameworks were mentioned, check them
    if framework_entities:
        print("\nFrameworks found in blog post:")
        for framework in framework_entities:
            print(f"  {framework.text} (confidence: {framework.confidence:.2f})")
    
    # If organizations were mentioned, check them
    if organization_entities:
        print("\nOrganizations found in blog post:")
        for org in organization_entities:
            print(f"  {org.text} (confidence: {org.confidence:.2f})")
    
    # Check that the knowledge graph was created
    knowledge_graph = advanced_knowledge_extractor.knowledge_graph[blog_path]
    assert len(knowledge_graph["nodes"]) > 0, "No nodes in knowledge graph"
    
    # Save the extraction results
    output_dir = advanced_knowledge_extractor.save_extraction_results(e2e_output_directory, blog_path)
    
    # Save a report of the findings
    report_path = os.path.join(output_dir, "report.json")
    with open(report_path, "w") as f:
        json.dump({
            "document_id": blog_path,
            "document_type": "blog_post",
            "entity_count": result["entity_count"],
            "entity_types": [str(e.type) for e in entities],
            "relationship_count": result["relationship_count"],
            "models": [e.text for e in model_entities],
            "frameworks": [e.text for e in framework_entities],
            "organizations": [e.text for e in organization_entities]
        }, f, indent=2)


def test_cross_domain_knowledge_extraction(e2e_document_directory, e2e_output_directory, advanced_knowledge_extractor):
    """Test extracting knowledge across different domains (research and blog)."""
    # Get the paths to the test documents
    paper_path = os.path.join(e2e_document_directory, "paper.txt")
    blog_path = os.path.join(e2e_document_directory, "article.html")
    
    # Process both documents
    paper_result = advanced_knowledge_extractor.extract_from_document(paper_path)
    blog_result = advanced_knowledge_extractor.extract_from_document(blog_path)
    
    # Get the extracted entities
    paper_entities = advanced_knowledge_extractor.entities[paper_path]
    blog_entities = advanced_knowledge_extractor.entities[blog_path]
    
    # Count entities by type in each document
    paper_entity_types = {e.type: len([x for x in paper_entities if x.type == e.type]) for e in paper_entities}
    blog_entity_types = {e.type: len([x for x in blog_entities if x.type == e.type]) for e in blog_entities}
    
    # Compare entity distributions
    print("\nEntity type distribution in research paper:")
    for entity_type, count in paper_entity_types.items():
        print(f"  {entity_type}: {count}")
    
    print("\nEntity type distribution in blog post:")
    for entity_type, count in blog_entity_types.items():
        print(f"  {entity_type}: {count}")
    
    # Look for entities that appear in both documents
    paper_entity_texts = {e.text.lower() for e in paper_entities}
    blog_entity_texts = {e.text.lower() for e in blog_entities}
    common_entities = paper_entity_texts & blog_entity_texts
    
    # We don't assert on this since it depends on the specific documents,
    # but we print it for information
    if common_entities:
        print("\nEntities found in both documents:")
        for entity_text in common_entities:
            print(f"  {entity_text}")
    
    # Check if the knowledge graphs were created for both documents
    paper_graph = advanced_knowledge_extractor.knowledge_graph[paper_path]
    blog_graph = advanced_knowledge_extractor.knowledge_graph[blog_path]
    
    # Create a directory for cross-domain analysis
    cross_domain_dir = os.path.join(e2e_output_directory, "cross_domain")
    os.makedirs(cross_domain_dir, exist_ok=True)
    
    # Save a report of the cross-domain analysis
    report_path = os.path.join(cross_domain_dir, "cross_domain_report.json")
    with open(report_path, "w") as f:
        json.dump({
            "paper": {
                "entity_count": paper_result["entity_count"],
                "relationship_count": paper_result["relationship_count"],
                "entity_types": {str(k): v for k, v in paper_entity_types.items()}
            },
            "blog": {
                "entity_count": blog_result["entity_count"],
                "relationship_count": blog_result["relationship_count"],
                "entity_types": {str(k): v for k, v in blog_entity_types.items()}
            },
            "common_entities": list(common_entities)
        }, f, indent=2)
    
    # This is a qualitative test, so we don't assert on specific outcomes