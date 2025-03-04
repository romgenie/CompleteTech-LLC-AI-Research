"""
Research Understanding Engine package.

This package provides components for analyzing and extracting structured information
from research papers, including algorithms, implementation details, and architectures.
"""

# Make subpackages available
from . import paper_processing
from . import algorithm_extraction
from . import implementation_details

# Import main engine class
from .understanding_engine import ResearchUnderstandingEngine

__all__ = [
    'paper_processing',
    'algorithm_extraction',
    'implementation_details',
    'ResearchUnderstandingEngine',
]