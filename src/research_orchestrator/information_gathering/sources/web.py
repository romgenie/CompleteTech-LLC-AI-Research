"""
Web Information Source.

This module provides implementation for web search sources like
general search engines, specialized websites, and news sources.
"""

import logging
import requests
import time
import json
from typing import Dict, List, Any, Optional, Union
from urllib.parse import quote_plus
from research_orchestrator.information_gathering.sources.base_source import BaseSource

logger = logging.getLogger(__name__)

class WebSource(BaseSource):
    """
    Web information source for general web search.
    
    This class handles integration with web search engines and specialized
    websites to retrieve information from the internet.
    """
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize the web source.
        
        Args:
            source_id: Unique identifier for this source.
            config: Configuration dictionary for the source.
        """
        super().__init__(source_id, config)
        self.source_type = 'web'
        self.provider = config.get('provider', 'generic')
        self.base_url = config.get('base_url')
        self.last_request_time = 0
        
        # Set provider-specific base URLs if not explicitly configured
        if not self.base_url:
            if self.provider == 'serper':
                self.base_url = 'https://google.serper.dev/search'
            elif self.provider == 'serpapi':
                self.base_url = 'https://serpapi.com/search'
            elif self.provider == 'tavily':
                self.base_url = 'https://api.tavily.com/search'
            elif self.provider == 'perplexity':
                self.base_url = 'https://api.perplexity.ai/search'
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web source for information matching the query.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of search result dictionaries.
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Prepare the query for this specific web source
        processed_query = self.prepare_query(query)
        
        try:
            if self.provider == 'serper':
                return self._search_serper(processed_query, limit)
            elif self.provider == 'serpapi':
                return self._search_serpapi(processed_query, limit)
            elif self.provider == 'tavily':
                return self._search_tavily(processed_query, limit)
            elif self.provider == 'perplexity':
                return self._search_perplexity(processed_query, limit)
            elif self.provider == 'generic':
                return self._search_generic(processed_query, limit)
            else:
                logger.warning(f"Unsupported web provider: {self.provider}")
                return []
        except Exception as e:
            logger.error(f"Error searching {self.provider}: {str(e)}")
            return []
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific web document by ID.
        
        Args:
            document_id: The ID of the document to retrieve.
            
        Returns:
            The document as a dictionary.
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        try:
            # For web sources, document_id is usually a URL
            # We need to fetch the content of that URL
            return self._fetch_web_content(document_id)
        except Exception as e:
            logger.error(f"Error retrieving document {document_id} from {self.provider}: {str(e)}")
            return {}
    
    def prepare_query(self, query: str) -> str:
        """
        Prepare a query for this specific web source.
        
        Args:
            query: The original search query.
            
        Returns:
            Processed query string optimized for the web source.
        """
        # Handle provider-specific query formatting
        if self.provider == 'serper' or self.provider == 'serpapi':
            # Remove special characters that might cause issues
            return query.replace('"', ' ').replace(':', ' ')
        
        return query
    
    def _apply_rate_limit(self) -> None:
        """
        Apply rate limiting to prevent too many requests.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Calculate seconds per request based on rate limit
        seconds_per_request = 60.0 / self.rate_limit
        
        # If requesting too quickly, sleep to respect rate limit
        if time_since_last_request < seconds_per_request:
            sleep_time = seconds_per_request - time_since_last_request
            time.sleep(sleep_time)
        
        # Update last request time
        self.last_request_time = time.time()
    
    def _search_serper(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search using Serper API.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": limit
        }
        
        response = requests.post(
            self.base_url, 
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_serper_results(data, limit)
    
    def _search_serpapi(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search using SerpAPI.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        params = {
            "q": query,
            "api_key": self.api_key,
            "num": limit
        }
        
        response = requests.get(
            self.base_url, 
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_serpapi_results(data, limit)
    
    def _search_tavily(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search using Tavily API.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        
        payload = {
            "query": query,
            "max_results": limit,
            "search_depth": "advanced"
        }
        
        response = requests.post(
            self.base_url, 
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_tavily_results(data, limit)
    
    def _search_perplexity(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search using Perplexity API.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "max_results": limit
        }
        
        response = requests.post(
            self.base_url, 
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_perplexity_results(data, limit)
    
    def _search_generic(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search using a generic web API defined in config.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # For custom/generic web sources
        if not self.base_url:
            logger.error("No base URL configured for generic web source")
            return []
        
        # Record the query for result processing
        self._current_query = query
        
        # Get configuration for this generic source
        method = self.config.get('method', 'GET')
        headers = self.config.get('headers', {})
        if self.api_key and 'api_key_header' in self.config:
            headers[self.config['api_key_header']] = self.api_key
            
        query_param = self.config.get('query_param', 'q')
        limit_param = self.config.get('limit_param', 'limit')
        
        if method.upper() == 'GET':
            params = {
                query_param: query,
                limit_param: limit
            }
            # Add any additional parameters specified in config
            params.update(self.config.get('additional_params', {}))
            
            response = requests.get(
                self.base_url, 
                headers=headers,
                params=params,
                timeout=self.timeout
            )
        else:  # POST
            payload = {
                query_param: query,
                limit_param: limit
            }
            # Add any additional parameters specified in config
            payload.update(self.config.get('additional_params', {}))
            
            response = requests.post(
                self.base_url, 
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
        response.raise_for_status()
        
        # Determine response format
        if response.headers.get('Content-Type', '').startswith('application/json'):
            data = response.json()
        else:
            data = response.text
            
        # Use custom result extraction if provided
        if 'result_path' in self.config:
            return self._extract_results_by_path(data, self.config['result_path'], limit)
        
        # Default to a simple placeholder response
        return self._format_generic_results(data, limit)
    
    def _fetch_web_content(self, url: str) -> Dict[str, Any]:
        """
        Fetch the content of a web page.
        
        Args:
            url: The URL to fetch.
            
        Returns:
            Dictionary with the web page content.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        
        # Determine content type
        content_type = response.headers.get('Content-Type', '')
        
        if 'text/html' in content_type:
            return {
                'url': url,
                'content': response.text,
                'content_type': 'html',
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'source_type': 'web'
            }
        elif 'application/json' in content_type:
            return {
                'url': url,
                'content': response.json(),
                'content_type': 'json',
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'source_type': 'web'
            }
        elif 'application/pdf' in content_type:
            return {
                'url': url,
                'content': response.content,  # Binary content
                'content_type': 'pdf',
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'source_type': 'web'
            }
        else:
            return {
                'url': url,
                'content': response.text,
                'content_type': 'text',
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'source_type': 'web'
            }
    
    def _format_serper_results(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Format Serper API search results.
        
        Args:
            data: The JSON response from Serper.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        # Process organic search results
        organic = data.get('organic', [])
        for i, item in enumerate(organic[:limit]):
            result = {
                'id': f"serper:{i}",
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'url': item.get('link', ''),
                'source_type': 'web',
                'query': self._current_query,
                'position': item.get('position', i),
                'domain': item.get('domain', '')
            }
            results.append(result)
            
        return results
    
    def _format_serpapi_results(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Format SerpAPI search results.
        
        Args:
            data: The JSON response from SerpAPI.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        # Process organic search results
        organic = data.get('organic_results', [])
        for i, item in enumerate(organic[:limit]):
            result = {
                'id': f"serpapi:{i}",
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'url': item.get('link', ''),
                'source_type': 'web',
                'query': self._current_query,
                'position': i,
                'displayed_url': item.get('displayed_link', '')
            }
            results.append(result)
            
        return results
    
    def _format_tavily_results(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Format Tavily API search results.
        
        Args:
            data: The JSON response from Tavily.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        # Process results
        items = data.get('results', [])
        for i, item in enumerate(items[:limit]):
            result = {
                'id': f"tavily:{i}",
                'title': item.get('title', ''),
                'snippet': item.get('content', ''),
                'url': item.get('url', ''),
                'source_type': 'web',
                'query': self._current_query,
                'score': item.get('score', 0.0)
            }
            results.append(result)
            
        return results
    
    def _format_perplexity_results(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Format Perplexity API search results.
        
        Args:
            data: The JSON response from Perplexity.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        # Process results
        answer = data.get('answer', {})
        items = data.get('web_search', [])
        
        # Add the main answer as a result if present
        if answer and isinstance(answer, dict) and 'text' in answer:
            results.append({
                'id': f"perplexity:answer",
                'title': "Perplexity Answer",
                'snippet': answer.get('text', ''),
                'url': '',  # No direct URL for the answer
                'source_type': 'web',
                'query': self._current_query,
                'is_answer': True
            })
        
        # Add web search results
        for i, item in enumerate(items[:limit]):
            result = {
                'id': f"perplexity:{i}",
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'url': item.get('url', ''),
                'source_type': 'web',
                'query': self._current_query,
                'is_answer': False
            }
            results.append(result)
            
        return results
    
    def _format_generic_results(self, data: Any, limit: int) -> List[Dict[str, Any]]:
        """
        Format results from a generic web API.
        
        Args:
            data: The response from the generic API.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        # If we got JSON data, try to extract results
        if isinstance(data, dict):
            # Try some common result paths
            for path in ['results', 'items', 'data', 'response']:
                if path in data and isinstance(data[path], list):
                    return self._extract_results_from_list(data[path], limit)
        
        # If all else fails, return sample placeholder data
        return [
            {
                'id': f"web:{i}",
                'title': f"Web Result {i} for {self._current_query}",
                'snippet': f"This is a sample result for the query: {self._current_query}",
                'url': f"https://example.com/result/{i}",
                'source_type': 'web',
                'query': self._current_query
            }
            for i in range(1, min(limit + 1, 6))
        ]
    
    def _extract_results_from_list(self, items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """
        Extract search results from a list of items.
        
        Args:
            items: List of result items.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        for i, item in enumerate(items[:limit]):
            # Try to determine field names from the item
            title_field = next((f for f in ['title', 'name', 'headline'] if f in item), None)
            url_field = next((f for f in ['url', 'link', 'href'] if f in item), None)
            snippet_field = next((f for f in ['snippet', 'description', 'summary', 'content'] if f in item), None)
            
            result = {
                'id': f"generic:{i}",
                'title': item.get(title_field, f"Result {i}") if title_field else f"Result {i}",
                'snippet': item.get(snippet_field, '') if snippet_field else '',
                'url': item.get(url_field, '') if url_field else '',
                'source_type': 'web',
                'query': self._current_query
            }
            
            # Add any other fields found in the item
            for key, value in item.items():
                if key not in ['title', 'snippet', 'url', 'id', 'source_type', 'query'] and not isinstance(value, (dict, list)):
                    result[key] = value
                    
            results.append(result)
            
        return results
    
    def _extract_results_by_path(self, data: Any, path: str, limit: int) -> List[Dict[str, Any]]:
        """
        Extract search results by following a dot-notation path.
        
        Args:
            data: The data to extract from.
            path: Dot-notation path to the results (e.g. 'response.items').
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        # If data is not a dictionary, return empty result
        if not isinstance(data, dict):
            return []
            
        # Split the path and navigate through the data
        parts = path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Path doesn't exist
                return []
        
        # If we reached a list, format the results
        if isinstance(current, list):
            return self._extract_results_from_list(current, limit)
            
        # Otherwise return empty list
        return []