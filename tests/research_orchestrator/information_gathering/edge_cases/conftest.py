"""
Fixtures for edge case tests for the Information Gathering module.

This module provides pytest fixtures for testing edge cases and error handling.
"""

import pytest
import os
import tempfile
import json
import string
import random
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any

from research_orchestrator.information_gathering.search_manager import SearchManager
from research_orchestrator.information_gathering.source_manager import SourceManager
from research_orchestrator.information_gathering.quality_assessor import QualityAssessor
from research_orchestrator.information_gathering.sources.base_source import BaseSource


class MockSource(BaseSource):
    """Mock source implementation for edge case testing."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        super().__init__(source_id, config)
        self.search_results = config.get('search_results', [])
        self.documents = config.get('documents', {})
        self.raise_error_on_search = config.get('raise_error_on_search', False)
        self.raise_error_on_document = config.get('raise_error_on_document', False)
        self.error_type = config.get('error_type', Exception)
        self.error_message = config.get('error_message', 'Mock error')
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Return mock search results or raise an error if configured."""
        if self.raise_error_on_search:
            raise self.error_type(self.error_message)
        
        results = self.search_results[:limit]
        for result in results:
            result['query'] = query
        return results
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Return a mock document or raise an error if configured."""
        if self.raise_error_on_document:
            raise self.error_type(self.error_message)
        
        return self.documents.get(document_id, {})


@pytest.fixture
def empty_query():
    """Return an empty query string."""
    return ""


@pytest.fixture
def very_long_query():
    """Return a very long query string."""
    # Generate a 10KB query
    chars = string.ascii_letters + string.digits + ' ' * 5
    return ''.join(random.choices(chars, k=10 * 1024))


@pytest.fixture
def malformed_query():
    """Return a malformed query with special characters."""
    return "query with \0 null \t tab \r return \n newline characters"


@pytest.fixture
def query_with_special_characters():
    """Return a query with special characters and multiple languages."""
    return """
    Query with special characters:
    • Bullets and symbols: ©®™•★☆♦♣♠♥
    • Emoji: 😀🤣😎👍❤️🔥
    • Languages: مرحبا بالعالم 你好，世界 こんにちは世界 Привет, мир
    """


@pytest.fixture
def edge_case_search_manager():
    """Return a search manager for edge case testing."""
    search_manager = SearchManager({})
    
    # Create a mock source manager
    source_manager = MagicMock()
    source_manager.search.return_value = [
        {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1', 'query': 'test query'},
        {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2', 'query': 'test query'}
    ]
    source_manager.get_document.return_value = {
        'id': 'test:1', 'content': 'Full content of result 1'
    }
    
    # Create a mock quality assessor
    quality_assessor = MagicMock()
    quality_assessor.assess_results.return_value = [
        {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1', 'query': 'test query', 'quality_score': 0.9},
        {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2', 'query': 'test query', 'quality_score': 0.7}
    ]
    
    # Assign mocks to search manager
    search_manager.source_manager = source_manager
    search_manager.quality_assessor = quality_assessor
    
    return search_manager


@pytest.fixture
def edge_case_source_manager():
    """Return a source manager for edge case testing."""
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
            },
            'error_source': {
                'type': 'mock',
                'enabled': True,
                'raise_error_on_search': True,
                'error_type': ConnectionError,
                'error_message': 'Connection error'
            },
            'timeout_source': {
                'type': 'mock',
                'enabled': True,
                'raise_error_on_search': True,
                'error_type': TimeoutError,
                'error_message': 'Timeout error'
            },
            'disabled': {
                'type': 'mock',
                'enabled': False,
                'search_results': []
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
def edge_case_quality_assessor():
    """Return a quality assessor for edge case testing."""
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
def malformed_json_file():
    """Create and return path to a malformed JSON file."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.write(b'{"this": "is", "not": "valid", json')
        file_path = f.name
    
    yield file_path
    
    # Clean up
    os.unlink(file_path)


@pytest.fixture
def empty_results():
    """Return an empty results list."""
    return []


@pytest.fixture
def results_without_quality_scores():
    """Return a list of results without quality scores."""
    return [
        {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1'},
        {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2'}
    ]


@pytest.fixture
def results_with_duplicate_ids():
    """Return a list of results with duplicate IDs."""
    return [
        {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1'},
        {'id': 'test:1', 'title': 'Duplicate Result', 'snippet': 'This is a duplicate result'},
        {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2'}
    ]