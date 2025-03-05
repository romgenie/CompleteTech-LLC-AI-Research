"""
Workspace models for team collaboration.

This module defines workspace-related models including teams, shared projects,
and access control settings.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class WorkspaceVisibility(str, Enum):
    """Visibility levels for workspaces."""
    PRIVATE = "private"  # Only visible to members
    INTERNAL = "internal"  # Visible to all authenticated users
    PUBLIC = "public"  # Visible to everyone, including anonymous users


class Team(BaseModel):
    """Team model for grouping users."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    avatar_url: Optional[str] = None


class Workspace(BaseModel):
    """Workspace model for collaborative research."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    team_id: str
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # IDs of projects contained in this workspace
    project_ids: List[str] = Field(default_factory=list)


class WorkspaceMember(BaseModel):
    """Workspace member with role-based permissions."""
    workspace_id: str
    user_id: str
    role: str = "member"  # 'owner', 'admin', 'member', 'guest'
    permissions: List[str] = ["read"]  # Specific permissions for this user in this workspace
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = None  # User ID of the inviter


class WorkspaceInvitation(BaseModel):
    """Invitation to join a workspace."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    email: str
    role: str = "member"
    invited_by: str  # User ID
    invited_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    accepted: bool = False
    accepted_at: Optional[datetime] = None


class WorkspaceCreate(BaseModel):
    """Schema for workspace creation."""
    name: str
    description: Optional[str] = None
    team_id: Optional[str] = None
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceUpdate(BaseModel):
    """Schema for workspace updates."""
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[WorkspaceVisibility] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None