"""
Document Processor for the Knowledge Extraction Pipeline.

This module provides the main DocumentProcessor class that coordinates
processing of different document types and manages the pipeline for
document segmentation and preparation.
"""

import logging
import mimetypes
from typing import Dict, List, Any, Optional, Union, BinaryIO, TextIO
import os
from datetime import datetime
import tempfile

logger = logging.getLogger(__name__)


class Document:
    """
    Representation of a processed document.
    
    This class encapsulates document content and metadata after processing,
    providing structured access to document information and segments.
    """
    
    def __init__(
        self,
        content: str,
        document_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        path: Optional[str] = None,
        segments: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize a Document object.
        
        Args:
            content: The document's text content
            document_type: Type of document (text, pdf, html, etc.)
            metadata: Additional metadata about the document
            path: Path to the source file, if applicable
            segments: List of document segments, if pre-processed
        """
        self.content = content
        self.document_type = document_type
        self.metadata = metadata or {}
        self.path = path
        self.segments = segments or []
        self.processed_at = datetime.now().isoformat()
    
    def get_text(self) -> str:
        """
        Get the full text content of the document.
        
        Returns:
            Document text content
        """
        return self.content
    
    def get_segments(self) -> List[Dict[str, Any]]:
        """
        Get the document segments.
        
        Returns:
            List of document segments
        """
        return self.segments
    
    def add_segment(self, segment: Dict[str, Any]) -> None:
        """
        Add a segment to the document.
        
        Args:
            segment: The segment to add
        """
        self.segments.append(segment)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert document to a dictionary.
        
        Returns:
            Dictionary representation of the document
        """
        return {
            "content": self.content,
            "document_type": self.document_type,
            "metadata": self.metadata,
            "path": self.path,
            "segments": self.segments,
            "processed_at": self.processed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """
        Create a document from a dictionary.
        
        Args:
            data: Dictionary representation of a document
            
        Returns:
            Document object
        """
        return cls(
            content=data.get("content", ""),
            document_type=data.get("document_type", "text"),
            metadata=data.get("metadata", {}),
            path=data.get("path"),
            segments=data.get("segments", [])
        )


class DocumentProcessor:
    """
    Main document processing coordinator that handles different document types.
    
    This class manages the document processing pipeline, dispatching to specialized
    processors based on document type and coordinating the segmentation and
    cleaning operations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the document processor.
        
        Args:
            config: Configuration dictionary with processing settings.
        """
        self.config = config or {}
        self._initialize_processors()
        
    def _initialize_processors(self):
        """
        Initialize the specialized document processors.
        """
        # These will be initialized on-demand to avoid unnecessary imports
        self._pdf_processor = None
        self._html_processor = None
        self._text_processor = None
    
    def process_document(self, document_path: str) -> Document:
        """
        Process a document from a file path.
        
        Args:
            document_path: Path to the document file
            
        Returns:
            Processed Document object
        """
        logger.info(f"Processing document: {document_path}")
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(document_path)
        if content_type is None:
            # Try to guess based on extension
            ext = os.path.splitext(document_path)[1].lower()
            if ext == '.pdf':
                content_type = 'application/pdf'
            elif ext in ['.html', '.htm']:
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
        
        # Process based on content type
        if 'pdf' in content_type:
            return self._process_pdf(document_path)
        elif 'html' in content_type:
            return self._process_html(document_path)
        else:
            # Default to text processing
            return self._process_text(document_path)
    
    def process_text_content(
        self, 
        text: str, 
        document_id: str = "text_content",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Process text content directly.
        
        Args:
            text: The text content to process
            document_id: Identifier for the document
            metadata: Additional metadata
            
        Returns:
            Processed Document object
        """
        logger.info(f"Processing text content with ID: {document_id}")
        
        # Create a temporary file to process
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(text)
            temp_path = temp_file.name
        
        try:
            # Process the temporary file
            document = self._process_text(temp_path)
            
            # Update document metadata
            document.metadata.update(metadata or {})
            document.metadata["document_id"] = document_id
            
            return document
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def process_url(self, url: str) -> Document:
        """
        Process a document from a URL.
        
        Args:
            url: The URL of the document to process
            
        Returns:
            Processed Document object
        """
        logger.info(f"Processing document from URL: {url}")
        
        # Fetch the content
        import requests
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        # Determine content type
        content_type = response.headers.get('Content-Type', 'text/plain')
        
        # Create a temporary file
        suffix = '.pdf' if 'pdf' in content_type else '.html' if 'html' in content_type else '.txt'
        mode = 'wb' if 'pdf' in content_type else 'w'
        
        with tempfile.NamedTemporaryFile(mode=mode, suffix=suffix, delete=False) as temp_file:
            if mode == 'wb':
                temp_file.write(response.content)
            else:
                temp_file.write(response.text)
            temp_path = temp_file.name
        
        try:
            # Process the temporary file
            document = self.process_document(temp_path)
            
            # Add URL metadata
            document.metadata["url"] = url
            document.metadata["headers"] = dict(response.headers)
            
            return document
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _process_pdf(self, file_path: str) -> Document:
        """
        Process a PDF document.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Processed Document object
        """
        # Lazy load the PDF processor
        if self._pdf_processor is None:
            try:
                from .pdf_processor import PDFProcessor
                self._pdf_processor = PDFProcessor(self.config.get('pdf', {}))
            except ImportError:
                logger.warning("PDF processor not available, falling back to text processor")
                return self._process_text(file_path)
        
        # Read the file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Process the PDF content
        text_content, metadata = self._pdf_processor.process(content)
        
        # Create and return the document
        document = Document(
            content=text_content,
            document_type="pdf",
            metadata=metadata,
            path=file_path
        )
        
        return document
    
    def _process_html(self, file_path: str) -> Document:
        """
        Process an HTML document.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            Processed Document object
        """
        # Lazy load the HTML processor
        if self._html_processor is None:
            try:
                from .html_processor import HTMLProcessor
                self._html_processor = HTMLProcessor(self.config.get('html', {}))
            except ImportError:
                logger.warning("HTML processor not available, falling back to text processor")
                return self._process_text(file_path)
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Process the HTML content
        text_content, metadata = self._html_processor.process(content)
        
        # Create and return the document
        document = Document(
            content=text_content,
            document_type="html",
            metadata=metadata,
            path=file_path
        )
        
        return document
    
    def _process_text(self, file_path: str) -> Document:
        """
        Process a text document.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Processed Document object
        """
        # Lazy load the text processor
        if self._text_processor is None:
            try:
                from .text_processor import TextProcessor
                self._text_processor = TextProcessor(self.config.get('text', {}))
            except ImportError:
                # Create a simple text processor if import fails
                self._text_processor = SimpleTextProcessor()
        
        # Read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Process the text content
        text_content, metadata = self._text_processor.process(content)
        
        # Create and return the document
        document = Document(
            content=text_content,
            document_type="text",
            metadata=metadata,
            path=file_path
        )
        
        return document


class SimpleTextProcessor:
    """
    Simple text processor for when the specialized processor is not available.
    """
    
    def process(self, content: str) -> tuple:
        """
        Process text content.
        
        Args:
            content: The text content to process
            
        Returns:
            Tuple of (processed_text, metadata)
        """
        # Simple processing - just trim whitespace
        processed_text = content.strip()
        
        # Create basic metadata
        metadata = {
            "char_count": len(processed_text),
            "word_count": len(processed_text.split()),
            "line_count": len(processed_text.splitlines())
        }
        
        return processed_text, metadata