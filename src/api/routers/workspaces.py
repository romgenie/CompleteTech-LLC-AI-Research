"""
Workspaces API router for team collaboration.

This module provides endpoints for creating and managing workspaces,
teams, and workspace memberships.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.api.dependencies.auth import get_current_user
from src.api.models.user import User
from src.api.models.workspace import (
    Workspace, WorkspaceCreate, WorkspaceUpdate, 
    WorkspaceMember, WorkspaceInvitation, Team
)
from src.api.services.workspace_service import WorkspaceService


logger = logging.getLogger(__name__)
router = APIRouter()
workspace_service = WorkspaceService()


@router.post("/workspaces", response_model=Workspace, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user)
) -> Workspace:
    """
    Create a new workspace for team collaboration.
    
    Args:
        workspace_data: Workspace creation data
        current_user: Authenticated user
        
    Returns:
        Workspace: Created workspace
    """
    return workspace_service.create_workspace(
        workspace_data=workspace_data, 
        created_by=current_user.id
    )


@router.get("/workspaces", response_model=List[Workspace])
async def list_workspaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    team_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[Workspace]:
    """
    List workspaces the user has access to.
    
    Args:
        skip: Number of items to skip for pagination
        limit: Maximum number of items to return
        search: Optional search term to filter by name
        team_id: Optional team ID to filter by
        current_user: Authenticated user
        
    Returns:
        List[Workspace]: Available workspaces
    """
    return workspace_service.list_workspaces(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        team_id=team_id
    )


@router.get("/workspaces/{workspace_id}", response_model=Workspace)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
) -> Workspace:
    """
    Get a specific workspace by ID.
    
    Args:
        workspace_id: Workspace ID
        current_user: Authenticated user
        
    Returns:
        Workspace: Requested workspace
    """
    workspace = workspace_service.get_workspace(workspace_id)
    
    # Check if user has access to the workspace
    if not workspace_service.check_workspace_access(workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this workspace"
        )
        
    return workspace


@router.put("/workspaces/{workspace_id}", response_model=Workspace)
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    current_user: User = Depends(get_current_user)
) -> Workspace:
    """
    Update a workspace.
    
    Args:
        workspace_id: Workspace ID
        workspace_data: Updated workspace data
        current_user: Authenticated user
        
    Returns:
        Workspace: Updated workspace
    """
    # Check if user has admin permissions for the workspace
    if not workspace_service.check_workspace_permission(workspace_id, current_user.id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this workspace"
        )
        
    return workspace_service.update_workspace(workspace_id, workspace_data)


@router.delete("/workspaces/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a workspace.
    
    Args:
        workspace_id: Workspace ID
        current_user: Authenticated user
    """
    # Check if user is the workspace owner
    workspace = workspace_service.get_workspace(workspace_id)
    if workspace.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the workspace owner can delete it"
        )
        
    workspace_service.delete_workspace(workspace_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


# Workspace members endpoints
@router.get("/workspaces/{workspace_id}/members", response_model=List[WorkspaceMember])
async def list_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user)
) -> List[WorkspaceMember]:
    """
    List members of a workspace.
    
    Args:
        workspace_id: Workspace ID
        current_user: Authenticated user
        
    Returns:
        List[WorkspaceMember]: Workspace members
    """
    # Check if user has access to the workspace
    if not workspace_service.check_workspace_access(workspace_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this workspace"
        )
        
    return workspace_service.list_workspace_members(workspace_id)


@router.post("/workspaces/{workspace_id}/members", response_model=WorkspaceMember)
async def add_workspace_member(
    workspace_id: str,
    user_id: str,
    role: str = "member",
    current_user: User = Depends(get_current_user)
) -> WorkspaceMember:
    """
    Add a member to a workspace.
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID to add
        role: Role for the new member
        current_user: Authenticated user
        
    Returns:
        WorkspaceMember: New workspace member
    """
    # Check if user has admin permissions for the workspace
    if not workspace_service.check_workspace_permission(workspace_id, current_user.id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add members to this workspace"
        )
        
    return workspace_service.add_workspace_member(
        workspace_id=workspace_id,
        user_id=user_id,
        role=role,
        invited_by=current_user.id
    )


@router.post("/workspaces/{workspace_id}/invitations", response_model=WorkspaceInvitation)
async def invite_to_workspace(
    workspace_id: str,
    email: str,
    role: str = "member",
    current_user: User = Depends(get_current_user)
) -> WorkspaceInvitation:
    """
    Invite a user to a workspace by email.
    
    Args:
        workspace_id: Workspace ID
        email: Email to invite
        role: Role for the invited user
        current_user: Authenticated user
        
    Returns:
        WorkspaceInvitation: Created invitation
    """
    # Check if user has admin permissions for the workspace
    if not workspace_service.check_workspace_permission(workspace_id, current_user.id, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite members to this workspace"
        )
        
    return workspace_service.create_workspace_invitation(
        workspace_id=workspace_id,
        email=email,
        role=role,
        invited_by=current_user.id
    )


# Team endpoints
@router.post("/teams", response_model=Team)
async def create_team(
    name: str,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Team:
    """
    Create a new team.
    
    Args:
        name: Team name
        description: Team description
        current_user: Authenticated user
        
    Returns:
        Team: Created team
    """
    return workspace_service.create_team(
        name=name,
        description=description,
        created_by=current_user.id
    )


@router.get("/teams", response_model=List[Team])
async def list_teams(
    current_user: User = Depends(get_current_user)
) -> List[Team]:
    """
    List teams the user is a member of.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List[Team]: User's teams
    """
    return workspace_service.list_user_teams(current_user.id)