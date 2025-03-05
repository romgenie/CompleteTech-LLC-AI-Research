"""
User models for authentication, authorization, and collaboration.

This module defines user-related models including enhanced role-based permissions,
team memberships, and workspace access control.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field, EmailStr


class UserRole(BaseModel):
    """Role definition with associated permissions."""
    name: str
    description: str
    permissions: List[str]


class TeamMembership(BaseModel):
    """User's membership in a team."""
    team_id: str
    role: str  # 'owner', 'admin', 'member', 'guest'
    joined_at: datetime


class UserPreferences(BaseModel):
    """User preferences for UI and system behavior."""
    theme: str = "light"  # 'light', 'dark', 'system'
    notification_settings: Dict[str, bool] = Field(default_factory=lambda: {
        "email_notifications": True,
        "project_updates": True,
        "comment_replies": True,
        "research_updates": True
    })
    visualization_settings: Dict[str, Any] = Field(default_factory=lambda: {
        "nodeSize": 5,
        "forceStrength": 1,
        "showLabels": True,
        "darkMode": False,
        "highlightNeighbors": True,
        "showRelationshipLabels": False
    })


class User(BaseModel):
    """Enhanced user model with collaboration features."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "researcher"  # 'admin', 'researcher', 'implementer', 'reviewer', 'viewer'
    permissions: List[str] = []
    teams: List[TeamMembership] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    disabled: bool = False


class UserCreate(BaseModel):
    """Schema for user creation."""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "researcher"


class UserUpdate(BaseModel):
    """Schema for user updates."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserInDB(User):
    """User as stored in database with hashed password."""
    hashed_password: str


# Define standard roles with their permissions
STANDARD_ROLES = {
    "admin": UserRole(
        name="admin",
        description="Administrator with full system access",
        permissions=["read", "write", "delete", "admin", "user_management", "system_config"]
    ),
    "researcher": UserRole(
        name="researcher",
        description="Creates and manages research projects",
        permissions=["read", "write", "research_management"]
    ),
    "implementer": UserRole(
        name="implementer",
        description="Implements code from research papers",
        permissions=["read", "write", "code_generation"]
    ),
    "reviewer": UserRole(
        name="reviewer",
        description="Reviews and comments on research projects",
        permissions=["read", "comment", "approve"]
    ),
    "viewer": UserRole(
        name="viewer",
        description="Read-only access to projects they are invited to",
        permissions=["read"]
    )
}