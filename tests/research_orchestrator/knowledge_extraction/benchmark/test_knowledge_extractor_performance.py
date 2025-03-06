"""
Benchmark tests for knowledge extractor performance.

This module contains tests that measure the performance of the knowledge
extractor components with different document sizes and entity/relationship counts.
"""

import pytest
import time
import os
import json
import numpy as np

# Mark all tests in this module as benchmark tests and knowledge graph related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.knowledge_graph,
    pytest.mark.slow
]

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor


@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_full_extraction_pipeline_performance(size_kb, generate_text_document, benchmark_knowledge_extractor, timer, benchmark_temp_directory):
    """Test the performance of the full extraction pipeline with different document sizes."""
    # Generate a document of the specified size
    document = generate_text_document(size_kb)
    
    # Need to save the document to a file for testing
    temp_file_path = os.path.join(benchmark_temp_directory, f"test_{size_kb}kb.txt")
    with open(temp_file_path, 'w') as f:
        f.write(document.content)
    
    # Measure extraction time
    with timer(f"KnowledgeExtractor.extract_from_document({size_kb}KB)"):
        result = benchmark_knowledge_extractor.extract_from_document(temp_file_path)
    
    # Print extraction statistics
    print(f"\nExtracted {result['entity_count']} entities and {result['relationship_count']} relationships from a {size_kb}KB document")
    
    # Measure knowledge graph creation time
    doc_id = temp_file_path
    entities = benchmark_knowledge_extractor.entities[doc_id]
    relationships = benchmark_knowledge_extractor.relationships[doc_id]
    
    with timer(f"KnowledgeExtractor._create_knowledge_graph({len(entities)} entities, {len(relationships)} relationships)"):
        knowledge_graph = benchmark_knowledge_extractor._create_knowledge_graph(entities, relationships, doc_id)
    
    # Measure save results time
    with timer(f"KnowledgeExtractor.save_extraction_results({size_kb}KB)"):
        output_dir = benchmark_knowledge_extractor.save_extraction_results(benchmark_temp_directory, doc_id)
    
    # Measure get statistics time
    with timer(f"KnowledgeExtractor.get_extraction_statistics()"):
        stats = benchmark_knowledge_extractor.get_extraction_statistics()
    
    # Print output dir for manual inspection
    print(f"\nResults saved to: {output_dir}")


@pytest.mark.parametrize('entity_count,relationship_count', [(10, 20), (100, 200), (1000, 2000)])
def test_knowledge_graph_creation_performance(entity_count, relationship_count, generate_entities, generate_relationships, benchmark_knowledge_extractor, timer):
    """Test the performance of knowledge graph creation with different entity and relationship counts."""
    # Generate entities and relationships
    entities = generate_entities(entity_count)
    relationships = generate_relationships(entities, relationship_count)
    
    # Measure knowledge graph creation time
    with timer(f"KnowledgeExtractor._create_knowledge_graph({entity_count} entities, {relationship_count} relationships)"):
        knowledge_graph = benchmark_knowledge_extractor._create_knowledge_graph(entities, relationships, "test_doc")
    
    # Check knowledge graph structure
    assert len(knowledge_graph["nodes"]) == entity_count
    assert len(knowledge_graph["edges"]) == relationship_count


@pytest.mark.parametrize('doc_count', [1, 5, 10])
def test_multi_document_extraction_performance(doc_count, generate_text_document, benchmark_knowledge_extractor, timer, benchmark_temp_directory):
    """Test the performance of extracting knowledge from multiple documents."""
    # Generate multiple documents
    doc_paths = []
    for i in range(doc_count):
        # Generate a document (100KB each)
        document = generate_text_document(100)
        
        # Save the document to a file
        temp_file_path = os.path.join(benchmark_temp_directory, f"doc_{i}.txt")
        with open(temp_file_path, 'w') as f:
            f.write(document.content)
        
        doc_paths.append(temp_file_path)
    
    # Process each document
    total_entities = 0
    total_relationships = 0
    
    with timer(f"Extract from {doc_count} documents"):
        for doc_path in doc_paths:
            result = benchmark_knowledge_extractor.extract_from_document(doc_path)
            total_entities += result["entity_count"]
            total_relationships += result["relationship_count"]
    
    # Print extraction statistics
    print(f"\nExtracted {total_entities} entities and {total_relationships} relationships from {doc_count} documents")
    
    # Measure statistics generation time
    with timer(f"Get statistics for {doc_count} documents"):
        stats = benchmark_knowledge_extractor.get_extraction_statistics()
    
    # Verify statistics
    assert stats["documents"]["count"] == doc_count
    assert stats["entities"]["count"] == total_entities
    assert stats["relationships"]["count"] == total_relationships


