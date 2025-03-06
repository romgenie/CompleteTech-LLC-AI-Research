"""
KARMA Adapter for the Research Orchestration Framework.

This module provides adapters for integrating with the KARMA framework
for knowledge extraction and knowledge graph construction.
"""

from .karma_adapter import KARMAAdapter
from .knowledge_extractor import KARMAKnowledgeExtractor

__all__ = [
    'KARMAAdapter',
    'KARMAKnowledgeExtractor'
]