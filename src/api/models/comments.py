"""
Comment and annotation models for collaborative research.

This module defines models for commenting on and annotating research reports,
implementations, and knowledge graph entities.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class CommentType(str, Enum):
    """Types of comments."""
    GENERAL = "general"  # General comment on the document
    ANNOTATION = "annotation"  # Specific annotation of a portion of text
    REVIEW = "review"  # Formal review comment
    SUGGESTION = "suggestion"  # Suggested edit
    QUESTION = "question"  # Question for other collaborators
    ANSWER = "answer"  # Answer to a question


class CommentStatus(str, Enum):
    """Status of comments."""
    OPEN = "open"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class TextRange(BaseModel):
    """Range of text in a document for annotations."""
    start_offset: int
    end_offset: int
    section_id: Optional[str] = None  # ID of the document section if applicable


class Comment(BaseModel):
    """Comment or annotation on a research document or entity."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    type: CommentType = CommentType.GENERAL
    status: CommentStatus = CommentStatus.OPEN
    
    # Target information
    target_type: str  # 'report', 'section', 'implementation', 'entity', 'relationship'
    target_id: str  # ID of the target object
    text_range: Optional[TextRange] = None  # For annotations, the text range being commented on
    
    # User and timestamps
    author_id: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Threading
    parent_id: Optional[str] = None  # ID of parent comment if this is a reply
    resolved_by: Optional[str] = None  # User ID who resolved the comment
    resolved_at: Optional[datetime] = None
    
    # Additional data
    attachment_urls: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CommentReaction(BaseModel):
    """User reaction to a comment."""
    comment_id: str
    user_id: str
    reaction: str  # e.g., 'like', 'heart', 'thumbs_up', etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommentCreate(BaseModel):
    """Schema for comment creation."""
    content: str
    type: CommentType = CommentType.GENERAL
    target_type: str
    target_id: str
    text_range: Optional[TextRange] = None
    parent_id: Optional[str] = None
    attachment_urls: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CommentUpdate(BaseModel):
    """Schema for comment updates."""
    content: Optional[str] = None
    status: Optional[CommentStatus] = None
    attachment_urls: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


# Specialized annotation types for specific research content
class ResearchAnnotation(Comment):
    """Specialized annotation for research reports with research-specific metadata."""
    citation: Optional[str] = None  # If comment includes citation to support the annotation
    significance: Optional[str] = None  # 'low', 'medium', 'high'
    keywords: List[str] = Field(default_factory=list)  # Research keywords related to annotation


class CodeAnnotation(Comment):
    """Specialized annotation for code implementations."""
    code_suggestion: Optional[str] = None  # Suggested code changes
    line_numbers: Optional[List[int]] = None  # Line numbers being commented on
    file_path: Optional[str] = None  # Path to the file being commented on