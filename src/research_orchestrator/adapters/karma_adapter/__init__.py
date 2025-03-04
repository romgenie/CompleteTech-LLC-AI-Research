"""
KARMA Adapter for the Research Orchestration Framework.

This module provides adapters for integrating with the KARMA framework
for knowledge extraction and knowledge graph construction.
"""

from research_orchestrator.adapters.karma_adapter.karma_adapter import KARMAAdapter
from research_orchestrator.adapters.karma_adapter.knowledge_extractor import KARMAKnowledgeExtractor

__all__ = [
    'KARMAAdapter',
    'KARMAKnowledgeExtractor'
]