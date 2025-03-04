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

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Main document processing coordinator that handles different document types.
    
    This class manages the document processing pipeline, dispatching to specialized
    processors based on document type and coordinating the segmentation and
    cleaning operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the document processor.
        
        Args:
            config: Configuration dictionary with processing settings.
        """
        self.config = config
        self.processors = {}
        self._initialize_processors()
        
    def _initialize_processors(self):
        """
        Initialize the specialized document processors.
        """
        # These will be initialized on-demand to avoid unnecessary imports
        self._pdf_processor = None
        self._html_processor = None
        self._text_processor = None
    
    def process_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document and prepare it for knowledge extraction.
        
        Args:
            document: A dictionary containing document details and content.
                     Must include 'content' and either 'content_type' or 'url'.
            
        Returns:
            A dictionary with the processed document including segments and metadata.
        """
        logger.info(f"Processing document: {document.get('id', 'unknown')}")
        
        # Determine document type if not specified
        if 'content_type' not in document and 'url' in document:
            document['content_type'] = self._guess_content_type(document['url'])
        
        content_type = document.get('content_type', 'text')
        
        # Process based on content type
        if 'pdf' in content_type:
            processed_doc = self._process_pdf(document)
        elif 'html' in content_type:
            processed_doc = self._process_html(document)
        else:
            # Default to text processing
            processed_doc = self._process_text(document)
        
        # Add metadata
        processed_doc.update({
            'processed': True,
            'processor_version': self.__class__.__version__ if hasattr(self.__class__, '__version__') else '0.1.0',
            'processing_timestamp': self._get_current_timestamp()
        })
        
        logger.info(f"Document processed: {len(processed_doc.get('segments', []))} segments created")
        return processed_doc
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """
        Process a document from a URL.
        
        Args:
            url: The URL of the document to process.
            
        Returns:
            A dictionary with the processed document.
        """
        # First fetch the document
        document = self._fetch_document(url)
        
        # Then process it
        return self.process_document(document)
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document from a local file.
        
        Args:
            file_path: Path to the local file.
            
        Returns:
            A dictionary with the processed document.
        """
        # Read the file and create a document dictionary
        document = self._read_file(file_path)
        
        # Then process it
        return self.process_document(document)
    
    def _process_pdf(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a PDF document.
        
        Args:
            document: The document dictionary.
            
        Returns:
            The processed document.
        """
        # Lazy load the PDF processor
        if self._pdf_processor is None:
            from research_orchestrator.knowledge_extraction.document_processing.pdf_processor import PDFProcessor
            self._pdf_processor = PDFProcessor(self.config.get('pdf', {}))
        
        return self._pdf_processor.process(document)
    
    def _process_html(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an HTML document.
        
        Args:
            document: The document dictionary.
            
        Returns:
            The processed document.
        """
        # Lazy load the HTML processor
        if self._html_processor is None:
            from research_orchestrator.knowledge_extraction.document_processing.html_processor import HTMLProcessor
            self._html_processor = HTMLProcessor(self.config.get('html', {}))
        
        return self._html_processor.process(document)
    
    def _process_text(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a text document.
        
        Args:
            document: The document dictionary.
            
        Returns:
            The processed document.
        """
        # Lazy load the text processor
        if self._text_processor is None:
            from research_orchestrator.knowledge_extraction.document_processing.text_processor import TextProcessor
            self._text_processor = TextProcessor(self.config.get('text', {}))
        
        return self._text_processor.process(document)
    
    def _guess_content_type(self, url: str) -> str:
        """
        Guess content type from URL.
        
        Args:
            url: The URL to analyze.
            
        Returns:
            The guessed content type.
        """
        # Use mimetypes to guess based on URL extension
        content_type, _ = mimetypes.guess_type(url)
        
        if content_type is None:
            # Default to text/html for unknown types
            return 'text/html'
        
        return content_type
    
    def _fetch_document(self, url: str) -> Dict[str, Any]:
        """
        Fetch a document from a URL.
        
        Args:
            url: The URL to fetch.
            
        Returns:
            A document dictionary.
        """
        import requests
        
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        # Determine content type
        content_type = response.headers.get('Content-Type', 'text/plain')
        
        # Create document dictionary
        document = {
            'id': url,
            'url': url,
            'title': url.split('/')[-1],
            'content': response.content if 'pdf' in content_type else response.text,
            'content_type': content_type,
            'headers': dict(response.headers)
        }
        
        return document
    
    def _read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a document from a local file.
        
        Args:
            file_path: Path to the local file.
            
        Returns:
            A document dictionary.
        """
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            # Try to guess based on extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.pdf':
                content_type = 'application/pdf'
            elif ext in ['.html', '.htm']:
                content_type = 'text/html'
            else:
                content_type = 'text/plain'
        
        # Read the file
        mode = 'rb' if 'pdf' in content_type else 'r'
        with open(file_path, mode) as f:
            content = f.read()
        
        # Create document dictionary
        document = {
            'id': os.path.basename(file_path),
            'file_path': file_path,
            'title': os.path.basename(file_path),
            'content': content,
            'content_type': content_type
        }
        
        return document
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            Current timestamp string.
        """
        from datetime import datetime
        return datetime.now().isoformat()