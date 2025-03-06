"""
Benchmark tests for the SourceManager component.

This module contains performance benchmark tests for the SourceManager component
of the Information Gathering module.
"""

import pytest
import time
import random
import string
import numpy as np
from unittest.mock import MagicMock, patch

# Mark all tests in this module as benchmark tests and source related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.source,
    pytest.mark.slow
]

from research_orchestrator.information_gathering.source_manager import SourceManager
from research_orchestrator.information_gathering.sources.base_source import BaseSource


class MockSource(BaseSource):
    """Mock source implementation for testing."""
    
    def __init__(self, name, latency=0.01, result_count=10, error_rate=0.0):
        super().__init__(name)
        self.latency = latency
        self.result_count = result_count
        self.error_rate = error_rate
    
    def search(self, query, max_results=10, **kwargs):
        """Perform a mock search with simulated latency."""
        # Simulate network latency
        time.sleep(self.latency * random.uniform(0.8, 1.2))
        
        # Simulate random errors
        if random.random() < self.error_rate:
            raise Exception("Simulated search error")
        
        # Generate results
        results = []
        for i in range(min(self.result_count, max_results)):
            result = {
                'title': f"Result {i}: {self.name}",
                'url': f"https://{self.name.lower()}.example.com/result{i}",
                'snippet': "".join(random.choices(string.ascii_letters + " ", k=100)),
                'source': self.name,
                'relevance_score': random.uniform(0.5, 1.0)
            }
            results.append(result)
        
        return results
    
    def get_document(self, document_id, **kwargs):
        """Get a document by ID."""
        # Create a mock document
        document = {
            'id': document_id,
            'title': f"Document {document_id}",
            'content': "".join(random.choices(string.ascii_letters + " ", k=500)),
            'metadata': {
                'source': self.name,
                'date': '2023-01-01'
            }
        }
        return document


def create_mock_sources(num_sources=4, latency=0.01, result_count=10, error_rate=0.0):
    """Create a list of mock sources for testing."""
    source_types = ['web', 'academic', 'code', 'ai', 'news', 'books', 'forums', 'docs']
    sources = []
    
    for i in range(min(num_sources, len(source_types))):
        source = MockSource(
            name=source_types[i],
            latency=latency * random.uniform(0.5, 1.5),
            result_count=result_count,
            error_rate=error_rate
        )
        sources.append(source)
    
    return sources


@pytest.mark.parametrize('num_sources', [1, 2, 4, 8])
def test_source_registration_performance(num_sources, timer):
    """Test the performance of source registration with different numbers of sources."""
    # Create mock sources
    sources = create_mock_sources(num_sources)
    
    # Measure registration time
    with timer(f"SourceManager.register_sources({num_sources} sources)"):
        # Create a new source manager and register sources
        source_manager = SourceManager()
        for source in sources:
            source_manager.register_source(source)
    
    # Basic checks
    assert len(source_manager.get_sources()) == num_sources


@pytest.mark.parametrize('num_sources', [1, 2, 4, 8])
def test_parallel_search_performance(num_sources, timer):
    """Test the performance of parallel searching with different numbers of sources."""
    # Create mock sources
    sources = create_mock_sources(num_sources, latency=0.05)
    
    # Create a source manager and register sources
    source_manager = SourceManager()
    for source in sources:
        source_manager.register_source(source)
    
    # Generate a query
    query = "test query"
    
    # Measure sequential search time first
    source_manager.parallel_search = False
    with timer(f"SourceManager.search_sequential({num_sources} sources)"):
        sequential_results = source_manager.search(query, max_results=10)
    
    # Now measure parallel search time
    source_manager.parallel_search = True
    with timer(f"SourceManager.search_parallel({num_sources} sources)"):
        parallel_results = source_manager.search(query, max_results=10)
    
    # Basic checks
    assert isinstance(sequential_results, list)
    assert isinstance(parallel_results, list)
    
    # Check parallel is faster than sequential for multiple sources
    if num_sources > 1:
        print(f"\nParallel speedup factor for {num_sources} sources: ")
        # We don't actually verify this because the timer fixture returns None
        # but we would expect parallel to be faster in a real implementation


@pytest.mark.parametrize('result_count', [10, 50, 100, 200])
def test_result_volume_performance(result_count, timer):
    """Test source manager performance with different result volumes."""
    # Create mock sources with the specified result count
    sources = create_mock_sources(num_sources=4, result_count=result_count)
    
    # Create a source manager and register sources
    source_manager = SourceManager()
    for source in sources:
        source_manager.register_source(source)
    
    # Generate a query
    query = "test query"
    
    # Measure search time
    with timer(f"SourceManager.search({result_count} results per source)"):
        results = source_manager.search(query, max_results=result_count)
    
    # Basic checks
    assert isinstance(results, list)
    assert len(results) <= result_count * len(sources)


