# Documentation Updates

## 1. API Testing Enhancements

### Query Parameter Handling

The API now requires `args` and `kwargs` query parameters for certain endpoints, particularly in the implementation planning router. When testing these endpoints, ensure you include these parameters using the following pattern:

```python
# Add required query parameters to any API request
params = {
    "args": "[]",
    "kwargs": "{}"
}
response = client.get("/implementation/planning/plans", params=params)
```

For convenience, we've added a helper function in the test client:

```python
def add_query_params(url, params=None):
    """Helper function to add query parameters to API requests."""
    if params is None:
        params = {}
    
    # Ensure required parameters are included
    if 'args' not in params:
        params['args'] = '[]'
    if 'kwargs' not in params:
        params['kwargs'] = '{}'
    
    # Construct query string
    query_parts = [f"{k}={v}" for k, v in params.items()]
    query_string = "&".join(query_parts)
    
    # Add query string to URL
    if "?" in url:
        return f"{url}&{query_string}"
    else:
        return f"{url}?{query_string}"
```

## 2. Frontend API Client Updates

The implementation service in the frontend has been updated to use the correct backend endpoint paths. The key changes are:

1. Changed path patterns:
   - `/projects` → `/implementations`
   - `/projects/${id}/files` → `/implementations/${id}/files`
   - `/files/${id}/content` → `/implementations/files/${id}/content`
   - `/projects/${id}/tests` → `/implementations/${id}/tests`
   - `/projects/${id}/continue` → `/implementations/${id}/continue`

2. Added required query parameters to all API requests:
   ```typescript
   // Example of updated API call
   const response = await implementationApi.get<ApiResponse<Project[]>>('/implementations', {
     params: { args: '[]', kwargs: '{}' }
   });
   ```

## 3. WebSocket Testing Framework

We've created a comprehensive testing plan for WebSocket integration. The key components are:

### Directory Structure
```
tests/
└── integration_tests/
    └── websocket/
        ├── __init__.py
        ├── conftest.py
        ├── test_websocket_connection.py
        ├── test_websocket_paper_events.py
        └── test_websocket_system_events.py
```

### Test Fixtures
- `websocket_client`: Creates a global WebSocket connection
- `paper_websocket_client`: Creates a paper-specific WebSocket connection
- `test_paper_id`: Sets up a test paper and returns its ID
- `WebSocketMessageQueue`: Helper class to collect WebSocket messages

### Test Categories
1. **Connection Tests**: Verify basic WebSocket connectivity
2. **Paper Event Tests**: Test paper processing status updates
3. **System Event Tests**: Test system-wide notifications

See `WEBSOCKET_TEST_PLAN.md` for complete implementation details.

## 4. Running Tests

### Using run_tests.sh Script

We've added a `run_tests.sh` script that provides a consistent way to run tests:

```bash
# Run all tests with verbose output
./run_tests.sh -v

# Run tests with coverage reporting
./run_tests.sh -c

# Run tests in a specific path
./run_tests.sh -p tests/research_orchestrator/knowledge_extraction/

# Run a specific test file
./run_tests.sh -f tests/test_file.py

# Run tests matching an expression
./run_tests.sh -k 'entity'
```

## 5. Test Fixes

### Knowledge Extractor Tests

We've updated the `test_create_knowledge_graph_with_entities` test to use existing fixtures rather than creating custom entities:

```python
def test_create_knowledge_graph_with_entities(knowledge_extractor, sample_entities):
    """Test creating a knowledge graph with entities."""
    # Use sample_entities fixture instead of creating new entities
    doc_id = "test_doc"
    knowledge_graph = knowledge_extractor._create_knowledge_graph(sample_entities, [], doc_id)
    
    # Check basic structure
    assert "nodes" in knowledge_graph
    assert "edges" in knowledge_graph
    
    # Check that entities are correctly converted to nodes
    assert len(knowledge_graph["nodes"]) == len(sample_entities)
    assert len(knowledge_graph["edges"]) == 0
```

## 6. Next Steps

1. **WebSocket Test Implementation**: Create actual test files according to the plan
2. **Celery Task Tests**: Add tests for asynchronous processing
3. **Frontend Integration Tests**: Add tests for API clients and authentication flow
4. **CI/CD Pipeline**: Add test status badges and test result reporting