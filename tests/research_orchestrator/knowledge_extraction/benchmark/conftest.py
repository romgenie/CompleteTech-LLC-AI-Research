"""
Fixtures for benchmark tests.

This module provides pytest fixtures for benchmarking the performance
of the knowledge extraction components.
"""

import pytest
import os
import tempfile
import random
import string
import time

from research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from research_orchestrator.knowledge_extraction.document_processing.document_processor import Document, DocumentProcessor
from research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
from research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor


@pytest.fixture
def benchmark_document_processor():
    """Return a document processor for benchmarking."""
    return DocumentProcessor()


@pytest.fixture
def benchmark_entity_recognizer():
    """Return an entity recognizer for benchmarking."""
    return EntityRecognizerFactory.create_recognizer("ai")


@pytest.fixture
def benchmark_relationship_extractor():
    """Return a relationship extractor for benchmarking."""
    return RelationshipExtractorFactory.create_extractor("pattern")


@pytest.fixture
def benchmark_knowledge_extractor(benchmark_document_processor, benchmark_entity_recognizer, benchmark_relationship_extractor):
    """Return a knowledge extractor for benchmarking."""
    return KnowledgeExtractor(
        document_processor=benchmark_document_processor,
        entity_recognizer=benchmark_entity_recognizer,
        relationship_extractor=benchmark_relationship_extractor
    )


@pytest.fixture
def generate_text_document():
    """Generate a text document of the given size."""
    def _generate(size_kb):
        # Generate random paragraphs
        paragraphs = []
        remaining_size = size_kb * 1024  # Convert to bytes
        
        # Add some AI-related content to ensure entity detection
        ai_terms = [
            "GPT-4 is a large language model developed by OpenAI.",
            "BERT was created by Google and revolutionized NLP.",
            "PyTorch is a popular framework for deep learning.",
            "The MMLU benchmark is used to evaluate language models.",
            "Transformer architecture is the foundation of modern NLP models.",
            "ResNet is a convolutional neural network architecture.",
            "ImageNet is a large dataset used for training computer vision models.",
            "TensorFlow was developed by Google for machine learning tasks."
        ]
        
        # Add AI terms as initial paragraphs
        for term in ai_terms:
            paragraphs.append(term)
            remaining_size -= len(term) + 2  # +2 for newlines
        
        # Generate random paragraphs to fill the remaining size
        while remaining_size > 0:
            # Generate a random paragraph
            paragraph_length = min(random.randint(50, 200), remaining_size)
            paragraph = ''.join(random.choices(string.ascii_letters + string.digits + ' ' + ',.!?', k=paragraph_length))
            paragraphs.append(paragraph)
            remaining_size -= len(paragraph) + 2  # +2 for newlines
        
        # Join paragraphs with double newlines
        content = '\n\n'.join(paragraphs)
        
        # Create a Document
        return Document(
            content=content,
            document_type="text",
            path=None,
            metadata={"size_kb": size_kb}
        )
    
    return _generate


@pytest.fixture
def generate_entities():
    """Generate a list of random entities."""
    def _generate(count):
        entities = []
        
        # Define some common entity texts for each type
        entity_texts = {
            EntityType.MODEL: ["GPT-4", "BERT", "ResNet", "VGG", "Transformer", "LSTM", "RNN", "CNN"],
            EntityType.DATASET: ["ImageNet", "COCO", "CIFAR-10", "MNIST", "WMT", "BookCorpus"],
            EntityType.BENCHMARK: ["MMLU", "GLUE", "SQuAD", "BLEU", "ROUGE", "WER"],
            EntityType.FRAMEWORK: ["PyTorch", "TensorFlow", "JAX", "Keras", "scikit-learn"],
            EntityType.INSTITUTION: ["OpenAI", "Google", "Microsoft", "Meta", "DeepMind"]
        }
        
        # Generate entities
        for i in range(count):
            # Choose a random entity type
            entity_type = random.choice(list(EntityType))
            
            # Choose a text from the appropriate list, or a random one if not in our predefined lists
            if entity_type in entity_texts:
                entity_text = random.choice(entity_texts[entity_type])
            else:
                entity_text = "Entity_" + ''.join(random.choices(string.ascii_letters, k=5))
            
            # Create entity
            entity = Entity(
                id=f"e{i}",
                text=entity_text,
                type=entity_type,
                confidence=random.uniform(0.5, 1.0),
                start_pos=random.randint(0, 1000),
                end_pos=random.randint(1001, 2000),
                metadata={}
            )
            
            entities.append(entity)
        
        return entities
    
    return _generate


@pytest.fixture
def generate_relationships():
    """Generate a list of random relationships between the given entities."""
    def _generate(entities, count):
        if len(entities) < 2:
            return []
        
        relationships = []
        
        for i in range(count):
            # Choose random source and target entities
            source = random.choice(entities)
            target = random.choice([e for e in entities if e.id != source.id])
            
            # Choose a random relationship type
            relation_type = random.choice(list(RelationType))
            
            # Create relationship
            relationship = Relationship(
                id=f"r{i}",
                source=source,
                target=target,
                relation_type=relation_type,
                confidence=random.uniform(0.5, 1.0),
                context=f"Context between {source.text} and {target.text}",
                metadata={}
            )
            
            relationships.append(relationship)
        
        return relationships
    
    return _generate


@pytest.fixture
def benchmark_temp_directory():
    """Create a temporary directory for benchmarking."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Don't delete the directory to allow inspection of benchmark results


class Timer:
    """Utility class for timing operations."""
    
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        print(f"{self.name}: {self.duration:.4f} seconds")
    
    @property
    def duration(self):
        """Return the duration in seconds."""
        if self.start_time is None or self.end_time is None:
            return 0
        return self.end_time - self.start_time


@pytest.fixture
def timer():
    """Return a Timer instance for benchmarking."""
    return Timer