# Paper Processing Pipeline Implementation Guide

## Overview

The Paper Processing Pipeline is the fourth implementation priority for the AI Research Integration Project. This system bridges the gap between paper uploads and knowledge extraction, enabling automatic processing of research documents and seamless integration with the knowledge graph and implementation systems.

## Architecture

The Paper Processing Pipeline follows a modular, asynchronous architecture designed for reliability, scalability, and extensibility.

### Core Components

1. **Asynchronous Processing Architecture**
   - Celery task queue with Redis as message broker
   - Worker configuration with auto-retry and exponential backoff
   - Dead letter queues for failed processing tasks
   - Resource management with task prioritization
   - Logging and monitoring dashboards for system health

2. **Paper Lifecycle Management**
   - State machine to track paper processing status
   - Granular states with detailed transitions:
     ```
     uploaded → queued → processing → extracting_entities → 
     extracting_relationships → building_knowledge_graph → 
     analyzed → implementation_ready
     ```
   - Transaction-based state changes for consistency
   - Processing history tracking with timestamps
   - Reporting system for statistics and performance metrics

3. **Processing Integration Components**
   - Document processors for different formats (PDF, HTML, text, LaTeX, etc.)
   - Entity and relationship extraction from academic papers
   - Knowledge graph integration for extracted entities
   - Citation extraction and reference analysis
   - Metadata classification for paper organization

4. **API and Interface**
   - RESTful API endpoints for paper management
   - WebSocket endpoints for real-time updates
   - Progress tracking with detailed stage information
   - Paper search, filtering, and organization tools

5. **Implementation System Integration**
   - Algorithm extraction for code generation
   - Entity-to-code mapping frameworks
   - Automatic test generation from paper metrics
   - Validation comparing implementations to source papers
   - Traceability between papers and generated code

## Implementation Guidelines

### 1. Asynchronous Processing Architecture

#### Celery Configuration
```python
# celery_app.py
from celery import Celery
from celery.signals import task_failure, task_success
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Celery app
app = Celery(
    'paper_processing',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configure Celery
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Queue settings
    task_queues={
        'default': {'exchange': 'default', 'routing_key': 'default'},
        'paper_processing': {'exchange': 'paper_processing', 'routing_key': 'paper_processing'},
        'entity_extraction': {'exchange': 'entity_extraction', 'routing_key': 'entity_extraction'},
        'relationship_extraction': {'exchange': 'relationship_extraction', 'routing_key': 'relationship_extraction'},
        'knowledge_graph': {'exchange': 'knowledge_graph', 'routing_key': 'knowledge_graph'},
    },
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Result settings
    result_expires=86400,  # 1 day
    
    # Prefetch settings for better throughput
    worker_prefetch_multiplier=4,
    
    # Rate limiting to prevent overwhelming external services
    task_default_rate_limit='10/m',  # 10 tasks per minute
)

# Task success handler
@task_success.connect
def task_success_handler(sender=None, **kwargs):
    logger.info(f"Task {sender.name}[{sender.request.id}] succeeded")

# Task failure handler
@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    logger.error(f"Task {sender.name}[{task_id}] failed: {exception}")
```

#### Dead Letter Queue Implementation
```python
# dead_letter.py
from functools import wraps
from celery.exceptions import MaxRetriesExceededError
import logging

logger = logging.getLogger(__name__)

def dead_letter_queue(task_name):
    """
    Decorator to send failed tasks to a dead-letter queue
    after max retries are exhausted.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MaxRetriesExceededError as exc:
                logger.error(f"Max retries exceeded for task {task_name}: {exc}")
                # Send to dead letter queue
                from celery_app import app
                dead_letter_task = app.send_task(
                    'paper_processing.tasks.dead_letter_task',
                    args=[task_name, args, kwargs],
                    kwargs={'error': str(exc)},
                    queue='dead_letter'
                )
                logger.info(f"Task sent to dead letter queue: {dead_letter_task.id}")
                raise
            except Exception as exc:
                logger.error(f"Unexpected error in task {task_name}: {exc}")
                raise
        return wrapper
    return decorator
```

### 2. Paper Lifecycle Management

#### State Machine Implementation
```python
# state_machine.py
from enum import Enum
from typing import Optional, List, Dict, Any
import datetime
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class PaperStatus(str, Enum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    EXTRACTING_ENTITIES = "extracting_entities"
    EXTRACTING_RELATIONSHIPS = "extracting_relationships"
    BUILDING_KNOWLEDGE_GRAPH = "building_knowledge_graph"
    ANALYZED = "analyzed"
    IMPLEMENTATION_READY = "implementation_ready"
    ERROR = "error"

@dataclass
class StateTransition:
    from_state: PaperStatus
    to_state: PaperStatus
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PaperStateHistory:
    paper_id: str
    transitions: List[StateTransition] = field(default_factory=list)
    
    def add_transition(self, from_state: PaperStatus, to_state: PaperStatus, 
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        if metadata is None:
            metadata = {}
        transition = StateTransition(from_state, to_state, datetime.datetime.now(), metadata)
        self.transitions.append(transition)
        logger.info(f"Paper {self.paper_id} transitioned from {from_state} to {to_state}")
    
    def current_state(self) -> Optional[PaperStatus]:
        if not self.transitions:
            return None
        return self.transitions[-1].to_state
    
    def get_transition_time(self, from_state: PaperStatus, to_state: PaperStatus) -> Optional[float]:
        """Calculate time (in seconds) between specific state transitions"""
        from_timestamp = None
        to_timestamp = None
        
        for transition in self.transitions:
            if transition.from_state == from_state and from_timestamp is None:
                from_timestamp = transition.timestamp
            if transition.to_state == to_state:
                to_timestamp = transition.timestamp
                
        if from_timestamp and to_timestamp:
            return (to_timestamp - from_timestamp).total_seconds()
        return None
    
    def total_processing_time(self) -> Optional[float]:
        """Calculate total processing time in seconds"""
        if len(self.transitions) < 2:
            return None
            
        start = self.transitions[0].timestamp
        end = self.transitions[-1].timestamp
        return (end - start).total_seconds()

class PaperStateMachine:
    # Define valid state transitions
    VALID_TRANSITIONS = {
        PaperStatus.UPLOADED: [PaperStatus.QUEUED, PaperStatus.ERROR],
        PaperStatus.QUEUED: [PaperStatus.PROCESSING, PaperStatus.ERROR],
        PaperStatus.PROCESSING: [PaperStatus.EXTRACTING_ENTITIES, PaperStatus.ERROR],
        PaperStatus.EXTRACTING_ENTITIES: [PaperStatus.EXTRACTING_RELATIONSHIPS, PaperStatus.ERROR],
        PaperStatus.EXTRACTING_RELATIONSHIPS: [PaperStatus.BUILDING_KNOWLEDGE_GRAPH, PaperStatus.ERROR],
        PaperStatus.BUILDING_KNOWLEDGE_GRAPH: [PaperStatus.ANALYZED, PaperStatus.ERROR],
        PaperStatus.ANALYZED: [PaperStatus.IMPLEMENTATION_READY, PaperStatus.ERROR],
        PaperStatus.IMPLEMENTATION_READY: [PaperStatus.ERROR],
        PaperStatus.ERROR: [PaperStatus.QUEUED],  # Allow retrying from error state
    }
    
    def __init__(self, state_history_repository):
        self.state_history_repository = state_history_repository
    
    def transition(self, paper_id: str, to_state: PaperStatus, 
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Transition a paper to a new state.
        Returns True if transition is successful, False otherwise.
        """
        history = self.state_history_repository.get(paper_id)
        if not history:
            # Initialize new paper with UPLOADED state
            history = PaperStateHistory(paper_id)
            if to_state != PaperStatus.UPLOADED:
                logger.error(f"New paper {paper_id} must start in UPLOADED state, not {to_state}")
                return False
            
            history.add_transition(PaperStatus.UPLOADED, to_state, metadata)
            self.state_history_repository.save(history)
            return True
        
        current_state = history.current_state()
        if not current_state:
            logger.error(f"Paper {paper_id} has no current state")
            return False
            
        # Check if transition is valid
        if to_state not in self.VALID_TRANSITIONS.get(current_state, []):
            logger.error(f"Invalid transition for paper {paper_id}: {current_state} -> {to_state}")
            return False
            
        # Add transition
        history.add_transition(current_state, to_state, metadata)
        self.state_history_repository.save(history)
        
        # Publish state change event
        self._publish_state_change(paper_id, current_state, to_state, metadata)
        
        return True
    
    def _publish_state_change(self, paper_id: str, from_state: PaperStatus, 
                             to_state: PaperStatus, metadata: Dict[str, Any]) -> None:
        """Publish state change event to message broker for WebSocket notifications"""
        # Implementation will depend on message broker choice
        pass
```

