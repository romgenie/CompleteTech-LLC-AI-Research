# Performance Benchmarks

This directory contains performance benchmark tests for the knowledge extraction components. These tests measure the performance of the components with various inputs and configurations.

## Running Benchmarks

### Using the Script

The easiest way to run benchmarks is using the provided script:

```bash
# Run all benchmarks
./benchmark/run_benchmarks.py

# Run benchmarks for a specific component
./benchmark/run_benchmarks.py -c document
./benchmark/run_benchmarks.py -c entity
./benchmark/run_benchmarks.py -c relationship
./benchmark/run_benchmarks.py -c knowledge_graph

# Run a quick benchmark (smaller datasets)
./benchmark/run_benchmarks.py -q

# Generate a report in a custom directory
./benchmark/run_benchmarks.py -o benchmark_results

# Show help
./benchmark/run_benchmarks.py -h
```

### Using pytest

You can also run benchmark tests directly with pytest:

```bash
# Run all benchmark tests
python -m pytest benchmark/

# Run document processing benchmarks
python -m pytest benchmark/test_document_processing_performance.py

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

Reports are saved to the specified output directory (default: `benchmark_results`).

## Performance Metrics

The benchmarks measure various performance metrics:
- Execution time for different operations
- Scaling characteristics with input size
- Memory usage for different data structures

## Performance Goals

The benchmark tests include assertions to verify that components meet performance goals:
- Document processing should scale approximately linearly with input size (O(n))
- Entity recognition should scale approximately linearly with input size (O(n))
- Relationship extraction should scale better than quadratic with input size (O(n^2))
- Knowledge extraction should scale reasonably with input size