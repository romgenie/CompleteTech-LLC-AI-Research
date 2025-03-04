"""
External Adapters package for the research orchestrator.

This package provides adapters for external repositories, allowing the research
orchestrator to integrate and utilize their capabilities.
"""

from .base_adapter import BaseAdapter
from .gdesigner.gdesigner_adapter import GDesignerAdapter
from .open_deep_research.open_deep_research_adapter import OpenDeepResearchAdapter
from .autocode_agent.autocode_agent_adapter import AutoCodeAgentAdapter

__all__ = ['BaseAdapter', 'GDesignerAdapter', 'OpenDeepResearchAdapter', 'AutoCodeAgentAdapter']