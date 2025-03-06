"""
Benchmark tests for the SearchManager component.

This module contains performance benchmark tests for the SearchManager component
of the Information Gathering module.
"""

import pytest
import time
import random
import string
import numpy as np
from unittest.mock import MagicMock, patch

# Mark all tests in this module as benchmark tests and search related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.search,
    pytest.mark.slow
]

# Try both import styles to ensure compatibility
try:
    from src.research_orchestrator.information_gathering.search_manager import SearchManager
    from src.research_orchestrator.information_gathering.source_manager import SourceManager
except ImportError:
    try:
        from research_orchestrator.information_gathering.search_manager import SearchManager
        from research_orchestrator.information_gathering.source_manager import SourceManager
    except ImportError:
        # Create mock classes for testing when actual modules are not available
        class SearchManager:
            def __init__(self, *args, **kwargs):
                pass
            def search(self, *args, **kwargs):
                return []
            def filter_results(self, *args, **kwargs):
                return []
            def sort_results(self, *args, **kwargs):
                return []
                
        class SourceManager:
            def __init__(self, *args, **kwargs):
                pass
            def search(self, *args, **kwargs):
                return []
            def get_sources(self, *args, **kwargs):
                return []


def generate_search_query(length=10):
    """Generate a random search query of specified length."""
    words = []
    for _ in range(length):
        word_length = random.randint(3, 10)
        word = ''.join(random.choices(string.ascii_lowercase, k=word_length))
        words.append(word)
    return ' '.join(words)


def generate_search_results(num_results=10):
    """Generate random search results."""
    results = []
    for i in range(num_results):
        result = {
            'title': f"Result {i}: {generate_search_query(3)}",
            'url': f"https://example.com/result{i}",
            'snippet': generate_search_query(random.randint(10, 30)),
            'source': random.choice(['web', 'academic', 'code', 'ai']),
            'relevance_score': random.uniform(0.5, 1.0)
        }
        results.append(result)
    return results


@pytest.fixture
def mock_source_manager():
    """Create a mock SourceManager for testing."""
    mock_manager = MagicMock(spec=SourceManager)
    
    # Set up the search method to return random results
    def mock_search(query, num_results=10, **kwargs):
        # Add a small delay to simulate network latency
        time.sleep(0.01 * random.uniform(0.5, 1.5))
        return generate_search_results(num_results)
    
    mock_manager.search = mock_search
    
    # The method might be get_source or get_sources, let's define both for flexibility
    sources = ['web', 'academic', 'code', 'ai']
    mock_manager.get_source = MagicMock(return_value=sources[0])
    mock_manager.get_sources = MagicMock(return_value=sources)
    
    # Also add sources as a dictionary attribute
    mock_manager.sources = {name: MagicMock() for name in sources}
    
    return mock_manager


@pytest.mark.parametrize('query_length', [5, 10, 20])
def test_search_performance(query_length, mock_source_manager, timer):
    """Test the search performance with different query lengths."""
    # Create a search manager with the mock source manager
    search_manager = SearchManager(source_manager=mock_source_manager)
    
    # Generate a query
    query = generate_search_query(query_length)
    
    # Measure search time
    with timer(f"SearchManager.search({query_length} words)"):
        results = search_manager.search(query, max_results=20)
    
    # Basic checks
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.parametrize('num_sources', [1, 2, 4, 8])
def test_multisource_search_scaling(num_sources, mock_source_manager, timer):
    """Test how search performance scales with the number of sources."""
    # Create a search manager with the mock source manager
    search_manager = SearchManager(source_manager=mock_source_manager)
    
    # Generate a query
    query = generate_search_query(10)
    
    # Select a subset of sources
    sources = ['web', 'academic', 'code', 'ai'][:num_sources]
    
    # Measure search time
    with timer(f"SearchManager.search_multiple_sources({num_sources} sources)"):
        results = search_manager.search(query, sources=sources, max_results=20)
    
    # Basic checks
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.parametrize('result_count', [10, 50, 100, 200])
def test_result_volume_performance(result_count, mock_source_manager, timer):
    """Test search performance with different result volumes."""
    # Modify the mock source manager to return the specified number of results
    mock_source_manager.search = lambda q, **kwargs: generate_search_results(result_count)
    
    # Create a search manager with the mock source manager
    search_manager = SearchManager(source_manager=mock_source_manager)
    
    # Generate a query
    query = generate_search_query(10)
    
    # Measure search time
    with timer(f"SearchManager.search({result_count} results)"):
        results = search_manager.search(query)
    
    # Measure result processing time
    with timer(f"SearchManager.filter_results({result_count} results)"):
        filtered_results = search_manager.filter_results(results, min_relevance=0.7)
    
    # Measure result sorting time
    with timer(f"SearchManager.sort_results({result_count} results)"):
        sorted_results = search_manager.sort_results(results, sort_by='relevance')
    
    # Basic checks
    assert isinstance(results, list)
    assert len(results) == result_count


