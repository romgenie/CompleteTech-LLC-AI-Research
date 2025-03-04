"""
Tests for the Information Gathering module of the Research Orchestration Framework.

This module tests the functionality of the SearchManager, SourceManager, QualityAssessor,
and various source implementations.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from research_orchestrator.information_gathering.search_manager import SearchManager
from research_orchestrator.information_gathering.source_manager import SourceManager
from research_orchestrator.information_gathering.quality_assessor import QualityAssessor
from research_orchestrator.information_gathering.sources.base_source import BaseSource
from research_orchestrator.information_gathering.sources.academic import AcademicSource
from research_orchestrator.information_gathering.sources.web import WebSource
from research_orchestrator.information_gathering.sources.code import CodeSource
from research_orchestrator.information_gathering.sources.ai import AISource


class MockSource(BaseSource):
    """Mock source implementation for testing."""
    
    def __init__(self, source_id, config):
        super().__init__(source_id, config)
        self.source_type = config.get('type', 'mock')
        self.search_results = config.get('search_results', [])
        self.documents = config.get('documents', {})
    
    def search(self, query, limit=10):
        """Return mock search results."""
        results = self.search_results[:limit]
        for result in results:
            result['query'] = query
        return results
    
    def get_document(self, document_id):
        """Return a mock document."""
        return self.documents.get(document_id, {})


class TestSourceManager(unittest.TestCase):
    """Tests for the SourceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
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
                'disabled': {
                    'type': 'mock',
                    'enabled': False,
                    'search_results': []
                }
            }
        }
        
        # Patch the _register_source method to use our MockSource
        with patch('research_orchestrator.information_gathering.source_manager.SourceManager._register_source') as mock_register:
            self.source_manager = SourceManager(self.config)
            # Replace the mocked method with our implementation
            self.source_manager._register_source = self._mock_register_source
            # Register our test sources
            for source_id, source_config in self.config['sources'].items():
                if source_config.get('enabled', True):
                    self.source_manager._register_source(source_id, source_config)
    
    def _mock_register_source(self, source_id, config):
        """Mock implementation of _register_source."""
        source = MockSource(source_id, config)
        self.source_manager.sources[source_id] = source
    
    def test_get_enabled_sources(self):
        """Test that get_enabled_sources returns all enabled sources."""
        enabled_sources = self.source_manager.get_enabled_sources()
        self.assertEqual(set(enabled_sources), {'mock1', 'mock2'})
        self.assertNotIn('disabled', enabled_sources)
    
    def test_search_all_sources(self):
        """Test searching across all sources."""
        results = self.source_manager.search('test query')
        self.assertEqual(len(results), 3)  # 2 from mock1, 1 from mock2
        
        # Check that all results have the correct query
        for result in results:
            self.assertEqual(result['query'], 'test query')
            
    def test_search_specific_source(self):
        """Test searching a specific source."""
        results = self.source_manager.search('test query', sources=['mock1'])
        self.assertEqual(len(results), 2)  # Only results from mock1
        self.assertEqual(results[0]['id'], 'mock1:1')
        self.assertEqual(results[1]['id'], 'mock1:2')
    
    def test_get_document(self):
        """Test retrieving a document."""
        document = self.source_manager.get_document('mock1:1', 'mock1')
        self.assertEqual(document['id'], 'mock1:1')
        self.assertEqual(document['content'], 'Full content of mock result 1')


