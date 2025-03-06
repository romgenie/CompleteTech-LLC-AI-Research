"""
Global fixtures for all tests in the project.

This file contains fixtures that are available to all tests in the project,
providing common utilities and mock objects to simplify testing.
"""

import pytest
import os
import sys
import tempfile
import shutil
import json
import logging
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional, Union


@pytest.fixture(scope="session", autouse=True)
def setup_pythonpath():
    """
    Ensure the project root directory is in the PYTHONPATH.
    This allows imports from src to work correctly in tests.
    """
    # Get the directory containing this conftest.py (should be the tests directory)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the project root (parent of tests directory)
    project_root = os.path.dirname(tests_dir)
    
    # Add to sys.path if not already present
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Added {project_root} to PYTHONPATH")


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing and clean it up afterwards."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_data_dir():
    """Return the path to the test_data directory."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(tests_dir, "test_data")


@pytest.fixture
def mock_logger():
    """Return a mock logger for testing."""
    logger = MagicMock()
    return logger


@pytest.fixture
def suppress_logging():
    """Temporarily suppress logging during tests."""
    original_level = logging.root.level
    logging.root.setLevel(logging.CRITICAL)
    yield
    logging.root.setLevel(original_level)


@pytest.fixture
def test_file_path(temp_directory) -> str:
    """Create a test file with some content and return its path."""
    file_path = os.path.join(temp_directory, "test_file.txt")
    with open(file_path, "w") as f:
        f.write("This is a test file.\nIt has multiple lines.\nFor testing purposes.")
    return file_path


@pytest.fixture
def json_file_path(temp_directory) -> str:
    """Create a test JSON file and return its path."""
    file_path = os.path.join(temp_directory, "test_data.json")
    test_data = {
        "name": "Test Data",
        "values": [1, 2, 3, 4, 5],
        "nested": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    with open(file_path, "w") as f:
        json.dump(test_data, f)
    return file_path


@pytest.fixture
def mock_response():
    """Return a mock HTTP response object."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"status": "success", "data": {"id": 1, "name": "Test"}}
    response.text = '{"status": "success", "data": {"id": 1, "name": "Test"}}'
    response.content = b'{"status": "success", "data": {"id": 1, "name": "Test"}}'
    response.headers = {"Content-Type": "application/json"}
    return response


@pytest.fixture
def mock_failed_response():
    """Return a mock HTTP error response object."""
    response = MagicMock()
    response.status_code = 404
    response.json.return_value = {"status": "error", "message": "Not found"}
    response.text = '{"status": "error", "message": "Not found"}'
    response.content = b'{"status": "error", "message": "Not found"}'
    response.headers = {"Content-Type": "application/json"}
    response.raise_for_status.side_effect = Exception("404 Client Error: Not Found")
    return response


@pytest.fixture
def patch_requests():
    """Patch the requests.get/post/put/delete methods for testing HTTP calls."""
    with patch("requests.get") as mock_get, \
         patch("requests.post") as mock_post, \
         patch("requests.put") as mock_put, \
         patch("requests.delete") as mock_delete:
        
        # Configure default success responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.text = '{"status": "success"}'
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_put.return_value = mock_response
        mock_delete.return_value = mock_response
        
        yield {
            "get": mock_get,
            "post": mock_post,
            "put": mock_put,
            "delete": mock_delete,
            "response": mock_response
        }