"""
Comments API router for collaborative annotations.

This module provides endpoints for creating, retrieving, and managing comments
and annotations on research reports and other content.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.api.dependencies.auth import get_current_user
from src.api.models.user import User
from src.api.models.comments import (
    Comment, CommentCreate, CommentUpdate,
    CommentStatus, CommentReaction
)
from src.api.services.comment_service import CommentService


logger = logging.getLogger(__name__)
router = APIRouter()
comment_service = CommentService()


@router.post("/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user)
) -> Comment:
    """
    Create a new comment or annotation.
    
    Args:
        comment_data: Comment creation data
        current_user: Authenticated user
        
    Returns:
        Comment: Created comment
    """
    return comment_service.create_comment(
        comment_data=comment_data,
        author_id=current_user.id
    )


@router.get("/comments", response_model=List[Comment])
async def list_comments(
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    status: Optional[CommentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user)
) -> List[Comment]:
    """
    List comments with optional filtering.
    
    Args:
        target_type: Filter by target type (e.g., 'report', 'section')
        target_id: Filter by target ID
        status: Filter by comment status
        skip: Number of items to skip for pagination
        limit: Maximum number of items to return
        current_user: Authenticated user
        
    Returns:
        List[Comment]: Filtered comments
    """
    # Check if user has permission to view these comments
    if target_type and target_id:
        if not comment_service.check_comment_access(target_type, target_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access these comments"
            )
            
    return comment_service.list_comments(
        target_type=target_type,
        target_id=target_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get("/comments/{comment_id}", response_model=Comment)
async def get_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
) -> Comment:
    """
    Get a specific comment by ID.
    
    Args:
        comment_id: Comment ID
        current_user: Authenticated user
        
    Returns:
        Comment: Requested comment
    """
    comment = comment_service.get_comment(comment_id)
    
    # Check if user can access the comment's target
    if not comment_service.check_comment_access(comment.target_type, comment.target_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this comment"
        )
        
    return comment


@router.put("/comments/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user)
) -> Comment:
    """
    Update a comment.
    
    Args:
        comment_id: Comment ID
        comment_data: Updated comment data
        current_user: Authenticated user
        
    Returns:
        Comment: Updated comment
    """
    comment = comment_service.get_comment(comment_id)
    
    # Check if user is the author or has admin permissions
    if comment.author_id != current_user.id and "admin" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this comment"
        )
        
    return comment_service.update_comment(comment_id, comment_data)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a comment.
    
    Args:
        comment_id: Comment ID
        current_user: Authenticated user
    """
    comment = comment_service.get_comment(comment_id)
    
    # Check if user is the author or has admin permissions
    if comment.author_id != current_user.id and "admin" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this comment"
        )
        
    comment_service.delete_comment(comment_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@router.post("/comments/{comment_id}/resolve", response_model=Comment)
async def resolve_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
) -> Comment:
    """
    Mark a comment as resolved.
    
    Args:
        comment_id: Comment ID
        current_user: Authenticated user
        
    Returns:
        Comment: Updated comment
    """
    comment = comment_service.get_comment(comment_id)
    
    # Check if user can modify the comment status
    if not comment_service.can_modify_comment_status(comment, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to resolve this comment"
        )
        
    return comment_service.resolve_comment(comment_id, resolved_by=current_user.id)


@router.post("/comments/{comment_id}/reactions", response_model=CommentReaction)
async def add_reaction(
    comment_id: str,
    reaction: str,
    current_user: User = Depends(get_current_user)
) -> CommentReaction:
    """
    Add a reaction to a comment.
    
    Args:
        comment_id: Comment ID
        reaction: Reaction type (e.g., 'like', 'heart')
        current_user: Authenticated user
        
    Returns:
        CommentReaction: Created reaction
    """
    comment = comment_service.get_comment(comment_id)
    
    # Check if user has access to the comment
    if not comment_service.check_comment_access(comment.target_type, comment.target_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to react to this comment"
        )
        
    return comment_service.add_comment_reaction(
        comment_id=comment_id,
        user_id=current_user.id,
        reaction=reaction
    )


@router.delete("/comments/{comment_id}/reactions/{reaction}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reaction(
    comment_id: str,
    reaction: str,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a reaction from a comment.
    
    Args:
        comment_id: Comment ID
        reaction: Reaction type
        current_user: Authenticated user
    """
    comment_service.delete_comment_reaction(
        comment_id=comment_id,
        user_id=current_user.id,
        reaction=reaction
    )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})


@router.get("/comments/threads", response_model=List[Comment])
async def list_comment_threads(
    target_type: str,
    target_id: str,
    current_user: User = Depends(get_current_user)
) -> List[Comment]:
    """
    List top-level comments (threads) for a target.
    
    Args:
        target_type: Target type
        target_id: Target ID
        current_user: Authenticated user
        
    Returns:
        List[Comment]: Top-level comments
    """
    # Check if user has permission to view these comments
    if not comment_service.check_comment_access(target_type, target_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access these comments"
        )
        
    return comment_service.list_thread_comments(target_type, target_id)


@router.get("/comments/{comment_id}/replies", response_model=List[Comment])
async def list_comment_replies(
    comment_id: str,
    current_user: User = Depends(get_current_user)
) -> List[Comment]:
    """
    List replies to a specific comment.
    
    Args:
        comment_id: Comment ID
        current_user: Authenticated user
        
    Returns:
        List[Comment]: Comment replies
    """
    comment = comment_service.get_comment(comment_id)
    
    # Check if user has access to the comment's target
    if not comment_service.check_comment_access(comment.target_type, comment.target_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this comment's replies"
        )
        
    return comment_service.list_comment_replies(comment_id)