### 3. Processing Integration Components

#### Document Processing Integration
```python
# document_processor.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor(ABC):
    """Base class for document processors"""
    
    @abstractmethod
    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file"""
        pass
    
    @abstractmethod
    def process(self, file_path: str) -> Dict[str, Any]:
        """Process the document and return structured content"""
        pass

class PDFProcessor(DocumentProcessor):
    """Processor for PDF documents"""
    
    def can_process(self, file_path: str) -> bool:
        return file_path.lower().endswith('.pdf')
    
    def process(self, file_path: str) -> Dict[str, Any]:
        # Implementation using PyPDF2, pdfminer, or similar
        pass

class HTMLProcessor(DocumentProcessor):
    """Processor for HTML documents"""
    
    def can_process(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.html', '.htm'))
    
    def process(self, file_path: str) -> Dict[str, Any]:
        # Implementation using BeautifulSoup or similar
        pass

class TextProcessor(DocumentProcessor):
    """Processor for plain text documents"""
    
    def can_process(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.txt', '.md'))
    
    def process(self, file_path: str) -> Dict[str, Any]:
        # Implementation for plain text processing
        pass

class LaTeXProcessor(DocumentProcessor):
    """Processor for LaTeX documents"""
    
    def can_process(self, file_path: str) -> bool:
        return file_path.lower().endswith(('.tex', '.latex'))
    
    def process(self, file_path: str) -> Dict[str, Any]:
        # Implementation for LaTeX processing
        pass

class DocumentProcessorFactory:
    """Factory for creating document processors"""
    
    def __init__(self):
        self.processors = [
            PDFProcessor(),
            HTMLProcessor(),
            TextProcessor(),
            LaTeXProcessor(),
        ]
    
    def get_processor(self, file_path: str) -> Optional[DocumentProcessor]:
        """Get appropriate processor for the given file"""
        for processor in self.processors:
            if processor.can_process(file_path):
                return processor
        return None
```

