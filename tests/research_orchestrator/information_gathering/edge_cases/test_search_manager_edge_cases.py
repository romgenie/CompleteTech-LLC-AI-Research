"""
Edge case tests for the SearchManager in the Information Gathering module.

This module contains tests for edge cases and error handling in the SearchManager.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
import logging

# Mark all tests in this module as edge case tests and search manager related tests
pytestmark = [
    pytest.mark.edge_case,
    pytest.mark.information_gathering,
    pytest.mark.search_manager,
    pytest.mark.medium
]

from research_orchestrator.information_gathering.search_manager import SearchManager


@pytest.mark.empty
def test_empty_query_handling(edge_case_search_manager, empty_query):
    """Test handling of empty search queries."""
    # Search with empty query
    results = edge_case_search_manager.search(empty_query)
    
    # Should handle empty query gracefully (return results or empty list)
    assert isinstance(results, list)


@pytest.mark.large
def test_very_long_query_handling(edge_case_search_manager, very_long_query):
    """Test handling of very long search queries."""
    # Search with very long query
    results = edge_case_search_manager.search(very_long_query)
    
    # Should handle long query gracefully
    assert isinstance(results, list)
    
    # Verify cache uses a truncated key for very long queries
    cache_keys = list(edge_case_search_manager.results_cache.keys())
    assert all(len(key) < 1000 for key in cache_keys)


@pytest.mark.special_chars
def test_special_character_query_handling(edge_case_search_manager, query_with_special_characters):
    """Test handling of queries with special characters."""
    # Search with query containing special characters
    results = edge_case_search_manager.search(query_with_special_characters)
    
    # Should handle special characters gracefully
    assert isinstance(results, list)


@pytest.mark.error
def test_source_manager_error_handling(edge_case_search_manager):
    """Test handling of errors from the source manager."""
    # Mock source_manager to raise an exception
    edge_case_search_manager.source_manager.search.side_effect = ConnectionError("Mock connection error")
    
    # Search should handle the error gracefully
    results = edge_case_search_manager.search("test query")
    
    # Should return an empty list when source_manager raises an error
    assert isinstance(results, list)
    assert len(results) == 0
    
    # Restore normal behavior
    edge_case_search_manager.source_manager.search.side_effect = None


@pytest.mark.error
def test_quality_assessor_error_handling(edge_case_search_manager):
    """Test handling of errors from the quality assessor."""
    # Setup source_manager to return normal results
    edge_case_search_manager.source_manager.search.return_value = [
        {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1'},
        {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2'}
    ]
    
    # Mock quality_assessor to raise an exception
    edge_case_search_manager.quality_assessor.assess_results.side_effect = Exception("Mock quality error")
    
    # Search should handle the error gracefully
    results = edge_case_search_manager.search("test query")
    
    # Should return the original results without quality assessment when quality_assessor raises an error
    assert isinstance(results, list)
    assert len(results) == 2
    
    # Restore normal behavior
    edge_case_search_manager.quality_assessor.assess_results.side_effect = None


@pytest.mark.malformed
def test_malformed_query_handling(edge_case_search_manager, malformed_query):
    """Test handling of malformed queries with invalid characters."""
    # Search with malformed query
    results = edge_case_search_manager.search(malformed_query)
    
    # Should handle malformed query gracefully
    assert isinstance(results, list)


@pytest.mark.error
def test_document_retrieval_error_handling(edge_case_search_manager):
    """Test handling of errors during document retrieval."""
    # Mock source_manager.get_document to raise an exception
    edge_case_search_manager.source_manager.get_document.side_effect = Exception("Mock document error")
    
    # Attempt to retrieve a document
    with pytest.raises(Exception):
        document = edge_case_search_manager.get_document("test:1", "test_source")
    
    # Restore normal behavior
    edge_case_search_manager.source_manager.get_document.side_effect = None


@pytest.mark.filter
def test_invalid_filter_criteria_handling(edge_case_search_manager):
    """Test handling of invalid filter criteria."""
    # Search with invalid filter criteria
    invalid_criteria = {"invalid_key": "invalid_value"}
    results = edge_case_search_manager.search("test query", filter_criteria=invalid_criteria)
    
    # Should ignore invalid filter criteria and return results
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.timeout
def test_search_caching_behavior(edge_case_search_manager):
    """Test that search results are properly cached and reused."""
    # Clear the cache to start fresh
    edge_case_search_manager.clear_cache()
    
    # Mock source_manager to track calls
    original_search = edge_case_search_manager.source_manager.search
    edge_case_search_manager.source_manager.search = MagicMock(side_effect=original_search)
    
    # First search should hit the source_manager
    results1 = edge_case_search_manager.search("test query")
    assert edge_case_search_manager.source_manager.search.call_count == 1
    
    # Second search with same query should use cache
    results2 = edge_case_search_manager.search("test query")
    assert edge_case_search_manager.source_manager.search.call_count == 1  # Still 1
    
    # Verify both results are identical
    assert results1 == results2
    
    # Restore original method
    edge_case_search_manager.source_manager.search = original_search


@pytest.mark.concurrent
def test_parallel_search_isolation(edge_case_search_manager):
    """Test that parallel searches with different queries don't interfere with each other."""
    # Clear the cache to start fresh
    edge_case_search_manager.clear_cache()
    
    # Setup source_manager to return different results for different queries
    def mock_search(query, *args, **kwargs):
        if query == "query1":
            return [{'id': 'test:1', 'title': 'Result 1 for query1', 'query': query}]
        else:
            return [{'id': 'test:2', 'title': 'Result 2 for query2', 'query': query}]
    
    edge_case_search_manager.source_manager.search = MagicMock(side_effect=mock_search)
    
    # Run two different searches
    results1 = edge_case_search_manager.search("query1")
    results2 = edge_case_search_manager.search("query2")
    
    # Verify the results are different and correspond to the correct queries
    assert results1[0]['title'] == 'Result 1 for query1'
    assert results1[0]['query'] == 'query1'
    assert results2[0]['title'] == 'Result 2 for query2'
    assert results2[0]['query'] == 'query2'


@pytest.mark.empty
def test_empty_results_handling(edge_case_search_manager):
    """Test handling of empty search results from the source manager."""
    # Setup source_manager to return empty results
    edge_case_search_manager.source_manager.search.return_value = []
    
    # Search should handle empty results gracefully
    results = edge_case_search_manager.search("test query")
    
    # Should return an empty list
    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.invalid
def test_invalid_source_handling(edge_case_search_manager):
    """Test handling of invalid source specification."""
    # Search with invalid sources
    results = edge_case_search_manager.search("test query", sources=["invalid_source"])
    
    # Should handle invalid sources gracefully
    assert isinstance(results, list)


@pytest.mark.limit
def test_zero_limit_handling(edge_case_search_manager):
    """Test handling of zero search result limit."""
    # Search with limit=0
    results = edge_case_search_manager.search("test query", limit=0)
    
    # Should return an empty list for limit=0
    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.limit
def test_negative_limit_handling(edge_case_search_manager):
    """Test handling of negative search result limit."""
    # Search with negative limit (should be treated as invalid and use default)
    results = edge_case_search_manager.search("test query", limit=-10)
    
    # Should handle negative limit gracefully (use default or treat as 0)
    assert isinstance(results, list)