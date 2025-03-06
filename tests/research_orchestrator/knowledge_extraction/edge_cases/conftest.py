"""
Fixtures for edge case and error handling tests.

This module provides pytest fixtures for testing edge cases and error handling
in the knowledge extraction components.
"""

import pytest
import os
import tempfile
import string
import random
import io

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import Document, DocumentProcessor
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor


@pytest.fixture
def empty_document():
    """Return an empty document."""
    return Document(
        content="",
        document_type="text",
        path="/path/to/empty.txt",
        metadata={}
    )


@pytest.fixture
def very_large_document():
    """Return a very large document (10MB)."""
    # Generate 10MB of random text
    chars = string.ascii_letters + string.digits + ' ' * 10 + '\n' * 2
    content = ''.join(random.choices(chars, k=10 * 1024 * 1024))  # 10MB
    
    return Document(
        content=content,
        document_type="text",
        path="/path/to/large.txt",
        metadata={"size": "10MB"}
    )


@pytest.fixture
def malformed_html_document():
    """Return a document with malformed HTML."""
    content = """
    <html>
    <head>
    <title>Malformed HTML Example</title>
    </head>
    <body>
    <p>This is a paragraph with <strong>unclosed strong tag.
    <div>This div has no closing tag.
    <ul>
        <li>Item 1
        <li>Item 2</li>
    </body>
    </html>
    """
    
    return Document(
        content=content,
        document_type="html",
        path="/path/to/malformed.html",
        metadata={}
    )


@pytest.fixture
def document_with_invalid_encoding():
    """Return a document with invalid encoding."""
    # Create content with invalid UTF-8 sequence
    content = "This document contains an invalid UTF-8 sequence: " + "\xc3\x28" + " which is invalid."
    
    return Document(
        content=content,
        document_type="text",
        path="/path/to/invalid_encoding.txt",
        metadata={}
    )


@pytest.fixture
def document_with_special_characters():
    """Return a document with special characters."""
    content = """
    This document contains various special characters:
    • Bullets and other symbols: ©®™•★☆♦♣♠♥
    • Emoji: 😀🤣😎👍❤️🔥
    • Mathematical symbols: ∑∫√≤≥≠
    • Various languages:
      - Arabic: مرحبا بالعالم
      - Chinese: 你好，世界
      - Japanese: こんにちは世界
      - Russian: Привет, мир
      - Greek: Γειά σου Κόσμε
    """
    
    return Document(
        content=content,
        document_type="text",
        path="/path/to/special_chars.txt",
        metadata={}
    )


@pytest.fixture
def document_with_code():
    """Return a document containing code snippets."""
    content = """
    # Example Python code
    def hello_world():
        print("Hello, world!")
        
    # Example of a class
    class MyClass:
        def __init__(self, name):
            self.name = name
            
        def say_hello(self):
            return f"Hello, {self.name}!"
            
    # Example of using a library
    import tensorflow as tf
    
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    """
    
    return Document(
        content=content,
        document_type="text",
        path="/path/to/code.txt",
        metadata={}
    )


@pytest.fixture
def duplicate_entities():
    """Return a list of entities with duplicates."""
    entities = [
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=15, id="e1"),
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.8, start_pos=10, end_pos=15, id="e2"),
        Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=20, end_pos=24, id="e3"),
        Entity(text="BERT", type=EntityType.MODEL, confidence=0.85, start_pos=20, end_pos=24, id="e4"),
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.95, start_pos=30, end_pos=35, id="e5")
    ]
    return entities


@pytest.fixture
def conflicting_entities():
    """Return a list of entities with conflicting types."""
    entities = [
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=15, id="e1"),
        Entity(text="GPT-4", type=EntityType.ALGORITHM, confidence=0.8, start_pos=10, end_pos=15, id="e2"),
        Entity(text="BERT", type=EntityType.MODEL, confidence=0.9, start_pos=20, end_pos=24, id="e3"),
        Entity(text="BERT", type=EntityType.FRAMEWORK, confidence=0.7, start_pos=20, end_pos=24, id="e4")
    ]
    return entities


