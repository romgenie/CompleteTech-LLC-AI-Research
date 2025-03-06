"""
Benchmark tests for relationship extraction performance.

This module contains tests that measure the performance of the relationship
extraction components with different document sizes and entity counts.
"""

import pytest
import time
import numpy as np

# Mark all tests in this module as benchmark tests and relationship related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.relationship,
    pytest.mark.slow
]

from research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import RelationType
from research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
from research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory


@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_relationship_extraction_performance(size_kb, generate_text_document, timer):
    """Test the performance of relationship extraction with different document sizes."""
    # Generate a document of the specified size
    document = generate_text_document(size_kb)
    content = document.content
    
    # First, recognize entities
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    entities = entity_recognizer.recognize(content)
    
    # Ensure we have some entities
    if len(entities) < 2:
        pytest.skip("Not enough entities found for relationship extraction")
    
    # Create a relationship extractor
    extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    # Measure extraction time
    with timer(f"RelationshipExtractor.extract_relationships({size_kb}KB, {len(entities)} entities)"):
        relationships = extractor.extract_relationships(content, entities)
    
    # Print extraction statistics
    print(f"\nExtracted {len(relationships)} relationships from {len(entities)} entities in a {size_kb}KB document")
    
    # Measure filtering time if we have relationships
    if relationships:
        with timer(f"RelationshipExtractor.filter_relationships({len(relationships)} relationships)"):
            filtered_relationships = extractor.filter_relationships(relationships, min_confidence=0.7)
        
        # Check filtering
        assert len(filtered_relationships) <= len(relationships)


@pytest.mark.parametrize('entity_count', [10, 50, 100])
def test_relationship_extraction_with_entity_count(entity_count, generate_text_document, generate_entities, timer):
    """Test how relationship extraction performance scales with entity count."""
    # Generate a document
    document = generate_text_document(100)  # 100KB
    content = document.content
    
    # Generate entities
    entities = generate_entities(entity_count)
    
    # Create a relationship extractor
    extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    # Measure extraction time
    with timer(f"RelationshipExtractor.extract_relationships(100KB, {entity_count} entities)"):
        relationships = extractor.extract_relationships(content, entities)
    
    # Print extraction statistics
    print(f"\nExtracted {len(relationships)} relationships from {entity_count} entities")
    
    # Check how many potential relationships were found
    potential_relationships = entity_count * (entity_count - 1)  # Maximum possible directed relationships
    extraction_ratio = len(relationships) / potential_relationships if potential_relationships > 0 else 0
    print(f"Extraction ratio: {extraction_ratio:.2%} ({len(relationships)} / {potential_relationships})")