#### Processing Task Definition
```python
# processing_tasks.py
from celery import shared_task
from typing import Dict, Any, List
import logging
from functools import wraps
import time

from paper_processing.document_processor import DocumentProcessorFactory
from paper_processing.state_machine import PaperStateMachine, PaperStatus
from paper_processing.dead_letter import dead_letter_queue

logger = logging.getLogger(__name__)

def transition_state(to_state: PaperStatus):
    """Decorator to update paper state before and after task execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(paper_id: str, *args, **kwargs):
            # Get state machine
            from paper_processing.repositories import state_history_repository
            state_machine = PaperStateMachine(state_history_repository)
            
            # Update state before processing
            state_machine.transition(paper_id, to_state, {"started_at": time.time()})
            
            try:
                # Execute task
                result = func(paper_id, *args, **kwargs)
                
                # Task completed successfully
                return result
            except Exception as e:
                # Task failed, transition to ERROR state
                state_machine.transition(paper_id, PaperStatus.ERROR, {
                    "error": str(e),
                    "task": func.__name__
                })
                raise
        return wrapper
    return decorator

@shared_task(bind=True, name="paper_processing.tasks.process_paper")
@dead_letter_queue("process_paper")
@transition_state(PaperStatus.PROCESSING)
def process_paper(self, paper_id: str, file_path: str) -> Dict[str, Any]:
    """Process paper document and extract content"""
    logger.info(f"Processing paper {paper_id} from {file_path}")
    
    # Get appropriate processor
    factory = DocumentProcessorFactory()
    processor = factory.get_processor(file_path)
    
    if not processor:
        raise ValueError(f"No processor available for file: {file_path}")
    
    # Process document
    document_data = processor.process(file_path)
    
    # Queue entity extraction
    extract_entities.delay(paper_id, document_data)
    
    return {"paper_id": paper_id, "processed": True}

@shared_task(bind=True, name="paper_processing.tasks.extract_entities")
@dead_letter_queue("extract_entities")
@transition_state(PaperStatus.EXTRACTING_ENTITIES)
def extract_entities(self, paper_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract entities from processed document"""
    logger.info(f"Extracting entities for paper {paper_id}")
    
    # Use entity recognition system
    from knowledge_extraction.entity_recognition import EntityRecognizerFactory
    
    # Create recognizers
    factory = EntityRecognizerFactory()
    ai_recognizer = factory.create_ai_entity_recognizer()
    scientific_recognizer = factory.create_scientific_entity_recognizer()
    
    # Extract entities
    ai_entities = ai_recognizer.extract_entities(document_data["content"])
    scientific_entities = scientific_recognizer.extract_entities(document_data["content"])
    
    # Combine entities
    all_entities = {**ai_entities, **scientific_entities}
    
    # Queue relationship extraction
    extract_relationships.delay(paper_id, document_data, all_entities)
    
    return {"paper_id": paper_id, "entity_count": len(all_entities)}

@shared_task(bind=True, name="paper_processing.tasks.extract_relationships")
@dead_letter_queue("extract_relationships")
@transition_state(PaperStatus.EXTRACTING_RELATIONSHIPS)
def extract_relationships(self, paper_id: str, document_data: Dict[str, Any], 
                         entities: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relationships between entities"""
    logger.info(f"Extracting relationships for paper {paper_id}")
    
    # Use relationship extraction system
    from knowledge_extraction.relationship_extraction import RelationshipExtractorFactory
    
    # Create extractors
    factory = RelationshipExtractorFactory()
    pattern_extractor = factory.create_pattern_relationship_extractor()
    ai_extractor = factory.create_ai_relationship_extractor()
    
    # Extract relationships
    pattern_relationships = pattern_extractor.extract_relationships(document_data["content"], entities)
    ai_relationships = ai_extractor.extract_relationships(document_data["content"], entities)
    
    # Combine relationships
    all_relationships = {**pattern_relationships, **ai_relationships}
    
    # Queue knowledge graph building
    build_knowledge_graph.delay(paper_id, entities, all_relationships)
    
    return {"paper_id": paper_id, "relationship_count": len(all_relationships)}

@shared_task(bind=True, name="paper_processing.tasks.build_knowledge_graph")
@dead_letter_queue("build_knowledge_graph")
@transition_state(PaperStatus.BUILDING_KNOWLEDGE_GRAPH)
def build_knowledge_graph(self, paper_id: str, entities: Dict[str, Any], 
                         relationships: Dict[str, Any]) -> Dict[str, Any]:
    """Build knowledge graph from extracted entities and relationships"""
    logger.info(f"Building knowledge graph for paper {paper_id}")
    
    # Use knowledge graph system
    from knowledge_graph_system.core import KnowledgeGraphManager
    
    # Connect to graph database
    kg_manager = KnowledgeGraphManager()
    
    # Add entities to graph
    entity_ids = {}
    for entity_id, entity in entities.items():
        graph_id = kg_manager.add_entity({
            "type": entity["type"],
            "name": entity["name"],
            "properties": entity["properties"]
        })
        entity_ids[entity_id] = graph_id
    
    # Add relationships to graph
    for rel_id, rel in relationships.items():
        source_id = entity_ids.get(rel["source"])
        target_id = entity_ids.get(rel["target"])
        
        if source_id and target_id:
            kg_manager.add_relationship(
                source_id, target_id, rel["type"], rel["properties"]
            )
    
    # Transition to analyzed state
    analyze_paper.delay(paper_id, entities, relationships)
    
    return {"paper_id": paper_id, "entity_count": len(entities), 
            "relationship_count": len(relationships)}

@shared_task(bind=True, name="paper_processing.tasks.analyze_paper")
@dead_letter_queue("analyze_paper")
@transition_state(PaperStatus.ANALYZED)
def analyze_paper(self, paper_id: str, entities: Dict[str, Any], 
                relationships: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze paper for implementation potential"""
    logger.info(f"Analyzing paper {paper_id} for implementation")
    
    # Check if paper has algorithms or models
    has_algorithm = any(e["type"] == "ALGORITHM" for e in entities.values())
    has_model = any(e["type"] == "MODEL" for e in entities.values())
    
    if has_algorithm or has_model:
        # Queue for implementation
        prepare_for_implementation.delay(paper_id, entities, relationships)
    
    return {"paper_id": paper_id, "implementation_candidate": has_algorithm or has_model}

@shared_task(bind=True, name="paper_processing.tasks.prepare_for_implementation")
@dead_letter_queue("prepare_for_implementation")
@transition_state(PaperStatus.IMPLEMENTATION_READY)
def prepare_for_implementation(self, paper_id: str, entities: Dict[str, Any], 
                             relationships: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare paper for implementation code generation"""
    logger.info(f"Preparing paper {paper_id} for implementation")
    
    # Use implementation system
    from research_implementation.core import ImplementationManager
    
    # Create implementation context
    impl_manager = ImplementationManager()
    
    # Extract key information
    algorithms = [e for e in entities.values() if e["type"] == "ALGORITHM"]
    models = [e for e in entities.values() if e["type"] == "MODEL"]
    datasets = [e for e in entities.values() if e["type"] == "DATASET"]
    
    # Create implementation context
    context = {
        "paper_id": paper_id,
        "algorithms": algorithms,
        "models": models,
        "datasets": datasets,
        "relationships": relationships
    }
    
    # Register with implementation system
    impl_manager.register_implementation_candidate(paper_id, context)
    
    return {"paper_id": paper_id, "implementation_ready": True}
```

### 4. API and Interface

#### API Endpoints
```python
# api/paper_endpoints.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
from typing import List, Optional, Dict, Any
import uuid
import os
from datetime import datetime
import shutil

from paper_processing.models import (
    PaperSubmission, 
    PaperResponse, 
    PaperStatusResponse,
    PaperListResponse,
    BatchProcessRequest,
    ProcessingStatistics
)
from paper_processing.state_machine import PaperStateMachine, PaperStatus
from paper_processing.repositories import paper_repository, state_history_repository
from paper_processing.tasks.processing_tasks import process_paper

router = APIRouter(prefix="/papers", tags=["papers"])

@router.post("/", response_model=PaperResponse)
async def upload_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: Optional[PaperSubmission] = None
):
    """
    Upload a new paper for processing
    """
    # Generate unique ID for paper
    paper_id = str(uuid.uuid4())
    
    # Save file
    file_path = f"/tmp/papers/{paper_id}/{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create paper record
    paper = {
        "id": paper_id,
        "filename": file.filename,
        "file_path": file_path,
        "upload_time": datetime.now().isoformat(),
        "metadata": metadata.dict() if metadata else {},
    }
    
    # Save paper to repository
    paper_repository.save(paper)
    
    # Initialize paper state
    state_machine = PaperStateMachine(state_history_repository)
    state_machine.transition(paper_id, PaperStatus.UPLOADED, {"filename": file.filename})
    
    # Queue paper for processing
    process_paper.delay(paper_id, file_path)
    
    return {
        "paper_id": paper_id,
        "status": "uploaded",
        "filename": file.filename,
        "message": "Paper uploaded successfully and queued for processing"
    }

@router.post("/{paper_id}/process", response_model=PaperResponse)
async def process_existing_paper(paper_id: str):
    """
    Manually trigger processing for an existing paper
    """
    # Check if paper exists
    paper = paper_repository.get(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get current state
    state_machine = PaperStateMachine(state_history_repository)
    history = state_history_repository.get(paper_id)
    
    if not history:
        raise HTTPException(status_code=400, detail="Paper has no state history")
    
    current_state = history.current_state()
    
    # Only allow processing if paper is in UPLOADED or ERROR state
    if current_state not in [PaperStatus.UPLOADED, PaperStatus.ERROR]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot process paper in {current_state} state"
        )
    
    # Queue paper for processing
    process_paper.delay(paper_id, paper["file_path"])
    
    # Transition to QUEUED state
    state_machine.transition(paper_id, PaperStatus.QUEUED, {
        "manual_trigger": True,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "paper_id": paper_id,
        "status": "queued",
        "filename": paper["filename"],
        "message": "Paper queued for processing"
    }

@router.post("/batch/process", response_model=List[PaperResponse])
async def process_batch(request: BatchProcessRequest):
    """
    Process multiple papers in batch
    """
    responses = []
    
    for paper_id in request.paper_ids:
        try:
            # Process each paper
            response = await process_existing_paper(paper_id)
            responses.append(response)
        except HTTPException as e:
            # Add error response
            responses.append({
                "paper_id": paper_id,
                "status": "error",
                "message": e.detail
            })
    
    return responses

@router.get("/{paper_id}/status", response_model=PaperStatusResponse)
async def get_paper_status(paper_id: str):
    """
    Get current status of a paper
    """
    # Check if paper exists
    paper = paper_repository.get(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Get state history
    history = state_history_repository.get(paper_id)
    if not history:
        raise HTTPException(status_code=400, detail="Paper has no state history")
    
    current_state = history.current_state()
    
    # Get processing statistics
    total_time = history.total_processing_time()
    
    return {
        "paper_id": paper_id,
        "status": current_state,
        "history": [
            {
                "from_state": t.from_state,
                "to_state": t.to_state,
                "timestamp": t.timestamp.isoformat(),
                "metadata": t.metadata
            }
            for t in history.transitions
        ],
        "statistics": {
            "total_processing_time": total_time,
            "current_state": current_state,
            "transitions_count": len(history.transitions)
        }
    }

@router.get("/", response_model=PaperListResponse)
async def list_papers(
    status: Optional[PaperStatus] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    List all papers with optional filtering by status
    """
    # Get papers from repository
    papers = paper_repository.list(limit, offset)
    
    # Filter by status if provided
    if status:
        filtered_papers = []
        state_machine = PaperStateMachine(state_history_repository)
        
        for paper in papers:
            history = state_history_repository.get(paper["id"])
            if history and history.current_state() == status:
                filtered_papers.append(paper)
        
        papers = filtered_papers
    
    # Get total count
    total_count = paper_repository.count(status)
    
    return {
        "papers": papers,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }

@router.get("/statistics", response_model=ProcessingStatistics)
async def get_processing_statistics():
    """
    Get paper processing statistics
    """
    # Count papers by status
    status_counts = {}
    for status in PaperStatus:
        status_counts[status] = paper_repository.count(status)
    
    # Calculate average processing times
    # This would involve querying the state history repository
    
    return {
        "total_papers": sum(status_counts.values()),
        "status_counts": status_counts,
        "average_processing_time": 0  # To be implemented
    }
```

