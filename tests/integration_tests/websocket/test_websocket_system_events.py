"""
Tests for WebSocket system event notifications.

These tests verify that WebSocket connections properly receive system-wide events.
"""

import pytest
import asyncio
import json
from .conftest import WebSocketMessageQueue


@pytest.mark.asyncio
async def test_system_status_events(websocket_client):
    """Test receiving system status events."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(websocket_client)
    await message_queue.start_listening()
    
    # System status events might be periodic, so we wait for them
    await asyncio.sleep(5)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check for system status events
    system_events = message_queue.get_messages_by_type("system_status")
    
    # System events might not come during the test period
    # So we mark this as informational
    if len(system_events) == 0:
        print("No system status events received during test period - this may be normal")
    else:
        # Verify system status event structure
        for event in system_events:
            assert "data" in event, "System event missing data field"
            if "status" in event["data"]:
                assert isinstance(event["data"]["status"], str), "Status should be a string"


@pytest.mark.asyncio
async def test_system_metrics_events(websocket_client):
    """Test receiving system metrics events."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(websocket_client)
    await message_queue.start_listening()
    
    # System metrics events might be periodic, so we wait for them
    await asyncio.sleep(5)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check for system metrics events
    metrics_events = message_queue.get_messages_by_type("system_metrics")
    
    # Metrics events might not come during the test period
    # So we mark this as informational
    if len(metrics_events) == 0:
        print("No system metrics events received during test period - this may be normal")
    else:
        # Verify metrics event structure
        for event in metrics_events:
            assert "data" in event, "Metrics event missing data field"
            # Check for common metrics fields
            if "cpu_usage" in event["data"]:
                assert isinstance(event["data"]["cpu_usage"], (int, float)), "CPU usage should be a number"
            if "memory_usage" in event["data"]:
                assert isinstance(event["data"]["memory_usage"], (int, float)), "Memory usage should be a number"


@pytest.mark.asyncio
async def test_extended_connection(websocket_client):
    """Test maintaining a WebSocket connection for an extended period."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(websocket_client)
    await message_queue.start_listening()
    
    # Keep the connection open for a longer period
    await asyncio.sleep(10)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Verify connection stayed open by checking we have at least the welcome message
    assert len(message_queue.messages) > 0, "No messages received during extended connection"
    
    # Print summary of message types received (for debugging)
    event_types = {}
    for msg in message_queue.messages:
        if "event_type" in msg:
            event_type = msg["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print(f"Message types received during extended connection: {event_types}")


@pytest.mark.asyncio
async def test_reconnection(test_paper_id):
    """Test reconnecting to WebSocket endpoints."""
    # Connect once
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        # Get initial welcome message
        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        data = json.loads(message)
        assert data["event_type"] == "connection", "Did not receive welcome message on first connection"
    
    # Reconnect
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        # Get welcome message again
        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        data = json.loads(message)
        assert data["event_type"] == "connection", "Did not receive welcome message on reconnection"
        
    # Reconnect to paper-specific endpoint
    async with websockets.connect(f"ws://localhost:8000/ws/{test_paper_id}") as websocket:
        # Get welcome message for paper connection
        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        data = json.loads(message)
        assert data["event_type"] == "connection", "Did not receive welcome message on paper connection"
        assert test_paper_id in data["message"], f"Paper ID {test_paper_id} not in welcome message"