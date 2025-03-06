# Test Migration Guide

This document provides guidance on migrating tests from the old test structure to the new structure implemented in this directory.

## Old Test Structure

The old test structure had all tests in the root directory, with a mix of unittest-based tests and pytest fixture-based tests:

```
knowledge_extraction/
├── test_document_processing.py
├── test_entity_recognition.py
├── test_entity_recognition_fixtures.py
├── test_knowledge_extractor.py
├── test_knowledge_extractor_fixtures.py
├── test_relationship_extraction.py
├── test_relationship_extraction_fixtures.py
├── test_relationship_extraction_integration.py
├── test_relationship_extraction_integration_fixtures.py
```

## New Test Structure

The new test structure organizes tests by level of testing:

```
knowledge_extraction/
├── unit/                          # Unit tests
│   ├── conftest.py                # Unit test fixtures
│   ├── test_document_processing.py
│   ├── test_entity_recognition.py
│   ├── test_knowledge_extractor.py
│   └── test_relationship_extraction.py
├── integration/                   # Integration tests
│   ├── conftest.py                # Integration test fixtures
│   ├── test_entity_extraction.py
│   └── test_relationship_extraction.py
├── e2e/                           # End-to-end tests
│   ├── conftest.py                # End-to-end test fixtures
│   ├── test_pipeline.py
│   ├── test_multi_document.py
│   └── test_scenarios.py
├── property/                      # Property-based tests
│   ├── conftest.py                # Property test fixtures 
│   ├── test_document_properties.py
│   ├── test_entity_properties.py
│   ├── test_relationship_properties.py
│   └── test_knowledge_graph_properties.py
├── benchmark/                     # Performance benchmarks
│   ├── conftest.py                # Benchmark fixtures
│   ├── test_document_processing_performance.py
│   ├── test_entity_recognition_performance.py
│   ├── test_relationship_extraction_performance.py
│   ├── test_knowledge_extractor_performance.py
│   └── run_benchmarks.py          # Benchmark runner script
├── edge_cases/                    # Edge case tests
│   ├── conftest.py                # Edge case fixtures
│   ├── test_document_processing_edge_cases.py
│   ├── test_entity_recognition_edge_cases.py
│   ├── test_relationship_extraction_edge_cases.py
│   └── test_knowledge_extractor_edge_cases.py
├── data/                          # Test data
│   ├── documents/                 # Test documents
│   ├── entities/                  # Entity test data
│   ├── relationships/             # Relationship test data
│   └── graphs/                    # Knowledge graph test data
├── fixtures/                      # Legacy fixtures
│   ├── test_entity_recognition_fixtures.py
│   ├── test_knowledge_extractor_fixtures.py
│   ├── test_relationship_extraction_fixtures.py
│   └── test_relationship_extraction_integration_fixtures.py
├── old_tests/                     # Original test files (for reference)
├── conftest.py                    # Shared fixtures
├── pytest.ini                     # Test configuration
├── run_tests.sh                   # Test runner script
├── README.md                      # Documentation
└── TEST_PLAN.md                   # Test plan
```

## Migration Plan

1. **Unit Tests**:
   - The unit tests have been migrated to `unit/` directory
   - All unit tests use pytest syntax instead of unittest
   - Mocks and fixtures are defined in `unit/conftest.py`

2. **Integration Tests**:
   - Integration tests have been migrated to `integration/` directory
   - Tests focus on the integration points between components
   - Integration fixtures are defined in `integration/conftest.py`

3. **End-to-End Tests**:
   - End-to-end tests have been migrated to `e2e/` directory
   - Tests cover the full extraction pipeline
   - E2E fixtures are defined in `e2e/conftest.py`

4. **Property-Based Tests**:
   - New property-based tests have been added in the `property/` directory
   - Tests focus on invariants and properties of the system
   - Uses Hypothesis library for generating test cases
   - Property fixtures are defined in `property/conftest.py`

5. **Benchmark Tests**:
   - Performance benchmarks have been added in the `benchmark/` directory
   - Tests measure speed and scalability of components
   - Uses pytest-benchmark for consistent measurement
   - Includes a dedicated benchmark runner script
   - Benchmark fixtures are defined in `benchmark/conftest.py`

