"""
Tests for Celery task creation and execution.

These tests verify that Celery tasks are properly created, executed,
and can handle error conditions.
"""

import pytest
import os
from unittest.mock import patch, MagicMock, call


@pytest.mark.parametrize("task_name", [
    "process_paper",
    "extract_entities",
    "extract_relationships",
    "build_knowledge_graph"
])
def test_task_creation(mock_celery_app, task_name):
    """Test that tasks can be created and sent with correct parameters."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.paper_tasks import create_task
    
    # Create test arguments
    kwargs = {"paper_id": "test_paper_id", "options": {"detailed": True}}
    
    # Create the task
    task_result = create_task(task_name, **kwargs)
    
    # Verify the task was created correctly
    assert task_result is not None
    assert task_result.id == "test_task_id"
    
    # Verify the task was sent to Celery with correct arguments
    mock_celery_app.send_task.assert_called_once_with(
        f"paper_processing.tasks.{task_name}",
        kwargs=kwargs,
        queue="paper_processing"
    )


def test_task_execution(mock_celery_app, mock_celery_task, test_paper_file):
    """Test task execution with simulated success."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.paper_tasks import process_paper
    
    # Configure the mock to simulate a successful task execution
    mock_celery_task.delay.return_value.status = "SUCCESS"
    mock_celery_task.delay.return_value.result = {
        "paper_id": "test_paper_id",
        "status": "processed",
        "entities_count": 15,
        "relationships_count": 10
    }
    
    # Apply mock to task function
    with patch('paper_processing.tasks.paper_tasks.process_paper', mock_celery_task):
        # Execute the task
        result = process_paper("test_paper_id", file_path=test_paper_file)
        
        # Verify the task was called correctly
        mock_celery_task.delay.assert_called_once_with(
            "test_paper_id", 
            file_path=test_paper_file
        )
        
        # Verify the result is what we expected
        assert result.id == "test_task_id"
        assert result.status == "SUCCESS"


def test_task_error_handling(mock_celery_app, mock_celery_task):
    """Test task error handling with simulated failure."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.paper_tasks import extract_entities
    
    # Configure the mock to simulate a failed task execution
    error_result = MagicMock()
    error_result.id = "error_task_id"
    error_result.status = "FAILURE"
    error_result.result = Exception("Test error message")
    error_result.traceback = "Traceback: Test error\n..."
    error_result.successful.return_value = False
    error_result.failed.return_value = True
    
    mock_celery_task.delay.return_value = error_result
    
    # Apply mock to task function
    with patch('paper_processing.tasks.paper_tasks.extract_entities', mock_celery_task):
        # Execute the task (should handle the error)
        result = extract_entities("test_paper_id")
        
        # Verify the task was called correctly
        mock_celery_task.delay.assert_called_once_with("test_paper_id")
        
        # Verify the result is what we expected
        assert result.id == "error_task_id"
        assert result.status == "FAILURE"
        assert result.failed() is True
        assert result.successful() is False


def test_task_chain(mock_celery_app, test_paper_file):
    """Test that task chains are correctly created and executed."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.paper_tasks import create_processing_chain
    
    # Mock the chain and group constructors
    chain_mock = MagicMock()
    group_mock = MagicMock()
    
    # Return mocks for testing
    chain_mock.return_value = MagicMock()
    chain_mock.return_value.delay.return_value = MagicMock(id="chain_task_id")
    group_mock.return_value = MagicMock()
    
    with patch('celery.chain', chain_mock), \
         patch('celery.group', group_mock):
        
        # Create a task chain
        result = create_processing_chain("test_paper_id", file_path=test_paper_file)
        
        # Verify chain was created with correct signature
        assert chain_mock.called
        
        # Verify the result is what we expected
        assert result.id == "chain_task_id"


def test_retry_mechanism(mock_celery_app, mock_celery_task):
    """Test that tasks properly retry on transient errors."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.paper_tasks import extract_relationships
    
    # Mock the Celery retry method
    retry_mock = MagicMock()
    retry_mock.side_effect = extract_relationships.retry
    
    # Create mock exception for testing retry
    test_error = Exception("Temporary network error")
    
    # Configure the task to simulate an exception
    mock_celery_task.side_effect = [test_error, {"status": "success"}]
    mock_celery_task.retry = retry_mock
    
    # Apply mock to task function
    with patch('paper_processing.tasks.paper_tasks.extract_relationships', mock_celery_task):
        try:
            # This should trigger retry
            extract_relationships("test_paper_id")
        except Exception:
            # Expected to retry, so let's check retry was called
            pass
            
        # Verify that retry was called with correct parameters
        assert retry_mock.called
        
        # Call again to test successful execution after retry
        result = extract_relationships("test_paper_id")
        assert result == {"status": "success"}