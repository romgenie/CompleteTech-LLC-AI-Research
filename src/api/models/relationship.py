"""
Relationship models for the knowledge graph API.

This module defines Pydantic models for knowledge graph relationships.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class RelationshipBase(BaseModel):
    """Base model for knowledge graph relationships."""
    type: str = Field(..., description="The type or label of the relationship")
    source_id: str = Field(..., description="The ID of the source entity")
    target_id: str = Field(..., description="The ID of the target entity")
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional properties of the relationship"
    )
    confidence: Optional[float] = Field(
        1.0, 
        description="Confidence score for the relationship (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    source: Optional[str] = Field(
        None, 
        description="The source of the relationship information"
    )
    bidirectional: Optional[bool] = Field(
        False, 
        description="Whether the relationship is bidirectional"
    )


class RelationshipCreate(RelationshipBase):
    """Model for creating a new relationship."""
    pass


class Relationship(RelationshipBase):
    """Model for a relationship with ID and timestamps."""
    id: str = Field(..., description="The unique identifier for the relationship")
    created_at: Optional[datetime] = Field(
        None, 
        description="When the relationship was created"
    )
    updated_at: Optional[datetime] = Field(
        None, 
        description="When the relationship was last updated"
    )
    
    class Config:
        orm_mode = True


class RelationshipUpdate(BaseModel):
    """Model for updating an existing relationship."""
    type: Optional[str] = Field(None, description="The type or label of the relationship")
    properties: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional properties of the relationship"
    )
    confidence: Optional[float] = Field(
        None, 
        description="Confidence score for the relationship (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    source: Optional[str] = Field(
        None, 
        description="The source of the relationship information"
    )
    bidirectional: Optional[bool] = Field(
        None, 
        description="Whether the relationship is bidirectional"
    )


class RelationshipSearch(BaseModel):
    """Model for relationship search parameters."""
    types: Optional[List[str]] = Field(
        None, 
        description="Filter by relationship types"
    )
    entity_id: Optional[str] = Field(
        None, 
        description="Filter relationships involving this entity"
    )
    direction: Optional[str] = Field(
        "both", 
        description="Direction of relationships: 'outgoing', 'incoming', or 'both'"
    )
    min_confidence: Optional[float] = Field(
        0.0, 
        description="Minimum confidence score",
        ge=0.0,
        le=1.0
    )
    limit: Optional[int] = Field(
        10, 
        description="Maximum number of results",
        gt=0,
        le=100
    )


class RelationshipWithEntities(Relationship):
    """Relationship with details of the connected entities."""
    source_entity: Dict[str, Any] = Field(
        ..., 
        description="Details of the source entity"
    )
    target_entity: Dict[str, Any] = Field(
        ..., 
        description="Details of the target entity"
    )


class RelationshipList(BaseModel):
    """Model for a list of relationships with metadata."""
    items: List[RelationshipWithEntities] = Field(..., description="List of relationships")
    total: int = Field(..., description="Total number of matching relationships")
    page: Optional[int] = Field(1, description="Current page number")
    pages: Optional[int] = Field(1, description="Total number of pages")
    limit: Optional[int] = Field(10, description="Items per page")