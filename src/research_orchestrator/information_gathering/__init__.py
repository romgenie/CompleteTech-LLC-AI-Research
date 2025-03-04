"""
Information Gathering Module.

This module handles the retrieval of information from various sources
for the Research Orchestration Framework.
"""

from research_orchestrator.information_gathering.search_manager import SearchManager
from research_orchestrator.information_gathering.source_manager import SourceManager
from research_orchestrator.information_gathering.quality_assessor import QualityAssessor

__version__ = "0.1.0"

__all__ = [
    'SearchManager',
    'SourceManager',
    'QualityAssessor'
]