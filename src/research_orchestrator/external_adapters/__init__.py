"""
External Adapters package for the research orchestrator.

This package provides adapters for external repositories, allowing the research
orchestrator to integrate and utilize their capabilities.
"""

from .base_adapter import BaseAdapter
from .gdesigner import GDesignerAdapter
from .open_deep_research import OpenDeepResearchAdapter

__all__ = ['BaseAdapter', 'GDesignerAdapter', 'OpenDeepResearchAdapter']