"""
Research Generation System for the Research Orchestration Framework.

This package provides components for generating well-structured research outputs,
including report planning, content synthesis, citation management, visualization,
and code examples.
"""

from .report_structure import ReportStructurePlanner, DocumentType, SectionType

__all__ = ['ReportStructurePlanner', 'DocumentType', 'SectionType']