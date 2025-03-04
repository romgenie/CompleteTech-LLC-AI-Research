"""
Research Understanding module for analyzing and extracting structured information from papers.
"""

from .understanding_engine import ResearchUnderstandingEngine
from .paper_processing.paper_processor import PaperProcessor, StructuredPaper, PaperFormat
from .algorithm_extraction.algorithm_extractor import AlgorithmExtractor, ExtractedAlgorithm
from .implementation_details.detail_collector import ImplementationDetailCollector