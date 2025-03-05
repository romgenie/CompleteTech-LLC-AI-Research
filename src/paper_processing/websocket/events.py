"""
WebSocket events for the Paper Processing Pipeline.

This module defines the events that can be sent over WebSocket connections.
These events represent status updates and notifications for paper processing.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

from ..models.paper import PaperStatus

# Configure logging
logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for paper processing updates."""
    
    # Status updates
    PAPER_UPLOADED = "paper_uploaded"
    PAPER_QUEUED = "paper_queued"
    PAPER_PROCESSING = "paper_processing"
    PAPER_EXTRACTING_ENTITIES = "paper_extracting_entities"
    PAPER_EXTRACTING_RELATIONSHIPS = "paper_extracting_relationships"
    PAPER_BUILDING_KNOWLEDGE_GRAPH = "paper_building_knowledge_graph"
    PAPER_ANALYZED = "paper_analyzed"
    PAPER_IMPLEMENTATION_READY = "paper_implementation_ready"
    PAPER_FAILED = "paper_failed"
    
    # Progress updates
    PAPER_PROGRESS = "paper_progress"
    PAPER_ENTITY_EXTRACTED = "paper_entity_extracted"
    PAPER_RELATIONSHIP_EXTRACTED = "paper_relationship_extracted"
    
    # Action updates
    PAPER_PROCESSING_STARTED = "paper_processing_started"
    PAPER_PROCESSING_COMPLETED = "paper_processing_completed"
    PAPER_PROCESSING_CANCELLED = "paper_processing_cancelled"
    
    # System events
    SYSTEM_STATUS = "system_status"
    SYSTEM_ERROR = "system_error"
    SYSTEM_METRICS = "system_metrics"


class PaperEvent(BaseModel):
    """
    Base model for paper processing events.
    
    This model represents an event related to paper processing.
    """
    
    event_type: EventType = Field(..., description="Type of the event")
    paper_id: Optional[str] = Field(None, description="ID of the paper the event relates to")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time the event occurred")
    message: str = Field(..., description="Human-readable event message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional event data")


class StatusUpdateEvent(PaperEvent):
    """
    Event for paper status updates.
    
    This event is sent when a paper's status changes.
    """
    
    status: str = Field(..., description="New paper status")
    progress: int = Field(..., description="Processing progress percentage")
    previous_status: Optional[str] = Field(None, description="Previous paper status")


class ProgressUpdateEvent(PaperEvent):
    """
    Event for paper processing progress updates.
    
    This event is sent to update clients on processing progress.
    """
    
    progress: int = Field(..., description="Processing progress percentage")
    step: str = Field(..., description="Current processing step")
    step_progress: int = Field(..., description="Progress percentage for the current step")
    steps_completed: int = Field(..., description="Number of steps completed")
    steps_total: int = Field(..., description="Total number of steps")


class EntityExtractionEvent(PaperEvent):
    """
    Event for entity extraction updates.
    
    This event is sent when entities are extracted from a paper.
    """
    
    entity_count: int = Field(..., description="Number of entities extracted")
    entity_types: List[str] = Field(..., description="Types of entities extracted")


class RelationshipExtractionEvent(PaperEvent):
    """
    Event for relationship extraction updates.
    
    This event is sent when relationships are extracted from a paper.
    """
    
    relationship_count: int = Field(..., description="Number of relationships extracted")
    relationship_types: List[str] = Field(..., description="Types of relationships extracted")


class SystemStatusEvent(PaperEvent):
    """
    Event for system status updates.
    
    This event is sent to update clients on the system's overall status.
    """
    
    status: str = Field(..., description="System status")
    active_tasks: int = Field(..., description="Number of active tasks")
    queue_length: int = Field(..., description="Number of tasks in the queue")
    worker_count: int = Field(..., description="Number of active workers")


# Type alias for any event type
AnyEvent = Union[
    StatusUpdateEvent,
    ProgressUpdateEvent,
    EntityExtractionEvent,
    RelationshipExtractionEvent,
    SystemStatusEvent
]


