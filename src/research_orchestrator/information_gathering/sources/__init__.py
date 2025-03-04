"""
Information Sources for the Information Gathering Module.

This module contains implementations for various information sources
that can be used for research.
"""

from research_orchestrator.information_gathering.sources.base_source import BaseSource
from research_orchestrator.information_gathering.sources.academic import AcademicSource
from research_orchestrator.information_gathering.sources.web import WebSource
from research_orchestrator.information_gathering.sources.code import CodeSource
from research_orchestrator.information_gathering.sources.ai import AISource

__all__ = [
    'BaseSource',
    'AcademicSource',
    'WebSource',
    'CodeSource',
    'AISource'
]