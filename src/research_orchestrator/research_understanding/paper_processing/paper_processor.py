"""
Paper Processor module for analyzing and extracting structured information from research papers.

This module provides functionality to process research papers, extract key information,
and convert them into structured representations for further analysis.
"""

from typing import Dict, List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass
import os
import json
from pathlib import Path


class PaperFormat(Enum):
    """Enum representing supported paper formats."""
    PDF = "pdf"
    ARXIV = "arxiv"
    HTML = "html"
    PLAINTEXT = "txt"
    MARKDOWN = "md"
    LATEX = "tex"


@dataclass
class PaperSection:
    """Represents a section within a research paper."""
    title: str
    content: str
    subsections: List['PaperSection'] = None
    section_type: Optional[str] = None
    section_level: int = 0
    
    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


@dataclass
class PaperReference:
    """Represents a reference or citation in a research paper."""
    reference_id: str
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citation_count: Optional[int] = None
    raw_text: Optional[str] = None


@dataclass
class PaperFigure:
    """Represents a figure in a research paper."""
    figure_id: str
    caption: str
    content: Optional[bytes] = None
    content_path: Optional[str] = None
    description: Optional[str] = None
    referenced_by: Optional[List[str]] = None  # Section IDs that reference this figure


@dataclass
class PaperTable:
    """Represents a table in a research paper."""
    table_id: str
    caption: str
    content: List[List[str]]
    referenced_by: Optional[List[str]] = None  # Section IDs that reference this table


@dataclass
class PaperAlgorithm:
    """Represents an algorithm described in a research paper."""
    algorithm_id: str
    name: str
    description: str
    pseudocode: Optional[str] = None
    complexity: Optional[Dict[str, str]] = None  # E.g., {"time": "O(n^2)", "space": "O(n)"}
    referenced_by: Optional[List[str]] = None  # Section IDs that reference this algorithm


@dataclass
class StructuredPaper:
    """
    Structured representation of a research paper with all its components.
    """
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    sections: List[PaperSection]
    references: List[PaperReference]
    figures: Optional[List[PaperFigure]] = None
    tables: Optional[List[PaperTable]] = None
    algorithms: Optional[List[PaperAlgorithm]] = None
    keywords: Optional[List[str]] = None
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    venue: Optional[str] = None
    
    def __post_init__(self):
        if self.figures is None:
            self.figures = []
        if self.tables is None:
            self.tables = []
        if self.algorithms is None:
            self.algorithms = []
        if self.keywords is None:
            self.keywords = []


