"""
PDF Processor for the Knowledge Extraction Pipeline.

This module provides the PDFProcessor class that handles PDF documents,
extracting text content and metadata from them.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, BinaryIO
import re
import io

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Processor for PDF documents.
    
    This class handles the processing of PDF documents, extracting text content,
    metadata, and organizing content into logical sections.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PDF processor.
        
        Args:
            config: Configuration dictionary with processing settings
        """
        self.config = config or {}
        
        # Default configuration
        self.extract_metadata = self.config.get("extract_metadata", True)
        self.segment_by_pages = self.config.get("segment_by_pages", True)
        self.segment_by_headers = self.config.get("segment_by_headers", False)
        self.ocr_enabled = self.config.get("ocr_enabled", False)
        self.tables_enabled = self.config.get("tables_enabled", False)
        self.page_range = self.config.get("page_range", None)  # (start, end) or None for all
    
    def process(self, content: bytes) -> Tuple[str, Dict[str, Any]]:
        """
        Process a PDF document.
        
        Args:
            content: PDF content as bytes
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            import PyPDF2
        except ImportError:
            logger.error("PyPDF2 library not found. Please install it to process PDF documents.")
            return "", {"error": "PyPDF2 library not found"}
        
        # Open the PDF from binary content
        pdf_file = io.BytesIO(content)
        
        try:
            # Parse the PDF
            with PyPDF2.PdfReader(pdf_file) as pdf_reader:
                # Extract metadata if configured
                metadata = self._extract_metadata(pdf_reader) if self.extract_metadata else {}
                
                # Extract text from pages
                text, page_texts = self._extract_text(pdf_reader)
                
                # Add page segments if configured
                if self.segment_by_pages:
                    metadata["segments"] = self._create_page_segments(page_texts)
                
                # Add basic statistics
                char_count = len(text)
                word_count = len(text.split())
                metadata.update({
                    "char_count": char_count,
                    "word_count": word_count,
                    "page_count": len(pdf_reader.pages)
                })
                
                return text, metadata
                
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return "", {"error": str(e)}
    
    def _extract_metadata(self, pdf_reader) -> Dict[str, Any]:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_reader: PyPDF2 PdfReader object
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {}
        
        # Extract document information
        if pdf_reader.metadata:
            # Convert from PyPDF2's metadata format
            doc_info = {}
            for key, value in pdf_reader.metadata.items():
                # Skip empty values
                if value:
                    # Remove the leading '/' from keys
                    clean_key = key[1:] if key.startswith('/') else key
                    doc_info[clean_key] = value
            
            metadata["document_info"] = doc_info
        
        return metadata
    
    def _extract_text(self, pdf_reader) -> Tuple[str, List[str]]:
        """
        Extract text content from PDF pages.
        
        Args:
            pdf_reader: PyPDF2 PdfReader object
            
        Returns:
            Tuple of (full_text, list_of_page_texts)
        """
        page_texts = []
        
        # Determine page range
        start_page, end_page = 0, len(pdf_reader.pages)
        if self.page_range:
            start_page = max(0, self.page_range[0])
            end_page = min(len(pdf_reader.pages), self.page_range[1])
        
        # Extract text from each page
        for i in range(start_page, end_page):
            try:
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                
                # Clean up the text
                page_text = self._clean_text(page_text)
                
                page_texts.append(page_text)
            except Exception as e:
                logger.warning(f"Error extracting text from page {i}: {e}")
                page_texts.append("")
        
        # Combine all pages
        full_text = "\n\n".join(page_texts)
        
        return full_text, page_texts
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content from PDF.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text).strip()
        
        # Fix common OCR issues if needed
        # ...
        
        return cleaned
    
    def _create_page_segments(self, page_texts: List[str]) -> List[Dict[str, Any]]:
        """
        Create segments from PDF pages.
        
        Args:
            page_texts: List of text content for each page
            
        Returns:
            List of segment dictionaries
        """
        segments = []
        
        for i, page_text in enumerate(page_texts):
            if page_text.strip():  # Skip empty pages
                segment = {
                    "id": f"page{i+1}",
                    "type": "page",
                    "page_number": i + 1,
                    "content": page_text,
                    "word_count": len(page_text.split())
                }
                segments.append(segment)
        
        return segments
    
    def _detect_headers(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect potential headers in text based on formatting.
        
        Args:
            text: Text to analyze for headers
            
        Returns:
            List of header dictionaries
        """
        # This is a simplistic approach - in reality, header detection in PDFs
        # often requires more sophisticated analysis of font sizes, positioning, etc.
        
        # Look for lines that might be headers (all caps, short, etc.)
        headers = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line is potential header (simple heuristics)
            is_header = False
            
            # Short line (less than 7 words)
            if 1 < len(line.split()) < 7:
                is_header = True
            
            # All caps or title case
            if line.isupper() or line.istitle():
                is_header = True
            
            # Ends with a colon
            if line.endswith(':'):
                is_header = True
            
            # Numeric prefix like "1. Introduction"
            if re.match(r'^\d+\.?\d*\s+\w+', line):
                is_header = True
            
            if is_header:
                headers.append({
                    "id": f"h{i}",
                    "text": line,
                    "line_number": i
                })
        
        return headers