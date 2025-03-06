"""
Property-based tests for the SearchManager in the Information Gathering module.

This module contains property-based tests using Hypothesis to verify the properties
of the SearchManager's behavior across a wide range of inputs.
"""

import pytest
import json
import sys
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any

# Try to import hypothesis, but skip tests if not available
try:
    from hypothesis import given, strategies as st, settings, example, assume
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    # Create dummy decorators for when hypothesis is not available
    def given(*args, **kwargs):
        return lambda func: pytest.mark.skip(reason="Hypothesis not installed")(func)
    def settings(*args, **kwargs):
        return lambda func: func
    def example(*args, **kwargs):
        return lambda func: func
    # Create a simple namespace for strategies
    class DummyStrategies:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
        def composite(self, func):
            return func
    st = DummyStrategies()

# Mark all tests in this module as property-based tests and search related tests
pytestmark = [
    pytest.mark.property,
    pytest.mark.information_gathering,
    pytest.mark.search,
    pytest.mark.medium
]

# Try both import paths
try:
    from src.research_orchestrator.information_gathering.search_manager import SearchManager
except ImportError:
    try:
        from src.research_orchestrator.information_gathering.search_manager import SearchManager
    except ImportError:
        # Create a stub if the import fails for CI environments
        class SearchManager:
            def __init__(self, config=None):
                self.config = config or {}
                self.source_manager = None
                self.quality_assessor = None
                self.results_cache = {}
                
            def search(self, query, limit=10, sources=None):
                return []
                
            def get_document(self, document_id, source_id):
                return {"id": document_id}
                
            def clear_cache(self):
                self.results_cache = {}


# Strategy for generating valid search queries
@st.composite
def valid_search_query(draw):
    """Strategy for generating valid search queries."""
    # Generate different types of search queries
    query_type = draw(st.sampled_from(["simple", "complex", "specialized"]))
    
    if query_type == "simple":
        # Simple one-word query
        return draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=20))
    elif query_type == "complex":
        # Multi-word query
        words = draw(st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=15),
            min_size=2, max_size=5
        ))
        return " ".join(words)
    else:  # specialized
        # Query with special operators or formatting
        prefix = draw(st.sampled_from(["", "topic:", "author:", "title:"]))
        base_query = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=15))
        suffix = draw(st.sampled_from(["", " filetype:pdf", " site:edu", " year:2023"]))
        return f"{prefix}{base_query}{suffix}"


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(query=valid_search_query())
@settings(max_examples=50)
def test_search_query_preservation(property_search_manager, query):
    """Test that the search manager preserves the original query."""
    # Search with the query
    results = property_search_manager.search(query)
    
    # Verify the query is preserved in the results
    for result in results:
        assert 'query' in result
        assert result['query'] == query


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(query=valid_search_query())
@settings(max_examples=25)
def test_search_idempotence(property_search_manager, query):
    """Test that searching with the same query multiple times gives consistent results."""
    # First search
    results1 = property_search_manager.search(query)
    
    # Second search with the same query
    results2 = property_search_manager.search(query)
    
    # The results should be identical (same order, same content)
    assert len(results1) == len(results2)
    for i in range(len(results1)):
        assert results1[i]['id'] == results2[i]['id']
        assert results1[i]['title'] == results2[i]['title']
        assert results1[i]['snippet'] == results2[i]['snippet']


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(
    query=valid_search_query(),
    limit=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=25)
def test_search_limit_respected(property_search_manager, query, limit):
    """Test that the search respects the result limit parameter."""
    # Search with a specific limit
    results = property_search_manager.search(query, limit=limit)
    
    # The number of results should not exceed the limit
    assert len(results) <= limit


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(
    query1=valid_search_query(),
    query2=valid_search_query()
)
@settings(max_examples=25)
def test_cache_isolation(property_search_manager, query1, query2):
    """Test that different search queries use different cache entries."""
    # Skip if the queries happen to be identical
    assume(query1 != query2)
    
    # Clear cache to start fresh
    property_search_manager.clear_cache()
    
    # First search with query1
    results1 = property_search_manager.search(query1)
    
    # Second search with query2
    results2 = property_search_manager.search(query2)
    
    # The results should have the correct query attribute
    for result in results1:
        assert result['query'] == query1
    
    for result in results2:
        assert result['query'] == query2


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(query=valid_search_query())
@settings(max_examples=25)
def test_document_retrieval_consistency(property_search_manager):
    """Test that document retrieval is consistent with the search results."""
    # Mock search results with a document ID we'll test
    document_id = "mock1:1"
    source_id = "mock1"
    
    # Retrieve the document
    document = property_search_manager.get_document(document_id, source_id)
    
    # Verify the document has the expected ID
    assert document['id'] == document_id


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(query=valid_search_query())
@settings(max_examples=25)
def test_quality_assessment_applied(property_search_manager, property_quality_assessor, query):
    """Test that quality assessment is applied to search results."""
    # Mock the assess_results method to track calls
    original_assess = property_quality_assessor.assess_results
    property_quality_assessor.assess_results = MagicMock(side_effect=original_assess)
    
    # Perform search
    results = property_search_manager.search(query)
    
    # Verify assess_results was called
    property_quality_assessor.assess_results.assert_called_once()
    
    # Restore original method
    property_quality_assessor.assess_results = original_assess


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(query=valid_search_query())
@settings(max_examples=25)
def test_cache_clearing(property_search_manager, query):
    """Test that cache clearing removes cached results."""
    # Perform initial search to populate cache
    property_search_manager.search(query)
    
    # Clear the cache
    property_search_manager.clear_cache()
    
    # Verify the cache is empty
    assert property_search_manager.results_cache == {}


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="Hypothesis not installed")
@given(
    query=valid_search_query(),
    sources=st.lists(st.sampled_from(["mock1", "mock2"]), min_size=0, max_size=2)
)
@settings(max_examples=25)
def test_source_specification(property_search_manager, query, sources):
    """Test that specifying sources influences the search results."""
    # Mock the source_manager's search method to track calls
    original_search = property_search_manager.source_manager.search
    property_search_manager.source_manager.search = MagicMock(side_effect=original_search)
    
    # Perform search with specific sources
    results = property_search_manager.search(query, sources=sources)
    
    # Verify source_manager.search was called with the correct sources
    property_search_manager.source_manager.search.assert_called_once_with(query, sources, 10, 'general')
    
    # Restore original method
    property_search_manager.source_manager.search = original_search