6. **Edge Case Tests**:
   - Edge case and error handling tests added in the `edge_cases/` directory
   - Tests focus on boundary conditions and error scenarios
   - Includes tests for empty inputs, malformed data, and invalid configurations
   - Edge case fixtures are defined in `edge_cases/conftest.py`

7. **Test Data**:
   - Test data has been organized in the `data/` directory
   - Sample documents, entities, relationships, and graphs are provided

8. **Legacy Fixtures**:
   - Legacy fixture files have been kept in the `fixtures/` directory for reference
   - These will be deprecated once all tests are fully migrated

9. **Original Test Files**:
   - Original test files are preserved in the `old_tests/` directory
   - These are kept for reference only and should not be used

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided script:

```bash
# Run all tests
./run_tests.sh

# Run only unit tests
./run_tests.sh -t unit

# Run only integration tests
./run_tests.sh -t integration

# Run only end-to-end tests
./run_tests.sh -t e2e

# Run only property-based tests
./run_tests.sh -t property

# Run only benchmark tests
./run_tests.sh -t benchmark

# Run only edge case tests
./run_tests.sh -t edge

# Run only entity-related tests
./run_tests.sh -m entity

# Run entity-related unit tests
./run_tests.sh -t unit -m entity

# Generate HTML report for tests
./run_tests.sh -r
```

### Using pytest Directly

You can also run tests directly with pytest:

```bash
# Run all tests
python -m pytest tests/research_orchestrator/knowledge_extraction/

# Run specific test types
python -m pytest tests/research_orchestrator/knowledge_extraction/unit/
python -m pytest tests/research_orchestrator/knowledge_extraction/integration/
python -m pytest tests/research_orchestrator/knowledge_extraction/e2e/
python -m pytest tests/research_orchestrator/knowledge_extraction/property/
python -m pytest tests/research_orchestrator/knowledge_extraction/benchmark/
python -m pytest tests/research_orchestrator/knowledge_extraction/edge_cases/

# Run a specific test file
python -m pytest tests/research_orchestrator/knowledge_extraction/unit/test_document_processing.py

# Run with specific markers
python -m pytest tests/research_orchestrator/knowledge_extraction/ -m "entity and not slow"
```

### Running Benchmarks

To run benchmarks with detailed output:

```bash
cd tests/research_orchestrator/knowledge_extraction/
python -m benchmark.run_benchmarks
```

## CI/CD Integration

The test suite has been integrated with GitHub Actions for CI/CD:

### GitHub Actions Workflows

1. **Knowledge Extraction Tests** (`.github/workflows/knowledge_extraction_tests.yml`):
   - Runs tests on push to main branch and pull requests
   - Matrix testing across Python 3.9 and 3.10
   - Separate jobs for different test types
   - Dedicated benchmark job
   - Code coverage reporting with Codecov

2. **Generate Test Status Badges** (`.github/workflows/generate_test_badges.yml`):
   - Generates status badges based on test results
   - Updates README with badge information
   - Runs automatically after Knowledge Extraction Tests workflow

3. **Dependency Review** (`.github/workflows/dependency_review.yml`):
   - Checks for security vulnerabilities in dependencies
   - Runs on pull requests to main branch
   - Fails on high severity vulnerabilities

### Test Status Badges

Status badges are shown in the README.md file and provide quick visibility into the test status for each test type and Python version.

### Viewing CI/CD Results

To view CI/CD results:
1. Go to the Actions tab in the GitHub repository
2. Select the relevant workflow run
3. View test results, artifacts, and logs

## Completed Improvements

1. ✅ Completed migration of tests from old structure
2. ✅ Added comprehensive test data for different scenarios
3. ✅ Implemented property-based testing for entity and relationship validation
4. ✅ Added end-to-end tests with realistic scenarios
5. ✅ Created performance benchmarks for all components
6. ✅ Implemented edge case testing for all components
7. ✅ Added CI/CD integration with GitHub Actions

## Future Enhancements

1. Add flaky test detection and retries
2. Implement test result trending over time
3. Create dashboard for monitoring test health
4. Set up weekly scheduled runs for stability testing
5. Implement mutation testing for improved test quality assessment

## Questions?

If you have questions about the test migration, contact the Research Orchestrator team.