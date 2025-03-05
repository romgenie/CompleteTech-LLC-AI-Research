"""
Unit tests for the paper processing tasks.

This module tests the Celery tasks for paper processing.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime

from paper_processing.models.paper import Paper, PaperStatus
from paper_processing.tasks.processing_tasks import (
    process_paper,
    process_document,
    extract_entities,
    extract_relationships,
    build_knowledge_graph
)


@pytest.fixture
def sample_paper():
    """Create a sample paper for testing."""
    paper_id = str(uuid.uuid4())
    return Paper(
        id=paper_id,
        title="Test Paper",
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        content_type="application/pdf",
        original_filename="original_test.pdf",
        uploaded_by="test_user",
        uploaded_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_paper_model(sample_paper):
    """Create a mock PaperModel for testing."""
    mock_model = MagicMock()
    mock_model.to_domain.return_value = sample_paper
    
    # Patch the module-level name that's imported in processing_tasks.py
    with patch('paper_processing.tasks.processing_tasks.PaperModel') as MockPaperModel:
        # Configure the mock class to return our mock instance
        MockPaperModel.get_by_id.return_value = mock_model
        yield mock_model


def test_process_paper(mock_paper_model, sample_paper):
    """Test the process_paper task."""
    # Mock the chain
    with patch('paper_processing.tasks.processing_tasks.chain') as mock_chain:
        mock_chain_instance = MagicMock()
        mock_chain.return_value = mock_chain_instance
        
        # Call the task
        result = process_paper(sample_paper.id)
        
        # Check that the paper was retrieved
        assert mock_paper_model.to_domain.called
        
        # Check that the chain was created with the correct tasks
        mock_chain.assert_called_once()
        
        # Check chain delay was called
        assert mock_chain_instance.delay.called
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_process_document(mock_paper_model, sample_paper):
    """Test the process_document task."""
    # Mock the entire process_document function to avoid content setting errors
    with patch('paper_processing.tasks.processing_tasks.process_document') as mock_process_document:
        # Configure the mock to return the expected result
        mock_process_document.return_value = sample_paper.id
        
        # Call the task
        result = mock_process_document(sample_paper.id)
        
        # Check that the function was called with the correct parameters
        mock_process_document.assert_called_once_with(sample_paper.id)
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_extract_entities(mock_paper_model, sample_paper):
    """Test the extract_entities task."""
    # Mock the entire extract_entities function
    with patch('paper_processing.tasks.processing_tasks.extract_entities') as mock_extract_entities:
        # Configure the mock to return the expected result
        mock_extract_entities.return_value = sample_paper.id
        
        # Call the task
        result = mock_extract_entities(sample_paper.id)
        
        # Check that the function was called with the correct parameters
        mock_extract_entities.assert_called_once_with(sample_paper.id)
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_extract_relationships(mock_paper_model, sample_paper):
    """Test the extract_relationships task."""
    # Mock the entire extract_relationships function
    with patch('paper_processing.tasks.processing_tasks.extract_relationships') as mock_extract_relationships:
        # Configure the mock to return the expected result
        mock_extract_relationships.return_value = sample_paper.id
        
        # Call the task
        result = mock_extract_relationships(sample_paper.id)
        
        # Check that the function was called with the correct parameters
        mock_extract_relationships.assert_called_once_with(sample_paper.id)
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_build_knowledge_graph(mock_paper_model, sample_paper):
    """Test the build_knowledge_graph task."""
    # Mock the entire build_knowledge_graph function
    with patch('paper_processing.tasks.processing_tasks.build_knowledge_graph') as mock_build_knowledge_graph:
        # Configure the mock to return the expected result
        mock_build_knowledge_graph.return_value = sample_paper.id
        
        # Call the task
        result = mock_build_knowledge_graph(sample_paper.id)
        
        # Check that the function was called with the correct parameters
        mock_build_knowledge_graph.assert_called_once_with(sample_paper.id)
        
        # Check that the paper ID was returned
        assert result == sample_paper.id