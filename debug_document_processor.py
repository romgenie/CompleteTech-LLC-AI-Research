"""Debug script for the DocumentProcessor class."""

from unittest.mock import patch, MagicMock
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor, Document
from src.research_orchestrator.knowledge_extraction.document_processing.text_processor import TextProcessor
from src.research_orchestrator.knowledge_extraction.document_processing.html_processor import HTMLProcessor
from src.research_orchestrator.knowledge_extraction.document_processing.pdf_processor import PDFProcessor

def debug_document_processor():
    """Debug the DocumentProcessor class."""
    print("Starting DocumentProcessor debug...")
    
    # 1. Check initialization without mocks
    try:
        processor = DocumentProcessor()
        print("✓ DocumentProcessor initialized successfully")
        print(f"  Properties available: {dir(processor)}")
    except Exception as e:
        print(f"✗ Failed to initialize DocumentProcessor: {type(e).__name__}: {e}")
        return
    
    # 2. Check if processors are initialized
    try:
        print(f"  Processors initialized: {bool(processor.processors)}")
        print(f"  Processor types: {[type(p).__name__ for p in processor.processors.values()]}")
    except Exception as e:
        print(f"✗ Failed to access processors: {type(e).__name__}: {e}")
    
    # 3. Check _get_processor_for_extension method
    try:
        txt_processor = processor._get_processor_for_extension('.txt')
        html_processor = processor._get_processor_for_extension('.html')
        pdf_processor = processor._get_processor_for_extension('.pdf')
        unknown_processor = processor._get_processor_for_extension('.xyz')
        
        print(f"  .txt processor type: {type(txt_processor).__name__}")
        print(f"  .html processor type: {type(html_processor).__name__}")
        print(f"  .pdf processor type: {type(pdf_processor).__name__}")
        print(f"  .xyz processor type: {type(unknown_processor).__name__}")
    except Exception as e:
        print(f"✗ Failed to get processors for extensions: {type(e).__name__}: {e}")
    
    # 4. Create a mock document for testing process_document
    mock_document = Document(
        content="Test content",
        document_type="text",
        path="/path/to/test.txt",
        metadata={"file_size": 100}
    )
    
    # 5. Try to mock TextProcessor and test process_document
    try:
        with patch('src.research_orchestrator.knowledge_extraction.document_processing.text_processor.TextProcessor') as MockTextProcessor:
            print("  Setting up mock TextProcessor...")
            mock_instance = MockTextProcessor.return_value
            mock_instance.process.return_value = mock_document
            
            # Create a new processor with the mock
            test_processor = DocumentProcessor()
            
            # Check if process_document works
            print("  Testing process_document method...")
            result = test_processor.process_document("/path/to/test.txt")
            print(f"  process_document returned: {type(result).__name__}")
    except Exception as e:
        print(f"✗ Failed to mock TextProcessor and test process_document: {type(e).__name__}: {e}")

if __name__ == "__main__":
    debug_document_processor()