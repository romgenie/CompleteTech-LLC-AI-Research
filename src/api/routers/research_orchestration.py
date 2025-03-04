"""
Research Orchestration router for the API.

This module provides endpoints for research orchestration tasks.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path

from src.api.dependencies.auth import User, get_current_user
from src.api.dependencies.database import get_db
from src.api.models.research import (
    ResearchQueryCreate,
    ResearchTask,
    ResearchStatus,
    TaskFilter,
    InfoSourceType
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/queries/", 
    response_model=ResearchTask, 
    status_code=201,
    summary="Submit research query"
)
async def submit_research_query(
    query: ResearchQueryCreate,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResearchTask:
    """
    Submit a new research query for processing.
    
    Args:
        query: Research query data
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        ResearchTask: Created research task
    """
    # Create a new research task
    task_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Convert sources from enum values to strings if needed
    sources = [
        s if isinstance(s, str) else s.value 
        for s in query.sources
    ]
    
    task = {
        "id": task_id,
        "query": query.query,
        "sources": sources,
        "max_results": query.max_results,
        "filters": query.filters,
        "status": ResearchStatus.PENDING.value,
        "created_at": now,
        "updated_at": now,
        "user": current_user.username,
        "results": None
    }
    
    # Insert task into database
    db.research_tasks.insert_one(task)
    
    # Convert task to response model
    return ResearchTask(
        id=task_id,
        query=query.query,
        sources=[InfoSourceType(s) for s in sources],
        max_results=query.max_results,
        filters=query.filters,
        status=ResearchStatus.PENDING,
        created_at=now,
        updated_at=now,
        user=current_user.username,
        results=None
    )


@router.get(
    "/tasks/", 
    response_model=List[ResearchTask],
    summary="List research tasks"
)
async def list_research_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[ResearchTask]:
    """
    List research tasks for the current user.
    
    Args:
        status: Optional status filter
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        List[ResearchTask]: List of research tasks
    """
    # Prepare query
    query = {"user": current_user.username}
    
    if status:
        query["status"] = status
    
    # Query database
    cursor = db.research_tasks.find(query).sort(
        "created_at", -1  # Newest first
    ).skip(offset).limit(limit)
    
    # Convert tasks to response models
    tasks = []
    for task_data in cursor:
        # Convert sources to InfoSourceType
        sources = [
            InfoSourceType(s) if isinstance(s, str) else s 
            for s in task_data.get("sources", [])
        ]
        
        # Convert status
        status_value = task_data.get("status", "pending")
        try:
            status_enum = ResearchStatus(status_value)
        except ValueError:
            status_enum = ResearchStatus.PENDING
        
        # Timestamps
        created_at = task_data.get("created_at")
        updated_at = task_data.get("updated_at")
        completed_at = task_data.get("completed_at")
        
        tasks.append(
            ResearchTask(
                id=task_data["id"],
                query=task_data["query"],
                sources=sources,
                max_results=task_data.get("max_results", 10),
                filters=task_data.get("filters", {}),
                status=status_enum,
                created_at=created_at,
                updated_at=updated_at,
                completed_at=completed_at,
                user=task_data["user"],
                results=task_data.get("results")
            )
        )
    
    return tasks


@router.get(
    "/tasks/{task_id}", 
    response_model=ResearchTask,
    summary="Get research task"
)
async def get_research_task(
    task_id: str = Path(..., description="The ID of the task to retrieve"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ResearchTask:
    """
    Get a specific research task by ID.
    
    Args:
        task_id: ID of the task to retrieve
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        ResearchTask: Research task
        
    Raises:
        HTTPException: If task is not found
    """
    # Query database
    task_data = db.research_tasks.find_one({
        "id": task_id,
        "user": current_user.username
    })
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Convert sources to InfoSourceType
    sources = [
        InfoSourceType(s) if isinstance(s, str) else s 
        for s in task_data.get("sources", [])
    ]
    
    # Convert status
    status_value = task_data.get("status", "pending")
    try:
        status_enum = ResearchStatus(status_value)
    except ValueError:
        status_enum = ResearchStatus.PENDING
    
    # Timestamps
    created_at = task_data.get("created_at")
    updated_at = task_data.get("updated_at")
    completed_at = task_data.get("completed_at")
    
    # Convert to response model
    return ResearchTask(
        id=task_data["id"],
        query=task_data["query"],
        sources=sources,
        max_results=task_data.get("max_results", 10),
        filters=task_data.get("filters", {}),
        status=status_enum,
        created_at=created_at,
        updated_at=updated_at,
        completed_at=completed_at,
        user=task_data["user"],
        results=task_data.get("results")
    )


@router.delete(
    "/tasks/{task_id}", 
    status_code=204,
    summary="Cancel research task"
)
async def cancel_research_task(
    task_id: str = Path(..., description="The ID of the task to cancel"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Cancel a research task or delete a completed task.
    
    Args:
        task_id: ID of the task to cancel
        db: Database connection
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If task is not found
    """
    # Check if task exists
    task_data = db.research_tasks.find_one({
        "id": task_id,
        "user": current_user.username
    })
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get task status
    status = task_data.get("status", "pending")
    
    # If task is in progress, cancel it
    if status in ["pending", "in_progress"]:
        db.research_tasks.update_one(
            {"id": task_id},
            {
                "$set": {
                    "status": ResearchStatus.CANCELLED.value,
                    "updated_at": datetime.now()
                }
            }
        )
    # If task is completed or failed, delete it
    else:
        db.research_tasks.delete_one({"id": task_id})
    
    # 204 No Content response handled by FastAPI


@router.post(
    "/search", 
    response_model=Dict[str, Any],
    summary="Quick search"
)
async def quick_search(
    query: str = Query(..., description="Search query"),
    sources: Optional[List[str]] = Query(None, description="Sources to search"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum results per source"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Perform a quick search without creating a persistent task.
    
    Args:
        query: Search query
        sources: Sources to search
        max_results: Maximum results per source
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Search results
    """
    # This is a simplified implementation
    # In a real system, you would call the actual search service
    
    # Default sources if not specified
    if not sources:
        sources = [s.value for s in InfoSourceType]
    
    # Mock results
    results = {
        "query": query,
        "sources": sources,
        "max_results": max_results,
        "results": {
            source: [
                {
                    "title": f"Result {i+1} for {query} from {source}",
                    "url": f"https://example.com/{source}/result-{i+1}",
                    "summary": f"Mock result summary for {query} from {source}.",
                    "relevance": 1.0 - (i * 0.1),
                }
                for i in range(max_results)
            ]
            for source in sources
        }
    }
    
    return results