def test_knowledge_extraction_scalability():
    """Test how knowledge extraction time scales with document size."""
    sizes = [10, 50, 100, 500]  # KB
    times = []
    entity_counts = []
    relationship_counts = []
    
    # Create knowledge extractor
    from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
    from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
    from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
    
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    relationship_extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    extractor = KnowledgeExtractor(
        document_processor=document_processor,
        entity_recognizer=entity_recognizer,
        relationship_extractor=relationship_extractor
    )
    
    # Create temporary directory
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    try:
        for size_kb in sizes:
            # Generate a document
            document = generate_text_document(size_kb)
            
            # Save the document to a file
            temp_file_path = os.path.join(temp_dir, f"doc_{size_kb}kb.txt")
            with open(temp_file_path, 'w') as f:
                f.write(document.content)
            
            # Measure extraction time
            start_time = time.time()
            result = extractor.extract_from_document(temp_file_path)
            end_time = time.time()
            
            times.append(end_time - start_time)
            entity_counts.append(result["entity_count"])
            relationship_counts.append(result["relationship_count"])
        
        # Output results
        print("\nKnowledge Extraction Scalability:")
        print("---------------------------------")
        print(f"{'Size (KB)':<10} {'Time (s)':<10} {'Entities':<10} {'Relationships':<15}")
        print("---------------------------------")
        for i, size_kb in enumerate(sizes):
            print(f"{size_kb:<10} {times[i]:<10.4f} {entity_counts[i]:<10} {relationship_counts[i]:<15}")
        
        # Calculate scaling factor using linear regression
        log_sizes = np.log(sizes)
        log_times = np.log(times)
        slope, intercept = np.polyfit(log_sizes, log_times, 1)
        
        print(f"\nScaling factor: O(n^{slope:.2f})")
        
        # Knowledge extraction can be super-linear due to relationship extraction, but should be reasonable
        assert slope < 2.0, f"Knowledge extraction scales poorly: O(n^{slope:.2f})"
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


def test_knowledge_graph_memory_usage():
    """Test the memory usage of knowledge graphs with different entity and relationship counts."""
    import sys
    import json
    
    # Test configurations
    configurations = [
        (10, 20),      # Small
        (100, 200),    # Medium
        (1000, 2000),  # Large
    ]
    
    # Create knowledge extractor
    from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
    from src.research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
    from src.research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory
    
    document_processor = DocumentProcessor()
    entity_recognizer = EntityRecognizerFactory.create_recognizer("ai")
    relationship_extractor = RelationshipExtractorFactory.create_extractor("pattern")
    
    extractor = KnowledgeExtractor(
        document_processor=document_processor,
        entity_recognizer=entity_recognizer,
        relationship_extractor=relationship_extractor
    )
    
    print("\nKnowledge Graph Memory Usage:")
    print("---------------------------------")
    print(f"{'Entities':<10} {'Relationships':<15} {'Memory (KB)':<15} {'JSON Size (KB)':<15}")
    print("---------------------------------")
    
    for entity_count, relationship_count in configurations:
        # Generate entities and relationships
        entities = generate_entities(entity_count)
        relationships = generate_relationships(entities, relationship_count)
        
        # Create knowledge graph
        knowledge_graph = extractor._create_knowledge_graph(entities, relationships, "test_doc")
        
        # Measure memory usage
        memory_size = sys.getsizeof(knowledge_graph) / 1024  # KB
        
        # Measure JSON size
        json_size = len(json.dumps(knowledge_graph).encode('utf-8')) / 1024  # KB
        
        print(f"{entity_count:<10} {relationship_count:<15} {memory_size:<15.2f} {json_size:<15.2f}")
        
        # Check memory usage is reasonable
        # These are very rough estimates and may need adjustment
        expected_memory = (entity_count * 0.5) + (relationship_count * 1.0)  # KB
        assert memory_size < expected_memory * 10, f"Memory usage is excessive: {memory_size}KB > {expected_memory * 10}KB"