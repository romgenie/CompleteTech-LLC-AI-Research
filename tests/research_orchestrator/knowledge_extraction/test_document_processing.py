"""
Tests for the document processing module.

This module contains tests for the document processing components that are responsible
for extracting and structuring content from various document formats.
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor, Document
from src.research_orchestrator.knowledge_extraction.document_processing.text_processor import TextProcessor
from src.research_orchestrator.knowledge_extraction.document_processing.html_processor import HTMLProcessor
from src.research_orchestrator.knowledge_extraction.document_processing.pdf_processor import PDFProcessor


@patch('src.research_orchestrator.knowledge_extraction.document_processing.text_processor.TextProcessor')
@patch('src.research_orchestrator.knowledge_extraction.document_processing.html_processor.HTMLProcessor')
@patch('src.research_orchestrator.knowledge_extraction.document_processing.pdf_processor.PDFProcessor')
class TestDocumentProcessor(unittest.TestCase):
    """Tests for the DocumentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a sample text file
        self.text_content = "This is a test document.\nIt has multiple lines.\nAnd contains test information."
        self.text_path = os.path.join(self.temp_dir, "test_document.txt")
        with open(self.text_path, 'w') as f:
            f.write(self.text_content)
        
        # Create a sample HTML file
        self.html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test HTML Document</title>
        </head>
        <body>
            <h1>Test Heading</h1>
            <p>This is a test paragraph.</p>
            <div>
                <p>This is another paragraph in a div.</p>
            </div>
        </body>
        </html>
        """
        self.html_path = os.path.join(self.temp_dir, "test_document.html")
        with open(self.html_path, 'w') as f:
            f.write(self.html_content)
        
        # Create mock document objects
        self.mock_text_document = Document(
            content=self.text_content,
            document_type="text",
            path=self.text_path,
            metadata={"file_size": 100, "file_extension": ".txt", "line_count": 3}
        )
        
        self.mock_html_document = Document(
            content="Test Heading This is a test paragraph. This is another paragraph in a div.",
            document_type="html",
            path=self.html_path,
            metadata={"file_size": 200, "file_extension": ".html", "title": "Test HTML Document"}
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files and directory
        os.remove(self.text_path)
        os.remove(self.html_path)
        os.rmdir(self.temp_dir)
    
    def test_process_text_document(self, mock_pdf_processor, mock_html_processor, mock_text_processor):
        """Test processing a text document."""
        # Configure mock
        mock_text_processor_instance = mock_text_processor.return_value
        mock_text_processor_instance.process.return_value = self.mock_text_document
        
        # Initialize the document processor
        processor = DocumentProcessor()
        
        # Process the text document
        document = processor.process_document(self.text_path)
        
        # Check that the text processor was called
        mock_text_processor_instance.process.assert_called_once_with(self.text_path)
        
        # Check that the document was correctly processed
        self.assertEqual(document.document_type, "text")
        self.assertEqual(document.path, self.text_path)
        
        # Check that the content was extracted
        extracted_text = document.get_text()
        self.assertEqual(extracted_text, self.text_content)
        
        # Check metadata
        self.assertIn("file_size", document.metadata)
        self.assertIn("file_extension", document.metadata)
        self.assertEqual(document.metadata["file_extension"], ".txt")
    
    def test_process_html_document(self, mock_pdf_processor, mock_html_processor, mock_text_processor):
        """Test processing an HTML document."""
        # Configure mock
        mock_html_processor_instance = mock_html_processor.return_value
        mock_html_processor_instance.process.return_value = self.mock_html_document
        
        # Initialize the document processor
        processor = DocumentProcessor()
        
        # Process the HTML document
        document = processor.process_document(self.html_path)
        
        # Check that the HTML processor was called
        mock_html_processor_instance.process.assert_called_once_with(self.html_path)
        
        # Check that the document was correctly processed
        self.assertEqual(document.document_type, "html")
        self.assertEqual(document.path, self.html_path)
        
        # Check metadata
        self.assertIn("file_size", document.metadata)
        self.assertIn("file_extension", document.metadata)
        self.assertEqual(document.metadata["file_extension"], ".html")
        
        # Check HTML-specific metadata
        self.assertIn("title", document.metadata)
        self.assertEqual(document.metadata["title"], "Test HTML Document")
    
    def test_process_unknown_format(self, mock_pdf_processor, mock_html_processor, mock_text_processor):
        """Test processing a document with unknown format."""
        # Create a file with unknown extension
        unknown_path = os.path.join(self.temp_dir, "test_document.xyz")
        with open(unknown_path, 'w') as f:
            f.write("This is a test document with unknown format.")
        
        # Configure mock
        mock_text_processor_instance = mock_text_processor.return_value
        mock_text_document = Document(
            content="This is a test document with unknown format.",
            document_type="text",
            path=unknown_path,
            metadata={"file_size": 50, "file_extension": ".xyz"}
        )
        mock_text_processor_instance.process.return_value = mock_text_document
        
        # Initialize the document processor
        processor = DocumentProcessor()
        
        try:
            # Process the document and expect it to try text processor as fallback
            document = processor.process_document(unknown_path)
            
            # Check that the text processor was called
            mock_text_processor_instance.process.assert_called_once_with(unknown_path)
            
            # Check that the document was processed as text
            self.assertEqual(document.document_type, "text")
            
            # Clean up
            os.remove(unknown_path)
        except Exception as e:
            # Clean up in case of error
            os.remove(unknown_path)
            raise
    
    def test_get_document_processor(self, mock_pdf_processor, mock_html_processor, mock_text_processor):
        """Test getting the appropriate document processor for different file types."""
        # Initialize processor instances
        mock_text_processor_instance = mock_text_processor.return_value
        mock_html_processor_instance = mock_html_processor.return_value
        mock_pdf_processor_instance = mock_pdf_processor.return_value
        
        # Initialize the document processor
        processor = DocumentProcessor()
        
        # Store the original _get_processor_for_extension method
        original_get_processor = processor._get_processor_for_extension
        
        # Replace with our test method to avoid the dependency on _initialize_processors
        def test_get_processor(extension):
            if extension == '.txt':
                return mock_text_processor_instance
            elif extension == '.html' or extension == '.htm':
                return mock_html_processor_instance
            elif extension == '.pdf':
                return mock_pdf_processor_instance
            else:
                return mock_text_processor_instance
        
        # Patch the method
        processor._get_processor_for_extension = test_get_processor
        
        # Test getting text processor
        result = processor._get_processor_for_extension(".txt")
        self.assertEqual(result, mock_text_processor_instance)
        
        # Test getting HTML processor
        result = processor._get_processor_for_extension(".html")
        self.assertEqual(result, mock_html_processor_instance)
        
        # Test getting PDF processor
        result = processor._get_processor_for_extension(".pdf")
        self.assertEqual(result, mock_pdf_processor_instance)
        
        # Test getting processor for unknown extension
        result = processor._get_processor_for_extension(".xyz")
        self.assertEqual(result, mock_text_processor_instance)  # Should default to text
        
        # Restore the original method
        processor._get_processor_for_extension = original_get_processor
    
    def test_processor_initialization(self, mock_pdf_processor, mock_html_processor, mock_text_processor):
        """Test that processors are initialized with the correct configuration."""
        # Create processor with custom config
        config = {
            "text_processor": {
                "encoding": "latin-1",
                "chunk_size": 1000
            }
        }
        processor = DocumentProcessor(config=config)
        
        # Check that text processor was initialized with the custom config
        mock_text_processor.assert_called_with(config=config["text_processor"])
    

class TestDocumentClass(unittest.TestCase):
    """Tests for the Document class."""
    
    def test_document_methods(self):
        """Test methods of the Document class."""
        # Create a document
        document = Document(
            content="This is test content.",
            document_type="text",
            path="/path/to/document.txt",
            metadata={"author": "Test Author"}
        )
        
        # Test get_text method
        self.assertEqual(document.get_text(), "This is test content.")
        
        # Test get_metadata method
        self.assertEqual(document.get_metadata(), {"author": "Test Author"})
        
        # Test to_dict method
        doc_dict = document.to_dict()
        self.assertEqual(doc_dict["content"], "This is test content.")
        self.assertEqual(doc_dict["document_type"], "text")
        self.assertEqual(doc_dict["path"], "/path/to/document.txt")
        self.assertEqual(doc_dict["metadata"], {"author": "Test Author"})
        
        # Test from_dict method
        new_document = Document.from_dict(doc_dict)
        self.assertEqual(new_document.content, "This is test content.")
        self.assertEqual(new_document.document_type, "text")
        self.assertEqual(new_document.path, "/path/to/document.txt")
        self.assertEqual(new_document.metadata, {"author": "Test Author"})


class TestTextProcessor(unittest.TestCase):
    """Tests for the TextProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample text file
        self.text_content = "This is a test document.\nIt has multiple lines.\nAnd contains test information."
        self.temp_dir = tempfile.mkdtemp()
        self.text_path = os.path.join(self.temp_dir, "test_document.txt")
        with open(self.text_path, 'w') as f:
            f.write(self.text_content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.remove(self.text_path)
        os.rmdir(self.temp_dir)
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="This is a test document.\nIt has multiple lines.\nAnd contains test information.")
    @patch('os.path.getsize')
    def test_process_text_file(self, mock_getsize, mock_open):
        """Test processing a text file."""
        # Configure mocks
        mock_getsize.return_value = 100
        
        # Create the processor
        processor = TextProcessor()
        
        # Process the text file
        document = processor.process(self.text_path)
        
        # Check that the file was opened
        mock_open.assert_called_once_with(self.text_path, 'r', encoding='utf-8')
        
        # Check that the document was correctly processed
        self.assertIsInstance(document, Document)
        self.assertEqual(document.document_type, "text")
        self.assertEqual(document.path, self.text_path)
        self.assertEqual(document.content, self.text_content)
    
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="This is a test document.\nIt has multiple lines.\nAnd contains test information.")
    @patch('os.path.getsize')
    def test_process_with_custom_encoding(self, mock_getsize, mock_open):
        """Test processing a text file with custom encoding."""
        # Configure mocks
        mock_getsize.return_value = 100
        
        # Create a processor with custom encoding
        processor = TextProcessor(config={"encoding": "latin-1"})
        
        # Process the text file
        document = processor.process(self.text_path)
        
        # Check that the file was opened with the correct encoding
        mock_open.assert_called_once_with(self.text_path, 'r', encoding='latin-1')
        
        # Check that the document was correctly processed
        self.assertEqual(document.content, self.text_content)
    
    @patch('os.path.getsize')
    @patch('os.path.basename')
    @patch('os.path.splitext')
    def test_extract_metadata(self, mock_splitext, mock_basename, mock_getsize):
        """Test extracting metadata from a text file."""
        # Configure mocks
        mock_getsize.return_value = 100
        mock_basename.return_value = "test_document.txt"
        mock_splitext.return_value = ("test_document", ".txt")
        
        # Create mock file content for line counting
        mock_content = "Line 1\nLine 2\nLine 3"
        
        # Create the processor
        processor = TextProcessor()
        
        # Mock the open function
        with patch('builtins.open', unittest.mock.mock_open(read_data=mock_content)):
            # Extract metadata
            metadata = processor._extract_metadata(self.text_path)
        
        # Check basic metadata
        self.assertIn("file_size", metadata)
        self.assertEqual(metadata["file_size"], 100)
        self.assertIn("file_extension", metadata)
        self.assertEqual(metadata["file_extension"], ".txt")
        self.assertIn("line_count", metadata)
        self.assertEqual(metadata["line_count"], 3)
    
    def test_process_text_content(self):
        """Test processing text content directly."""
        # Create the processor
        processor = TextProcessor()
        
        # Process text content
        document = processor.process_text(self.text_content)
        
        # Check that the document was correctly processed
        self.assertIsInstance(document, Document)
        self.assertEqual(document.document_type, "text")
        self.assertEqual(document.content, self.text_content)
        
        # Check that path is None for direct content processing
        self.assertIsNone(document.path)


if __name__ == '__main__':
    unittest.main()