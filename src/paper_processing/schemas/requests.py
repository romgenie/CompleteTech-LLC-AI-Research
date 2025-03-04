"""
Request schemas for the Paper Processing Pipeline API.

This module defines the Pydantic models for API requests in the Paper Processing
Pipeline. These models are used to validate incoming requests and generate
API documentation.

Current Implementation Status:
- Core request schemas defined ✓
- Validation rules established ✓
- Documentation examples created ✓

Upcoming Development:
- Additional request parameters
- Advanced filtering options
- Batch processing options
- WebSocket subscription requests
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from datetime import datetime
import uuid

from ..models.paper import PaperStatus


class ProcessPaperRequest(BaseModel):
    """Request model for processing a paper."""
    
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Processing options"
    )
    priority: Optional[int] = Field(
        None,
        description="Processing priority (1-10, higher is more important)",
        ge=1,
        le=10
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "options": {
                    "extract_citations": True,
                    "build_knowledge_graph": True,
                    "check_implementation_readiness": True
                },
                "priority": 5
            }
        }


class BatchProcessRequest(BaseModel):
    """Request model for batch processing multiple papers."""
    
    paper_ids: List[str] = Field(
        ...,
        description="List of paper IDs to process"
    )
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Processing options"
    )
    priority: Optional[int] = Field(
        None,
        description="Processing priority (1-10, higher is more important)",
        ge=1,
        le=10
    )
    
    @validator('paper_ids')
    def validate_paper_ids(cls, paper_ids):
        """Validate that paper_ids is not empty."""
        if not paper_ids:
            raise ValueError("paper_ids cannot be empty")
        return paper_ids
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "paper_ids": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ],
                "options": {
                    "extract_citations": True,
                    "build_knowledge_graph": True
                },
                "priority": 3
            }
        }


class PaperSearchRequest(BaseModel):
    """Request model for searching papers."""
    
    query: Optional[str] = Field(
        None,
        description="Search query string"
    )
    status: Optional[PaperStatus] = Field(
        None,
        description="Filter by paper status"
    )
    from_date: Optional[datetime] = Field(
        None,
        description="Filter by upload date (from)"
    )
    to_date: Optional[datetime] = Field(
        None,
        description="Filter by upload date (to)"
    )
    limit: int = Field(
        10,
        description="Maximum number of results",
        ge=1,
        le=100
    )
    offset: int = Field(
        0,
        description="Number of results to skip",
        ge=0
    )
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort by"
    )
    sort_order: Optional[str] = Field(
        None,
        description="Sort order (asc or desc)"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "query": "transformer",
                "status": "analyzed",
                "from_date": "2025-01-01T00:00:00Z",
                "to_date": "2025-03-01T00:00:00Z",
                "limit": 20,
                "offset": 0,
                "sort_by": "uploaded_at",
                "sort_order": "desc"
            }
        }


class PaperUploadRequest(BaseModel):
    """Request model for uploading a paper."""
    
    # Note: This model would be used with Form data and File uploads
    # The actual implementation would use FastAPI's File and Form classes
    
    title: str = Field(
        ...,
        description="Paper title"
    )
    authors: Optional[str] = Field(
        None,
        description="Comma-separated list of authors"
    )
    abstract: Optional[str] = Field(
        None,
        description="Paper abstract"
    )
    year: Optional[int] = Field(
        None,
        description="Publication year",
        ge=1900
    )
    doi: Optional[str] = Field(
        None,
        description="Digital Object Identifier"
    )
    url: Optional[HttpUrl] = Field(
        None,
        description="URL to the paper"
    )
    auto_process: bool = Field(
        False,
        description="Automatically start processing after upload"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "title": "Attention Is All You Need",
                "authors": "Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin",
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                "year": 2017,
                "doi": "10.48550/arXiv.1706.03762",
                "url": "https://arxiv.org/abs/1706.03762",
                "auto_process": True
            }
        }