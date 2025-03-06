"""
Tests for WebSocket connection functionality.

These tests verify that WebSocket connections can be established and that 
welcome messages are properly sent.
"""

import pytest
import asyncio
import websockets
import json
from .conftest import WebSocketMessageQueue


@pytest.mark.asyncio
async def test_websocket_connect_global():
    """Test connecting to the global WebSocket endpoint."""
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        # We expect a welcome message
        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        
        # Parse the message and verify it's a connection message
        try:
            data = json.loads(message)
            assert "event_type" in data, "Missing event_type field in response"
            assert data["event_type"] == "connection", f"Expected connection event, got {data['event_type']}"
            assert "message" in data, "Missing message field in response"
            assert "Connected to Paper Processing WebSocket" in data["message"], "Unexpected welcome message"
        except json.JSONDecodeError:
            pytest.fail(f"Server returned non-JSON response: {message}")


@pytest.mark.asyncio
async def test_websocket_connect_paper_specific(test_paper_id):
    """Test connecting to a paper-specific WebSocket endpoint."""
    async with websockets.connect(f"ws://localhost:8000/ws/{test_paper_id}") as websocket:
        # We expect a welcome message
        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        
        # Parse the message and verify it's a connection message for the specific paper
        try:
            data = json.loads(message)
            assert "event_type" in data, "Missing event_type field in response"
            assert data["event_type"] == "connection", f"Expected connection event, got {data['event_type']}"
            assert "message" in data, "Missing message field in response"
            assert f"Connected to updates for paper {test_paper_id}" in data["message"], "Unexpected welcome message"
        except json.JSONDecodeError:
            pytest.fail(f"Server returned non-JSON response: {message}")


@pytest.mark.asyncio
async def test_websocket_message_queue(websocket_client):
    """Test the WebSocketMessageQueue helper class."""
    # Create a message queue to collect messages
    message_queue = WebSocketMessageQueue(websocket_client)
    await message_queue.start_listening()
    
    # Wait a moment to receive the welcome message
    await asyncio.sleep(1)
    
    # Stop listening
    await message_queue.stop_listening()
    
    # Verify we received at least one message
    assert len(message_queue.messages) > 0, "No messages received"
    
    # Verify we received a connection message
    connection_messages = message_queue.get_messages_by_type("connection")
    assert len(connection_messages) > 0, "No connection messages received"
    assert "message" in connection_messages[0], "Missing message field in connection message"


@pytest.mark.asyncio
async def test_multiple_websocket_connections():
    """Test establishing multiple WebSocket connections simultaneously."""
    # Connect to the global WebSocket endpoint 3 times
    websockets_list = []
    try:
        for i in range(3):
            ws = await websockets.connect("ws://localhost:8000/ws")
            websockets_list.append(ws)
            
        # Verify all connections received welcome messages
        for i, ws in enumerate(websockets_list):
            message = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(message)
            assert data["event_type"] == "connection", f"Connection {i} did not receive welcome message"
            
    finally:
        # Clean up all connections
        for ws in websockets_list:
            await ws.close()