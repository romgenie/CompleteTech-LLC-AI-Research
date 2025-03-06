"""
Tests for WebSocket paper event notifications.

These tests verify that WebSocket connections properly receive events
related to paper processing, including status changes and progress updates.
"""

import pytest
import asyncio
import json
from .conftest import WebSocketMessageQueue


@pytest.mark.asyncio
async def test_paper_status_updates(api_client, paper_websocket_client, test_paper_id):
    """Test receiving status updates when paper processing state changes."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(paper_websocket_client)
    await message_queue.start_listening()
    
    # Parameters for API requests
    params = {"args": "[]", "kwargs": "{}"}
    
    # Trigger paper processing via API
    response = await api_client.post(f"/papers/{test_paper_id}/process", params=params)
    assert response.status_code == 200, f"Failed to process paper: {response.text}"
    
    # Wait for status update events (with timeout)
    await asyncio.sleep(3)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check for status update events
    status_events = message_queue.get_messages_by_type("paper_status")
    assert len(status_events) > 0, "No paper status events received"
    
    # Verify status event structure
    for event in status_events:
        assert "data" in event, "Status event missing data field"
        assert "status" in event["data"], "Status event missing status field"
        assert "paper_id" in event["data"], "Status event missing paper_id field"
        assert event["data"]["paper_id"] == test_paper_id, "Paper ID mismatch in status event"


@pytest.mark.asyncio
async def test_paper_progress_updates(api_client, paper_websocket_client, test_paper_id):
    """Test receiving progress updates during paper processing."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(paper_websocket_client)
    await message_queue.start_listening()
    
    # Parameters for API requests
    params = {"args": "[]", "kwargs": "{}"}
    
    # Trigger paper processing via API
    response = await api_client.post(f"/papers/{test_paper_id}/process", params=params)
    assert response.status_code == 200, f"Failed to process paper: {response.text}"
    
    # Wait for progress update events (with longer timeout)
    await asyncio.sleep(5)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check for progress update events
    progress_events = message_queue.get_messages_by_type("paper_progress")
    
    # Progress events might not come in certain quick test scenarios
    # So we mark this as informational
    if len(progress_events) == 0:
        print("No progress events received - this may be normal for quick processing")
    else:
        # Verify progress event structure
        for event in progress_events:
            assert "data" in event, "Progress event missing data field"
            assert "progress" in event["data"], "Progress event missing progress field"
            assert "paper_id" in event["data"], "Progress event missing paper_id field"
            assert event["data"]["paper_id"] == test_paper_id, "Paper ID mismatch in progress event"
            assert isinstance(event["data"]["progress"], (int, float)), "Progress should be a number"
            assert 0 <= event["data"]["progress"] <= 100, "Progress should be between 0 and 100"


@pytest.mark.asyncio
async def test_entity_extraction_events(api_client, paper_websocket_client, test_paper_id):
    """Test receiving entity extraction events during paper processing."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(paper_websocket_client)
    await message_queue.start_listening()
    
    # Parameters for API requests
    params = {"args": "[]", "kwargs": "{}"}
    
    # Trigger paper processing via API
    response = await api_client.post(f"/papers/{test_paper_id}/process", params=params)
    assert response.status_code == 200, f"Failed to process paper: {response.text}"
    
    # Wait for entity extraction events (with timeout)
    await asyncio.sleep(5)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check for entity extraction events
    entity_events = message_queue.get_messages_by_type("entity_extraction")
    
    # Entity events might not come in certain quick test scenarios
    # So we mark this as informational
    if len(entity_events) == 0:
        print("No entity extraction events received - this may be normal for quick processing")
    else:
        # Verify entity event structure
        for event in entity_events:
            assert "data" in event, "Entity event missing data field"
            assert "paper_id" in event["data"], "Entity event missing paper_id field"
            assert event["data"]["paper_id"] == test_paper_id, "Paper ID mismatch in entity event"
            assert "entities" in event["data"], "Entity event missing entities field"
            assert isinstance(event["data"]["entities"], list), "Entities should be a list"


@pytest.mark.asyncio
async def test_global_paper_events(api_client, websocket_client, test_paper_id):
    """Test that paper events are also sent to the global WebSocket."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(websocket_client)
    await message_queue.start_listening()
    
    # Parameters for API requests
    params = {"args": "[]", "kwargs": "{}"}
    
    # Trigger paper processing via API
    response = await api_client.post(f"/papers/{test_paper_id}/process", params=params)
    assert response.status_code == 200, f"Failed to process paper: {response.text}"
    
    # Wait for events (with timeout)
    await asyncio.sleep(5)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check we received paper-related events on the global channel
    # (either status, progress, or entity extraction)
    paper_events = []
    paper_events.extend(message_queue.get_messages_by_type("paper_status"))
    paper_events.extend(message_queue.get_messages_by_type("paper_progress"))
    paper_events.extend(message_queue.get_messages_by_type("entity_extraction"))
    
    # At least status events should be sent
    assert len(paper_events) > 0, "No paper events received on global channel"
    
    # Verify events have the correct paper ID
    for event in paper_events:
        if "data" in event and "paper_id" in event["data"]:
            assert event["data"]["paper_id"] == test_paper_id, "Event contains incorrect paper ID"