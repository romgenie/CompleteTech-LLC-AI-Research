"""
Fixtures for benchmark tests for the Information Gathering module.

This module provides pytest fixtures for benchmark testing using pytest-benchmark.
"""

import pytest
import random
import string
import json
import time
from contextlib import contextmanager
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any

# Try both import styles to ensure compatibility
try:
    from src.research_orchestrator.information_gathering.search_manager import SearchManager
    from src.research_orchestrator.information_gathering.source_manager import SourceManager
    from src.research_orchestrator.information_gathering.quality_assessor import QualityAssessor
    from src.research_orchestrator.information_gathering.sources.base_source import BaseSource
except ImportError:
    try:
        from src.research_orchestrator.information_gathering.search_manager import SearchManager
        from src.research_orchestrator.information_gathering.source_manager import SourceManager
        from src.research_orchestrator.information_gathering.quality_assessor import QualityAssessor
        from src.research_orchestrator.information_gathering.sources.base_source import BaseSource
    except ImportError:
        # Create mock classes for testing when actual modules are not available
        class SearchManager:
            def __init__(self, *args, **kwargs):
                self.source_manager = kwargs.get('source_manager', None)
                self.quality_assessor = kwargs.get('quality_assessor', None)
            def search(self, *args, **kwargs):
                return []
            def filter_results(self, *args, **kwargs):
                return []
            def sort_results(self, *args, **kwargs):
                return []
                
        class SourceManager:
            def __init__(self, *args, **kwargs):
                self.sources = {}
                self.parallel_search = True
            def register_source(self, source):
                self.sources[source.name] = source
            def get_sources(self, *args, **kwargs):
                return list(self.sources.keys())
            def search(self, *args, **kwargs):
                return []
        
        class QualityAssessor:
            def __init__(self, *args, **kwargs):
                pass
            def assess_results(self, results):
                return results
            def assess_result(self, result):
                return result
            def filter_results(self, results, min_quality=0.0):
                return [r for r in results if r.get('quality_score', 0) >= min_quality]
            def calculate_relevance_score(self, result):
                return 0.9
            def calculate_completeness_score(self, result):
                return 0.8
            def calculate_accuracy_score(self, result):
                return 0.7
            def calculate_overall_quality_score(self, result):
                return 0.8
                
        class BaseSource:
            def __init__(self, name, *args, **kwargs):
                self.name = name
            
            def search(self, *args, **kwargs):
                return []
            
            def get_document(self, *args, **kwargs):
                return {}


@pytest.fixture
def timer():
    """
    A timer fixture that measures the execution time of a code block.
    
    Example:
        def test_example(timer):
            with timer("operation_name"):
                # Code to measure
                ...
    """
    @contextmanager
    def _timer(name):
        start_time = time.time()
        yield
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"{name}: {elapsed:.6f} seconds")
    
    return _timer


@pytest.fixture
def performance_threshold():
    """
    Returns performance thresholds for different operations.
    
    This fixture provides expected maximum execution times for various operations,
    allowing tests to assert that performance meets requirements.
    """
    return {
        # SearchManager thresholds (in seconds)
        "search_query_small": 0.1,      # Small query search
        "search_query_medium": 0.5,     # Medium query search
        "search_query_large": 1.0,      # Large query search
        "search_filter": 0.05,          # Result filtering
        "search_sort": 0.05,            # Result sorting
        
        # SourceManager thresholds (in seconds)
        "source_register": 0.01,        # Registering a source
        "source_search_single": 0.1,    # Single source search
        "source_search_multiple": 0.5,  # Multiple source search
        
        # QualityAssessor thresholds (in seconds)
        "quality_assess_single": 0.01,  # Assessing a single result
        "quality_assess_batch": 0.1,    # Assessing a batch of results
        "quality_filter": 0.05,         # Filtering by quality
    }


@pytest.fixture
def memory_thresholds():
    """
    Returns memory usage thresholds for different operations.
    
    This fixture provides expected maximum memory usage for various operations,
    allowing tests to assert that memory usage meets requirements.
    """
    return {
        # SearchManager thresholds (in MB)
        "search_results_small": 1,      # 10 results
        "search_results_medium": 5,     # 100 results
        "search_results_large": 20,     # 1000 results
        
        # SourceManager thresholds (in MB)
        "source_small": 1,              # 10 sources
        "source_medium": 5,             # 50 sources
        "source_large": 10,             # 100 sources
        
        # QualityAssessor thresholds (in MB)
        "quality_results_small": 1,     # 10 results
        "quality_results_medium": 5,    # 100 results
        "quality_results_large": 20,    # 1000 results
    }