class PaperProcessor:
    """
    Main class for processing research papers and extracting structured information.
    
    This class handles various paper formats and extracts structured information
    such as sections, references, figures, tables, and algorithms.
    """
    
    def __init__(self, 
                 document_processors: Optional[Dict] = None,
                 language_model_config: Optional[Dict] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the PaperProcessor.
        
        Args:
            document_processors: Dictionary of document processors for different formats
            language_model_config: Configuration for language models used in processing
            cache_dir: Directory to cache processed papers
        """
        self.document_processors = document_processors or {}
        self.language_model_config = language_model_config or {}
        self.cache_dir = cache_dir
        
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def process_paper(self, 
                      paper_path: Union[str, Path], 
                      paper_format: Optional[PaperFormat] = None,
                      metadata: Optional[Dict[str, Any]] = None,
                      force_reprocess: bool = False) -> StructuredPaper:
        """
        Process a paper and extract structured information.
        
        Args:
            paper_path: Path to the paper file
            paper_format: Format of the paper (autodetected if None)
            metadata: Optional metadata about the paper
            force_reprocess: If True, force reprocessing even if cached
            
        Returns:
            StructuredPaper object containing structured information
        """
        paper_path = Path(paper_path)
        
        # Determine paper format if not provided
        if paper_format is None:
            paper_format = self._detect_format(paper_path)
        
        # Check cache first
        if self.cache_dir and not force_reprocess:
            cached_result = self._check_cache(paper_path)
            if cached_result:
                return cached_result
        
        # Initialize processing context
        processing_context = {
            "metadata": metadata or {},
            "paper_path": paper_path,
            "extracted_text": "",
            "sections": [],
            "references": [],
            "figures": [],
            "tables": [],
            "algorithms": []
        }
        
        # Extract text from document
        processing_context["extracted_text"] = self._extract_text(paper_path, paper_format)
        
        # Process document structure
        self._process_document_structure(processing_context)
        
        # Extract components
        self._extract_sections(processing_context)
        self._extract_references(processing_context)
        self._extract_figures(processing_context)
        self._extract_tables(processing_context)
        self._extract_algorithms(processing_context)
        
        # Post-process and create structured paper
        structured_paper = self._create_structured_paper(processing_context)
        
        # Cache result
        if self.cache_dir:
            self._cache_result(structured_paper, paper_path)
        
        return structured_paper
    
    def _detect_format(self, paper_path: Path) -> PaperFormat:
        """
        Detect the format of the paper based on file extension.
        
        Args:
            paper_path: Path to the paper file
            
        Returns:
            PaperFormat enum value
        """
        extension = paper_path.suffix.lower().lstrip('.')
        
        format_map = {
            'pdf': PaperFormat.PDF,
            'html': PaperFormat.HTML,
            'htm': PaperFormat.HTML,
            'txt': PaperFormat.PLAINTEXT,
            'md': PaperFormat.MARKDOWN,
            'tex': PaperFormat.LATEX
        }
        
        return format_map.get(extension, PaperFormat.PDF)
    
    def _check_cache(self, paper_path: Path) -> Optional[StructuredPaper]:
        """
        Check if the paper has been processed and cached already.
        
        Args:
            paper_path: Path to the paper file
            
        Returns:
            StructuredPaper if cached, None otherwise
        """
        if not self.cache_dir:
            return None
        
        # Create cache filename from paper path hash
        cache_filename = f"{hash(str(paper_path.absolute()))}.json"
        cache_path = Path(self.cache_dir) / cache_filename
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                
                # Convert cached JSON back to StructuredPaper
                return self._json_to_structured_paper(cached_data)
            except Exception:
                # If any error occurs, return None to reprocess
                return None
        
        return None
    
    def _cache_result(self, structured_paper: StructuredPaper, paper_path: Path) -> None:
        """
        Cache the processing result.
        
        Args:
            structured_paper: Processed paper structure
            paper_path: Original paper path
        """
        if not self.cache_dir:
            return
        
        # Create cache filename from paper path hash
        cache_filename = f"{hash(str(paper_path.absolute()))}.json"
        cache_path = Path(self.cache_dir) / cache_filename
        
        # Convert StructuredPaper to JSON-serializable dict
        paper_dict = self._structured_paper_to_json(structured_paper)
        
        with open(cache_path, 'w') as f:
            json.dump(paper_dict, f, indent=2)
    
    def _extract_text(self, paper_path: Path, paper_format: PaperFormat) -> str:
        """
        Extract text from paper based on its format.
        
        Args:
            paper_path: Path to the paper file
            paper_format: Format of the paper
            
        Returns:
            Extracted text content
        """
        # This would be implemented based on different document types
        # For now returning a placeholder
        return f"Extracted text from {paper_path} in format {paper_format.value}"
    
    def _process_document_structure(self, context: Dict) -> None:
        """
        Process the document structure to prepare for component extraction.
        
        Args:
            context: Processing context dictionary
        """
        # Placeholder for document structure processing
        pass
    
    def _extract_sections(self, context: Dict) -> None:
        """
        Extract sections from the paper.
        
        Args:
            context: Processing context dictionary
        """
        # Placeholder for section extraction logic
        # Would implement section boundary detection, hierarchical structure, etc.
        pass
    
    def _extract_references(self, context: Dict) -> None:
        """
        Extract references from the paper.
        
        Args:
            context: Processing context dictionary
        """
        # Placeholder for reference extraction logic
        pass
    
    def _extract_figures(self, context: Dict) -> None:
        """
        Extract figures from the paper.
        
        Args:
            context: Processing context dictionary
        """
        # Placeholder for figure extraction logic
        pass
    
    def _extract_tables(self, context: Dict) -> None:
        """
        Extract tables from the paper.
        
        Args:
            context: Processing context dictionary
        """
        # Placeholder for table extraction logic
        pass
    
    def _extract_algorithms(self, context: Dict) -> None:
        """
        Extract algorithms from the paper.
        
        Args:
            context: Processing context dictionary
        """
        # Placeholder for algorithm extraction logic
        pass
    
    def _create_structured_paper(self, context: Dict) -> StructuredPaper:
        """
        Create a structured paper object from the processing context.
        
        Args:
            context: Processing context dictionary
            
        Returns:
            StructuredPaper object
        """
        # This is a placeholder implementation
        # In a real implementation, this would use the extracted information
        # from the context to create a proper StructuredPaper instance
        
        # Using metadata if available
        metadata = context.get("metadata", {})
        
        return StructuredPaper(
            paper_id=metadata.get("paper_id", f"paper_{hash(str(context['paper_path']))}"),
            title=metadata.get("title", "Unknown Title"),
            authors=metadata.get("authors", ["Unknown Author"]),
            abstract=metadata.get("abstract", ""),
            sections=[],  # Would be populated from context["sections"]
            references=[],  # Would be populated from context["references"]
            figures=[],  # Would be populated from context["figures"]
            tables=[],  # Would be populated from context["tables"]
            algorithms=[],  # Would be populated from context["algorithms"]
            keywords=metadata.get("keywords", []),
            publication_date=metadata.get("publication_date"),
            doi=metadata.get("doi"),
            arxiv_id=metadata.get("arxiv_id"),
            venue=metadata.get("venue")
        )
    
    def _structured_paper_to_json(self, paper: StructuredPaper) -> Dict:
        """
        Convert a StructuredPaper object to a JSON-serializable dict.
        
        Args:
            paper: StructuredPaper object
            
        Returns:
            JSON-serializable dictionary
        """
        # This is a simplified implementation
        # A complete implementation would handle all nested objects
        return {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": paper.authors,
            "abstract": paper.abstract,
            # Other fields would be converted as well
        }
    
    def _json_to_structured_paper(self, data: Dict) -> StructuredPaper:
        """
        Convert JSON data back to a StructuredPaper object.
        
        Args:
            data: JSON data
            
        Returns:
            StructuredPaper object
        """
        # This is a simplified implementation
        # A complete implementation would recreate all nested objects
        return StructuredPaper(
            paper_id=data.get("paper_id", ""),
            title=data.get("title", ""),
            authors=data.get("authors", []),
            abstract=data.get("abstract", ""),
            sections=[],  # Would parse and recreate section objects
            references=[],  # Would parse and recreate reference objects
            figures=[],  # Would parse and recreate figure objects
            tables=[],  # Would parse and recreate table objects
            algorithms=[],  # Would parse and recreate algorithm objects
            keywords=data.get("keywords", []),
            publication_date=data.get("publication_date"),
            doi=data.get("doi"),
            arxiv_id=data.get("arxiv_id"),
            venue=data.get("venue")
        )


class PDFPaperProcessor:
    """
    Specialized processor for PDF research papers.
    
    Handles extraction of text and structure from PDF documents.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the PDF processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def extract_text(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        # This would use a library like PyPDF2, pdfminer, or PyMuPDF (fitz)
        # For now returning placeholder
        return f"Extracted text from PDF: {pdf_path}"
    
    def extract_structure(self, pdf_path: Union[str, Path]) -> Dict:
        """
        Extract document structure from a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with document structure information
        """
        # This would extract TOC, sections, etc.
        # For now returning placeholder
        return {
            "sections": [
                {"title": "Introduction", "level": 1, "pages": [1, 2]},
                {"title": "Methods", "level": 1, "pages": [2, 3, 4]},
                {"title": "Results", "level": 1, "pages": [4, 5, 6]},
                {"title": "Discussion", "level": 1, "pages": [6, 7, 8]},
                {"title": "Conclusion", "level": 1, "pages": [8, 9]},
                {"title": "References", "level": 1, "pages": [9, 10]}
            ]
        }
    
    def extract_figures(self, pdf_path: Union[str, Path]) -> List[Dict]:
        """
        Extract figures from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries with figure information
        """
        # This would extract images and captions
        # For now returning placeholder
        return []
    
    def extract_tables(self, pdf_path: Union[str, Path]) -> List[Dict]:
        """
        Extract tables from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries with table information
        """
        # This would extract tables
        # For now returning placeholder
        return []


class HTMLPaperProcessor:
    """
    Specialized processor for HTML research papers.
    
    Handles extraction of text and structure from HTML documents.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the HTML processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def extract_text(self, html_path: Union[str, Path]) -> str:
        """
        Extract text from an HTML file.
        
        Args:
            html_path: Path to the HTML file
            
        Returns:
            Extracted text content
        """
        # This would use a library like BeautifulSoup
        # For now returning placeholder
        return f"Extracted text from HTML: {html_path}"
    
    def extract_structure(self, html_path: Union[str, Path]) -> Dict:
        """
        Extract document structure from an HTML file.
        
        Args:
            html_path: Path to the HTML file
            
        Returns:
            Dictionary with document structure information
        """
        # This would parse HTML headings to extract TOC
        # For now returning placeholder
        return {
            "sections": [
                {"title": "Introduction", "level": 1},
                {"title": "Methods", "level": 1},
                {"title": "Results", "level": 1},
                {"title": "Discussion", "level": 1},
                {"title": "Conclusion", "level": 1},
                {"title": "References", "level": 1}
            ]
        }


class ArXivPaperProcessor:
    """
    Specialized processor for ArXiv papers.
    
    Handles fetching and processing of papers from ArXiv using the ArXiv API.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the ArXiv processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def fetch_paper(self, arxiv_id: str, save_dir: Optional[str] = None) -> Dict:
        """
        Fetch a paper from ArXiv by its ID.
        
        Args:
            arxiv_id: ArXiv ID of the paper
            save_dir: Directory to save the PDF file (if None, won't save)
            
        Returns:
            Dictionary with paper metadata and local path (if saved)
        """
        # This would use the arxiv package to fetch the paper
        # For now returning placeholder
        return {
            "arxiv_id": arxiv_id,
            "title": f"ArXiv Paper {arxiv_id}",
            "authors": ["Author 1", "Author 2"],
            "abstract": f"Abstract for paper {arxiv_id}",
            "categories": ["cs.AI", "cs.LG"],
            "published": "2023-01-01",
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            "local_path": save_dir and os.path.join(save_dir, f"{arxiv_id}.pdf")
        }