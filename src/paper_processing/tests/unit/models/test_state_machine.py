"""
Unit tests for the paper state machine.

This module tests the paper state machine functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime

from paper_processing.models.paper import Paper, PaperStatus
from paper_processing.models.state_machine import (
    PaperState,
    UploadedState,
    QueuedState,
    ProcessingState,
    ExtractingEntitiesState,
    ExtractingRelationshipsState,
    BuildingKnowledgeGraphState,
    AnalyzedState,
    ImplementationReadyState,
    FailedState,
    PaperStateMachine,
    StateTransitionException
)


def test_uploaded_state():
    """Test the UploadedState class."""
    # Create state
    state = UploadedState()
    
    # Check status
    assert state.status == PaperStatus.UPLOADED
    
    # Check transitions
    queued_state = QueuedState()
    processing_state = ProcessingState()
    failed_state = FailedState()
    
    assert state.can_transition_to(queued_state) is True
    assert state.can_transition_to(processing_state) is False
    assert state.can_transition_to(failed_state) is False
    
    # Test process method
    paper = MagicMock()
    result_paper, result_state = state.process(paper)
    assert result_paper == paper
    assert result_state == state


def test_queued_state():
    """Test the QueuedState class."""
    # Create state
    state = QueuedState()
    
    # Check status
    assert state.status == PaperStatus.QUEUED
    
    # Check transitions
    uploaded_state = UploadedState()
    processing_state = ProcessingState()
    failed_state = FailedState()
    
    assert state.can_transition_to(uploaded_state) is True
    assert state.can_transition_to(processing_state) is True
    assert state.can_transition_to(failed_state) is False


def test_processing_state():
    """Test the ProcessingState class."""
    # Create state
    state = ProcessingState()
    
    # Check status
    assert state.status == PaperStatus.PROCESSING
    
    # Check transitions
    queued_state = QueuedState()
    entities_state = ExtractingEntitiesState()
    failed_state = FailedState()
    
    assert state.can_transition_to(queued_state) is True
    assert state.can_transition_to(entities_state) is True
    assert state.can_transition_to(failed_state) is True


def test_extracting_entities_state():
    """Test the ExtractingEntitiesState class."""
    # Create state
    state = ExtractingEntitiesState()
    
    # Check status
    assert state.status == PaperStatus.EXTRACTING_ENTITIES
    
    # Check transitions
    processing_state = ProcessingState()
    relationships_state = ExtractingRelationshipsState()
    failed_state = FailedState()
    
    assert state.can_transition_to(processing_state) is True
    assert state.can_transition_to(relationships_state) is True
    assert state.can_transition_to(failed_state) is True


def test_extracting_relationships_state():
    """Test the ExtractingRelationshipsState class."""
    # Create state
    state = ExtractingRelationshipsState()
    
    # Check status
    assert state.status == PaperStatus.EXTRACTING_RELATIONSHIPS
    
    # Check transitions
    entities_state = ExtractingEntitiesState()
    graph_state = BuildingKnowledgeGraphState()
    failed_state = FailedState()
    
    assert state.can_transition_to(entities_state) is True
    assert state.can_transition_to(graph_state) is True
    assert state.can_transition_to(failed_state) is True


def test_building_knowledge_graph_state():
    """Test the BuildingKnowledgeGraphState class."""
    # Create state
    state = BuildingKnowledgeGraphState()
    
    # Check status
    assert state.status == PaperStatus.BUILDING_KNOWLEDGE_GRAPH
    
    # Check transitions
    relationships_state = ExtractingRelationshipsState()
    analyzed_state = AnalyzedState()
    failed_state = FailedState()
    
    assert state.can_transition_to(relationships_state) is True
    assert state.can_transition_to(analyzed_state) is True
    assert state.can_transition_to(failed_state) is True


def test_analyzed_state():
    """Test the AnalyzedState class."""
    # Create state
    state = AnalyzedState()
    
    # Check status
    assert state.status == PaperStatus.ANALYZED
    
    # Check transitions
    graph_state = BuildingKnowledgeGraphState()
    impl_state = ImplementationReadyState()
    failed_state = FailedState()
    
    assert state.can_transition_to(graph_state) is True
    assert state.can_transition_to(impl_state) is True
    assert state.can_transition_to(failed_state) is False


def test_implementation_ready_state():
    """Test the ImplementationReadyState class."""
    # Create state
    state = ImplementationReadyState()
    
    # Check status
    assert state.status == PaperStatus.IMPLEMENTATION_READY
    
    # Check transitions
    analyzed_state = AnalyzedState()
    failed_state = FailedState()
    
    assert state.can_transition_to(analyzed_state) is True
    assert state.can_transition_to(failed_state) is False


def test_failed_state():
    """Test the FailedState class."""
    # Create state
    state = FailedState()
    
    # Check status
    assert state.status == PaperStatus.FAILED
    
    # Check transitions
    queued_state = QueuedState()
    processed_state = ProcessingState()
    
    assert state.can_transition_to(queued_state) is True
    assert state.can_transition_to(processed_state) is False


def test_paper_state_machine_init():
    """Test initializing the PaperStateMachine."""
    # Create a paper
    paper = MagicMock()
    paper.status = PaperStatus.UPLOADED
    
    # Initialize state machine
    with patch('paper_processing.models.state_machine.get_state') as mock_get_state:
        mock_state = MagicMock()
        mock_get_state.return_value = mock_state
        
        state_machine = PaperStateMachine(paper)
        
        # Check that get_state was called with the paper status
        mock_get_state.assert_called_once_with(PaperStatus.UPLOADED)
        
        # Check that the current state is set correctly
        assert state_machine.paper == paper
        assert state_machine.current_state == mock_state


def test_paper_state_machine_transition_valid():
    """Test valid state transition in PaperStateMachine."""
    # Create a paper
    paper = MagicMock()
    paper.status = PaperStatus.UPLOADED
    
    # Initialize state machine
    with patch('paper_processing.models.state_machine.get_state') as mock_get_state:
        # Mock states
        mock_uploaded_state = MagicMock()
        mock_uploaded_state.status = PaperStatus.UPLOADED
        mock_uploaded_state.can_transition_to.return_value = True
        
        mock_queued_state = MagicMock()
        mock_queued_state.status = PaperStatus.QUEUED
        mock_queued_state.enter.return_value = paper
        
        # Configure get_state
        def mock_get_state_func(status):
            if status == PaperStatus.UPLOADED:
                return mock_uploaded_state
            elif status == PaperStatus.QUEUED:
                return mock_queued_state
            return None
        
        mock_get_state.side_effect = mock_get_state_func
        
        # Create state machine
        state_machine = PaperStateMachine(paper)
        
        # Transition to queued state
        result = state_machine.transition_to(PaperStatus.QUEUED, "Test transition")
        
        # Check that can_transition_to was called
        mock_uploaded_state.can_transition_to.assert_called_once_with(mock_queued_state)
        
        # Check that enter was called
        mock_queued_state.enter.assert_called_once_with(paper, "Test transition")
        
        # Check that the state was updated
        assert state_machine.current_state == mock_queued_state
        
        # Check that the paper was returned
        assert result == paper


def test_paper_state_machine_transition_invalid():
    """Test invalid state transition in PaperStateMachine."""
    # Create a paper
    paper = MagicMock()
    paper.status = PaperStatus.UPLOADED
    
    # Initialize state machine
    with patch('paper_processing.models.state_machine.get_state') as mock_get_state:
        # Mock states
        mock_uploaded_state = MagicMock()
        mock_uploaded_state.status = PaperStatus.UPLOADED
        mock_uploaded_state.can_transition_to.return_value = False
        
        mock_processing_state = MagicMock()
        mock_processing_state.status = PaperStatus.PROCESSING
        
        # Configure get_state
        def mock_get_state_func(status):
            if status == PaperStatus.UPLOADED:
                return mock_uploaded_state
            elif status == PaperStatus.PROCESSING:
                return mock_processing_state
            return None
        
        mock_get_state.side_effect = mock_get_state_func
        
        # Create state machine
        state_machine = PaperStateMachine(paper)
        
        # Transition to processing state (invalid)
        with pytest.raises(StateTransitionException):
            state_machine.transition_to(PaperStatus.PROCESSING, "Test transition")
        
        # Check that can_transition_to was called
        mock_uploaded_state.can_transition_to.assert_called_once_with(mock_processing_state)
        
        # Check that the state was not updated
        assert state_machine.current_state == mock_uploaded_state


def test_paper_state_machine_process():
    """Test processing a paper in PaperStateMachine."""
    # Create a paper
    paper = MagicMock()
    paper.status = PaperStatus.UPLOADED
    
    # Initialize state machine
    with patch('paper_processing.models.state_machine.get_state') as mock_get_state:
        # Mock states
        mock_uploaded_state = MagicMock()
        mock_uploaded_state.status = PaperStatus.UPLOADED
        mock_uploaded_state.process.return_value = (paper, mock_uploaded_state)
        
        # Configure get_state
        mock_get_state.return_value = mock_uploaded_state
        
        # Create state machine
        state_machine = PaperStateMachine(paper)
        
        # Process the paper
        result = state_machine.process()
        
        # Check that process was called
        mock_uploaded_state.process.assert_called_once_with(paper)
        
        # Check that the state was not updated
        assert state_machine.current_state == mock_uploaded_state
        
        # Check that the paper was returned
        assert result == paper


def test_paper_state_machine_process_state_change():
    """Test processing a paper with state change in PaperStateMachine."""
    # Create a paper
    paper = MagicMock()
    paper.status = PaperStatus.UPLOADED
    
    # Initialize state machine
    with patch('paper_processing.models.state_machine.get_state') as mock_get_state:
        # Mock states
        mock_uploaded_state = MagicMock()
        mock_uploaded_state.status = PaperStatus.UPLOADED
        
        mock_queued_state = MagicMock()
        mock_queued_state.status = PaperStatus.QUEUED
        mock_queued_state.enter.return_value = paper
        
        # Process returns new state
        mock_uploaded_state.process.return_value = (paper, mock_queued_state)
        
        # Configure get_state
        def mock_get_state_func(status):
            if status == PaperStatus.UPLOADED:
                return mock_uploaded_state
            elif status == PaperStatus.QUEUED:
                return mock_queued_state
            return None
        
        mock_get_state.side_effect = mock_get_state_func
        
        # Create state machine
        state_machine = PaperStateMachine(paper)
        
        # Process the paper
        result = state_machine.process()
        
        # Check that process was called
        mock_uploaded_state.process.assert_called_once_with(paper)
        
        # Check that enter was called
        mock_queued_state.enter.assert_called_once()
        
        # Check that the state was updated
        assert state_machine.current_state == mock_queued_state
        
        # Check that the paper was returned
        assert result == paper