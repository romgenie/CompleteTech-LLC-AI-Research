"""
Tests for the Knowledge Extractor module.
"""

import unittest
import os
import tempfile
import json
import shutil
from typing import Dict, List, Any
from unittest.mock import MagicMock, patch

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType


class TestKnowledgeExtractor(unittest.TestCase):
    """Tests for the KnowledgeExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock document processor
        self.mock_document_processor = MagicMock()
        self.mock_document_processor.process.return_value = {
            "content": "GPT-4 was trained on a large dataset and evaluated on MMLU benchmark. "
                      "The model achieves 86.4% accuracy, outperforming previous models like GPT-3."
        }
        
        # Create mock entity recognizer
        self.mock_entity_recognizer = MagicMock()
        self.mock_entities = [
            Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=0, end_pos=5, metadata={}, id="e1"),
            Entity(text="large dataset", type=EntityType.DATASET, confidence=0.8, start_pos=20, end_pos=33, metadata={}, id="e2"),
            Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.9, start_pos=48, end_pos=52, metadata={}, id="e3"),
            Entity(text="accuracy", type=EntityType.METRIC, confidence=0.85, start_pos=77, end_pos=85, metadata={}, id="e4"),
            Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.9, start_pos=120, end_pos=125, metadata={}, id="e5")
        ]
        self.mock_entity_recognizer.recognize.return_value = self.mock_entities
        self.mock_entity_recognizer.filter_entities.return_value = self.mock_entities
        
        # Create mock relationship extractor
        self.mock_relationship_extractor = MagicMock()
        self.mock_relationships = [
            Relationship(
                source=self.mock_entities[0], 
                target=self.mock_entities[1], 
                relation_type=RelationType.TRAINED_ON, 
                confidence=0.9, 
                context="GPT-4 was trained on a large dataset", 
                metadata={},
                id="r1"
            ),
            Relationship(
                source=self.mock_entities[0], 
                target=self.mock_entities[2], 
                relation_type=RelationType.EVALUATED_ON, 
                confidence=0.85, 
                context="GPT-4 was evaluated on MMLU benchmark", 
                metadata={},
                id="r2"
            ),
            Relationship(
                source=self.mock_entities[0], 
                target=self.mock_entities[4], 
                relation_type=RelationType.OUTPERFORMS, 
                confidence=0.8, 
                context="GPT-4 outperforming previous models like GPT-3", 
                metadata={},
                id="r3"
            )
        ]
        self.mock_relationship_extractor.extract_relationships.return_value = self.mock_relationships
        self.mock_relationship_extractor.filter_relationships.return_value = self.mock_relationships
        
        # Create knowledge extractor with mocks
        self.knowledge_extractor = KnowledgeExtractor(
            document_processor=self.mock_document_processor,
            entity_recognizer=self.mock_entity_recognizer,
            relationship_extractor=self.mock_relationship_extractor
        )
        
        # Create temp directory for output
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temp directory
        shutil.rmtree(self.temp_dir)
    
    def test_process_document(self):
        """Test processing a document."""
        content = self.knowledge_extractor.process_document("test.pdf")
        
        # Check that the document processor was called
        self.mock_document_processor.process.assert_called_once_with("test.pdf")
        
        # Check that the content was returned
        self.assertEqual(content, "GPT-4 was trained on a large dataset and evaluated on MMLU benchmark. "
                       "The model achieves 86.4% accuracy, outperforming previous models like GPT-3.")
    
    def test_extract_entities(self):
        """Test extracting entities from text."""
        text = "Sample text"
        entities = self.knowledge_extractor.extract_entities(text)
        
        # Check that the entity recognizer was called
        self.mock_entity_recognizer.recognize_entities.assert_called_once_with(text)
        
        # Check that the entities were returned
        self.assertEqual(entities, self.mock_entities)
    
    def test_extract_relationships(self):
        """Test extracting relationships from text and entities."""
        text = "Sample text"
        relationships = self.knowledge_extractor.extract_relationships(text, self.mock_entities)
        
        # Check that the relationship extractor was called
        self.mock_relationship_extractor.extract_relationships.assert_called_once_with(text, self.mock_entities)
        
        # Check that the relationships were returned
        self.assertEqual(relationships, self.mock_relationships)
    
    def test_create_knowledge_graph(self):
        """Test creating a knowledge graph from entities and relationships."""
        knowledge_graph = self.knowledge_extractor.create_knowledge_graph(
            self.mock_entities, self.mock_relationships
        )
        
        # Check that the graph was created with the right structure
        self.assertIn("nodes", knowledge_graph)
        self.assertIn("edges", knowledge_graph)
        
        # Check nodes
        self.assertEqual(len(knowledge_graph["nodes"]), len(self.mock_entities))
        for node in knowledge_graph["nodes"]:
            self.assertIn("id", node)
            self.assertIn("label", node)
            self.assertIn("type", node)
            self.assertIn("confidence", node)
        
        # Check edges
        self.assertEqual(len(knowledge_graph["edges"]), len(self.mock_relationships))
        for edge in knowledge_graph["edges"]:
            self.assertIn("id", edge)
            self.assertIn("source", edge)
            self.assertIn("target", edge)
            self.assertIn("label", edge)
            self.assertIn("confidence", edge)
    
    def test_save_results(self):
        """Test saving results to output directory."""
        # Create a knowledge graph
        knowledge_graph = self.knowledge_extractor.create_knowledge_graph(
            self.mock_entities, self.mock_relationships
        )
        
        # Save results
        self.knowledge_extractor.save_results(
            self.mock_entities, self.mock_relationships, knowledge_graph, 
            self.temp_dir, "test.pdf"
        )
        
        # Check that files were created
        test_dir = os.path.join(self.temp_dir, "test")
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.exists(os.path.join(test_dir, "entities.json")))
        self.assertTrue(os.path.exists(os.path.join(test_dir, "relationships.json")))
        self.assertTrue(os.path.exists(os.path.join(test_dir, "knowledge_graph.json")))
        
        # Check that files contain correct data
        with open(os.path.join(test_dir, "entities.json"), "r") as f:
            entities_data = json.load(f)
            self.assertEqual(len(entities_data), len(self.mock_entities))
        
        with open(os.path.join(test_dir, "relationships.json"), "r") as f:
            relationships_data = json.load(f)
            self.assertEqual(len(relationships_data), len(self.mock_relationships))
        
        with open(os.path.join(test_dir, "knowledge_graph.json"), "r") as f:
            graph_data = json.load(f)
            self.assertEqual(len(graph_data["nodes"]), len(self.mock_entities))
            self.assertEqual(len(graph_data["edges"]), len(self.mock_relationships))
    
    def test_extract_knowledge(self):
        """Test extracting knowledge from a document."""
        result = self.knowledge_extractor.extract_from_document("test.pdf")
        
        # Check that the document processor, entity recognizer, and relationship extractor were called
        self.mock_document_processor.process.assert_called_once()
        self.mock_entity_recognizer.recognize.assert_called_once()
        self.mock_relationship_extractor.extract_relationships.assert_called_once()
        
        # Check that the result has the right structure
        self.assertIn("entities", result)
        self.assertIn("relationships", result)
        self.assertIn("knowledge_graph", result)
        
        # Check that the result contains the right data
        self.assertEqual(len(result["entities"]), len(self.mock_entities))
        self.assertEqual(len(result["relationships"]), len(self.mock_relationships))
        self.assertEqual(len(result["knowledge_graph"]["nodes"]), len(self.mock_entities))
        self.assertEqual(len(result["knowledge_graph"]["edges"]), len(self.mock_relationships))
    
    def test_analyze_results(self):
        """Test analyzing extraction results."""
        # Analyze results
        analysis = self.knowledge_extractor.analyze_results(
            self.mock_entities, self.mock_relationships
        )
        
        # Check that the analysis has the right structure
        self.assertIn("entity_count", analysis)
        self.assertIn("relationship_count", analysis)
        self.assertIn("entity_count_by_type", analysis)
        self.assertIn("relationship_count_by_type", analysis)
        self.assertIn("entity_pair_counts", analysis)
        self.assertIn("avg_entity_confidence", analysis)
        self.assertIn("avg_relationship_confidence", analysis)
        
        # Check entity count
        self.assertEqual(analysis["entity_count"], len(self.mock_entities))
        
        # Check relationship count
        self.assertEqual(analysis["relationship_count"], len(self.mock_relationships))
        
        # Check entity count by type
        self.assertIn("model", analysis["entity_count_by_type"])
        self.assertEqual(analysis["entity_count_by_type"]["model"], 2)
        
        # Check relationship count by type
        self.assertIn("trained_on", analysis["relationship_count_by_type"])
        self.assertEqual(analysis["relationship_count_by_type"]["trained_on"], 1)
        
        # Check entity pair counts
        self.assertIn("model_dataset", analysis["entity_pair_counts"])
        self.assertEqual(analysis["entity_pair_counts"]["model_dataset"], 1)
        
        # Check average confidences
        self.assertGreater(analysis["avg_entity_confidence"], 0)
        self.assertGreater(analysis["avg_relationship_confidence"], 0)


# To run additional tests, we need to create a more complex setup with real files and processors
class TestKnowledgeExtractorIntegration(unittest.TestCase):
    """Integration tests for the KnowledgeExtractor class."""
    
    @unittest.skip("This test requires actual files to be created")
    def test_integration(self):
        """Test the entire knowledge extraction process with real files."""
        # This test would create actual files, process them, and verify the results
        pass


if __name__ == '__main__':
    unittest.main()