"""Debug script to identify the source of test failures."""

from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import Document

def test_document_class():
    """Test the Document class methods."""
    try:
        # Create a document
        document = Document(
            content="This is test content.",
            document_type="text",
            path="/path/to/document.txt",
            metadata={"author": "Test Author"}
        )
        
        # Test get_text method
        assert document.get_text() == "This is test content."
        print("✓ get_text method works")
        
        # Test metadata attribute
        assert document.metadata == {"author": "Test Author"}
        print("✓ metadata attribute works")
        
        # Test to_dict method
        doc_dict = document.to_dict()
        assert doc_dict["content"] == "This is test content."
        assert doc_dict["document_type"] == "text"
        assert doc_dict["path"] == "/path/to/document.txt"
        assert doc_dict["metadata"] == {"author": "Test Author"}
        print("✓ to_dict method works")
        
        # Test from_dict method
        new_document = Document.from_dict(doc_dict)
        assert new_document.content == "This is test content."
        assert new_document.document_type == "text"
        assert new_document.path == "/path/to/document.txt"
        assert new_document.metadata == {"author": "Test Author"}
        print("✓ from_dict method works")
        
        print("All tests passed!")
        return True
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    test_document_class()