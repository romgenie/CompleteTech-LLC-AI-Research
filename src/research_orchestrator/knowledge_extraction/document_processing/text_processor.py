"""
Text Processor for the Knowledge Extraction Pipeline.

This module provides the TextProcessor class that handles plain text documents,
performing operations like normalization, cleaning, and segmentation.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Processor for plain text documents.
    
    This class handles the processing of plain text documents, including
    normalization, cleaning, and segmentation into logical chunks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the text processor.
        
        Args:
            config: Configuration dictionary with processing settings
        """
        self.config = config or {}
        
        # Default configuration
        self.min_line_length = self.config.get("min_line_length", 5)
        self.segment_by_paragraphs = self.config.get("segment_by_paragraphs", True)
        self.normalize_whitespace = self.config.get("normalize_whitespace", True)
        self.remove_urls = self.config.get("remove_urls", False)
        self.remove_emails = self.config.get("remove_emails", False)
    
    def process(self, content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process a text document.
        
        Args:
            content: Text content to process
            
        Returns:
            Tuple of (processed_text, metadata)
        """
        # Clean and normalize the text
        cleaned_text = self._clean_text(content)
        
        # Count basic statistics
        char_count = len(cleaned_text)
        word_count = len(cleaned_text.split())
        lines = cleaned_text.splitlines()
        line_count = len(lines)
        
        # Create metadata
        metadata = {
            "char_count": char_count,
            "word_count": word_count,
            "line_count": line_count,
            "avg_line_length": char_count / max(line_count, 1),
            "avg_word_length": char_count / max(word_count, 1)
        }
        
        # Segment the text if requested
        if self.segment_by_paragraphs and cleaned_text:
            segments = self._segment_by_paragraphs(cleaned_text)
            metadata["segments"] = segments
        
        return cleaned_text, metadata
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Trim whitespace
        cleaned = text.strip()
        
        # Normalize whitespace if configured
        if self.normalize_whitespace:
            # Replace multiple spaces with a single space
            cleaned = re.sub(r'\s+', ' ', cleaned)
            # Normalize newlines
            cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        # Remove URLs if configured
        if self.remove_urls:
            cleaned = re.sub(r'https?://\S+', '', cleaned)
        
        # Remove emails if configured
        if self.remove_emails:
            cleaned = re.sub(r'\S+@\S+\.\S+', '', cleaned)
        
        return cleaned
    
    def _segment_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text into paragraphs.
        
        Args:
            text: Text to segment
            
        Returns:
            List of segment dictionaries
        """
        # Split by double newlines to get paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Filter out empty paragraphs and create segment dictionaries
        segments = []
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if len(para) >= self.min_line_length:
                segment = {
                    "id": f"p{i}",
                    "type": "paragraph",
                    "content": para,
                    "start_char": text.find(para),
                    "end_char": text.find(para) + len(para),
                    "word_count": len(para.split())
                }
                segments.append(segment)
        
        return segments