def create_status_update_event(
    paper_id: str,
    status: str,
    progress: int,
    message: str,
    previous_status: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> StatusUpdateEvent:
    """
    Create a status update event.
    
    Args:
        paper_id: ID of the paper
        status: New paper status
        progress: Processing progress percentage
        message: Human-readable event message
        previous_status: Previous paper status
        data: Additional event data
        
    Returns:
        StatusUpdateEvent object
    """
    # Determine event type based on status
    event_type_map = {
        "uploaded": EventType.PAPER_UPLOADED,
        "queued": EventType.PAPER_QUEUED,
        "processing": EventType.PAPER_PROCESSING,
        "extracting_entities": EventType.PAPER_EXTRACTING_ENTITIES,
        "extracting_relationships": EventType.PAPER_EXTRACTING_RELATIONSHIPS,
        "building_knowledge_graph": EventType.PAPER_BUILDING_KNOWLEDGE_GRAPH,
        "analyzed": EventType.PAPER_ANALYZED,
        "implementation_ready": EventType.PAPER_IMPLEMENTATION_READY,
        "failed": EventType.PAPER_FAILED
    }
    
    event_type = event_type_map.get(status, EventType.PAPER_PROGRESS)
    
    return StatusUpdateEvent(
        event_type=event_type,
        paper_id=paper_id,
        status=status,
        progress=progress,
        message=message,
        previous_status=previous_status,
        data=data
    )


def create_progress_update_event(
    paper_id: str,
    progress: int,
    step: str,
    step_progress: int,
    steps_completed: int,
    steps_total: int,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> ProgressUpdateEvent:
    """
    Create a progress update event.
    
    Args:
        paper_id: ID of the paper
        progress: Processing progress percentage
        step: Current processing step
        step_progress: Progress percentage for the current step
        steps_completed: Number of steps completed
        steps_total: Total number of steps
        message: Human-readable event message
        data: Additional event data
        
    Returns:
        ProgressUpdateEvent object
    """
    return ProgressUpdateEvent(
        event_type=EventType.PAPER_PROGRESS,
        paper_id=paper_id,
        progress=progress,
        step=step,
        step_progress=step_progress,
        steps_completed=steps_completed,
        steps_total=steps_total,
        message=message,
        data=data
    )


def create_entity_extraction_event(
    paper_id: str,
    entity_count: int,
    entity_types: List[str],
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> EntityExtractionEvent:
    """
    Create an entity extraction event.
    
    Args:
        paper_id: ID of the paper
        entity_count: Number of entities extracted
        entity_types: Types of entities extracted
        message: Human-readable event message
        data: Additional event data
        
    Returns:
        EntityExtractionEvent object
    """
    return EntityExtractionEvent(
        event_type=EventType.PAPER_ENTITY_EXTRACTED,
        paper_id=paper_id,
        entity_count=entity_count,
        entity_types=entity_types,
        message=message,
        data=data
    )


def create_relationship_extraction_event(
    paper_id: str,
    relationship_count: int,
    relationship_types: List[str],
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> RelationshipExtractionEvent:
    """
    Create a relationship extraction event.
    
    Args:
        paper_id: ID of the paper
        relationship_count: Number of relationships extracted
        relationship_types: Types of relationships extracted
        message: Human-readable event message
        data: Additional event data
        
    Returns:
        RelationshipExtractionEvent object
    """
    return RelationshipExtractionEvent(
        event_type=EventType.PAPER_RELATIONSHIP_EXTRACTED,
        paper_id=paper_id,
        relationship_count=relationship_count,
        relationship_types=relationship_types,
        message=message,
        data=data
    )


def create_system_status_event(
    status: str,
    active_tasks: int,
    queue_length: int,
    worker_count: int,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> SystemStatusEvent:
    """
    Create a system status event.
    
    Args:
        status: System status
        active_tasks: Number of active tasks
        queue_length: Number of tasks in the queue
        worker_count: Number of active workers
        message: Human-readable event message
        data: Additional event data
        
    Returns:
        SystemStatusEvent object
    """
    return SystemStatusEvent(
        event_type=EventType.SYSTEM_STATUS,
        paper_id=None,
        status=status,
        active_tasks=active_tasks,
        queue_length=queue_length,
        worker_count=worker_count,
        message=message,
        data=data
    )


# Import at the end to avoid circular imports
from .connection import connection_manager

async def broadcast_paper_event(event: PaperEvent) -> None:
    """
    Broadcast a paper event to relevant WebSocket clients.
    
    Args:
        event: The event to broadcast
    """
    if not event.paper_id:
        logger.warning("Cannot broadcast paper event without paper_id")
        return
    
    # Convert event to dict for JSON serialization
    message = event.dict()
    
    # Broadcast to clients subscribed to this paper
    await connection_manager.broadcast_to_paper(event.paper_id, message)


async def broadcast_system_event(event: PaperEvent) -> None:
    """
    Broadcast a system event to all WebSocket clients.
    
    Args:
        event: The system event to broadcast
    """
    # Convert event to dict for JSON serialization
    message = event.dict()
    
    # Broadcast to all clients
    await connection_manager.broadcast(message)