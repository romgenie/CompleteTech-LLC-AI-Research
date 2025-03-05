"""
Tests for the relationship extraction module.
"""

import unittest
import os
import tempfile
import json
from typing import Dict, List, Any
from unittest.mock import MagicMock, patch

# Use the new src-based paths
from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship
from src.research_orchestrator.knowledge_extraction.relationship_extraction.base_extractor import RelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.pattern_extractor import PatternRelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.ai_extractor import AIRelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory


class TestRelationshipExtractor(unittest.TestCase):
    """Tests for the RelationshipExtractor class."""
    
    def test_relationship_creation(self):
        """Test relationship creation and conversion to/from dict."""
        source_entity = Entity(
            text="BERT",
            type="model",
            confidence=0.95,
            start_pos=10,
            end_pos=14,
            metadata={"source": "test"},
            id="entity_1"
        )
        
        target_entity = Entity(
            text="ImageNet",
            type="dataset",
            confidence=0.9,
            start_pos=30,
            end_pos=38,
            metadata={"source": "test"},
            id="entity_2"
        )
        
        relationship = Relationship(
            source=source_entity,
            target=target_entity,
            relation_type="trained_on",
            confidence=0.85,
            context="BERT was trained on ImageNet",
            metadata={"source": "test"},
            id="relationship_1"
        )
        
        self.assertEqual(relationship.id, "relationship_1")
        self.assertEqual(relationship.source.text, "BERT")
        self.assertEqual(relationship.target.text, "ImageNet")
        self.assertEqual(str(relationship.relation_type), "trained_on")
        self.assertEqual(relationship.confidence, 0.85)
        self.assertEqual(relationship.context, "BERT was trained on ImageNet")
        self.assertEqual(relationship.metadata, {"source": "test"})
        
        # Test conversion to dict
        relationship_dict = relationship.to_dict()
        self.assertEqual(relationship_dict["id"], "relationship_1")
        self.assertEqual(relationship_dict["relation_type"], "trained_on")
        self.assertEqual(relationship_dict["source"]["text"], "BERT")
        self.assertEqual(relationship_dict["target"]["text"], "ImageNet")
        
        # Test conversion from dict
        relationship2 = Relationship.from_dict(relationship_dict)
        self.assertEqual(relationship2.id, "relationship_1")
        self.assertEqual(relationship2.relation_type, "trained_on")
        self.assertEqual(relationship2.source.text, "BERT")
        self.assertEqual(relationship2.target.text, "ImageNet")
    
    def test_get_entity_pair_context(self):
        """Test getting context for an entity pair."""
        # Create a mock relationship extractor for testing
        class MockRelationshipExtractor(RelationshipExtractor):
            def extract_relationships(self, text, entities):
                return []
        
        extractor = MockRelationshipExtractor()
        
        # Create test entities
        entity1 = Entity(text="BERT", type="model", confidence=0.9, start_pos=10, end_pos=14, metadata={}, id="e1")
        entity2 = Entity(text="ImageNet", type="dataset", confidence=0.9, start_pos=30, end_pos=38, metadata={}, id="e2")
        
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
            Entity(text="BERT", type="model", confidence=0.9, start_pos=10, end_pos=14, metadata={}, id="e1"),
            Entity(text="ImageNet", type="dataset", confidence=0.9, start_pos=30, end_pos=38, metadata={}, id="e2"),
            Entity(text="GPT", type="model", confidence=0.9, start_pos=100, end_pos=103, metadata={}, id="e3"),
            Entity(text="CIFAR", type="dataset", confidence=0.9, start_pos=500, end_pos=505, metadata={}, id="e4")
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
            Entity(text="BERT", type="model", confidence=0.9, start_pos=0, end_pos=4, metadata={}, id="e1"),
            Entity(text="language model", type="model", confidence=0.8, start_pos=7, end_pos=21, metadata={}, id="e2"),
            Entity(text="Transformer", type="architecture", confidence=0.9, start_pos=44, end_pos=55, metadata={}, id="e3"),
            Entity(text="natural language processing", type="task", confidence=0.85, start_pos=72, end_pos=99, metadata={}, id="e4"),
            Entity(text="ResNet", type="model", confidence=0.9, start_pos=143, end_pos=149, metadata={}, id="e5"),
            Entity(text="convolutional neural network", type="architecture", confidence=0.85, start_pos=155, end_pos=185, metadata={}, id="e6"),
            Entity(text="residual learning", type="technique", confidence=0.8, start_pos=219, end_pos=236, metadata={}, id="e7")
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
            if (relationship.source.text == "BERT" and 
                relationship.relation_type == "is_a" and 
                relationship.target.text == "language model"):
                found_bert_is_a = True
            
            if (relationship.source.text == "BERT" and 
                relationship.relation_type == "based_on" and 
                relationship.target.text == "Transformer"):
                found_bert_based_on = True
            
            if (relationship.source.text == "ResNet" and 
                relationship.relation_type == "implements" and 
                relationship.target.text == "residual learning"):
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
            Entity(text="GPT-4", type="model", confidence=0.95, start_pos=0, end_pos=5, metadata={}, id="e1"),
            Entity(text="large dataset", type="dataset", confidence=0.8, start_pos=20, end_pos=33, metadata={}, id="e2"),
            Entity(text="MMLU", type="benchmark", confidence=0.9, start_pos=48, end_pos=52, metadata={}, id="e3"),
            Entity(text="accuracy", type="metric", confidence=0.85, start_pos=77, end_pos=85, metadata={}, id="e4"),
            Entity(text="GPT-3.5", type="model", confidence=0.9, start_pos=122, end_pos=129, metadata={}, id="e5"),
            Entity(text="BERT", type="model", confidence=0.9, start_pos=131, end_pos=135, metadata={}, id="e6"),
            Entity(text="Transformer", type="architecture", confidence=0.85, start_pos=145, end_pos=156, metadata={}, id="e7"),
            Entity(text="NLP", type="task", confidence=0.8, start_pos=190, end_pos=193, metadata={}, id="e8")
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
            if (relationship.source.text == "GPT-4" and 
                relationship.relation_type == "evaluated_on" and 
                relationship.target.text == "MMLU"):
                found_gpt4_evaluated = True
            
            if (relationship.source.text == "GPT-4" and 
                relationship.relation_type == "outperforms" and 
                relationship.target.text == "GPT-3.5"):
                found_gpt4_outperforms = True
            
            if (relationship.source.text == "BERT" and 
                relationship.relation_type == "uses" and 
                relationship.target.text == "Transformer"):
                found_bert_uses = True
        
        # We don't require all relationships to be found, but we expect at least one
        self.assertTrue(found_gpt4_evaluated or found_gpt4_outperforms or found_bert_uses)
    
    def test_extract_model_performance(self):
        """Test extracting model performance from relationships."""
        # Create relationships with performance information
        model1 = Entity(text="GPT-4", type="model", confidence=0.95, start_pos=0, end_pos=5, metadata={}, id="e1")
        model2 = Entity(text="BERT", type="model", confidence=0.9, start_pos=50, end_pos=54, metadata={}, id="e2")
        metric1 = Entity(text="accuracy", type="metric", confidence=0.9, start_pos=20, end_pos=28, metadata={}, id="e3")
        metric2 = Entity(text="F1", type="metric", confidence=0.9, start_pos=70, end_pos=72, metadata={}, id="e4")
        
        relationships = [
            Relationship(id="r1", source=model1, target=metric1, relation_type="achieves", confidence=0.9, context="GPT-4 achieves 95% accuracy", metadata={"performance_value": "95%"}),
            Relationship(id="r2", source=model2, target=metric1, relation_type="achieves", confidence=0.85, context="BERT achieves 90% accuracy", metadata={"performance_value": "90%"}),
            Relationship(id="r3", source=model2, target=metric2, relation_type="achieves", confidence=0.85, context="BERT achieves 0.88 F1", metadata={"performance_value": "0.88"})
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


class TestCombinedRelationshipExtractor(unittest.TestCase):
    """Tests for the CombinedRelationshipExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock extractors for testing
        self.mock_pattern_extractor = MagicMock()
        self.mock_ai_extractor = MagicMock()
        
        # Sample test text with AI relationships
        self.test_text = (
            "GPT-4 was trained on a large dataset and evaluated on the MMLU benchmark. "
            "The model achieves 86.4% accuracy, outperforming previous models like GPT-3.5. "
            "BERT uses the Transformer architecture and can be applied to various NLP tasks."
        )
        
        # Sample entities
        self.entities = [
            Entity(text="GPT-4", type="model", confidence=0.95, start_pos=0, end_pos=5, metadata={}, id="e1"),
            Entity(text="large dataset", type="dataset", confidence=0.8, start_pos=20, end_pos=33, metadata={}, id="e2"),
            Entity(text="MMLU", type="benchmark", confidence=0.9, start_pos=48, end_pos=52, metadata={}, id="e3"),
            Entity(text="accuracy", type="metric", confidence=0.85, start_pos=77, end_pos=85, metadata={}, id="e4"),
            Entity(text="GPT-3.5", type="model", confidence=0.9, start_pos=122, end_pos=129, metadata={}, id="e5"),
            Entity(text="BERT", type="model", confidence=0.9, start_pos=131, end_pos=135, metadata={}, id="e6"),
            Entity(text="Transformer", type="architecture", confidence=0.85, start_pos=145, end_pos=156, metadata={}, id="e7"),
            Entity(text="NLP", type="task", confidence=0.8, start_pos=190, end_pos=193, metadata={}, id="e8")
        ]
        
        # Configure mock extractors to return different relationships
        self.pattern_relationships = [
            Relationship(
                id="r1",
                source=self.entities[0],
                target=self.entities[1],
                relation_type="trained_on",
                confidence=0.8,
                context="GPT-4 was trained on a large dataset",
                metadata={}
            ),
            Relationship(
                id="r2",
                source=self.entities[5],
                target=self.entities[6],
                relation_type="uses",
                confidence=0.9,
                context="BERT uses the Transformer architecture",
                metadata={}
            )
        ]
        
        self.ai_relationships = [
            Relationship(
                id="r3",
                source=self.entities[0],
                target=self.entities[2],
                relation_type="evaluated_on",
                confidence=0.85,
                context="GPT-4 was evaluated on the MMLU benchmark",
                metadata={}
            ),
            Relationship(
                id="r4",
                source=self.entities[0],
                target=self.entities[4],
                relation_type="outperforms",
                confidence=0.75,
                context="The model achieves 86.4% accuracy, outperforming previous models like GPT-3.5",
                metadata={}
            ),
            # Duplicate relationship with different confidence
            Relationship(
                id="r5",
                source=self.entities[0],
                target=self.entities[1],
                relation_type="trained_on",
                confidence=0.7,
                context="GPT-4 was trained on a large dataset",
                metadata={}
            )
        ]
        
        self.mock_pattern_extractor.extract_relationships.return_value = self.pattern_relationships
        self.mock_ai_extractor.extract_relationships.return_value = self.ai_relationships
        
        # Create combined extractor with mocks
        from src.research_orchestrator.knowledge_extraction.relationship_extraction.combined_extractor import CombinedRelationshipExtractor
        self.extractor = CombinedRelationshipExtractor(
            extractors=[self.mock_pattern_extractor, self.mock_ai_extractor]
        )
    
    def test_extract_relationships(self):
        """Test extracting relationships using the combined extractor."""
        # Extract relationships
        relationships = self.extractor.extract_relationships(self.test_text, self.entities)
        
        # Check that both mock extractors were called
        self.mock_pattern_extractor.extract_relationships.assert_called_once_with(
            self.test_text, self.entities
        )
        self.mock_ai_extractor.extract_relationships.assert_called_once_with(
            self.test_text, self.entities
        )
        
        # Check that we got relationships from both extractors (but without duplicates)
        # Since one relationship appears in both with different confidences, we should get the one with higher confidence
        self.assertEqual(len(relationships), 4)  # 2 from pattern + 2 unique from AI
        
        # Check for specific relationships
        relation_types = {r.relation_type for r in relationships}
        expected_types = {"trained_on", "uses", "evaluated_on", "outperforms"}
        self.assertEqual(relation_types, expected_types)
        
        # Check that the duplicate relationship uses the higher confidence version
        trained_on_rel = [r for r in relationships if r.relation_type == "trained_on"][0]
        self.assertEqual(trained_on_rel.confidence, 0.8)  # Should have the higher confidence
    
    def test_combine_relationships(self):
        """Test combining relationships from different extractors."""
        # Call the private method directly
        combined = self.extractor._combine_relationships(
            self.pattern_relationships + self.ai_relationships
        )
        
        # Check that duplicates were properly handled
        self.assertEqual(len(combined), 4)
        
        # Check that the higher confidence version was kept
        trained_on_relationships = [r for r in combined if r.relation_type == "trained_on"]
        self.assertEqual(len(trained_on_relationships), 1)
        self.assertEqual(trained_on_relationships[0].confidence, 0.8)
    
    def test_is_duplicate_relationship(self):
        """Test identifying duplicate relationships."""
        # Create two relationships between the same entities with same relation type
        rel1 = Relationship(
            id="test1",
            source=self.entities[0],
            target=self.entities[1],
            relation_type="trained_on",
            confidence=0.8,
            context="Context 1",
            metadata={}
        )
        
        rel2 = Relationship(
            id="test2",
            source=self.entities[0],
            target=self.entities[1],
            relation_type="trained_on",
            confidence=0.7,
            context="Context 2",
            metadata={}
        )
        
        rel3 = Relationship(
            id="test3",
            source=self.entities[0],
            target=self.entities[2],  # Different target
            relation_type="trained_on",
            confidence=0.9,
            context="Context 3",
            metadata={}
        )
        
        rel4 = Relationship(
            id="test4",
            source=self.entities[0],
            target=self.entities[1],
            relation_type="uses",  # Different relation type
            confidence=0.85,
            context="Context 4",
            metadata={}
        )
        
        # Check is_duplicate_relationship method
        self.assertTrue(self.extractor._is_duplicate_relationship(rel1, rel2))
        self.assertFalse(self.extractor._is_duplicate_relationship(rel1, rel3))
        self.assertFalse(self.extractor._is_duplicate_relationship(rel1, rel4))
        self.assertFalse(self.extractor._is_duplicate_relationship(rel3, rel4))
    
    def test_filter_relationships(self):
        """Test filtering relationships based on confidence."""
        # Set up test relationships with various confidence scores
        relationships = [
            Relationship(
                id="r1",
                source=self.entities[0],
                target=self.entities[1],
                relation_type="trained_on",
                confidence=0.9,
                context="Context 1",
                metadata={}
            ),
            Relationship(
                id="r2",
                source=self.entities[0],
                target=self.entities[2],
                relation_type="evaluated_on",
                confidence=0.6,
                context="Context 2",
                metadata={}
            ),
            Relationship(
                id="r3",
                source=self.entities[5],
                target=self.entities[6],
                relation_type="uses",
                confidence=0.3,
                context="Context 3",
                metadata={}
            )
        ]
        
        # Filter with minimum confidence of 0.7
        filtered = self.extractor.filter_relationships(relationships, min_confidence=0.7)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].id, "r1")
        
        # Filter with minimum confidence of 0.5
        filtered = self.extractor.filter_relationships(relationships, min_confidence=0.5)
        self.assertEqual(len(filtered), 2)
        self.assertEqual({r.id for r in filtered}, {"r1", "r2"})
        
        # Filter by relation type
        filtered = self.extractor.filter_relationships(
            relationships, 
            relation_types={"trained_on", "uses"}
        )
        self.assertEqual(len(filtered), 2)
        self.assertEqual({r.relation_type for r in filtered}, {"trained_on", "uses"})


if __name__ == '__main__':
    unittest.main()