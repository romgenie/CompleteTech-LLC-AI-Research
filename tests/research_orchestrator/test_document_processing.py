"""
Tests for the Document Processing module of the Knowledge Extraction Pipeline.

This module tests the functionality of the DocumentProcessor, PDFProcessor,
HTMLProcessor, and TextProcessor.
"""

import unittest
from unittest.mock import MagicMock, patch
import io
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from src.research_orchestrator.knowledge_extraction.document_processing.text_processor import TextProcessor
from src.research_orchestrator.knowledge_extraction.document_processing.html_processor import HTMLProcessor


class TestDocumentProcessor(unittest.TestCase):
    """Tests for the DocumentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'text': {
                'segment_min_length': 50,
                'segment_max_length': 500
            },
            'html': {
                'segment_min_length': 50,
                'segment_max_length': 500
            },
            'pdf': {
                'segment_min_length': 50,
                'segment_max_length': 500
            }
        }
        
        self.processor = DocumentProcessor(self.config)
    
    def test_content_type_detection(self):
        """Test detection of content type from URL."""
        # Test PDF detection
        pdf_url = "https://example.com/document.pdf"
        content_type = self.processor._guess_content_type(pdf_url)
        self.assertEqual(content_type, "application/pdf")
        
        # Test HTML detection
        html_url = "https://example.com/page.html"
        content_type = self.processor._guess_content_type(html_url)
        self.assertEqual(content_type, "text/html")
        
        # Test text detection
        text_url = "https://example.com/file.txt"
        content_type = self.processor._guess_content_type(text_url)
        self.assertEqual(content_type, "text/plain")
        
        # Test unknown extension
        unknown_url = "https://example.com/file"
        content_type = self.processor._guess_content_type(unknown_url)
        self.assertEqual(content_type, "text/html")  # Default for unknown
    
    @patch('src.research_orchestrator.knowledge_extraction.document_processing.document_processor.DocumentProcessor._process_text')
    def test_process_document_text(self, mock_process_text):
        """Test processing text document."""
        # Set up mock
        mock_process_text.return_value = {'extracted_text': 'Processed text', 'segments': [{'content': 'Segment 1'}]}
        
        # Create a text document
        document = {
            'id': 'doc1',
            'content': 'This is a test document.',
            'content_type': 'text/plain'
        }
        
        # Process document
        result = self.processor.process_document(document)
        
        # Check result
        self.assertTrue(mock_process_text.called)
        self.assertEqual(result['id'], 'doc1')
        self.assertEqual(result['extracted_text'], 'Processed text')
        self.assertEqual(len(result['segments']), 1)
        self.assertTrue('processed' in result)
        self.assertTrue(result['processed'])
    
    @patch('src.research_orchestrator.knowledge_extraction.document_processing.document_processor.DocumentProcessor._process_html')
    def test_process_document_html(self, mock_process_html):
        """Test processing HTML document."""
        # Set up mock
        mock_process_html.return_value = {'extracted_text': 'Processed HTML', 'segments': [{'content': 'Segment 1'}]}
        
        # Create an HTML document
        document = {
            'id': 'doc2',
            'content': '<html><body>Test</body></html>',
            'content_type': 'text/html'
        }
        
        # Process document
        result = self.processor.process_document(document)
        
        # Check result
        self.assertTrue(mock_process_html.called)
        self.assertEqual(result['id'], 'doc2')
        self.assertEqual(result['extracted_text'], 'Processed HTML')
        self.assertEqual(len(result['segments']), 1)
        self.assertTrue('processed' in result)
        self.assertTrue(result['processed'])
    
    @patch('src.research_orchestrator.knowledge_extraction.document_processing.document_processor.DocumentProcessor._read_file')
    def test_process_file(self, mock_read_file):
        """Test processing a file."""
        # Set up mock
        mock_read_file.return_value = {
            'id': 'file.txt',
            'content': 'File content',
            'content_type': 'text/plain'
        }
        
        # Mock the process_document method
        self.processor.process_document = MagicMock(return_value={'processed': True})
        
        # Process file
        result = self.processor.process_file('/path/to/file.txt')
        
        # Check result
        self.assertTrue(mock_read_file.called)
        self.assertTrue(self.processor.process_document.called)
        self.assertEqual(result, {'processed': True})


class TestTextProcessor(unittest.TestCase):
    """Tests for the TextProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'segment_min_length': 10,
            'segment_max_length': 100
        }
        
        self.processor = TextProcessor(self.config)
    
    def test_clean_text(self):
        """Test text cleaning."""
        # Test with various text issues
        text = "This is a test.\\t\\tIt has tabs.\\r\\nAnd different\\r\\newlines.\\n\\n\\nAnd empty lines."
        
        cleaned = self.processor._clean_text(text)
        
        # Check result
        self.assertFalse('\\t\\t' in cleaned)
        self.assertFalse('\\r\\n' in cleaned)
        self.assertFalse('\\n\\n\\n' in cleaned)
    
    def test_segment_text(self):
        """Test text segmentation."""
        # Create a text with multiple paragraphs
        text = """# Section 1
        
        This is the first paragraph of section 1.
        
        This is the second paragraph of section 1.
        
        # Section 2
        
        This is the first paragraph of section 2.
        
        This is the second paragraph of section 2."""
        
        segments = self.processor._segment_text(text)
        
        # Check result
        self.assertGreater(len(segments), 0)
        self.assertEqual(segments[0]['segment_type'], 'section')
        self.assertEqual(segments[0]['section_header'], 'Section 1')
    
    def test_process(self):
        """Test full text processing."""
        # Create a document
        document = {
            'id': 'text1',
            'content': """# Test Document
            
            This is a test document with multiple paragraphs.
            
            ## Section 1
            
            This is section 1 content.
            
            ## Section 2
            
            This is section 2 content."""
        }
        
        # Process document
        result = self.processor.process(document)
        
        # Check result
        self.assertTrue('extracted_text' in result)
        self.assertTrue('segments' in result)
        self.assertTrue('metadata' in result)
        self.assertGreater(len(result['segments']), 0)


