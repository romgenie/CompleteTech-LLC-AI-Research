# Knowledge Extraction Benchmark System - Technical Details

## Overview

The Knowledge Extraction Benchmark System provides a standardized way to measure the performance, memory usage, and scaling characteristics of the knowledge extraction components. It generates reports that include visualizations and comparisons to previous benchmark runs.

## Architecture

The benchmark system consists of:

1. **Test files** for each component (`test_*_performance.py`)
2. **Run script** (`run_benchmarks.py`) for executing benchmarks and generating reports
3. **Result storage** in JSON and HTML formats
4. **Visualization system** with charts and metrics

## Metrics Collected

### Timing Metrics

Each component has specialized test cases that measure execution time:

- **Document processing**: Time to process documents of different types and sizes
- **Entity recognition**: Entity extraction time across different text sizes and entity densities
- **Relationship extraction**: Time to identify relationships in different text and entity configurations 
- **Knowledge extractor**: End-to-end pipeline processing time

### Memory Usage

Memory profiling includes:

- **Peak memory usage**: Maximum memory consumption during processing
- **Memory growth**: How memory usage changes with input size
- **Object count**: Number of objects created during processing

### Scaling Factors

Scaling tests measure how performance changes as input size increases:

- **Scaling factor < 1.1**: Excellent scaling (constant time or logarithmic)
- **Scaling factor 1.0-1.2**: Good linear scaling (processing time increases linearly with input)
- **Scaling factor 1.2-1.5**: Acceptable scaling (slightly superlinear, like n log n)
- **Scaling factor > 1.5**: Poor scaling (quadratic or worse, needs optimization)

## Running Benchmarks

The benchmark system can be run with:

```bash
python -m tests.research_orchestrator.knowledge_extraction.benchmark.run_benchmarks
```

Options include:
- `--component` or `-c`: Specify which component to benchmark (document, entity, relationship, knowledge_graph, all)
- `--output` or `-o`: Directory for benchmark results (default: benchmark_results)
- `--verbose` or `-v`: Print detailed output during benchmarking
- `--quick` or `-q`: Run a reduced benchmark suite for faster results

## Report Format

### JSON Report Structure

```json
{
  "timestamp": "2025-03-06T14:30:00.000000",
  "quick_mode": false,
  "components": {
    "document": {
      "success": true,
      "runtime": 3.45,
      "timings": {
        "test_text_processing_performance": 0.5,
        "test_html_processing_performance": 1.2,
        "test_pdf_processing_performance": 1.75
      },
      "memory_usage": {
        "test_memory_usage": {
          "value": 45.6,
          "unit": "MB"
        }
      },
      "scaling_metrics": {
        "test_document_processing_scalability": 1.05
      }
    },
    // Additional components...
  },
  "history": {
    // Previous benchmark data...
  }
}
```

### HTML Report Features

- **Interactive tabs**: Separate views for summary, component details, history, memory, and scaling
- **Charts**: Visual representation of benchmark results using Chart.js
- **Comparison**: Historical data comparison to track performance changes
- **Scaling analysis**: Color-coded indicators for good/poor scaling
- **Error reporting**: Detailed error information for failed tests

## Implementation Details

### Parsing Test Output

The benchmark runner parses test output to extract timing information, memory usage, and scaling factors using multiple regex patterns to identify different metrics in the output.

### Historical Data Management

Previous benchmark results are stored and loaded to provide historical comparisons. The system:
- Keeps the last 10 benchmark reports by default
- Generates an index.html file to navigate between reports
- Tracks performance changes over time

### Chart Generation

Charts are generated using Chart.js with custom configuration:
- **Bar charts** for component runtime comparison
- **Line charts** for historical performance
- **Color-coded charts** for memory usage and scaling factors

### Thresholds and Analysis

The system includes built-in thresholds for analysis:
- **Timing thresholds**: Based on expected processing times for each component
- **Memory thresholds**: Based on reasonable memory usage for each component
- **Scaling thresholds**: To identify performance degradation with larger inputs

## Adding New Benchmark Tests

When adding new benchmark tests:

1. Create test functions in the appropriate performance test file
2. Use the `@pytest.mark.benchmark` decorator
3. Include timing information in the test output with the format: `test_name: X.XX seconds`
4. For memory tests, include output with the format: `test_name memory usage: X.XX MB`
5. For scaling tests, include output with the format: `test_name scaling factor: X.XX`

Example:

```python
@pytest.mark.benchmark
def test_new_component_performance():
    start = time.time()
    # Test code here...
    elapsed = time.time() - start
    print(f"test_new_component_performance: {elapsed:.4f} seconds")
    
    # Report memory usage
    mem_usage = get_memory_usage()  # Your memory measurement function
    print(f"test_new_component_performance memory usage: {mem_usage:.2f} MB")
    
    # Report scaling factor
    scaling = measure_scaling_factor()  # Your scaling measurement function
    print(f"test_new_component_performance scaling factor: {scaling:.3f}")
    
    assert elapsed < 5.0, "Performance threshold exceeded"
```