#### WebSocket Implementation
```python
# websockets/paper_status.py
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, List, Any, Optional
import logging
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class PaperStatusNotifier:
    """
    Manage WebSocket connections for paper status updates
    """
    def __init__(self):
        # Map of paper_id -> list of connected WebSockets
        self.connections: Dict[str, List[WebSocket]] = {}
        # Active connections for all papers
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, paper_id: Optional[str] = None):
        """Connect a client to receive updates"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # If subscribing to specific paper
        if paper_id:
            if paper_id not in self.connections:
                self.connections[paper_id] = []
            self.connections[paper_id].append(websocket)
            logger.info(f"Client subscribed to paper {paper_id}")
    
    def disconnect(self, websocket: WebSocket, paper_id: Optional[str] = None):
        """Disconnect a client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from paper-specific connections
        if paper_id and paper_id in self.connections:
            if websocket in self.connections[paper_id]:
                self.connections[paper_id].remove(websocket)
            
            # Clean up empty lists
            if not self.connections[paper_id]:
                del self.connections[paper_id]
    
    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all connected clients"""
        if not self.active_connections:
            return
            
        # Convert message to JSON
        message_json = json.dumps(message)
        
        # Send to all active connections
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending broadcast: {e}")
    
    async def send_paper_update(self, paper_id: str, data: Dict[str, Any]):
        """Send update about a specific paper"""
        if paper_id not in self.connections:
            return
            
        # Add timestamp to message
        data["timestamp"] = datetime.now().isoformat()
        data["paper_id"] = paper_id
        
        # Convert message to JSON
        message_json = json.dumps(data)
        
        # Send to subscribed connections
        for connection in self.connections[paper_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending paper update for {paper_id}: {e}")

# Create singleton instance
notifier = PaperStatusNotifier()

async def get_notifier():
    """Dependency for accessing the notifier"""
    return notifier

# WebSocket routes
def setup_websocket_routes(app):
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for general updates"""
        await notifier.connect(websocket)
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            notifier.disconnect(websocket)
    
    @app.websocket("/ws/paper/{paper_id}")
    async def paper_status_endpoint(
        websocket: WebSocket, 
        paper_id: str
    ):
        """WebSocket endpoint for specific paper updates"""
        # Validate paper_id (could use a dependency)
        from paper_processing.repositories import paper_repository
        paper = paper_repository.get(paper_id)
        if not paper:
            await websocket.close(code=4004, reason="Paper not found")
            return
            
        await notifier.connect(websocket, paper_id)
        
        # Send initial status
        from paper_processing.repositories import state_history_repository
        history = state_history_repository.get(paper_id)
        if history:
            current_state = history.current_state()
            await websocket.send_json({
                "type": "paper_status",
                "paper_id": paper_id,
                "status": current_state,
                "timestamp": datetime.now().isoformat()
            })
        
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            notifier.disconnect(websocket, paper_id)
```

### 5. Implementation System Integration

