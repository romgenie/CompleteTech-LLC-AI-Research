"""
Tests for Celery task status monitoring.

These tests verify that task status can be checked and that progress 
is accurately reported.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, call


def test_task_status_check(mock_task_state):
    """Test checking the status of a Celery task."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.task_monitor import get_task_status
    
    # Check the status of our mock task
    status = get_task_status("test_task_id")
    
    # Verify status reflects our mock
    assert status is not None
    assert status["task_id"] == "test_task_id"
    assert status["status"] == "SUCCESS"
    assert "result" in status
    assert status["result"]["paper_id"] == "test_paper_id"


def test_task_monitoring_history(mock_redis, mock_task_state):
    """Test recording and retrieving task execution history."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.task_monitor import record_task_completion, get_task_history
    
    # Configure Redis mock for history data
    mock_history = [
        {"task_id": "task1", "status": "SUCCESS", "timestamp": "2025-03-01T10:00:00"},
        {"task_id": "task2", "status": "FAILURE", "timestamp": "2025-03-01T11:00:00"}
    ]
    mock_redis.get.return_value = json.dumps(mock_history).encode()
    
    # Test retrieving history
    history = get_task_history("test_paper_id")
    
    # Verify Redis was called correctly
    mock_redis.get.assert_called_with("task_history:test_paper_id")
    
    # Verify history matches our mock
    assert len(history) == 2
    assert history[0]["task_id"] == "task1"
    assert history[1]["status"] == "FAILURE"
    
    # Test recording new task completion
    record_task_completion("test_task_id", "test_paper_id", "completed")
    
    # Verify Redis was called to get and set history
    mock_redis.get.assert_called_with("task_history:test_paper_id")
    assert mock_redis.set.called


def test_progress_tracking(mock_redis):
    """Test tracking progress of long-running tasks."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.task_monitor import update_progress, get_progress
    
    # Configure Redis mock for progress data
    mock_redis.get.return_value = json.dumps({"progress": 50}).encode()
    
    # Test retrieving progress
    progress = get_progress("test_task_id")
    
    # Verify Redis was called correctly
    mock_redis.get.assert_called_with("task_progress:test_task_id")
    
    # Verify progress matches our mock
    assert progress == 50
    
    # Test updating progress
    update_progress("test_task_id", 75)
    
    # Verify Redis was called to set progress
    mock_redis.set.assert_called_with(
        "task_progress:test_task_id", 
        json.dumps({"progress": 75}),
        ex=86400  # 24 hours expiry
    )


def test_task_result_retrieval(mock_task_state):
    """Test retrieving task results after completion."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.task_monitor import get_task_result
    
    # Test retrieving result
    result = get_task_result("test_task_id")
    
    # Verify result matches our mock
    assert result is not None
    assert result["status"] == "completed"
    assert result["paper_id"] == "test_paper_id"


@pytest.mark.parametrize("task_id,status,expected_state", [
    ("task1", "SUCCESS", "completed"),
    ("task2", "FAILURE", "failed"),
    ("task3", "PENDING", "in_progress"),
    ("task4", "STARTED", "in_progress"),
    ("task5", "RETRY", "in_progress"),
    ("task6", "REVOKED", "canceled")
])
def test_task_state_mapping(mock_celery_app, task_id, status, expected_state):
    """Test mapping between Celery task states and application states."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.task_monitor import map_task_state
    
    # Create a mock result with the specified status
    mock_result = MagicMock()
    mock_result.id = task_id
    mock_result.status = status
    
    # Test mapping the state
    state = map_task_state(mock_result)
    
    # Verify state matches expected
    assert state == expected_state


def test_error_reporting(mock_task_state, mock_redis):
    """Test reporting and retrieving task errors."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.task_monitor import report_task_error, get_task_errors
    
    # Configure mock for error data
    error_data = [
        {"task_id": "task1", "error": "Connection error", "timestamp": "2025-03-01T10:00:00"},
        {"task_id": "task2", "error": "Timeout", "timestamp": "2025-03-01T11:00:00"}
    ]
    mock_redis.get.return_value = json.dumps(error_data).encode()
    
    # Test retrieving errors
    errors = get_task_errors("test_paper_id")
    
    # Verify Redis was called correctly
    mock_redis.get.assert_called_with("task_errors:test_paper_id")
    
    # Verify errors match our mock
    assert len(errors) == 2
    assert errors[0]["task_id"] == "task1"
    assert errors[1]["error"] == "Timeout"
    
    # Test reporting a new error
    report_task_error("test_task_id", "test_paper_id", "Processing error")
    
    # Verify Redis was called to get and set errors
    mock_redis.get.assert_called_with("task_errors:test_paper_id")
    assert mock_redis.set.called