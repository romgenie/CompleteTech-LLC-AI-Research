# Testing Guidelines

This document provides comprehensive instructions for testing across the project, with specific details for the Paper Processing Pipeline and other components.

## General Testing Approach

Our testing strategy employs:

1. **Unit Tests**: Testing individual components in isolation with mocks
2. **Integration Tests**: Testing interactions between components
3. **End-to-End Tests**: Testing complete workflows

We use pytest for all testing with these key features:
- Fixtures for test setup and data preparation
- Parameterized tests for comprehensive test coverage
- CI/CD integration via GitHub Actions

## Paper Processing Pipeline Testing

The Paper Processing Pipeline is designed to extract knowledge from academic papers and integrate it into our knowledge graph system. The implementation includes:

- Document processing with PDF, HTML, and text support
- Entity recognition and relationship extraction
- Knowledge Graph integration with Temporal Evolution support
- Real-time updates via WebSocket connections

## Prerequisites

To test the Paper Processing Pipeline, ensure you have the following:

1. Running MongoDB instance
2. Running Neo4j instance
3. Running Redis server (for Celery)
4. Python requirements installed:
   ```
   pip install -r requirements.txt
   ```

## Running the API Services

1. Start the backend services:
   ```bash
   docker-compose up -d
   ```

2. Start the Celery worker:
   ```bash
   cd src/paper_processing
   celery -A paper_processing.tasks.celery_app worker --loglevel=INFO
   ```

3. Start the FastAPI application:
   ```bash
   cd src/paper_processing
   uvicorn api.main:app --reload --port 8000
   ```

## Testing the API

### Basic Testing

You can perform basic API testing using the provided shell script:

```bash
./test_paper_api.sh
```

This script tests the basic endpoints and WebSocket availability.

### Full Testing

For complete testing of the paper processing pipeline, use the Python test script:

```bash
python test_api.py --paper-file path/to/paper.pdf --api-url http://localhost:8000
```

Replace `path/to/paper.pdf` with a path to a valid PDF file.

### API Endpoints

The main endpoints for testing are:

- `POST /papers`: Upload a paper
- `POST /papers/{paper_id}/process`: Start processing a paper
- `GET /papers/{paper_id}/status`: Get paper processing status
- `GET /papers/{paper_id}/progress`: Get detailed progress information
- `GET /papers/stats`: Get overall statistics

### WebSocket Endpoints

Real-time updates are available via WebSocket:

- `ws://localhost:8000/ws`: Global updates
- `ws://localhost:8000/ws/{paper_id}`: Paper-specific updates

## Testing WebSocket Connection

You can test the WebSocket connection using any WebSocket client. For example, using `websocat`:

```bash
websocat ws://localhost:8000/ws/{paper_id}
```

## Expected Results

When processing a paper, you should observe:

1. The paper progresses through the states: UPLOADED → QUEUED → PROCESSING → EXTRACTING_ENTITIES → EXTRACTING_RELATIONSHIPS → BUILDING_KNOWLEDGE_GRAPH → ANALYZED → IMPLEMENTATION_READY
2. Entity and relationship counts increase as the processing progresses
3. The knowledge graph is updated with new entities and relationships
4. Real-time status updates are sent through WebSocket

## Troubleshooting

If you encounter issues:

- Check MongoDB connection in `src/paper_processing/config/settings.py`
- Check Neo4j connection in `src/paper_processing/config/settings.py`
- Check Redis connection in `src/paper_processing/tasks/celery_app.py`
- Ensure all services are running properly
- Check logs for detailed error messages

## Research Orchestrator Testing

The research orchestrator components have comprehensive parameterized tests implemented for:

1. **Knowledge Extraction Module**:
   - Entity recognition tests with different entity types
   - Relationship extraction tests with different confidence levels
   - Knowledge extractor integration tests

2. **API Testing**:
   - All API endpoints include required query parameters:
   ```python
   # Example of adding required parameters:
   url = self.add_query_params("/implementation/planning/plans")
   response = self.client.get(url)
   
   # With additional parameters:
   url = self.add_query_params("/research/tasks/", {"limit": "10", "offset": "0"})
   response = self.client.get(url)
   ```

3. **Running Orchestrator Tests**:
   ```bash
   # Using the test runner script (recommended)
   ./run_tests.sh -p tests/research_orchestrator
   
   # Or manually with pytest
   cd tests/research_orchestrator
   python -m pytest
   ```

4. **WebSocket Testing**:
   - Tests for real-time updates via WebSocket connections
   - WebSocket message queue for collecting and validating event messages
   - Paper-specific and global event subscriptions
   
5. **CI/CD Integration**:
   - Tests automatically run on GitHub via GitHub Actions
   - Multi-Python version testing (3.9, 3.10, 3.11, 3.12)
   - Code coverage reporting

## Test Structure Best Practices

1. **Use Fixtures**:
   - Place common fixtures in `conftest.py`
   - Create specialized fixtures in component-specific test files
   - Use fixtures for reusing test data and setup code

2. **Parameterize Tests**:
   - Use `@pytest.mark.parametrize` for testing multiple scenarios
   - Group related test cases into single parameterized tests
   - Example:
   ```python
   @pytest.mark.parametrize("confidence,expected_ids", [
       (0.9, ["r1"]),
       (0.6, ["r1", "r2"]),
       (0.3, ["r1", "r2", "r3"]),
       (0.0, ["r1", "r2", "r3"])
   ])
   def test_filter_relationships_by_confidence(extractor, relationships, confidence, expected_ids):
       filtered = extractor.filter_relationships_by_confidence(relationships, confidence)
       filtered_ids = [rel.id for rel in filtered]
       assert sorted(filtered_ids) == sorted(expected_ids)
   ```

3. **Mock External Dependencies**:
   - Use pytest monkeypatch for temporary modifications
   - Create mock objects for external services
   - For API testing, include required query parameters:
   ```python
   def add_query_params(self, url, params=None):
       """Helper function to add required query parameters."""
       if params is None:
           params = {}
       if 'args' not in params:
           params['args'] = '[]'
       if 'kwargs' not in params:
           params['kwargs'] = '{}'
       # Build query string...
   ```

4. **Skip Tests Appropriately**:
   - Use `@pytest.mark.skip(reason="...")` for tests that need fixing
   - Use `@pytest.mark.skipif(condition, reason="...")` for conditional skips

5. **Using Test Runner Script**:
   - For consistent test execution, use the run_tests.sh script
   - Provides standard options for verbosity, coverage, and filtering
   - Example: `./run_tests.sh -v -c -k 'entity'`