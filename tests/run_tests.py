"""
Simple test runner script for the AI Research Integration Project.

This script runs the simplified tests for the TDAG adapter and Information Gathering module.
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.research_orchestrator.adapters.tdag_adapter import TDAGAdapter
from src.research_orchestrator.information_gathering.search_manager import SearchManager
from src.research_orchestrator.information_gathering.quality_assessor import QualityAssessor


class TestTDAGAdapter(unittest.TestCase):
    """Tests for the simplified TDAGAdapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'model_name': 'gpt-4',
            'proxy': None,
            'record_path': None
        }
        self.adapter = TDAGAdapter(self.config)
    
    def test_init(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.model_name, 'gpt-4')
        self.assertIsNone(self.adapter.proxy)
        self.assertIsNone(self.adapter.record_path)
    
    def test_validate_config(self):
        """Test configuration validation."""
        # Valid config
        self.assertTrue(self.adapter.validate_config({'model_name': 'gpt-4'}))
        
        # Invalid config (missing required key)
        self.assertFalse(self.adapter.validate_config({'proxy': None}))
    
    def test_decompose_task(self):
        """Test task decomposition functionality."""
        task = "Research the latest advancements in AI"
        subtasks = self.adapter.decompose_task(task)
        
        # Check that we get the expected subtasks
        self.assertEqual(len(subtasks), 4)  # Should return 4 subtasks
        self.assertIn('subtask_name', subtasks[0])
        self.assertIn('goal', subtasks[0])
    
    def test_create_research_plan(self):
        """Test research plan creation functionality."""
        task = "Create a research plan on quantum computing"
        plan = self.adapter.create_research_plan(task)
        
        # Check that we get a properly structured plan
        self.assertIn('title', plan)
        self.assertIn('steps', plan)
        self.assertEqual(len(plan['steps']), 4)  # Should have 4 steps
        
        # Check the title reflects the task
        self.assertIn('quantum computing', plan['title'].lower())
    
    def test_create_research_plan_with_context(self):
        """Test research plan creation with context."""
        task = "Create a research plan on quantum computing"
        context = {'focus_area': 'quantum algorithms', 'timeframe': '2 weeks'}
        
        # Call the method with context
        plan = self.adapter.create_research_plan(task, context)
        
        # Check that the context was included
        self.assertIn('context', plan)
        self.assertEqual(plan['context'], context)


class TestSearchManager(unittest.TestCase):
    """Tests for the simplified SearchManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {}
        self.search_manager = SearchManager(self.config)
    
    def test_search(self):
        """Test search functionality."""
        # Test with transformer query
        results = self.search_manager.search('transformer neural networks')
        
        # Should get relevant results
        self.assertGreater(len(results), 0)
        self.assertIn('transformer', results[0]['title'].lower())
        
        # Test with generic query
        generic_results = self.search_manager.search('random topic')
        self.assertGreater(len(generic_results), 0)
    
    def test_get_document(self):
        """Test document retrieval."""
        document = self.search_manager.get_document('demo:1', 'demo')
        
        # Check that we got the right document
        self.assertEqual(document['id'], 'demo:1')
        self.assertIn('content', document)
        
        # Check that content is detailed
        self.assertIn('Advances in Transformer Neural Networks', document['title'])
        self.assertIn('Introduction', document['content'])
    
    def test_caching(self):
        """Test that results are cached."""
        query = "transformer test query"
        
        # First search should not be cached
        results1 = self.search_manager.search(query)
        
        # Second search should use cache
        results2 = self.search_manager.search(query)
        
        # Results should be identical
        self.assertEqual(results1, results2)
        
        # Clear cache and search again
        self.search_manager.clear_cache()
        
        # Results should still be the same (our implementation is deterministic)
        results3 = self.search_manager.search(query)
        self.assertEqual(results1, results3)


class TestQualityAssessor(unittest.TestCase):
    """Tests for the simplified QualityAssessor."""
    
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
                'id': 'test:2',
                'title': 'Lower Quality Result',
                'quality_score': 0.7
            },
            {
                'id': 'test:1',
                'title': 'Higher Quality Result',
                'quality_score': 0.9
            }
        ]
    
    def test_assess_results(self):
        """Test quality assessment and sorting of results."""
        assessed_results = self.quality_assessor.assess_results(self.test_results)
        
        # Check that results are sorted by quality score (highest first)
        self.assertEqual(assessed_results[0]['id'], 'test:1')  # Higher quality (0.9)
        self.assertEqual(assessed_results[1]['id'], 'test:2')  # Lower quality (0.7)


if __name__ == '__main__':
    unittest.main()