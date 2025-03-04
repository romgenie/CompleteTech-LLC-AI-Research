"""
Text Processor for handling plain text documents.

This module provides the TextProcessor class that cleans and segments
plain text content for knowledge extraction.
"""

import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class TextProcessor:
    """
    Processor for plain text documents that cleans and segments content.
    
    This class handles the cleaning and segmentation of plain text for
    knowledge extraction, identifying sections, paragraphs, and other
    meaningful segments.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the text processor.
        
        Args:
            config: Configuration dictionary with text processing settings.
        """
        self.config = config
        self.segment_min_length = config.get('segment_min_length', 100)
        self.segment_max_length = config.get('segment_max_length', 1000)
    
    def process(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a text document.
        
        Args:
            document: The document dictionary containing text content.
            
        Returns:
            The processed document with cleaned text and segments.
        """
        logger.info(f"Processing text document: {document.get('id', 'unknown')}")
        
        # Get text content
        content = document.get('content')
        if not content:
            logger.warning("Text document has no content")
            return document
        
        # If content is bytes, convert to string
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='replace')
        
        # Clean text
        clean_text = self._clean_text(content)
        
        # Try to extract metadata
        metadata = self._extract_metadata(clean_text)
        
        # Segment the text
        segments = self._segment_text(clean_text)
        
        # Create the processed document
        processed_doc = document.copy()
        processed_doc.update({
            'extracted_text': clean_text,
            'metadata': metadata,
            'segments': segments
        })
        
        return processed_doc
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text content.
        
        Args:
            text: The text content to clean.
            
        Returns:
            Cleaned text.
        """
        # Replace tabs with spaces
        cleaned = text.replace('\\t', ' ')
        
        # Normalize newlines
        cleaned = cleaned.replace('\\r\\n', '\\n').replace('\\r', '\\n')
        
        # Remove control characters
        cleaned = re.sub(r'[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f-\\x9f]', '', cleaned)
        
        # Remove multiple spaces
        cleaned = re.sub(r' +', ' ', cleaned)
        
        # Remove empty lines
        cleaned = re.sub(r'\\n\\s*\\n', '\\n\\n', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        Try to extract metadata from plain text.
        
        Args:
            text: The text content.
            
        Returns:
            Dictionary with metadata.
        """
        metadata = {}
        
        # Try to find title (first line ending with newline)
        title_match = re.match(r'^([^\\n]+)\\n', text)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Try to find author (look for "by" or "author" in the first few lines)
        author_match = re.search(r'(?:by|author)[:\\s]+([^\\n,]+)', text[:500], re.IGNORECASE)
        if author_match:
            metadata['author'] = author_match.group(1).strip()
        
        # Try to find date (look for date patterns in the first few lines)
        date_patterns = [
            r'(\d{1,2}[/\\-]\d{1,2}[/\\-]\d{2,4})',  # MM/DD/YYYY or similar
            r'(\d{4}[/\\-]\d{1,2}[/\\-]\d{1,2})',  # YYYY/MM/DD or similar
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}'  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text[:500])
            if date_match:
                metadata['date'] = date_match.group(0)
                break
        
        return metadata
    
    def _segment_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text into meaningful chunks for knowledge extraction.
        
        Args:
            text: The text to segment.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Skip empty text
        if not text:
            return segments
        
        # First try to segment by markdown-style headers
        markdown_segments = self._segment_by_markdown_headers(text)
        
        if markdown_segments:
            # If markdown headers found, use those
            segments = markdown_segments
        else:
            # Next try to segment by uppercase headers
            uppercase_segments = self._segment_by_uppercase_headers(text)
            
            if uppercase_segments:
                # If uppercase headers found, use those
                segments = uppercase_segments
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
    
    def _segment_by_markdown_headers(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by markdown-style headers (# Header, ## Subheader, etc.).
        
        Args:
            text: The text to segment.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Pattern for Markdown-style headers
        header_pattern = re.compile(r'^(#+\s+[^\\n]+)', re.MULTILINE)
        
        # Find all headers
        headers = [(m.group(1), m.start()) for m in header_pattern.finditer(text)]
        
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
                    'section_header': header.strip('#').strip(),
                    'content': section_text
                }
                segments.append(segment)
        
        return segments
    
    def _segment_by_uppercase_headers(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by uppercase headers.
        
        Args:
            text: The text to segment.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Pattern for uppercase headers (at least 3 uppercase letters, possibly with numbers)
        header_pattern = re.compile(r'^([A-Z][A-Z0-9 ]{2,}[A-Z][A-Z0-9 ]*?)$', re.MULTILINE)
        
        # Find all headers
        headers = [(m.group(1), m.start()) for m in header_pattern.finditer(text)]
        
        # If no headers found or too many (probably not headers), return empty list
        if not headers or len(headers) > 20:  # Arbitrary threshold
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