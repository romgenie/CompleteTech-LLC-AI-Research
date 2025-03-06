"""
Benchmark tests for document processing performance.

This module contains tests that measure the performance of the document
processing components with documents of various sizes.
"""

import pytest
import time
import tempfile
import os
import random
import string
import numpy as np

# Mark all tests in this module as benchmark tests and document related tests
pytestmark = [
    pytest.mark.benchmark,
    pytest.mark.document,
    pytest.mark.slow
]

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor, TextProcessor


def write_text_file(file_path, size_kb):
    """Write a text file of the given size."""
    # Calculate content size in bytes
    content_size = size_kb * 1024
    
    # Generate random content
    chars = string.ascii_letters + string.digits + ' ' * 10 + '\n' * 2 + ',.!?'
    content = ''.join(random.choices(chars, k=content_size))
    
    # Write to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return file_path


@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_text_processor_performance(size_kb, timer):
    """Test the performance of TextProcessor with different file sizes."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        file_path = temp_file.name
    
    try:
        # Write text file
        write_text_file(file_path, size_kb)
        
        # Create processor
        processor = TextProcessor()
        
        # Measure processing time
        with timer(f"TextProcessor.process({size_kb}KB)"):
            document = processor.process(file_path)
        
        # Basic checks
        assert document.document_type == "text"
        assert len(document.content) >= size_kb * 1024 * 0.8  # Allow for some variation in content size
        
        # Measure content processing time
        content = document.content
        with timer(f"TextProcessor.process_content({size_kb}KB)"):
            document2 = processor.process_content(content)
        
        # Measure metadata extraction time
        with timer(f"TextProcessor.get_metadata({size_kb}KB)"):
            metadata = processor.get_metadata(content)
    
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_document_processor_performance(size_kb, timer):
    """Test the performance of DocumentProcessor with different file sizes."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        file_path = temp_file.name
    
    try:
        # Write text file
        write_text_file(file_path, size_kb)
        
        # Create processor
        processor = DocumentProcessor()
        
        # Measure processing time
        with timer(f"DocumentProcessor.process_document({size_kb}KB)"):
            document = processor.process_document(file_path)
        
        # Basic checks
        assert document.document_type == "text"
        assert len(document.content) >= size_kb * 1024 * 0.8  # Allow for some variation in content size
        
        # Measure text processing time
        content = document.content
        with timer(f"DocumentProcessor.process_text({size_kb}KB)"):
            document2 = processor.process_text(content)
    
    finally:
        # Clean up
        os.unlink(file_path)


@pytest.mark.parametrize('size_kb', [10, 100, 1000])
def test_document_segmentation_performance(size_kb, timer):
    """Test the performance of document segmentation with different file sizes."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        file_path = temp_file.name
    
    try:
        # Write text file
        write_text_file(file_path, size_kb)
        
        # Create processor and process document
        processor = DocumentProcessor()
        document = processor.process_document(file_path)
        
        # Measure segmentation time for different separators
        separators = ['\n', '.', ' ', '\t']
        for separator in separators:
            with timer(f"Document.get_segments({size_kb}KB, '{separator}')"):
                segments = document.get_segments(separator=separator)
            
            # Basic checks
            assert isinstance(segments, list)
            assert len(segments) > 0
    
    finally:
        # Clean up
        os.unlink(file_path)


def test_document_processor_scalability():
    """Test how document processing time scales with document size."""
    sizes = [10, 50, 100, 500, 1000]  # KB
    times = []
    
    processor = DocumentProcessor()
    
    for size_kb in sizes:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            file_path = temp_file.name
        
        try:
            # Write text file
            write_text_file(file_path, size_kb)
            
            # Measure processing time
            start_time = time.time()
            document = processor.process_document(file_path)
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        finally:
            # Clean up
            os.unlink(file_path)
    
    # Output results
    print("\nDocument Processing Scalability:")
    print("-------------------------------")
    print(f"{'Size (KB)':<10} {'Time (s)':<10}")
    print("-------------------------------")
    for i, size_kb in enumerate(sizes):
        print(f"{size_kb:<10} {times[i]:<10.4f}")
    
    # Calculate scaling factor using linear regression
    log_sizes = np.log(sizes)
    log_times = np.log(times)
    slope, intercept = np.polyfit(log_sizes, log_times, 1)
    
    print(f"\nScaling factor: O(n^{slope:.2f})")
    
    # Check linear or near-linear scaling
    assert slope < 1.5, f"Document processing scales poorly: O(n^{slope:.2f})"