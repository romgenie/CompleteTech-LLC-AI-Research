"""
Information Sources for the Information Gathering Module.

This module contains implementations for various information sources
that can be used for research.
"""

# Use relative imports instead of absolute imports
from .base_source import BaseSource
from .academic import AcademicSource
from .web import WebSource
from .code import CodeSource
from .ai import AISource

__all__ = [
    'BaseSource',
    'AcademicSource',
    'WebSource',
    'CodeSource',
    'AISource'
]