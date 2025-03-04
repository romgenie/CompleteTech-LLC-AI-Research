"""
Tests for the entity recognition module.
"""

import unittest
import os
import tempfile
import json
from typing import Dict, List, Any

from research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import Entity, EntityRecognizer
from research_orchestrator.knowledge_extraction.entity_recognition.ai_entity_recognizer import AIEntityRecognizer
from research_orchestrator.knowledge_extraction.entity_recognition.scientific_entity_recognizer import ScientificEntityRecognizer
from research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer_factory import EntityRecognizerFactory


class TestEntityRecognizer(unittest.TestCase):
    """Tests for the EntityRecognizer class."""
    
    def test_entity_creation(self):
        """Test entity creation and conversion to/from dict."""
        entity = Entity(
            id="test_entity_1",
            text="BERT",
            type="model",
            confidence=0.95,
            start_pos=10,
            end_pos=14,
            metadata={"source": "test"}
        )
        
        self.assertEqual(entity.id, "test_entity_1")
        self.assertEqual(entity.text, "BERT")
        self.assertEqual(entity.type, "model")
        self.assertEqual(entity.confidence, 0.95)
        self.assertEqual(entity.start_pos, 10)
        self.assertEqual(entity.end_pos, 14)
        self.assertEqual(entity.metadata, {"source": "test"})
        
        # Test conversion to dict
        entity_dict = entity.to_dict()
        self.assertEqual(entity_dict["id"], "test_entity_1")
        self.assertEqual(entity_dict["text"], "BERT")
        self.assertEqual(entity_dict["type"], "model")
        
        # Test conversion from dict
        entity2 = Entity.from_dict(entity_dict)
        self.assertEqual(entity2.id, "test_entity_1")
        self.assertEqual(entity2.text, "BERT")
        self.assertEqual(entity2.type, "model")
    
    def test_merge_overlapping_entities(self):
        """Test merging overlapping entities."""
        # Create a mock entity recognizer for testing
        class MockEntityRecognizer(EntityRecognizer):
            def recognize_entities(self, text):
                return []
        
        recognizer = MockEntityRecognizer()
        
        # Create overlapping entities
        entities = [
            Entity("e1", "BERT", "model", 0.9, 10, 14, {}),
            Entity("e2", "BERT model", "model", 0.8, 10, 20, {}),
            Entity("e3", "GPT", "model", 0.9, 30, 33, {}),
            Entity("e4", "GPT-3", "model", 0.95, 30, 35, {})
        ]
        
        # Merge overlapping entities
        merged = recognizer.merge_overlapping_entities(entities)
        
        # Check results
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0].text, "BERT")
        self.assertEqual(merged[1].text, "GPT-3")


