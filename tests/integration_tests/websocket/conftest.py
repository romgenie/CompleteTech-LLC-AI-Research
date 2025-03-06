"""
Test fixtures for WebSocket integration tests.
"""

import pytest
import asyncio
from pathlib import Path
import websockets
import httpx
from typing import List, Dict, Any, Optional


class WebSocketMessageQueue:
    """Helper to collect WebSocket messages."""
    
    def __init__(self, websocket):
        """Initialize the WebSocket message queue.
        
        Args:
            websocket: WebSocket client connection
        """
        self.websocket = websocket
        self.messages: List[Dict[str, Any]] = []
        self._listening = False
        self._task = None

    async def start_listening(self):
        """Start listening for messages in the background."""
        self._listening = True
        self._task = asyncio.create_task(self._listen())
        
    async def _listen(self):
        """Listen for WebSocket messages."""
        while self._listening:
            try:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                # Try to parse as JSON, fall back to string if that fails
                try:
                    import json
                    parsed_message = json.loads(message)
                    self.messages.append(parsed_message)
                except json.JSONDecodeError:
                    self.messages.append({"text": message})
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                print(f"Error receiving message: {e}")
                self._listening = False
                
    async def stop_listening(self):
        """Stop listening for messages."""
        self._listening = False
        if self._task:
            try:
                self._task.cancel()
                await asyncio.gather(self._task, return_exceptions=True)
            except asyncio.CancelledError:
                pass
            
    def get_messages_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Get messages of a specific type.
        
        Args:
            event_type: The type of event to filter by
            
        Returns:
            List of messages matching the specified event type
        """
        return [msg for msg in self.messages if msg.get("event_type") == event_type]


@pytest.fixture
async def api_client():
    """Create an API client for testing."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        yield client


@pytest.fixture
async def test_paper_id(api_client):
    """Upload a test paper and return its ID.
    
    Args:
        api_client: HTTP client fixture
        
    Returns:
        String ID of the uploaded test paper
    """
    test_file = Path(__file__).parent.parent.parent / "test_papers" / "test_paper_content.txt"
    
    with open(test_file, "rb") as f:
        file_content = f.read()
    
    files = {"file": ("test_paper.txt", file_content, "text/plain")}
    params = {"args": "[]", "kwargs": "{}"}  # Required query parameters
    
    response = await api_client.post("/papers/", files=files, params=params)
    assert response.status_code == 201, f"Failed to upload paper: {response.text}"
    
    paper_id = response.json()["id"]
    yield paper_id
    
    # Clean up after test
    await api_client.delete(f"/papers/{paper_id}", params=params)


@pytest.fixture
async def websocket_client():
    """Create a WebSocket client for testing.
    
    Returns:
        WebSocket client connected to the global WebSocket endpoint
    """
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        yield websocket


@pytest.fixture
async def paper_websocket_client(test_paper_id):
    """Create a WebSocket client for a specific paper.
    
    Args:
        test_paper_id: ID of the test paper
        
    Returns:
        WebSocket client connected to the paper-specific WebSocket endpoint
    """
    async with websockets.connect(f"ws://localhost:8000/ws/{test_paper_id}") as websocket:
        yield websocket