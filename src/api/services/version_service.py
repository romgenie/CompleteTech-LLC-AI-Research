"""
Version service for research project version control.

This module implements the business logic for tracking versions of research projects,
supporting branches, merge requests, and comparing versions.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Set

from src.api.models.versioning import (
    Version, VersionCreate, Branch, BranchCreate,
    MergeRequest, MergeRequestCreate, VersionStatus,
    ContentChange, ChangeType
)


logger = logging.getLogger(__name__)


class VersionService:
    """Service for version control operations."""
    
    def __init__(self):
        """Initialize version service."""
        # In a real implementation, this would connect to a database
        # For now, we'll use in-memory storage for demonstration
        self.versions = {}
        self.branches = {}
        self.merge_requests = {}
        
        # Mock project permissions for demonstration
        # In a real implementation, this would query permissions from other services
        self.permissions_cache = {}
    
    def create_version(self, version_data: VersionCreate, created_by: str) -> Version:
        """
        Create a new version of a project.
        
        Args:
            version_data: Version creation data
            created_by: ID of the creating user
            
        Returns:
            Version: Created version
        """
        # Get next version number - find the highest version for this project in this branch
        version_number = self._get_next_version_number(
            version_data.project_id,
            version_data.branch_name
        )
        
        # Create version
        version = Version(
            project_id=version_data.project_id,
            version_number=version_number,
            name=version_data.name,
            description=version_data.description,
            created_by=created_by,
            parent_version_id=version_data.parent_version_id,
            branch_name=version_data.branch_name,
            changes=version_data.changes,
            tags=version_data.tags,
            metadata=version_data.metadata
        )
        
        # Store version
        self.versions[version.id] = version
        
        logger.info(f"Created version {version.id} for project {version.project_id}")
        return version
    
    def _get_next_version_number(self, project_id: str, branch_name: str) -> str:
        """
        Get the next version number for a project branch.
        
        Args:
            project_id: Project ID
            branch_name: Branch name
            
        Returns:
            str: Next version number
        """
        # Find the latest version for this project and branch
        latest_version = None
        latest_version_number = "0.0.0"
        
        for version_id, version in self.versions.items():
            if version.project_id == project_id and version.branch_name == branch_name:
                if self._compare_versions(version.version_number, latest_version_number) > 0:
                    latest_version = version
                    latest_version_number = version.version_number
        
        # If no versions exist, start with 0.1.0 for non-main branches, 1.0.0 for main
        if latest_version is None:
            if branch_name == "main":
                return "1.0.0"
            else:
                return "0.1.0"
        
        # Increment version number
        # For simplicity, just increment the last segment
        major, minor, patch = latest_version_number.split(".")
        
        # On main branch, increment minor for new features, patch otherwise
        if branch_name == "main":
            # For demonstration, always increment patch
            patch = str(int(patch) + 1)
        else:
            # For other branches, increment patch
            patch = str(int(patch) + 1)
            
        return f"{major}.{minor}.{patch}"
    
    def _compare_versions(self, version_a: str, version_b: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version_a: First version
            version_b: Second version
            
        Returns:
            int: 1 if a > b, -1 if a < b, 0 if a == b
        """
        def parse_version(version: str) -> List[int]:
            return [int(x) for x in version.split(".")]
            
        a_parts = parse_version(version_a)
        b_parts = parse_version(version_b)
        
        for i in range(max(len(a_parts), len(b_parts))):
            a_val = a_parts[i] if i < len(a_parts) else 0
            b_val = b_parts[i] if i < len(b_parts) else 0
            
            if a_val > b_val:
                return 1
            elif a_val < b_val:
                return -1
                
        return 0
    
    def get_version(self, version_id: str) -> Version:
        """
        Get a version by ID.
        
        Args:
            version_id: Version ID
            
        Returns:
            Version: Retrieved version
            
        Raises:
            KeyError: If version not found
        """
        if version_id not in self.versions:
            raise KeyError(f"Version {version_id} not found")
            
        return self.versions[version_id]
    
    def list_project_versions(
        self,
        project_id: str,
        branch_name: Optional[str] = None,
        status: Optional[VersionStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Version]:
        """
        List versions of a project with optional filtering.
        
        Args:
            project_id: Project ID
            branch_name: Optional branch name to filter by
            status: Optional version status to filter by
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[Version]: Project versions
        """
        results = []
        
        for version_id, version in self.versions.items():
            # Match project ID
            if version.project_id != project_id:
                continue
                
            # Apply branch filter
            if branch_name and version.branch_name != branch_name:
                continue
                
            # Apply status filter
            if status and version.status != status:
                continue
                
            results.append(version)
        
        # Sort by version number (descending) and apply pagination
        return sorted(
            results, 
            key=lambda v: v.version_number,
            reverse=True
        )[skip:skip+limit]
    
    def approve_version(self, version_id: str, approved_by: str) -> Version:
        """
        Approve a version.
        
        Args:
            version_id: Version ID
            approved_by: User ID who approved
            
        Returns:
            Version: Updated version
            
        Raises:
            KeyError: If version not found
            ValueError: If version is already approved
        """
        if version_id not in self.versions:
            raise KeyError(f"Version {version_id} not found")
            
        version = self.versions[version_id]
        
        # Check if version is already approved
        if version.status == VersionStatus.APPROVED:
            raise ValueError(f"Version {version_id} is already approved")
        
        # Approve version
        version.status = VersionStatus.APPROVED
        version.approved_by = approved_by
        version.approved_at = datetime.utcnow()
        version.updated_at = datetime.utcnow()
        
        logger.info(f"Version {version_id} approved by user {approved_by}")
        return version
    
    def create_branch(self, branch_data: BranchCreate, created_by: str) -> Branch:
        """
        Create a new branch for a project.
        
        Args:
            branch_data: Branch creation data
            created_by: ID of the creating user
            
        Returns:
            Branch: Created branch
            
        Raises:
            ValueError: If branch with same name already exists
        """
        # Check if branch already exists
        for branch_id, branch in self.branches.items():
            if branch.project_id == branch_data.project_id and branch.name == branch_data.name:
                raise ValueError(f"Branch '{branch_data.name}' already exists for project {branch_data.project_id}")
        
        # Create branch
        branch = Branch(
            project_id=branch_data.project_id,
            name=branch_data.name,
            description=branch_data.description,
            created_from_version_id=branch_data.created_from_version_id,
            created_by=created_by,
            metadata=branch_data.metadata
        )
        
        # Store branch
        self.branches[branch.id] = branch
        
        logger.info(f"Created branch {branch.id} for project {branch.project_id}")
        return branch
    
    def list_project_branches(self, project_id: str, status: Optional[str] = None) -> List[Branch]:
        """
        List branches of a project.
        
        Args:
            project_id: Project ID
            status: Optional branch status to filter by
            
        Returns:
            List[Branch]: Project branches
        """
        results = []
        
        for branch_id, branch in self.branches.items():
            # Match project ID
            if branch.project_id != project_id:
                continue
                
            # Apply status filter
            if status and branch.status != status:
                continue
                
            results.append(branch)
        
        # Sort by creation date (newest first)
        return sorted(results, key=lambda b: b.created_at, reverse=True)
    
    def create_merge_request(self, merge_request_data: MergeRequestCreate, created_by: str) -> MergeRequest:
        """
        Create a new merge request.
        
        Args:
            merge_request_data: Merge request creation data
            created_by: ID of the creating user
            
        Returns:
            MergeRequest: Created merge request
            
        Raises:
            ValueError: If source and target branches are the same
        """
        # Check if source and target branches are the same
        if merge_request_data.source_branch == merge_request_data.target_branch:
            raise ValueError(f"Source and target branches cannot be the same")
        
        # Create merge request
        merge_request = MergeRequest(
            project_id=merge_request_data.project_id,
            title=merge_request_data.title,
            description=merge_request_data.description,
            source_branch=merge_request_data.source_branch,
            target_branch=merge_request_data.target_branch,
            created_by=created_by,
            reviewers=merge_request_data.reviewers,
            metadata=merge_request_data.metadata
        )
        
        # Store merge request
        self.merge_requests[merge_request.id] = merge_request
        
        logger.info(f"Created merge request {merge_request.id} for project {merge_request.project_id}")
        return merge_request
    
    def get_merge_request(self, merge_request_id: str) -> MergeRequest:
        """
        Get a merge request by ID.
        
        Args:
            merge_request_id: Merge request ID
            
        Returns:
            MergeRequest: Retrieved merge request
            
        Raises:
            KeyError: If merge request not found
        """
        if merge_request_id not in self.merge_requests:
            raise KeyError(f"Merge request {merge_request_id} not found")
            
        return self.merge_requests[merge_request_id]
    
    def list_merge_requests(self, project_id: str, status: Optional[str] = None) -> List[MergeRequest]:
        """
        List merge requests for a project.
        
        Args:
            project_id: Project ID
            status: Optional merge request status to filter by
            
        Returns:
            List[MergeRequest]: Project merge requests
        """
        results = []
        
        for merge_request_id, merge_request in self.merge_requests.items():
            # Match project ID
            if merge_request.project_id != project_id:
                continue
                
            # Apply status filter
            if status and merge_request.status != status:
                continue
                
            results.append(merge_request)
        
        # Sort by creation date (newest first)
        return sorted(results, key=lambda mr: mr.created_at, reverse=True)
    
    def approve_merge_request(self, merge_request_id: str, user_id: str) -> MergeRequest:
        """
        Approve a merge request.
        
        Args:
            merge_request_id: Merge request ID
            user_id: User ID who approved
            
        Returns:
            MergeRequest: Updated merge request
            
        Raises:
            KeyError: If merge request not found
            ValueError: If merge request is not open
        """
        if merge_request_id not in self.merge_requests:
            raise KeyError(f"Merge request {merge_request_id} not found")
            
        merge_request = self.merge_requests[merge_request_id]
        
        # Check if merge request is open
        if merge_request.status != "open":
            raise ValueError(f"Merge request {merge_request_id} is not open")
        
        # Add approval
        merge_request.approved_by.add(user_id)
        merge_request.updated_at = datetime.utcnow()
        
        logger.info(f"Merge request {merge_request_id} approved by user {user_id}")
        return merge_request
    
    def has_required_approvals(self, merge_request: MergeRequest) -> bool:
        """
        Check if a merge request has the required number of approvals.
        
        Args:
            merge_request: Merge request to check
            
        Returns:
            bool: True if required approvals are met, False otherwise
        """
        # In a real implementation, this would check against project settings
        # For demonstration, require one approval if reviewers are assigned,
        # or any approval if no reviewers are assigned
        if len(merge_request.reviewers) > 0:
            # Check if at least one assigned reviewer has approved
            for reviewer in merge_request.reviewers:
                if reviewer in merge_request.approved_by:
                    return True
            return False
        else:
            # If no reviewers assigned, any approval is sufficient
            return len(merge_request.approved_by) > 0
    
    def merge_merge_request(self, merge_request_id: str, merged_by: str) -> MergeRequest:
        """
        Merge a merge request.
        
        Args:
            merge_request_id: Merge request ID
            merged_by: User ID who merged
            
        Returns:
            MergeRequest: Updated merge request
            
        Raises:
            KeyError: If merge request not found
            ValueError: If merge request is not open or has conflicts
        """
        if merge_request_id not in self.merge_requests:
            raise KeyError(f"Merge request {merge_request_id} not found")
            
        merge_request = self.merge_requests[merge_request_id]
        
        # Check if merge request is open
        if merge_request.status != "open":
            raise ValueError(f"Merge request {merge_request_id} is not open")
        
        # In a real implementation, check for conflicts and perform the merge
        # Here we just update the status
        
        merge_request.status = "merged"
        merge_request.merged_by = merged_by
        merge_request.merged_at = datetime.utcnow()
        merge_request.updated_at = datetime.utcnow()
        
        # Update branch status when merge request is completed
        source_branch_id = self._find_branch_id(merge_request.project_id, merge_request.source_branch)
        if source_branch_id:
            self.branches[source_branch_id].status = "merged"
            self.branches[source_branch_id].merged_into = merge_request.target_branch
            self.branches[source_branch_id].merged_at = datetime.utcnow()
        
        logger.info(f"Merge request {merge_request_id} merged by user {merged_by}")
        return merge_request
    
    def _find_branch_id(self, project_id: str, branch_name: str) -> Optional[str]:
        """
        Find branch ID by project ID and branch name.
        
        Args:
            project_id: Project ID
            branch_name: Branch name
            
        Returns:
            Optional[str]: Branch ID if found, None otherwise
        """
        for branch_id, branch in self.branches.items():
            if branch.project_id == project_id and branch.name == branch_name:
                return branch_id
        return None
    
    def get_version_diff(self, version_id: str, base_version_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get differences between versions.
        
        Args:
            version_id: Version ID
            base_version_id: Optional base version ID to compare against
            
        Returns:
            Dict[str, Any]: Version differences
            
        Raises:
            KeyError: If version not found
        """
        if version_id not in self.versions:
            raise KeyError(f"Version {version_id} not found")
            
        version = self.versions[version_id]
        
        # If no base version specified, use parent version
        if base_version_id is None:
            if version.parent_version_id:
                base_version_id = version.parent_version_id
            else:
                # No parent version, return all changes as additions
                return {
                    "version": version.version_number,
                    "changes": version.changes,
                    "added": len([c for c in version.changes if c.type == ChangeType.ADDITION]),
                    "modified": len([c for c in version.changes if c.type == ChangeType.MODIFICATION]),
                    "deleted": len([c for c in version.changes if c.type == ChangeType.DELETION]),
                    "reordered": len([c for c in version.changes if c.type == ChangeType.REORDER]),
                    "merged": len([c for c in version.changes if c.type == ChangeType.MERGE]),
                }
        
        # Get base version
        if base_version_id not in self.versions:
            raise KeyError(f"Base version {base_version_id} not found")
            
        base_version = self.versions[base_version_id]
        
        # Compute diff
        # In a real implementation, this would compute actual semantic diffs
        # Here we just return a summary
        return {
            "version": version.version_number,
            "base_version": base_version.version_number,
            "changes": version.changes,
            "added": len([c for c in version.changes if c.type == ChangeType.ADDITION]),
            "modified": len([c for c in version.changes if c.type == ChangeType.MODIFICATION]),
            "deleted": len([c for c in version.changes if c.type == ChangeType.DELETION]),
            "reordered": len([c for c in version.changes if c.type == ChangeType.REORDER]),
            "merged": len([c for c in version.changes if c.type == ChangeType.MERGE]),
        }
    
    def check_project_permission(self, project_id: str, user_id: str, permission: str) -> bool:
        """
        Check if a user has a specific permission for a project.
        
        Args:
            project_id: Project ID
            user_id: User ID
            permission: Permission to check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Mock implementation - in a real system, this would query permissions
        # from other services
        
        # For demonstration, assume all authenticated users have read access
        if permission == "read":
            return True
        
        # For write and approve, check cache or compute
        permission_key = f"{project_id}:{user_id}:{permission}"
        
        # Get from cache or calculate
        if permission_key in self.permissions_cache:
            return self.permissions_cache[permission_key]
        
        # In a real implementation, query the permission system
        # For now, allow access for demonstration
        has_permission = True
        
        # Cache result
        self.permissions_cache[permission_key] = has_permission
        
        return has_permission