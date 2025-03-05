"""
Versions API router for research project version control.

This module provides endpoints for creating, retrieving, and managing versions
of research projects, supporting collaborative development with branches and merge requests.
"""

import logging
from typing import List, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.api.dependencies.auth import get_current_user
from src.api.models.user import User
from src.api.models.versioning import (
    Version, VersionCreate, Branch, BranchCreate,
    MergeRequest, MergeRequestCreate, VersionStatus
)
from src.api.services.version_service import VersionService


logger = logging.getLogger(__name__)
router = APIRouter()
version_service = VersionService()


@router.post("/projects/{project_id}/versions", response_model=Version, status_code=status.HTTP_201_CREATED)
async def create_version(
    project_id: str,
    version_data: VersionCreate,
    current_user: User = Depends(get_current_user)
) -> Version:
    """
    Create a new version of a project.
    
    Args:
        project_id: Project ID
        version_data: Version creation data
        current_user: Authenticated user
        
    Returns:
        Version: Created version
    """
    # Check if user has write access to the project
    if not version_service.check_project_permission(project_id, current_user.id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create versions for this project"
        )
        
    # Ensure project ID in path matches the one in data
    if version_data.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID in path does not match project ID in data"
        )
        
    return version_service.create_version(
        version_data=version_data,
        created_by=current_user.id
    )


@router.get("/projects/{project_id}/versions", response_model=List[Version])
async def list_project_versions(
    project_id: str,
    branch_name: Optional[str] = None,
    status: Optional[VersionStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user)
) -> List[Version]:
    """
    List versions of a project with optional filtering.
    
    Args:
        project_id: Project ID
        branch_name: Optional branch name to filter by
        status: Optional version status to filter by
        skip: Number of items to skip for pagination
        limit: Maximum number of items to return
        current_user: Authenticated user
        
    Returns:
        List[Version]: Project versions
    """
    # Check if user has read access to the project
    if not version_service.check_project_permission(project_id, current_user.id, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view versions for this project"
        )
        
    return version_service.list_project_versions(
        project_id=project_id,
        branch_name=branch_name,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get("/versions/{version_id}", response_model=Version)
async def get_version(
    version_id: str,
    current_user: User = Depends(get_current_user)
) -> Version:
    """
    Get a specific version by ID.
    
    Args:
        version_id: Version ID
        current_user: Authenticated user
        
    Returns:
        Version: Requested version
    """
    version = version_service.get_version(version_id)
    
    # Check if user has read access to the project
    if not version_service.check_project_permission(version.project_id, current_user.id, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this version"
        )
        
    return version


@router.post("/versions/{version_id}/approve", response_model=Version)
async def approve_version(
    version_id: str,
    current_user: User = Depends(get_current_user)
) -> Version:
    """
    Approve a version.
    
    Args:
        version_id: Version ID
        current_user: Authenticated user
        
    Returns:
        Version: Updated version
    """
    version = version_service.get_version(version_id)
    
    # Check if user has approval permission for the project
    if not version_service.check_project_permission(version.project_id, current_user.id, "approve"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve versions for this project"
        )
        
    return version_service.approve_version(version_id, current_user.id)


@router.post("/projects/{project_id}/branches", response_model=Branch, status_code=status.HTTP_201_CREATED)
async def create_branch(
    project_id: str,
    branch_data: BranchCreate,
    current_user: User = Depends(get_current_user)
) -> Branch:
    """
    Create a new branch for a project.
    
    Args:
        project_id: Project ID
        branch_data: Branch creation data
        current_user: Authenticated user
        
    Returns:
        Branch: Created branch
    """
    # Check if user has write access to the project
    if not version_service.check_project_permission(project_id, current_user.id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create branches for this project"
        )
        
    # Ensure project ID in path matches the one in data
    if branch_data.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID in path does not match project ID in data"
        )
        
    return version_service.create_branch(
        branch_data=branch_data,
        created_by=current_user.id
    )


