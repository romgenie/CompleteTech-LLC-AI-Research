"""
Citation management module for the Research Generation System.

This module provides functionality for handling citations, references,
and bibliographies in research documents.
"""

from .citation_manager import CitationManager, CitationStyle
from .citation_formatter import format_citation, format_reference_list

__all__ = [
    "CitationManager",
    "CitationStyle",
    "format_citation",
    "format_reference_list"
]