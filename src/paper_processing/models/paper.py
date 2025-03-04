"""
Paper model for the Paper Processing Pipeline.

This module defines the Paper model and related classes for representing
research papers and their processing state in the system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class PaperStatus(str, Enum):
    """
    Status of a paper in the processing pipeline.
    
    Represents the various states a paper can be in during processing.
    """
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    EXTRACTING_ENTITIES = "extracting_entities"
    EXTRACTING_RELATIONSHIPS = "extracting_relationships"
    BUILDING_KNOWLEDGE_GRAPH = "building_knowledge_graph"
    ANALYZED = "analyzed"
    IMPLEMENTATION_READY = "implementation_ready"
    FAILED = "failed"


class ProcessingEvent(BaseModel):
    """
    Represents a processing event in the paper's history.
    
    Records state transitions and processing milestones.
    """
    timestamp: datetime = Field(..., description="When the event occurred")
    status: PaperStatus = Field(..., description="The status at this event")
    message: str = Field(..., description="Description of the event")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class Author(BaseModel):
    """
    Represents an author of a paper.
    """
    name: str = Field(..., description="Author's name")
    email: Optional[str] = Field(None, description="Author's email")
    affiliation: Optional[str] = Field(None, description="Author's affiliation")
    orcid: Optional[str] = Field(None, description="Author's ORCID identifier")


class Entity(BaseModel):
    """
    Represents an entity extracted from a paper.
    """
    id: str = Field(..., description="Entity identifier")
    type: str = Field(..., description="Entity type")
    name: str = Field(..., description="Entity name")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    context: Optional[str] = Field(None, description="Surrounding context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class Relationship(BaseModel):
    """
    Represents a relationship between entities extracted from a paper.
    """
    id: str = Field(..., description="Relationship identifier")
    type: str = Field(..., description="Relationship type")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    context: Optional[str] = Field(None, description="Surrounding context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProcessingStatistics(BaseModel):
    """
    Statistics about the paper processing.
    """
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    entity_count: int = Field(0, description="Number of entities extracted")
    relationship_count: int = Field(0, description="Number of relationships extracted")
    page_count: Optional[int] = Field(None, description="Number of pages in the document")
    word_count: Optional[int] = Field(None, description="Number of words in the document")


class Paper(BaseModel):
    """
    Represents a research paper in the system.
    """
    id: str = Field(..., description="Unique identifier for the paper")
    title: str = Field(..., description="Paper title")
    authors: List[Author] = Field(default_factory=list, description="Paper authors")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    year: Optional[int] = Field(None, description="Publication year")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    url: Optional[str] = Field(None, description="URL to the paper")
    filename: str = Field(..., description="Filename in the system")
    file_path: str = Field(..., description="Path to the file in the system")
    content_type: str = Field(..., description="Content MIME type")
    original_filename: str = Field(..., description="Original filename from upload")
    uploaded_by: str = Field(..., description="Username who uploaded the paper")
    uploaded_at: datetime = Field(..., description="When the paper was uploaded")
    status: PaperStatus = Field(
        PaperStatus.UPLOADED, 
        description="Current processing status"
    )
    processing_history: List[ProcessingEvent] = Field(
        default_factory=list, 
        description="History of processing events"
    )
    entities: List[Entity] = Field(
        default_factory=list, 
        description="Entities extracted from paper"
    )
    relationships: List[Relationship] = Field(
        default_factory=list, 
        description="Relationships extracted from paper"
    )
    statistics: Optional[ProcessingStatistics] = Field(
        None, 
        description="Processing statistics"
    )
    knowledge_graph_id: Optional[str] = Field(
        None, 
        description="ID in the knowledge graph"
    )
    implementation_ready: bool = Field(
        False, 
        description="Whether the paper is ready for implementation"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata"
    )

    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Attention Is All You Need",
                "authors": [
                    {
                        "name": "Ashish Vaswani",
                        "affiliation": "Google Brain",
                        "email": None,
                        "orcid": None
                    }
                ],
                "abstract": "The dominant sequence transduction models...",
                "year": 2017,
                "doi": "10.48550/arXiv.1706.03762",
                "url": "https://arxiv.org/abs/1706.03762",
                "filename": "123e4567-e89b-12d3-a456-426614174000.pdf",
                "file_path": "/app/uploads/123e4567-e89b-12d3-a456-426614174000.pdf",
                "content_type": "application/pdf",
                "original_filename": "attention_is_all_you_need.pdf",
                "uploaded_by": "researcher",
                "uploaded_at": "2025-01-01T00:00:00",
                "status": "uploaded",
                "processing_history": [],
                "entities": [],
                "relationships": [],
                "statistics": None,
                "knowledge_graph_id": None,
                "implementation_ready": False,
                "metadata": {
                    "keywords": ["transformer", "attention", "neural machine translation"]
                }
            }
        }


def add_processing_event(
    paper: Paper,
    status: PaperStatus,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Paper:
    """
    Add a processing event to a paper's history.
    
    Args:
        paper: The paper to update
        status: The new status
        message: Description of the event
        details: Optional additional details
        
    Returns:
        The updated paper
    """
    event = ProcessingEvent(
        timestamp=datetime.utcnow(),
        status=status,
        message=message,
        details=details
    )
    
    # Update the paper
    paper.status = status
    paper.processing_history.append(event)
    
    return paper