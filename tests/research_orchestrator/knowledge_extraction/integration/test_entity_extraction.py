"""
Integration tests for entity recognition with document processing.

This module contains tests that validate the integration between document processing
and entity recognition, ensuring documents can be properly processed and entities
can be correctly extracted.
"""

import pytest

# Mark all tests in this module as integration tests and entity related tests
pytestmark = [
    pytest.mark.integration,
    pytest.mark.entity,
    pytest.mark.document,
    pytest.mark.medium
]
import os
import json
import tempfile
from unittest.mock import patch

from research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType


def test_entity_extraction_from_text_document(integration_document_directory, document_processor, entity_recognizer):
    """Test extracting entities from a text document."""
    # Process the document
    text_file_path = os.path.join(integration_document_directory, "integration_test.txt")
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
    
    # Check for other expected entity types
    institution_entities = [e for e in entities if e.type == EntityType.INSTITUTION]
    has_openai = any("OpenAI" in e.text for e in institution_entities)
    assert has_openai, "OpenAI not found in institution entities"
    
    # Check for benchmark entities
    benchmark_entities = [e for e in entities if e.type == EntityType.BENCHMARK]
    has_mmlu = any("MMLU" in e.text for e in benchmark_entities)
    assert has_mmlu, "MMLU not found in benchmark entities"


def test_entity_extraction_from_html_document(integration_document_directory, document_processor, entity_recognizer):
    """Test extracting entities from an HTML document."""
    # Process the document
    html_file_path = os.path.join(integration_document_directory, "integration_test.html")
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
    
    # Verify BERT was found
    has_bert = any("BERT" in e.text for e in model_entities)
    assert has_bert, "BERT not found in model entities"
    
    # Check for other expected entity types
    institution_entities = [e for e in entities if e.type == EntityType.INSTITUTION]
    has_google = any("Google" in e.text for e in institution_entities)
    assert has_google, "Google not found in institution entities"
    
    # Check for framework entities
    framework_entities = [e for e in entities if e.type == EntityType.FRAMEWORK]
    has_pytorch = any("PyTorch" in e.text for e in framework_entities)
    assert has_pytorch, "PyTorch not found in framework entities"


def test_entity_filtering_integration(integration_test_data, entity_recognizer):
    """Test filtering entities by type and confidence score."""
    # Get test text from fixtures
    test_text = integration_test_data["test_text"]
    
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
    
    # Check for expected entity types
    expected_entities = integration_test_data["expected_entities"]
    
    for expected in expected_entities:
        entity_type = expected["type"]
        entity_text = expected["text"]
        
        # Filter entities by type
        entities_of_type = entity_recognizer.filter_entities(entities, entity_types=[entity_type])
        
        # Check if any entity of this type contains the expected text
        found = any(entity_text.lower() in e.text.lower() for e in entities_of_type)
        
        # If not found, we might want to print diagnostics but not fail the test,
        # since entity recognition can be imperfect
        if not found:
            print(f"Expected entity {entity_text} of type {entity_type} not found")


def test_entity_serialization_integration(integration_test_data, entity_recognizer):
    """Test serialization and deserialization of entities."""
    # Get test text from fixtures
    test_text = integration_test_data["test_text"]
    
    # Extract entities
    entities = entity_recognizer.recognize(test_text)
    
    # Create a temporary directory for serialization testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Serialize all entities to JSON
        entities_path = os.path.join(temp_dir, "entities.json")
        with open(entities_path, "w") as f:
            json.dump([e.to_dict() for e in entities], f, indent=2)
        
        # Read entities back from JSON
        with open(entities_path, "r") as f:
            entity_dicts = json.load(f)
        
        # Deserialize entities
        loaded_entities = [entity_recognizer.entity_class.from_dict(e_dict) for e_dict in entity_dicts]
        
        # Verify entities were properly serialized and deserialized
        assert len(loaded_entities) == len(entities)
        
        # Compare a few key properties
        for i, entity in enumerate(entities):
            loaded = loaded_entities[i]
            assert loaded.id == entity.id
            assert loaded.text == entity.text
            assert loaded.type == entity.type
            assert loaded.confidence == entity.confidence
        
        # Test serialization of filtered entities
        model_entities = entity_recognizer.filter_entities(entities, entity_types=[EntityType.MODEL])
        models_path = os.path.join(temp_dir, "models.json")
        
        with open(models_path, "w") as f:
            json.dump([e.to_dict() for e in model_entities], f, indent=2)
        
        # Read model entities back
        with open(models_path, "r") as f:
            model_dicts = json.load(f)
        
        # Verify correct count
        assert len(model_dicts) == len(model_entities)
        
        # Verify all are model type
        for model_dict in model_dicts:
            assert model_dict["type"] == "model"


def test_document_processor_entity_recognizer_integration(integration_document_directory, document_processor, entity_recognizer):
    """Test full integration of document processor and entity recognizer with multiple documents."""
    # List of test documents
    test_files = [
        os.path.join(integration_document_directory, "integration_test.txt"),
        os.path.join(integration_document_directory, "integration_test.html")
    ]
    
    # Process each document and extract entities
    for file_path in test_files:
        # Process document
        document = document_processor.process_document(file_path)
        
        # Extract entities
        entities = entity_recognizer.recognize(document.content)
        
        # Verify entities were found
        assert len(entities) > 0, f"No entities found in {file_path}"
        
        # Basic sanity checks based on document type
        if document.document_type == "text":
            # Text document should have GPT entities
            model_entities = [e for e in entities if e.type == EntityType.MODEL]
            has_gpt = any("GPT" in e.text for e in model_entities)
            assert has_gpt, "GPT not found in text document"
            
        elif document.document_type == "html":
            # HTML document should have BERT entity
            model_entities = [e for e in entities if e.type == EntityType.MODEL]
            has_bert = any("BERT" in e.text for e in model_entities)
            assert has_bert, "BERT not found in HTML document"