class TestQualityAssessor(unittest.TestCase):
    """Tests for the QualityAssessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'metric_weights': {
                'relevance': 0.4,
                'recency': 0.2,
                'authority': 0.2,
                'completeness': 0.2
            }
        }
        self.quality_assessor = QualityAssessor(self.config)
        
        self.test_results = [
            {
                'id': 'test:1',
                'title': 'Recent High Quality Result',
                'snippet': 'This is a recent, authoritative, complete result about AI research',
                'url': 'https://example.edu/research',
                'date': '2023-01-15',
                'query': 'AI research',
                'citation_count': 120,
                'content_length': 6000
            },
            {
                'id': 'test:2',
                'title': 'Old Low Quality Result',
                'snippet': 'Brief result',
                'url': 'https://example.com/old',
                'date': '2010-05-20',
                'query': 'AI research'
            }
        ]
    
    def test_assess_results(self):
        """Test quality assessment of results."""
        assessed_results = self.quality_assessor.assess_results(self.test_results)
        
        # Check that quality scores were added
        self.assertIn('quality_score', assessed_results[0])
        self.assertIn('relevance_score', assessed_results[0])
        self.assertIn('recency_score', assessed_results[0])
        self.assertIn('authority_score', assessed_results[0])
        self.assertIn('completeness_score', assessed_results[0])
        
        # Check that scores are between 0 and 1
        for result in assessed_results:
            self.assertGreaterEqual(result['quality_score'], 0.0)
            self.assertLessEqual(result['quality_score'], 1.0)
        
        # First result should have higher quality than second
        self.assertGreater(assessed_results[0]['quality_score'], assessed_results[1]['quality_score'])
        
        # Specifically check recency scoring
        self.assertGreater(assessed_results[0]['recency_score'], assessed_results[1]['recency_score'])
        
        # Specifically check authority scoring
        self.assertGreater(assessed_results[0]['authority_score'], assessed_results[1]['authority_score'])


class TestSearchManager(unittest.TestCase):
    """Tests for the SearchManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock source manager
        self.mock_source_manager = MagicMock()
        self.mock_source_manager.search.return_value = [
            {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1', 'query': 'test query'},
            {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2', 'query': 'test query'}
        ]
        self.mock_source_manager.get_document.return_value = {
            'id': 'test:1', 'content': 'Full content of result 1'
        }
        
        # Create a mock quality assessor
        self.mock_quality_assessor = MagicMock()
        self.mock_quality_assessor.assess_results.return_value = [
            {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1', 'query': 'test query', 'quality_score': 0.9},
            {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2', 'query': 'test query', 'quality_score': 0.7}
        ]
        
        # Initialize the search manager with mocks
        self.search_manager = SearchManager({})
        self.search_manager.source_manager = self.mock_source_manager
        self.search_manager.quality_assessor = self.mock_quality_assessor
    
    def test_search(self):
        """Test search functionality."""
        results = self.search_manager.search('test query', limit=5)
        
        # Check that source manager was called
        self.mock_source_manager.search.assert_called_once_with('test query', None, 5, 'general')
        
        # Check that quality assessor was called
        self.mock_quality_assessor.assess_results.assert_called_once()
        
        # Check that results were sorted by quality score
        self.assertEqual(results[0]['id'], 'test:1')  # Higher quality should be first
        self.assertEqual(results[1]['id'], 'test:2')
    
    def test_get_document(self):
        """Test document retrieval."""
        document = self.search_manager.get_document('test:1', 'test_source')
        
        # Check that source manager was called
        self.mock_source_manager.get_document.assert_called_once_with('test:1', 'test_source')
        
        # Check that we got the right document
        self.assertEqual(document['id'], 'test:1')
        self.assertEqual(document['content'], 'Full content of result 1')


class TestSourceImplementations(unittest.TestCase):
    """Tests for the different source implementations."""
    
    def test_academic_source_init(self):
        """Test initialization of AcademicSource."""
        config = {
            'provider': 'arxiv',
            'api_key': 'test_key',
            'rate_limit': 30,
            'timeout': 10
        }
        source = AcademicSource('academic_test', config)
        
        self.assertEqual(source.source_id, 'academic_test')
        self.assertEqual(source.source_type, 'academic')
        self.assertEqual(source.provider, 'arxiv')
        self.assertEqual(source.api_key, 'test_key')
        self.assertEqual(source.rate_limit, 30)
        self.assertEqual(source.timeout, 10)
        self.assertTrue(source.base_url.startswith('http'))
    
    def test_web_source_init(self):
        """Test initialization of WebSource."""
        config = {
            'provider': 'serper',
            'api_key': 'test_key',
            'rate_limit': 30,
            'timeout': 10
        }
        source = WebSource('web_test', config)
        
        self.assertEqual(source.source_id, 'web_test')
        self.assertEqual(source.source_type, 'web')
        self.assertEqual(source.provider, 'serper')
        self.assertEqual(source.api_key, 'test_key')
        self.assertEqual(source.rate_limit, 30)
        self.assertEqual(source.timeout, 10)
        self.assertTrue(source.base_url.startswith('http'))
    
    def test_code_source_init(self):
        """Test initialization of CodeSource."""
        config = {
            'provider': 'github',
            'api_key': 'test_key',
            'rate_limit': 30,
            'timeout': 10
        }
        source = CodeSource('code_test', config)
        
        self.assertEqual(source.source_id, 'code_test')
        self.assertEqual(source.source_type, 'code')
        self.assertEqual(source.provider, 'github')
        self.assertEqual(source.api_key, 'test_key')
        self.assertEqual(source.rate_limit, 30)
        self.assertEqual(source.timeout, 10)
        self.assertTrue(source.base_url.startswith('http'))
    
    def test_ai_source_init(self):
        """Test initialization of AISource."""
        config = {
            'provider': 'openai',
            'api_key': 'test_key',
            'model': 'gpt-4',
            'max_tokens': 1000,
            'temperature': 0.7,
            'system_prompt': 'You are a helpful assistant.',
            'rate_limit': 30,
            'timeout': 10
        }
        source = AISource('ai_test', config)
        
        self.assertEqual(source.source_id, 'ai_test')
        self.assertEqual(source.source_type, 'ai')
        self.assertEqual(source.provider, 'openai')
        self.assertEqual(source.api_key, 'test_key')
        self.assertEqual(source.model, 'gpt-4')
        self.assertEqual(source.max_tokens, 1000)
        self.assertEqual(source.temperature, 0.7)
        self.assertEqual(source.system_prompt, 'You are a helpful assistant.')
        self.assertEqual(source.rate_limit, 30)
        self.assertEqual(source.timeout, 10)
        self.assertTrue(source.base_url.startswith('http'))


if __name__ == '__main__':
    unittest.main()