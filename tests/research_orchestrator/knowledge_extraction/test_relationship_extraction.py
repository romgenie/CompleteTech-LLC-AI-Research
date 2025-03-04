"""
Tests for the relationship extraction module.
"""

import unittest
import os
import tempfile
import json
from typing import Dict, List, Any

from research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import Entity
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship_extractor import Relationship, RelationshipExtractor
from research_orchestrator.knowledge_extraction.relationship_extraction.pattern_relationship_extractor import PatternRelationshipExtractor
from research_orchestrator.knowledge_extraction.relationship_extraction.ai_relationship_extractor import AIRelationshipExtractor
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship_extractor_factory import RelationshipExtractorFactory


class TestRelationshipExtractor(unittest.TestCase):
    """Tests for the RelationshipExtractor class."""
    
    def test_relationship_creation(self):
        """Test relationship creation and conversion to/from dict."""
        source_entity = Entity(
            id="entity_1",
            text="BERT",
            type="model",
            confidence=0.95,
            start_pos=10,
            end_pos=14,
            metadata={"source": "test"}
        )
        
        target_entity = Entity(
            id="entity_2",
            text="ImageNet",
            type="dataset",
            confidence=0.9,
            start_pos=30,
            end_pos=38,
            metadata={"source": "test"}
        )
        
        relationship = Relationship(
            id="relationship_1",
            source_entity=source_entity,
            target_entity=target_entity,
            relation_type="trained_on",
            confidence=0.85,
            context="BERT was trained on ImageNet",
            metadata={"source": "test"}
        )
        
        self.assertEqual(relationship.id, "relationship_1")
        self.assertEqual(relationship.source_entity.text, "BERT")
        self.assertEqual(relationship.target_entity.text, "ImageNet")
        self.assertEqual(relationship.relation_type, "trained_on")
        self.assertEqual(relationship.confidence, 0.85)
        self.assertEqual(relationship.context, "BERT was trained on ImageNet")
        self.assertEqual(relationship.metadata, {"source": "test"})
        
        # Test conversion to dict
        relationship_dict = relationship.to_dict()
        self.assertEqual(relationship_dict["id"], "relationship_1")
        self.assertEqual(relationship_dict["relation_type"], "trained_on")
        self.assertEqual(relationship_dict["source_entity"]["text"], "BERT")
        self.assertEqual(relationship_dict["target_entity"]["text"], "ImageNet")
        
        # Test conversion from dict
        relationship2 = Relationship.from_dict(relationship_dict)
        self.assertEqual(relationship2.id, "relationship_1")
        self.assertEqual(relationship2.relation_type, "trained_on")
        self.assertEqual(relationship2.source_entity.text, "BERT")
        self.assertEqual(relationship2.target_entity.text, "ImageNet")
    
    def test_get_entity_pair_context(self):
        """Test getting context for an entity pair."""
        # Create a mock relationship extractor for testing
        class MockRelationshipExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = MockRelationshipExtractor()
        
        # Create test entities
        entity1 = Entity("e1", "BERT", "model", 0.9, 10, 14, {})
        entity2 = Entity("e2", "ImageNet", "dataset", 0.9, 30, 38, {})
        
        # Create test text
        text = "We trained BERT on the ImageNet dataset and evaluated it."
        
        # Get context
        context = extractor.get_entity_pair_context(text, entity1, entity2)
        
        # Check that context contains both entities
        self.assertIn("BERT", context)
        self.assertIn("ImageNet", context)
    
    def test_find_entity_pairs(self):
        """Test finding entity pairs based on proximity."""
        # Create a mock relationship extractor for testing
        class MockRelationshipExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = MockRelationshipExtractor()
        
        # Create test entities
        entities = [
            Entity("e1", "BERT", "model", 0.9, 10, 14, {}),
            Entity("e2", "ImageNet", "dataset", 0.9, 30, 38, {}),
            Entity("e3", "GPT", "model", 0.9, 100, 103, {}),
            Entity("e4", "CIFAR", "dataset", 0.9, 500, 505, {})
        ]
        
        # Find pairs with a max distance of 50
        pairs = extractor.find_entity_pairs(entities, max_distance=50)
        
        # Check results
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][0].text, "BERT")
        self.assertEqual(pairs[0][1].text, "ImageNet")
        
        # Find pairs with a larger max distance
        pairs = extractor.find_entity_pairs(entities, max_distance=100)
        
        # Check results
        self.assertEqual(len(pairs), 3)


