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
├── conftest.py                    # Shared fixtures
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

4. **Test Data**:
   - Test data has been organized in the `data/` directory
   - Sample documents, entities, relationships, and graphs are provided

5. **Legacy Fixtures**:
   - Legacy fixture files have been kept in the `fixtures/` directory for reference
   - These will be deprecated once all tests are fully migrated

## Running Tests

To run all tests:

```bash
pytest tests/research_orchestrator/knowledge_extraction/
```

To run a specific level of tests:

```bash
pytest tests/research_orchestrator/knowledge_extraction/unit/
pytest tests/research_orchestrator/knowledge_extraction/integration/
pytest tests/research_orchestrator/knowledge_extraction/e2e/
```

To run a specific test file:

```bash
pytest tests/research_orchestrator/knowledge_extraction/unit/test_document_processing.py
```

## Future Improvements

1. Complete migration of remaining tests from old structure
2. Add more comprehensive test data for different scenarios
3. Add property-based testing for entity and relationship validation
4. Implement additional e2e tests with real-world documents
5. Add performance tests for the full pipeline

## Questions?

If you have questions about the test migration, contact the test infrastructure team.