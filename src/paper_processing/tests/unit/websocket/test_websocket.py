"""
Unit tests for the WebSocket functionality.

This module tests the WebSocket connection manager and event handling.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from datetime import datetime

from paper_processing.websocket.connection import ConnectionManager
from paper_processing.websocket.events import (
    create_system_event,
    create_paper_status_event,
    create_error_event
)


@pytest.fixture
def connection_manager():
    """Create a connection manager for testing."""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    websocket = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.send_json = AsyncMock()
    return websocket


@pytest.mark.asyncio
async def test_connection_manager_connect(connection_manager, mock_websocket):
    """Test connecting a client to the connection manager."""
    paper_id = "test_paper"
    
    # Connect the client
    await connection_manager.connect(mock_websocket, paper_id)
    
    # Check that the client was added to active connections
    assert mock_websocket in connection_manager.active_connections
    
    # Check that the client was subscribed to the paper
    assert paper_id in connection_manager.paper_connections
    assert mock_websocket in connection_manager.paper_connections[paper_id]


@pytest.mark.asyncio
async def test_connection_manager_disconnect(connection_manager, mock_websocket):
    """Test disconnecting a client from the connection manager."""
    paper_id = "test_paper"
    
    # Connect the client
    await connection_manager.connect(mock_websocket, paper_id)
    
    # Disconnect the client
    await connection_manager.disconnect(mock_websocket)
    
    # Check that the client was removed from active connections
    assert mock_websocket not in connection_manager.active_connections
    
    # Check that the paper is also removed from paper_connections when the last client is removed
    # This is how the actual implementation works
    assert paper_id not in connection_manager.paper_connections


@pytest.mark.asyncio
async def test_connection_manager_subscribe(connection_manager, mock_websocket):
    """Test subscribing a client to a paper."""
    paper_id = "test_paper"
    
    # Connect the client without initially subscribing to the paper
    await connection_manager.connect(mock_websocket)
    
    # Subscribe the client to a paper
    await connection_manager.subscribe_to_paper(mock_websocket, paper_id)
    
    # Check that the subscription was added
    assert paper_id in connection_manager.paper_connections
    assert mock_websocket in connection_manager.paper_connections[paper_id]


@pytest.mark.asyncio
async def test_connection_manager_unsubscribe(connection_manager, mock_websocket):
    """Test unsubscribing a client from a paper."""
    paper_id = "test_paper"
    
    # Connect the client and subscribe to a paper
    await connection_manager.connect(mock_websocket, paper_id)
    
    # Unsubscribe the client from the paper
    await connection_manager.unsubscribe_from_paper(mock_websocket, paper_id)
    
    # Check that the paper subscription was removed completely
    # The implementation removes the paper_id entry when there are no more subscribers
    assert paper_id not in connection_manager.paper_connections


@pytest.mark.asyncio
async def test_connection_manager_broadcast(connection_manager, mock_websocket):
    """Test broadcasting a message to all clients."""
    # Connect the client
    await connection_manager.connect(mock_websocket)
    
    # Create an event
    event = {"type": "test", "message": "Test message"}
    
    # Broadcast the event
    await connection_manager.broadcast(event)
    
    # Check that the event was sent to the client as text
    # The implementation uses send_text with JSON-formatted string
    mock_websocket.send_text.assert_called_once()


@pytest.mark.asyncio
async def test_connection_manager_broadcast_to_paper(connection_manager, mock_websocket):
    """Test broadcasting a message to clients subscribed to a paper."""
    paper_id = "test_paper"
    
    # Connect the client and subscribe to a paper
    await connection_manager.connect(mock_websocket, paper_id)
    
    # Create an event
    event = {"type": "test", "message": "Test message"}
    
    # Broadcast the event to the paper
    await connection_manager.broadcast_to_paper(paper_id, event)
    
    # Check that the event was sent to the client as text
    # The implementation uses send_text with JSON-formatted string
    mock_websocket.send_text.assert_called_once()


@pytest.mark.asyncio
async def test_connection_manager_send_personal_message(connection_manager, mock_websocket):
    """Test sending a personal message to a client."""
    # Connect the client
    await connection_manager.connect(mock_websocket)
    
    # Create an event
    event = {"type": "test", "message": "Test message"}
    
    # Send a personal message
    await connection_manager.send_personal_message(mock_websocket, event)
    
    # Check that the event was sent to the client as text
    # The implementation uses send_text with JSON-formatted string
    mock_websocket.send_text.assert_called_once()


def test_create_system_event():
    """Test creating a system event."""
    message = "Test message"
    event_type = "test"
    metadata = {"key": "value"}
    
    # Create the event
    event = create_system_event(message, event_type, metadata)
    
    # Check event structure
    assert event["event_type"] == event_type
    assert event["message"] == message
    assert event["metadata"] == metadata
    assert "timestamp" in event


def test_create_paper_status_event():
    """Test creating a paper status event."""
    paper_id = "test_paper"
    status = "PROCESSING"
    message = "Test message"
    progress = 50
    metadata = {"key": "value"}
    
    # Create the event
    event = create_paper_status_event(paper_id, status, message, progress, metadata)
    
    # Check event structure
    assert event["event_type"] == "paper_status"
    assert event["paper_id"] == paper_id
    assert event["data"]["status"] == status
    assert event["data"]["message"] == message
    assert event["data"]["progress"] == progress
    assert event["data"]["metadata"] == metadata
    assert "timestamp" in event


def test_create_error_event():
    """Test creating an error event."""
    message = "Test error"
    error_type = "test_error"
    details = {"error": "details"}
    
    # Create the event
    event = create_error_event(message, error_type, details)
    
    # Check event structure
    assert event["event_type"] == "error"
    assert event["message"] == message
    assert event["error_type"] == error_type
    assert event["details"] == details
    assert "timestamp" in event