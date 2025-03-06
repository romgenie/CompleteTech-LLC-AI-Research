"""
Property-based tests for the SourceManager in the Information Gathering module.

This module contains property-based tests using Hypothesis to verify the properties
of the SourceManager's behavior across a wide range of inputs.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings, example, assume
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor

# Mark all tests in this module as property-based tests and source manager related tests
pytestmark = [
    pytest.mark.property,
    pytest.mark.information_gathering,
    pytest.mark.source_manager,
    pytest.mark.medium
]

from src.research_orchestrator.information_gathering.source_manager import SourceManager
from src.research_orchestrator.information_gathering.sources.base_source import BaseSource


# Strategy for generating search queries
@st.composite
def search_query(draw):
    """Strategy for generating search queries."""
    return draw(st.text(min_size=1, max_size=50))


# Strategy for generating source configurations
@st.composite
def source_config(draw):
    """Strategy for generating source configurations."""
    source_type = draw(st.sampled_from(["academic", "web", "code", "ai"]))
    enabled = draw(st.booleans())
    name = draw(st.text(min_size=1, max_size=20))
    
    config = {
        "type": source_type,
        "enabled": enabled,
        "name": name,
        "api_key": "test_key",
        "rate_limit": draw(st.integers(min_value=1, max_value=100)),
        "timeout": draw(st.integers(min_value=1, max_value=60))
    }
    
    if source_type == "academic":
        config["provider"] = draw(st.sampled_from(["arxiv", "pubmed", "semanticscholar"]))
    elif source_type == "web":
        config["provider"] = draw(st.sampled_from(["serper", "serpapi", "tavily"]))
    elif source_type == "code":
        config["provider"] = draw(st.sampled_from(["github", "gitlab", "huggingface"]))
    elif source_type == "ai":
        config["provider"] = draw(st.sampled_from(["openai", "anthropic", "cohere"]))
        config["model"] = draw(st.sampled_from(["gpt-4", "claude-3", "command-r"]))
        config["max_tokens"] = draw(st.integers(min_value=100, max_value=2000))
        config["temperature"] = draw(st.floats(min_value=0.0, max_value=1.0))
    
    return config


@given(query=search_query())
@settings(max_examples=50)
def test_source_manager_search_query_propagation(property_source_manager, query):
    """Test that search queries are properly propagated to all sources."""
    # Search with the query
    results = property_source_manager.search(query)
    
    # Verify the query is propagated to all source results
    for result in results:
        assert 'query' in result
        assert result['query'] == query


@given(
    query=search_query(),
    sources=st.lists(st.sampled_from(["mock1", "mock2"]), min_size=0, max_size=2)
)
@settings(max_examples=25)
def test_source_filtering(property_source_manager, query, sources):
    """Test that source filtering works correctly."""
    # Skip if sources is empty
    assume(len(sources) > 0)
    
    # Search with specific sources
    results = property_source_manager.search(query, sources=sources)
    
    # Verify results only come from the specified sources
    result_sources = {result.get('source_id') for result in results if 'source_id' in result}
    
    # If sources were specified, only those sources should be present
    if sources:
        for source_id in result_sources:
            assert source_id in sources


@given(query=search_query())
@settings(max_examples=25)
def test_source_metadata_addition(property_source_manager, query):
    """Test that source metadata is added to all search results."""
    # Patch the _search_source method to track calls and ensure source metadata is added
    original_search = property_source_manager._search_source
    
    def mock_search_source(source_id, q, limit):
        results = original_search(source_id, q, limit)
        # Verify source metadata is added
        for result in results:
            assert 'source_id' in result, f"source_id missing from result: {result}"
            assert result['source_id'] == source_id, f"source_id mismatch: {result['source_id']} != {source_id}"
            assert 'source_name' in result, f"source_name missing from result: {result}"
        return results
    
    property_source_manager._search_source = mock_search_source
    
    # Search with the query
    results = property_source_manager.search(query)
    
    # Verify all results have source metadata
    for result in results:
        assert 'source_id' in result
        assert 'source_name' in result
    
    # Restore original method
    property_source_manager._search_source = original_search


@given(
    query=search_query(),
    limit=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=25)
def test_search_limit_per_source(property_source_manager, query, limit):
    """Test that search limit is applied per source."""
    # Search with the query and limit
    results = property_source_manager.search(query, limit=limit)
    
    # Group results by source
    results_by_source = {}
    for result in results:
        if 'source_id' in result:
            source_id = result['source_id']
            if source_id not in results_by_source:
                results_by_source[source_id] = []
            results_by_source[source_id].append(result)
    
    # Verify each source returned at most 'limit' results
    for source_id, source_results in results_by_source.items():
        assert len(source_results) <= limit


@given(query=search_query())
@settings(max_examples=25)
def test_document_retrieval_by_id(property_source_manager):
    """Test that documents can be retrieved by ID from the correct source."""
    document_id = "mock1:1"
    source_id = "mock1"
    
    # Retrieve document
    document = property_source_manager.get_document(document_id, source_id)
    
    # Verify document is retrieved correctly
    assert document['id'] == document_id
    assert 'content' in document


@given(query=search_query())
@settings(max_examples=25)
def test_default_source_selection(property_source_manager, query):
    """Test that default sources are used when no sources are specified."""
    # Get default sources from source manager
    default_sources = property_source_manager.default_sources
    
    # Mock the _search_source method to track which sources are used
    called_sources = []
    original_search = property_source_manager._search_source
    
    def mock_search_source(source_id, q, limit):
        called_sources.append(source_id)
        return original_search(source_id, q, limit)
    
    property_source_manager._search_source = mock_search_source
    
    # Search without specifying sources
    property_source_manager.search(query)
    
    # Verify default sources were used
    for source_id in default_sources:
        assert source_id in called_sources
    
    # Restore original method
    property_source_manager._search_source = original_search


@given(query=search_query())
@settings(max_examples=25)
def test_parallel_execution(property_source_manager, query):
    """Test that search operations are executed in parallel."""
    # Create a mock ThreadPoolExecutor to verify it's used with the correct parameters
    original_executor = ThreadPoolExecutor
    executor_init_args = {}
    
    class MockExecutor(ThreadPoolExecutor):
        def __init__(self, max_workers=None, *args, **kwargs):
            executor_init_args['max_workers'] = max_workers
            super().__init__(max_workers, *args, **kwargs)
    
    # Patch ThreadPoolExecutor
    patch_path = 'research_orchestrator.information_gathering.source_manager.ThreadPoolExecutor'
    with patch(patch_path, MockExecutor):
        # Execute search
        property_source_manager.search(query)
        
        # Verify ThreadPoolExecutor was initialized with the correct max_workers
        assert 'max_workers' in executor_init_args
        assert executor_init_args['max_workers'] == property_source_manager.max_workers