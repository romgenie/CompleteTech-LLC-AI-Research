"""
Base Source for Information Gathering.

This module defines the base class for all information sources.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseSource(ABC):
    """
    Base class for all information sources.
    
    All specific source implementations should inherit from this class.
    """
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize the information source.
        
        Args:
            source_id: Unique identifier for this source.
            config: Configuration dictionary for the source.
        """
        self.source_id = source_id
        self.config = config
        self.name = config.get('name', source_id)
        self.source_type = config.get('type', 'custom')
        self.enabled = config.get('enabled', True)
        self.api_key = config.get('api_key')
        self.rate_limit = config.get('rate_limit', 60)  # Requests per minute
        self.timeout = config.get('timeout', 30)  # Seconds
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search this source for information.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of search result dictionaries.
        """
        pass
    
    @abstractmethod
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: The ID of the document to retrieve.
            
        Returns:
            The document as a dictionary.
        """
        pass
    
    def prepare_query(self, query: str) -> str:
        """
        Prepare a query for this specific source.
        
        Args:
            query: The original search query.
            
        Returns:
            Processed query string optimized for this source.
        """
        # Base implementation just returns the original query
        # Subclasses can override to add source-specific query processing
        return query
    
    def format_results(self, raw_results: Any) -> List[Dict[str, Any]]:
        """
        Format raw search results into standardized format.
        
        Args:
            raw_results: Raw results from the source API.
            
        Returns:
            List of standardized result dictionaries.
        """
        # This should be implemented by subclasses
        # Base implementation just returns an empty list
        return []
    
    def validate_config(self) -> bool:
        """
        Validate the source configuration.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        # Base implementation just checks if source is enabled
        return self.enabled