#### Algorithm Extraction
```python
# algorithm_extraction.py
from typing import Dict, Any, List, Optional
import logging
import re

logger = logging.getLogger(__name__)

class AlgorithmExtractor:
    """Extract algorithm details from research papers"""
    
    def __init__(self):
        # Regular expressions for algorithm detection
        self.algorithm_patterns = [
            r"(?:Algorithm|Procedure|Function)\s+(\d+|[A-Z]+)(?:\s*:)?\s*([\w\s]+)",
            r"(?:Algorithm|Procedure|Function)\s+([\w\s]+):",
            r"def\s+(\w+)\s*\(",  # Python-style function definition
        ]
    
    def extract_algorithms(self, content: str) -> List[Dict[str, Any]]:
        """Extract algorithms from paper content"""
        algorithms = []
        
        # Search for algorithm patterns
        for pattern in self.algorithm_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                # Extract algorithm name and surrounding context
                algorithm_name = match.group(1) if len(match.groups()) > 0 else "Unknown"
                
                # Get context (lines around the algorithm)
                start_pos = max(0, match.start() - 500)
                end_pos = min(len(content), match.end() + 2000)
                algorithm_context = content[start_pos:end_pos]
                
                # Extract pseudocode if available (typically indented blocks after algorithm definition)
                pseudocode = self._extract_pseudocode(content, match.end())
                
                # Extract inputs and outputs
                inputs = self._extract_inputs(algorithm_context)
                outputs = self._extract_outputs(algorithm_context)
                
                # Extract complexity information
                time_complexity = self._extract_time_complexity(algorithm_context)
                space_complexity = self._extract_space_complexity(algorithm_context)
                
                algorithms.append({
                    "name": algorithm_name,
                    "type": "ALGORITHM",
                    "pseudocode": pseudocode,
                    "inputs": inputs,
                    "outputs": outputs,
                    "time_complexity": time_complexity,
                    "space_complexity": space_complexity,
                    "context": algorithm_context,
                    "position": match.start()
                })
        
        return algorithms
    
    def _extract_pseudocode(self, content: str, start_pos: int) -> Optional[str]:
        """Extract pseudocode from the content starting at start_pos"""
        # Find the end of the current line
        line_end = content.find('\n', start_pos)
        if line_end == -1:
            return None
            
        # Look for indented block in subsequent lines
        pseudocode_lines = []
        position = line_end + 1
        
        # Maximum lines to check
        max_lines = 50
        lines_checked = 0
        
        while position < len(content) and lines_checked < max_lines:
            line_end = content.find('\n', position)
            if line_end == -1:
                line = content[position:]
                position = len(content)
            else:
                line = content[position:line_end]
                position = line_end + 1
            
            lines_checked += 1
            
            # Skip empty lines
            if not line.strip():
                continue
                
            # Check if line is indented (part of pseudocode)
            if line.startswith('  ') or line.startswith('\t'):
                pseudocode_lines.append(line)
            # If we've seen pseudocode and hit a non-indented line, we're done
            elif pseudocode_lines:
                break
        
        return '\n'.join(pseudocode_lines) if pseudocode_lines else None
    
    def _extract_inputs(self, context: str) -> List[str]:
        """Extract input parameters from algorithm context"""
        # Look for input patterns
        input_patterns = [
            r"Input\s*:?\s*(.*?)(?:Output|Return|$)",
            r"Parameters\s*:?\s*(.*?)(?:Returns|$)",
            r"Args\s*:?\s*(.*?)(?:Returns|$)",
        ]
        
        for pattern in input_patterns:
            match = re.search(pattern, context, re.DOTALL | re.IGNORECASE)
            if match:
                # Parse inputs
                inputs_text = match.group(1).strip()
                
                # Split by commas and/or line breaks
                inputs = re.split(r',|\n', inputs_text)
                
                # Clean up each input
                return [input.strip() for input in inputs if input.strip()]
        
        return []
    
    def _extract_outputs(self, context: str) -> List[str]:
        """Extract output parameters from algorithm context"""
        # Look for output patterns
        output_patterns = [
            r"Output\s*:?\s*(.*?)(?:$)",
            r"Returns?\s*:?\s*(.*?)(?:$)",
        ]
        
        for pattern in output_patterns:
            match = re.search(pattern, context, re.DOTALL | re.IGNORECASE)
            if match:
                # Parse outputs
                outputs_text = match.group(1).strip()
                
                # Split by commas and/or line breaks
                outputs = re.split(r',|\n', outputs_text)
                
                # Clean up each output
                return [output.strip() for output in outputs if output.strip()]
        
        return []
    
    def _extract_time_complexity(self, context: str) -> Optional[str]:
        """Extract time complexity information"""
        # Look for complexity patterns
        complexity_patterns = [
            r"[Tt]ime\s+[Cc]omplexity\s*:?\s*[OΟ]\(([^)]+)\)",
            r"[Rr]unning\s+[Tt]ime\s*:?\s*[OΟ]\(([^)]+)\)",
            r"[Cc]omplexity\s*:?\s*[OΟ]\(([^)]+)\)",
        ]
        
        for pattern in complexity_patterns:
            match = re.search(pattern, context)
            if match:
                return f"O({match.group(1)})"
        
        return None
    
    def _extract_space_complexity(self, context: str) -> Optional[str]:
        """Extract space complexity information"""
        # Look for space complexity patterns
        complexity_patterns = [
            r"[Ss]pace\s+[Cc]omplexity\s*:?\s*[OΟ]\(([^)]+)\)",
            r"[Mm]emory\s+[Uu]sage\s*:?\s*[OΟ]\(([^)]+)\)",
        ]
        
        for pattern in complexity_patterns:
            match = re.search(pattern, context)
            if match:
                return f"O({match.group(1)})"
        
        return None
```