class TestHTMLProcessor(unittest.TestCase):
    """Tests for the HTMLProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'segment_min_length': 10,
            'segment_max_length': 100
        }
        
        self.processor = HTMLProcessor(self.config)
    
    def test_clean_html(self):
        """Test HTML cleaning."""
        # Create HTML with various elements
        html = """<!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <header>Header content</header>
            <main>
                <h1>Main Title</h1>
                <p>This is a paragraph of content.</p>
                <div>
                    <p>Another paragraph in a div.</p>
                </div>
            </main>
            <script>console.log("This should be removed");</script>
            <footer>Footer content</footer>
        </body>
        </html>"""
        
        clean_text, metadata = self.processor._clean_html(html)
        
        # Check result
        self.assertTrue('Main Title' in clean_text)
        self.assertTrue('This is a paragraph' in clean_text)
        self.assertFalse('console.log' in clean_text)
        self.assertEqual(metadata['title'], 'Test Page')
        self.assertEqual(metadata['description'], 'Test description')
    
    def test_extract_metadata(self):
        """Test metadata extraction."""
        # Create HTML with metadata
        html = """<!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
            <meta name="keywords" content="test, page, keywords">
            <meta name="author" content="Test Author">
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
            <link rel="canonical" href="https://example.com/canonical">
        </head>
        <body>
            <h1>Test</h1>
        </body>
        </html>"""
        
        metadata = self.processor._extract_metadata(html)
        
        # Check result
        self.assertTrue('open_graph' in metadata)
        self.assertEqual(metadata['open_graph']['title'], 'OG Title')
        self.assertEqual(metadata['canonical_url'], 'https://example.com/canonical')
    
    def test_process(self):
        """Test full HTML processing."""
        # Create a document
        document = {
            'id': 'html1',
            'content': """<!DOCTYPE html>
            <html>
            <head>
                <title>Test Document</title>
            </head>
            <body>
                <h1>Test Document</h1>
                <p>This is a test document with HTML content.</p>
                <h2>Section 1</h2>
                <p>This is section 1 content.</p>
                <h2>Section 2</h2>
                <p>This is section 2 content.</p>
            </body>
            </html>"""
        }
        
        # Process document
        result = self.processor.process(document)
        
        # Check result
        self.assertTrue('extracted_text' in result)
        self.assertTrue('segments' in result)
        self.assertTrue('metadata' in result)
        self.assertGreater(len(result['segments']), 0)


if __name__ == '__main__':
    unittest.main()