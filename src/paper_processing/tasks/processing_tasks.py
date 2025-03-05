"""
Core processing tasks for the Paper Processing Pipeline.

This module implements the primary Celery tasks for processing papers through
the full lifecycle from document extraction to knowledge graph integration.
"""

import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from celery import Task, chain, group
from celery.exceptions import MaxRetriesExceededError

from paper_processing.models.paper import Paper, PaperStatus, add_processing_event
from paper_processing.models.state_machine import PaperStateMachine, StateTransitionException
from paper_processing.tasks.celery_app import app
from paper_processing.tasks.dead_letter import dead_letter_task
from paper_processing.db.models import PaperModel

# Configure logging
logger = logging.getLogger(__name__)


# Base task class with error handling
class PaperProcessingTask(Task):
    """Base task class for paper processing tasks with enhanced error handling."""
    
    # Automatic retries for transient failures
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    # Don't propagate exceptions to the next task in the chain
    ignore_result = False
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure by logging and sending to dead letter queue."""
        paper_id = kwargs.get('paper_id', args[0] if args else None)
        logger.error(f"Task {self.name}[{task_id}] for paper {paper_id} failed: {exc}")
        
        # Check if we've exceeded max retries
        if isinstance(exc, MaxRetriesExceededError) or not self.request.retries:
            # Send to dead letter queue for manual inspection
            dead_letter_task.delay(
                task_id=task_id,
                paper_id=paper_id,
                task_name=self.name,
                exception=str(exc),
                traceback=str(einfo),
                args=args,
                kwargs=kwargs
            )
            
            # Update paper status to failed if paper_id is available
            if paper_id:
                try:
                    # Get paper from database
                    paper_model = PaperModel.get_by_id(paper_id)
                    if paper_model:
                        paper = paper_model.to_domain()
                        
                        # Transition to failed state
                        state_machine = PaperStateMachine(paper)
                        try:
                            paper = state_machine.transition_to(
                                PaperStatus.FAILED,
                                f"Failed in task {self.name}: {exc}"
                            )
                            # Save updated paper
                            paper_model.update_from_domain(paper)
                            paper_model.save()
                        except StateTransitionException as e:
                            logger.error(f"Could not transition paper {paper_id} to FAILED state: {e}")
                except Exception as e:
                    logger.error(f"Error updating paper {paper_id} status to FAILED: {e}")
                    
        super().on_failure(exc, task_id, args, kwargs, einfo)


@app.task(bind=True, base=PaperProcessingTask)
def process_paper(self, paper_id: str) -> str:
    """
    Main entry point for paper processing.
    
    Initiates the processing workflow for a paper. This task coordinates the
    overall processing flow and transitions the paper through the state machine.
    
    Args:
        paper_id: ID of the paper to process
        
    Returns:
        Paper ID for chaining
    """
    logger.info(f"Starting paper processing for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Create state machine and transition to processing
        state_machine = PaperStateMachine(paper)
        
        # If paper is in UPLOADED state, transition to QUEUED first
        if paper.status == PaperStatus.UPLOADED:
            paper = state_machine.transition_to(
                PaperStatus.QUEUED,
                "Paper queued for processing"
            )
        
        # Then transition to PROCESSING
        if paper.status == PaperStatus.QUEUED:
            paper = state_machine.transition_to(
                PaperStatus.PROCESSING,
                "Starting paper processing"
            )
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        # Start the processing chain
        processing_chain = chain(
            process_document.s(paper_id),
            extract_entities.s(),
            extract_relationships.s(),
            build_knowledge_graph.s(),
            check_implementation_readiness.s()
        )
        
        # Execute the chain
        processing_chain.delay()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error initiating processing for paper {paper_id}: {e}")
        self.retry(exc=e)


@app.task(bind=True, base=PaperProcessingTask)
def process_document(self, paper_id: str) -> str:
    """
    Process the document content.
    
    Extracts text and metadata from the document file.
    
    Args:
        paper_id: ID of the paper to process
        
    Returns:
        Paper ID for chaining
    """
    logger.info(f"Processing document for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Simulate document processing
        # In a full implementation, this would extract text from PDF/DOCX files,
        # parse document structure, extract metadata, etc.
        time.sleep(2)  # Simulate processing time
        
        # Update paper with processing results
        paper = add_processing_event(
            paper,
            paper.status,
            "Document processed successfully",
            {
                "page_count": 10,
                "word_count": 5000,
                "processing_time": 2.0
            }
        )
        
        # Initialize statistics if not already present
        if not paper.statistics:
            paper.statistics = {
                "processing_time": 2.0,
                "entity_count": 0,
                "relationship_count": 0,
                "page_count": 10,
                "word_count": 5000
            }
        else:
            paper.statistics.page_count = 10
            paper.statistics.word_count = 5000
            paper.statistics.processing_time = 2.0
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error processing document for paper {paper_id}: {e}")
        self.retry(exc=e)


@app.task(bind=True, base=PaperProcessingTask)
def extract_entities(self, paper_id: str) -> str:
    """
    Extract entities from the paper.
    
    Identifies and extracts entities like algorithms, models, datasets, etc.
    
    Args:
        paper_id: ID of the paper to process
        
    Returns:
        Paper ID for chaining
    """
    logger.info(f"Extracting entities for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Create state machine and transition to EXTRACTING_ENTITIES
        state_machine = PaperStateMachine(paper)
        paper = state_machine.transition_to(
            PaperStatus.EXTRACTING_ENTITIES,
            "Starting entity extraction"
        )
        
        # Simulate entity extraction
        # In a full implementation, this would use NLP techniques to identify
        # entities in the paper text, classify them, etc.
        time.sleep(3)  # Simulate processing time
        
        # Add some sample entities
        entities = [
            {
                "id": str(uuid.uuid4()),
                "type": "algorithm",
                "name": "Sample Algorithm",
                "confidence": 0.95,
                "context": "... sample algorithm is used to ...",
                "metadata": {"complexity": "O(n log n)"}
            },
            {
                "id": str(uuid.uuid4()),
                "type": "dataset",
                "name": "Sample Dataset",
                "confidence": 0.92,
                "context": "... evaluated on the sample dataset ...",
                "metadata": {"size": "10,000 samples"}
            },
            {
                "id": str(uuid.uuid4()),
                "type": "model",
                "name": "Sample Neural Network",
                "confidence": 0.88,
                "context": "... implemented using a sample neural network ...",
                "metadata": {"architecture": "transformer"}
            }
        ]
        
        # Update paper with extracted entities
        paper.entities = entities
        
        # Update statistics
        if paper.statistics:
            paper.statistics.entity_count = len(entities)
        
        # Add processing event
        paper = add_processing_event(
            paper,
            paper.status,
            f"Extracted {len(entities)} entities successfully",
            {"entity_types": [entity["type"] for entity in entities]}
        )
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error extracting entities for paper {paper_id}: {e}")
        self.retry(exc=e)


@app.task(bind=True, base=PaperProcessingTask)
def extract_relationships(self, paper_id: str) -> str:
    """
    Extract relationships between entities in the paper.
    
    Identifies relationships between previously extracted entities.
    
    Args:
        paper_id: ID of the paper to process
        
    Returns:
        Paper ID for chaining
    """
    logger.info(f"Extracting relationships for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Create state machine and transition to EXTRACTING_RELATIONSHIPS
        state_machine = PaperStateMachine(paper)
        paper = state_machine.transition_to(
            PaperStatus.EXTRACTING_RELATIONSHIPS,
            "Starting relationship extraction"
        )
        
        # Simulate relationship extraction
        # In a full implementation, this would analyze co-occurrences, patterns,
        # and semantic relationships between entities in the paper text
        time.sleep(2)  # Simulate processing time
        
        # Ensure we have entities to work with
        if not paper.entities or len(paper.entities) < 2:
            logger.warning(f"Not enough entities to extract relationships for paper {paper_id}")
            # Create a dummy relationship for demo purposes
            relationships = [{
                "id": str(uuid.uuid4()),
                "type": "uses",
                "source_id": str(uuid.uuid4()),
                "target_id": str(uuid.uuid4()),
                "confidence": 0.8,
                "context": "No actual entities found"
            }]
        else:
            # Create sample relationships between existing entities
            relationships = []
            
            # Get entity IDs
            entity_ids = [entity["id"] for entity in paper.entities]
            
            # Create a relationship between entities
            if len(entity_ids) >= 2:
                relationships.append({
                    "id": str(uuid.uuid4()),
                    "type": "uses",
                    "source_id": entity_ids[0],
                    "target_id": entity_ids[1],
                    "confidence": 0.85,
                    "context": "... algorithm uses the dataset ...",
                    "metadata": {"frequency": "multiple times"}
                })
            
            # Create another relationship if there are enough entities
            if len(entity_ids) >= 3:
                relationships.append({
                    "id": str(uuid.uuid4()),
                    "type": "evaluates",
                    "source_id": entity_ids[2],
                    "target_id": entity_ids[0],
                    "confidence": 0.78,
                    "context": "... model evaluates the algorithm ...",
                    "metadata": {"metric": "accuracy"}
                })
        
        # Update paper with extracted relationships
        paper.relationships = relationships
        
        # Update statistics
        if paper.statistics:
            paper.statistics.relationship_count = len(relationships)
        
        # Add processing event
        paper = add_processing_event(
            paper,
            paper.status,
            f"Extracted {len(relationships)} relationships successfully",
            {"relationship_types": [rel["type"] for rel in relationships]}
        )
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error extracting relationships for paper {paper_id}: {e}")
        self.retry(exc=e)


@app.task(bind=True, base=PaperProcessingTask)
def build_knowledge_graph(self, paper_id: str) -> str:
    """
    Build knowledge graph from extracted entities and relationships.
    
    Integrates the paper's entities and relationships into the knowledge graph.
    
    Args:
        paper_id: ID of the paper to process
        
    Returns:
        Paper ID for chaining
    """
    logger.info(f"Building knowledge graph for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Create state machine and transition to BUILDING_KNOWLEDGE_GRAPH
        state_machine = PaperStateMachine(paper)
        paper = state_machine.transition_to(
            PaperStatus.BUILDING_KNOWLEDGE_GRAPH,
            "Starting knowledge graph integration"
        )
        
        # Simulate knowledge graph integration
        # In a full implementation, this would add the entities and relationships
        # to the knowledge graph database, resolve duplicates, etc.
        time.sleep(2)  # Simulate processing time
        
        # Generate a fake knowledge graph ID
        knowledge_graph_id = f"kg-{uuid.uuid4()}"
        paper.knowledge_graph_id = knowledge_graph_id
        
        # Add processing event
        paper = add_processing_event(
            paper,
            paper.status,
            "Successfully integrated into knowledge graph",
            {"knowledge_graph_id": knowledge_graph_id}
        )
        
        # Transition to ANALYZED state
        paper = state_machine.transition_to(
            PaperStatus.ANALYZED,
            "Paper analysis complete"
        )
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error building knowledge graph for paper {paper_id}: {e}")
        self.retry(exc=e)


@app.task(bind=True, base=PaperProcessingTask)
def check_implementation_readiness(self, paper_id: str) -> str:
    """
    Check if the paper is ready for implementation.
    
    Evaluates the paper to determine if it contains enough information for
    algorithm implementation.
    
    Args:
        paper_id: ID of the paper to process
        
    Returns:
        Paper ID
    """
    logger.info(f"Checking implementation readiness for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Simulate readiness check
        # In a full implementation, this would analyze the paper structure,
        # look for algorithm descriptions, pseudocode, etc.
        time.sleep(1)  # Simulate processing time
        
        # Check if the paper has entities of type 'algorithm'
        has_algorithm = any(
            entity["type"] == "algorithm" for entity in paper.entities
        ) if paper.entities else False
        
        # Determine implementation readiness
        paper.implementation_ready = has_algorithm
        
        # Add processing event
        paper = add_processing_event(
            paper,
            paper.status,
            f"Implementation readiness check: {'Ready' if paper.implementation_ready else 'Not ready'}",
            {"implementation_ready": paper.implementation_ready}
        )
        
        # If ready, transition to IMPLEMENTATION_READY state
        if paper.implementation_ready:
            state_machine = PaperStateMachine(paper)
            paper = state_machine.transition_to(
                PaperStatus.IMPLEMENTATION_READY,
                "Paper ready for implementation"
            )
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error checking implementation readiness for paper {paper_id}: {e}")
        self.retry(exc=e)


@app.task(bind=True, base=PaperProcessingTask)
def request_implementation(self, paper_id: str) -> str:
    """
    Request implementation of the paper's algorithms.
    
    Initiates the implementation process for a paper that is ready for implementation.
    
    Args:
        paper_id: ID of the paper to implement
        
    Returns:
        Paper ID
    """
    logger.info(f"Requesting implementation for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Check if paper is in IMPLEMENTATION_READY state
        if paper.status != PaperStatus.IMPLEMENTATION_READY:
            logger.warning(f"Paper {paper_id} is not ready for implementation")
            return paper_id
        
        # Simulate implementation request
        # In a full implementation, this would call the Research Implementation
        # System API to request implementation of the paper's algorithms
        time.sleep(1)  # Simulate processing time
        
        # Update paper with implementation request details
        paper = add_processing_event(
            paper,
            paper.status,
            "Implementation requested",
            {"request_id": f"impl-{uuid.uuid4()}", "request_time": datetime.utcnow().isoformat()}
        )
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error requesting implementation for paper {paper_id}: {e}")
        self.retry(exc=e)


@app.task(bind=True, base=PaperProcessingTask)
def cancel_processing_task(self, paper_id: str) -> str:
    """
    Cancel ongoing processing for a paper.
    
    This task handles the cancellation of a paper's processing.
    
    Args:
        paper_id: ID of the paper to cancel
        
    Returns:
        Paper ID
    """
    logger.info(f"Cancelling processing for paper {paper_id}")
    
    try:
        # Get paper from database
        paper_model = PaperModel.get_by_id(paper_id)
        if not paper_model:
            raise ValueError(f"Paper with ID {paper_id} not found")
            
        paper = paper_model.to_domain()
        
        # Revoke any active Celery tasks for this paper
        # Note: In a real implementation, this would use Celery's task revocation API
        # For now, we'll just simulate it
        logger.info(f"Would revoke active tasks for paper {paper_id}")
        
        # Transition paper back to UPLOADED state for reprocessing
        state_machine = PaperStateMachine(paper)
        try:
            # First try transition to FAILED as an intermediate step
            paper = state_machine.transition_to(
                PaperStatus.FAILED,
                "Processing cancelled by user"
            )
            
            # Then try to transition back to UPLOADED
            paper = state_machine.transition_to(
                PaperStatus.UPLOADED,
                "Reset to uploaded state after cancellation"
            )
        except StateTransitionException as e:
            logger.error(f"Could not transition paper {paper_id} after cancellation: {e}")
            # If we can't transition all the way back to UPLOADED, at least mark it as FAILED
            try:
                paper = state_machine.transition_to(
                    PaperStatus.FAILED,
                    "Processing cancelled by user"
                )
            except StateTransitionException as e2:
                logger.error(f"Could not transition paper {paper_id} to FAILED state: {e2}")
                # Add a processing event to indicate cancellation
                paper = add_processing_event(
                    paper,
                    paper.status,  # Keep current status
                    "Processing cancellation attempted but could not change state"
                )
        
        # Save updated paper
        paper_model.update_from_domain(paper)
        paper_model.save()
        
        return paper_id
    
    except Exception as e:
        logger.error(f"Error cancelling processing for paper {paper_id}: {e}")
        self.retry(exc=e)