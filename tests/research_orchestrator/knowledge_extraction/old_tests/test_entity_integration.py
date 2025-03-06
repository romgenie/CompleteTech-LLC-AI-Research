"""
Integration tests for entity recognition with document processing.

This module contains tests that validate the integration between document processing
and entity recognition, ensuring documents can be properly processed and entities
can be correctly extracted.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType


def test_entity_extraction_from_text_document(document_directory):
    """Test extracting entities from a text document."""
    # Create the document processor and entity recognizer
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Process the document
    text_file_path = os.path.join(document_directory, "test.txt")
    document = document_processor.process_document(text_file_path)
    
    # Verify the document was properly processed
    assert document.content is not None
    assert document.document_type == "text"
    assert "GPT-4" in document.content
    
    # Extract entities
    entities = entity_recognizer.recognize(document.content)
    
    # Verify entities were extracted
    assert len(entities) > 0
    
    # Check for expected entity types in the extracted entities
    model_entities = [e for e in entities if e.type == EntityType.MODEL]
    assert len(model_entities) > 0, "No model entities found"
    
    # Verify at least one of the expected entities was found
    expected_models = ["GPT-4", "GPT-3"]
    found_models = [e.text for e in model_entities]
    
    # Check if any expected model is in the list of found models
    has_expected_model = any(expected in ' '.join(found_models) for expected in expected_models)
    assert has_expected_model, f"None of the expected models {expected_models} were found. Found: {found_models}"


def test_entity_extraction_from_html_document(document_directory):
    """Test extracting entities from an HTML document."""
    # Create the document processor and entity recognizer
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Process the document
    html_file_path = os.path.join(document_directory, "test.html")
    document = document_processor.process_document(html_file_path)
    
    # Verify the document was properly processed
    assert document.content is not None
    assert document.document_type == "html"
    assert "BERT" in document.content
    
    # Extract entities
    entities = entity_recognizer.recognize(document.content)
    
    # Verify entities were extracted
    assert len(entities) > 0
    
    # Check for expected entity types in the extracted entities
    model_entities = [e for e in entities if e.type == EntityType.MODEL]
    assert len(model_entities) > 0, "No model entities found"
    
    # Verify at least one of the expected entities was found
    expected_models = ["BERT"]
    found_models = [e.text for e in model_entities]
    
    # Check if any expected model is in the list of found models
    has_expected_model = any(expected in ' '.join(found_models) for expected in expected_models)
    assert has_expected_model, f"None of the expected models {expected_models} were found. Found: {found_models}"


def test_entity_filtering_integration():
    """Test filtering entities by type and confidence score."""
    # Create an entity recognizer
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Sample text with AI content
    test_text = """
    GPT-4 is a large language model developed by OpenAI. It was trained on a massive dataset
    of text and code, and it outperforms previous models like GPT-3.5 on many benchmarks.
    The model was evaluated on tasks such as the MMLU benchmark, where it achieved
    86.4% accuracy. Researchers implemented the model using PyTorch framework.
    """
    
    # Extract entities
    entities = entity_recognizer.recognize(test_text)
    
    # Verify entities were extracted
    assert len(entities) > 0
    
    # Filter entities by confidence
    high_confidence = entity_recognizer.filter_entities(entities, min_confidence=0.8)
    low_confidence = entity_recognizer.filter_entities(entities, min_confidence=0.5)
    assert len(high_confidence) <= len(low_confidence)
    
    # Filter entities by type
    models = entity_recognizer.filter_entities(entities, entity_types=[EntityType.MODEL])
    assert all(e.type == EntityType.MODEL for e in models)
    
    frameworks = entity_recognizer.filter_entities(entities, entity_types=[EntityType.FRAMEWORK])
    datasets = entity_recognizer.filter_entities(entities, entity_types=[EntityType.DATASET])
    benchmarks = entity_recognizer.filter_entities(entities, entity_types=[EntityType.BENCHMARK])
    
    # Combine filtered results
    combined_entities = models + frameworks + datasets + benchmarks
    assert len(combined_entities) <= len(entities)


def test_entity_context_extraction():
    """Test extracting context around entities."""
    # Create an entity recognizer
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Sample text with AI content
    test_text = """
    GPT-4 is a large language model developed by OpenAI. It was trained on a massive dataset
    of text and code, and it outperforms previous models like GPT-3.5 on many benchmarks.
    The model was evaluated on tasks such as the MMLU benchmark, where it achieved
    86.4% accuracy.
    """
    
    # Extract entities
    entities = entity_recognizer.recognize(test_text)
    
    # Verify entities were extracted
    assert len(entities) > 0
    
    # Get a model entity
    model_entities = [e for e in entities if e.type == EntityType.MODEL]
    if model_entities:
        model = model_entities[0]
        
        # Extract context around the entity (assuming a get_entity_context method)
        if hasattr(entity_recognizer, 'get_entity_context'):
            context = entity_recognizer.get_entity_context(test_text, model, window_size=20)
            
            # Verify the context contains the entity
            assert model.text in context
            
            # Verify the context is of appropriate length
            assert len(context) <= len(model.text) + 2 * 20  # entity text + window on each side


def test_entity_serialization_integration(document_directory, temp_directory):
    """Test serialization and deserialization of entities from a document."""
    # Create the document processor and entity recognizer
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Process the document
    text_file_path = os.path.join(document_directory, "test.txt")
    document = document_processor.process_document(text_file_path)
    
    # Extract entities
    entities = entity_recognizer.recognize(document.content)
    
    # Verify entities were extracted
    assert len(entities) > 0
    
    # Create a serialization directory
    os.makedirs(os.path.join(temp_directory, "entities"), exist_ok=True)
    
    # Serialize entities to JSON
    entities_path = os.path.join(temp_directory, "entities", "entities.json")
    with open(entities_path, "w") as f:
        json.dump([e.to_dict() for e in entities], f, indent=2)
    
    # Read the entities back
    with open(entities_path, "r") as f:
        entity_dicts = json.load(f)
    
    # Deserialize entities
    loaded_entities = [entity_recognizer.entity_class.from_dict(e_dict) for e_dict in entity_dicts]
    
    # Verify the entities were properly deserialized
    assert len(loaded_entities) == len(entities)
    
    # Check that the key properties are preserved
    for i, entity in enumerate(entities):
        loaded = loaded_entities[i]
        assert loaded.id == entity.id
        assert loaded.text == entity.text
        assert loaded.type == entity.type
        assert loaded.confidence == entity.confidence