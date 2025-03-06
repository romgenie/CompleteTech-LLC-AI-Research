"""
Paper Processing package for the Research Understanding Engine.

This package provides components for parsing and processing research papers
into structured representations for further analysis.
"""

from .paper_processor import (
    PaperFormat,
    PaperSection,
    PaperReference,
    PaperFigure,
    PaperTable,
    PaperAlgorithm,
    StructuredPaper,
    PaperProcessor,
    PDFPaperProcessor,
    HTMLPaperProcessor,
    ArXivPaperProcessor
)

__all__ = [
    'PaperFormat',
    'PaperSection',
    'PaperReference',
    'PaperFigure',
    'PaperTable',
    'PaperAlgorithm',
    'StructuredPaper',
    'PaperProcessor',
    'PDFPaperProcessor',
    'HTMLPaperProcessor',
    'ArXivPaperProcessor',
]