#### Algorithm-to-Code Mapping
```python
# algorithm_to_code.py
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AlgorithmImplementationGenerator:
    """Generate code implementations from algorithm descriptions"""
    
    def __init__(self):
        self.language_templates = {
            "python": {
                "function": "def {name}({params}):\n    \"\"\"\n    {docstring}\n    \"\"\"\n{body}",
                "class": "class {name}:\n    \"\"\"\n    {docstring}\n    \"\"\"\n    \n    def __init__(self, {init_params}):\n{init_body}\n{methods}"
            },
            "javascript": {
                "function": "/**\n * {docstring}\n */\nfunction {name}({params}) {\n{body}\n}",
                "class": "/**\n * {docstring}\n */\nclass {name} {\n    constructor({init_params}) {\n{init_body}    }\n\n{methods}\n}"
            },
            "java": {
                "function": "/**\n * {docstring}\n */\npublic {return_type} {name}({params}) {\n{body}\n}",
                "class": "/**\n * {docstring}\n */\npublic class {name} {\n    /**\n     * Constructor\n     */\n    public {name}({init_params}) {\n{init_body}    }\n\n{methods}\n}"
            }
        }
    
    def generate_implementation(self, algorithm: Dict[str, Any], language: str = "python") -> Dict[str, Any]:
        """Generate code implementation from algorithm description"""
        if language not in self.language_templates:
            raise ValueError(f"Unsupported language: {language}")
        
        # Get language templates
        templates = self.language_templates[language]
        
        # Generate implementation based on algorithm type
        if self._is_class_algorithm(algorithm):
            code = self._generate_class_implementation(algorithm, templates, language)
        else:
            code = self._generate_function_implementation(algorithm, templates, language)
        
        return {
            "algorithm_id": algorithm.get("id", "unknown"),
            "name": algorithm.get("name", "Unknown"),
            "language": language,
            "code": code,
            "dependencies": self._extract_dependencies(algorithm, language)
        }
    
    def _is_class_algorithm(self, algorithm: Dict[str, Any]) -> bool:
        """Determine if algorithm should be implemented as a class"""
        # Check algorithm name and structure
        name = algorithm.get("name", "").strip()
        
        # Class-like names typically start with capital letter
        if name and name[0].isupper():
            return True
            
        # Check for class-like keywords in context
        context = algorithm.get("context", "")
        class_indicators = ["class", "struct", "object", "data structure"]
        
        for indicator in class_indicators:
            if indicator in context.lower():
                return True
                
        return False
    
    def _generate_function_implementation(self, algorithm: Dict[str, Any], templates: Dict[str, str], language: str) -> str:
        """Generate function implementation"""
        # Parse inputs for parameters
        params = self._format_parameters(algorithm.get("inputs", []), language)
        
        # Create docstring
        docstring = self._generate_docstring(algorithm, language)
        
        # Generate function body from pseudocode
        body = self._generate_function_body(algorithm, language)
        
        # Fill template
        if language == "java":
            return_type = self._infer_return_type(algorithm, language)
            return templates["function"].format(
                name=algorithm.get("name", "algorithm"),
                params=params,
                docstring=docstring,
                body=body,
                return_type=return_type
            )
        else:
            return templates["function"].format(
                name=algorithm.get("name", "algorithm"),
                params=params,
                docstring=docstring,
                body=body
            )
    
    def _generate_class_implementation(self, algorithm: Dict[str, Any], templates: Dict[str, str], language: str) -> str:
        """Generate class implementation"""
        # Extract likely constructor parameters
        init_params = self._format_parameters(algorithm.get("inputs", []), language)
        
        # Create docstring
        docstring = self._generate_docstring(algorithm, language)
        
        # Generate constructor body
        init_body = self._generate_constructor_body(algorithm, language)
        
        # Generate methods
        methods = self._generate_class_methods(algorithm, language)
        
        return templates["class"].format(
            name=algorithm.get("name", "Algorithm"),
            init_params=init_params,
            docstring=docstring,
            init_body=init_body,
            methods=methods
        )
    
    def _format_parameters(self, inputs: List[str], language: str) -> str:
        """Format algorithm inputs as language-specific parameters"""
        if not inputs:
            return ""
            
        params = []
        for input in inputs:
            # Clean up the input to extract parameter name
            param_name = input.strip().split(":")[0].split(" ")[0].lower()
            
            # Ensure valid identifier
            param_name = "".join(c if c.isalnum() else "_" for c in param_name)
            if param_name and not param_name[0].isalpha() and param_name[0] != "_":
                param_name = "arg_" + param_name
                
            if not param_name:
                continue
                
            # Add type annotations for statically typed languages
            if language == "java":
                # Try to infer type
                java_type = "Object"  # Default type
                if "array" in input.lower() or "list" in input.lower():
                    java_type = "List<Object>"
                elif "string" in input.lower():
                    java_type = "String"
                elif "int" in input.lower() or "integer" in input.lower():
                    java_type = "int"
                elif "float" in input.lower() or "double" in input.lower():
                    java_type = "double"
                elif "boolean" in input.lower():
                    java_type = "boolean"
                    
                params.append(f"{java_type} {param_name}")
            else:
                params.append(param_name)
        
        return ", ".join(params)
    
    def _generate_docstring(self, algorithm: Dict[str, Any], language: str) -> str:
        """Generate language-appropriate docstring"""
        name = algorithm.get("name", "algorithm")
        
        # Format inputs for docstring
        inputs_doc = ""
        for input in algorithm.get("inputs", []):
            if language == "python":
                inputs_doc += f"    Args:\n        {input}\n"
            elif language == "javascript":
                inputs_doc += f" * @param {input}\n"
            elif language == "java":
                inputs_doc += f" * @param {input}\n"
        
        # Format outputs for docstring
        outputs_doc = ""
        for output in algorithm.get("outputs", []):
            if language == "python":
                outputs_doc += f"    Returns:\n        {output}\n"
            elif language == "javascript":
                outputs_doc += f" * @returns {output}\n"
            elif language == "java":
                outputs_doc += f" * @return {output}\n"
        
        # Add time and space complexity if available
        complexity_doc = ""
        time_complexity = algorithm.get("time_complexity")
        space_complexity = algorithm.get("space_complexity")
        
        if time_complexity or space_complexity:
            if language == "python":
                complexity_doc += "    Complexity:\n"
                if time_complexity:
                    complexity_doc += f"        Time: {time_complexity}\n"
                if space_complexity:
                    complexity_doc += f"        Space: {space_complexity}\n"
            else:
                complexity_doc += " * Complexity:\n"
                if time_complexity:
                    complexity_doc += f" * - Time: {time_complexity}\n"
                if space_complexity:
                    complexity_doc += f" * - Space: {space_complexity}\n"
        
        # Combine all parts
        docstring = f"{name} algorithm implementation\n\n"
        if inputs_doc:
            docstring += inputs_doc
        if outputs_doc:
            docstring += outputs_doc
        if complexity_doc:
            docstring += complexity_doc
            
        return docstring
    
    def _generate_function_body(self, algorithm: Dict[str, Any], language: str) -> str:
        """Generate function body from pseudocode"""
        pseudocode = algorithm.get("pseudocode", "")
        
        if not pseudocode:
            # Generate placeholder implementation with comment
            if language == "python":
                return "    # TODO: Implement the algorithm\n    pass"
            elif language == "javascript":
                return "    // TODO: Implement the algorithm\n    throw new Error('Not implemented');"
            elif language == "java":
                return "    // TODO: Implement the algorithm\n    throw new UnsupportedOperationException(\"Not implemented\");"
        
        # Translate pseudocode to language-specific implementation
        # This would involve a more sophisticated algorithm translation system
        # For now, we'll just add comments with the pseudocode
        
        body_lines = []
        indent = "    " if language in ["python", "java"] else "    "
        
        if language == "python":
            body_lines.append(f"{indent}# Pseudocode:")
            for line in pseudocode.split("\n"):
                body_lines.append(f"{indent}# {line}")
            body_lines.append("")
            body_lines.append(f"{indent}# TODO: Implement based on pseudocode")
            body_lines.append(f"{indent}pass")
        elif language == "javascript":
            body_lines.append(f"{indent}// Pseudocode:")
            for line in pseudocode.split("\n"):
                body_lines.append(f"{indent}// {line}")
            body_lines.append("");
            body_lines.append(f"{indent}// TODO: Implement based on pseudocode")
            body_lines.append(f"{indent}throw new Error('Not implemented');")
        elif language == "java":
            body_lines.append(f"{indent}// Pseudocode:")
            for line in pseudocode.split("\n"):
                body_lines.append(f"{indent}// {line}")
            body_lines.append("");
            body_lines.append(f"{indent}// TODO: Implement based on pseudocode")
            body_lines.append(f'{indent}throw new UnsupportedOperationException("Not implemented");')
        
        return "\n".join(body_lines)
    
    def _generate_constructor_body(self, algorithm: Dict[str, Any], language: str) -> str:
        """Generate constructor body for class implementation"""
        inputs = algorithm.get("inputs", [])
        
        body_lines = []
        indent = "        " if language in ["python", "java"] else "        "
        
        if language == "python":
            body_lines.append(f"{indent}# Initialize class attributes")
            for input in inputs:
                param_name = input.strip().split(":")[0].split(" ")[0].lower()
                param_name = "".join(c if c.isalnum() else "_" for c in param_name)
                if param_name and not param_name[0].isalpha() and param_name[0] != "_":
                    param_name = "arg_" + param_name
                if param_name:
                    body_lines.append(f"{indent}self.{param_name} = {param_name}")
        elif language == "javascript":
            body_lines.append(f"{indent}// Initialize class attributes")
            for input in inputs:
                param_name = input.strip().split(":")[0].split(" ")[0].lower()
                param_name = "".join(c if c.isalnum() else "_" for c in param_name)
                if param_name and not param_name[0].isalpha() and param_name[0] != "_":
                    param_name = "arg_" + param_name
                if param_name:
                    body_lines.append(f"{indent}this.{param_name} = {param_name};")
        elif language == "java":
            body_lines.append(f"{indent}// Initialize class attributes")
            for input in inputs:
                param_name = input.strip().split(":")[0].split(" ")[0].lower()
                param_name = "".join(c if c.isalnum() else "_" for c in param_name)
                if param_name and not param_name[0].isalpha() and param_name[0] != "_":
                    param_name = "arg_" + param_name
                if param_name:
                    body_lines.append(f"{indent}this.{param_name} = {param_name};")
        
        return "\n".join(body_lines)
    
    def _generate_class_methods(self, algorithm: Dict[str, Any], language: str) -> str:
        """Generate class methods based on algorithm description"""
        # For now, just add a placeholder main method
        if language == "python":
            return """    def run(self):
        """Execute the algorithm"""
        # TODO: Implement the main algorithm logic
        pass"""
        elif language == "javascript":
            return """    /**
     * Execute the algorithm
     */
    run() {
        // TODO: Implement the main algorithm logic
        throw new Error('Not implemented');
    }"""
        elif language == "java":
            return """    /**
     * Execute the algorithm
     */
    public void run() {
        // TODO: Implement the main algorithm logic
        throw new UnsupportedOperationException("Not implemented");
    }"""
    
    def _infer_return_type(self, algorithm: Dict[str, Any], language: str) -> str:
        """Infer return type for languages that require it"""
        outputs = algorithm.get("outputs", [])
        
        if not outputs:
            return "void"
            
        # Try to infer from output description
        output_text = " ".join(outputs).lower()
        
        if "boolean" in output_text or "true/false" in output_text:
            return "boolean"
        elif "integer" in output_text or "int" in output_text:
            return "int"
        elif "float" in output_text or "double" in output_text:
            return "double"
        elif "string" in output_text:
            return "String"
        elif "list" in output_text or "array" in output_text:
            if "integer" in output_text or "int" in output_text:
                return "List<Integer>"
            elif "string" in output_text:
                return "List<String>"
            else:
                return "List<Object>"
        
        return "Object"
    
    def _extract_dependencies(self, algorithm: Dict[str, Any], language: str) -> List[str]:
        """Extract likely dependencies based on algorithm description"""
        context = algorithm.get("context", "")
        pseudocode = algorithm.get("pseudocode", "")
        content = context + "\n" + pseudocode
        
        dependencies = []
        
        if language == "python":
            # Check for common Python libraries
            if any(term in content.lower() for term in ["array", "matrix", "vector"]):
                dependencies.append("import numpy as np")
            if any(term in content.lower() for term in ["dataframe", "csv", "pandas"]):
                dependencies.append("import pandas as pd")
            if any(term in content.lower() for term in ["plot", "figure", "chart", "graph"]):
                dependencies.append("import matplotlib.pyplot as plt")
        elif language == "javascript":
            # Check for common JavaScript libraries
            if any(term in content.lower() for term in ["array", "matrix", "vector"]):
                dependencies.append("// Consider using math.js for matrix operations")
            if any(term in content.lower() for term in ["dataframe", "csv", "data"]):
                dependencies.append("// Consider using d3.js for data handling")
            if any(term in content.lower() for term in ["plot", "figure", "chart", "graph"]):
                dependencies.append("// Consider using chart.js for visualization")
        elif language == "java":
            # Check for common Java libraries
            if any(term in content.lower() for term in ["array", "list", "collection"]):
                dependencies.append("import java.util.*;")
            if any(term in content.lower() for term in ["file", "io", "input", "output"]):
                dependencies.append("import java.io.*;")
        
        return dependencies
```

