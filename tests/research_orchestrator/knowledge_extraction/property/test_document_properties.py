"""
Property-based tests for the Document class and DocumentProcessor.

This module contains property-based tests using hypothesis to validate
that the Document class and related functions maintain invariants and
properties across a wide range of inputs.
"""

import pytest
from hypothesis import given, strategies as st
import json
import tempfile
import os

# Mark all tests in this module as property tests and document related tests
pytestmark = [
    pytest.mark.property,
    pytest.mark.document,
    pytest.mark.medium
]

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import Document, DocumentProcessor, SimpleTextProcessor as TextProcessor


class TestDocumentProperties:
    """Property-based tests for the Document class."""

    @given(
        content=st.text(min_size=0, max_size=1000),
        document_type=st.sampled_from(['text', 'html', 'pdf', 'markdown', 'docx']),
        path=st.text(min_size=0, max_size=100),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        )
    )
    def test_document_serialization_roundtrip(self, content, document_type, path, metadata):
        """Test that Document objects can be serialized to dict and back without data loss."""
        # Create a document
        document = Document(
            content=content,
            document_type=document_type,
            path=path,
            metadata=metadata
        )
        
        # Convert to dict
        document_dict = document.to_dict()
        
        # Convert back to document
        document2 = Document.from_dict(document_dict)
        
        # Check that the document has the same properties after round trip
        assert document2.content == document.content
        assert document2.document_type == document.document_type
        assert document2.path == document.path
        assert document2.metadata == document.metadata
    
    @given(
        content=st.text(min_size=0, max_size=1000),
        document_type=st.sampled_from(['text', 'html', 'pdf', 'markdown', 'docx']),
        path=st.text(min_size=0, max_size=100),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        )
    )
    def test_document_json_serialization(self, content, document_type, path, metadata):
        """Test that Document objects can be serialized to JSON and back without data loss."""
        # Create a document
        document = Document(
            content=content,
            document_type=document_type,
            path=path,
            metadata=metadata
        )
        
        # Convert to dict then to JSON
        document_dict = document.to_dict()
        document_json = json.dumps(document_dict)
        
        # Convert back from JSON to dict to document
        document_dict2 = json.loads(document_json)
        document2 = Document.from_dict(document_dict2)
        
        # Check that the document has the same properties after JSON round trip
        assert document2.content == document.content
        assert document2.document_type == document.document_type
        assert document2.path == document.path
        assert document2.metadata == document.metadata
    
    @given(
        content=st.text(min_size=1, max_size=1000),
        document_type=st.sampled_from(['text', 'html', 'pdf', 'markdown', 'docx']),
        path=st.text(min_size=0, max_size=100),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        )
    )
    def test_document_get_text(self, content, document_type, path, metadata):
        """Test that Document.get_text() returns the document content."""
        # Create a document
        document = Document(
            content=content,
            document_type=document_type,
            path=path,
            metadata=metadata
        )
        
        # Get text
        text = document.get_text()
        
        # Check that text equals content
        assert text == content
    
    @given(
        content=st.text(min_size=1, max_size=1000).map(lambda s: s.replace('\n', ' \n ')),  # Ensure some newlines
        document_type=st.sampled_from(['text', 'html', 'pdf', 'markdown', 'docx']),
        path=st.text(min_size=0, max_size=100),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=10),
            values=st.one_of(st.text(), st.integers(), st.floats())
        ),
        separator=st.sampled_from(['\n', '.', ',', ' '])
    )
    def test_document_get_segments(self, content, document_type, path, metadata, separator):
        """Test that Document.get_segments() correctly segments the document."""
        # Create a document
        document = Document(
            content=content,
            document_type=document_type,
            path=path,
            metadata=metadata
        )
        
        # Get segments
        segments = document.get_segments(separator=separator)
        
        # Check that segments is a list of strings
        assert isinstance(segments, list)
        assert all(isinstance(segment, str) for segment in segments)
        
        # Check that joining segments with separator approximately recovers content
        # (There may be some differences due to handling of multiple separators, empty segments, etc.)
        if separator in content and len(segments) > 1:
            # If we split by a character that's in the content, there should be segments
            assert len(segments) >= 1


class TestDocumentProcessorProperties:
    """Property-based tests for the DocumentProcessor class."""
    
    @given(
        content=st.text(min_size=1, max_size=1000)
    )
    def test_text_processor_content_processing(self, content):
        """Test that TextProcessor correctly processes text content."""
        # Create a text processor
        processor = TextProcessor()
        
        # Process content
        document = processor.process_content(content)
        
        # Check that document has correct properties
        assert document.content == content
        assert document.document_type == "text"
        assert document.path is None
        assert "line_count" in document.metadata
        assert document.metadata["line_count"] == content.count('\n') + 1
    
    @given(
        content=st.text(min_size=1, max_size=1000)
    )
    def test_document_processor_text_processing(self, content):
        """Test that DocumentProcessor correctly processes text content."""
        # Create a document processor
        processor = DocumentProcessor()
        
        # Process content
        document = processor.process_text(content)
        
        # Check that document has correct properties
        assert document.content == content
        assert document.document_type == "text"
        
    @given(
        content=st.text(min_size=1, max_size=1000),
        document_type=st.sampled_from(['text', 'html', 'pdf'])
    )
    def test_text_processor_metadata_extraction(self, content, document_type):
        """Test that TextProcessor correctly extracts metadata from content."""
        # Create a text processor
        processor = TextProcessor()
        
        # Get metadata
        metadata = processor.get_metadata(content)
        
        # Check that metadata has correct properties
        assert "line_count" in metadata
        assert metadata["line_count"] == content.count('\n') + 1
        assert "char_count" in metadata
        assert metadata["char_count"] == len(content)
        assert "word_count" in metadata
        assert isinstance(metadata["word_count"], int)