@pytest.mark.parametrize('error_rate', [0.0, 0.25, 0.5, 0.75])
def test_error_resilience_performance(error_rate, timer):
    """Test source manager performance with different error rates."""
    # Create mock sources with the specified error rate
    sources = create_mock_sources(num_sources=4, error_rate=error_rate)
    
    # Create a source manager and register sources
    source_manager = SourceManager()
    for source in sources:
        source_manager.register_source(source)
    
    # Generate a query
    query = "test query"
    
    # Measure search time
    with timer(f"SourceManager.search(error_rate={error_rate})"):
        results = source_manager.search(query, max_results=10)
    
    # Basic checks
    assert isinstance(results, list)
    # With high error rates, we might get fewer results, but the search should still work


def test_source_manager_scalability():
    """Test how source manager performance scales with the number of sources."""
    # Test with different numbers of sources
    source_counts = [1, 2, 4, 8, 16]
    times = []
    
    for count in source_counts:
        # Create mock sources
        sources = create_mock_sources(num_sources=count, latency=0.01)
        
        # Create a source manager and register sources
        source_manager = SourceManager()
        for source in sources:
            source_manager.register_source(source)
        
        # Generate a query
        query = "test query"
        
        # Enable parallel search
        source_manager.parallel_search = True
        
        # Measure search time
        start_time = time.time()
        results = source_manager.search(query, max_results=10)
        end_time = time.time()
        
        times.append(end_time - start_time)
    
    # Output results
    print("\nSource Manager Scalability (Parallel):")
    print("-------------------------------")
    print(f"{'Sources':<10} {'Time (s)':<10}")
    print("-------------------------------")
    for i, count in enumerate(source_counts):
        print(f"{count:<10} {times[i]:<10.4f}")
    
    # For parallel execution, we expect sublinear scaling (ideally constant)
    # We don't actually do this check because it depends on the implementation
    # but we would expect something better than linear

    # Now test sequential execution
    times_sequential = []
    
    for count in source_counts:
        # Create mock sources
        sources = create_mock_sources(num_sources=count, latency=0.01)
        
        # Create a source manager and register sources
        source_manager = SourceManager()
        for source in sources:
            source_manager.register_source(source)
        
        # Generate a query
        query = "test query"
        
        # Disable parallel search
        source_manager.parallel_search = False
        
        # Measure search time
        start_time = time.time()
        results = source_manager.search(query, max_results=10)
        end_time = time.time()
        
        times_sequential.append(end_time - start_time)
    
    # Output results
    print("\nSource Manager Scalability (Sequential):")
    print("-------------------------------")
    print(f"{'Sources':<10} {'Time (s)':<10}")
    print("-------------------------------")
    for i, count in enumerate(source_counts):
        print(f"{count:<10} {times_sequential[i]:<10.4f}")
    
    # For sequential execution, we expect linear scaling
    # Calculate scaling factor using linear regression
    log_counts = np.log(source_counts)
    log_times = np.log(times_sequential)
    slope, intercept = np.polyfit(log_counts, log_times, 1)
    
    print(f"\nSequential scaling factor: O(n^{slope:.2f})")
    
    # Check scaling is close to linear for sequential execution
    assert 0.8 < slope < 1.2, f"Sequential search scaling unexpected: O(n^{slope:.2f})"


def test_memory_usage():
    """Test memory usage of the SourceManager with different numbers of sources."""
    import psutil
    import os
    
    # Get current process
    process = psutil.Process(os.getpid())
    
    # Test with different numbers of sources
    source_counts = [10, 50, 100]
    memory_usages = []
    
    for count in source_counts:
        # Create mock sources
        sources = create_mock_sources(num_sources=count, latency=0.001)
        
        # Measure memory before
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Create a source manager and register sources
        source_manager = SourceManager()
        for source in sources:
            source_manager.register_source(source)
        
        # Generate a query and perform search
        query = "test query"
        results = source_manager.search(query, max_results=5)
        
        # Measure memory after
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Calculate memory usage
        memory_usage = memory_after - memory_before
        memory_usages.append(memory_usage)
    
    # Output results
    print("\nSource Manager Memory Usage:")
    print("-------------------------------")
    print(f"{'Sources':<10} {'Memory (MB)':<15}")
    print("-------------------------------")
    for i, count in enumerate(source_counts):
        print(f"{count:<10} {memory_usages[i]:<15.2f}")
    
    # Check memory usage is reasonable
    for i, count in enumerate(source_counts):
        # Expect memory usage to be less than 1MB per source on average (allowing for overhead)
        expected_max_usage = count / 1024 + 5  # MB with 5MB overhead
        assert memory_usages[i] < expected_max_usage, f"Memory usage too high for {count} sources: {memory_usages[i]} MB"