class MockSource(BaseSource):
    """Mock source implementation for benchmark testing."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.search_results = config.get('search_results', [])
        self.documents = config.get('documents', {})
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Return mock search results."""
        results = self.search_results[:limit]
        for result in results:
            result['query'] = query
        return results
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Return a mock document."""
        return self.documents.get(document_id, {})


@pytest.fixture
def benchmark_source_manager():
    """Return a source manager for benchmark testing."""
    # Create search results
    search_results = []
    for i in range(100):  # 100 results
        search_results.append({
            'id': f'mock1:{i}',
            'title': f'Mock Result {i}',
            'snippet': f'This is mock result {i} with some additional context to make it more realistic.'
        })
    
    # Create documents
    documents = {}
    for i in range(100):
        documents[f'mock1:{i}'] = {
            'id': f'mock1:{i}',
            'content': f'Full content of mock result {i}. ' + ''.join(random.choices(string.ascii_letters + ' ', k=1000))
        }
    
    config = {
        'max_workers': 4,
        'default_sources': ['mock1', 'mock2', 'mock3'],
        'sources': {
            'mock1': {
                'type': 'mock',
                'enabled': True,
                'search_results': search_results[:30],
                'documents': {k: documents[k] for k in list(documents.keys())[:30]}
            },
            'mock2': {
                'type': 'mock',
                'enabled': True,
                'search_results': search_results[30:60],
                'documents': {k: documents[k] for k in list(documents.keys())[30:60]}
            },
            'mock3': {
                'type': 'mock',
                'enabled': True,
                'search_results': search_results[60:90],
                'documents': {k: documents[k] for k in list(documents.keys())[60:90]}
            }
        }
    }
    
    # Patch the _register_source method to use our MockSource
    with patch('research_orchestrator.information_gathering.source_manager.SourceManager._register_source') as mock_register:
        source_manager = SourceManager(config)
        # Replace the mocked method with our implementation
        source_manager._register_source = lambda source_id, config: _mock_register_source(source_manager, source_id, config)
        # Register our test sources
        for source_id, source_config in config['sources'].items():
            if source_config.get('enabled', True):
                source_manager._register_source(source_id, source_config)
    
    return source_manager


def _mock_register_source(source_manager, source_id, config):
    """Helper to register a mock source."""
    source = MockSource(source_id, config)
    source_manager.sources[source_id] = source


@pytest.fixture
def benchmark_quality_assessor():
    """Return a quality assessor for benchmark testing."""
    config = {
        'metric_weights': {
            'relevance': 0.4,
            'recency': 0.2,
            'authority': 0.2,
            'completeness': 0.2
        }
    }
    return QualityAssessor(config)


@pytest.fixture
def benchmark_search_manager(benchmark_source_manager, benchmark_quality_assessor):
    """Return a search manager for benchmark testing."""
    search_manager = SearchManager({})
    search_manager.source_manager = benchmark_source_manager
    search_manager.quality_assessor = benchmark_quality_assessor
    return search_manager


@pytest.fixture
def small_query():
    """Return a small query."""
    return "artificial intelligence"


@pytest.fixture
def medium_query():
    """Return a medium query."""
    return "recent advancements in large language models and their applications in natural language processing"


@pytest.fixture
def large_query():
    """Return a large query."""
    return "comprehensive analysis of recent developments in transformer-based large language models including attention mechanisms, parameter efficiency techniques, training methodologies, fine-tuning approaches, and applications in various domains such as natural language processing, computer vision, and multimodal understanding"


@pytest.fixture
def very_large_query():
    """Return a very large query."""
    # Generate a 5KB query
    base_query = "transformer architecture large language models neural networks deep learning attention mechanisms parameter sharing adapter layers low-rank approximations quantization knowledge distillation vision transformers multimodal models contrastive learning self-supervised learning fine-tuning prompt engineering retrieval augmented generation chain of thought reasoning"
    words = base_query.split()
    expanded_query = " ".join([word for _ in range(50) for word in words])
    return expanded_query


@pytest.fixture
def small_results_set():
    """Return a small set of results (10 items)."""
    results = []
    for i in range(10):
        results.append({
            'id': f'test:{i}',
            'title': f'Result {i}',
            'snippet': f'This is result {i}',
            'url': f'https://example.com/result{i}',
            'date': f'2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'
        })
    return results


@pytest.fixture
def medium_results_set():
    """Return a medium set of results (100 items)."""
    results = []
    for i in range(100):
        results.append({
            'id': f'test:{i}',
            'title': f'Result {i}',
            'snippet': f'This is result {i}',
            'url': f'https://example.com/result{i}',
            'date': f'2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'
        })
    return results


@pytest.fixture
def large_results_set():
    """Return a large set of results (1000 items)."""
    results = []
    for i in range(1000):
        results.append({
            'id': f'test:{i}',
            'title': f'Result {i}',
            'snippet': f'This is result {i}',
            'url': f'https://example.com/result{i}',
            'date': f'2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'
        })
    return results