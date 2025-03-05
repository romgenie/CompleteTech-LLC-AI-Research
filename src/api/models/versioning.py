"""
Version control models for research projects.

This module defines models for tracking versions of research projects,
reports, and implementations, supporting collaborative editing.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Set
from uuid import uuid4

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Types of changes in a version."""
    ADDITION = "addition"
    MODIFICATION = "modification"
    DELETION = "deletion"
    REORDER = "reorder"
    MERGE = "merge"


class ContentChange(BaseModel):
    """Record of a specific content change."""
    path: str  # Path to the changed element (e.g., "sections.introduction.content")
    type: ChangeType
    before: Optional[Any] = None
    after: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VersionStatus(str, Enum):
    """Status of a version."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Version(BaseModel):
    """Version of a research project, report, or implementation."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    version_number: str  # Semantic versioning (e.g., "1.0.0")
    name: Optional[str] = None  # Optional name for this version
    description: Optional[str] = None
    status: VersionStatus = VersionStatus.DRAFT
    
    # User and timestamps
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Version relationships
    parent_version_id: Optional[str] = None
    branch_name: str = "main"  # Name of the branch this version belongs to
    
    # Content changes
    changes: List[ContentChange] = Field(default_factory=list)
    
    # Review and approval
    reviewed_by: Optional[List[str]] = None  # User IDs of reviewers
    approved_by: Optional[str] = None  # User ID who approved this version
    approved_at: Optional[datetime] = None
    
    # Additional data
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Branch(BaseModel):
    """Branch in version control for parallel development."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    name: str
    description: Optional[str] = None
    created_from_version_id: str  # Version ID this branch was created from
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # 'active', 'merged', 'abandoned'
    merged_into: Optional[str] = None  # Branch name this was merged into
    merged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MergeRequest(BaseModel):
    """Request to merge changes from one branch to another."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    title: str
    description: Optional[str] = None
    source_branch: str
    target_branch: str
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "open"  # 'open', 'merged', 'closed', 'rejected'
    reviewers: List[str] = Field(default_factory=list)  # User IDs of requested reviewers
    approved_by: Set[str] = Field(default_factory=set)  # User IDs who approved
    merged_by: Optional[str] = None  # User ID who merged
    merged_at: Optional[datetime] = None
    closed_by: Optional[str] = None
    closed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VersionCreate(BaseModel):
    """Schema for version creation."""
    project_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    parent_version_id: Optional[str] = None
    branch_name: str = "main"
    changes: List[ContentChange] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BranchCreate(BaseModel):
    """Schema for branch creation."""
    project_id: str
    name: str
    description: Optional[str] = None
    created_from_version_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MergeRequestCreate(BaseModel):
    """Schema for merge request creation."""
    project_id: str
    title: str
    description: Optional[str] = None
    source_branch: str
    target_branch: str
    reviewers: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)