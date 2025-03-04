"""
State factory for paper processing state machine.

This module provides a factory for creating state objects based on paper status.
"""

from typing import Dict, Type

from .paper import PaperStatus
from .state_machine import (
    PaperState,
    UploadedState,
    QueuedState,
    ProcessingState,
    ExtractingEntitiesState,
    ExtractingRelationshipsState,
    BuildingKnowledgeGraphState,
    AnalyzedState,
    ImplementationReadyState,
    FailedState
)


# Map of status to state classes
_STATE_MAP: Dict[PaperStatus, Type[PaperState]] = {
    PaperStatus.UPLOADED: UploadedState,
    PaperStatus.QUEUED: QueuedState,
    PaperStatus.PROCESSING: ProcessingState,
    PaperStatus.EXTRACTING_ENTITIES: ExtractingEntitiesState,
    PaperStatus.EXTRACTING_RELATIONSHIPS: ExtractingRelationshipsState,
    PaperStatus.BUILDING_KNOWLEDGE_GRAPH: BuildingKnowledgeGraphState,
    PaperStatus.ANALYZED: AnalyzedState,
    PaperStatus.IMPLEMENTATION_READY: ImplementationReadyState,
    PaperStatus.FAILED: FailedState
}


def get_state(status: PaperStatus) -> PaperState:
    """
    Get the appropriate state for a paper status.
    
    Args:
        status: The paper status to get a state for
        
    Returns:
        A PaperState instance for the given status
        
    Raises:
        ValueError: If no state is defined for the status
    """
    if status not in _STATE_MAP:
        raise ValueError(f"No state defined for status: {status}")
        
    return _STATE_MAP[status]()