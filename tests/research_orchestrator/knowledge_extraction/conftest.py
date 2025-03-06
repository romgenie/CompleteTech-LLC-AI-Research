"""
Fixtures for knowledge extraction tests.

This module provides pytest fixtures for testing the knowledge extraction components,
including entity recognition, relationship extraction, document processing, and 
knowledge extraction core functionality.
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import MagicMock, patch

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.entity_recognition.base_recognizer import EntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.ai_recognizer import AIEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.scientific_recognizer import ScientificEntityRecognizer
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import Document, DocumentProcessor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.base_extractor import RelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.pattern_extractor import PatternRelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.ai_extractor import AIRelationshipExtractor
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
from src.research_orchestrator.knowledge_extraction.relationship_extraction.combined_extractor import CombinedRelationshipExtractor


@pytest.fixture
def sample_entity():
    """Return a sample entity for testing."""
    return Entity(
        text="BERT", 
        type=EntityType.MODEL,
        confidence=0.95,
        start_pos=10,
        end_pos=14,
        metadata={"source": "test"},
        id="test_entity_1"
    )


@pytest.fixture
def sample_entity_dict():
    """Return a sample entity dictionary for testing."""
    return {
        "id": "test_entity_1",
        "text": "BERT",
        "type": "model",
        "confidence": 0.95,
        "start_pos": 10,
        "end_pos": 14,
        "metadata": {"source": "test"}
    }


@pytest.fixture
def overlapping_entities():
    """Return a list of overlapping entities for testing."""
    return [
        Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=14, metadata={}, id="e1"),
        Entity(text="BERT model", type=EntityType.MODEL, confidence=0.8, start_pos=10, end_pos=20, metadata={}, id="e2"),
        Entity(text="GPT", type=EntityType.MODEL, confidence=0.9, start_pos=30, end_pos=33, metadata={}, id="e3"),
        Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.95, start_pos=30, end_pos=35, metadata={}, id="e4")
    ]


@pytest.fixture
def mock_entity_recognizer():
    """Return a mock entity recognizer for testing."""
    class MockEntityRecognizer(EntityRecognizer):
        def recognize(self, text):
            return []
    
    return MockEntityRecognizer()


@pytest.fixture
def ai_test_text():
    """Return sample text for AI entity recognition testing."""
    return (
        "In this paper, we introduce GPT-4, a large language model that outperforms "
        "previous models like GPT-3.5. We trained GPT-4 on a large dataset of text "
        "and evaluated it on the MMLU benchmark. The model achieves 86.4% accuracy "
        "on the benchmark, surpassing human performance. We implemented the model "
        "using PyTorch and trained it on NVIDIA A100 GPUs."
    )


@pytest.fixture
def scientific_test_text():
    """Return sample text for scientific entity recognition testing."""
    return (
        "Our hypothesis is that large language models can achieve better performance "
        "through careful fine-tuning. We conducted an ablation study to understand "
        "the impact of different training techniques. The results show that our approach "
        "significantly improves performance. This finding has implications for the field of "
        "natural language processing. As demonstrated by Smith et al. (2022), transfer "
        "learning is a powerful technique in this domain."
    )


@pytest.fixture
def sample_entities():
    """Return a list of sample entities for testing."""
    return [
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=0, end_pos=5, metadata={}, id="e1"),
        Entity(text="large dataset", type=EntityType.DATASET, confidence=0.8, start_pos=20, end_pos=33, metadata={}, id="e2"),
        Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.9, start_pos=48, end_pos=52, metadata={}, id="e3"),
        Entity(text="accuracy", type=EntityType.METRIC, confidence=0.85, start_pos=77, end_pos=85, metadata={}, id="e4"),
        Entity(text="GPT-3", type=EntityType.MODEL, confidence=0.9, start_pos=120, end_pos=125, metadata={}, id="e5")
    ]


@pytest.fixture
def sample_relationships(sample_entities):
    """Return a list of sample relationships for testing."""
    return [
        Relationship(
            source=sample_entities[0], 
            target=sample_entities[1], 
            relation_type=RelationType.TRAINED_ON, 
            confidence=0.9, 
            context="GPT-4 was trained on a large dataset", 
            metadata={},
            id="r1"
        ),
        Relationship(
            source=sample_entities[0], 
            target=sample_entities[2], 
            relation_type=RelationType.EVALUATED_ON, 
            confidence=0.85, 
            context="GPT-4 was evaluated on MMLU benchmark", 
            metadata={},
            id="r2"
        ),
        Relationship(
            source=sample_entities[0], 
            target=sample_entities[4], 
            relation_type=RelationType.OUTPERFORMS, 
            confidence=0.8, 
            context="GPT-4 outperforming previous models like GPT-3", 
            metadata={},
            id="r3"
        )
    ]


@pytest.fixture
def sample_text_document():
    """Return a sample text document for testing."""
    content = "GPT-4 was trained on a large dataset and evaluated on MMLU benchmark. " \
             "The model achieves 86.4% accuracy, outperforming previous models like GPT-3."
    
    return Document(
        content=content,
        document_type="text",
        path="/path/to/test.txt",
        metadata={"file_size": 100, "file_extension": ".txt", "line_count": 3}
    )


@pytest.fixture
def mock_document_processor():
    """Return a mock document processor for testing."""
    processor = MagicMock()
    processor.process_document.return_value = {
        "content": "GPT-4 was trained on a large dataset and evaluated on MMLU benchmark. "
                 "The model achieves 86.4% accuracy, outperforming previous models like GPT-3."
    }
    return processor


@pytest.fixture
def mock_entity_recognizer_with_entities(sample_entities):
    """Return a mock entity recognizer that returns sample entities."""
    recognizer = MagicMock()
    recognizer.recognize.return_value = sample_entities
    recognizer.filter_entities.return_value = sample_entities
    return recognizer


@pytest.fixture
def mock_relationship_extractor_with_relationships(sample_relationships):
    """Return a mock relationship extractor that returns sample relationships."""
    extractor = MagicMock()
    extractor.extract_relationships.return_value = sample_relationships
    extractor.filter_relationships.return_value = sample_relationships
    return extractor


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing and clean it up afterwards."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def document_directory():
    """Create a directory with test documents for document processing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create a text file
    with open(os.path.join(temp_dir, "test.txt"), "w") as f:
        f.write("This is a test document with AI content.\n")
        f.write("GPT-4 is a large language model developed by OpenAI.\n")
        f.write("It outperforms previous models like GPT-3 on various benchmarks.\n")
    
    # Create an HTML file
    with open(os.path.join(temp_dir, "test.html"), "w") as f:
        f.write("<html><head><title>Test Document</title></head><body>\n")
        f.write("<h1>AI Research Overview</h1>\n")
        f.write("<p>BERT is a transformer model developed by Google.</p>\n")
        f.write("<p>It uses bidirectional training for language representations.</p>\n")
        f.write("</body></html>")
    
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def integration_fixtures():
    """Create fixtures for integration testing."""
    return {
        "test_text": (
            "GPT-4 is a large language model developed by OpenAI. It was trained on a massive dataset "
            "of text and code, and it outperforms previous models like GPT-3.5 on many benchmarks. "
            "The model was evaluated on tasks such as the MMLU benchmark, where it achieved "
            "86.4% accuracy."
        ),
        "test_entities": [
            Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=0, end_pos=5, id="e1"),
            Entity(text="OpenAI", type=EntityType.ORGANIZATION, confidence=0.9, start_pos=44, end_pos=50, id="e2"),
            Entity(text="GPT-3.5", type=EntityType.MODEL, confidence=0.9, start_pos=135, end_pos=142, id="e3"),
            Entity(text="MMLU", type=EntityType.BENCHMARK, confidence=0.85, start_pos=198, end_pos=202, id="e4")
        ],
        "expected_relationship_types": [
            RelationType.DEVELOPED_BY, 
            RelationType.TRAINED_ON,
            RelationType.OUTPERFORMS,
            RelationType.EVALUATED_ON
        ]
    }


@pytest.fixture
def knowledge_extractor(mock_document_processor, mock_entity_recognizer_with_entities, 
                       mock_relationship_extractor_with_relationships):
    """Return a KnowledgeExtractor with mock components."""
    from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
    
    extractor = KnowledgeExtractor(
        document_processor=mock_document_processor,
        entity_recognizer=mock_entity_recognizer_with_entities,
        relationship_extractor=mock_relationship_extractor_with_relationships
    )
    return extractor


@pytest.fixture
def real_knowledge_extractor():
    """Return a KnowledgeExtractor with real components for integration testing."""
    from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
    from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
    
    # Create real components
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    relationship_extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    extractor = KnowledgeExtractor(
        document_processor=document_processor,
        entity_recognizer=entity_recognizer,
        relationship_extractor=relationship_extractor
    )
    return extractor