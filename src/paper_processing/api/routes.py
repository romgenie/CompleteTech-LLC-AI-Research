"""
API routes for the Paper Processing Pipeline.

This module implements the FastAPI routes for the Paper Processing Pipeline,
providing endpoints for controlling paper processing and retrieving status.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from fastapi.responses import JSONResponse

from ..models.paper import Paper, PaperStatus, add_processing_event
from ..models.state_machine import PaperStateMachine, StateTransitionException
from ..db.models import PaperModel
from ..tasks.processing_tasks import process_paper, cancel_processing_task

# Create router
router = APIRouter(prefix="/papers", tags=["Paper Processing"])

# Configure logging
logger = logging.getLogger(__name__)


async def get_paper_model(paper_id: str) -> PaperModel:
    """
    Helper to get a paper by ID.
    
    Args:
        paper_id: The ID of the paper to get
        
    Returns:
        The paper model
        
    Raises:
        HTTPException: If the paper is not found
    """
    paper_model = PaperModel.get_by_id(paper_id)
    if not paper_model:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    return paper_model


@router.post("/{paper_id}/process")
async def start_paper_processing(
    background_tasks: BackgroundTasks,
    paper_id: str = Path(..., description="The ID of the paper to process")
) -> Dict[str, Any]:
    """
    Process a paper.
    
    Initiates the processing of a paper that has been uploaded.
    
    Args:
        background_tasks: FastAPI background tasks
        paper_id: The ID of the paper to process
        
    Returns:
        Dict containing the process request result
    """
    logger.info(f"Process request for paper {paper_id}")
    
    try:
        # Get the paper
        paper_model = await get_paper_model(paper_id)
        paper = paper_model.to_domain()
        
        # Check if paper is in a state that can be processed
        if paper.status not in [PaperStatus.UPLOADED, PaperStatus.FAILED]:
            return JSONResponse(
                status_code=400,
                content={
                    "paper_id": paper_id,
                    "status": "error",
                    "message": f"Paper is already in {paper.status.value} state"
                }
            )
        
        # Queue the processing task
        background_tasks.add_task(process_paper.delay, paper_id)
        
        # Update paper status to QUEUED
        state_machine = PaperStateMachine(paper)
        try:
            paper = state_machine.transition_to(
                PaperStatus.QUEUED, 
                "Paper queued for processing via API"
            )
            
            # Save the updated paper
            paper_model.update_from_domain(paper)
            paper_model.save()
            
            return {
                "paper_id": paper_id,
                "status": "success",
                "message": "Paper queued for processing",
                "current_status": paper.status.value,
                "queue_time": datetime.utcnow().isoformat()
            }
        except StateTransitionException as e:
            logger.error(f"State transition error for paper {paper_id}: {e}")
            return JSONResponse(
                status_code=400,
                content={
                    "paper_id": paper_id,
                    "status": "error",
                    "message": str(e)
                }
            )
            
    except Exception as e:
        logger.error(f"Error processing paper {paper_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "paper_id": paper_id,
                "status": "error",
                "message": f"Error processing paper: {str(e)}"
            }
        )


@router.post("/batch/process")
async def process_papers_batch(
    background_tasks: BackgroundTasks,
    paper_ids: List[str]
) -> Dict[str, Any]:
    """
    Process multiple papers in batch.
    
    Initiates the processing of multiple papers in batch.
    
    Args:
        background_tasks: FastAPI background tasks
        paper_ids: List of paper IDs to process
        
    Returns:
        Dict containing the batch process request result
    """
    logger.info(f"Batch process request for {len(paper_ids)} papers")
    
    results = {
        "total": len(paper_ids),
        "queued": 0,
        "skipped": 0,
        "errors": 0,
        "details": []
    }
    
    for paper_id in paper_ids:
        try:
            # Get the paper
            paper_model = PaperModel.get_by_id(paper_id)
            if not paper_model:
                results["errors"] += 1
                results["details"].append({
                    "paper_id": paper_id,
                    "status": "error",
                    "message": "Paper not found"
                })
                continue
                
            paper = paper_model.to_domain()
            
            # Check if paper is in a state that can be processed
            if paper.status not in [PaperStatus.UPLOADED, PaperStatus.FAILED]:
                results["skipped"] += 1
                results["details"].append({
                    "paper_id": paper_id,
                    "status": "skipped",
                    "message": f"Paper is already in {paper.status.value} state"
                })
                continue
            
            # Queue the processing task
            background_tasks.add_task(process_paper.delay, paper_id)
            
            # Update paper status to QUEUED
            state_machine = PaperStateMachine(paper)
            try:
                paper = state_machine.transition_to(
                    PaperStatus.QUEUED, 
                    "Paper queued for batch processing via API"
                )
                
                # Save the updated paper
                paper_model.update_from_domain(paper)
                paper_model.save()
                
                results["queued"] += 1
                results["details"].append({
                    "paper_id": paper_id,
                    "status": "queued",
                    "message": "Paper queued for processing"
                })
            except StateTransitionException as e:
                results["errors"] += 1
                results["details"].append({
                    "paper_id": paper_id,
                    "status": "error",
                    "message": f"State transition error: {str(e)}"
                })
                
        except Exception as e:
            results["errors"] += 1
            results["details"].append({
                "paper_id": paper_id,
                "status": "error",
                "message": f"Error: {str(e)}"
            })
    
    return results


@router.get("/{paper_id}/status")
async def get_paper_status(
    paper_id: str = Path(..., description="The ID of the paper to check")
) -> Dict[str, Any]:
    """
    Get the processing status of a paper.
    
    Retrieves the current processing status and details for a paper.
    
    Args:
        paper_id: The ID of the paper to check
        
    Returns:
        Dict containing the paper status information
    """
    logger.info(f"Status request for paper {paper_id}")
    
    try:
        # Get the paper
        paper_model = await get_paper_model(paper_id)
        paper = paper_model.to_domain()
        
        # Extract status history
        history = [
            {
                "timestamp": event.timestamp.isoformat(),
                "status": event.status.value,
                "message": event.message,
                "details": event.details
            }
            for event in paper.processing_history
        ]
        
        # Calculate progress based on status
        progress_map = {
            PaperStatus.UPLOADED: 0,
            PaperStatus.QUEUED: 5,
            PaperStatus.PROCESSING: 20,
            PaperStatus.EXTRACTING_ENTITIES: 40,
            PaperStatus.EXTRACTING_RELATIONSHIPS: 60,
            PaperStatus.BUILDING_KNOWLEDGE_GRAPH: 80,
            PaperStatus.ANALYZED: 90,
            PaperStatus.IMPLEMENTATION_READY: 100,
            PaperStatus.FAILED: 0
        }
        
        progress = progress_map.get(paper.status, 0)
        
        return {
            "paper_id": paper_id,
            "status": paper.status.value,
            "title": paper.title,
            "progress": progress,
            "implementation_ready": paper.implementation_ready,
            "knowledge_graph_id": paper.knowledge_graph_id,
            "updated_at": paper.processing_history[-1].timestamp.isoformat() if paper.processing_history else None,
            "history": history,
            "entity_count": len(paper.entities),
            "relationship_count": len(paper.relationships)
        }
    except Exception as e:
        logger.error(f"Error retrieving status for paper {paper_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "paper_id": paper_id,
                "status": "error",
                "message": f"Error retrieving paper status: {str(e)}"
            }
        )


@router.get("/{paper_id}/progress")
async def get_paper_progress(
    paper_id: str = Path(..., description="The ID of the paper to check")
) -> Dict[str, Any]:
    """
    Get detailed progress information for a paper.
    
    Retrieves detailed progress information for a paper being processed.
    
    Args:
        paper_id: The ID of the paper to check
        
    Returns:
        Dict containing detailed progress information
    """
    logger.info(f"Progress request for paper {paper_id}")
    
    try:
        # Get the paper
        paper_model = await get_paper_model(paper_id)
        paper = paper_model.to_domain()
        
        # Calculate progress based on status
        progress_map = {
            PaperStatus.UPLOADED: 0,
            PaperStatus.QUEUED: 5,
            PaperStatus.PROCESSING: 20,
            PaperStatus.EXTRACTING_ENTITIES: 40,
            PaperStatus.EXTRACTING_RELATIONSHIPS: 60,
            PaperStatus.BUILDING_KNOWLEDGE_GRAPH: 80,
            PaperStatus.ANALYZED: 90,
            PaperStatus.IMPLEMENTATION_READY: 100,
            PaperStatus.FAILED: 0
        }
        
        overall_progress = progress_map.get(paper.status, 0)
        
        # Define step statuses based on paper status
        steps = [
            {
                "name": "document_processing",
                "display_name": "Document Processing",
                "status": _get_step_status(paper.status, PaperStatus.PROCESSING),
                "progress": _get_step_progress(paper.status, PaperStatus.PROCESSING)
            },
            {
                "name": "entity_extraction",
                "display_name": "Entity Extraction",
                "status": _get_step_status(paper.status, PaperStatus.EXTRACTING_ENTITIES),
                "progress": _get_step_progress(paper.status, PaperStatus.EXTRACTING_ENTITIES)
            },
            {
                "name": "relationship_extraction",
                "display_name": "Relationship Extraction",
                "status": _get_step_status(paper.status, PaperStatus.EXTRACTING_RELATIONSHIPS),
                "progress": _get_step_progress(paper.status, PaperStatus.EXTRACTING_RELATIONSHIPS)
            },
            {
                "name": "knowledge_graph_building",
                "display_name": "Knowledge Graph Building",
                "status": _get_step_status(paper.status, PaperStatus.BUILDING_KNOWLEDGE_GRAPH),
                "progress": _get_step_progress(paper.status, PaperStatus.BUILDING_KNOWLEDGE_GRAPH)
            },
            {
                "name": "analysis",
                "display_name": "Analysis",
                "status": _get_step_status(paper.status, PaperStatus.ANALYZED),
                "progress": _get_step_progress(paper.status, PaperStatus.ANALYZED)
            }
        ]
        
        return {
            "paper_id": paper_id,
            "title": paper.title,
            "status": paper.status.value,
            "progress": overall_progress,
            "steps": steps,
            "entity_count": len(paper.entities),
            "relationship_count": len(paper.relationships),
            "updated_at": paper.processing_history[-1].timestamp.isoformat() if paper.processing_history else None
        }
    except Exception as e:
        logger.error(f"Error retrieving progress for paper {paper_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "paper_id": paper_id,
                "status": "error",
                "message": f"Error retrieving paper progress: {str(e)}"
            }
        )


def _get_step_status(current_status: PaperStatus, step_status: PaperStatus) -> str:
    """
    Get the status for a processing step.
    
    Args:
        current_status: Current paper status
        step_status: Status corresponding to the step
        
    Returns:
        Status string for the step
    """
    status_order = [
        PaperStatus.UPLOADED,
        PaperStatus.QUEUED,
        PaperStatus.PROCESSING,
        PaperStatus.EXTRACTING_ENTITIES,
        PaperStatus.EXTRACTING_RELATIONSHIPS,
        PaperStatus.BUILDING_KNOWLEDGE_GRAPH,
        PaperStatus.ANALYZED,
        PaperStatus.IMPLEMENTATION_READY
    ]
    
    if current_status == PaperStatus.FAILED:
        # If the status is exactly the step we're checking, it failed during this step
        if step_status == current_status:
            return "failed"
        # For other steps, use normal logic
    
    current_idx = status_order.index(current_status) if current_status in status_order else -1
    step_idx = status_order.index(step_status) if step_status in status_order else -1
    
    if current_idx < 0 or step_idx < 0:
        return "unknown"
    
    if step_idx < current_idx:
        return "completed"
    elif step_idx == current_idx:
        return "in_progress"
    else:
        return "pending"


def _get_step_progress(current_status: PaperStatus, step_status: PaperStatus) -> int:
    """
    Get the progress for a processing step.
    
    Args:
        current_status: Current paper status
        step_status: Status corresponding to the step
        
    Returns:
        Progress percentage for the step
    """
    step_status_str = _get_step_status(current_status, step_status)
    
    if step_status_str == "completed":
        return 100
    elif step_status_str == "in_progress":
        return 50  # We could make this more granular with subtask tracking
    elif step_status_str == "failed":
        return 0
    else:  # pending or unknown
        return 0


@router.post("/{paper_id}/cancel")
async def cancel_processing(
    background_tasks: BackgroundTasks,
    paper_id: str = Path(..., description="The ID of the paper to cancel")
) -> Dict[str, Any]:
    """
    Cancel the processing of a paper.
    
    Cancels the ongoing processing of a paper.
    
    Args:
        background_tasks: FastAPI background tasks
        paper_id: The ID of the paper to cancel
        
    Returns:
        Dict containing the cancellation result
    """
    logger.info(f"Cancel request for paper {paper_id}")
    
    try:
        # Get the paper
        paper_model = await get_paper_model(paper_id)
        paper = paper_model.to_domain()
        
        # Check if paper is in a state that can be cancelled
        if paper.status in [PaperStatus.UPLOADED, PaperStatus.ANALYZED, 
                           PaperStatus.IMPLEMENTATION_READY, PaperStatus.FAILED]:
            return JSONResponse(
                status_code=400,
                content={
                    "paper_id": paper_id,
                    "status": "error",
                    "message": f"Paper in {paper.status.value} state cannot be cancelled"
                }
            )
        
        # Call the cancellation task
        background_tasks.add_task(cancel_processing_task.delay, paper_id)
        
        # Update the paper status
        paper = add_processing_event(
            paper,
            paper.status,  # Don't change status yet - task will do that
            "Processing cancellation requested"
        )
        
        # Save the updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return {
            "paper_id": paper_id,
            "status": "success",
            "message": "Processing cancellation requested",
            "current_status": paper.status.value
        }
    except Exception as e:
        logger.error(f"Error canceling processing for paper {paper_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "paper_id": paper_id,
                "status": "error",
                "message": f"Error canceling processing: {str(e)}"
            }
        )


@router.get("/stats")
async def get_processing_stats() -> Dict[str, Any]:
    """
    Get paper processing statistics.
    
    Retrieves statistics about paper processing, including counts by status,
    processing times, and other metrics.
    
    Returns:
        Dict containing processing statistics
    """
    logger.info("Processing statistics request")
    
    try:
        # Get statistics from the model
        # In a real implementation, this would query aggregate statistics
        # For now, we'll create some sample statistics
        
        # Count papers by status
        status_counts = {status.value: 0 for status in PaperStatus}
        
        # Generate sample data
        status_counts.update({
            PaperStatus.UPLOADED.value: 10,
            PaperStatus.QUEUED.value: 3,
            PaperStatus.PROCESSING.value: 2,
            PaperStatus.EXTRACTING_ENTITIES.value: 1,
            PaperStatus.EXTRACTING_RELATIONSHIPS.value: 1,
            PaperStatus.BUILDING_KNOWLEDGE_GRAPH.value: 1,
            PaperStatus.ANALYZED.value: 5,
            PaperStatus.IMPLEMENTATION_READY.value: 3,
            PaperStatus.FAILED.value: 2
        })
        
        total_papers = sum(status_counts.values())
        
        return {
            "total_papers": total_papers,
            "papers_by_status": status_counts,
            "avg_processing_time": 120.5,  # seconds
            "avg_entity_count": 25.3,
            "avg_relationship_count": 18.7,
            "success_rate": 0.92,  # 92% success rate
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving processing statistics: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error retrieving processing statistics: {str(e)}"
            }
        )


@router.get("/search")
async def search_papers(
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
) -> Dict[str, Any]:
    """
    Search for papers.
    
    Searches for papers matching the given criteria.
    
    Args:
        query: Optional search query
        status: Optional status filter
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        Dict containing search results
    """
    logger.info(f"Search papers request: query={query}, status={status}")
    
    try:
        # Convert status string to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = PaperStatus(status)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": f"Invalid status: {status}"
                    }
                )
        
        # In a real implementation, this would query the database
        # For now, we'll return an empty result
        
        return {
            "count": 0,
            "total": 0,
            "papers": [],
            "query": query,
            "status": status,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error searching papers: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error searching papers: {str(e)}"
            }
        )