"""
Unit tests for the entity recognition component.

This module contains tests for the Entity class, EntityRecognizer, AIEntityRecognizer,
ScientificEntityRecognizer, and EntityRecognizerFactory classes, focusing on testing
entity creation, recognition, filtering, and factory functionality.
"""

import pytest

# Mark all tests in this module as unit tests and entity related tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.entity,
    pytest.mark.fast
]
from unittest.mock import MagicMock, patch

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.entity_recognition.base_recognizer import EntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.ai_recognizer import AIEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.scientific_recognizer import ScientificEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory


class TestEntity:
    """Tests for the Entity class."""
    
    def test_entity_creation(self):
        """Test creating an Entity with proper attributes."""
        entity = Entity(
            text="BERT",
            type=EntityType.MODEL,
            confidence=0.95,
            start_pos=10,
            end_pos=14,
            metadata={"source": "test"},
            id="entity_1"
        )
        
        assert entity.id == "entity_1"
        assert entity.text == "BERT"
        assert entity.type == EntityType.MODEL
        assert entity.confidence == 0.95
        assert entity.start_pos == 10
        assert entity.end_pos == 14
        assert entity.metadata == {"source": "test"}
    
    def test_entity_to_dict(self):
        """Test conversion of Entity to dictionary."""
        entity = Entity(
            text="BERT",
            type=EntityType.MODEL,
            confidence=0.95,
            start_pos=10,
            end_pos=14,
            metadata={"source": "test"},
            id="entity_1"
        )
        
        entity_dict = entity.to_dict()
        
        assert entity_dict["id"] == "entity_1"
        assert entity_dict["text"] == "BERT"
        assert entity_dict["type"] == "model"
        assert entity_dict["confidence"] == 0.95
        assert entity_dict["start_pos"] == 10
        assert entity_dict["end_pos"] == 14
        assert entity_dict["metadata"] == {"source": "test"}
    
    def test_entity_from_dict(self):
        """Test creation of Entity from dictionary."""
        entity_dict = {
            "id": "entity_1",
            "text": "BERT",
            "type": "model",
            "confidence": 0.95,
            "start_pos": 10,
            "end_pos": 14,
            "metadata": {"source": "test"}
        }
        
        entity = Entity.from_dict(entity_dict)
        
        assert entity.id == "entity_1"
        assert entity.text == "BERT"
        assert entity.type == EntityType.MODEL
        assert entity.confidence == 0.95
        assert entity.start_pos == 10
        assert entity.end_pos == 14
        assert entity.metadata == {"source": "test"}
    
    def test_entity_str_representation(self):
        """Test string representation of Entity."""
        entity = Entity(
            text="BERT",
            type=EntityType.MODEL,
            confidence=0.95,
            start_pos=10,
            end_pos=14,
            metadata={},
            id="entity_1"
        )
        
        entity_str = str(entity)
        
        assert "BERT" in entity_str
        assert "model" in entity_str.lower()
        assert "0.95" in entity_str


