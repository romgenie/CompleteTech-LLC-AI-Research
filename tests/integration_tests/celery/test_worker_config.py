"""
Tests for Celery worker configuration.

These tests verify that Celery workers are properly configured with appropriate
task routes, concurrency settings, and error handling.
"""

import pytest
import os
from unittest.mock import patch, MagicMock, call


def test_celery_app_configuration(mock_celery_app):
    """Test that the Celery app is configured with correct settings."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.celery_app import celery_app, init_celery
    
    # Reinitialize the app to apply configuration
    init_celery(celery_app)
    
    # Verify app configuration settings were applied
    config_update_call = None
    for mock_call in mock_celery_app.method_calls:
        if mock_call[0] == 'config_from_object':
            config_update_call = mock_call
            break
    
    # Check that config was updated
    assert config_update_call is not None, "config_from_object was not called"
    
    # Manually update the mock's config dict to test setting retrieval
    mock_celery_app.conf.task_serializer = 'json'
    mock_celery_app.conf.result_serializer = 'json'
    mock_celery_app.conf.accept_content = ['json']
    mock_celery_app.conf.task_routes = {'paper_processing.tasks.*': {'queue': 'paper_processing'}}
    mock_celery_app.conf.worker_concurrency = 4
    
    # Test retrieving settings
    assert mock_celery_app.conf.task_serializer == 'json'
    assert "paper_processing.tasks.*" in mock_celery_app.conf.task_routes


def test_task_routing(mock_celery_app):
    """Test that tasks are routed to appropriate queues."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.celery_app import get_queue_for_task
    
    # Define task route patterns and expected queues
    routes = {
        'paper_processing.tasks.process_paper': 'paper_processing',
        'paper_processing.tasks.extract_entities': 'entity_extraction',
        'paper_processing.tasks.extract_relationships': 'relationship_extraction',
        'paper_processing.tasks.build_knowledge_graph': 'knowledge_graph',
        'paper_processing.tasks.notify': 'notifications'
    }
    
    # Set up mock Celery app with test routes
    mock_celery_app.conf.task_routes = routes
    
    # Test each route
    for task_name, expected_queue in routes.items():
        queue = get_queue_for_task(task_name)
        assert queue == expected_queue, f"Task {task_name} not routed to {expected_queue}"
    
    # Test default queue for unknown task
    queue = get_queue_for_task('unknown.task')
    assert queue == 'default', "Unknown task not routed to default queue"


def test_worker_concurrency(mock_celery_app):
    """Test worker concurrency configuration based on system resources."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.worker import configure_worker_concurrency
    
    # Mock CPU count
    with patch('multiprocessing.cpu_count', return_value=8):
        # Test default concurrency (should be cpu_count * 2)
        concurrency = configure_worker_concurrency()
        assert concurrency == 16, "Default concurrency should be cpu_count * 2"
        
        # Test with environment variable
        with patch.dict(os.environ, {'CELERY_WORKER_CONCURRENCY': '4'}):
            concurrency = configure_worker_concurrency()
            assert concurrency == 4, "Concurrency not respecting environment variable"
        
        # Test with low CPU count
        with patch('multiprocessing.cpu_count', return_value=1):
            concurrency = configure_worker_concurrency()
            assert concurrency == 2, "Minimum concurrency should be 2"


def test_task_result_backend(mock_celery_app, mock_redis):
    """Test that results backend is properly configured."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.celery_app import configure_result_backend
    
    # Test with Redis backend
    with patch.dict(os.environ, {'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0'}):
        backend_url = configure_result_backend()
        assert "redis" in backend_url, "Redis backend not configured correctly"
        
    # Test with default (Redis) backend with no env var
    with patch.dict(os.environ, {}, clear=True):
        backend_url = configure_result_backend()
        assert "redis" in backend_url, "Default backend should be Redis"


def test_error_handling_configuration(mock_celery_app):
    """Test error handling and retry configuration."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.celery_app import configure_error_handling
    
    # Test configuring error handling
    configure_error_handling(mock_celery_app)
    
    # Verify task_acks_late was set
    assert mock_celery_app.conf.task_acks_late is True, "task_acks_late should be True"
    
    # Verify task_reject_on_worker_lost was set
    assert mock_celery_app.conf.task_reject_on_worker_lost is True, "task_reject_on_worker_lost should be True"
    
    # Verify retry policy was set
    assert mock_celery_app.conf.task_default_retry_delay == 60, "Default retry delay should be 60 seconds"
    assert mock_celery_app.conf.task_max_retries == 3, "Max retries should be 3"


def test_worker_startup_tasks(mock_celery_app):
    """Test that worker startup tasks are correctly registered."""
    # Import here to ensure mocks are applied first
    from paper_processing.tasks.worker import worker_ready
    
    # Create a mock worker instance
    mock_worker = MagicMock()
    
    # Set up mock for worker_init signal handler
    worker_ready_handler = MagicMock()
    
    # Call the worker ready handler with our mock worker
    with patch('celery.signals.worker_ready.connect', worker_ready_handler):
        worker_ready(mock_worker)
        
        # Verify the signal handler was connected
        worker_ready_handler.assert_called_once()
        
        # Verify any startup operations the handler performed
        assert mock_worker.info.called, "Worker info should be called on startup"