@router.get("/projects/{project_id}/branches", response_model=List[Branch])
async def list_project_branches(
    project_id: str,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[Branch]:
    """
    List branches of a project.
    
    Args:
        project_id: Project ID
        status: Optional branch status to filter by
        current_user: Authenticated user
        
    Returns:
        List[Branch]: Project branches
    """
    # Check if user has read access to the project
    if not version_service.check_project_permission(project_id, current_user.id, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view branches for this project"
        )
        
    return version_service.list_project_branches(
        project_id=project_id,
        status=status
    )


@router.post("/projects/{project_id}/merge-requests", response_model=MergeRequest, status_code=status.HTTP_201_CREATED)
async def create_merge_request(
    project_id: str,
    merge_request_data: MergeRequestCreate,
    current_user: User = Depends(get_current_user)
) -> MergeRequest:
    """
    Create a new merge request.
    
    Args:
        project_id: Project ID
        merge_request_data: Merge request creation data
        current_user: Authenticated user
        
    Returns:
        MergeRequest: Created merge request
    """
    # Check if user has write access to the project
    if not version_service.check_project_permission(project_id, current_user.id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create merge requests for this project"
        )
        
    # Ensure project ID in path matches the one in data
    if merge_request_data.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID in path does not match project ID in data"
        )
        
    return version_service.create_merge_request(
        merge_request_data=merge_request_data,
        created_by=current_user.id
    )


@router.get("/projects/{project_id}/merge-requests", response_model=List[MergeRequest])
async def list_merge_requests(
    project_id: str,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[MergeRequest]:
    """
    List merge requests for a project.
    
    Args:
        project_id: Project ID
        status: Optional merge request status to filter by
        current_user: Authenticated user
        
    Returns:
        List[MergeRequest]: Project merge requests
    """
    # Check if user has read access to the project
    if not version_service.check_project_permission(project_id, current_user.id, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view merge requests for this project"
        )
        
    return version_service.list_merge_requests(
        project_id=project_id,
        status=status
    )


@router.post("/merge-requests/{merge_request_id}/approve", response_model=MergeRequest)
async def approve_merge_request(
    merge_request_id: str,
    current_user: User = Depends(get_current_user)
) -> MergeRequest:
    """
    Approve a merge request.
    
    Args:
        merge_request_id: Merge request ID
        current_user: Authenticated user
        
    Returns:
        MergeRequest: Updated merge request
    """
    merge_request = version_service.get_merge_request(merge_request_id)
    
    # Check if user is a reviewer or has approval permission
    if current_user.id not in merge_request.reviewers and not version_service.check_project_permission(
        merge_request.project_id, current_user.id, "approve"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve this merge request"
        )
        
    return version_service.approve_merge_request(merge_request_id, current_user.id)


@router.post("/merge-requests/{merge_request_id}/merge", response_model=MergeRequest)
async def merge_merge_request(
    merge_request_id: str,
    current_user: User = Depends(get_current_user)
) -> MergeRequest:
    """
    Merge a merge request.
    
    Args:
        merge_request_id: Merge request ID
        current_user: Authenticated user
        
    Returns:
        MergeRequest: Updated merge request
    """
    merge_request = version_service.get_merge_request(merge_request_id)
    
    # Check if user has write permission to the project
    if not version_service.check_project_permission(merge_request.project_id, current_user.id, "write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to merge this merge request"
        )
        
    # Check if merge request has required approvals
    if not version_service.has_required_approvals(merge_request):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Merge request does not have required approvals"
        )
        
    return version_service.merge_merge_request(merge_request_id, current_user.id)


@router.get("/versions/{version_id}/diff", response_model=dict)
async def get_version_diff(
    version_id: str,
    base_version_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get differences between versions.
    
    Args:
        version_id: Version ID
        base_version_id: Optional base version ID to compare against
        current_user: Authenticated user
        
    Returns:
        dict: Version differences
    """
    version = version_service.get_version(version_id)
    
    # Check if user has read access to the project
    if not version_service.check_project_permission(version.project_id, current_user.id, "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this version"
        )
        
    return version_service.get_version_diff(version_id, base_version_id)