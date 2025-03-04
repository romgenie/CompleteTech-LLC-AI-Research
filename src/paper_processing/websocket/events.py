"""
WebSocket events for the Paper Processing Pipeline.

This module defines the event types and handling for WebSocket communication
in the Paper Processing Pipeline. These events enable real-time status updates
for papers being processed.

Current Implementation Status:
- Event types defined ✓
- Core event structure designed ✓

Upcoming Development:
- Event broadcasting implementation
- Event serialization and deserialization
- Client event handling
- Connection management integration
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from datetime import datetime

from ..models.paper import PaperStatus


class EventType(str, Enum):
    """Types of WebSocket events for paper processing."""
    
    # Status events
    STATUS_CHANGED = "status_changed"
    PROGRESS_UPDATED = "progress_updated"
    
    # Processing events
    PROCESSING_STARTED = "processing_started"
    PROCESSING_COMPLETED = "processing_completed"
    PROCESSING_FAILED = "processing_failed"
    
    # Entity events
    ENTITY_EXTRACTED = "entity_extracted"
    RELATIONSHIP_EXTRACTED = "relationship_extracted"
    
    # Knowledge graph events
    KNOWLEDGE_GRAPH_UPDATED = "knowledge_graph_updated"
    
    # System events
    SYSTEM_STATUS = "system_status"
    ERROR = "error"


class StatusEvent(BaseModel):
    """Event for paper status changes."""
    
    event_type: EventType = Field(EventType.STATUS_CHANGED, const=True)
    paper_id: str = Field(..., description="Paper ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    old_status: PaperStatus = Field(..., description="Previous status")
    new_status: PaperStatus = Field(..., description="New status")
    message: Optional[str] = Field(None, description="Status change message")


class ProgressEvent(BaseModel):
    """Event for paper processing progress updates."""
    
    event_type: EventType = Field(EventType.PROGRESS_UPDATED, const=True)
    paper_id: str = Field(..., description="Paper ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    progress: float = Field(..., description="Overall progress (0-1)", ge=0.0, le=1.0)
    step: str = Field(..., description="Current processing step")
    step_progress: float = Field(..., description="Step progress (0-1)", ge=0.0, le=1.0)
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class ProcessingEvent(BaseModel):
    """Event for paper processing lifecycle events."""
    
    event_type: EventType = Field(..., description="Processing event type")
    paper_id: str = Field(..., description="Paper ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(None, description="Processing details")
    task_id: Optional[str] = Field(None, description="Celery task ID")
    message: Optional[str] = Field(None, description="Processing message")


class EntityEvent(BaseModel):
    """Event for entity extraction updates."""
    
    event_type: EventType = Field(EventType.ENTITY_EXTRACTED, const=True)
    paper_id: str = Field(..., description="Paper ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    entity_id: str = Field(..., description="Entity ID")
    entity_type: str = Field(..., description="Entity type")
    entity_name: str = Field(..., description="Entity name")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class RelationshipEvent(BaseModel):
    """Event for relationship extraction updates."""
    
    event_type: EventType = Field(EventType.RELATIONSHIP_EXTRACTED, const=True)
    paper_id: str = Field(..., description="Paper ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    relationship_id: str = Field(..., description="Relationship ID")
    relationship_type: str = Field(..., description="Relationship type")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class ErrorEvent(BaseModel):
    """Event for error notifications."""
    
    event_type: EventType = Field(EventType.ERROR, const=True)
    paper_id: Optional[str] = Field(None, description="Paper ID, if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


class SystemStatusEvent(BaseModel):
    """Event for system status updates."""
    
    event_type: EventType = Field(EventType.SYSTEM_STATUS, const=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    queue_size: int = Field(..., description="Number of papers in queue")
    active_workers: int = Field(..., description="Number of active workers")
    processing_rate: float = Field(..., description="Papers per minute")
    system_load: float = Field(..., description="System load (0-1)", ge=0.0, le=1.0)


# Type alias for any event type
PaperEvent = Union[
    StatusEvent, 
    ProgressEvent, 
    ProcessingEvent, 
    EntityEvent,
    RelationshipEvent,
    ErrorEvent,
    SystemStatusEvent
]


# This is a placeholder for the future implementation
def broadcast_event(event: PaperEvent) -> None:
    """
    Broadcast an event to WebSocket clients.
    
    Args:
        event: The event to broadcast
    """
    # This will be implemented in upcoming sprints
    pass