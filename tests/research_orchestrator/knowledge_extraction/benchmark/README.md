# Performance Benchmarks

This directory contains performance benchmark tests for the knowledge extraction components. These tests measure the performance of the components with various inputs and configurations.

## Overview

The benchmark tests measure:

- **Processing Speed**: How quickly components process data of different sizes
- **Memory Usage**: How much memory is consumed during processing
- **Scaling Properties**: How performance scales with input size (linear, quadratic, etc.)
- **Comparative Performance**: How different implementations compare against each other

## Running Benchmarks

### Using the Script

The easiest way to run benchmarks is using the provided script:

```bash
# Run all benchmarks
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py

# Run benchmarks for a specific component
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py -c document
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py -c entity
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py -c relationship
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py -c knowledge_graph

# Run a quick benchmark (smaller datasets)
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py -q

# Generate a report in a custom directory
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py -o benchmark_results

# Show help
python tests/research_orchestrator/knowledge_extraction/benchmark/run_benchmarks.py -h
```

### Using pytest

You can also run benchmark tests directly with pytest:

```bash
# Run all benchmark tests
python -m pytest tests/research_orchestrator/knowledge_extraction/benchmark/

# Run document processing benchmarks
python -m pytest tests/research_orchestrator/knowledge_extraction/benchmark/test_document_processing_performance.py

# Run a specific test with a certain parameter
python -m pytest "tests/research_orchestrator/knowledge_extraction/benchmark/test_document_processing_performance.py::test_text_processor_performance[10]"

# Run benchmark tests with a specific marker
python -m pytest -m "benchmark and document"
```

## Benchmark Tests

### Document Processing

The document processing benchmarks test:
- Processing documents of different sizes
- Segmenting documents with different separators
- Measuring how processing time scales with document size

### Entity Recognition

The entity recognition benchmarks test:
- Recognizing entities in documents of different sizes
- Filtering entities by type and confidence
- Merging overlapping entities
- Measuring how recognition time scales with document size
- Comparing different entity recognizer types

### Relationship Extraction

The relationship extraction benchmarks test:
- Extracting relationships from documents of different sizes
- Filtering relationships by type and confidence
- Measuring how extraction time scales with document size and entity count
- Comparing different relationship extractor types

### Knowledge Extractor

The knowledge extractor benchmarks test:
- Running the full extraction pipeline with different document sizes
- Creating knowledge graphs with different entity and relationship counts
- Extracting knowledge from multiple documents
- Measuring memory usage of knowledge graphs

## Benchmark Reports

The benchmarks generate reports in both JSON and HTML formats. The HTML reports include:
- Summary of benchmark results
- Detailed results for each component
- Charts showing performance characteristics
- Scaling factors for each component

Reports are saved to the specified output directory (default: `benchmark_results`).

## Performance Metrics

The benchmarks measure various performance metrics:
- Execution time for different operations
- Scaling characteristics with input size
- Memory usage for different data structures
- Component-specific performance indicators

## Performance Goals

The benchmark tests include assertions to verify that components meet performance goals:
- Document processing should scale approximately linearly with input size (O(n))
- Entity recognition should scale approximately linearly with input size (O(n))
- Relationship extraction should scale better than quadratic with input size (O(n^2))
- Knowledge extraction should scale reasonably with input size

## Fixture System

The benchmarks use a sophisticated fixture system to generate test data:

- `generate_text_document`: Creates documents of specified sizes with realistic AI-related content
- `generate_entities`: Creates random entities of various types (models, datasets, etc.)
- `generate_relationships`: Creates relationships between entities with realistic attributes
- `timer`: Provides timing functionality for measuring operation duration

These fixtures are designed to be composable and parametrizable, supporting tests with different input sizes and configurations.

## Implementation Notes

- All benchmarks are marked with `pytest.mark.benchmark` for easy filtering
- Component-specific markers are used to organize tests (`document`, `entity`, etc.)
- Size parameters cover small, medium, and large inputs (10KB, 100KB, 1000KB)
- The `test_document_processor_scalability` test measures and reports scaling factors
- HTML reports include interactive charts for visualizing performance characteristics