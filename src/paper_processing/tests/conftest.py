"""
Test configuration for the Paper Processing Pipeline.

This module provides fixtures and configuration for pytest tests.
"""

import os
import pytest
import asyncio
import logging
from typing import Dict, Any, List, Optional, Generator
from unittest.mock import MagicMock, AsyncMock

# Set test environment variable
os.environ["PAPER_PROCESSING_ENVIRONMENT"] = "testing"

# Import after setting environment
from paper_processing.config.settings import Settings, settings
from paper_processing.models.paper import Paper, PaperStatus
from paper_processing.models.state_machine import PaperStateMachine
from paper_processing.db.models import PaperModel
from paper_processing.db.connection import DatabaseConnection


# Configure test logging
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def test_settings() -> Settings:
    """
    Fixture for test settings.
    
    Returns:
        Test settings instance
    """
    # Create test settings with in-memory MongoDB
    test_settings = Settings(
        environment="testing",
        database={"mongodb_uri": "mongodb://localhost:27017", "database_name": "test_paper_processing"},
        celery={"broker_url": "memory://", "result_backend": "memory://"},
        logging={"level": "DEBUG"}
    )
    
    return test_settings


@pytest.fixture
def sample_paper() -> Paper:
    """
    Fixture for a sample paper.
    
    Returns:
        Sample paper instance
    """
    from datetime import datetime
    import uuid
    
    # Create a sample paper
    paper = Paper(
        id=str(uuid.uuid4()),
        title="Test Paper",
        authors=[{"name": "Test Author", "affiliation": "Test University"}],
        abstract="This is a test paper abstract.",
        year=2025,
        doi="10.1234/test.1234",
        url="https://example.com/test-paper",
        filename="test-paper.pdf",
        file_path="/tmp/test-paper.pdf",
        content_type="application/pdf",
        original_filename="test_paper.pdf",
        uploaded_by="test_user",
        uploaded_at=datetime.utcnow(),
        status=PaperStatus.UPLOADED
    )
    
    return paper


@pytest.fixture
def mock_db_connection() -> AsyncMock:
    """
    Fixture for a mock database connection.
    
    Returns:
        Mock database connection
    """
    # Create a mock database connection
    mock_conn = AsyncMock()
    mock_conn.is_connected = True
    mock_conn.get_collection = AsyncMock()
    
    # Mock collections
    mock_papers_collection = AsyncMock()
    mock_conn.get_collection.return_value = mock_papers_collection
    mock_conn.collections = {"papers": mock_papers_collection}
    
    return mock_conn


@pytest.fixture
def mock_paper_model(mock_db_connection) -> PaperModel:
    """
    Fixture for a mock paper model.
    
    Args:
        mock_db_connection: Mock database connection
        
    Returns:
        Mock paper model
    """
    # Create mock paper collection
    mock_papers_collection = mock_db_connection.collections["papers"]
    
    # Configure mock methods
    mock_papers_collection.find_one = AsyncMock()
    mock_papers_collection.replace_one = AsyncMock()
    mock_papers_collection.update_one = AsyncMock()
    mock_papers_collection.find = AsyncMock()
    mock_papers_collection.count_documents = AsyncMock()
    
    # Create paper model with mock collection
    paper_model = PaperModel(mock_papers_collection)
    
    return paper_model


@pytest.fixture
def mock_task_runner() -> AsyncMock:
    """
    Fixture for a mock task runner.
    
    Returns:
        Mock task runner
    """
    # Create a mock task runner
    mock_runner = AsyncMock()
    mock_runner.run_task = AsyncMock()
    
    return mock_runner


@pytest.fixture
def mock_knowledge_graph_adapter() -> AsyncMock:
    """
    Fixture for a mock knowledge graph adapter.
    
    Returns:
        Mock knowledge graph adapter
    """
    # Create a mock knowledge graph adapter
    mock_adapter = AsyncMock()
    mock_adapter.add_paper_to_knowledge_graph = AsyncMock()
    mock_adapter.create_paper_node = AsyncMock()
    mock_adapter.convert_entity = AsyncMock()
    mock_adapter.convert_relationship = AsyncMock()
    
    # Configure return values
    mock_adapter.add_paper_to_knowledge_graph.return_value = {
        "paper_node_id": "kg-123",
        "entity_count": 5,
        "relationship_count": 10,
        "status": "success"
    }
    
    return mock_adapter


@pytest.fixture
def mock_research_implementation_adapter() -> AsyncMock:
    """
    Fixture for a mock research implementation adapter.
    
    Returns:
        Mock research implementation adapter
    """
    # Create a mock research implementation adapter
    mock_adapter = AsyncMock()
    mock_adapter.create_implementation_request = AsyncMock()
    mock_adapter.check_implementation_status = AsyncMock()
    mock_adapter.extract_algorithm_entities = AsyncMock()
    
    # Configure return values
    mock_adapter.create_implementation_request.return_value = {
        "status": "success",
        "implementation_id": "impl-123",
        "message": "Implementation request created successfully"
    }
    
    return mock_adapter


@pytest.fixture
def mock_research_orchestrator_adapter() -> AsyncMock:
    """
    Fixture for a mock research orchestrator adapter.
    
    Returns:
        Mock research orchestrator adapter
    """
    # Create a mock research orchestrator adapter
    mock_adapter = AsyncMock()
    mock_adapter.create_research_task = AsyncMock()
    mock_adapter.generate_research_query = AsyncMock()
    mock_adapter.generate_related_research = AsyncMock()
    
    # Configure return values
    mock_adapter.create_research_task.return_value = {
        "status": "success",
        "task_id": "task-123",
        "message": "Research task created successfully"
    }
    
    return mock_adapter


@pytest.fixture
def mock_extraction_adapter() -> AsyncMock:
    """
    Fixture for a mock extraction adapter.
    
    Returns:
        Mock extraction adapter
    """
    # Create a mock extraction adapter
    mock_adapter = AsyncMock()
    mock_adapter.process_document = AsyncMock()
    mock_adapter.extract_entities = AsyncMock()
    mock_adapter.extract_relationships = AsyncMock()
    mock_adapter.process_paper = AsyncMock()
    
    # Configure return values
    mock_adapter.process_paper.return_value = {
        "status": "success",
        "document_id": "doc-123",
        "entity_count": 5,
        "relationship_count": 10,
        "entities": [],
        "relationships": [],
        "metadata_updates": {}
    }
    
    return mock_adapter