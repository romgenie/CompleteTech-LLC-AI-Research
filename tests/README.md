# Testing Guidelines and Best Practices

This document provides guidelines for writing effective tests for the Research Orchestration Framework. Following these practices will ensure maintainable, reliable tests.

## Types of Tests

1. **Unit Tests**: Test individual components in isolation
   - Located in `tests/*/test_*.py`
   - Use extensive mocking of dependencies
   - Fast to run and should not have external dependencies

2. **Integration Tests**: Test interactions between multiple components
   - Located in `tests/integration_tests/`
   - Test how components work together
   - May have limited external dependencies

3. **End-to-End Tests**: Test the complete system
   - Located in `tests/e2e/`
   - Test the system from a user perspective
   - Can use real external dependencies

## Best Practices

### 1. Use Fixtures

Fixtures are the primary way to set up test data in pytest. They provide:
- Reusable test setups
- Clean isolation between tests
- Automatic teardown

```python
@pytest.fixture
def sample_entity():
    """Return a sample entity for testing."""
    return Entity(
        text="BERT", 
        type=EntityType.MODEL,
        confidence=0.95,
        start_pos=10,
        end_pos=14,
        metadata={"source": "test"},
        id="test_entity_1"
    )

def test_with_fixture(sample_entity):
    # Use the fixture in your test
    assert sample_entity.text == "BERT"
```

### 2. Prefer Function-Based Tests Over Class-Based Tests

- Function-based tests are more concise and focused
- They make better use of pytest fixtures
- Less boilerplate code compared to unittest-style tests

*Preferred*:
```python
def test_extract_entities(knowledge_extractor, sample_entities):
    # Test implementation
    ...
```

*Less preferred*:
```python
class TestKnowledgeExtractor(unittest.TestCase):
    def setUp(self):
        # Setup code
        ...
    
    def test_extract_entities(self):
        # Test implementation
        ...
```

### 3. Name Tests Clearly

- Use descriptive test names that clearly indicate what's being tested
- Follow the pattern `test_[function]_[condition]_[expected_result]`

```python
def test_filter_relationships_with_high_confidence_returns_only_high_confidence_relationships():
    # Test implementation
    ...
```

### 4. Use Markers Appropriately

Markers help categorize tests:

```python
@pytest.mark.slow
def test_large_document_processing():
    # A slow test that processes a large document
    ...

@pytest.mark.api
def test_api_endpoint():
    # A test for an API endpoint
    ...
```

### 5. Mock External Dependencies

Use mocking to isolate tests from external dependencies:

```python
@pytest.mark.parametrize("status_code,expected_result", [
    (200, True),
    (404, False),
    (500, False)
])
def test_api_client(mock_response, status_code, expected_result):
    # Configure the mock response
    mock_response.status_code = status_code
    
    # Test implementation
    ...
```

### 6. Make Tests Deterministic

- Avoid dependencies on external state
- Use fixed data rather than random or time-based values
- Seed random number generators if randomness is needed

### 7. One Assertion per Test (when possible)

- Focus each test on a single behavior
- Makes it easier to identify failures
- Improves test readability

### 8. Use Parametrized Tests

Use `@pytest.mark.parametrize` to test multiple cases:

```python
@pytest.mark.parametrize("entity_type,expected_count", [
    (EntityType.MODEL, 3),
    (EntityType.DATASET, 2),
    (EntityType.BENCHMARK, 1)
])
def test_filter_entities_by_type(recognizer, entity_type, expected_count):
    # Test implementation
    ...
```

#### Real-world Example

Here's an example from our entity recognition tests:

```python
@pytest.mark.parametrize("entity_type, expected_count", [
    (EntityType.MODEL, 2),
    (EntityType.DATASET, 3),
    (EntityType.ALGORITHM, 1),
    (EntityType.METRIC, 2),
])
def test_entity_recognition_by_type(entity_recognizer, sample_text, entity_type, expected_count):
    """Test entity recognizer can identify specific entity types correctly."""
    entities = entity_recognizer.extract_entities(sample_text)
    filtered_entities = [e for e in entities if e.type == entity_type]
    assert len(filtered_entities) == expected_count
```

### 9. Avoid Test Logic

- Keep tests simple and straightforward
- Avoid complex control structures (if/else, loops) in tests
- Use fixtures and parameterization instead

### 10. Test Error Cases

- Don't just test the "happy path"
- Test how code handles invalid inputs, errors, and edge cases

```python
def test_process_document_with_invalid_format_raises_error():
    # Test implementation
    ...
```

## Running Tests

### Basic Test Run
```
python -m pytest
```

### Run Tests with Coverage
```
python -m pytest --cov=src tests/
```

### Run Specific Test Files
```
python -m pytest tests/research_orchestrator/knowledge_extraction/test_entity_recognition.py
```

### Run Tests with Markers
```
python -m pytest -m "unit and not slow"
```

## Continuous Integration

Our CI/CD pipeline automatically runs tests on:
- Pull requests
- Merge to main branch

Tests must pass before code can be merged.

### GitHub Actions Configuration

We use GitHub Actions for CI/CD with the following features:

- **Multi-environment testing**: Tests run against Python 3.9, 3.10, 3.11, and 3.12
- **Automatic test discovery**: All test files matching the pattern `test_*.py` are discovered and executed
- **Coverage reporting**: Code coverage is measured and reported for each run
- **Pull request integration**: Tests automatically run on all PRs
- **Status badges**: Repository includes badges for build status and code coverage

The workflow is defined in `.github/workflows/run-tests.yml`.

## Testing Tools Reference

### Pytest
- [Pytest Documentation](https://docs.pytest.org/en/stable/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Parametrizing](https://docs.pytest.org/en/stable/parametrize.html)

### Mock
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### Coverage
- [Coverage.py Documentation](https://coverage.readthedocs.io/)