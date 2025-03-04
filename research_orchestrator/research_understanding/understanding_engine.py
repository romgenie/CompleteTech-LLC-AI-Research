"""
Research Understanding Engine module.

This module provides high-level functionality for understanding research papers,
extracting structured information, and preparing for implementation.
"""

from typing import Dict, List, Optional, Union, Any
import os
import json
from pathlib import Path
import logging

from .paper_processing import PaperProcessor, StructuredPaper, PaperFormat
from .algorithm_extraction import (
    AlgorithmExtractor, ExtractedAlgorithm, AlgorithmImplementationGenerator
)
from .implementation_details import (
    ImplementationDetailCollector, ImplementationDetail
)

# Configure logger
logger = logging.getLogger(__name__)


class ResearchUnderstandingEngine:
    """
    Main engine for understanding research papers and extracting implementation details.
    
    This class coordinates the paper processing, algorithm extraction, and implementation
    generation stages to provide a comprehensive understanding of research papers.
    """
    
    def __init__(self,
                config: Optional[Dict[str, Any]] = None,
                cache_dir: Optional[str] = None):
        """
        Initialize the Research Understanding Engine.
        
        Args:
            config: Configuration dictionary for the engine and its components
            cache_dir: Directory to cache processed papers and extracted information
        """
        self.config = config or {}
        self.cache_dir = cache_dir
        
        # Configure cache directories
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            self.paper_cache_dir = os.path.join(self.cache_dir, "papers")
            self.algorithm_cache_dir = os.path.join(self.cache_dir, "algorithms")
            self.implementation_cache_dir = os.path.join(self.cache_dir, "implementations")
            self.detail_cache_dir = os.path.join(self.cache_dir, "implementation_details")
            
            os.makedirs(self.paper_cache_dir, exist_ok=True)
            os.makedirs(self.algorithm_cache_dir, exist_ok=True)
            os.makedirs(self.implementation_cache_dir, exist_ok=True)
            os.makedirs(self.detail_cache_dir, exist_ok=True)
        else:
            self.paper_cache_dir = None
            self.algorithm_cache_dir = None
            self.implementation_cache_dir = None
            self.detail_cache_dir = None
        
        # Initialize components
        self.paper_processor = PaperProcessor(
            document_processors=self.config.get("document_processors"),
            language_model_config=self.config.get("language_model_config"),
            cache_dir=self.paper_cache_dir
        )
        
        self.algorithm_extractor = AlgorithmExtractor(
            language_model_config=self.config.get("language_model_config"),
            cache_dir=self.algorithm_cache_dir
        )
        
        self.detail_collector = ImplementationDetailCollector(
            language_model_config=self.config.get("language_model_config"),
            cache_dir=self.detail_cache_dir
        )
        
        self.implementation_generator = AlgorithmImplementationGenerator(
            language_model_config=self.config.get("language_model_config"),
            template_dir=self.config.get("implementation_templates_dir")
        )
    
    def process_paper(self,
                     paper_path: Union[str, Path],
                     paper_format: Optional[PaperFormat] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     extract_algorithms: bool = True,
                     collect_implementation_details: bool = True,
                     force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process a research paper end-to-end.
        
        Args:
            paper_path: Path to the paper file
            paper_format: Format of the paper (autodetected if None)
            metadata: Optional metadata about the paper
            extract_algorithms: Whether to extract algorithms
            collect_implementation_details: Whether to collect implementation details
            force_reprocess: If True, force reprocessing even if cached
            
        Returns:
            Dictionary containing structured paper and extracted information
        """
        # Process the paper
        logger.info(f"Processing paper: {paper_path}")
        paper = self.paper_processor.process_paper(
            paper_path=paper_path,
            paper_format=paper_format,
            metadata=metadata,
            force_reprocess=force_reprocess
        )
        
        result = {
            "paper": paper,
            "algorithms": [],
            "implementation_details": None,
            "implementations": {}
        }
        
        # Extract algorithms if requested
        algorithms = []
        if extract_algorithms:
            logger.info(f"Extracting algorithms from paper: {paper.paper_id}")
            algorithms = self.algorithm_extractor.extract_algorithms(
                paper=paper,
                force_reextract=force_reprocess
            )
            result["algorithms"] = algorithms
        
        # Collect implementation details if requested
        if collect_implementation_details:
            logger.info(f"Collecting implementation details from paper: {paper.paper_id}")
            implementation_details = self.detail_collector.collect_details(
                paper=paper,
                algorithms=algorithms,
                force_recollect=force_reprocess
            )
            result["implementation_details"] = implementation_details
        
        return result
    
    def generate_implementations(self,
                               algorithms: List[ExtractedAlgorithm],
                               language: str = "python",
                               include_comments: bool = True) -> Dict[str, str]:
        """
        Generate code implementations for a list of algorithms.
        
        Args:
            algorithms: List of algorithms to implement
            language: Target programming language
            include_comments: Whether to include detailed comments
            
        Returns:
            Dictionary mapping algorithm IDs to implementations
        """
        implementations = {}
        
        for algorithm in algorithms:
            logger.info(f"Generating {language} implementation for algorithm: {algorithm.name}")
            implementation = self.implementation_generator.generate_implementation(
                algorithm=algorithm,
                language=language,
                include_comments=include_comments
            )
            implementations[algorithm.algorithm_id] = implementation
            
            # Cache implementation if appropriate
            if self.implementation_cache_dir:
                self._cache_implementation(
                    algorithm_id=algorithm.algorithm_id,
                    language=language,
                    implementation=implementation
                )
        
        return implementations
    
    def extract_implementation_details(self,
                                     paper: StructuredPaper,
                                     algorithm_id: str) -> ExtractedAlgorithm:
        """
        Extract detailed implementation information for a specific algorithm.
        
        Args:
            paper: Source paper
            algorithm_id: ID of the algorithm to extract details for
            
        Returns:
            Enriched ExtractedAlgorithm with implementation details
        """
        # Find the algorithm
        algorithm = None
        for algo in paper.algorithms:
            if algo.algorithm_id == algorithm_id:
                algorithm = ExtractedAlgorithm.from_paper_algorithm(algo, paper.paper_id)
                break
        
        if not algorithm:
            raise ValueError(f"Algorithm with ID {algorithm_id} not found in paper {paper.paper_id}")
        
        # Extract implementation details
        logger.info(f"Extracting implementation details for algorithm: {algorithm.name}")
        enriched_algorithm = self.algorithm_extractor.extract_implementation_details(
            algorithm=algorithm,
            paper=paper
        )
        
        return enriched_algorithm
    
    def enhance_algorithm_with_details(self,
                                      algorithm: ExtractedAlgorithm,
                                      paper: StructuredPaper) -> ExtractedAlgorithm:
        """
        Enhance an algorithm with comprehensive implementation details.
        
        This method combines the algorithm extractor's capabilities with the 
        implementation detail collector to create a rich algorithm representation.
        
        Args:
            algorithm: Algorithm to enhance
            paper: Source paper
            
        Returns:
            Enhanced algorithm with comprehensive implementation details
        """
        # First use the algorithm extractor to get basic implementation details
        logger.info(f"Enhancing algorithm with implementation details: {algorithm.name}")
        enhanced_algorithm = self.algorithm_extractor.extract_implementation_details(
            algorithm=algorithm,
            paper=paper
        )
        
        # Then use the implementation detail collector for richer information
        enhanced_algorithm = self.detail_collector.enhance_algorithm(
            algorithm=enhanced_algorithm,
            paper=paper
        )
        
        return enhanced_algorithm
    
    def collect_implementation_details(self,
                                     paper: StructuredPaper,
                                     algorithms: Optional[List[ExtractedAlgorithm]] = None,
                                     force_recollect: bool = False) -> ImplementationDetail:
        """
        Collect comprehensive implementation details from a paper.
        
        Args:
            paper: Source paper
            algorithms: Pre-extracted algorithms (will be extracted if None)
            force_recollect: If True, force re-collection even if cached
            
        Returns:
            Implementation details object
        """
        logger.info(f"Collecting comprehensive implementation details from paper: {paper.paper_id}")
        return self.detail_collector.collect_details(
            paper=paper,
            algorithms=algorithms,
            force_recollect=force_recollect
        )
    
    def _cache_implementation(self,
                            algorithm_id: str,
                            language: str,
                            implementation: str) -> None:
        """
        Cache a generated implementation.
        
        Args:
            algorithm_id: ID of the algorithm
            language: Programming language of the implementation
            implementation: Implementation code
        """
        if not self.implementation_cache_dir:
            return
        
        cache_path = Path(self.implementation_cache_dir) / f"{algorithm_id}_{language}.py"
        
        with open(cache_path, 'w') as f:
            f.write(implementation)