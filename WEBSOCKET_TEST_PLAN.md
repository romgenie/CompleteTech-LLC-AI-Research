# WebSocket Integration Test Implementation Plan

This document outlines the plan for implementing WebSocket integration tests for our paper processing system. These tests will verify that real-time updates are properly sent through WebSocket connections when paper processing events occur.

## 1. Create Test Directory Structure

```
tests/
└── integration_tests/
    └── websocket/
        ├── __init__.py
        ├── conftest.py
        ├── test_websocket_connection.py
        ├── test_websocket_paper_events.py
        └── test_websocket_system_events.py
```

## 2. Create Fixtures in conftest.py

### WebSocket Test Client Fixture

```python
@pytest.fixture
async def websocket_client():
    """Create a WebSocket client for testing."""
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        yield websocket
```

### Paper-Specific WebSocket Client Fixture

```python
@pytest.fixture
async def paper_websocket_client(test_paper_id):
    """Create a WebSocket client for a specific paper."""
    async with websockets.connect(f"ws://localhost:8000/ws/{test_paper_id}") as websocket:
        yield websocket
```

### Test Paper Setup Fixture

```python
@pytest.fixture
async def test_paper_id(api_client):
    """Upload a test paper and return its ID."""
    test_file = Path(__file__).parent.parent.parent / "test_papers" / "test_paper_content.txt"
    
    with open(test_file, "rb") as f:
        file_content = f.read()
    
    files = {"file": ("test_paper.txt", file_content, "text/plain")}
    response = await api_client.post("/papers/", files=files)
    assert response.status_code == 201
    
    paper_id = response.json()["id"]
    yield paper_id
    
    # Clean up after test
    await api_client.delete(f"/papers/{paper_id}")
```

### WebSocket Message Queue Helper

```python
class WebSocketMessageQueue:
    """Helper to collect WebSocket messages."""
    def __init__(self, websocket):
        self.websocket = websocket
        self.messages = []
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
                message = await asyncio.wait_for(self.websocket.receive_json(), timeout=1.0)
                self.messages.append(message)
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                print(f"Error receiving message: {e}")
                self._listening = False
                
    async def stop_listening(self):
        """Stop listening for messages."""
        self._listening = False
        if self._task:
            await self._task
            
    def get_messages_by_type(self, event_type):
        """Get messages of a specific type."""
        return [msg for msg in self.messages if msg.get("event_type") == event_type]
```

## 3. Test Cases to Implement

### A. Connection Tests (test_websocket_connection.py)

```python
@pytest.mark.asyncio
async def test_websocket_connect_global():
    """Test connecting to the global WebSocket endpoint."""
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        # We expect a welcome message
        message = await websocket.receive_json()
        assert message["event_type"] == "connection"
        assert "Connected to Paper Processing WebSocket" in message["message"]

@pytest.mark.asyncio
async def test_websocket_connect_paper_specific(test_paper_id):
    """Test connecting to a paper-specific WebSocket endpoint."""
    async with websockets.connect(f"ws://localhost:8000/ws/{test_paper_id}") as websocket:
        # We expect a welcome message
        message = await websocket.receive_json()
        assert message["event_type"] == "connection"
        assert f"Connected to updates for paper {test_paper_id}" in message["message"]
```

### B. Paper Event Tests (test_websocket_paper_events.py)

```python
@pytest.mark.asyncio
async def test_paper_status_updates(api_client, paper_websocket_client, test_paper_id):
    """Test receiving status updates when paper processing state changes."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(paper_websocket_client)
    await message_queue.start_listening()
    
    # Trigger paper processing via API
    response = await api_client.post(f"/papers/{test_paper_id}/process")
    assert response.status_code == 200
    
    # Wait for messages to arrive (with timeout)
    await asyncio.sleep(2)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check for status update events
    status_events = message_queue.get_messages_by_type("paper_status")
    assert len(status_events) > 0
    
    # Verify at least one status changed to "queued"
    queued_events = [e for e in status_events if e["data"]["status"] == "queued"]
    assert len(queued_events) > 0
```

### C. System Event Tests (test_websocket_system_events.py)

```python
@pytest.mark.asyncio
async def test_system_status_events(websocket_client):
    """Test receiving system status events."""
    # Create a message queue to collect WebSocket messages
    message_queue = WebSocketMessageQueue(websocket_client)
    await message_queue.start_listening()
    
    # Wait for system status events (these might be periodic)
    await asyncio.sleep(5)
    
    # Stop listening for messages
    await message_queue.stop_listening()
    
    # Check for system status events
    system_events = message_queue.get_messages_by_type("system_status")
    assert len(system_events) > 0
```

## 4. Required Dependencies

Ensure these dependencies are installed:
- pytest-asyncio (for async test support)
- websockets (for WebSocket client)
- httpx (for API client)

## 5. Environment Setup

The tests require:
- Running MongoDB instance
- Running Neo4j instance
- Running Redis server (for Celery)
- Running FastAPI application with WebSocket support

## 6. Implementation Steps

1. **Day 1: Setup**
   - Create the directory structure
   - Create conftest.py with basic fixtures
   - Implement WebSocketMessageQueue helper

2. **Day 2: Connection Tests**
   - Implement test_websocket_connection.py
   - Test basic connectivity to WebSocket endpoints

3. **Day 3: Paper Event Tests**
   - Implement test_websocket_paper_events.py
   - Test status updates and progress notifications

4. **Day 4: System Event Tests**
   - Implement test_websocket_system_events.py
   - Test system-wide notifications

5. **Day 5: Integration**
   - Update run_tests.sh to include WebSocket tests
   - Add WebSocket tests to CI/CD pipeline
   - Update documentation

## 7. Success Criteria

WebSocket integration tests will be considered successful when:

1. All connection tests pass, verifying basic WebSocket connectivity
2. Paper event tests detect and validate status updates
3. System event tests correctly capture system-wide notifications
4. Tests run consistently in both local and CI environments
5. Documentation is updated to describe WebSocket testing

## 8. Resources

- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [Pytest AsyncIO Documentation](https://github.com/pytest-dev/pytest-asyncio)
- [Websockets Python Library](https://websockets.readthedocs.io/)