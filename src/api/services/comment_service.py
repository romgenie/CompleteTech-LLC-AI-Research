"""
Comment service for annotations and collaborative feedback.

This module implements the business logic for comments and annotations
on research reports, implementations, and other content.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.api.models.comments import (
    Comment, CommentCreate, CommentUpdate,
    CommentStatus, CommentReaction, CommentType
)


logger = logging.getLogger(__name__)


class CommentService:
    """Service for comment operations."""
    
    def __init__(self):
        """Initialize comment service."""
        # In a real implementation, this would connect to a database
        # For now, we'll use in-memory storage for demonstration
        self.comments = {}
        self.comment_reactions = {}
        self.access_rules = {
            # Define which target types require which permissions
            "report": {"read": "read", "write": "comment"},
            "section": {"read": "read", "write": "comment"},
            "implementation": {"read": "read", "write": "comment"},
            "entity": {"read": "read", "write": "comment"},
            "relationship": {"read": "read", "write": "comment"}
        }
        
        # Mock access control for demonstration
        # In a real implementation, this would query permissions from the workspace service
        self.permissions_cache = {}
    
    def create_comment(self, comment_data: CommentCreate, author_id: str) -> Comment:
        """
        Create a new comment or annotation.
        
        Args:
            comment_data: Comment creation data
            author_id: ID of the author
            
        Returns:
            Comment: Created comment
        """
        comment = Comment(
            content=comment_data.content,
            type=comment_data.type,
            target_type=comment_data.target_type,
            target_id=comment_data.target_id,
            text_range=comment_data.text_range,
            author_id=author_id,
            parent_id=comment_data.parent_id,
            attachment_urls=comment_data.attachment_urls,
            metadata=comment_data.metadata
        )
        
        # Store comment
        self.comments[comment.id] = comment
        
        logger.info(f"Created comment {comment.id} by user {author_id}")
        return comment
    
    def get_comment(self, comment_id: str) -> Comment:
        """
        Get a comment by ID.
        
        Args:
            comment_id: Comment ID
            
        Returns:
            Comment: Retrieved comment
            
        Raises:
            KeyError: If comment not found
        """
        if comment_id not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
            
        return self.comments[comment_id]
    
    def update_comment(self, comment_id: str, comment_data: CommentUpdate) -> Comment:
        """
        Update a comment.
        
        Args:
            comment_id: Comment ID
            comment_data: Updated comment data
            
        Returns:
            Comment: Updated comment
            
        Raises:
            KeyError: If comment not found
        """
        if comment_id not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
        
        comment = self.comments[comment_id]
        
        # Update fields if provided
        if comment_data.content is not None:
            comment.content = comment_data.content
            
        if comment_data.status is not None:
            comment.status = comment_data.status
            
        if comment_data.attachment_urls is not None:
            comment.attachment_urls = comment_data.attachment_urls
            
        if comment_data.metadata is not None:
            comment.metadata = comment_data.metadata
        
        comment.updated_at = datetime.utcnow()
        return comment
    
    def delete_comment(self, comment_id: str) -> None:
        """
        Delete a comment.
        
        Args:
            comment_id: Comment ID
            
        Raises:
            KeyError: If comment not found
        """
        if comment_id not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
        
        # Delete reactions
        if comment_id in self.comment_reactions:
            del self.comment_reactions[comment_id]
        
        # Delete comment
        del self.comments[comment_id]
        
        logger.info(f"Deleted comment {comment_id}")
    
    def list_comments(
        self,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[CommentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Comment]:
        """
        List comments with optional filtering.
        
        Args:
            target_type: Filter by target type
            target_id: Filter by target ID
            status: Filter by comment status
            skip: Number of items to skip for pagination
            limit: Maximum number of items to return
            
        Returns:
            List[Comment]: Filtered comments
        """
        results = []
        
        for comment_id, comment in self.comments.items():
            # Apply target type filter
            if target_type and comment.target_type != target_type:
                continue
                
            # Apply target ID filter
            if target_id and comment.target_id != target_id:
                continue
                
            # Apply status filter
            if status and comment.status != status:
                continue
                
            results.append(comment)
        
        # Sort by creation time (newest first) and apply pagination
        return sorted(results, key=lambda c: c.created_at, reverse=True)[skip:skip+limit]
    
    def list_thread_comments(self, target_type: str, target_id: str) -> List[Comment]:
        """
        List top-level comments (threads) for a target.
        
        Args:
            target_type: Target type
            target_id: Target ID
            
        Returns:
            List[Comment]: Top-level comments
        """
        results = []
        
        for comment_id, comment in self.comments.items():
            # Match target type and ID, and only include top-level comments
            if (comment.target_type == target_type and 
                comment.target_id == target_id and 
                comment.parent_id is None):
                results.append(comment)
        
        # Sort by creation time (newest first)
        return sorted(results, key=lambda c: c.created_at, reverse=True)
    
    def list_comment_replies(self, parent_id: str) -> List[Comment]:
        """
        List replies to a specific comment.
        
        Args:
            parent_id: Parent comment ID
            
        Returns:
            List[Comment]: Comment replies
        """
        results = []
        
        for comment_id, comment in self.comments.items():
            # Match parent ID
            if comment.parent_id == parent_id:
                results.append(comment)
        
        # Sort by creation time (oldest first)
        return sorted(results, key=lambda c: c.created_at)
    
    def resolve_comment(self, comment_id: str, resolved_by: str) -> Comment:
        """
        Mark a comment as resolved.
        
        Args:
            comment_id: Comment ID
            resolved_by: User ID who resolved the comment
            
        Returns:
            Comment: Updated comment
            
        Raises:
            KeyError: If comment not found
        """
        if comment_id not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
        
        comment = self.comments[comment_id]
        comment.status = CommentStatus.RESOLVED
        comment.resolved_by = resolved_by
        comment.resolved_at = datetime.utcnow()
        comment.updated_at = datetime.utcnow()
        
        logger.info(f"Comment {comment_id} resolved by user {resolved_by}")
        return comment
    
    def add_comment_reaction(self, comment_id: str, user_id: str, reaction: str) -> CommentReaction:
        """
        Add a reaction to a comment.
        
        Args:
            comment_id: Comment ID
            user_id: User ID
            reaction: Reaction type
            
        Returns:
            CommentReaction: Created reaction
            
        Raises:
            KeyError: If comment not found
        """
        if comment_id not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
        
        comment_reaction = CommentReaction(
            comment_id=comment_id,
            user_id=user_id,
            reaction=reaction
        )
        
        # Store reaction
        if comment_id not in self.comment_reactions:
            self.comment_reactions[comment_id] = []
            
        # Remove any existing reaction of the same type from this user
        self.comment_reactions[comment_id] = [
            r for r in self.comment_reactions.get(comment_id, [])
            if not (r.user_id == user_id and r.reaction == reaction)
        ]
        
        # Add new reaction
        self.comment_reactions[comment_id].append(comment_reaction)
        
        logger.info(f"User {user_id} reacted to comment {comment_id} with {reaction}")
        return comment_reaction
    
    def delete_comment_reaction(self, comment_id: str, user_id: str, reaction: str) -> None:
        """
        Delete a reaction from a comment.
        
        Args:
            comment_id: Comment ID
            user_id: User ID
            reaction: Reaction type
            
        Raises:
            KeyError: If comment not found or reaction not found
        """
        if comment_id not in self.comments:
            raise KeyError(f"Comment {comment_id} not found")
            
        if comment_id not in self.comment_reactions:
            raise KeyError(f"No reactions found for comment {comment_id}")
        
        # Filter out the reaction to delete
        initial_length = len(self.comment_reactions[comment_id])
        self.comment_reactions[comment_id] = [
            r for r in self.comment_reactions[comment_id]
            if not (r.user_id == user_id and r.reaction == reaction)
        ]
        
        # Check if reaction was deleted
        if len(self.comment_reactions[comment_id]) == initial_length:
            raise KeyError(f"Reaction '{reaction}' by user {user_id} not found for comment {comment_id}")
        
        logger.info(f"User {user_id} removed reaction {reaction} from comment {comment_id}")
    
    def check_comment_access(self, target_type: str, target_id: str, user_id: str) -> bool:
        """
        Check if a user has access to comments on a target.
        
        Args:
            target_type: Target type
            target_id: Target ID
            user_id: User ID
            
        Returns:
            bool: True if user has access, False otherwise
        """
        # Mock implementation - in a real system, this would query permissions
        # from the workspace service or other permission systems
        
        # For demonstration, assume all users have read access to all targets
        permission_key = f"{target_type}:{target_id}:{user_id}"
        
        # Get from cache or calculate
        if permission_key in self.permissions_cache:
            return self.permissions_cache[permission_key]
        
        # In a real implementation, query the permission system
        # For now, allow access for all authenticated users
        has_access = True
        
        # Cache result
        self.permissions_cache[permission_key] = has_access
        
        return has_access
    
    def can_modify_comment_status(self, comment: Comment, user_id: str) -> bool:
        """
        Check if a user can modify the status of a comment.
        
        Args:
            comment: Comment to check
            user_id: User ID
            
        Returns:
            bool: True if user can modify status, False otherwise
        """
        # Author can always modify their own comments
        if comment.author_id == user_id:
            return True
        
        # In a real implementation, check if user is a reviewer or admin
        # For now, assume admins can modify any comment
        
        # Mock admin check - in a real system, check user's permissions
        # TODO: Replace with actual permission check
        is_admin = True
        
        return is_admin