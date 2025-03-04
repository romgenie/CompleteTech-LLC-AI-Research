"""
Adapters for the Research Orchestration Framework.

This module contains adapters for integrating with external repositories
and tools.
"""

from research_orchestrator.adapters.base_adapter import (
    BaseAdapter,
    TaskDecompositionAdapter,
    PlanningAdapter,
    InformationGatheringAdapter,
    KnowledgeExtractionAdapter
)
from research_orchestrator.adapters.tdag_adapter import TDAGAdapter

__version__ = "0.1.0"

__all__ = [
    'BaseAdapter',
    'TaskDecompositionAdapter',
    'PlanningAdapter',
    'InformationGatheringAdapter',
    'KnowledgeExtractionAdapter',
    'TDAGAdapter'
]