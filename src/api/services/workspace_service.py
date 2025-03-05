"""
Workspace service for team collaboration features.

This module implements the business logic for workspaces, teams,
and workspace membership management.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from src.api.models.workspace import (
    Workspace, WorkspaceCreate, WorkspaceUpdate,
    WorkspaceMember, WorkspaceInvitation, Team,
    WorkspaceVisibility
)


logger = logging.getLogger(__name__)


class WorkspaceService:
    """Service for workspace operations."""
    
    def __init__(self):
        """Initialize workspace service."""
        # In a real implementation, this would connect to a database
        # For now, we'll use in-memory storage for demonstration
        self.workspaces = {}
        self.workspace_members = {}
        self.workspace_invitations = {}
        self.teams = {}
        self.team_members = {}
    
    def create_workspace(self, workspace_data: WorkspaceCreate, created_by: str) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            workspace_data: Workspace creation data
            created_by: ID of the creating user
            
        Returns:
            Workspace: Created workspace
        """
        # Create workspace
        workspace = Workspace(
            name=workspace_data.name,
            description=workspace_data.description,
            team_id=workspace_data.team_id or "",
            visibility=workspace_data.visibility,
            created_by=created_by,
            tags=workspace_data.tags,
            metadata=workspace_data.metadata
        )
        
        # Store workspace
        self.workspaces[workspace.id] = workspace
        
        # Add creator as workspace owner
        owner_member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=created_by,
            role="owner",
            permissions=["read", "write", "admin"],
            invited_by=None
        )
        
        if workspace.id not in self.workspace_members:
            self.workspace_members[workspace.id] = []
            
        self.workspace_members[workspace.id].append(owner_member)
        
        logger.info(f"Created workspace {workspace.id} by user {created_by}")
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Workspace:
        """
        Get a workspace by ID.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Workspace: Retrieved workspace
        
        Raises:
            KeyError: If workspace not found
        """
        if workspace_id not in self.workspaces:
            raise KeyError(f"Workspace {workspace_id} not found")
            
        return self.workspaces[workspace_id]
    
    def update_workspace(self, workspace_id: str, workspace_data: WorkspaceUpdate) -> Workspace:
        """
        Update a workspace.
        
        Args:
            workspace_id: Workspace ID
            workspace_data: Updated workspace data
            
        Returns:
            Workspace: Updated workspace
            
        Raises:
            KeyError: If workspace not found
        """
        if workspace_id not in self.workspaces:
            raise KeyError(f"Workspace {workspace_id} not found")
        
        workspace = self.workspaces[workspace_id]
        
        # Update fields if provided
        if workspace_data.name is not None:
            workspace.name = workspace_data.name
            
        if workspace_data.description is not None:
            workspace.description = workspace_data.description
            
        if workspace_data.visibility is not None:
            workspace.visibility = workspace_data.visibility
            
        if workspace_data.tags is not None:
            workspace.tags = workspace_data.tags
            
        if workspace_data.metadata is not None:
            workspace.metadata = workspace_data.metadata
        
        workspace.updated_at = datetime.utcnow()
        return workspace
    
    def delete_workspace(self, workspace_id: str) -> None:
        """
        Delete a workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Raises:
            KeyError: If workspace not found
        """
        if workspace_id not in self.workspaces:
            raise KeyError(f"Workspace {workspace_id} not found")
        
        # Delete workspace members
        if workspace_id in self.workspace_members:
            del self.workspace_members[workspace_id]
        
        # Delete workspace invitations
        if workspace_id in self.workspace_invitations:
            del self.workspace_invitations[workspace_id]
        
        # Delete workspace
        del self.workspaces[workspace_id]
        
        logger.info(f"Deleted workspace {workspace_id}")
    
    def list_workspaces(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> List[Workspace]:
        """
        List workspaces the user has access to.
        
        Args:
            user_id: User ID
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            search: Optional search term for workspace name
            team_id: Optional team ID to filter by
            
        Returns:
            List[Workspace]: Accessible workspaces
        """
        # Find workspaces the user is a member of
        user_workspace_ids = set()
        for workspace_id, members in self.workspace_members.items():
            for member in members:
                if member.user_id == user_id:
                    user_workspace_ids.add(workspace_id)
                    break
        
        # Find internal and public workspaces
        for workspace_id, workspace in self.workspaces.items():
            if workspace.visibility == WorkspaceVisibility.INTERNAL or workspace.visibility == WorkspaceVisibility.PUBLIC:
                user_workspace_ids.add(workspace_id)
        
        # Apply filters
        results = []
        for workspace_id in user_workspace_ids:
            workspace = self.workspaces[workspace_id]
            
            # Apply team filter
            if team_id and workspace.team_id != team_id:
                continue
            
            # Apply search filter
            if search and search.lower() not in workspace.name.lower():
                continue
            
            results.append(workspace)
        
        # Apply pagination
        return sorted(results, key=lambda w: w.created_at, reverse=True)[skip:skip+limit]
    
    def check_workspace_access(self, workspace_id: str, user_id: str) -> bool:
        """
        Check if user has access to a workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            
        Returns:
            bool: True if user has access, False otherwise
        """
        try:
            workspace = self.get_workspace(workspace_id)
        except KeyError:
            return False
        
        # Public workspaces are accessible to everyone
        if workspace.visibility == WorkspaceVisibility.PUBLIC:
            return True
        
        # Internal workspaces are accessible to all authenticated users
        if workspace.visibility == WorkspaceVisibility.INTERNAL:
            return True
        
        # Check if user is a member of the workspace
        if workspace_id in self.workspace_members:
            for member in self.workspace_members[workspace_id]:
                if member.user_id == user_id:
                    return True
        
        return False
    
    def check_workspace_permission(self, workspace_id: str, user_id: str, permission: str) -> bool:
        """
        Check if user has a specific permission in a workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            permission: Permission to check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        if workspace_id not in self.workspace_members:
            return False
        
        for member in self.workspace_members[workspace_id]:
            if member.user_id == user_id and permission in member.permissions:
                return True
        
        return False
    
    def list_workspace_members(self, workspace_id: str) -> List[WorkspaceMember]:
        """
        List members of a workspace.
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List[WorkspaceMember]: Workspace members
        """
        if workspace_id not in self.workspace_members:
            return []
        
        return self.workspace_members[workspace_id]
    
    def add_workspace_member(
        self, 
        workspace_id: str, 
        user_id: str, 
        role: str = "member",
        invited_by: Optional[str] = None
    ) -> WorkspaceMember:
        """
        Add a member to a workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID to add
            role: Role for the new member
            invited_by: User ID who invited the new member
            
        Returns:
            WorkspaceMember: New workspace member
            
        Raises:
            KeyError: If workspace not found
            ValueError: If user is already a member
        """
        if workspace_id not in self.workspaces:
            raise KeyError(f"Workspace {workspace_id} not found")
        
        # Check if user is already a member
        if workspace_id in self.workspace_members:
            for member in self.workspace_members[workspace_id]:
                if member.user_id == user_id:
                    raise ValueError(f"User {user_id} is already a member of workspace {workspace_id}")
        
        # Determine permissions based on role
        permissions = ["read"]
        if role in ["owner", "admin"]:
            permissions.extend(["write", "admin"])
        elif role == "member":
            permissions.append("write")
        
        # Create member
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            permissions=permissions,
            invited_by=invited_by
        )
        
        # Add to members
        if workspace_id not in self.workspace_members:
            self.workspace_members[workspace_id] = []
            
        self.workspace_members[workspace_id].append(member)
        
        logger.info(f"Added user {user_id} to workspace {workspace_id} with role {role}")
        return member
    
    def create_workspace_invitation(
        self, 
        workspace_id: str, 
        email: str, 
        role: str = "member",
        invited_by: str = None
    ) -> WorkspaceInvitation:
        """
        Create an invitation to a workspace.
        
        Args:
            workspace_id: Workspace ID
            email: Email to invite
            role: Role for the invited user
            invited_by: User ID who created the invitation
            
        Returns:
            WorkspaceInvitation: Created invitation
            
        Raises:
            KeyError: If workspace not found
        """
        if workspace_id not in self.workspaces:
            raise KeyError(f"Workspace {workspace_id} not found")
        
        # Create invitation
        invitation = WorkspaceInvitation(
            workspace_id=workspace_id,
            email=email,
            role=role,
            invited_by=invited_by,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        # Store invitation
        if workspace_id not in self.workspace_invitations:
            self.workspace_invitations[workspace_id] = []
            
        self.workspace_invitations[workspace_id].append(invitation)
        
        logger.info(f"Created invitation for {email} to workspace {workspace_id}")
        return invitation
    
    def create_team(self, name: str, description: Optional[str], created_by: str) -> Team:
        """
        Create a new team.
        
        Args:
            name: Team name
            description: Team description
            created_by: User ID who created the team
            
        Returns:
            Team: Created team
        """
        team = Team(
            name=name,
            description=description,
            created_by=created_by
        )
        
        # Store team
        self.teams[team.id] = team
        
        # Add creator to team
        if team.id not in self.team_members:
            self.team_members[team.id] = []
            
        self.team_members[team.id].append({
            "user_id": created_by,
            "role": "owner",
            "joined_at": datetime.utcnow()
        })
        
        logger.info(f"Created team {team.id} by user {created_by}")
        return team
    
    def list_user_teams(self, user_id: str) -> List[Team]:
        """
        List teams the user is a member of.
        
        Args:
            user_id: User ID
            
        Returns:
            List[Team]: User's teams
        """
        team_ids = []
        
        # Find teams user is a member of
        for team_id, members in self.team_members.items():
            for member in members:
                if member["user_id"] == user_id:
                    team_ids.append(team_id)
                    break
        
        # Get team details
        teams = []
        for team_id in team_ids:
            if team_id in self.teams:
                teams.append(self.teams[team_id])
                
        return teams