## Testing Guidance

### Unit Tests

```python
# test_state_machine.py
import pytest
from datetime import datetime, timedelta
from paper_processing.state_machine import PaperStatus, StateTransition, PaperStateHistory, PaperStateMachine

class MockStateHistoryRepository:
    def __init__(self):
        self.histories = {}
    
    def get(self, paper_id):
        return self.histories.get(paper_id)
    
    def save(self, history):
        self.histories[history.paper_id] = history
        return history

class TestPaperStateHistory:
    def test_add_transition(self):
        history = PaperStateHistory("test-paper")
        history.add_transition(PaperStatus.UPLOADED, PaperStatus.QUEUED)
        
        assert len(history.transitions) == 1
        assert history.transitions[0].from_state == PaperStatus.UPLOADED
        assert history.transitions[0].to_state == PaperStatus.QUEUED
    
    def test_current_state(self):
        history = PaperStateHistory("test-paper")
        
        # No transitions yet
        assert history.current_state() is None
        
        # Add transition
        history.add_transition(PaperStatus.UPLOADED, PaperStatus.QUEUED)
        assert history.current_state() == PaperStatus.QUEUED
        
        # Add another transition
        history.add_transition(PaperStatus.QUEUED, PaperStatus.PROCESSING)
        assert history.current_state() == PaperStatus.PROCESSING
    
    def test_get_transition_time(self):
        history = PaperStateHistory("test-paper")
        
        # Create transitions with fixed timestamps for testing
        now = datetime.now()
        transition1 = StateTransition(PaperStatus.UPLOADED, PaperStatus.QUEUED, now)
        transition2 = StateTransition(PaperStatus.QUEUED, PaperStatus.PROCESSING, now + timedelta(seconds=60))
        
        history.transitions = [transition1, transition2]
        
        # Test transition time calculation
        assert history.get_transition_time(PaperStatus.UPLOADED, PaperStatus.QUEUED) == 0
        assert history.get_transition_time(PaperStatus.QUEUED, PaperStatus.PROCESSING) == 60
        
        # Non-existent transition
        assert history.get_transition_time(PaperStatus.PROCESSING, PaperStatus.ANALYZED) is None
    
    def test_total_processing_time(self):
        history = PaperStateHistory("test-paper")
        
        # Create transitions with fixed timestamps for testing
        now = datetime.now()
        transition1 = StateTransition(PaperStatus.UPLOADED, PaperStatus.QUEUED, now)
        transition2 = StateTransition(PaperStatus.QUEUED, PaperStatus.PROCESSING, now + timedelta(seconds=60))
        transition3 = StateTransition(PaperStatus.PROCESSING, PaperStatus.EXTRACTING_ENTITIES, now + timedelta(seconds=120))
        
        history.transitions = [transition1, transition2, transition3]
        
        # Test total processing time
        assert history.total_processing_time() == 120
        
        # Not enough transitions
        history.transitions = [transition1]
        assert history.total_processing_time() is None

class TestPaperStateMachine:
    def test_valid_transition(self):
        repo = MockStateHistoryRepository()
        state_machine = PaperStateMachine(repo)
        
        # Initial transition for new paper
        result = state_machine.transition("test-paper", PaperStatus.UPLOADED)
        assert result is True
        
        # Get the history and check current state
        history = repo.get("test-paper")
        assert history.current_state() == PaperStatus.UPLOADED
        
        # Valid next transition
        result = state_machine.transition("test-paper", PaperStatus.QUEUED)
        assert result is True
        
        # Check updated state
        history = repo.get("test-paper")
        assert history.current_state() == PaperStatus.QUEUED
    
    def test_invalid_transition(self):
        repo = MockStateHistoryRepository()
        state_machine = PaperStateMachine(repo)
        
        # Create paper in UPLOADED state
        state_machine.transition("test-paper", PaperStatus.UPLOADED)
        
        # Invalid transition
        result = state_machine.transition("test-paper", PaperStatus.ANALYZED)
        assert result is False
        
        # State should not change
        history = repo.get("test-paper")
        assert history.current_state() == PaperStatus.UPLOADED
    
    def test_new_paper_must_start_with_uploaded(self):
        repo = MockStateHistoryRepository()
        state_machine = PaperStateMachine(repo)
        
        # Try to start new paper in non-UPLOADED state
        result = state_machine.transition("test-paper", PaperStatus.QUEUED)
        assert result is False
        
        # No history should be created
        assert repo.get("test-paper") is None
```