@pytest.mark.parametrize('relationship_count', [10, 100, 1000])
def test_relationship_filtering_performance(relationship_count, generate_entities, generate_relationships, timer):
    """Test the performance of relationship filtering with different relationship counts."""
    # Generate a sufficient number of entities
    entity_count = max(50, relationship_count // 10)
    entities = generate_entities(entity_count)
    
    # Generate relationships
    relationships = generate_relationships(entities, relationship_count)
    
    # Create a relationship extractor
    extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    # Measure filtering by confidence
    with timer(f"filter_relationships_by_confidence({relationship_count} relationships)"):
        filtered_by_confidence = extractor.filter_relationships(relationships, min_confidence=0.7)
    
    # Measure filtering by type
    with timer(f"filter_relationships_by_type({relationship_count} relationships)"):
        filtered_by_type = extractor.filter_relationships(
            relationships,
            relation_types=[RelationType.TRAINED_ON, RelationType.EVALUATED_ON]
        )
    
    # Measure filtering by both
    with timer(f"filter_relationships_by_both({relationship_count} relationships)"):
        filtered_by_both = extractor.filter_relationships(
            relationships,
            min_confidence=0.7,
            relation_types=[RelationType.TRAINED_ON, RelationType.EVALUATED_ON]
        )


@pytest.mark.parametrize('extractor_type', ['pattern', 'ai', 'combined'])
def test_extractor_type_performance(extractor_type, generate_text_document, timer):
    """Test the performance of different relationship extractor types."""
    # Generate a document
    document = generate_text_document(100)  # 100KB
    content = document.content
    
    # First, recognize entities
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    entities = entity_recognizer.recognize(content)
    
    # Ensure we have some entities
    if len(entities) < 2:
        pytest.skip("Not enough entities found for relationship extraction")
    
    # Create config for combined extractor
    config = None
    if extractor_type == "combined":
        config = {
            "extractors": [
                {"type": "pattern"},
                {"type": "ai"}
            ]
        }
    
    # Create a relationship extractor
    extractor = RelationshipExtractorFactory.create_extractor(extractor_type, config)
    
    # Measure extraction time
    with timer(f"{extractor_type.capitalize()}RelationshipExtractor.extract_relationships(100KB, {len(entities)} entities)"):
        relationships = extractor.extract_relationships(content, entities)
    
    # Print extraction statistics
    print(f"\nExtracted {len(relationships)} relationships using {extractor_type} extractor")
    
    # Verify combined extractor finds more relationships when possible
    if extractor_type == "combined" and relationships:
        # Test individual extractors
        pattern_extractor = RelationshipExtractorFactory.create_extractor("pattern")
        ai_extractor = RelationshipExtractorFactory.create_extractor("ai")
        
        pattern_relationships = pattern_extractor.extract_relationships(content, entities)
        ai_relationships = ai_extractor.extract_relationships(content, entities)
        
        print(f"Pattern extractor: {len(pattern_relationships)} relationships")
        print(f"AI extractor: {len(ai_relationships)} relationships")
        print(f"Combined extractor: {len(relationships)} relationships")
        
        # Combined should find at least as many as the best individual
        assert len(relationships) >= max(len(pattern_relationships), len(ai_relationships)), \
            "Combined extractor should find at least as many relationships as the best individual extractor"


def test_relationship_extraction_scalability():
    """Test how relationship extraction time scales with document size and entity count."""
    sizes = [10, 50, 100, 500]  # KB
    times = []
    relationship_counts = []
    entity_counts = []
    
    # Create recognizer and extractor
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    relationship_extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    for size_kb in sizes:
        # Generate a document
        document = generate_text_document(size_kb)
        content = document.content
        
        # Extract entities
        entities = entity_recognizer.recognize(content)
        entity_counts.append(len(entities))
        
        # Skip if not enough entities
        if len(entities) < 2:
            times.append(0)
            relationship_counts.append(0)
            continue
        
        # Measure relationship extraction time
        start_time = time.time()
        relationships = relationship_extractor.extract_relationships(content, entities)
        end_time = time.time()
        
        times.append(end_time - start_time)
        relationship_counts.append(len(relationships))
    
    # Output results
    print("\nRelationship Extraction Scalability:")
    print("---------------------------------")
    print(f"{'Size (KB)':<10} {'Time (s)':<10} {'Entities':<10} {'Relationships':<15}")
    print("---------------------------------")
    for i, size_kb in enumerate(sizes):
        print(f"{size_kb:<10} {times[i]:<10.4f} {entity_counts[i]:<10} {relationship_counts[i]:<15}")
    
    # Skip scaling factor calculation if we have zeros
    if 0 in times or len([t for t in times if t > 0]) < 2:
        print("\nNot enough data points for scaling factor calculation")
        return
    
    # Calculate scaling factor using linear regression
    valid_indices = [i for i, t in enumerate(times) if t > 0]
    valid_sizes = [sizes[i] for i in valid_indices]
    valid_times = [times[i] for i in valid_indices]
    
    log_sizes = np.log(valid_sizes)
    log_times = np.log(valid_times)
    slope, intercept = np.polyfit(log_sizes, log_times, 1)
    
    print(f"\nScaling factor: O(n^{slope:.2f})")
    
    # Relationship extraction can be quadratic in worst case, but should be sub-quadratic in practice
    assert slope < 2.5, f"Relationship extraction scales very poorly: O(n^{slope:.2f})"