"""
API models for implementation planning.

This module defines Pydantic models for validating API requests and responses 
for the implementation planning system.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class PlanOptions(BaseModel):
    """Options for plan creation."""
    
    language: Optional[str] = Field(
        None, 
        description="Target implementation language"
    )
    framework: Optional[str] = Field(
        None,
        description="Target framework/library"
    )
    max_tasks: Optional[int] = Field(
        None,
        description="Maximum number of tasks to generate",
        gt=0
    )
    priority_factors: Optional[Dict[str, float]] = Field(
        None,
        description="Weighting factors for priority calculation"
    )
    custom_requirements: Optional[List[str]] = Field(
        None,
        description="Additional implementation requirements"
    )


class PlanUpdate(BaseModel):
    """Model for plan updates."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    estimated_timeline: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class TaskUpdate(BaseModel):
    """Model for task updates."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[float] = Field(None, gt=0)
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = None
    dependencies: Optional[List[str]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Implement data preprocessing",
                "description": "Create preprocessing pipeline for input data",
                "estimated_hours": 4.5,
                "priority": 2,
                "status": "in_progress",
                "dependencies": ["setup_environment", "design_interfaces"]
            }
        }


class TaskBase(BaseModel):
    """Base model for tasks."""
    
    id: str
    name: str
    description: str
    estimated_hours: float = Field(..., gt=0)
    priority: int = Field(..., ge=1, le=5)
    status: str
    dependencies: List[str] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class PlanComponent(BaseModel):
    """Model for implementation components."""
    
    name: str
    type: str
    description: str
    source_reference: Optional[str] = None
    interfaces: List[str] = []
    dependencies: List[str] = []


class Plan(BaseModel):
    """Model for implementation plans."""
    
    id: str
    title: str
    description: str
    paper_id: str
    components: List[PlanComponent]
    tasks: List[TaskBase]
    requirements: Dict[str, Any]
    estimated_timeline: Dict[str, Any]
    critical_path: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    created_by: str
    repository_url: Optional[HttpUrl] = None


class PlanList(BaseModel):
    """Model for paginated plan lists."""
    
    total: int
    plans: List[Plan]
    skip: int
    limit: int