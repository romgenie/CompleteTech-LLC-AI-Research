"""
Unit tests for the knowledge extractor component.

This module contains tests for the KnowledgeExtractor class, focusing on testing
document processing, entity recognition, relationship extraction, knowledge graph
creation, and extraction results management.
"""

import pytest

# Mark all tests in this module as unit tests and knowledge graph related tests
pytestmark = [
    pytest.mark.unit, 
    pytest.mark.knowledge_graph,
    pytest.mark.medium
]
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import Document


class TestKnowledgeExtractor:
    """Tests for the KnowledgeExtractor class."""
    
    def test_knowledge_extractor_creation(self):
        """Test creating a KnowledgeExtractor with the required components."""
        # Create mock components
        document_processor = MagicMock()
        entity_recognizer = MagicMock()
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Check that components were set correctly
        assert extractor.document_processor == document_processor
        assert extractor.entity_recognizer == entity_recognizer
        assert extractor.relationship_extractor == relationship_extractor
        
        # Check that the data dictionaries were initialized
        assert extractor.documents == {}
        assert extractor.entities == {}
        assert extractor.relationships == {}
        assert extractor.knowledge_graph == {}
    
    def test_process_document(self, mock_document):
        """Test processing a document."""
        # Create mock components
        document_processor = MagicMock()
        document_processor.process_document.return_value = mock_document
        
        entity_recognizer = MagicMock()
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Process a document
        document = extractor.document_processor.process_document("test.txt")
        
        # Check that the document processor was called correctly
        document_processor.process_document.assert_called_once_with("test.txt")
        
        # Check that the document was returned correctly
        assert document == mock_document
    
    def test_extract_entities(self, mock_document, sample_unit_entities):
        """Test extracting entities from a document."""
        # Create mock components
        document_processor = MagicMock()
        
        entity_recognizer = MagicMock()
        entity_recognizer.recognize.return_value = sample_unit_entities
        entity_recognizer.filter_entities.return_value = sample_unit_entities
        
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Extract entities
        entities = extractor.entity_recognizer.recognize(mock_document.content)
        
        # Check that the entity recognizer was called correctly
        entity_recognizer.recognize.assert_called_once_with(mock_document.content)
        
        # Check that the entities were returned correctly
        assert entities == sample_unit_entities
        
        # Test entity filtering
        filtered_entities = extractor.entity_recognizer.filter_entities(entities, min_confidence=0.8)
        entity_recognizer.filter_entities.assert_called_once_with(entities, min_confidence=0.8)
        assert filtered_entities == sample_unit_entities
    
    def test_extract_relationships(self, mock_document, sample_unit_entities, sample_unit_relationships):
        """Test extracting relationships from a document and entities."""
        # Create mock components
        document_processor = MagicMock()
        
        entity_recognizer = MagicMock()
        
        relationship_extractor = MagicMock()
        relationship_extractor.extract_relationships.return_value = sample_unit_relationships
        relationship_extractor.filter_relationships.return_value = sample_unit_relationships
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Extract relationships
        relationships = extractor.relationship_extractor.extract_relationships(
            mock_document.content, sample_unit_entities
        )
        
        # Check that the relationship extractor was called correctly
        relationship_extractor.extract_relationships.assert_called_once_with(
            mock_document.content, sample_unit_entities
        )
        
        # Check that the relationships were returned correctly
        assert relationships == sample_unit_relationships
        
        # Test relationship filtering
        filtered_relationships = extractor.relationship_extractor.filter_relationships(
            relationships, min_confidence=0.8
        )
        relationship_extractor.filter_relationships.assert_called_once_with(
            relationships, min_confidence=0.8
        )
        assert filtered_relationships == sample_unit_relationships
    
    def test_create_knowledge_graph(self, sample_unit_entities, sample_unit_relationships):
        """Test creating a knowledge graph from entities and relationships."""
        # Create mock components
        document_processor = MagicMock()
        entity_recognizer = MagicMock()
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Create a knowledge graph
        doc_id = "test_doc"
        knowledge_graph = extractor._create_knowledge_graph(
            sample_unit_entities, sample_unit_relationships, doc_id
        )
        
        # Check the knowledge graph structure
        assert "nodes" in knowledge_graph
        assert "edges" in knowledge_graph
        assert "metadata" in knowledge_graph
        
        # Check that the nodes were created correctly
        assert len(knowledge_graph["nodes"]) == len(sample_unit_entities)
        for entity in sample_unit_entities:
            assert entity.id in knowledge_graph["nodes"]
            node = knowledge_graph["nodes"][entity.id]
            assert node["id"] == entity.id
            assert node["text"] == entity.text
            assert node["type"] == entity.type.value
            assert node["confidence"] == entity.confidence
        
        # Check that the edges were created correctly
        assert len(knowledge_graph["edges"]) == len(sample_unit_relationships)
        for relationship in sample_unit_relationships:
            assert relationship.id in knowledge_graph["edges"]
            edge = knowledge_graph["edges"][relationship.id]
            assert edge["id"] == relationship.id
            assert edge["source"] == relationship.source.id
            assert edge["target"] == relationship.target.id
            assert edge["type"] == relationship.relation_type.value
            assert edge["confidence"] == relationship.confidence
        
        # Check metadata
        assert "document_id" in knowledge_graph["metadata"]
        assert knowledge_graph["metadata"]["document_id"] == doc_id
        assert "created_at" in knowledge_graph["metadata"]
    
    def test_extract_from_document(self, mock_document, sample_unit_entities, sample_unit_relationships):
        """Test extracting knowledge from a document."""
        # Create mock components
        document_processor = MagicMock()
        document_processor.process_document.return_value = mock_document
        
        entity_recognizer = MagicMock()
        entity_recognizer.recognize.return_value = sample_unit_entities
        entity_recognizer.filter_entities.return_value = sample_unit_entities
        
        relationship_extractor = MagicMock()
        relationship_extractor.extract_relationships.return_value = sample_unit_relationships
        relationship_extractor.filter_relationships.return_value = sample_unit_relationships
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Extract from document
        doc_path = "/path/to/test.txt"
        result = extractor.extract_from_document(doc_path)
        
        # Check that all components were called correctly
        document_processor.process_document.assert_called_once_with(doc_path)
        entity_recognizer.recognize.assert_called_once_with(mock_document.content)
        relationship_extractor.extract_relationships.assert_called_once_with(
            mock_document.content, sample_unit_entities
        )
        
        # Check that the result has the correct structure
        assert "document_id" in result
        assert result["document_id"] == doc_path
        assert "document_type" in result
        assert result["document_type"] == mock_document.document_type
        assert "extraction_time" in result
        assert "entity_count" in result
        assert result["entity_count"] == len(sample_unit_entities)
        assert "relationship_count" in result
        assert result["relationship_count"] == len(sample_unit_relationships)
        
        # Check that the data was stored correctly
        assert doc_path in extractor.documents
        assert extractor.documents[doc_path] == mock_document
        assert doc_path in extractor.entities
        assert extractor.entities[doc_path] == sample_unit_entities
        assert doc_path in extractor.relationships
        assert extractor.relationships[doc_path] == sample_unit_relationships
        assert doc_path in extractor.knowledge_graph
    
    def test_extract_from_text(self, sample_unit_entities, sample_unit_relationships):
        """Test extracting knowledge from text content."""
        # Create mock components
        document_processor = MagicMock()
        document_processor.process_text.return_value = Document(
            content="This is test content",
            document_type="text",
            path=None,
            metadata={}
        )
        
        entity_recognizer = MagicMock()
        entity_recognizer.recognize.return_value = sample_unit_entities
        entity_recognizer.filter_entities.return_value = sample_unit_entities
        
        relationship_extractor = MagicMock()
        relationship_extractor.extract_relationships.return_value = sample_unit_relationships
        relationship_extractor.filter_relationships.return_value = sample_unit_relationships
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Extract from text
        text = "This is test content"
        doc_id = "test_text"
        result = extractor.extract_from_text(text, doc_id=doc_id)
        
        # Check that all components were called correctly
        document_processor.process_text.assert_called_once_with(text)
        entity_recognizer.recognize.assert_called_once_with("This is test content")
        relationship_extractor.extract_relationships.assert_called_once_with(
            "This is test content", sample_unit_entities
        )
        
        # Check that the result has the correct structure
        assert "document_id" in result
        assert result["document_id"] == doc_id
        assert "document_type" in result
        assert result["document_type"] == "text"
        assert "extraction_time" in result
        assert "entity_count" in result
        assert result["entity_count"] == len(sample_unit_entities)
        assert "relationship_count" in result
        assert result["relationship_count"] == len(sample_unit_relationships)
        
        # Check that the data was stored correctly
        assert doc_id in extractor.documents
        assert doc_id in extractor.entities
        assert extractor.entities[doc_id] == sample_unit_entities
        assert doc_id in extractor.relationships
        assert extractor.relationships[doc_id] == sample_unit_relationships
        assert doc_id in extractor.knowledge_graph
    
    def test_save_extraction_results(self, mock_document, sample_unit_entities, sample_unit_relationships):
        """Test saving extraction results to a directory."""
        # Create mock components
        document_processor = MagicMock()
        entity_recognizer = MagicMock()
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Set up test data
        doc_id = "test_doc"
        extractor.documents[doc_id] = mock_document
        extractor.entities[doc_id] = sample_unit_entities
        extractor.relationships[doc_id] = sample_unit_relationships
        extractor.knowledge_graph[doc_id] = extractor._create_knowledge_graph(
            sample_unit_entities, sample_unit_relationships, doc_id
        )
        
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the results
            output_dir = extractor.save_extraction_results(temp_dir, doc_id)
            
            # Check that the output directory exists
            assert os.path.isdir(output_dir)
            
            # Check that the files were created
            entity_file = os.path.join(output_dir, "entities.json")
            relationship_file = os.path.join(output_dir, "relationships.json")
            graph_file = os.path.join(output_dir, "knowledge_graph.json")
            stats_file = os.path.join(temp_dir, "extraction_statistics.json")
            
            assert os.path.isfile(entity_file)
            assert os.path.isfile(relationship_file)
            assert os.path.isfile(graph_file)
            assert os.path.isfile(stats_file)
            
            # Check the content of the files
            with open(entity_file, "r") as f:
                entities_data = json.load(f)
                assert len(entities_data) == len(sample_unit_entities)
            
            with open(relationship_file, "r") as f:
                relationships_data = json.load(f)
                assert len(relationships_data) == len(sample_unit_relationships)
            
            with open(graph_file, "r") as f:
                graph_data = json.load(f)
                assert len(graph_data["nodes"]) == len(sample_unit_entities)
                assert len(graph_data["edges"]) == len(sample_unit_relationships)
    
    def test_get_extraction_statistics(self, mock_document, sample_unit_entities, sample_unit_relationships):
        """Test getting extraction statistics."""
        # Create mock components
        document_processor = MagicMock()
        entity_recognizer = MagicMock()
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Set up test data
        doc_id = "test_doc"
        extractor.documents[doc_id] = mock_document
        extractor.entities[doc_id] = sample_unit_entities
        extractor.relationships[doc_id] = sample_unit_relationships
        extractor.knowledge_graph[doc_id] = extractor._create_knowledge_graph(
            sample_unit_entities, sample_unit_relationships, doc_id
        )
        
        # Get statistics
        stats = extractor.get_extraction_statistics()
        
        # Check that the statistics have the correct structure
        assert "documents" in stats
        assert "count" in stats["documents"]
        assert stats["documents"]["count"] == 1
        
        assert "entities" in stats
        assert "count" in stats["entities"]
        assert stats["entities"]["count"] == len(sample_unit_entities)
        assert "by_type" in stats["entities"]
        assert "avg_confidence" in stats["entities"]
        
        assert "relationships" in stats
        assert "count" in stats["relationships"]
        assert stats["relationships"]["count"] == len(sample_unit_relationships)
        assert "by_type" in stats["relationships"]
        assert "avg_confidence" in stats["relationships"]
        
        assert "knowledge_graph" in stats
        assert "total_nodes" in stats["knowledge_graph"]
        assert stats["knowledge_graph"]["total_nodes"] == len(sample_unit_entities)
        assert "total_edges" in stats["knowledge_graph"]
        assert stats["knowledge_graph"]["total_edges"] == len(sample_unit_relationships)
    
    def test_entity_type_statistics(self, sample_unit_entities):
        """Test getting entity type statistics."""
        # Create mock components
        document_processor = MagicMock()
        entity_recognizer = MagicMock()
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Call the method
        type_stats = extractor._get_entity_type_statistics(sample_unit_entities)
        
        # Check that the statistics have the correct structure
        assert EntityType.MODEL.value in type_stats
        assert EntityType.ORGANIZATION.value in type_stats
        assert EntityType.ARCHITECTURE.value in type_stats
        assert EntityType.BENCHMARK.value in type_stats
        
        # Check the counts
        model_count = len([e for e in sample_unit_entities if e.type == EntityType.MODEL])
        assert type_stats[EntityType.MODEL.value] == model_count
    
    def test_relationship_type_statistics(self, sample_unit_relationships):
        """Test getting relationship type statistics."""
        # Create mock components
        document_processor = MagicMock()
        entity_recognizer = MagicMock()
        relationship_extractor = MagicMock()
        
        # Create the extractor
        extractor = KnowledgeExtractor(
            document_processor=document_processor,
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Call the method
        type_stats = extractor._get_relationship_type_statistics(sample_unit_relationships)
        
        # Check that the statistics have the correct structure
        assert RelationType.DEVELOPED_BY.value in type_stats
        assert RelationType.BASED_ON.value in type_stats
        assert RelationType.EVALUATED_ON.value in type_stats
        
        # Check the counts
        developed_by_count = len([r for r in sample_unit_relationships if r.relation_type == RelationType.DEVELOPED_BY])
        assert type_stats[RelationType.DEVELOPED_BY.value] == developed_by_count