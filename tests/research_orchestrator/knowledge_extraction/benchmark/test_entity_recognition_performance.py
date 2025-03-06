"""
Benchmark tests for entity recognition performance.

This module contains tests that measure the performance of the entity
recognition components with documents of various sizes and entity counts.
"""

import pytest
import time
import numpy as np

# Mark all tests in this module as benchmark tests and entity related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.entity,
    pytest.mark.slow
]

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory


@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_entity_recognition_performance(size_kb, generate_text_document, timer):
    """Test the performance of entity recognition with different document sizes."""
    # Generate a document of the specified size
    document = generate_text_document(size_kb)
    content = document.content
    
    # Create an entity recognizer
    recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Measure recognition time
    with timer(f"EntityRecognizer.recognize({size_kb}KB)"):
        entities = recognizer.recognize(content)
    
    # Check that entities were found
    assert len(entities) > 0
    
    # Measure filtering time
    with timer(f"EntityRecognizer.filter_entities({len(entities)} entities)"):
        filtered_entities = recognizer.filter_entities(entities, min_confidence=0.7)
    
    # Check filtering
    assert len(filtered_entities) <= len(entities)
    
    # Measure entity type filtering time
    with timer(f"EntityRecognizer.filter_entities_by_type({len(entities)} entities)"):
        model_entities = recognizer.filter_entities(entities, entity_types=[EntityType.MODEL])
    
    # Check type filtering
    assert all(e.type == EntityType.MODEL for e in model_entities)


@pytest.mark.parametrize('entity_count', [10, 100, 1000])
def test_entity_filtering_performance(entity_count, generate_entities, timer):
    """Test the performance of entity filtering with different entity counts."""
    # Generate entities
    entities = generate_entities(entity_count)
    
    # Create an entity recognizer
    recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Measure filtering by confidence
    with timer(f"filter_entities_by_confidence({entity_count} entities)"):
        filtered_by_confidence = recognizer.filter_entities(entities, min_confidence=0.7)
    
    # Measure filtering by type
    with timer(f"filter_entities_by_type({entity_count} entities)"):
        filtered_by_type = recognizer.filter_entities(entities, entity_types=[EntityType.MODEL, EntityType.DATASET])
    
    # Measure filtering by both
    with timer(f"filter_entities_by_both({entity_count} entities)"):
        filtered_by_both = recognizer.filter_entities(
            entities,
            min_confidence=0.7,
            entity_types=[EntityType.MODEL, EntityType.DATASET]
        )


@pytest.mark.parametrize('entity_count', [10, 100, 1000])
def test_entity_overlap_merging_performance(entity_count, generate_entities, timer):
    """Test the performance of entity overlap merging with different entity counts."""
    # Generate entities
    entities = generate_entities(entity_count)
    
    # Create overlapping entities by modifying 50% of them
    for i in range(entity_count // 2):
        # Modify start and end positions to create overlaps
        entities[i].start_pos = 100 + i
        entities[i].end_pos = 150 + i
    
    # Create an entity recognizer
    recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Measure overlap merging
    with timer(f"merge_overlapping_entities({entity_count} entities)"):
        merged_entities = recognizer.merge_overlapping_entities(entities)
    
    # Check that merging worked
    assert len(merged_entities) < entity_count


def test_entity_recognition_scalability():
    """Test how entity recognition time scales with document size."""
    sizes = [10, 50, 100, 500, 1000]  # KB
    times = []
    entity_counts = []
    
    recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    for size_kb in sizes:
        # Generate a document
        document = generate_text_document(size_kb)
        content = document.content
        
        # Measure recognition time
        start_time = time.time()
        entities = recognizer.recognize(content)
        end_time = time.time()
        
        times.append(end_time - start_time)
        entity_counts.append(len(entities))
    
    # Output results
    print("\nEntity Recognition Scalability:")
    print("-------------------------------")
    print(f"{'Size (KB)':<10} {'Time (s)':<10} {'Entities':<10}")
    print("-------------------------------")
    for i, size_kb in enumerate(sizes):
        print(f"{size_kb:<10} {times[i]:<10.4f} {entity_counts[i]:<10}")
    
    # Calculate scaling factor using linear regression
    log_sizes = np.log(sizes)
    log_times = np.log(times)
    slope, intercept = np.polyfit(log_sizes, log_times, 1)
    
    print(f"\nScaling factor: O(n^{slope:.2f})")
    
    # Entity recognition should ideally be linear or better
    assert slope < 1.5, f"Entity recognition scales poorly: O(n^{slope:.2f})"


@pytest.mark.parametrize('recognizer_type', ['ai', 'scientific', 'combined'])
def test_recognizer_type_performance(recognizer_type, generate_text_document, timer):
    """Test the performance of different entity recognizer types."""
    # Generate a document
    document = generate_text_document(100)  # 100KB
    content = document.content
    
    # Create config for combined recognizer
    config = None
    if recognizer_type == "combined":
        config = {
            "recognizers": [
                {"type": "ai"},
                {"type": "scientific"}
            ]
        }
    
    # Create an entity recognizer
    recognizer = EntityRecognizerFactory.create_recognizer(recognizer_type, config)
    
    # Measure recognition time
    with timer(f"{recognizer_type.capitalize()}EntityRecognizer.recognize(100KB)"):
        entities = recognizer.recognize(content)
    
    # Check that entities were found
    assert len(entities) > 0
    
    # Print entity type distribution
    type_counts = {}
    for entity in entities:
        type_counts[entity.type] = type_counts.get(entity.type, 0) + 1
    
    print(f"\nEntity type distribution for {recognizer_type} recognizer:")
    for entity_type, count in type_counts.items():
        print(f"  {entity_type}: {count}")
    
    # Verify combined recognizer finds more entity types
    if recognizer_type == "combined":
        assert len(type_counts) >= 2, "Combined recognizer should find more entity types"