class TestEntityRecognizer:
    """Tests for the EntityRecognizer base class."""
    
    def test_base_recognizer_creation(self):
        """Test creating a base EntityRecognizer."""
        class TestRecognizer(EntityRecognizer):
            def recognize(self, text):
                return []
        
        recognizer = TestRecognizer()
        assert recognizer is not None
    
    def test_merge_overlapping_entities(self):
        """Test merging overlapping entities."""
        class TestRecognizer(EntityRecognizer):
            def recognize(self, text):
                return []
        
        recognizer = TestRecognizer()
        
        # Create overlapping entities
        entities = [
            Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, id="e1"),
            Entity(text="BERT model", type=EntityType.MODEL, confidence=0.8, start_pos=10, end_pos=20, id="e2"),
            Entity(text="GPT", type=EntityType.MODEL, confidence=0.9, start_pos=30, end_pos=33, id="e3"),
            Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.95, start_pos=30, end_pos=35, id="e4")
        ]
        
        # Merge entities
        merged = recognizer.merge_overlapping_entities(entities)
        
        # Should have merged down to 2 entities (one for BERT, one for GPT)
        assert len(merged) == 2
        
        # GPT-3 should be chosen over GPT due to higher confidence
        gpt_entity = next((e for e in merged if "GPT" in e.text), None)
        assert gpt_entity is not None
        assert gpt_entity.text == "GPT-3"
        assert gpt_entity.confidence == 0.95
        
        # BERT entity could be either one depending on the implementation
        bert_entity = next((e for e in merged if "BERT" in e.text), None)
        assert bert_entity is not None
        assert bert_entity.text in ["BERT", "BERT model"]
    
    def test_filter_entities(self):
        """Test filtering entities by type and confidence."""
        class TestRecognizer(EntityRecognizer):
            def recognize(self, text):
                return []
        
        recognizer = TestRecognizer()
        
        # Create test entities
        entities = [
            Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, id="e1"),
            Entity(text="ImageNet", type=EntityType.DATASET, confidence=0.8, start_pos=20, end_pos=28, id="e2"),
            Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.7, start_pos=30, end_pos=35, id="e3"),
            Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.85, start_pos=40, end_pos=44, id="e4")
        ]
        
        # Filter by type
        models = recognizer.filter_entities(entities, entity_types=[EntityType.MODEL])
        assert len(models) == 2
        assert all(e.type == EntityType.MODEL for e in models)
        
        # Filter by confidence
        high_confidence = recognizer.filter_entities(entities, min_confidence=0.85)
        assert len(high_confidence) == 2
        assert all(e.confidence >= 0.85 for e in high_confidence)
        
        # Filter by both type and confidence
        high_confidence_models = recognizer.filter_entities(
            entities, 
            entity_types=[EntityType.MODEL], 
            min_confidence=0.85
        )
        assert len(high_confidence_models) == 1
        assert high_confidence_models[0].text == "BERT"
        assert high_confidence_models[0].type == EntityType.MODEL
        assert high_confidence_models[0].confidence >= 0.85


class TestAIEntityRecognizer:
    """Tests for the AIEntityRecognizer class."""
    
    def test_ai_recognizer_creation(self):
        """Test creating an AIEntityRecognizer."""
        recognizer = AIEntityRecognizer()
        assert recognizer is not None
        assert hasattr(recognizer, "patterns")
    
    def test_ai_recognizer_with_custom_patterns(self):
        """Test creating an AIEntityRecognizer with custom patterns."""
        custom_patterns = {
            str(EntityType.MODEL): [r"GPT-\d+", r"BERT(?:-\w+)?"],
            str(EntityType.DATASET): [r"ImageNet"]
        }
        
        recognizer = AIEntityRecognizer(config={"patterns": custom_patterns})
        # Check that MODEL and DATASET are in patterns and have at least one compiled pattern
        assert EntityType.MODEL in recognizer.patterns
        assert len(recognizer.patterns[EntityType.MODEL]) > 0
        assert EntityType.DATASET in recognizer.patterns 
        assert len(recognizer.patterns[EntityType.DATASET]) > 0
    
    @patch.object(AIEntityRecognizer, "recognize")
    def test_ai_entity_recognition(self, mock_recognize):
        """Test entity recognition with AI text."""
        # Set up mock
        mock_recognize.return_value = [
            Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=15, id="e1"),
            Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.9, start_pos=30, end_pos=34, id="e2"),
            Entity(text="PyTorch", type=EntityType.FRAMEWORK, confidence=0.85, start_pos=50, end_pos=57, id="e3")
        ]
        
        # Create recognizer and recognize entities
        recognizer = AIEntityRecognizer()
        text = "Sample AI text mentioning GPT-4, MMLU benchmark, and PyTorch"
        entities = recognizer.recognize(text)
        
        # Verify results
        mock_recognize.assert_called_once_with(text)
        assert len(entities) == 3
        assert entities[0].text == "GPT-4"
        assert entities[0].type == EntityType.MODEL
        assert entities[1].text == "MMLU"
        assert entities[1].type == EntityType.BENCHMARK
    
    @patch.object(AIEntityRecognizer, "recognize")
    def test_ai_entity_filtering(self, mock_recognize):
        """Test filtering AI entities by type."""
        # Set up mock
        mock_recognize.return_value = [
            Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=10, end_pos=15, id="e1"),
            Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=20, end_pos=24, id="e2"),
            Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.9, start_pos=30, end_pos=34, id="e3"),
            Entity(text="PyTorch", type=EntityType.FRAMEWORK, confidence=0.85, start_pos=50, end_pos=57, id="e4")
        ]
        
        # Create recognizer and recognize entities
        recognizer = AIEntityRecognizer()
        text = "Sample text"
        entities = recognizer.recognize(text)
        
        # Filter by type
        models = recognizer.filter_entities(entities, entity_types=[EntityType.MODEL])
        assert len(models) == 2
        assert all(e.type == EntityType.MODEL for e in models)
        assert set(e.text for e in models) == {"GPT-4", "BERT"}
        
        # Filter by type and confidence
        high_confidence_models = recognizer.filter_entities(
            entities, 
            entity_types=[EntityType.MODEL], 
            min_confidence=0.95
        )
        assert len(high_confidence_models) == 1
        assert high_confidence_models[0].text == "GPT-4"


