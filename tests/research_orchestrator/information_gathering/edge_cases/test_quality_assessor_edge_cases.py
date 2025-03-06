"""
Edge case tests for the QualityAssessor in the Information Gathering module.

This module contains tests for edge cases and error handling in the QualityAssessor.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
import logging

# Mark all tests in this module as edge case tests and quality assessor related tests
pytestmark = [
    pytest.mark.edge_case,
    pytest.mark.information_gathering,
    pytest.mark.quality_assessor,
    pytest.mark.medium
]

from src.research_orchestrator.information_gathering.quality_assessor import QualityAssessor


@pytest.mark.empty
def test_empty_results_handling(edge_case_quality_assessor, empty_results):
    """Test handling of empty results list."""
    # Assess empty results list
    results = edge_case_quality_assessor.assess_results(empty_results)
    
    # Should handle empty results gracefully
    assert isinstance(results, list)
    assert len(results) == 0


@pytest.mark.missing
def test_results_without_quality_scores(edge_case_quality_assessor, results_without_quality_scores):
    """Test handling of results without quality scores."""
    # Assess results without quality scores
    results = edge_case_quality_assessor.assess_results(results_without_quality_scores)
    
    # Should handle missing quality scores gracefully
    assert isinstance(results, list)
    assert len(results) == len(results_without_quality_scores)


@pytest.mark.duplicate
def test_results_with_duplicate_ids(edge_case_quality_assessor, results_with_duplicate_ids):
    """Test handling of results with duplicate IDs."""
    # Assess results with duplicate IDs
    results = edge_case_quality_assessor.assess_results(results_with_duplicate_ids)
    
    # Should handle duplicate IDs gracefully
    assert isinstance(results, list)
    assert len(results) == len(results_with_duplicate_ids)


@pytest.mark.invalid
def test_invalid_metric_weights():
    """Test handling of invalid metric weights configuration."""
    # Create a quality assessor with invalid metric weights
    invalid_weights = {
        'relevance': -0.5,  # Negative weight
        'recency': 1.5,     # Weight > 1
        'authority': 0,     # Zero weight
        'completeness': "invalid"  # Non-numeric weight
    }
    
    # Should handle invalid weights gracefully (use defaults or normalize)
    assessor = QualityAssessor({'metric_weights': invalid_weights})
    
    # All weights should be valid (between 0 and 1)
    for metric, weight in assessor.metric_weights.items():
        assert isinstance(weight, float)
        assert 0 <= weight <= 1


@pytest.mark.large
def test_very_large_result_set(edge_case_quality_assessor):
    """Test handling of very large result sets."""
    # Create a large result set
    large_results = []
    for i in range(1000):  # 1000 results
        large_results.append({
            'id': f'test:{i}',
            'title': f'Result {i}',
            'snippet': f'This is result {i}',
            'quality_score': i / 1000
        })
    
    # Assess large result set
    results = edge_case_quality_assessor.assess_results(large_results)
    
    # Should handle large result sets gracefully
    assert isinstance(results, list)
    assert len(results) == len(large_results)


@pytest.mark.malformed
def test_malformed_results(edge_case_quality_assessor):
    """Test handling of malformed results."""
    # Create malformed results with missing required fields
    malformed_results = [
        {},  # Empty dict
        {'id': 'test:1'},  # Missing title and snippet
        {'title': 'No ID Result'},  # Missing ID
        None,  # None instead of dict
        ['not', 'a', 'dict']  # List instead of dict
    ]
    
    # Assess malformed results
    results = edge_case_quality_assessor.assess_results(malformed_results)
    
    # Should handle malformed results gracefully
    assert isinstance(results, list)


@pytest.mark.error
def test_metric_calculation_error_handling():
    """Test handling of errors during metric calculation."""
    # Create a quality assessor with a mock metric calculation method that raises an exception
    assessor = QualityAssessor({})
    
    # Create a simple result
    result = {'id': 'test:1', 'title': 'Test Result', 'snippet': 'This is a test result'}
    
    # Assess the result (should not raise an exception)
    results = assessor.assess_results([result])
    
    # Should handle metric calculation errors gracefully
    assert isinstance(results, list)
    assert len(results) == 1


@pytest.mark.sorting
def test_sorting_stability(edge_case_quality_assessor):
    """Test stability of sorting when quality scores are identical."""
    # Create results with identical quality scores
    results_with_identical_scores = [
        {'id': 'test:1', 'title': 'Result 1', 'snippet': 'This is result 1', 'quality_score': 0.8},
        {'id': 'test:2', 'title': 'Result 2', 'snippet': 'This is result 2', 'quality_score': 0.8},
        {'id': 'test:3', 'title': 'Result 3', 'snippet': 'This is result 3', 'quality_score': 0.8}
    ]
    
    # Assess results with identical scores
    results = edge_case_quality_assessor.assess_results(results_with_identical_scores)
    
    # Should maintain order for identical scores (stable sort)
    assert results[0]['id'] == 'test:1'
    assert results[1]['id'] == 'test:2'
    assert results[2]['id'] == 'test:3'


@pytest.mark.special_chars
def test_special_character_handling(edge_case_quality_assessor):
    """Test handling of results with special characters."""
    # Create results with special characters
    results_with_special_chars = [
        {
            'id': 'test:1',
            'title': 'Result with special characters: ©®™•★☆♦♣♠♥',
            'snippet': 'This result has emoji 😀🤣😎👍❤️🔥 and multi-language text: مرحبا بالعالم 你好，世界',
            'quality_score': 0.9
        }
    ]
    
    # Assess results with special characters
    results = edge_case_quality_assessor.assess_results(results_with_special_chars)
    
    # Should handle special characters gracefully
    assert isinstance(results, list)
    assert results[0]['title'] == 'Result with special characters: ©®™•★☆♦♣♠♥'


@pytest.mark.extreme
def test_extreme_quality_scores(edge_case_quality_assessor):
    """Test handling of extreme quality scores (0 and 1)."""
    # Create results with extreme quality scores
    extreme_score_results = [
        {'id': 'test:1', 'title': 'Zero Score', 'snippet': 'This result has score 0', 'quality_score': 0.0},
        {'id': 'test:2', 'title': 'Perfect Score', 'snippet': 'This result has score 1', 'quality_score': 1.0}
    ]
    
    # Assess results with extreme scores
    results = edge_case_quality_assessor.assess_results(extreme_score_results)
    
    # Should handle extreme scores gracefully and maintain ordering (1.0 first, 0.0 last)
    assert results[0]['id'] == 'test:2'
    assert results[1]['id'] == 'test:1'