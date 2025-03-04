"""
Search Manager for the Information Gathering Module.

This module manages search operations across multiple sources,
coordinating queries and aggregating results.
"""

import logging
from typing import Dict, List, Any, Optional

from research_orchestrator.information_gathering.source_manager import SourceManager
from research_orchestrator.information_gathering.quality_assessor import QualityAssessor

logger = logging.getLogger(__name__)

class SearchManager:
    """
    Manages search operations across multiple sources.
    
    This class handles search query execution across different
    information sources, managing parallel searches, aggregating
    results, and implementing search strategies based on context.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the search manager.
        
        Args:
            config: Configuration dictionary with search settings.
        """
        self.config = config
        self.source_manager = SourceManager(config.get('sources', {}))
        self.quality_assessor = QualityAssessor(config.get('quality', {}))
        self.results_cache = {}
        
    def search(self, query: str, sources: Optional[List[str]] = None, 
               limit: int = 10, search_type: str = 'general',
               filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a search query across specified sources.
        
        Args:
            query: The search query string.
            sources: Optional list of source IDs to search. If None, all enabled
                    sources will be used.
            limit: Maximum number of results to return per source.
            search_type: Type of search to perform ('general', 'academic', 'code').
            filter_criteria: Optional criteria for filtering results.
            
        Returns:
            A list of search result dictionaries.
        """
        logger.info(f"Executing search: '{query}' across {sources or 'all'} sources")
        
        # Normalize and enhance the query
        processed_query = self._process_query(query, search_type)
        
        # Check cache for existing results
        cache_key = f"{processed_query}_{str(sources)}_{limit}_{search_type}"
        if cache_key in self.results_cache:
            logger.debug(f"Returning cached results for '{query}'")
            return self.results_cache[cache_key]
        
        # Execute search across sources
        results = self._execute_search(processed_query, sources, limit, search_type)
        
        # Apply filters if specified
        if filter_criteria:
            results = self._filter_results(results, filter_criteria)
        
        # Assess quality and sort results
        results = self._assess_and_sort_results(results)
        
        # Cache the results
        self.results_cache[cache_key] = results
        
        logger.info(f"Search completed for '{query}': {len(results)} results")
        return results
    
    def get_document(self, document_id: str, source_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: The ID of the document to retrieve.
            source_id: The ID of the source containing the document.
            
        Returns:
            The document as a dictionary.
        """
        logger.info(f"Retrieving document {document_id} from {source_id}")
        return self.source_manager.get_document(document_id, source_id)
    
    def clear_cache(self) -> None:
        """
        Clear the search results cache.
        """
        self.results_cache = {}
        logger.debug("Search cache cleared")
    
    def _process_query(self, query: str, search_type: str) -> str:
        """
        Process and enhance the search query.
        
        Args:
            query: The original search query.
            search_type: Type of search to perform.
            
        Returns:
            The processed query string.
        """
        # Add search type specific enhancements
        if search_type == 'academic':
            return self._enhance_academic_query(query)
        elif search_type == 'code':
            return self._enhance_code_query(query)
        else:
            return query
    
    def _enhance_academic_query(self, query: str) -> str:
        """
        Enhance a query for academic sources.
        
        Args:
            query: The original query.
            
        Returns:
            The enhanced query string.
        """
        # Add academic-specific terms/filters
        # For example, adding 'research' or 'paper' if not present
        return query
    
    def _enhance_code_query(self, query: str) -> str:
        """
        Enhance a query for code repositories.
        
        Args:
            query: The original query.
            
        Returns:
            The enhanced query string.
        """
        # Add code-specific terms/filters
        # For example, adding 'github' or 'implementation' if not present
        return query
    
    def _execute_search(self, query: str, sources: Optional[List[str]], 
                       limit: int, search_type: str) -> List[Dict[str, Any]]:
        """
        Execute search across specified sources.
        
        Args:
            query: The processed search query.
            sources: Optional list of source IDs to search.
            limit: Maximum number of results to return per source.
            search_type: Type of search to perform.
            
        Returns:
            A list of search result dictionaries.
        """
        return self.source_manager.search(query, sources, limit, search_type)
    
    def _filter_results(self, results: List[Dict[str, Any]], 
                       criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter search results based on criteria.
        
        Args:
            results: The list of search results.
            criteria: Dictionary of filtering criteria.
            
        Returns:
            Filtered list of search results.
        """
        filtered_results = []
        
        for result in results:
            if self._matches_criteria(result, criteria):
                filtered_results.append(result)
        
        return filtered_results
    
    def _matches_criteria(self, result: Dict[str, Any], 
                         criteria: Dict[str, Any]) -> bool:
        """
        Check if a result matches the filtering criteria.
        
        Args:
            result: A single search result.
            criteria: Dictionary of filtering criteria.
            
        Returns:
            True if the result matches the criteria, False otherwise.
        """
        for key, value in criteria.items():
            if key not in result:
                return False
            
            if isinstance(value, list):
                if result[key] not in value:
                    return False
            elif result[key] != value:
                return False
        
        return True
    
    def _assess_and_sort_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assess quality and sort search results.
        
        Args:
            results: The list of search results.
            
        Returns:
            Quality-assessed and sorted list of search results.
        """
        # Assess quality of each result
        assessed_results = self.quality_assessor.assess_results(results)
        
        # Sort by quality score
        assessed_results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return assessed_results