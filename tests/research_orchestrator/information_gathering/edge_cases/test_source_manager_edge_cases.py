"""
Edge case tests for the SourceManager in the Information Gathering module.

This module contains tests for edge cases and error handling in the SourceManager.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
import logging
from concurrent.futures import ThreadPoolExecutor

# Mark all tests in this module as edge case tests and source manager related tests
pytestmark = [
    pytest.mark.edge_case,
    pytest.mark.information_gathering,
    pytest.mark.source_manager,
    pytest.mark.medium
]

from src.research_orchestrator.information_gathering.source_manager import SourceManager


@pytest.mark.empty
def test_empty_query_handling(edge_case_source_manager, empty_query):
    """Test handling of empty search queries in source manager."""
    # Search with empty query
    results = edge_case_source_manager.search(empty_query)
    
    # Should handle empty query gracefully (return results or empty list)
    assert isinstance(results, list)


@pytest.mark.error
def test_source_error_handling(edge_case_source_manager):
    """Test handling of errors from individual sources."""
    # Search using all sources including ones that raise errors
    results = edge_case_source_manager.search("test query", sources=["mock1", "mock2", "error_source"])
    
    # Should handle source errors gracefully and return results from working sources
    assert isinstance(results, list)
    assert len(results) > 0  # Should have results from mock1 and mock2


@pytest.mark.timeout
def test_source_timeout_handling(edge_case_source_manager):
    """Test handling of timeout errors from sources."""
    # Search using the timeout source
    results = edge_case_source_manager.search("test query", sources=["timeout_source"])
    
    # Should handle timeout errors gracefully
    assert isinstance(results, list)
    assert len(results) == 0  # No results from the timeout source


@pytest.mark.special_chars
def test_special_character_query_handling(edge_case_source_manager, query_with_special_characters):
    """Test handling of queries with special characters in source manager."""
    # Search with query containing special characters
    results = edge_case_source_manager.search(query_with_special_characters)
    
    # Should handle special characters gracefully
    assert isinstance(results, list)


@pytest.mark.error
def test_document_retrieval_error_handling(edge_case_source_manager):
    """Test handling of errors during document retrieval."""
    # Create a source that raises an error on document retrieval
    source_id = "error_doc_source"
    source_config = {
        'type': 'mock',
        'enabled': True,
        'raise_error_on_document': True,
        'error_type': Exception,
        'error_message': 'Document error'
    }
    
    # Register the source
    edge_case_source_manager._register_source(source_id, source_config)
    
    # Attempt to retrieve a document
    with pytest.raises(Exception):
        document = edge_case_source_manager.get_document("any_id", source_id)


@pytest.mark.invalid
def test_invalid_source_id_handling(edge_case_source_manager):
    """Test handling of invalid source ID during document retrieval."""
    # Attempt to retrieve a document from a non-existent source
    with pytest.raises(KeyError):
        document = edge_case_source_manager.get_document("test:1", "nonexistent_source")


@pytest.mark.invalid
def test_invalid_document_id_handling(edge_case_source_manager):
    """Test handling of invalid document ID."""
    # Attempt to retrieve a non-existent document
    document = edge_case_source_manager.get_document("nonexistent_id", "mock1")
    
    # Should return an empty dictionary or some default value
    assert isinstance(document, dict)
    assert len(document) == 0


@pytest.mark.concurrent
def test_thread_pool_executor_failure(edge_case_source_manager):
    """Test handling of ThreadPoolExecutor initialization failure."""
    # Patch ThreadPoolExecutor to raise an exception
    original_executor = ThreadPoolExecutor
    
    def mock_executor_init(*args, **kwargs):
        raise RuntimeError("Mock ThreadPoolExecutor error")
    
    # Apply patch
    patch_path = 'research_orchestrator.information_gathering.source_manager.ThreadPoolExecutor'
    with patch(patch_path, MagicMock(side_effect=mock_executor_init)):
        # Search should handle ThreadPoolExecutor failure gracefully
        results = edge_case_source_manager.search("test query")
        
        # Should return an empty list on executor failure
        assert isinstance(results, list)
        assert len(results) == 0


@pytest.mark.concurrent
def test_future_exception_handling(edge_case_source_manager):
    """Test handling of exceptions raised by futures in as_completed."""
    # Patch as_completed to raise an exception
    original_as_completed = edge_case_source_manager.search.__globals__['as_completed']
    
    def mock_as_completed(*args, **kwargs):
        raise RuntimeError("Mock as_completed error")
    
    # Apply patch
    patch_path = 'research_orchestrator.information_gathering.source_manager.as_completed'
    with patch(patch_path, mock_as_completed):
        # Search should handle as_completed failure gracefully
        results = edge_case_source_manager.search("test query")
        
        # Should return an empty list on as_completed failure
        assert isinstance(results, list)
        assert len(results) == 0


@pytest.mark.empty
def test_no_sources_handling(edge_case_source_manager):
    """Test handling of search with no sources available."""
    # Clear all sources
    original_sources = edge_case_source_manager.sources
    edge_case_source_manager.sources = {}
    
    # Search with no sources
    results = edge_case_source_manager.search("test query")
    
    # Should return an empty list
    assert isinstance(results, list)
    assert len(results) == 0
    
    # Restore original sources
    edge_case_source_manager.sources = original_sources


@pytest.mark.invalid
def test_source_type_handling():
    """Test handling of invalid source types during initialization."""
    config = {
        'sources': {
            'invalid': {
                'type': 'invalid_type',
                'enabled': True
            }
        }
    }
    
    # Create source manager with invalid source type
    source_manager = SourceManager(config)
    
    # Should initialize without errors, but skip the invalid source
    assert 'invalid' not in source_manager.sources


@pytest.mark.invalid
def test_custom_source_handling():
    """Test handling of custom sources with missing required fields."""
    config = {
        'sources': {
            'custom': {
                'type': 'custom',
                'enabled': True
                # Missing required module_path and class_name
            }
        }
    }
    
    # Create source manager with invalid custom source
    source_manager = SourceManager(config)
    
    # Should initialize without errors, but skip the invalid custom source
    assert 'custom' not in source_manager.sources


@pytest.mark.filter
def test_search_type_filtering(edge_case_source_manager):
    """Test filtering of sources based on search type."""
    # Mock sources with different types
    edge_case_source_manager.sources["mock1"].source_type = "academic"
    edge_case_source_manager.sources["mock2"].source_type = "web"
    
    # Search with academic search type
    results = edge_case_source_manager.search("test query", search_type="academic")
    
    # Should only get results from academic sources
    source_ids = set()
    for result in results:
        if 'source_id' in result:
            source_ids.add(result['source_id'])
    
    assert "mock1" in source_ids
    assert "mock2" not in source_ids
    
    # Restore original source types
    edge_case_source_manager.sources["mock1"].source_type = "mock"
    edge_case_source_manager.sources["mock2"].source_type = "mock"