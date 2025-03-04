"""
Research Understanding Engine module.

This module provides high-level functionality for understanding research papers,
extracting structured information, and preparing for implementation.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import os
import json
import logging
import tempfile
from pathlib import Path

from .paper_processing import PaperProcessor, StructuredPaper, PaperFormat
from .algorithm_extraction import (
    AlgorithmExtractor, ExtractedAlgorithm, AlgorithmImplementationGenerator
)
from .implementation_details import (
    ImplementationDetailCollector, ImplementationDetail, CodeSnippet, 
    DatasetInfo, EvaluationMetric, HyperparameterInfo
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
    
    def process_arxiv_paper(self, 
                           arxiv_id: str, 
                           extract_algorithms: bool = True,
                           collect_implementation_details: bool = True,
                           force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process a paper from ArXiv by its ID.
        
        Args:
            arxiv_id: ArXiv ID of the paper
            extract_algorithms: Whether to extract algorithms
            collect_implementation_details: Whether to collect implementation details
            force_reprocess: If True, force reprocessing even if cached
            
        Returns:
            Dictionary containing structured paper and extracted information
        """
        try:
            # Import arxiv library
            import arxiv
        except ImportError:
            logger.error("The arxiv library is required to process ArXiv papers. Install it with: pip install arxiv")
            raise ImportError("The arxiv library is required to process ArXiv papers")
        
        # Create a temporary directory for the PDF
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Fetching paper from ArXiv: {arxiv_id}")
            
            # Search for the paper
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(search.results())
            
            # Download the paper
            pdf_path = os.path.join(temp_dir, f"{arxiv_id}.pdf")
            paper.download_pdf(filename=pdf_path)
            
            # Prepare metadata
            metadata = {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "abstract": paper.summary,
                "publication_date": paper.published.isoformat(),
                "arxiv_id": arxiv_id,
                "categories": paper.categories,
                "doi": paper.doi,
                "pdf_url": paper.pdf_url
            }
            
            # Process the paper using the downloaded PDF
            return self.process_paper(
                paper_path=pdf_path,
                paper_format=PaperFormat.PDF,
                metadata=metadata,
                extract_algorithms=extract_algorithms,
                collect_implementation_details=collect_implementation_details,
                force_reprocess=force_reprocess
            )
    
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
    
    def summarize_paper(self, paper: StructuredPaper) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a research paper.
        
        Args:
            paper: Structured paper to summarize
            
        Returns:
            Dictionary containing summary information
        """
        logger.info(f"Generating summary for paper: {paper.paper_id}")
        
        # Basic paper information
        summary = {
            "title": paper.title,
            "authors": paper.authors,
            "publication_date": paper.publication_date,
            "venue": paper.venue,
            "abstract": paper.abstract,
            "keywords": paper.keywords,
            "doi": paper.doi,
            "arxiv_id": paper.arxiv_id,
            "section_count": len(paper.sections),
            "main_sections": [section.title for section in paper.sections],
            "reference_count": len(paper.references),
            "figure_count": len(paper.figures) if paper.figures else 0,
            "table_count": len(paper.tables) if paper.tables else 0,
            "algorithm_count": len(paper.algorithms) if paper.algorithms else 0
        }
        
        # Add algorithm summaries if available
        if paper.algorithms:
            summary["algorithms"] = [{
                "name": algo.name,
                "description": algo.description[:200] + "..." if len(algo.description) > 200 else algo.description,
                "complexity": algo.complexity
            } for algo in paper.algorithms]
        
        return summary
    
    def compare_papers(self, 
                      papers: List[StructuredPaper]) -> Dict[str, Any]:
        """
        Compare multiple papers to identify similarities, differences, and relationships.
        
        Args:
            papers: List of structured papers to compare
            
        Returns:
            Dictionary containing comparison results
        """
        logger.info(f"Comparing {len(papers)} papers")
        
        comparison = {
            "papers": [{"id": paper.paper_id, "title": paper.title} for paper in papers],
            "common_authors": self._find_common_authors(papers),
            "keyword_analysis": self._analyze_keywords(papers),
            "citation_relationships": self._analyze_citations(papers),
            "methodology_comparison": self._compare_methodologies(papers),
            "algorithm_comparison": self._compare_algorithms(papers)
        }
        
        return comparison
    
    def _find_common_authors(self, papers: List[StructuredPaper]) -> List[str]:
        """Find authors common to multiple papers."""
        if not papers:
            return []
            
        # Start with the authors of the first paper
        common_authors = set(papers[0].authors)
        
        # Intersect with authors of each subsequent paper
        for paper in papers[1:]:
            common_authors = common_authors.intersection(set(paper.authors))
        
        return list(common_authors)
    
    def _analyze_keywords(self, papers: List[StructuredPaper]) -> Dict[str, Any]:
        """Analyze keywords across multiple papers."""
        if not papers:
            return {}
            
        # Collect all keywords with their frequencies
        keyword_counts = {}
        for paper in papers:
            if paper.keywords:
                for keyword in paper.keywords:
                    if keyword in keyword_counts:
                        keyword_counts[keyword] += 1
                    else:
                        keyword_counts[keyword] = 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Analyze paper-keyword relationships
        paper_keyword_matrix = {}
        for paper in papers:
            paper_keyword_matrix[paper.paper_id] = {
                keyword: keyword in (paper.keywords or [])
                for keyword, _ in sorted_keywords[:20]  # Top 20 keywords
            }
        
        return {
            "common_keywords": [k for k, v in sorted_keywords if v == len(papers)],
            "keyword_frequencies": dict(sorted_keywords),
            "paper_keyword_matrix": paper_keyword_matrix
        }
    
    def _analyze_citations(self, papers: List[StructuredPaper]) -> Dict[str, Any]:
        """Analyze citation relationships between papers."""
        citation_graph = {}
        
        # Find papers that cite other papers in the set
        for i, paper1 in enumerate(papers):
            citation_graph[paper1.paper_id] = []
            
            for j, paper2 in enumerate(papers):
                if i == j:  # Skip self
                    continue
                    
                # Check if paper1 cites paper2
                cites = False
                for ref in paper1.references:
                    # Match by title, DOI, or a combination of factors
                    if ((paper2.title and ref.title and paper2.title.lower() == ref.title.lower()) or
                        (paper2.doi and ref.doi and paper2.doi == ref.doi) or
                        (paper2.arxiv_id and "arxiv" in (ref.url or "").lower() and paper2.arxiv_id in (ref.url or ""))):
                        cites = True
                        break
                
                if cites:
                    citation_graph[paper1.paper_id].append(paper2.paper_id)
        
        return {
            "citation_graph": citation_graph
        }
    
    def _compare_methodologies(self, papers: List[StructuredPaper]) -> Dict[str, Any]:
        """Compare methodologies across papers."""
        # This is a simplified implementation
        # A real implementation would use more sophisticated analysis
        
        # Extract methodology sections
        methodology_sections = {}
        for paper in papers:
            for section in self._flatten_sections(paper.sections):
                if any(kw in section.title.lower() for kw in ["method", "approach", "model", "architecture"]):
                    if paper.paper_id not in methodology_sections:
                        methodology_sections[paper.paper_id] = []
                    methodology_sections[paper.paper_id].append({
                        "title": section.title,
                        "content_preview": section.content[:200] + "..." if len(section.content) > 200 else section.content
                    })
        
        return {
            "methodology_sections": methodology_sections
        }
    
    def _compare_algorithms(self, papers: List[StructuredPaper]) -> Dict[str, Any]:
        """Compare algorithms across papers."""
        # Collect all algorithms
        all_algorithms = []
        for paper in papers:
            if paper.algorithms:
                for algo in paper.algorithms:
                    all_algorithms.append({
                        "paper_id": paper.paper_id,
                        "algorithm_id": algo.algorithm_id,
                        "name": algo.name,
                        "complexity": algo.complexity
                    })
        
        # Find algorithms with similar names
        similar_algorithms = []
        for i, algo1 in enumerate(all_algorithms):
            for algo2 in all_algorithms[i+1:]:
                if algo1["paper_id"] != algo2["paper_id"]:  # Different papers
                    # Simple string similarity
                    name1 = algo1["name"].lower()
                    name2 = algo2["name"].lower()
                    
                    if (name1 in name2 or name2 in name1 or
                        self._name_similarity(name1, name2) > 0.7):
                        similar_algorithms.append({
                            "algorithm1": algo1,
                            "algorithm2": algo2,
                            "similarity": "name"
                        })
        
        return {
            "algorithm_count_by_paper": {
                paper.paper_id: len(paper.algorithms) if paper.algorithms else 0
                for paper in papers
            },
            "all_algorithms": all_algorithms,
            "similar_algorithms": similar_algorithms
        }
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names using Jaccard similarity.
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score between 0 and 1
        """
        # Convert to sets of characters
        set1 = set(name1)
        set2 = set(name2)
        
        # Calculate Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0
            
        return intersection / union
    
    def _flatten_sections(self, sections: List[Any]) -> List[Any]:
        """
        Flatten a hierarchical section structure.
        
        Args:
            sections: Hierarchical section list
            
        Returns:
            Flattened section list
        """
        result = []
        
        for section in sections:
            result.append(section)
            if hasattr(section, "subsections") and section.subsections:
                result.extend(self._flatten_sections(section.subsections))
        
        return result
    
    def export_to_knowledge_graph(self, 
                                paper: StructuredPaper,
                                implementation_details: Optional[ImplementationDetail] = None) -> Dict[str, Any]:
        """
        Export paper information to a format suitable for a knowledge graph.
        
        Args:
            paper: Structured paper
            implementation_details: Optional implementation details
            
        Returns:
            Dictionary containing entities and relationships for knowledge graph
        """
        logger.info(f"Exporting paper to knowledge graph format: {paper.paper_id}")
        
        entities = []
        relationships = []
        
        # Create paper entity
        paper_entity = {
            "id": paper.paper_id,
            "type": "Paper",
            "properties": {
                "title": paper.title,
                "abstract": paper.abstract,
                "publication_date": paper.publication_date,
                "venue": paper.venue,
                "doi": paper.doi,
                "arxiv_id": paper.arxiv_id
            }
        }
        entities.append(paper_entity)
        
        # Create author entities and relationships
        for i, author_name in enumerate(paper.authors):
            author_id = f"author_{paper.paper_id}_{i}"
            author_entity = {
                "id": author_id,
                "type": "Author",
                "properties": {
                    "name": author_name
                }
            }
            entities.append(author_entity)
            
            # Author relationship
            relationships.append({
                "source_id": author_id,
                "target_id": paper.paper_id,
                "type": "AUTHORED",
                "properties": {
                    "position": i
                }
            })
        
        # Add algorithms if available
        if paper.algorithms:
            for algo in paper.algorithms:
                algo_id = algo.algorithm_id
                algo_entity = {
                    "id": algo_id,
                    "type": "Algorithm",
                    "properties": {
                        "name": algo.name,
                        "description": algo.description,
                        "complexity_time": algo.complexity.get("time") if algo.complexity else None,
                        "complexity_space": algo.complexity.get("space") if algo.complexity else None
                    }
                }
                entities.append(algo_entity)
                
                # Algorithm relationship
                relationships.append({
                    "source_id": paper.paper_id,
                    "target_id": algo_id,
                    "type": "PRESENTS",
                    "properties": {}
                })
        
        # Add implementation details if available
        if implementation_details:
            # Add datasets
            for dataset in implementation_details.datasets:
                dataset_id = dataset.dataset_id
                dataset_entity = {
                    "id": dataset_id,
                    "type": "Dataset",
                    "properties": {
                        "name": dataset.name,
                        "description": dataset.description,
                        "source_url": dataset.source_url,
                        "format": dataset.format,
                        "size": dataset.size
                    }
                }
                entities.append(dataset_entity)
                
                # Dataset relationship
                relationships.append({
                    "source_id": paper.paper_id,
                    "target_id": dataset_id,
                    "type": "USES",
                    "properties": {}
                })
            
            # Add metrics
            for metric in implementation_details.metrics:
                metric_id = metric.metric_id
                metric_entity = {
                    "id": metric_id,
                    "type": "Metric",
                    "properties": {
                        "name": metric.name,
                        "description": metric.description,
                        "formula": metric.formula,
                        "higher_is_better": metric.higher_is_better
                    }
                }
                entities.append(metric_entity)
                
                # Metric relationship
                relationships.append({
                    "source_id": paper.paper_id,
                    "target_id": metric_id,
                    "type": "EVALUATES_WITH",
                    "properties": {}
                })
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
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
        
        file_extension = {"python": "py", "java": "java", "c++": "cpp", "javascript": "js"}.get(language.lower(), "txt")
        cache_path = Path(self.implementation_cache_dir) / f"{algorithm_id}.{file_extension}"
        
        with open(cache_path, 'w') as f:
            f.write(implementation)