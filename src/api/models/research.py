"""
Research models for the API.

This module defines Pydantic models for research orchestration and implementation.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, HttpUrl


class ResearchStatus(str, Enum):
    """Status of a research task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ImplementationStatus(str, Enum):
    """Status of an implementation task."""
    REQUESTED = "requested"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaperStatus(str, Enum):
    """Status of an uploaded paper."""
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    EXTRACTING_ENTITIES = "extracting_entities"
    EXTRACTING_RELATIONSHIPS = "extracting_relationships"
    BUILDING_KNOWLEDGE_GRAPH = "building_knowledge_graph"
    ANALYZED = "analyzed"
    IMPLEMENTATION_READY = "implementation_ready"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Type of research document."""
    PAPER = "paper"
    ARTICLE = "article"
    REPORT = "report"
    PRESENTATION = "presentation"
    CODE = "code"
    NOTEBOOK = "notebook"
    OTHER = "other"


class InfoSourceType(str, Enum):
    """Type of information source."""
    ACADEMIC = "academic"
    WEB = "web"
    CODE = "code"
    AI = "ai"
    USER = "user"


class Author(BaseModel):
    """Model for an author of a research paper or article."""
    name: str = Field(..., description="The name of the author")
    affiliations: Optional[List[str]] = Field(
        default_factory=list, 
        description="The author's affiliations"
    )
    email: Optional[str] = Field(None, description="The author's email")
    orcid: Optional[str] = Field(None, description="The author's ORCID identifier")


class PaperInfo(BaseModel):
    """Model for information about a research paper."""
    title: str = Field(..., description="The title of the paper")
    authors: List[Author] = Field(..., description="The authors of the paper")
    abstract: Optional[str] = Field(None, description="The abstract of the paper")
    year: Optional[int] = Field(None, description="The year of publication")
    doi: Optional[str] = Field(None, description="The DOI of the paper")
    arxiv_id: Optional[str] = Field(None, description="The arXiv identifier")
    url: Optional[HttpUrl] = Field(None, description="URL to the paper")
    keywords: Optional[List[str]] = Field(
        default_factory=list, 
        description="Keywords associated with the paper"
    )
    venue: Optional[str] = Field(
        None, 
        description="Conference or journal where the paper was published"
    )


class ResearchQueryCreate(BaseModel):
    """Model for creating a new research query."""
    query: str = Field(..., description="The research query")
    sources: Optional[List[InfoSourceType]] = Field(
        default_factory=lambda: [t.value for t in InfoSourceType], 
        description="Sources to search for information"
    )
    max_results: Optional[int] = Field(
        10, 
        description="Maximum number of results per source",
        gt=0,
        le=100
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional filters for the search"
    )


class ResearchTask(BaseModel):
    """Model for a research task."""
    id: str = Field(..., description="The unique identifier for the task")
    query: str = Field(..., description="The research query")
    status: ResearchStatus = Field(..., description="The status of the task")
    sources: List[InfoSourceType] = Field(..., description="Sources to search")
    max_results: int = Field(..., description="Maximum results per source")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional filters for the search"
    )
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: Optional[datetime] = Field(
        None, 
        description="When the task was last updated"
    )
    completed_at: Optional[datetime] = Field(
        None, 
        description="When the task was completed"
    )
    user: str = Field(..., description="The user who created the task")
    results: Optional[Dict[str, Any]] = Field(
        None, 
        description="The results of the task"
    )
    
    class Config:
        orm_mode = True


class ImplementationRequestCreate(BaseModel):
    """Model for creating an implementation request."""
    paper_info: PaperInfo = Field(..., description="Information about the paper")
    implementation_language: Optional[str] = Field(
        "python", 
        description="The programming language for implementation"
    )
    focus_areas: Optional[List[str]] = Field(
        default_factory=list, 
        description="Specific areas to focus on"
    )
    additional_notes: Optional[str] = Field(
        None, 
        description="Additional notes for the implementation"
    )


class Implementation(BaseModel):
    """Model for a research implementation."""
    id: str = Field(..., description="The unique identifier for the implementation")
    paper_info: PaperInfo = Field(..., description="Information about the paper")
    implementation_language: str = Field(
        ..., 
        description="The programming language for implementation"
    )
    focus_areas: List[str] = Field(
        ..., 
        description="Specific areas to focus on"
    )
    additional_notes: Optional[str] = Field(
        None, 
        description="Additional notes for the implementation"
    )
    status: ImplementationStatus = Field(..., description="The status of the implementation")
    created_at: datetime = Field(..., description="When the implementation was requested")
    updated_at: Optional[datetime] = Field(
        None, 
        description="When the implementation was last updated"
    )
    completed_at: Optional[datetime] = Field(
        None, 
        description="When the implementation was completed"
    )
    requested_by: str = Field(..., description="The user who requested the implementation")
    files: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, 
        description="Files generated for the implementation"
    )
    repository_url: Optional[HttpUrl] = Field(
        None, 
        description="URL to the implementation repository"
    )
    
    class Config:
        orm_mode = True


class TaskFilter(BaseModel):
    """Model for filtering tasks."""
    status: Optional[Union[ResearchStatus, List[ResearchStatus]]] = Field(
        None, 
        description="Filter by status"
    )
    query: Optional[str] = Field(
        None, 
        description="Filter by query text (partial match)"
    )
    created_after: Optional[datetime] = Field(
        None, 
        description="Filter by creation date (after)"
    )
    created_before: Optional[datetime] = Field(
        None, 
        description="Filter by creation date (before)"
    )
    limit: Optional[int] = Field(
        10, 
        description="Maximum number of results",
        gt=0,
        le=100
    )
    offset: Optional[int] = Field(
        0, 
        description="Results offset for pagination",
        ge=0
    )