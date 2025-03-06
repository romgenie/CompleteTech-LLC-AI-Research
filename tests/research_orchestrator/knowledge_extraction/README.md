# Knowledge Extraction Tests

This directory contains tests for the Knowledge Extraction components of the Research Orchestrator. The tests are organized by component and test type.

## Test Structure

Tests are organized into three levels:

1. **Unit Tests** (`unit/`): Test individual components in isolation
   - Document processing
   - Entity recognition
   - Relationship extraction
   - Knowledge extractor

2. **Integration Tests** (`integration/`): Test interactions between components
   - Document processing → Entity recognition
   - Entity recognition → Relationship extraction
   - Relationship extraction → Knowledge graph

3. **End-to-End Tests** (`e2e/`): Test the full pipeline
   - Full extraction pipeline
   - Multi-document extraction
   - Real-world scenarios

4. **Property-Based Tests** (`property/`): Test system properties and invariants
   - Entity serialization/deserialization
   - Knowledge graph properties
   - Document content extraction
   - Relationship bidirectionality

5. **Benchmark Tests** (`benchmark/`): Test performance characteristics
   - Document processing speed
   - Entity recognition scaling
   - Relationship extraction memory usage
   - End-to-end pipeline performance

6. **Edge Case Tests** (`edge_cases/`): Test error handling and boundary conditions
   - Empty documents and entities
   - Malformed inputs
   - Special characters and encoding issues
   - Conflicting and circular relationships
   - Very large inputs

## Test Data

Test data is provided in the `data/` directory:

- `documents/`: Sample documents (text, HTML, PDF)
- `entities/`: Entity test data
- `relationships/`: Relationship test data
- `graphs/`: Knowledge graph test data

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided script:

```bash
# Run all tests
./run_tests.sh

# Run only unit tests
./run_tests.sh -t unit

# Run only entity-related tests
./run_tests.sh -m entity

# Run fast unit tests
./run_tests.sh -m "fast and unit"

# Run property-based tests
./run_tests.sh -t property

# Run benchmark tests
./run_tests.sh -t benchmark

# Run edge case tests
./run_tests.sh -t edge

# Generate HTML report for end-to-end tests
./run_tests.sh -t e2e -r

# Show help
./run_tests.sh -h
```

### Using pytest Directly

You can also run tests directly with pytest:

```bash
# Run all tests
python -m pytest .

# Run unit tests
python -m pytest unit/

# Run integration tests
python -m pytest integration/

# Run end-to-end tests
python -m pytest e2e/

# Run property-based tests
python -m pytest property/

# Run benchmark tests
python -m pytest benchmark/

# Run edge case tests
python -m pytest edge_cases/

# Run tests with specific markers
python -m pytest -m "entity and not slow"

# Run property-based tests for entities
python -m pytest -m "property and entity"

# Run benchmark tests for document processing
python -m pytest -m "benchmark and document"

# Run edge case tests for entity recognition
python -m pytest -m "edge_case and entity"
```

## Test Markers

Tests are marked with various markers for easy filtering:

- **Test Level**
  - `unit`: Unit tests
  - `integration`: Integration tests
  - `e2e`: End-to-end tests
  - `property`: Property-based tests
  - `benchmark`: Performance benchmark tests
  - `edge_case`: Edge case and error handling tests

- **Component**
  - `document`: Document processing tests
  - `entity`: Entity recognition tests
  - `relationship`: Relationship extraction tests
  - `knowledge_graph`: Knowledge graph tests

- **Performance**
  - `fast`: Tests that run quickly
  - `medium`: Tests that run at moderate speed
  - `slow`: Tests that run slowly

- **Stability**
  - `stable`: Tests that are stable and reliable
  - `unstable`: Tests that may be flaky

- **Edge Cases**
  - `error`: Tests that expect errors to be raised
  - `malformed`: Tests with malformed inputs
  - `empty`: Tests with empty inputs
  - `large`: Tests with very large inputs
  - `duplicate`: Tests with duplicate data
  - `invalid`: Tests with invalid inputs
  - `circular`: Tests with circular references
  - `conflicting`: Tests with conflicting data
  - `special_chars`: Tests with special characters

## Test Fixtures

Test fixtures are defined in `conftest.py` files at different levels:

- Root `conftest.py`: Shared fixtures for all tests
- `unit/conftest.py`: Fixtures for unit tests
- `integration/conftest.py`: Fixtures for integration tests
- `e2e/conftest.py`: Fixtures for end-to-end tests
- `property/conftest.py`: Fixtures for property-based tests
- `benchmark/conftest.py`: Fixtures for benchmark tests
- `edge_cases/conftest.py`: Fixtures for edge case tests

## Test Components

### Document Processing Tests

Tests for document processing cover:
- Document class functionality
- Text processor
- HTML processor
- Document metadata extraction

### Entity Recognition Tests

Tests for entity recognition cover:
- Entity class functionality
- Entity type handling
- Pattern-based entity recognition
- AI-specific entity recognition
- Scientific entity recognition
- Entity filtering and confidence scoring

### Relationship Extraction Tests

Tests for relationship extraction cover:
- Relationship class functionality
- Relationship type handling
- Pattern-based relationship extraction
- AI-specific relationship extraction
- Relationship filtering and confidence scoring
- Combined extractors with conflict resolution

### Knowledge Extractor Tests

Tests for the knowledge extractor cover:
- Document processing integration
- Entity recognition integration
- Relationship extraction integration
- Knowledge graph creation
- Result serialization and storage
- Statistics generation

## Migration

This test structure represents a migration from the previous structure. For details on the migration, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

## Test Plan

For a comprehensive test plan including future improvements, see [TEST_PLAN.md](TEST_PLAN.md).