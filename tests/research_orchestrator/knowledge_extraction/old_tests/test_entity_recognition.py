"""
Tests for the entity recognition module.
"""

import unittest
import os
import tempfile
import json
from typing import Dict, List, Any

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.entity_recognition.base_recognizer import EntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.ai_recognizer import AIEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.scientific_recognizer import ScientificEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory


class TestEntityRecognizer(unittest.TestCase):
    """Tests for the EntityRecognizer class."""
    
    def test_entity_creation(self):
        """Test entity creation and conversion to/from dict."""
        entity = Entity(
            text="BERT",
            type=EntityType.MODEL,
            confidence=0.95,
            start_pos=10,
            end_pos=14,
            metadata={"source": "test"},
            id="test_entity_1"
        )
        
        # Verify entity properties
        self.assertEqual(entity.id, "test_entity_1")
        self.assertEqual(entity.text, "BERT")
        self.assertEqual(entity.type, EntityType.MODEL)
        self.assertEqual(entity.confidence, 0.95)
        self.assertEqual(entity.start_pos, 10)
        self.assertEqual(entity.end_pos, 14)
        self.assertEqual(entity.metadata, {"source": "test"})
        
        # Verify to_dict/from_dict conversions
        entity_dict = entity.to_dict()
        self.assertEqual(entity_dict["id"], "test_entity_1")
        self.assertEqual(entity_dict["text"], "BERT")
        self.assertEqual(entity_dict["type"], str(EntityType.MODEL).lower())
        
        entity2 = Entity.from_dict(entity_dict)
        self.assertEqual(entity2.id, "test_entity_1")
        self.assertEqual(entity2.text, "BERT")
        self.assertEqual(entity2.type, EntityType.MODEL)
    
    def test_merge_overlapping_entities(self):
        """Test merging overlapping entities."""
        class MockEntityRecognizer(EntityRecognizer):
            def recognize(self, text):
                return []
        
        recognizer = MockEntityRecognizer()
        
        # Test with overlapping entities
        entities = [
            Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, metadata={}, id="e1"),
            Entity(text="BERT model", type=EntityType.MODEL, confidence=0.8, start_pos=10, end_pos=20, metadata={}, id="e2"),
            Entity(text="GPT", type=EntityType.MODEL, confidence=0.9, start_pos=30, end_pos=33, metadata={}, id="e3"),
            Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.95, start_pos=30, end_pos=35, metadata={}, id="e4")
        ]
        
        merged = recognizer.merge_overlapping_entities(entities)
        
        # Verify merge results
        self.assertEqual(len(merged), 2)
        self.assertTrue(merged[0].text in ["BERT", "BERT model"])
        self.assertTrue(merged[1].text in ["GPT", "GPT-3"])


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
        entities = self.recognizer.recognize(self.test_text)
        
        # Verify entities were found with correct types and texts
        self.assertTrue(len(entities) > 0)
        
        entity_types = {entity.type for entity in entities}
        expected_types = {EntityType.MODEL, EntityType.DATASET, EntityType.FRAMEWORK}
        self.assertTrue(any(expected_type in entity_types for expected_type in expected_types))
        
        entity_texts = {entity.text.lower() for entity in entities}
        expected_entities = {"gpt-4", "gpt-3.5", "mmlu", "pytorch"}
        self.assertTrue(any(expected_text in entity_texts for expected_text in expected_entities))
    
    def test_get_entities_by_type(self):
        """Test getting entities by type."""
        entities = self.recognizer.recognize(self.test_text)
        model_entities = [e for e in entities if e.type == EntityType.MODEL]
        
        # Verify model entities were correctly extracted
        self.assertTrue(len(model_entities) > 0)
        
        for entity in model_entities:
            self.assertIsInstance(entity.text, str)
            self.assertEqual(entity.type, EntityType.MODEL)
            self.assertIsInstance(entity.confidence, float)


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
        entities = self.recognizer.recognize(self.test_text)
        
        # Verify scientific entities were recognized
        self.assertTrue(len(entities) > 0)
        
        entity_types = {entity.type for entity in entities}
        expected_types = {EntityType.HYPOTHESIS, EntityType.METHODOLOGY, EntityType.FINDING, EntityType.FIELD, EntityType.AUTHOR}
        self.assertTrue(any(t in entity_types for t in expected_types))
        
        # Verify specific entity content when available
        hypothesis_entities = [e for e in entities if e.type == EntityType.HYPOTHESIS]
        if hypothesis_entities:
            self.assertIn("large language model", hypothesis_entities[0].text.lower())
        
        methodology_entities = [e for e in entities if e.type == EntityType.METHODOLOGY]
        if methodology_entities:
            methodology_texts = [e.text.lower() for e in methodology_entities]
            self.assertTrue(any("ablation study" in text for text in methodology_texts))
    
    def test_get_finding_entities(self):
        """Test getting finding entities."""
        entities = self.recognizer.recognize(self.test_text)
        finding_entities = [e for e in entities if e.type == EntityType.FINDING]
        
        # Verify finding entities when available
        if finding_entities:
            for entity in finding_entities:
                self.assertIsInstance(entity.text, str)
                self.assertEqual(entity.type, EntityType.FINDING)
                self.assertIsInstance(entity.confidence, float)
                self.assertTrue(any(keyword in entity.text.lower() for keyword in ["approach", "results", "performance"]))


class TestEntityRecognizerFactory(unittest.TestCase):
    """Tests for the EntityRecognizerFactory class."""
    
    def test_create_ai_recognizer(self):
        """Test creating an AI entity recognizer."""
        recognizer = EntityRecognizerFactory.create_recognizer("ai")
        self.assertIsInstance(recognizer, AIEntityRecognizer)
        self.assertTrue(hasattr(recognizer, "recognize"))
    
    def test_create_scientific_recognizer(self):
        """Test creating a scientific entity recognizer."""
        recognizer = EntityRecognizerFactory.create_recognizer("scientific")
        self.assertIsInstance(recognizer, ScientificEntityRecognizer)
        self.assertTrue(hasattr(recognizer, "recognize"))
    
    def test_create_combined_recognizer(self):
        """Test creating a combined entity recognizer."""
        config = {
            "recognizers": [
                {"type": "ai"},
                {"type": "scientific"}
            ]
        }
        recognizer = EntityRecognizerFactory.create_recognizer("combined", config)
        
        self.assertTrue(hasattr(recognizer, "recognize"))
        self.assertTrue(hasattr(recognizer, "recognizers"))
        self.assertTrue(len(recognizer.recognizers) > 0)
    
    def test_create_with_config(self):
        """Test creating an entity recognizer with config."""
        config = {
            "patterns": {
                "MODEL": [r"\bGPT-4\b"]
            }
        }
        
        recognizer = EntityRecognizerFactory.create_recognizer("ai", config)
        self.assertIsInstance(recognizer, AIEntityRecognizer)
        self.assertTrue(hasattr(recognizer, "patterns"))


if __name__ == '__main__':
    unittest.main()