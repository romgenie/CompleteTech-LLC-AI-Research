# Information Gathering Benchmark Tests

This directory contains performance benchmark tests for the Information Gathering module of the Research Orchestrator. The benchmarks are designed to measure the performance of various components under different conditions and ensure that the system maintains good performance as development continues.

## Available Benchmarks

The benchmarks are organized by component:

1. **SearchManager Benchmarks** (`test_search_manager_performance.py`):
   - Query length performance tests
   - Multi-source search scaling tests
   - Result volume performance tests
   - Scalability tests
   - Memory usage tests

2. **SourceManager Benchmarks** (`test_source_manager_performance.py`):
   - Source registration performance tests
   - Parallel search performance tests
   - Result volume performance tests
   - Error resilience performance tests
   - Scalability tests for sequential and parallel execution
   - Memory usage tests

3. **QualityAssessor Benchmarks** (`test_quality_assessor_performance.py`):
   - Result assessment performance tests
   - Quality filtering performance tests
   - Scoring metrics performance tests
   - Content length performance tests
   - Batch processing performance tests
   - Scalability tests
   - Memory usage tests

## Running Benchmarks

### Running All Benchmarks

To run all benchmarks, use:

```bash
./run_benchmarks.py
```

### Running Specific Benchmarks

To run benchmarks for specific components:

```bash
./run_benchmarks.py -c search   # Run only SearchManager benchmarks
./run_benchmarks.py -c source   # Run only SourceManager benchmarks
./run_benchmarks.py -c quality  # Run only QualityAssessor benchmarks
```

### Quick Benchmarks

To run a quick version of the benchmarks (skipping memory usage and scalability tests):

```bash
./run_benchmarks.py -q
```

### Verbose Output

For more detailed output:

```bash
./run_benchmarks.py -v
```

### Custom Output Directory

To specify a custom output directory for benchmark results:

```bash
./run_benchmarks.py -o path/to/output
```

## Benchmark Output

The benchmark runner generates both JSON and HTML reports in the output directory:

- JSON report: Contains raw benchmark data including timing information and success status
- HTML report: Provides a visual representation of the benchmark results, including charts

## Adding New Benchmarks

When adding new benchmarks, please follow these guidelines:

1. Create a new file named `test_<component>_performance.py` for a new component
2. Use the appropriate pytest markers: `benchmark` and a component-specific marker
3. Include timing tests for various scenarios
4. Include scalability tests to ensure O(n) or better performance
5. Include memory usage tests where appropriate
6. Document the benchmarks with clear docstrings
7. Update the `run_benchmarks.py` script to include your new component

## Test Dependencies

These benchmarks require the following dependencies:

- pytest
- numpy (for data analysis)
- psutil (for memory usage tests)
- matplotlib (for chart generation)

These dependencies are automatically installed by the GitHub Actions workflow.