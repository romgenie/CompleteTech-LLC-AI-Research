"""
API router for implementation planning system.

This module provides endpoints for creating, managing, and tracking implementation plans.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from datetime import datetime

from ..implementation_planning.service import PlanningService
from ..implementation_planning.planner import ImplementationPlan, ImplementationComponent
from ..implementation_planning.task_planner import Task
from ..implementation_planning.validation import ValidationError
from .models import (
    PlanOptions, 
    PlanUpdate, 
    TaskUpdate,
    Plan,
    PlanList
)

from src.api.dependencies.auth import User, get_current_user
from src.api.dependencies.database import get_db


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/plans",
    response_model=PlanList,
    summary="List implementation plans"
)
async def list_plans(
    skip: int = Query(0, ge=0, description="Number of plans to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of plans to return"),
    status: Optional[str] = Query(None, description="Filter by plan status"),
    search: Optional[str] = Query(None, description="Search term to filter plans"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PlanList:
    """
    List implementation plans with pagination and filtering.
    
    Args:
        skip: Number of plans to skip for pagination
        limit: Maximum number of plans to return
        status: Optional status to filter by
        search: Optional search term to filter plans
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        PlanList containing plans and total count
        
    Raises:
        HTTPException: If listing fails
    """
    try:
        planning_service = PlanningService(
            storage_dir=db.get_storage_path("implementation_plans")
        )
        
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["search"] = search
            
        plans = planning_service.list_plans(
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        total = planning_service.count_plans(filters=filters)
        
        return PlanList(
            total=total,
            plans=plans,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/plans", 
    response_model=Plan,
    status_code=201,
    summary="Create implementation plan"
)
async def create_plan(
    understanding: Dict[str, Any] = Body(..., description="Research paper understanding"),
    options: Optional[PlanOptions] = Body(None, description="Planning options"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Plan:
    """
    Create a complete implementation plan from research paper understanding.
    
    Args:
        understanding: Research paper understanding dict
        options: Optional planning options
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Plan object containing the plan details
        
    Raises:
        HTTPException: If plan creation fails
    """
    try:
        planning_service = PlanningService(
            storage_dir=db.get_storage_path("implementation_plans")
        )
        plan_dict = planning_service.create_implementation_plan(
            understanding, 
            options.dict() if options else None
        )
        return Plan(**plan_dict)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating implementation plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/plans/{plan_id}",
    response_model=Plan,
    summary="Get implementation plan"
)
async def get_plan(
    plan_id: str = Path(..., description="The ID of the plan to retrieve"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Plan:
    """
    Get a specific implementation plan.
    
    Args:
        plan_id: ID of plan to retrieve
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Plan object containing the plan details
        
    Raises:
        HTTPException: If plan is not found
    """
    try:
        planning_service = PlanningService(
            storage_dir=db.get_storage_path("implementation_plans")
        )
        plan_dict = planning_service.get_plan(plan_id)
        if not plan_dict:
            raise HTTPException(status_code=404, detail="Plan not found")
        return Plan(**plan_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/plans/{plan_id}",
    response_model=Plan,
    summary="Update implementation plan" 
)
async def update_plan(
    plan_id: str = Path(..., description="The ID of the plan to update"),
    updates: PlanUpdate = Body(..., description="Updates to apply to the plan"),
    db = Depends(get_db), 
    current_user: User = Depends(get_current_user)
) -> Plan:
    """
    Update an existing implementation plan.
    
    Args:
        plan_id: ID of plan to update
        updates: Updates to apply to the plan
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Plan object containing the updated plan
        
    Raises:
        HTTPException: If plan is not found or validation fails
    """
    try:
        planning_service = PlanningService(
            storage_dir=db.get_storage_path("implementation_plans")
        )
        updated_plan_dict = planning_service.update_plan(plan_id, updates.dict(exclude_unset=True))
        if not updated_plan_dict:
            raise HTTPException(status_code=404, detail="Plan not found")
        return Plan(**updated_plan_dict)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/plans/{plan_id}/tasks/{task_id}",
    response_model=Plan,
    summary="Update task in plan"
)
async def update_task(
    plan_id: str = Path(..., description="The ID of the plan containing the task"),
    task_id: str = Path(..., description="The ID of the task to update"),
    updates: TaskUpdate = Body(..., description="Updates to apply to the task"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Plan:
    """
    Update a task in an implementation plan.
    
    Args:
        plan_id: ID of the plan containing the task
        task_id: ID of task to update 
        updates: Updates to apply to the task
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Plan object containing the updated plan
        
    Raises:
        HTTPException: If plan/task not found or validation fails
    """
    try:
        planning_service = PlanningService(
            storage_dir=db.get_storage_path("implementation_plans")
        )
        updated_plan_dict = planning_service.update_task(
            plan_id, 
            task_id, 
            updates.dict(exclude_unset=True)
        )
        if not updated_plan_dict:
            raise HTTPException(status_code=404, detail="Plan or task not found")
        return Plan(**updated_plan_dict)
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} in plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/plans/{plan_id}",
    status_code=204,
    summary="Delete implementation plan"
)
async def delete_plan(
    plan_id: str = Path(..., description="The ID of the plan to delete"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete an implementation plan.
    
    Args:
        plan_id: ID of plan to delete
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        None
        
    Raises:
        HTTPException: If plan deletion fails
    """
    try:
        planning_service = PlanningService(
            storage_dir=db.get_storage_path("implementation_plans")
        )
        if not planning_service.delete_plan(plan_id):
            raise HTTPException(status_code=404, detail="Plan not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))