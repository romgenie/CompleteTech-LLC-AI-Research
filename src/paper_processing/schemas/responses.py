"""
Response schemas for the Paper Processing Pipeline API.

This module defines the Pydantic models for API responses in the Paper Processing
Pipeline. These models are used to validate outgoing responses and generate
API documentation.

Current Implementation Status:
- Core response schemas defined ✓
- Status response models implemented ✓
- Documentation examples created ✓

Upcoming Development:
- Additional response fields
- Result pagination
- Advanced statistics responses
- WebSocket message responses
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ..models.paper import PaperStatus, ProcessingEvent


class ProcessingStepStatus(BaseModel):
    """Status of a processing step."""
    
    name: str = Field(..., description="Processing step name")
    status: str = Field(..., description="Step status (pending, in_progress, completed, failed)")
    progress: float = Field(..., description="Step progress (0-1)", ge=0.0, le=1.0)
    started_at: Optional[datetime] = Field(None, description="When the step started")
    completed_at: Optional[datetime] = Field(None, description="When the step completed")
    message: Optional[str] = Field(None, description="Status message")


class PaperStatusResponse(BaseModel):
    """Response model for paper status."""
    
    paper_id: str = Field(..., description="Paper ID")
    title: str = Field(..., description="Paper title")
    status: PaperStatus = Field(..., description="Current status")
    progress: float = Field(..., description="Overall progress (0-1)", ge=0.0, le=1.0)
    uploaded_at: datetime = Field(..., description="When the paper was uploaded")
    last_updated: datetime = Field(..., description="When the status was last updated")
    history: List[ProcessingEvent] = Field(default_factory=list, description="Processing history")
    steps: List[ProcessingStepStatus] = Field(default_factory=list, description="Processing steps status")
    task_id: Optional[str] = Field(None, description="Celery task ID if processing")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    message: Optional[str] = Field(None, description="Status message")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "paper_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Attention Is All You Need",
                "status": "processing",
                "progress": 0.35,
                "uploaded_at": "2025-03-01T10:30:00Z",
                "last_updated": "2025-03-01T10:35:00Z",
                "history": [
                    {
                        "timestamp": "2025-03-01T10:30:00Z",
                        "status": "uploaded",
                        "message": "Paper uploaded successfully"
                    },
                    {
                        "timestamp": "2025-03-01T10:32:00Z",
                        "status": "queued",
                        "message": "Paper queued for processing"
                    },
                    {
                        "timestamp": "2025-03-01T10:35:00Z",
                        "status": "processing",
                        "message": "Processing started"
                    }
                ],
                "steps": [
                    {
                        "name": "document_processing",
                        "status": "completed",
                        "progress": 1.0,
                        "started_at": "2025-03-01T10:35:00Z",
                        "completed_at": "2025-03-01T10:36:00Z",
                        "message": "Document processed successfully"
                    },
                    {
                        "name": "entity_extraction",
                        "status": "in_progress",
                        "progress": 0.6,
                        "started_at": "2025-03-01T10:36:00Z",
                        "completed_at": None,
                        "message": "Extracting entities"
                    },
                    {
                        "name": "relationship_extraction",
                        "status": "pending",
                        "progress": 0.0,
                        "started_at": None,
                        "completed_at": None,
                        "message": None
                    }
                ],
                "task_id": "4f8ed542-a2ea-4a47-92b3-5fe0ae7740f2",
                "estimated_completion": "2025-03-01T10:45:00Z",
                "message": "Processing on schedule"
            }
        }


class ProcessingResultResponse(BaseModel):
    """Response model for paper processing result."""
    
    paper_id: str = Field(..., description="Paper ID")
    status: str = Field(..., description="Result status (success, partial_success, failed)")
    task_id: str = Field(..., description="Celery task ID")
    started_at: datetime = Field(..., description="When processing started")
    completed_at: datetime = Field(..., description="When processing completed")
    processing_time: float = Field(..., description="Processing time in seconds")
    entity_count: int = Field(..., description="Number of entities extracted")
    relationship_count: int = Field(..., description="Number of relationships extracted")
    knowledge_graph_id: Optional[str] = Field(None, description="Knowledge graph ID if created")
    implementation_ready: bool = Field(..., description="Whether ready for implementation")
    message: str = Field(..., description="Result message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "paper_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "success",
                "task_id": "4f8ed542-a2ea-4a47-92b3-5fe0ae7740f2",
                "started_at": "2025-03-01T10:35:00Z",
                "completed_at": "2025-03-01T10:45:00Z",
                "processing_time": 600.0,
                "entity_count": 42,
                "relationship_count": 128,
                "knowledge_graph_id": "kg-123e4567-e89b-12d3-a456-426614174000",
                "implementation_ready": True,
                "message": "Processing completed successfully",
                "details": {
                    "entity_types": {
                        "MODEL": 3,
                        "ALGORITHM": 5,
                        "DATASET": 2,
                        "PAPER": 10,
                        "AUTHOR": 8
                    },
                    "relationship_types": {
                        "CITES": 35,
                        "TRAINED_ON": 3,
                        "OUTPERFORMS": 12,
                        "AUTHORED_BY": 68
                    }
                }
            }
        }


class BatchStatusResponse(BaseModel):
    """Response model for batch processing status."""
    
    batch_id: str = Field(..., description="Batch ID")
    paper_count: int = Field(..., description="Number of papers in batch")
    completed_count: int = Field(..., description="Number of completed papers")
    failed_count: int = Field(..., description="Number of failed papers")
    in_progress_count: int = Field(..., description="Number of papers still in progress")
    queued_count: int = Field(..., description="Number of papers still queued")
    overall_progress: float = Field(..., description="Overall batch progress (0-1)", ge=0.0, le=1.0)
    started_at: datetime = Field(..., description="When batch processing started")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    message: str = Field(..., description="Status message")
    papers: List[PaperStatusResponse] = Field(default_factory=list, description="Individual paper statuses")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "batch_id": "batch-123e4567-e89b-12d3-a456-426614174000",
                "paper_count": 3,
                "completed_count": 1,
                "failed_count": 0,
                "in_progress_count": 1,
                "queued_count": 1,
                "overall_progress": 0.33,
                "started_at": "2025-03-01T10:30:00Z",
                "estimated_completion": "2025-03-01T11:00:00Z",
                "message": "Batch processing in progress",
                "papers": [
                    {
                        "paper_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Paper 1",
                        "status": "analyzed",
                        "progress": 1.0,
                        "message": "Processing completed"
                    },
                    {
                        "paper_id": "123e4567-e89b-12d3-a456-426614174001",
                        "title": "Paper 2",
                        "status": "processing",
                        "progress": 0.5,
                        "message": "Processing in progress"
                    },
                    {
                        "paper_id": "123e4567-e89b-12d3-a456-426614174002",
                        "title": "Paper 3",
                        "status": "queued",
                        "progress": 0.0,
                        "message": "Waiting in queue"
                    }
                ]
            }
        }


class PaperSearchResponse(BaseModel):
    """Response model for paper search."""
    
    count: int = Field(..., description="Number of results returned")
    total: int = Field(..., description="Total number of matching results")
    limit: int = Field(..., description="Maximum number of results requested")
    offset: int = Field(..., description="Number of results skipped")
    papers: List[Dict[str, Any]] = Field(default_factory=list, description="Search results")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "count": 2,
                "total": 15,
                "limit": 10,
                "offset": 0,
                "papers": [
                    {
                        "paper_id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Attention Is All You Need",
                        "authors": ["Ashish Vaswani", "Noam Shazeer"],
                        "year": 2017,
                        "status": "analyzed",
                        "uploaded_at": "2025-03-01T10:30:00Z",
                        "entity_count": 42,
                        "relationship_count": 128
                    },
                    {
                        "paper_id": "123e4567-e89b-12d3-a456-426614174001",
                        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                        "authors": ["Jacob Devlin", "Ming-Wei Chang"],
                        "year": 2018,
                        "status": "processing",
                        "uploaded_at": "2025-03-02T09:15:00Z",
                        "entity_count": 0,
                        "relationship_count": 0
                    }
                ]
            }
        }


class ProcessingStatisticsResponse(BaseModel):
    """Response model for processing statistics."""
    
    total_papers: int = Field(..., description="Total number of papers")
    papers_by_status: Dict[str, int] = Field(..., description="Papers count by status")
    avg_processing_time: float = Field(..., description="Average processing time in seconds")
    avg_entity_count: float = Field(..., description="Average number of entities per paper")
    avg_relationship_count: float = Field(..., description="Average number of relationships per paper")
    processing_history: List[Dict[str, Any]] = Field(..., description="Processing counts over time")
    queue_length: int = Field(..., description="Current queue length")
    active_workers: int = Field(..., description="Number of active workers")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "total_papers": 150,
                "papers_by_status": {
                    "uploaded": 15,
                    "queued": 5,
                    "processing": 10,
                    "extracting_entities": 8,
                    "extracting_relationships": 7,
                    "building_knowledge_graph": 5,
                    "analyzed": 95,
                    "implementation_ready": 80,
                    "failed": 5
                },
                "avg_processing_time": 450.5,
                "avg_entity_count": 38.2,
                "avg_relationship_count": 112.5,
                "processing_history": [
                    {
                        "date": "2025-03-01",
                        "processed": 12
                    },
                    {
                        "date": "2025-03-02",
                        "processed": 18
                    },
                    {
                        "date": "2025-03-03",
                        "processed": 15
                    }
                ],
                "queue_length": 10,
                "active_workers": 5
            }
        }