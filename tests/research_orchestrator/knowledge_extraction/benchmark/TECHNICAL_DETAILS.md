# Technical Details for Knowledge Extraction Benchmarks

This document provides technical details about the benchmark implementation for the Knowledge Extraction components.

## Architecture

The benchmark system consists of several components:

1. **Benchmark Tests**: Individual test files for each component of the knowledge extraction system
2. **Fixture System**: Utilities for generating test data of various sizes and complexities
3. **Reporting System**: Tools for capturing and presenting performance results
4. **Runner Script**: A command-line interface for executing benchmarks and generating reports

## Import Structure

The benchmarks use relative imports with the following pattern:

```python
from research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from research_orchestrator.knowledge_extraction.document_processing.text_processor import TextProcessor
```

## Fixture Pattern

The fixtures use a closure pattern to support parameterization:

```python
@pytest.fixture
def generate_text_document():
    """Generate a text document of the given size."""
    def _generate(size_kb):
        # Implementation...
        return Document(content=content, document_type="text", ...)
    
    return _generate
```

This allows tests to call the fixture with parameters:

```python
@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_entity_recognition_performance(size_kb, generate_text_document, timer):
    document = generate_text_document(size_kb)
    # ...
```

## Timer Implementation

The timer fixture uses a context manager to measure execution times:

```python
class Timer:
    """Utility class for timing operations."""
    
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        print(f"{self.name}: {self.duration:.4f} seconds")
    
    @property
    def duration(self):
        """Return the duration in seconds."""
        if self.start_time is None or self.end_time is None:
            return 0
        return self.end_time - self.start_time
```

## Scaling Analysis

Scaling analysis is performed using numpy's `polyfit` to determine the relationship between input size and execution time:

```python
# Calculate scaling factor using linear regression
log_sizes = np.log(sizes)
log_times = np.log(times)
slope, intercept = np.polyfit(log_sizes, log_times, 1)

print(f"\nScaling factor: O(n^{slope:.2f})")
```

A slope of 1.0 indicates linear scaling (O(n)), while slopes greater than 1.0 indicate worse-than-linear scaling.

## Test Data Generation

Test data generation includes:

1. **Document Generation**: Creates documents with AI-related content and random text to reach desired size
2. **Entity Generation**: Creates entities with realistic types and attributes
3. **Relationship Generation**: Creates relationships between entities with appropriate types and contexts

## Report Generation

The reporting system generates:

1. **JSON Reports**: Machine-readable performance data
2. **HTML Reports**: Human-readable reports with charts and tables
3. **Console Output**: Real-time feedback during benchmark execution

## Integration with pytest

The benchmarks use pytest's marker and parametrization systems:

```python
# Mark all tests in this module as benchmark tests and document related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.document,
    pytest.mark.slow
]

@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_text_processor_performance(size_kb, timer):
    # Test implementation...
```

## Best Practices

1. **Isolation**: Each benchmark measures a specific component in isolation
2. **Parametrization**: Tests run with different input sizes to measure scaling
3. **Reproducibility**: Random data generation uses fixed seeds for consistency
4. **Verification**: Assertions verify that results meet expectations
5. **Cleanup**: Temporary files and resources are properly cleaned up