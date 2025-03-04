"""
Entity models for the knowledge graph API.

This module defines Pydantic models for knowledge graph entities.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class EntityBase(BaseModel):
    """Base model for knowledge graph entities."""
    name: str = Field(..., description="The name of the entity")
    label: str = Field(..., description="The entity label or type")
    aliases: Optional[List[str]] = Field(
        default_factory=list, 
        description="Alternative names for the entity"
    )
    properties: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional properties of the entity"
    )
    source: Optional[str] = Field(
        None, 
        description="The source of the entity information"
    )
    confidence: Optional[float] = Field(
        1.0, 
        description="Confidence score for the entity (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )


class EntityCreate(EntityBase):
    """Model for creating a new entity."""
    pass


class Entity(EntityBase):
    """Model for an entity with ID and timestamps."""
    id: str = Field(..., description="The unique identifier for the entity")
    created_at: Optional[datetime] = Field(
        None, 
        description="When the entity was created"
    )
    updated_at: Optional[datetime] = Field(
        None, 
        description="When the entity was last updated"
    )
    
    class Config:
        orm_mode = True


class EntityUpdate(BaseModel):
    """Model for updating an existing entity."""
    name: Optional[str] = Field(None, description="The name of the entity")
    label: Optional[str] = Field(None, description="The entity label or type")
    aliases: Optional[List[str]] = Field(
        None, 
        description="Alternative names for the entity"
    )
    properties: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional properties of the entity"
    )
    source: Optional[str] = Field(
        None, 
        description="The source of the entity information"
    )
    confidence: Optional[float] = Field(
        None, 
        description="Confidence score for the entity (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )


class EntitySearch(BaseModel):
    """Model for entity search parameters."""
    query: str = Field(..., description="Search query string")
    labels: Optional[List[str]] = Field(
        None, 
        description="Filter by entity labels"
    )
    sources: Optional[List[str]] = Field(
        None, 
        description="Filter by sources"
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


class EntityList(BaseModel):
    """Model for a list of entities with metadata."""
    items: List[Entity] = Field(..., description="List of entities")
    total: int = Field(..., description="Total number of matching entities")
    page: Optional[int] = Field(1, description="Current page number")
    pages: Optional[int] = Field(1, description="Total number of pages")
    limit: Optional[int] = Field(10, description="Items per page")