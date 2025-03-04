"""
Base adapter for external repositories.

This module provides a base class for adapters that integrate with external repositories,
defining the common interface and functionality for all adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAdapter(ABC):
    """
    Base class for adapters that integrate with external repositories.
    
    This abstract class defines the common interface that all adapters must implement.
    It provides a standard way for the research orchestrator to interact with external
    repositories regardless of their specific implementation details.
    """
    
    def __init__(self, name: str):
        """
        Initialize the adapter.
        
        Args:
            name: Name of the adapter
        """
        self.name = name
        self.initialized = False
        self.available = False
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the adapter with the provided configuration.
        
        Args:
            config: Configuration dictionary containing adapter-specific settings
            
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the external repository is available.
        
        Returns:
            True if the repository is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities provided by this adapter.
        
        Returns:
            List of capability strings
        """
        pass
    
    @abstractmethod
    def execute(self, 
               action: str, 
               params: Dict[str, Any], 
               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an action using the external repository.
        
        Args:
            action: The action to execute
            params: Parameters for the action
            context: Optional context information
            
        Returns:
            Result dictionary
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Shutdown the adapter and release any resources.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        pass
    
    def __str__(self) -> str:
        """
        Get a string representation of the adapter.
        
        Returns:
            String representation
        """
        status = "initialized" if self.initialized else "not initialized"
        available = "available" if self.is_available() else "not available"
        return f"{self.name} ({status}, {available})"