"""
Benchmark test template.

This template provides a structure for implementing benchmark tests using pytest-benchmark.
Replace placeholders with actual component-specific code.
"""

import pytest
import random
import string
import json
import time
import gc
import psutil
import os

# Mark all tests in this module as benchmark tests and component related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.component_name,  # Replace with actual component marker
    pytest.mark.slow
]

# Import your component classes here
# from src.your_module.your_component import YourComponent


def test_small_input_performance(benchmark_component, benchmark):
    """Benchmark performance with small inputs."""
    # Create a small input
    input_data = create_input(size="small")
    
    # Benchmark the process method
    result = benchmark(benchmark_component.process, input_data)
    
    # Verify result is correct (basic sanity check)
    assert result is not None


def test_medium_input_performance(benchmark_component, benchmark):
    """Benchmark performance with medium inputs."""
    # Create a medium input
    input_data = create_input(size="medium")
    
    # Benchmark the process method
    result = benchmark(benchmark_component.process, input_data)
    
    # Verify result is correct (basic sanity check)
    assert result is not None


def test_large_input_performance(benchmark_component, benchmark):
    """Benchmark performance with large inputs."""
    # Create a large input
    input_data = create_input(size="large")
    
    # Benchmark the process method
    result = benchmark(benchmark_component.process, input_data)
    
    # Verify result is correct (basic sanity check)
    assert result is not None


@pytest.mark.parametrize("input_size", ["small", "medium", "large"])
def test_input_size_scaling(benchmark_component, benchmark, input_size):
    """Test how performance scales with input size."""
    # Create an input of the specified size
    input_data = create_input(size=input_size)
    
    # Benchmark the process method
    result = benchmark(benchmark_component.process, input_data)
    
    # Verify result is correct (basic sanity check)
    assert result is not None


@pytest.mark.parametrize("complexity", ["simple", "medium", "complex"])
def test_complexity_scaling(benchmark_component, benchmark, complexity):
    """Test how performance scales with input complexity."""
    # Create input with the specified complexity
    input_data = create_input(complexity=complexity)
    
    # Benchmark the process method
    result = benchmark(benchmark_component.process, input_data)
    
    # Verify result is correct (basic sanity check)
    assert result is not None


def test_batch_processing_performance(benchmark_component, benchmark):
    """Benchmark batch processing performance."""
    # Create a batch of inputs
    batch = [create_input(size="small") for _ in range(10)]
    
    # Benchmark the batch process method
    result = benchmark(benchmark_component.process_batch, batch)
    
    # Verify result is correct (basic sanity check)
    assert result is not None
    assert len(result) == len(batch)


def test_repeated_processing_performance(benchmark_component, benchmark):
    """Benchmark performance of repeated processing of the same input."""
    # Create a medium input
    input_data = create_input(size="medium")
    
    # Define a function for repeated processing
    def repeated_process():
        for _ in range(5):
            benchmark_component.process(input_data)
    
    # Benchmark the repeated processing
    benchmark(repeated_process)


def test_memory_usage(benchmark_component):
    """Test memory usage during processing."""
    # Collect garbage to start with a clean state
    gc.collect()
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create a large input
    input_data = create_input(size="large")
    
    # Process the input
    result = benchmark_component.process(input_data)
    
    # Ensure result is not garbage collected
    assert result is not None
    
    # Get peak memory usage
    peak_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = peak_memory - initial_memory
    
    # Print memory usage information
    print(f"Memory used: {memory_used:.2f} MB")
    
    # Memory usage should be reasonable for the input size
    # Assert only if it exceeds a reasonable threshold
    assert memory_used < 1000, f"Memory usage too high: {memory_used:.2f} MB"


def test_concurrent_processing_performance(benchmark_component, benchmark):
    """Benchmark performance of concurrent processing."""
    # Create a batch of inputs
    batch = [create_input(size="small") for _ in range(10)]
    
    # Benchmark the concurrent process method
    result = benchmark(benchmark_component.process_concurrent, batch)
    
    # Verify result is correct (basic sanity check)
    assert result is not None
    assert len(result) == len(batch)


def test_cold_start_performance(benchmark):
    """Benchmark component initialization and first processing."""
    # Define a function for cold start
    def cold_start():
        # Create a new component instance
        component = YourComponent()
        # Process an input
        input_data = create_input(size="small")
        return component.process(input_data)
    
    # Benchmark the cold start
    result = benchmark(cold_start)
    
    # Verify result is correct (basic sanity check)
    assert result is not None


def test_serialization_performance(benchmark_component, benchmark):
    """Benchmark serialization performance."""
    # Create a medium input
    input_data = create_input(size="medium")
    
    # Process the input
    result = benchmark_component.process(input_data)
    
    # Benchmark the serialization
    serialized = benchmark(result.to_json)
    
    # Verify serialization is correct
    assert serialized is not None
    assert isinstance(serialized, str)


def test_deserialization_performance(benchmark_component, benchmark):
    """Benchmark deserialization performance."""
    # Create a medium input
    input_data = create_input(size="medium")
    
    # Process the input and serialize
    result = benchmark_component.process(input_data)
    serialized = result.to_json()
    
    # Benchmark the deserialization
    deserialized = benchmark(benchmark_component.from_json, serialized)
    
    # Verify deserialization is correct
    assert deserialized is not None
    assert deserialized == result


# Example fixture (for reference - implement in conftest.py)

@pytest.fixture
def benchmark_component():
    """Return a component instance for benchmark testing."""
    # Create and configure your component
    # component = YourComponent()
    # component.configure({"option": "value"})
    # return component
    pass


# Helper functions

def create_input(size="medium", complexity="medium"):
    """Create a test input with the specified size and complexity."""
    # Size dictates the volume of data
    if size == "small":
        text_length = 100
        num_items = 5
    elif size == "medium":
        text_length = 1000
        num_items = 20
    else:  # large
        text_length = 10000
        num_items = 100
    
    # Complexity dictates the structure of data
    if complexity == "simple":
        # Simple string
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=text_length))
    elif complexity == "medium":
        # Dictionary with simple values
        return {
            "name": ''.join(random.choices(string.ascii_letters, k=10)),
            "description": ''.join(random.choices(string.ascii_letters + ' ', k=text_length)),
            "values": [random.randint(0, 1000) for _ in range(num_items)],
            "active": random.choice([True, False])
        }
    else:  # complex
        # Nested structure with various data types
        return {
            "metadata": {
                "id": ''.join(random.choices(string.hexdigits, k=24)),
                "created": time.time(),
                "version": f"{random.randint(1, 10)}.{random.randint(0, 99)}"
            },
            "content": {
                "title": ''.join(random.choices(string.ascii_letters + ' ', k=20)),
                "body": ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=text_length)),
                "tags": [''.join(random.choices(string.ascii_lowercase, k=5)) for _ in range(random.randint(1, 10))]
            },
            "items": [
                {
                    "id": i,
                    "name": ''.join(random.choices(string.ascii_letters, k=8)),
                    "value": random.random() * 100
                } for i in range(num_items)
            ]
        }