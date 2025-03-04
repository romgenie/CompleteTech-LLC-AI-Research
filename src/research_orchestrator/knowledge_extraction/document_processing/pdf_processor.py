"""
PDF Processor for handling PDF documents.

This module provides the PDFProcessor class that extracts text content from
PDF documents and segments it for knowledge extraction.
"""

import logging
import io
from typing import Dict, List, Any, Optional, BinaryIO
import re

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Processor for PDF documents that extracts and segments text content.
    
    This class handles the extraction of text from PDF files, including
    handling document structure, tables, figures, and references.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the PDF processor.
        
        Args:
            config: Configuration dictionary with PDF processing settings.
        """
        self.config = config
        self.segment_min_length = config.get('segment_min_length', 100)
        self.segment_max_length = config.get('segment_max_length', 1000)
    
    def process(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a PDF document.
        
        Args:
            document: The document dictionary containing PDF content.
            
        Returns:
            The processed document with extracted text and segments.
        """
        logger.info(f"Processing PDF document: {document.get('id', 'unknown')}")
        
        # Get PDF content
        content = document.get('content')
        if not content:
            logger.warning("PDF document has no content")
            return document
        
        # Extract text from PDF
        text = self._extract_text(content)
        
        # Extract metadata
        metadata = self._extract_metadata(content)
        
        # Segment the text
        segments = self._segment_text(text)
        
        # Create the processed document
        processed_doc = document.copy()
        processed_doc.update({
            'extracted_text': text,
            'metadata': metadata,
            'segments': segments
        })
        
        return processed_doc
    
    def _extract_text(self, content: Any) -> str:
        """
        Extract text from PDF content.
        
        Args:
            content: The PDF content (bytes or BytesIO).
            
        Returns:
            The extracted text.
        """
        try:
            # Try to use PyPDF2 first (simpler, more common)
            return self._extract_with_pypdf2(content)
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
            try:
                # Fall back to pdfplumber
                return self._extract_with_pdfplumber(content)
            except Exception as e:
                logger.error(f"PDF text extraction failed: {str(e)}")
                # Return empty string on failure
                return ""
    
    def _extract_with_pypdf2(self, content: Any) -> str:
        """
        Extract text using PyPDF2.
        
        Args:
            content: The PDF content.
            
        Returns:
            The extracted text.
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            logger.warning("PyPDF2 not available, skipping this extraction method")
            raise ImportError("PyPDF2 not installed")
        
        # Convert content to BytesIO if it's bytes
        if isinstance(content, bytes):
            content = io.BytesIO(content)
        
        # Read PDF
        reader = PdfReader(content)
        
        # Extract text from all pages
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\\n\\n"
        
        return text
    
    def _extract_with_pdfplumber(self, content: Any) -> str:
        """
        Extract text using pdfplumber.
        
        Args:
            content: The PDF content.
            
        Returns:
            The extracted text.
        """
        try:
            import pdfplumber
        except ImportError:
            logger.warning("pdfplumber not available, skipping this extraction method")
            raise ImportError("pdfplumber not installed")
        
        # Convert content to BytesIO if it's bytes
        if isinstance(content, bytes):
            content = io.BytesIO(content)
        
        # Read PDF
        with pdfplumber.open(content) as pdf:
            # Extract text from all pages
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\\n\\n"
        
        return text
    
    def _extract_metadata(self, content: Any) -> Dict[str, Any]:
        """
        Extract metadata from PDF content.
        
        Args:
            content: The PDF content.
            
        Returns:
            Dictionary with metadata.
        """
        metadata = {}
        
        try:
            from PyPDF2 import PdfReader
            
            # Convert content to BytesIO if it's bytes
            if isinstance(content, bytes):
                content = io.BytesIO(content)
            
            # Read PDF
            reader = PdfReader(content)
            
            # Extract metadata
            info = reader.metadata
            
            if info:
                # Convert metadata to regular dict with string values
                for key, value in info.items():
                    if key.startswith('/'):
                        key = key[1:]
                    metadata[key] = str(value)
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {str(e)}")
        
        return metadata
    
    def _segment_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text into meaningful chunks for knowledge extraction.
        
        Args:
            text: The extracted text.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Skip empty text
        if not text:
            return segments
        
        # First, try to segment by sections
        section_segments = self._segment_by_sections(text)
        
        if section_segments:
            # If we found sections, use those
            segments = section_segments
        else:
            # Otherwise, segment by paragraphs
            segments = self._segment_by_paragraphs(text)
        
        # Apply length constraints and further segmentation if needed
        processed_segments = []
        for segment in segments:
            content = segment['content']
            
            # Skip short segments
            if len(content) < self.segment_min_length:
                continue
            
            # Further segment long content
            if len(content) > self.segment_max_length:
                # Split by sentences while respecting max length
                sub_segments = self._split_by_length(content, self.segment_max_length)
                
                # Add each sub-segment with the same metadata
                for i, sub_content in enumerate(sub_segments):
                    if len(sub_content) >= self.segment_min_length:
                        sub_segment = segment.copy()
                        sub_segment['content'] = sub_content
                        sub_segment['segment_id'] = f"{segment.get('segment_id', 'seg')}.{i+1}"
                        processed_segments.append(sub_segment)
            else:
                # Add segment as is
                processed_segments.append(segment)
        
        # Ensure all segments have IDs
        for i, segment in enumerate(processed_segments):
            if 'segment_id' not in segment:
                segment['segment_id'] = f"segment_{i+1}"
        
        return processed_segments
    
    def _segment_by_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by identified sections.
        
        Args:
            text: The text to segment.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Pattern for section headers (e.g., "1. Introduction", "II. Methods", etc.)
        section_patterns = [
            r'^\s*(\d+\.\s+[A-Z][^\\n]+)',  # Numbered sections (1. Introduction)
            r'^\s*([IVXLCDM]+\.\s+[A-Z][^\\n]+)',  # Roman numeral sections (II. Methods)
            r'^\s*([A-Z][A-Z0-9\s]+:)',  # All-caps sections (INTRODUCTION:)
            r'^\s*(#+\s+[A-Z][^\\n]+)'  # Markdown-style headers (# Introduction)
        ]
        
        # Compile patterns
        section_regexes = [re.compile(pattern, re.MULTILINE) for pattern in section_patterns]
        
        # Find all potential section headers
        headers = []
        for regex in section_regexes:
            headers.extend([(m.group(1), m.start()) for m in regex.finditer(text)])
        
        # Sort headers by position in text
        headers.sort(key=lambda x: x[1])
        
        # If no headers found, return empty list
        if not headers:
            return []
        
        # Extract sections
        for i, (header, start_pos) in enumerate(headers):
            # Determine section end
            if i < len(headers) - 1:
                end_pos = headers[i+1][1]
            else:
                end_pos = len(text)
            
            # Extract section content
            section_text = text[start_pos:end_pos].strip()
            
            # Create segment
            if section_text:
                segment = {
                    'segment_id': f"section_{i+1}",
                    'segment_type': 'section',
                    'section_header': header.strip(),
                    'content': section_text
                }
                segments.append(segment)
        
        return segments
    
    def _segment_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by paragraphs.
        
        Args:
            text: The text to segment.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\\n\\s*\\n', text)
        
        for i, paragraph in enumerate(paragraphs):
            # Clean and skip empty paragraphs
            content = paragraph.strip()
            if not content:
                continue
            
            # Create segment
            segment = {
                'segment_id': f"paragraph_{i+1}",
                'segment_type': 'paragraph',
                'content': content
            }
            segments.append(segment)
        
        return segments
    
    def _split_by_length(self, text: str, max_length: int) -> List[str]:
        """
        Split text by sentences while respecting maximum length.
        
        Args:
            text: The text to split.
            max_length: Maximum length for each segment.
            
        Returns:
            List of text segments.
        """
        segments = []
        
        # Pattern for sentence endings
        sentence_end = re.compile(r'(?<=[.!?])\\s+')
        
        # Split by sentences
        sentences = sentence_end.split(text)
        
        current_segment = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed max length and we already have content,
            # finalize the current segment and start a new one
            if current_segment and len(current_segment) + len(sentence) > max_length:
                segments.append(current_segment.strip())
                current_segment = sentence
            else:
                current_segment += " " + sentence if current_segment else sentence
        
        # Add the last segment if it has content
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments