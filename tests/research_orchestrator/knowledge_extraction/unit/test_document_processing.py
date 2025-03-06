"""
Unit tests for the document processing component.

This module contains tests for the DocumentProcessor class and related functionality,
focusing on testing document parsing, processing, and handling of different document types.
"""

import pytest

# Mark all tests in this module as unit tests and document related tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.document,
    pytest.mark.fast
]
import os
import tempfile
from unittest.mock import MagicMock, patch

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import (
    DocumentProcessor, Document, TextProcessor
)


class TestDocument:
    """Tests for the Document class."""
    
    def test_document_creation(self):
        """Test creating a Document with proper attributes."""
        doc = Document(
            content="This is test content",
            document_type="text",
            path="/path/to/doc.txt",
            metadata={"author": "Test Author", "file_size": 100}
        )
        
        assert doc.content == "This is test content"
        assert doc.document_type == "text"
        assert doc.path == "/path/to/doc.txt"
        assert doc.metadata["author"] == "Test Author"
        assert doc.metadata["file_size"] == 100
    
    def test_document_to_dict(self):
        """Test conversion of Document to dictionary."""
        doc = Document(
            content="This is test content",
            document_type="text",
            path="/path/to/doc.txt",
            metadata={"author": "Test Author", "file_size": 100}
        )
        
        doc_dict = doc.to_dict()
        
        assert doc_dict["content"] == "This is test content"
        assert doc_dict["document_type"] == "text"
        assert doc_dict["path"] == "/path/to/doc.txt"
        assert doc_dict["metadata"]["author"] == "Test Author"
        assert doc_dict["metadata"]["file_size"] == 100
    
    def test_document_from_dict(self):
        """Test creation of Document from dictionary."""
        doc_dict = {
            "content": "This is test content",
            "document_type": "text",
            "path": "/path/to/doc.txt",
            "metadata": {"author": "Test Author", "file_size": 100}
        }
        
        doc = Document.from_dict(doc_dict)
        
        assert doc.content == "This is test content"
        assert doc.document_type == "text"
        assert doc.path == "/path/to/doc.txt"
        assert doc.metadata["author"] == "Test Author"
        assert doc.metadata["file_size"] == 100
    
    def test_get_text(self):
        """Test getting text from Document."""
        doc = Document(
            content="This is test content",
            document_type="text",
            path="/path/to/doc.txt",
            metadata={}
        )
        
        assert doc.get_text() == "This is test content"
    
    def test_get_segments(self):
        """Test getting segments from Document."""
        doc = Document(
            content="This is line one.\nThis is line two.\nThis is line three.",
            document_type="text",
            path="/path/to/doc.txt",
            metadata={}
        )
        
        # Test segmentation by lines
        segments = doc.get_segments(by="line")
        assert len(segments) == 3
        assert segments[0] == "This is line one."
        assert segments[2] == "This is line three."
        
        # Test segmentation with custom separator
        segments = doc.get_segments(separator=".")
        assert len(segments) == 3
        assert segments[0] == "This is line one"
        assert segments[2] == "This is line three"


class TestDocumentProcessor:
    """Tests for the DocumentProcessor class."""
    
    def test_processor_creation(self):
        """Test creating a DocumentProcessor."""
        processor = DocumentProcessor()
        assert processor is not None
    
    def test_processor_with_config(self):
        """Test creating a DocumentProcessor with configuration."""
        config = {
            "text": {"encoding": "utf-8"},
            "html": {"extract_metadata": True},
            "pdf": {"extract_images": False}
        }
        
        processor = DocumentProcessor(config=config)
        assert processor.config == config
    
    @patch("src.research_orchestrator.knowledge_extraction.document_processing.document_processor.TextProcessor")
    def test_process_text_document(self, mock_text_processor):
        """Test processing a text document."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_text_processor.return_value = mock_instance
        mock_instance.process.return_value = Document(
            content="Processed content",
            document_type="text",
            path="/path/to/doc.txt",
            metadata={"file_size": 100}
        )
        
        # Create processor and process document
        processor = DocumentProcessor()
        result = processor.process_document("/path/to/doc.txt")
        
        # Verify results
        mock_text_processor.assert_called_once()
        mock_instance.process.assert_called_once_with("/path/to/doc.txt")
        assert result.content == "Processed content"
        assert result.document_type == "text"
    
    @patch("src.research_orchestrator.knowledge_extraction.document_processing.document_processor.HTMLProcessor")
    def test_process_html_document(self, mock_html_processor):
        """Test processing an HTML document."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_html_processor.return_value = mock_instance
        mock_instance.process.return_value = Document(
            content="Processed HTML content",
            document_type="html",
            path="/path/to/doc.html",
            metadata={"title": "Test Document"}
        )
        
        # Create processor and process document
        processor = DocumentProcessor()
        result = processor.process_document("/path/to/doc.html")
        
        # Verify results
        mock_html_processor.assert_called_once()
        mock_instance.process.assert_called_once_with("/path/to/doc.html")
        assert result.content == "Processed HTML content"
        assert result.document_type == "html"
    
    @patch("src.research_orchestrator.knowledge_extraction.document_processing.document_processor.PDFProcessor")
    def test_process_pdf_document(self, mock_pdf_processor):
        """Test processing a PDF document."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_pdf_processor.return_value = mock_instance
        mock_instance.process.return_value = Document(
            content="Processed PDF content",
            document_type="pdf",
            path="/path/to/doc.pdf",
            metadata={"pages": 10}
        )
        
        # Create processor and process document
        processor = DocumentProcessor()
        result = processor.process_document("/path/to/doc.pdf")
        
        # Verify results
        mock_pdf_processor.assert_called_once()
        mock_instance.process.assert_called_once_with("/path/to/doc.pdf")
        assert result.content == "Processed PDF content"
        assert result.document_type == "pdf"
    
    def test_process_unknown_document_type(self):
        """Test processing a document with unknown type."""
        # Create processor
        processor = DocumentProcessor()
        
        # Process document with unknown extension
        with pytest.warns(UserWarning, match="Unknown document type"):
            result = processor.process_document("/path/to/doc.unknown")
        
        # Should default to text processing
        assert result.document_type == "text"
    
    @patch("src.research_orchestrator.knowledge_extraction.document_processing.document_processor.TextProcessor")
    def test_process_text_content(self, mock_text_processor):
        """Test processing text content directly."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_text_processor.return_value = mock_instance
        mock_instance.process_content.return_value = Document(
            content="Processed content",
            document_type="text",
            path=None,
            metadata={}
        )
        
        # Create processor and process content
        processor = DocumentProcessor()
        content = "This is test content"
        result = processor.process_text(content)
        
        # Verify results
        mock_text_processor.assert_called_once()
        mock_instance.process_content.assert_called_once_with(content)
        assert result.content == "Processed content"
        assert result.document_type == "text"


class TestTextProcessor:
    """Tests for the TextProcessor class."""
    
    def test_text_processor_creation(self):
        """Test creating a TextProcessor."""
        processor = TextProcessor()
        assert processor is not None
    
    def test_text_processor_with_config(self):
        """Test creating a TextProcessor with configuration."""
        config = {"encoding": "utf-8", "max_length": 1000}
        processor = TextProcessor(config=config)
        assert processor.config == config
    
    def test_process_text_file(self):
        """Test processing a text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("This is a test document.\nIt has multiple lines.\nGPT-4 is mentioned here.")
            file_path = f.name
        
        try:
            # Process the file
            processor = TextProcessor()
            result = processor.process(file_path)
            
            # Verify results
            assert result.content == "This is a test document.\nIt has multiple lines.\nGPT-4 is mentioned here."
            assert result.document_type == "text"
            assert result.path == file_path
            assert "file_size" in result.metadata
            assert "line_count" in result.metadata
            assert result.metadata["line_count"] == 3
            assert result.metadata["file_extension"] == ".txt"
        finally:
            # Clean up the temporary file
            os.unlink(file_path)
    
    def test_process_text_content(self):
        """Test processing text content directly."""
        content = "This is test content.\nIt has multiple lines."
        
        processor = TextProcessor()
        result = processor.process_content(content)
        
        # Verify results
        assert result.content == content
        assert result.document_type == "text"
        assert result.path is None
        assert "line_count" in result.metadata
        assert result.metadata["line_count"] == 2
    
    def test_get_text_metadata(self):
        """Test extracting metadata from text content."""
        content = "This is line one.\nThis is line two.\nThis is line three."
        
        processor = TextProcessor()
        metadata = processor.get_metadata(content)
        
        # Verify metadata
        assert "line_count" in metadata
        assert metadata["line_count"] == 3
        assert "char_count" in metadata
        assert metadata["char_count"] == len(content)
        assert "word_count" in metadata
        assert metadata["word_count"] == 15  # 3 lines with 5 words each
    
    def test_process_with_custom_encoding(self):
        """Test processing a text file with custom encoding."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", encoding="utf-8", delete=False) as f:
            f.write("This is a test document with utf-8 encoding.")
            file_path = f.name
        
        try:
            # Process the file with custom encoding
            processor = TextProcessor(config={"encoding": "utf-8"})
            result = processor.process(file_path)
            
            # Verify results
            assert result.content == "This is a test document with utf-8 encoding."
            assert result.document_type == "text"
        finally:
            # Clean up the temporary file
            os.unlink(file_path)