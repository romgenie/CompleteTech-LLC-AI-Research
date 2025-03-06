"""
Edge case tests for document processing.

This module contains tests for document processing edge cases and error handling.
"""

import pytest
import os
import tempfile
import io
import json

# Mark all tests in this module as edge case tests and document related tests
pytestmark = [
    pytest.mark.edge_case,
    pytest.mark.document,
    pytest.mark.medium
]

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor, Document


@pytest.mark.error
def test_nonexistent_file_handling(edge_case_document_processor, invalid_document_path):
    """Test handling of nonexistent files."""
    # Attempt to process a nonexistent file should raise an error
    with pytest.raises(FileNotFoundError):
        edge_case_document_processor.process_document(invalid_document_path)


@pytest.mark.empty
def test_empty_file_handling():
    """Test handling of empty files."""
    # Create an empty file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        file_path = f.name
    
    try:
        # Process the empty file
        processor = DocumentProcessor()
        document = processor.process_document(file_path)
        
        # Check that the document is processed correctly
        assert document.content == ""
        assert document.document_type == "text"
        assert document.path == file_path
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.empty
def test_empty_content_handling(edge_case_document_processor, empty_document):
    """Test handling of empty content."""
    # Process empty content
    result = edge_case_document_processor.process_text("")
    
    # Check that the document is processed correctly
    assert result.content == ""
    assert result.document_type == "text"
    
    # Check that we can get text and segments from an empty document
    assert empty_document.get_text() == ""
    assert empty_document.get_segments() == []


@pytest.mark.malformed
def test_malformed_html_handling(edge_case_document_processor, malformed_html_document):
    """Test handling of malformed HTML."""
    # Save the malformed HTML to a file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        f.write(malformed_html_document.content.encode('utf-8'))
        file_path = f.name
    
    try:
        # Process the malformed HTML
        document = edge_case_document_processor.process_document(file_path)
        
        # Check that the document is processed correctly
        assert document.content is not None
        assert document.document_type == "html"
        assert document.path == file_path
        
        # Check that some of the original content is preserved
        assert "Malformed HTML Example" in document.content
        assert "This is a paragraph" in document.content
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.error
def test_invalid_encoding_handling(document_with_invalid_encoding):
    """Test handling of content with invalid encoding."""
    # Process content with invalid encoding directly
    processor = DocumentProcessor()
    
    # This should not raise an error but handle it gracefully
    document = processor.process_text(document_with_invalid_encoding.content)
    
    # Check that the document is processed correctly
    assert document.content is not None
    assert document.document_type == "text"
    assert "invalid UTF-8 sequence" in document.content


@pytest.mark.large
def test_large_file_handling(edge_case_document_processor, very_large_document):
    """Test handling of very large files."""
    # Process a very large document
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        # Write 1MB of data for a more reasonable test
        f.write(very_large_document.content[:1024 * 1024].encode('utf-8'))
        file_path = f.name
    
    try:
        # Process the large file
        document = edge_case_document_processor.process_document(file_path)
        
        # Check that the document is processed correctly
        assert document.content is not None
        assert document.document_type == "text"
        assert document.path == file_path
        assert len(document.content) >= 1024 * 1024  # At least 1MB
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.special_chars
def test_special_character_handling(edge_case_document_processor, document_with_special_characters):
    """Test handling of content with special characters."""
    # Process content with special characters
    document = edge_case_document_processor.process_text(document_with_special_characters.content)
    
    # Check that the document is processed correctly
    assert document.content is not None
    assert document.document_type == "text"
    
    # Check that special characters are preserved
    assert "©®™•★☆♦♣♠♥" in document.content
    assert "😀🤣😎👍❤️🔥" in document.content
    assert "∑∫√≤≥≠" in document.content
    assert "مرحبا بالعالم" in document.content
    assert "你好，世界" in document.content
    assert "こんにちは世界" in document.content
    assert "Привет, мир" in document.content
    assert "Γειά σου Κόσμε" in document.content


@pytest.mark.invalid
def test_unsupported_file_format_handling(edge_case_document_processor):
    """Test handling of unsupported file formats."""
    # Create a file with an unsupported extension
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        f.write(b"This is a test file with an unsupported extension")
        file_path = f.name
    
    try:
        # Process the file with an unsupported extension
        # This should not raise an error but fall back to text processing
        with pytest.warns(UserWarning, match="Unknown document type"):
            document = edge_case_document_processor.process_document(file_path)
        
        # Check that the document is processed as text
        assert document.content is not None
        assert document.document_type == "text"
        assert document.path == file_path
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.code
def test_code_handling(edge_case_document_processor, document_with_code):
    """Test handling of documents containing code."""
    # Process document with code
    document = edge_case_document_processor.process_text(document_with_code.content)
    
    # Check that the document is processed correctly
    assert document.content is not None
    assert document.document_type == "text"
    
    # Check that code structure is preserved
    assert "def hello_world():" in document.content
    assert "class MyClass:" in document.content
    assert "import tensorflow as tf" in document.content


@pytest.mark.error
def test_document_serialization_error():
    """Test error handling during document serialization."""
    # Create a document with a non-serializable object
    class NonSerializable:
        pass
    
    document = Document(
        content="Test content",
        document_type="text",
        path="/path/to/test.txt",
        metadata={"non_serializable": NonSerializable()}
    )
    
    # Attempting to convert to dict should raise an error
    with pytest.raises(TypeError):
        document_dict = document.to_dict()


@pytest.mark.malformed
def test_serialized_document_loading_error():
    """Test error handling when loading from a malformed JSON file."""
    # Create a malformed JSON file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        f.write(b'{"content": "Test content", "document_type": "text", "path": "/path/to/test.txt", "metadata":')
        file_path = f.name
    
    try:
        # Attempt to load the malformed JSON
        with pytest.raises(json.JSONDecodeError):
            with open(file_path, 'r') as f:
                document_dict = json.load(f)
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.error
def test_unreadable_file_handling():
    """Test handling of unreadable files."""
    # Create a file and make it unreadable
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b"This is a test file")
        file_path = f.name
    
    try:
        # Make the file unreadable (on Unix-like systems)
        if os.name != 'nt':  # Skip on Windows
            os.chmod(file_path, 0)
            
            # Process the unreadable file should raise an error
            with pytest.raises(PermissionError):
                edge_case_document_processor = DocumentProcessor()
                edge_case_document_processor.process_document(file_path)
    finally:
        # Make it readable again for cleanup
        if os.name != 'nt':
            os.chmod(file_path, 0o644)
        
        # Clean up
        os.unlink(file_path)


@pytest.mark.error
def test_directory_handling(edge_case_document_processor):
    """Test handling of directories instead of files."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Attempt to process a directory
        with pytest.raises(IsADirectoryError):
            edge_case_document_processor.process_document(temp_dir)
    finally:
        # Clean up
        os.rmdir(temp_dir)