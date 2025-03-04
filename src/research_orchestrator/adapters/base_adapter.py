"""
Base Adapter Interface.

This module defines the base adapter interface for external system integration.
All adapters should implement this interface to ensure consistency.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseAdapter(ABC):
    """
    Base class for all adapters in the Research Orchestration Framework.
    """
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter with configuration.
        
        Args:
            config: Configuration dictionary for the adapter.
        """
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate the provided configuration.
        
        Args:
            config: Configuration dictionary to validate.
            
        Returns:
            True if configuration is valid, False otherwise.
        """
        return True


class TaskDecompositionAdapter(BaseAdapter):
    """
    Interface for adapters that provide task decomposition capabilities.
    """
    
    @abstractmethod
    def decompose_task(self, task: str) -> List[Dict[str, str]]:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task: The task to decompose.
            
        Returns:
            A list of subtask dictionaries with name and goal fields.
        """
        pass


class PlanningAdapter(BaseAdapter):
    """
    Interface for adapters that provide planning capabilities.
    """
    
    @abstractmethod
    def create_research_plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a research plan for a given task.
        
        Args:
            task: The research task to plan for.
            context: Optional context information to guide planning.
            
        Returns:
            A dictionary containing the research plan.
        """
        pass


class InformationGatheringAdapter(BaseAdapter):
    """
    Interface for adapters that provide information gathering capabilities.
    """
    
    @abstractmethod
    def search(self, query: str, sources: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for information based on a query.
        
        Args:
            query: The search query.
            sources: List of sources to search.
            limit: Maximum number of results to return.
            
        Returns:
            A list of search result dictionaries.
        """
        pass
    
    @abstractmethod
    def retrieve_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: The ID of the document to retrieve.
            
        Returns:
            The document as a dictionary.
        """
        pass


class KnowledgeExtractionAdapter(BaseAdapter):
    """
    Interface for adapters that provide knowledge extraction capabilities.
    """
    
    @abstractmethod
    def extract_knowledge(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract knowledge from text.
        
        Args:
            text: The text to extract knowledge from.
            
        Returns:
            A list of knowledge triples as dictionaries.
        """
        pass