@pytest.fixture
def overlapping_entities():
    """Return a list of entities with complex overlaps."""
    entities = [
        Entity(text="GPT", type=EntityType.MODEL, confidence=0.8, start_pos=10, end_pos=13, id="e1"),
        Entity(text="GPT-4", type=EntityType.MODEL, confidence=0.9, start_pos=10, end_pos=15, id="e2"),
        Entity(text="GPT-4 model", type=EntityType.MODEL, confidence=0.7, start_pos=10, end_pos=20, id="e3"),
        Entity(text="BERT model", type=EntityType.MODEL, confidence=0.9, start_pos=30, end_pos=40, id="e4"),
        Entity(text="model", type=EntityType.MODEL, confidence=0.6, start_pos=35, end_pos=40, id="e5")
    ]
    return entities


@pytest.fixture
def circular_relationships(duplicate_entities):
    """Return a list of relationships with circular references."""
    # Get some entities to work with
    e1, e2, e3, e4, e5 = duplicate_entities
    
    relationships = [
        Relationship(source=e1, target=e3, relation_type=RelationType.OUTPERFORMS, confidence=0.8, context="", id="r1"),
        Relationship(source=e3, target=e5, relation_type=RelationType.OUTPERFORMS, confidence=0.7, context="", id="r2"),
        Relationship(source=e5, target=e1, relation_type=RelationType.OUTPERFORMS, confidence=0.9, context="", id="r3")
    ]
    return relationships


@pytest.fixture
def conflicting_relationships(duplicate_entities):
    """Return a list of relationships with conflicting information."""
    # Get some entities to work with
    e1, e2, e3, e4, e5 = duplicate_entities
    
    relationships = [
        Relationship(source=e1, target=e3, relation_type=RelationType.OUTPERFORMS, confidence=0.8, context="", id="r1"),
        Relationship(source=e3, target=e1, relation_type=RelationType.OUTPERFORMS, confidence=0.7, context="", id="r2")
    ]
    return relationships


@pytest.fixture
def invalid_document_path():
    """Return an invalid document path."""
    return "/path/that/does/not/exist.txt"


@pytest.fixture
def malformed_json_file():
    """Create and return path to a malformed JSON file."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.write(b'{"this": "is", "not": "valid", json')
        file_path = f.name
    
    yield file_path
    
    # Clean up
    os.unlink(file_path)


@pytest.fixture
def edge_case_document_processor():
    """Return a document processor for edge case testing."""
    return DocumentProcessor()


@pytest.fixture
def edge_case_entity_recognizer():
    """Return an entity recognizer for edge case testing."""
    return EntityRecognizerFactory.create_recognizer("ai")


@pytest.fixture
def edge_case_relationship_extractor():
    """Return a relationship extractor for edge case testing."""
    return RelationshipExtractorFactory.create_extractor("pattern")


@pytest.fixture
def edge_case_knowledge_extractor(edge_case_document_processor, edge_case_entity_recognizer, edge_case_relationship_extractor):
    """Return a knowledge extractor for edge case testing."""
    return KnowledgeExtractor(
        document_processor=edge_case_document_processor,
        entity_recognizer=edge_case_entity_recognizer,
        relationship_extractor=edge_case_relationship_extractor
    )


@pytest.fixture
def temp_output_directory():
    """Create a temporary directory for output testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def read_only_directory():
    """Create a read-only temporary directory."""
    temp_dir = tempfile.mkdtemp()
    
    # Make directory read-only (on Unix-like systems)
    if os.name != 'nt':  # Skip on Windows
        os.chmod(temp_dir, 0o555)  # Read and execute, but not write
    
    yield temp_dir
    
    # Make it writable again for cleanup
    if os.name != 'nt':
        os.chmod(temp_dir, 0o755)
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir)