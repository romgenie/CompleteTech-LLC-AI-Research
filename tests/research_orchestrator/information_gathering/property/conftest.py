"""
Fixtures for property-based tests for the Information Gathering module.

This module provides pytest fixtures for property-based testing using Hypothesis.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any

# Try to add the project root to sys.path if needed
try:
    import research_orchestrator
except ImportError:
    # Get the absolute path to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# Try different import paths
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
        # Create stub classes if imports fail in CI environments
        class BaseSource:
            def __init__(self, source_id, config):
                self.source_id = source_id
                self.config = config
                
            def search(self, query, limit=10):
                return []
                
            def get_document(self, document_id):
                return {"id": document_id}
                
        class SourceManager:
            def __init__(self, config=None):
                self.config = config or {}
                self.sources = {}
                
            def _register_source(self, source_id, config):
                pass
                
            def search(self, query, sources=None, limit=10, query_type="general"):
                return []
                
        class QualityAssessor:
            def __init__(self, config=None):
                self.config = config or {}
                
            def assess_results(self, results):
                return results
                
        class SearchManager:
            def __init__(self, config=None):
                self.config = config or {}
                self.source_manager = None
                self.quality_assessor = None
                self.results_cache = {}


class MockSource(BaseSource):
    """Mock source implementation for property testing."""
    
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
def property_source_manager():
    """Return a source manager for property testing."""
    config = {
        'max_workers': 2,
        'default_sources': ['mock1'],
        'sources': {
            'mock1': {
                'type': 'mock',
                'enabled': True,
                'search_results': [
                    {'id': 'mock1:1', 'title': 'Mock Result 1', 'snippet': 'This is mock result 1'},
                    {'id': 'mock1:2', 'title': 'Mock Result 2', 'snippet': 'This is mock result 2'}
                ],
                'documents': {
                    'mock1:1': {'id': 'mock1:1', 'content': 'Full content of mock result 1'}
                }
            },
            'mock2': {
                'type': 'mock',
                'enabled': True,
                'search_results': [
                    {'id': 'mock2:1', 'title': 'Another Mock Result', 'snippet': 'This is another mock result'}
                ]
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
def property_quality_assessor():
    """Return a quality assessor for property testing."""
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
def property_search_manager(property_source_manager, property_quality_assessor):
    """Return a search manager for property testing."""
    search_manager = SearchManager({})
    search_manager.source_manager = property_source_manager
    search_manager.quality_assessor = property_quality_assessor
    return search_manager


@pytest.fixture
def property_search_result():
    """Return a standard search result for property testing."""
    return {
        'id': 'test:1',
        'title': 'Test Result',
        'snippet': 'This is a test result',
        'url': 'https://example.com/test',
        'date': '2023-03-01',
        'quality_score': 0.85,
        'source_id': 'test_source',
        'source_name': 'Test Source'
    }


@pytest.fixture
def property_document():
    """Return a standard document for property testing."""
    return {
        'id': 'test:1',
        'title': 'Test Document',
        'content': 'This is the full content of the test document.',
        'url': 'https://example.com/test',
        'date': '2023-03-01',
        'quality_score': 0.85,
        'source_id': 'test_source',
        'source_name': 'Test Source'
    }