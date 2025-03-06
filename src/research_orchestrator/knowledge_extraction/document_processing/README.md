# Document Processing Module

The Document Processing module is a core component of the Knowledge Extraction Pipeline, responsible for handling various document formats and preparing them for entity and relationship extraction.

## Overview

This module provides a unified interface for processing different document types (text, PDF, HTML) and extracting their content in a standardized format. It handles various encoding issues, document structures, and edge cases to ensure robust processing across a wide range of inputs.

## Components

### DocumentProcessor

The main coordinator class that handles document processing pipeline. It:

- Detects document types based on file extensions or content inspection
- Coordinates specialized processors for different document formats
- Manages the processing workflow with proper error handling
- Provides a consistent interface for document processing

### Document

A data class representing a processed document with:

- Extracted text content
- Document type information
- Metadata about the document
- Optional segmentation for structured documents

### Specialized Processors

- **TextProcessor**: Handles plain text documents
- **PDFProcessor**: Extracts text from PDF files
- **HTMLProcessor**: Processes HTML documents and extracts clean text

## Usage Examples

### Processing a file:

```python
from research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor

processor = DocumentProcessor()
document = processor.process_document("/path/to/document.pdf")
print(f"Document content: {document.get('extracted_text')[:100]}...")
```

### Processing raw text:

```python
processor = DocumentProcessor()
document = processor.process_text("This is sample text content for processing.")
print(f"Processed {document.document_type} with {len(document.content)} characters")
```

### Processing from a URL:

```python
processor = DocumentProcessor()
document = processor.process_url("https://example.com/article.html")
print(f"Downloaded and processed document with {len(document.get('segments', []))} segments")
```

## Error Handling

The module implements comprehensive error handling for various failure scenarios:

- File access errors (missing files, permission issues)
- Encoding problems (handles various text encodings)
- Content size limits (prevents processing extremely large documents)
- Network errors (timeouts, connection issues when fetching URLs)
- Format-specific errors (malformed PDFs, invalid HTML)

All errors are gracefully handled, logged with appropriate context, and the module attempts to provide useful fallback behavior to prevent pipeline failures.

## Configuration

The DocumentProcessor accepts an optional configuration dictionary that can customize the behavior of each specialized processor:

```python
config = {
    "pdf": {
        "extract_images": False,
        "max_pages": 100
    },
    "html": {
        "extract_metadata": True,
        "include_links": True
    },
    "text": {
        "encoding": "utf-8",
        "line_ending": "\n"
    }
}
processor = DocumentProcessor(config)
```

## Testing

The module includes comprehensive tests:

- Unit tests for individual processors
- Integration tests for the complete pipeline
- Edge case tests for error handling
- Performance benchmarks for processing efficiency

## Dependencies

- PDF processing: PyPDF2 or pdfplumber (optional)
- HTML processing: BeautifulSoup4 (optional)
- URL fetching: requests library (optional)

The module will work even if optional dependencies are not installed, falling back to more basic processing capabilities.