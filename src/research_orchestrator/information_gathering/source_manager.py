"""
Source Manager for the Information Gathering Module.

This module manages information sources, including academic databases,
code repositories, web sources, and specialized AI sources.
"""

import logging
import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

class SourceManager:
    """
    Manages information sources for retrieval operations.
    
    This class handles the registration, configuration, and access
    to various information sources like academic databases,
    web search engines, code repositories, etc.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the source manager.
        
        Args:
            config: Configuration dictionary with source settings.
        """
        self.config = config
        self.sources = {}
        self.default_sources = config.get('default_sources', [])
        self.max_workers = config.get('max_workers', 5)
        
        # Initialize sources
        self._initialize_sources()
    
    def _initialize_sources(self) -> None:
        """
        Initialize all configured sources.
        """
        sources_config = self.config.get('sources', {})
        
        for source_id, source_config in sources_config.items():
            if not source_config.get('enabled', True):
                logger.info(f"Skipping disabled source: {source_id}")
                continue
                
            try:
                self._register_source(source_id, source_config)
            except Exception as e:
                logger.error(f"Failed to initialize source {source_id}: {str(e)}")
    
    def _register_source(self, source_id: str, config: Dict[str, Any]) -> None:
        """
        Register a source with the manager.
        
        Args:
            source_id: Unique identifier for the source.
            config: Configuration for the source.
        """
        source_type = config.get('type')
        
        if not source_type:
            logger.error(f"Source {source_id} missing required 'type' field")
            return
        
        # Get the source class based on type
        try:
            if source_type == 'academic':
                from research_orchestrator.information_gathering.sources.academic import AcademicSource
                source_class = AcademicSource
            elif source_type == 'web':
                from research_orchestrator.information_gathering.sources.web import WebSource
                source_class = WebSource
            elif source_type == 'code':
                from research_orchestrator.information_gathering.sources.code import CodeSource
                source_class = CodeSource
            elif source_type == 'ai':
                from research_orchestrator.information_gathering.sources.ai import AISource
                source_class = AISource
            elif source_type == 'custom':
                # Handle custom source with module path
                module_path = config.get('module_path')
                class_name = config.get('class_name')
                
                if not module_path or not class_name:
                    logger.error(f"Custom source {source_id} missing required module_path or class_name")
                    return
                
                module = importlib.import_module(module_path)
                source_class = getattr(module, class_name)
            else:
                logger.error(f"Unknown source type: {source_type}")
                return
                
            # Initialize the source
            source_instance = source_class(source_id, config)
            self.sources[source_id] = source_instance
            logger.info(f"Registered source: {source_id} ({source_type})")
            
        except Exception as e:
            logger.error(f"Error registering source {source_id}: {str(e)}")
    
    def get_source(self, source_id: str) -> Any:
        """
        Get a specific source by ID.
        
        Args:
            source_id: The ID of the source to retrieve.
            
        Returns:
            The source instance.
            
        Raises:
            KeyError: If the source ID is not found.
        """
        if source_id not in self.sources:
            raise KeyError(f"Source not found: {source_id}")
        
        return self.sources[source_id]
    
    def get_enabled_sources(self) -> List[str]:
        """
        Get a list of all enabled source IDs.
        
        Returns:
            List of enabled source IDs.
        """
        return list(self.sources.keys())
    
    def search(self, query: str, sources: Optional[List[str]] = None,
              limit: int = 10, search_type: str = 'general') -> List[Dict[str, Any]]:
        """
        Search across specified sources.
        
        Args:
            query: The search query.
            sources: Optional list of source IDs to search. If None, all enabled
                    sources will be used.
            limit: Maximum number of results to return per source.
            search_type: Type of search to perform.
            
        Returns:
            A list of search result dictionaries.
        """
        # Determine which sources to search
        if sources is None:
            if search_type == 'academic':
                # Use academic sources by default for academic searches
                active_sources = [s for s in self.sources if self.sources[s].source_type == 'academic']
            elif search_type == 'code':
                # Use code repositories by default for code searches
                active_sources = [s for s in self.sources if self.sources[s].source_type == 'code']
            else:
                # Use default sources for general searches
                active_sources = self.default_sources if self.default_sources else list(self.sources.keys())
        else:
            # Use specified sources, filtered by what's available
            active_sources = [s for s in sources if s in self.sources]
        
        if not active_sources:
            logger.warning(f"No active sources found for search_type={search_type}")
            return []
        
        # Execute search across sources in parallel
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Start search tasks for each source
            future_to_source = {
                executor.submit(self._search_source, source_id, query, limit): source_id
                for source_id in active_sources
            }
            
            # Process results as they complete
            for future in as_completed(future_to_source):
                source_id = future_to_source[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    logger.debug(f"Search completed for source {source_id}: {len(results)} results")
                except Exception as e:
                    logger.error(f"Error searching source {source_id}: {str(e)}")
        
        return all_results
    
    def _search_source(self, source_id: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search a specific source.
        
        Args:
            source_id: The ID of the source to search.
            query: The search query.
            limit: Maximum number of results.
            
        Returns:
            A list of search result dictionaries from this source.
        """
        source = self.sources[source_id]
        results = source.search(query, limit)
        
        # Add source metadata to each result
        for result in results:
            result['source_id'] = source_id
            result['source_name'] = source.name
            
        return results
    
    def get_document(self, document_id: str, source_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: The ID of the document to retrieve.
            source_id: The ID of the source containing the document.
            
        Returns:
            The document as a dictionary.
            
        Raises:
            KeyError: If the source ID is not found.
        """
        source = self.get_source(source_id)
        return source.get_document(document_id)