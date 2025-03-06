"""
Test fixtures for Celery integration tests.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from celery.result import AsyncResult


@pytest.fixture
def mock_celery_app():
    """Mock Celery application for testing."""
    celery_app = MagicMock()
    
    # Mock task registration
    celery_app.task.return_value = lambda f: f
    
    # Create mock for sending tasks
    mock_async_result = MagicMock(spec=AsyncResult)
    mock_async_result.id = "test_task_id"
    mock_async_result.status = "PENDING"
    mock_async_result.result = None
    mock_async_result.successful.return_value = True
    mock_async_result.failed.return_value = False
    
    celery_app.send_task.return_value = mock_async_result
    
    with patch('celery.Celery', return_value=celery_app):
        yield celery_app


@pytest.fixture
def mock_celery_task():
    """Mock a specific Celery task function."""
    task_func = MagicMock()
    task_func.delay.return_value = MagicMock(
        id="test_task_id",
        status="PENDING",
        result=None,
        successful=lambda: True,
        failed=lambda: False
    )
    task_func.s.return_value = MagicMock(
        delay=lambda: MagicMock(
            id="test_task_id",
            status="PENDING"
        )
    )
    yield task_func


@pytest.fixture
def mock_redis():
    """Mock Redis connection for Celery backend."""
    redis_client = MagicMock()
    redis_client.ping.return_value = True
    redis_client.get.return_value = None
    redis_client.set.return_value = True
    
    with patch('redis.Redis', return_value=redis_client):
        yield redis_client


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test papers directory
    papers_dir = os.path.join(temp_dir, "papers")
    os.makedirs(papers_dir, exist_ok=True)
    
    yield temp_dir
    
    # Clean up
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_paper_file():
    """Create a test paper file."""
    content = (
        "# Test Paper\n\n"
        "## Abstract\n\n"
        "This is a test paper for Celery task processing tests.\n\n"
        "## Introduction\n\n"
        "The paper introduces a new approach to automated testing.\n\n"
        "## Methods\n\n"
        "We use Celery for task processing and pytest for testing.\n\n"
        "## Results\n\n"
        "The results show that our approach improves testing efficiency.\n\n"
        "## Conclusion\n\n"
        "We conclude that automated testing is essential for reliable software.\n"
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        paper_path = f.name
    
    yield paper_path
    
    # Clean up
    if os.path.exists(paper_path):
        os.unlink(paper_path)


@pytest.fixture
def mock_task_state():
    """Mock functions that retrieve task state."""
    # Mock Celery's AsyncResult for getting task status
    mock_result = MagicMock(spec=AsyncResult)
    mock_result.id = "test_task_id"
    mock_result.status = "SUCCESS"
    mock_result.result = {"status": "completed", "paper_id": "test_paper_id"}
    mock_result.successful.return_value = True
    mock_result.failed.return_value = False
    mock_result.ready.return_value = True
    
    with patch('celery.result.AsyncResult', return_value=mock_result):
        yield mock_result