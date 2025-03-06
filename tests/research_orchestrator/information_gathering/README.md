# Information Gathering Test Suite

This directory contains comprehensive tests for the Information Gathering module of the Research Orchestrator. The tests are organized into several categories to ensure thorough testing of all components.

## Test Structure

The test suite is organized into the following directories:

- **unit/**: Unit tests for individual components in isolation
- **integration/**: Tests for how components work together
- **e2e/**: End-to-end tests for the complete information gathering pipeline
- **property/**: Property-based tests using hypothesis to test system invariants
- **edge_cases/**: Tests for boundary conditions and error handling
- **benchmark/**: Performance tests for various components

## Components Tested

The Information Gathering module consists of several key components:

1. **SearchManager**: Coordinates search operations across multiple sources
2. **SourceManager**: Handles different information sources
3. **QualityAssessor**: Evaluates search result quality
4. **Various Sources**: 
   - AcademicSource (scholarly papers from ArXiv, PubMed, etc.)
   - WebSource (web search through various APIs)
   - CodeSource (code repositories)
   - AISource (LLM-generated information)

## Running Tests

### Running All Tests

To run all tests, use the provided script:

```bash
./run_tests.sh
```

### Running Specific Test Types

To run specific test types, use the `-t` option:

```bash
./run_tests.sh -t unit        # Run only unit tests
./run_tests.sh -t integration # Run only integration tests
./run_tests.sh -t property    # Run only property-based tests
./run_tests.sh -t edge        # Run only edge case tests
./run_tests.sh -t benchmark   # Run only benchmark tests
./run_tests.sh -t e2e         # Run only end-to-end tests
```

### Running Tests by Component

To run tests for a specific component, use the `-m` option:

```bash
./run_tests.sh -m search    # Run tests related to the SearchManager
./run_tests.sh -m source    # Run tests related to the SourceManager
./run_tests.sh -m quality   # Run tests related to the QualityAssessor
```

### Generating Test Reports

To generate an HTML test report, use the `-r` option:

```bash
./run_tests.sh -r
```

## Benchmark Tests

Benchmark tests are designed to measure the performance of various components under different conditions. They are located in the `benchmark/` directory.

### Running Benchmarks

To run all benchmarks, use:

```bash
cd benchmark
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

## GitHub Actions Integration

The test suite is integrated with GitHub Actions for continuous integration. The workflow runs all tests automatically when changes are pushed to the Information Gathering module.

See `.github/workflows/information_gathering_tests.yml` for the workflow configuration.

## Adding New Tests

When adding new tests, please follow these guidelines:

1. Place the test in the appropriate directory based on its type
2. Use the appropriate pytest markers to categorize the test
3. Follow the existing naming convention for test files and functions
4. Add appropriate documentation for the test

## Test Dependencies

The tests require the following dependencies:

- pytest
- pytest-cov (for code coverage)
- pytest-html (for HTML reports)
- hypothesis (for property-based testing)
- numpy (for benchmark analysis)
- psutil (for memory usage tests)

These dependencies are automatically installed by the GitHub Actions workflow.