class TestAIEntityRecognizer(unittest.TestCase):
    """Tests for the AIEntityRecognizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recognizer = AIEntityRecognizer()
        
        # Sample test text with AI entities
        self.test_text = (
            "In this paper, we introduce GPT-4, a large language model that outperforms "
            "previous models like GPT-3.5. We trained GPT-4 on a large dataset of text "
            "and evaluated it on the MMLU benchmark. The model achieves 86.4% accuracy "
            "on the benchmark, surpassing human performance. We implemented the model "
            "using PyTorch and trained it on NVIDIA A100 GPUs."
        )
    
    def test_recognize_entities(self):
        """Test recognizing AI entities in text."""
        entities = self.recognizer.recognize_entities(self.test_text)
        
        # Check that we found some entities
        self.assertTrue(len(entities) > 0)
        
        # Check that we found the expected entity types
        entity_types = {entity.type for entity in entities}
        expected_types = {"model", "dataset", "framework"}
        self.assertTrue(expected_types.issubset(entity_types))
        
        # Check that we found specific entities
        entity_texts = {entity.text.lower() for entity in entities}
        expected_entities = {"gpt-4", "gpt-3.5", "mmlu", "pytorch"}
        self.assertTrue(all(entity in entity_texts for entity in expected_entities))
    
    def test_extract_top_entities(self):
        """Test extracting top entities by confidence."""
        entities = self.recognizer.recognize_entities(self.test_text)
        top_entities = self.recognizer.extract_top_entities(entities, top_n=2)
        
        # Check that we got a dictionary with entity types as keys
        self.assertIsInstance(top_entities, dict)
        
        # Check that each value is a list of (entity_text, confidence) tuples
        for entity_type, entities_list in top_entities.items():
            self.assertIsInstance(entities_list, list)
            for entity_tuple in entities_list:
                self.assertEqual(len(entity_tuple), 2)
                self.assertIsInstance(entity_tuple[0], str)
                self.assertIsInstance(entity_tuple[1], float)


class TestScientificEntityRecognizer(unittest.TestCase):
    """Tests for the ScientificEntityRecognizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.recognizer = ScientificEntityRecognizer()
        
        # Sample test text with scientific entities
        self.test_text = (
            "Our hypothesis is that large language models can achieve better performance "
            "through careful fine-tuning. We conducted an ablation study to understand "
            "the impact of different training techniques. The results show that our approach "
            "significantly improves performance. This finding has implications for the field of "
            "natural language processing. As demonstrated by Smith et al. (2022), transfer "
            "learning is a powerful technique in this domain."
        )
    
    def test_recognize_entities(self):
        """Test recognizing scientific entities in text."""
        entities = self.recognizer.recognize_entities(self.test_text)
        
        # Check that we found some entities
        self.assertTrue(len(entities) > 0)
        
        # Check that we found expected entity types
        entity_types = {entity.type for entity in entities}
        expected_types = {"hypothesis", "methodology", "finding", "field", "author"}
        self.assertTrue(any(t in entity_types for t in expected_types))
        
        # Check specific entities
        hypothesis_entities = [e for e in entities if e.type == "hypothesis"]
        if hypothesis_entities:
            hypothesis_text = hypothesis_entities[0].text.lower()
            self.assertIn("large language models", hypothesis_text)
        
        methodology_entities = [e for e in entities if e.type == "methodology"]
        if methodology_entities:
            methodology_texts = [e.text.lower() for e in methodology_entities]
            self.assertTrue(any("ablation study" in text for text in methodology_texts))
    
    def test_extract_findings(self):
        """Test extracting findings from entities."""
        entities = self.recognizer.recognize_entities(self.test_text)
        findings = self.recognizer.extract_findings(entities)
        
        # Check that we extracted some findings
        self.assertTrue(len(findings) >= 0)
        
        # If we found findings, check their content
        if findings:
            finding_text = findings[0].lower()
            self.assertTrue("approach" in finding_text or "performance" in finding_text)


class TestEntityRecognizerFactory(unittest.TestCase):
    """Tests for the EntityRecognizerFactory class."""
    
    def test_create_ai_recognizer(self):
        """Test creating an AI entity recognizer."""
        recognizer = EntityRecognizerFactory.create_recognizer("ai")
        
        self.assertIsInstance(recognizer, AIEntityRecognizer)
        self.assertTrue(hasattr(recognizer, "recognize_entities"))
    
    def test_create_scientific_recognizer(self):
        """Test creating a scientific entity recognizer."""
        recognizer = EntityRecognizerFactory.create_recognizer("scientific")
        
        self.assertIsInstance(recognizer, ScientificEntityRecognizer)
        self.assertTrue(hasattr(recognizer, "recognize_entities"))
    
    def test_create_combined_recognizer(self):
        """Test creating a combined entity recognizer."""
        recognizer = EntityRecognizerFactory.create_recognizer("combined")
        
        self.assertTrue(hasattr(recognizer, "recognize_entities"))
        self.assertTrue(hasattr(recognizer, "recognizers"))
        
        # Check that the combined recognizer has the expected recognizers
        recognizer_types = [type(r).__name__ for r in recognizer.recognizers]
        expected_types = ["AIEntityRecognizer", "ScientificEntityRecognizer"]
        for expected_type in expected_types:
            self.assertTrue(any(expected_type in r_type for r_type in recognizer_types))
    
    def test_create_from_config(self):
        """Test creating an entity recognizer from config."""
        config = {
            "type": "ai",
            "config": {
                "entity_types": ["model", "dataset", "framework"]
            }
        }
        
        recognizer = EntityRecognizerFactory.create_from_config(config)
        
        self.assertIsInstance(recognizer, AIEntityRecognizer)
        self.assertEqual(set(recognizer.entity_types), set(["model", "dataset", "framework"]))


if __name__ == '__main__':
    unittest.main()