### Integration Tests

```python
# test_paper_processing_flow.py
import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil

from paper_processing.tasks.processing_tasks import (
    process_paper,
    extract_entities,
    extract_relationships,
    build_knowledge_graph,
    analyze_paper,
    prepare_for_implementation
)

from paper_processing.state_machine import PaperStateMachine, PaperStatus

# Create a fixture for test paper
@pytest.fixture
def test_paper_file():
    # Create temporary directory
    test_dir = tempfile.mkdtemp()
    
    # Create test PDF file
    test_file_path = os.path.join(test_dir, "test_paper.pdf")
    with open(test_file_path, "wb") as f:
        # Write minimal PDF content
        f.write(b"%PDF-1.4\n%Test File\n")
    
    yield test_file_path
    
    # Clean up
    shutil.rmtree(test_dir)

# Mock repositories
class MockPaperRepository:
    def __init__(self):
        self.papers = {}
    
    def get(self, paper_id):
        return self.papers.get(paper_id)
    
    def save(self, paper):
        self.papers[paper["id"]] = paper
        return paper

class MockStateHistoryRepository:
    def __init__(self):
        self.histories = {}
    
    def get(self, paper_id):
        return self.histories.get(paper_id)
    
    def save(self, history):
        self.histories[history.paper_id] = history
        return history

# Test the complete processing flow
@patch("paper_processing.tasks.processing_tasks.extract_entities")
def test_process_paper(mock_extract_entities, test_paper_file):
    # Arrange
    paper_id = "test-paper-123"
    mock_extract_entities.delay = MagicMock()
    
    # Act
    result = process_paper(paper_id, test_paper_file)
    
    # Assert
    assert result["paper_id"] == paper_id
    assert result["processed"] is True
    
    # Verify next task was queued
    mock_extract_entities.delay.assert_called_once()

@patch("paper_processing.tasks.processing_tasks.extract_relationships")
def test_extract_entities(mock_extract_relationships):
    # Arrange
    paper_id = "test-paper-123"
    document_data = {"content": "This is a test paper about transformer models."}
    mock_extract_relationships.delay = MagicMock()
    
    # Mock entity recognition
    with patch("knowledge_extraction.entity_recognition.EntityRecognizerFactory") as mock_factory:
        mock_ai_recognizer = MagicMock()
        mock_scientific_recognizer = MagicMock()
        
        mock_factory.return_value.create_ai_entity_recognizer.return_value = mock_ai_recognizer
        mock_factory.return_value.create_scientific_entity_recognizer.return_value = mock_scientific_recognizer
        
        mock_ai_recognizer.extract_entities.return_value = {
            "entity1": {"type": "MODEL", "name": "Transformer"}
        }
        mock_scientific_recognizer.extract_entities.return_value = {
            "entity2": {"type": "PAPER", "name": "Attention is All You Need"}
        }
        
        # Act
        result = extract_entities(paper_id, document_data)
        
        # Assert
        assert result["paper_id"] == paper_id
        assert result["entity_count"] == 2
        
        # Verify next task was queued
        mock_extract_relationships.delay.assert_called_once()

# Additional tests for other stages would follow a similar pattern
```

### WebSocket Testing

```python
# test_websockets.py
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from paper_processing.websockets.paper_status import PaperStatusNotifier, setup_websocket_routes

@pytest.fixture
def app():
    app = FastAPI()
    setup_websocket_routes(app)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.mark.asyncio
async def test_connect_and_disconnect():
    # Arrange
    notifier = PaperStatusNotifier()
    mock_websocket = AsyncMock(spec=WebSocket)
    
    # Act
    await notifier.connect(mock_websocket)
    
    # Assert
    assert mock_websocket in notifier.active_connections
    assert mock_websocket.accept.called
    
    # Act - disconnect
    notifier.disconnect(mock_websocket)
    
    # Assert
    assert mock_websocket not in notifier.active_connections

@pytest.mark.asyncio
async def test_paper_specific_subscription():
    # Arrange
    notifier = PaperStatusNotifier()
    mock_websocket = AsyncMock(spec=WebSocket)
    paper_id = "test-paper-123"
    
    # Act
    await notifier.connect(mock_websocket, paper_id)
    
    # Assert
    assert mock_websocket in notifier.active_connections
    assert paper_id in notifier.connections
    assert mock_websocket in notifier.connections[paper_id]
    
    # Act - disconnect
    notifier.disconnect(mock_websocket, paper_id)
    
    # Assert
    assert mock_websocket not in notifier.active_connections
    assert paper_id not in notifier.connections or mock_websocket not in notifier.connections[paper_id]

@pytest.mark.asyncio
async def test_send_paper_update():
    # Arrange
    notifier = PaperStatusNotifier()
    mock_websocket = AsyncMock(spec=WebSocket)
    paper_id = "test-paper-123"
    
    # Connect websocket to paper
    await notifier.connect(mock_websocket, paper_id)
    
    # Prepare update data
    update_data = {
        "type": "paper_status",
        "status": "processing",
        "progress": 50
    }
    
    # Act
    await notifier.send_paper_update(paper_id, update_data)
    
    # Assert
    mock_websocket.send_text.assert_called_once()
    # The message should include the data we sent
    sent_message = mock_websocket.send_text.call_args[0][0]
    assert paper_id in sent_message
    assert "processing" in sent_message
    assert "50" in sent_message
```

## Deployment and Operations

For deploying the Paper Processing Pipeline, consider the following guidelines:

1. **Resource Allocation**:
   - Each Celery worker should have adequate CPU and memory resources
   - Scaling can be achieved by adding more workers
   - Monitor resource usage to optimize allocation

2. **Logging and Monitoring**:
   - Implement comprehensive logging throughout the pipeline
   - Use a central logging system (e.g., ELK stack, Datadog, Prometheus)
   - Set up alerts for errors and performance issues

3. **Error Handling and Recovery**:
   - Implement dead letter queues for failed tasks
   - Provide mechanisms for retrying failed papers
   - Design the system to recover gracefully from worker failures

4. **Security Considerations**:
   - Validate file types before processing
   - Implement resource limits to prevent DoS attacks
   - Sanitize inputs and outputs to prevent injection attacks

5. **Performance Optimization**:
   - Implement caching where appropriate
   - Use bulk operations for database interactions
   - Consider distributed processing for large workloads

## Conclusion

The Paper Processing Pipeline is a critical component of the AI Research Integration Project. It bridges the gap between paper uploads and knowledge extraction, enabling automatic processing of research documents and seamless integration with the knowledge graph and implementation systems.

By following the guidelines and implementations provided in this document, you will create a robust, scalable, and maintainable pipeline that can efficiently process research papers, extract valuable knowledge, and prepare them for implementation.

Remember to maintain the modular architecture, use appropriate error handling, and follow the testing guidelines to ensure the system works reliably in production.