class TestScientificEntityRecognizer:
    """Tests for the ScientificEntityRecognizer class."""
    
    def test_scientific_recognizer_creation(self):
        """Test creating a ScientificEntityRecognizer."""
        recognizer = ScientificEntityRecognizer()
        assert recognizer is not None
        assert hasattr(recognizer, "patterns")
    
    @patch.object(ScientificEntityRecognizer, "recognize")
    def test_scientific_entity_recognition(self, mock_recognize):
        """Test entity recognition with scientific text."""
        # Set up mock
        mock_recognize.return_value = [
            Entity(text="Our hypothesis", type=EntityType.HYPOTHESIS, confidence=0.9, start_pos=0, end_pos=13, id="e1"),
            Entity(text="ablation study", type=EntityType.METHODOLOGY, confidence=0.85, start_pos=30, end_pos=44, id="e2"),
            Entity(text="improved performance", type=EntityType.FINDING, confidence=0.8, start_pos=80, end_pos=100, id="e3")
        ]
        
        # Create recognizer and recognize entities
        recognizer = ScientificEntityRecognizer()
        text = "Our hypothesis is that language models improve with size. We conducted an ablation study to verify this. Results showed improved performance."
        entities = recognizer.recognize(text)
        
        # Verify results
        mock_recognize.assert_called_once_with(text)
        assert len(entities) == 3
        assert entities[0].text == "Our hypothesis"
        assert entities[0].type == EntityType.HYPOTHESIS
        assert entities[1].text == "ablation study"
        assert entities[1].type == EntityType.METHODOLOGY
        assert entities[2].text == "improved performance"
        assert entities[2].type == EntityType.FINDING


class TestEntityRecognizerFactory:
    """Tests for the EntityRecognizerFactory class."""
    
    def test_create_ai_recognizer(self):
        """Test creating an AI entity recognizer."""
        recognizer = EntityRecognizerFactory.create_recognizer("ai")
        assert isinstance(recognizer, AIEntityRecognizer)
    
    def test_create_scientific_recognizer(self):
        """Test creating a scientific entity recognizer."""
        recognizer = EntityRecognizerFactory.create_recognizer("scientific")
        assert isinstance(recognizer, ScientificEntityRecognizer)
    
    def test_create_with_config(self):
        """Test creating an entity recognizer with configuration."""
        config = {
            "patterns": {
                "MODEL": [r"GPT-\d+", r"BERT"]
            }
        }
        
        recognizer = EntityRecognizerFactory.create_recognizer("ai", config)
        assert isinstance(recognizer, AIEntityRecognizer)
        assert hasattr(recognizer, "patterns")
    
    def test_create_combined_recognizer(self):
        """Test creating a combined entity recognizer."""
        config = {
            "recognizers": [
                {"type": "ai"},
                {"type": "scientific"}
            ]
        }
        
        recognizer = EntityRecognizerFactory.create_recognizer("combined", config)
        assert hasattr(recognizer, "recognizers")
        assert len(recognizer.recognizers) == 2
        assert isinstance(recognizer.recognizers[0], AIEntityRecognizer)
        assert isinstance(recognizer.recognizers[1], ScientificEntityRecognizer)
    
    def test_create_invalid_recognizer(self):
        """Test creating an invalid entity recognizer."""
        with pytest.raises(ValueError):
            EntityRecognizerFactory.create_recognizer("invalid_type")