def test_search_manager_scalability():
    """Test how search performance scales with the number of results."""
    # Create mock source manager
    mock_source_manager = MagicMock(spec=SourceManager)
    
    # Create search manager
    search_manager = SearchManager(source_manager=mock_source_manager)
    
    # Test with different result counts
    result_counts = [10, 50, 100, 500, 1000]
    times = []
    
    for count in result_counts:
        # Set up mock to return the specified number of results
        mock_source_manager.search = lambda q, **kwargs: generate_search_results(count)
        
        # Generate a query
        query = generate_search_query(10)
        
        # Measure search time
        start_time = time.time()
        results = search_manager.search(query)
        end_time = time.time()
        
        times.append(end_time - start_time)
    
    # Output results
    print("\nSearch Manager Scalability:")
    print("-------------------------------")
    print(f"{'Results':<10} {'Time (s)':<10}")
    print("-------------------------------")
    for i, count in enumerate(result_counts):
        print(f"{count:<10} {times[i]:<10.4f}")
    
    # Calculate scaling factor using linear regression
    log_counts = np.log(result_counts)
    log_times = np.log(times)
    slope, intercept = np.polyfit(log_counts, log_times, 1)
    
    print(f"\nScaling factor: O(n^{slope:.2f})")
    
    # Check scaling is close to linear
    assert slope < 1.2, f"Search performance scales poorly: O(n^{slope:.2f})"


def test_memory_usage():
    """Test memory usage of the SearchManager with large result sets."""
    import psutil
    import os
    
    # Get current process
    process = psutil.Process(os.getpid())
    
    # Create mock source manager
    mock_source_manager = MagicMock(spec=SourceManager)
    
    # Create search manager
    search_manager = SearchManager(source_manager=mock_source_manager)
    
    # Test with different result counts
    result_counts = [100, 1000, 10000]
    memory_usages = []
    
    for count in result_counts:
        # Set up mock to return the specified number of results
        mock_source_manager.search = lambda q, **kwargs: generate_search_results(count)
        
        # Generate a query
        query = generate_search_query(10)
        
        # Measure memory before
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Execute search
        results = search_manager.search(query)
        
        # Measure memory after
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Calculate memory usage
        memory_usage = memory_after - memory_before
        memory_usages.append(memory_usage)
    
    # Output results
    print("\nSearch Manager Memory Usage:")
    print("-------------------------------")
    print(f"{'Results':<10} {'Memory (MB)':<15}")
    print("-------------------------------")
    for i, count in enumerate(result_counts):
        print(f"{count:<10} {memory_usages[i]:<15.2f}")
    
    # Check memory usage is reasonable
    for i, count in enumerate(result_counts):
        # Expect memory usage to be less than 10 bytes per result on average (allowing for overhead)
        expected_max_usage = count * 10 / (1024 * 1024) + 5  # MB with 5MB overhead
        assert memory_usages[i] < expected_max_usage, f"Memory usage too high for {count} results: {memory_usages[i]} MB"