class TestPatternRelationshipExtractor(unittest.TestCase):
    """Tests for the PatternRelationshipExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = PatternRelationshipExtractor()
        
        # Sample test text with entity relationships
        self.test_text = (
            "BERT is a language model that is based on the Transformer architecture. "
            "It is used for natural language processing tasks and outperforms traditional methods. "
            "ResNet is a convolutional neural network that is an implementation of residual learning."
        )
        
        # Sample entities
        self.entities = [
            Entity("e1", "BERT", "model", 0.9, 0, 4, {}),
            Entity("e2", "language model", "model", 0.8, 7, 21, {}),
            Entity("e3", "Transformer", "architecture", 0.9, 44, 55, {}),
            Entity("e4", "natural language processing", "task", 0.85, 72, 99, {}),
            Entity("e5", "ResNet", "model", 0.9, 143, 149, {}),
            Entity("e6", "convolutional neural network", "architecture", 0.85, 155, 185, {}),
            Entity("e7", "residual learning", "technique", 0.8, 219, 236, {})
        ]
    
    def test_extract_relationships(self):
        """Test extracting relationships using patterns."""
        relationships = self.extractor.extract_relationships(self.test_text, self.entities)
        
        # Check that we found some relationships
        self.assertTrue(len(relationships) > 0)
        
        # Check for expected relationship types
        relation_types = {r.relation_type for r in relationships}
        expected_types = {"is_a", "based_on", "used_for", "implements"}
        self.assertTrue(any(t in relation_types for t in expected_types))
        
        # Check for specific relationships
        found_bert_is_a = False
        found_bert_based_on = False
        found_resnet_implements = False
        
        for relationship in relationships:
            if (relationship.source_entity.text == "BERT" and 
                relationship.relation_type == "is_a" and 
                relationship.target_entity.text == "language model"):
                found_bert_is_a = True
            
            if (relationship.source_entity.text == "BERT" and 
                relationship.relation_type == "based_on" and 
                relationship.target_entity.text == "Transformer"):
                found_bert_based_on = True
            
            if (relationship.source_entity.text == "ResNet" and 
                relationship.relation_type == "implements" and 
                relationship.target_entity.text == "residual learning"):
                found_resnet_implements = True
        
        # We don't require all relationships to be found, as pattern matching
        # can be imprecise, but we expect at least one of them to be found
        self.assertTrue(found_bert_is_a or found_bert_based_on or found_resnet_implements)
    
    def test_add_pattern(self):
        """Test adding a custom pattern."""
        # Add a custom pattern
        custom_pattern = r"(\w+) enables (\w+)"
        self.extractor.add_pattern("enables", custom_pattern)
        
        # Check that the pattern was added
        self.assertIn("enables", self.extractor.patterns)
        self.assertIn(custom_pattern, self.extractor.patterns["enables"])
        
        # Check that the pattern was compiled
        self.assertIn("enables", self.extractor.compiled_patterns)
        self.assertEqual(len(self.extractor.compiled_patterns["enables"]), 1)


class TestAIRelationshipExtractor(unittest.TestCase):
    """Tests for the AIRelationshipExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = AIRelationshipExtractor()
        
        # Sample test text with AI relationships
        self.test_text = (
            "GPT-4 was trained on a large dataset and evaluated on the MMLU benchmark. "
            "The model achieves 86.4% accuracy, outperforming previous models like GPT-3.5. "
            "BERT uses the Transformer architecture and can be applied to various NLP tasks."
        )
        
        # Sample entities
        self.entities = [
            Entity("e1", "GPT-4", "model", 0.95, 0, 5, {}),
            Entity("e2", "large dataset", "dataset", 0.8, 20, 33, {}),
            Entity("e3", "MMLU", "benchmark", 0.9, 48, 52, {}),
            Entity("e4", "accuracy", "metric", 0.85, 77, 85, {}),
            Entity("e5", "GPT-3.5", "model", 0.9, 122, 129, {}),
            Entity("e6", "BERT", "model", 0.9, 131, 135, {}),
            Entity("e7", "Transformer", "architecture", 0.85, 145, 156, {}),
            Entity("e8", "NLP", "task", 0.8, 190, 193, {})
        ]
    
    def test_extract_relationships(self):
        """Test extracting AI-specific relationships."""
        relationships = self.extractor.extract_relationships(self.test_text, self.entities)
        
        # Check that we found some relationships
        self.assertTrue(len(relationships) > 0)
        
        # Check for expected relationship types
        relation_types = {r.relation_type for r in relationships}
        expected_types = {"trained_on", "evaluated_on", "outperforms", "uses", "applied_to"}
        self.assertTrue(any(t in relation_types for t in expected_types))
        
        # Check for specific relationships
        found_gpt4_evaluated = False
        found_gpt4_outperforms = False
        found_bert_uses = False
        
        for relationship in relationships:
            if (relationship.source_entity.text == "GPT-4" and 
                relationship.relation_type == "evaluated_on" and 
                relationship.target_entity.text == "MMLU"):
                found_gpt4_evaluated = True
            
            if (relationship.source_entity.text == "GPT-4" and 
                relationship.relation_type == "outperforms" and 
                relationship.target_entity.text == "GPT-3.5"):
                found_gpt4_outperforms = True
            
            if (relationship.source_entity.text == "BERT" and 
                relationship.relation_type == "uses" and 
                relationship.target_entity.text == "Transformer"):
                found_bert_uses = True
        
        # We don't require all relationships to be found, but we expect at least one
        self.assertTrue(found_gpt4_evaluated or found_gpt4_outperforms or found_bert_uses)
    
    def test_extract_model_performance(self):
        """Test extracting model performance from relationships."""
        # Create relationships with performance information
        model1 = Entity("e1", "GPT-4", "model", 0.95, 0, 5, {})
        model2 = Entity("e2", "BERT", "model", 0.9, 50, 54, {})
        metric1 = Entity("e3", "accuracy", "metric", 0.9, 20, 28, {})
        metric2 = Entity("e4", "F1", "metric", 0.9, 70, 72, {})
        
        relationships = [
            Relationship("r1", model1, metric1, "achieves", 0.9, "GPT-4 achieves 95% accuracy", {"performance_value": "95%"}),
            Relationship("r2", model2, metric1, "achieves", 0.85, "BERT achieves 90% accuracy", {"performance_value": "90%"}),
            Relationship("r3", model2, metric2, "achieves", 0.85, "BERT achieves 0.88 F1", {"performance_value": "0.88"})
        ]
        
        # Extract model performance
        performance = self.extractor.extract_model_performance(relationships)
        
        # Check results
        self.assertIn("GPT-4", performance)
        self.assertIn("BERT", performance)
        self.assertIn("accuracy", performance["GPT-4"])
        self.assertIn("accuracy", performance["BERT"])
        self.assertIn("F1", performance["BERT"])
        self.assertEqual(performance["GPT-4"]["accuracy"], 0.95)
        self.assertEqual(performance["BERT"]["accuracy"], 0.9)
        self.assertEqual(performance["BERT"]["F1"], 0.88)


