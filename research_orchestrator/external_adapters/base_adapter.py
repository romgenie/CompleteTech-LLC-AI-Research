"""
Base adapter interface for external repositories.

This module defines the base adapter interface that all external repository adapters
must implement to ensure consistent integration with the research orchestrator.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseAdapter(ABC):
    """
    Base adapter interface for external repositories.
    
    This abstract class defines the interface that all external repository adapters
    must implement to ensure consistent integration with the research orchestrator.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the adapter with the provided configuration.
        
        Args:
            config: Configuration dictionary for the adapter
            
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