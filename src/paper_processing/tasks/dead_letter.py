"""
Dead letter queue handling for the Paper Processing Pipeline.

This module implements functionality for handling tasks that have
exceeded their retry limits and need special attention.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from .celery_app import app

logger = logging.getLogger(__name__)


@app.task(name='paper_processing.tasks.dead_letter_task', bind=True)
def dead_letter_task(self, task_name: str, args: List[Any], kwargs: Dict[str, Any], 
                   error: Optional[str] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handles tasks that have exceeded their retry limits.
    
    This task is the final destination for tasks that have failed repeatedly.
    It records the failure information and can trigger alerts or other
    remediation actions.
    
    Args:
        self: The Celery task instance
        task_name: The name of the original task that failed
        args: The positional arguments of the original task
        kwargs: The keyword arguments of the original task
        error: The error message that caused the task to fail
        metadata: Additional metadata about the task failure
        
    Returns:
        Dict containing information about the dead letter handling
    """
    logger.error(f"Dead letter task received for {task_name}")
    
    # Extract paper_id if available
    paper_id = None
    if args and len(args) > 0:
        paper_id = args[0]
    elif kwargs and 'paper_id' in kwargs:
        paper_id = kwargs['paper_id']
    
    # Record the failure with timestamp
    failure_record = {
        'task_name': task_name,
        'args': args,
        'kwargs': kwargs,
        'error': error,
        'timestamp': datetime.utcnow().isoformat(),
        'paper_id': paper_id,
        'task_id': self.request.id,
        'metadata': metadata or {}
    }
    
    # Log the failure details
    logger.error(f"Task failure recorded: {json.dumps(failure_record, default=str)}")
    
    # In production, this would typically:
    # 1. Store the failure record in a database for review
    # 2. Send alerts via email, Slack, or other channels
    # 3. Potentially trigger remediation workflows
    # 4. Update the paper status to show failure
    
    # If there's a paper_id, update the paper status to FAILED
    if paper_id:
        try:
            # This is where we would update the paper status in the database
            # For now, just log that we would do this
            logger.info(f"Would update paper {paper_id} status to FAILED")
            
            # In future implementation:
            # from ..models.paper import PaperStatus
            # from ..db.repositories import paper_repository
            # paper_repository.update_status(paper_id, PaperStatus.FAILED, 
            #                               error_details={'task': task_name, 'error': error})
        except Exception as e:
            logger.error(f"Error updating paper status: {e}")
    
    # Return information about the handling
    return {
        'status': 'recorded',
        'paper_id': paper_id,
        'task_name': task_name,
        'error': error,
        'timestamp': datetime.utcnow().isoformat()
    }


def dead_letter_queue(task_name: str):
    """
    Decorator to send failed tasks to a dead-letter queue
    after max retries are exhausted.
    
    This decorator wraps tasks to catch MaxRetriesExceededError
    exceptions and forward them to the dead letter queue.
    
    Args:
        task_name: The name of the task being decorated
        
    Returns:
        Decorator function
    """
    from functools import wraps
    from celery.exceptions import MaxRetriesExceededError
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MaxRetriesExceededError as exc:
                logger.error(f"Max retries exceeded for task {task_name}: {exc}")
                
                # Extract metadata about the failure
                metadata = {
                    'retries': kwargs.get('request', {}).get('retries', 0),
                    'task_id': kwargs.get('request', {}).get('id', 'unknown'),
                    'origin': 'MaxRetriesExceededError'
                }
                
                # Send to dead letter queue
                dead_letter_task.delay(task_name, args, kwargs, 
                                       error=str(exc),
                                       metadata=metadata)
                
                # Re-raise the exception to maintain the original behavior
                raise
            except Exception as exc:
                logger.error(f"Unexpected error in task {task_name}: {exc}")
                
                # For unexpected exceptions, we also send to dead letter queue,
                # but with different metadata to distinguish from retry exhaustion
                metadata = {
                    'origin': 'UnexpectedException',
                    'exception_type': type(exc).__name__
                }
                
                # Send to dead letter queue
                dead_letter_task.delay(task_name, args, kwargs, 
                                       error=str(exc),
                                       metadata=metadata)
                
                # Re-raise the exception
                raise
        return wrapper
    return decorator