class TestRelationshipExtractorFactory(unittest.TestCase):
    """Tests for the RelationshipExtractorFactory class."""
    
    def test_create_pattern_extractor(self):
        """Test creating a pattern-based relationship extractor."""
        extractor = RelationshipExtractorFactory.create_extractor("pattern")
        
        self.assertIsInstance(extractor, PatternRelationshipExtractor)
        self.assertTrue(hasattr(extractor, "extract_relationships"))
    
    def test_create_ai_extractor(self):
        """Test creating an AI-specific relationship extractor."""
        extractor = RelationshipExtractorFactory.create_extractor("ai")
        
        self.assertIsInstance(extractor, AIRelationshipExtractor)
        self.assertTrue(hasattr(extractor, "extract_relationships"))
    
    def test_create_combined_extractor(self):
        """Test creating a combined relationship extractor."""
        extractor = RelationshipExtractorFactory.create_extractor("combined")
        
        self.assertTrue(hasattr(extractor, "extract_relationships"))
        self.assertTrue(hasattr(extractor, "extractors"))
        
        # Check that the combined extractor has the expected extractors
        extractor_types = [type(e).__name__ for e in extractor.extractors]
        expected_types = ["PatternRelationshipExtractor", "AIRelationshipExtractor"]
        for expected_type in expected_types:
            self.assertTrue(any(expected_type in e_type for e_type in extractor_types))
    
    def test_create_from_config(self):
        """Test creating a relationship extractor from config."""
        config = {
            "type": "ai",
            "config": {
                "relation_types": ["trained_on", "evaluated_on", "outperforms"],
                "use_karma": False
            }
        }
        
        extractor = RelationshipExtractorFactory.create_from_config(config)
        
        self.assertIsInstance(extractor, AIRelationshipExtractor)
        self.assertEqual(set(extractor.relation_types), set(["trained_on", "evaluated_on", "outperforms"]))
        self.assertFalse(extractor.use_karma)


if __name__ == '__main__':
    unittest.main()