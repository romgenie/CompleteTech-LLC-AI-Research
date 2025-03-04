"""
Document Processing module for the Knowledge Extraction Pipeline.

This module provides components for processing various document formats
(PDF, HTML, text) and preparing them for knowledge extraction.
"""

from research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from research_orchestrator.knowledge_extraction.document_processing.pdf_processor import PDFProcessor
from research_orchestrator.knowledge_extraction.document_processing.html_processor import HTMLProcessor
from research_orchestrator.knowledge_extraction.document_processing.text_processor import TextProcessor

__all__ = [
    'DocumentProcessor',
    'PDFProcessor',
    'HTMLProcessor',
    'TextProcessor'
]