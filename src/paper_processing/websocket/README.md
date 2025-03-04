# WebSocket Integration for Paper Processing Pipeline

## Overview

This directory contains the WebSocket integration for the Paper Processing Pipeline, providing real-time status updates for papers being processed. It follows the WebSocket protocol to enable bidirectional communication between the server and clients.

## Components

### Event Definitions

The `events.py` file defines the event types and structures for WebSocket communication:

- **Status Events**: Updates about paper status changes
- **Progress Events**: Real-time progress updates during processing
- **Entity Events**: Notifications about extracted entities
- **Relationship Events**: Notifications about extracted relationships
- **Error Events**: Notifications about processing errors
- **System Events**: Updates about the overall system status

### Connection Management

The `connection.py` file handles WebSocket connection management:

- **Client Tracking**: Manages active WebSocket connections
- **Authentication**: Validates client connections
- **Subscription**: Allows clients to subscribe to specific papers or event types
- **Broadcasting**: Sends events to relevant subscribers

## Event Types

The WebSocket integration supports the following event types:

### `STATUS_CHANGED`

Sent when a paper's status changes:

```json
{
  "event_type": "status_changed",
  "paper_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-03-01T10:35:00Z",
  "old_status": "uploaded",
  "new_status": "processing",
  "message": "Processing started"
}
```

### `PROGRESS_UPDATED`

Sent to provide real-time progress updates:

```json
{
  "event_type": "progress_updated",
  "paper_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-03-01T10:36:00Z",
  "progress": 0.35,
  "step": "entity_extraction",
  "step_progress": 0.6,
  "estimated_completion": "2025-03-01T10:45:00Z"
}
```

### `ENTITY_EXTRACTED`

Sent when an entity is extracted from a paper:

```json
{
  "event_type": "entity_extracted",
  "paper_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-03-01T10:36:30Z",
  "entity_id": "ent-123",
  "entity_type": "MODEL",
  "entity_name": "Transformer",
  "confidence": 0.95
}
```

### `RELATIONSHIP_EXTRACTED`

Sent when a relationship is extracted from a paper:

```json
{
  "event_type": "relationship_extracted",
  "paper_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-03-01T10:37:00Z",
  "relationship_id": "rel-123",
  "relationship_type": "TRAINED_ON",
  "source_id": "ent-123",
  "target_id": "ent-456",
  "confidence": 0.85
}
```

### `ERROR`

Sent when an error occurs during processing:

```json
{
  "event_type": "error",
  "paper_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-03-01T10:38:00Z",
  "error_code": "processing_failed",
  "error_message": "Failed to extract entities",
  "details": {
    "step": "entity_extraction",
    "task_id": "4f8ed542-a2ea-4a47-92b3-5fe0ae7740f2"
  }
}
```

### `SYSTEM_STATUS`

Sent to provide system-wide status updates:

```json
{
  "event_type": "system_status",
  "timestamp": "2025-03-01T10:40:00Z",
  "queue_size": 5,
  "active_workers": 3,
  "processing_rate": 2.5,
  "system_load": 0.7
}
```

## Client Usage

Clients can connect to the WebSocket endpoint and subscribe to events:

```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/papers');

// Authentication message
socket.send(JSON.stringify({
  type: 'authenticate',
  token: 'JWT_TOKEN'
}));

// Subscribe to a specific paper
socket.send(JSON.stringify({
  type: 'subscribe',
  paper_id: '123e4567-e89b-12d3-a456-426614174000'
}));

// Handle incoming events
socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received event:', data);
  
  switch(data.event_type) {
    case 'status_changed':
      updatePaperStatus(data);
      break;
    case 'progress_updated':
      updateProgressBar(data);
      break;
    case 'error':
      showError(data);
      break;
  }
};
```

## Server Integration

The WebSocket server integrates with the Paper Processing Pipeline tasks:

```python
# In Celery task
async def process_paper(paper_id: str):
    # Process paper...
    
    # Broadcast status change event
    status_event = StatusEvent(
        paper_id=paper_id,
        old_status=PaperStatus.UPLOADED,
        new_status=PaperStatus.PROCESSING,
        message="Processing started"
    )
    await broadcast_event(status_event)
    
    # Update progress as processing continues
    progress_event = ProgressEvent(
        paper_id=paper_id,
        progress=0.35,
        step="entity_extraction",
        step_progress=0.6,
        estimated_completion=datetime.utcnow() + timedelta(minutes=10)
    )
    await broadcast_event(progress_event)
```

## Future Work

- **Connection Pool**: Implement connection pooling for scalability
- **Heartbeat Mechanism**: Add ping/pong heartbeat for long-lived connections
- **Offline Recovery**: Store recent events for reconnecting clients
- **Compression**: Implement message compression for large payloads
- **Rate Limiting**: Add rate limiting to prevent abuse