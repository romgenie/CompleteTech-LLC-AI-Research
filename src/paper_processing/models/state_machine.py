"""
State machine for paper processing.

This module defines the state machine pattern implementation for tracking
and managing paper processing states in the Paper Processing Pipeline.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

from .paper import Paper, PaperStatus, add_processing_event


logger = logging.getLogger(__name__)


class StateTransitionException(Exception):
    """Exception raised for invalid state transitions."""
    pass


class PaperState(ABC):
    """Base class for paper states in the state machine."""
    
    @property
    @abstractmethod
    def status(self) -> PaperStatus:
        """Return the status associated with this state."""
        pass
    
    @abstractmethod
    def process(self, paper: Paper) -> Tuple[Paper, "PaperState"]:
        """
        Process the paper in this state.
        
        Args:
            paper: The paper to process
            
        Returns:
            Tuple containing the updated paper and the next state
        """
        pass
    
    def can_transition_to(self, next_state: "PaperState") -> bool:
        """
        Check if transition to the next state is valid.
        
        Args:
            next_state: The state to transition to
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Default implementation: no transitions allowed
        return False
    
    def enter(self, paper: Paper, message: str = None) -> Paper:
        """
        Actions to perform when entering this state.
        
        Args:
            paper: The paper entering this state
            message: Optional message for the state change
            
        Returns:
            The updated paper
        """
        if not message:
            message = f"Entered {self.status.value} state"
            
        logger.info(f"Paper {paper.id} entered {self.status.value} state")
        return add_processing_event(paper, self.status, message)


class UploadedState(PaperState):
    """State representing a newly uploaded paper."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.UPLOADED
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # No processing in this state, needs to be queued
        return paper, self
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can only transition to QUEUED state
        return next_state.status == PaperStatus.QUEUED


class QueuedState(PaperState):
    """State representing a paper queued for processing."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.QUEUED
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Begin processing
        from .state_factory import get_state
        return paper, get_state(PaperStatus.PROCESSING)
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can transition to PROCESSING or back to UPLOADED
        return next_state.status in [PaperStatus.PROCESSING, PaperStatus.UPLOADED]


class ProcessingState(PaperState):
    """State representing a paper being processed."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.PROCESSING
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Move to entity extraction
        from .state_factory import get_state
        return paper, get_state(PaperStatus.EXTRACTING_ENTITIES)
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can transition to extraction states or FAILED
        valid_states = [
            PaperStatus.EXTRACTING_ENTITIES, 
            PaperStatus.FAILED,
            PaperStatus.QUEUED  # Allow going back to queue if needed
        ]
        return next_state.status in valid_states


class ExtractingEntitiesState(PaperState):
    """State representing entity extraction from a paper."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.EXTRACTING_ENTITIES
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Move to relationship extraction
        from .state_factory import get_state
        return paper, get_state(PaperStatus.EXTRACTING_RELATIONSHIPS)
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can transition to relationship extraction or FAILED
        valid_states = [
            PaperStatus.EXTRACTING_RELATIONSHIPS, 
            PaperStatus.FAILED,
            PaperStatus.PROCESSING  # Allow going back if needed
        ]
        return next_state.status in valid_states


class ExtractingRelationshipsState(PaperState):
    """State representing relationship extraction from a paper."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.EXTRACTING_RELATIONSHIPS
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Move to knowledge graph building
        from .state_factory import get_state
        return paper, get_state(PaperStatus.BUILDING_KNOWLEDGE_GRAPH)
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can transition to knowledge graph or FAILED
        valid_states = [
            PaperStatus.BUILDING_KNOWLEDGE_GRAPH, 
            PaperStatus.FAILED,
            PaperStatus.EXTRACTING_ENTITIES  # Allow going back if needed
        ]
        return next_state.status in valid_states


class BuildingKnowledgeGraphState(PaperState):
    """State representing knowledge graph building from a paper."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.BUILDING_KNOWLEDGE_GRAPH
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Move to analyzed state
        from .state_factory import get_state
        return paper, get_state(PaperStatus.ANALYZED)
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can transition to analyzed or FAILED
        valid_states = [
            PaperStatus.ANALYZED, 
            PaperStatus.FAILED,
            PaperStatus.EXTRACTING_RELATIONSHIPS  # Allow going back if needed
        ]
        return next_state.status in valid_states


class AnalyzedState(PaperState):
    """State representing a fully analyzed paper."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.ANALYZED
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Move to implementation ready if applicable
        if paper.implementation_ready:
            from .state_factory import get_state
            return paper, get_state(PaperStatus.IMPLEMENTATION_READY)
        return paper, self
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can transition to implementation ready or back to knowledge graph
        valid_states = [
            PaperStatus.IMPLEMENTATION_READY, 
            PaperStatus.BUILDING_KNOWLEDGE_GRAPH
        ]
        return next_state.status in valid_states


class ImplementationReadyState(PaperState):
    """State representing a paper ready for implementation."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.IMPLEMENTATION_READY
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Terminal state, no further processing
        return paper, self
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Terminal state, no transitions except back to analyzed
        return next_state.status == PaperStatus.ANALYZED


class FailedState(PaperState):
    """State representing a paper that failed processing."""
    
    @property
    def status(self) -> PaperStatus:
        return PaperStatus.FAILED
    
    def process(self, paper: Paper) -> Tuple[Paper, PaperState]:
        # Terminal state, no further processing
        return paper, self
    
    def can_transition_to(self, next_state: PaperState) -> bool:
        # Can only transition back to queued for retry
        return next_state.status == PaperStatus.QUEUED


class PaperStateMachine:
    """
    State machine for managing paper processing states.
    
    This class handles the state transitions and processing of papers.
    """
    
    def __init__(self, paper: Paper):
        """
        Initialize the state machine.
        
        Args:
            paper: The paper to manage
        """
        from .state_factory import get_state
        self.paper = paper
        self.current_state = get_state(paper.status)
        
    def transition_to(self, new_status: PaperStatus, message: str = None) -> Paper:
        """
        Transition the paper to a new state.
        
        Args:
            new_status: The status to transition to
            message: Optional message for the transition
            
        Returns:
            The updated paper
            
        Raises:
            StateTransitionException: If the transition is invalid
        """
        from .state_factory import get_state
        new_state = get_state(new_status)
        
        if not self.current_state.can_transition_to(new_state):
            current_status = self.current_state.status.value
            raise StateTransitionException(
                f"Invalid transition from {current_status} to {new_status.value}"
            )
            
        # Enter the new state
        self.paper = new_state.enter(self.paper, message)
        self.current_state = new_state
        
        return self.paper
        
    def process(self) -> Paper:
        """
        Process the paper in its current state.
        
        Returns:
            The updated paper
        """
        self.paper, new_state = self.current_state.process(self.paper)
        
        # If the state has changed, perform the transition
        if new_state != self.current_state:
            self.paper = new_state.enter(
                self.paper, 
                f"Automatic transition from {self.current_state.status.value}"
            )
            self.current_state = new_state
            
        return self.paper