# Test Suite for Paper Processing Pipeline

## Overview

This directory contains tests for the Paper Processing Pipeline, including unit tests, integration tests, and end-to-end tests. These tests validate the functionality of the pipeline and ensure it meets the requirements.

## Structure

The test suite is organized as follows:

```
tests/
├── conftest.py                # Test configuration and fixtures
├── unit/                      # Unit tests
│   ├── models/                # Tests for data models
│   ├── db/                    # Tests for database models
│   ├── tasks/                 # Tests for Celery tasks
│   ├── api/                   # Tests for API endpoints
│   ├── integrations/          # Tests for integration adapters
│   ├── websocket/             # Tests for WebSocket integration
│   └── config/                # Tests for configuration
├── integration/               # Integration tests
│   ├── db/                    # Database integration tests
│   ├── api/                   # API integration tests
│   ├── tasks/                 # Task integration tests
│   └── integrations/          # External system integration tests
└── e2e/                       # End-to-end tests
```

## Test Types

### Unit Tests

Unit tests validate individual components in isolation, using mocks for dependencies. They ensure that each component functions as expected on its own.

Key unit test areas:
- **Models**: Test data models and state machine
- **Database**: Test database models and connection management
- **Tasks**: Test Celery task logic
- **API**: Test API endpoint handlers
- **Integrations**: Test integration adapters
- **WebSocket**: Test WebSocket event handling
- **Config**: Test configuration loading and validation

### Integration Tests

Integration tests validate interactions between components, using real dependencies when possible. They ensure that components work together correctly.

Key integration test areas:
- **Database Integration**: Test database operations with a real MongoDB instance
- **API Integration**: Test API endpoints with real request processing
- **Task Integration**: Test Celery tasks with real execution
- **External System Integration**: Test integration with external systems

### End-to-End Tests

End-to-end tests validate the entire pipeline from paper upload to implementation generation. They ensure that the system functions correctly as a whole.

## Running Tests

### Prerequisites

- Python 3.9+
- MongoDB (for integration tests)
- Redis (for integration tests)

### Environment Setup

```bash
# Set test environment
export PAPER_PROCESSING_ENVIRONMENT=testing

# Configure test database
export PAPER_PROCESSING_DATABASE__MONGODB_URI=mongodb://localhost:27017
export PAPER_PROCESSING_DATABASE__DATABASE_NAME=test_paper_processing

# Configure test Celery broker
export PAPER_PROCESSING_CELERY__BROKER_URL=memory://
export PAPER_PROCESSING_CELERY__RESULT_BACKEND=memory://
```

### Running All Tests

```bash
pytest
```

### Running Unit Tests

```bash
pytest tests/unit/
```

### Running Specific Tests

```bash
# Run model tests
pytest tests/unit/models/

# Run database tests
pytest tests/unit/db/

# Run a specific test file
pytest tests/unit/models/test_paper.py

# Run a specific test
pytest tests/unit/models/test_paper.py::test_paper_create
```

### Running with Coverage

```bash
pytest --cov=paper_processing
```

## Test Fixtures

The test suite provides several fixtures to simplify test setup:

- **test_settings**: Settings configured for testing
- **sample_paper**: A sample paper instance
- **mock_db_connection**: Mock database connection
- **mock_paper_model**: Mock paper model
- **mock_task_runner**: Mock task runner
- **mock_knowledge_graph_adapter**: Mock knowledge graph adapter
- **mock_research_implementation_adapter**: Mock research implementation adapter
- **mock_research_orchestrator_adapter**: Mock research orchestrator adapter
- **mock_extraction_adapter**: Mock extraction adapter

These fixtures are defined in `conftest.py` and can be used in tests by including them as parameters.

## Test Guidelines

- **Isolation**: Each test should be independent and not rely on other tests
- **Mocking**: Use mocks for external dependencies
- **Coverage**: Aim for >80% test coverage
- **Documentation**: Document the purpose of each test
- **Assertion**: Use meaningful assertions that clearly indicate what is being tested

## Future Work

- Implement integration tests with real database
- Implement end-to-end tests
- Add performance tests
- Add load tests