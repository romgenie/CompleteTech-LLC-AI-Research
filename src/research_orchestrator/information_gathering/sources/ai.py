"""
AI Information Source.

This module provides implementation for AI model-based information gathering,
such as using LLMs to generate information or summaries.
"""

import logging
import requests
import time
import json
from typing import Dict, List, Any, Optional, Union
from research_orchestrator.information_gathering.sources.base_source import BaseSource

logger = logging.getLogger(__name__)

class AISource(BaseSource):
    """
    AI information source using large language models.
    
    This class handles integration with AI models to generate information,
    summaries, or insights based on queries.
    """
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize the AI source.
        
        Args:
            source_id: Unique identifier for this source.
            config: Configuration dictionary for the source.
        """
        super().__init__(source_id, config)
        self.source_type = 'ai'
        self.provider = config.get('provider', 'openai')
        self.base_url = config.get('base_url')
        self.model = config.get('model', 'gpt-4')
        self.max_tokens = config.get('max_tokens', 1000)
        self.temperature = config.get('temperature', 0.7)
        self.system_prompt = config.get('system_prompt', 'You are a helpful assistant with expertise in AI research.')
        self.last_request_time = 0
        
        # Set provider-specific base URLs if not explicitly configured
        if not self.base_url:
            if self.provider == 'openai':
                self.base_url = 'https://api.openai.com/v1/chat/completions'
            elif self.provider == 'anthropic':
                self.base_url = 'https://api.anthropic.com/v1/messages'
            elif self.provider == 'cohere':
                self.base_url = 'https://api.cohere.ai/v1/generate'
            elif self.provider == 'local':
                self.base_url = config.get('local_url', 'http://localhost:8000/v1/chat/completions')
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate AI responses for the query.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return (used for multiple generations).
            
        Returns:
            A list of search result dictionaries.
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Prepare the query for this specific AI source
        processed_query = self.prepare_query(query)
        
        try:
            if self.provider == 'openai':
                return self._generate_openai(processed_query, limit)
            elif self.provider == 'anthropic':
                return self._generate_anthropic(processed_query, limit)
            elif self.provider == 'cohere':
                return self._generate_cohere(processed_query, limit)
            elif self.provider == 'local':
                return self._generate_local(processed_query, limit)
            else:
                logger.warning(f"Unsupported AI provider: {self.provider}")
                return []
        except Exception as e:
            logger.error(f"Error generating AI response from {self.provider}: {str(e)}")
            return []
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific AI-generated document by ID.
        
        Args:
            document_id: The ID of the document to retrieve. For AI sources,
                      this is typically a reference to a past generation.
            
        Returns:
            The document as a dictionary.
        """
        # For AI sources, document retrieval is typically a regeneration
        # or retrieval from a cache. We'll implement a simple regeneration.
        
        # Apply rate limiting
        self._apply_rate_limit()
        
        try:
            # Parse the document_id to extract the query
            parts = document_id.split(':', 1)
            if len(parts) < 2:
                raise ValueError(f"Invalid AI document ID: {document_id}")
            
            # The second part is the original query
            query = parts[1]
            
            # Generate a single response
            results = self.search(query, limit=1)
            if results:
                return results[0]
            else:
                return {}
        except Exception as e:
            logger.error(f"Error retrieving AI document {document_id}: {str(e)}")
            return {}
    
    def prepare_query(self, query: str) -> str:
        """
        Prepare a query for this specific AI source.
        
        Args:
            query: The original search query.
            
        Returns:
            Processed query string optimized for the AI source.
        """
        # Enhance the query with specific instructions based on configuration
        if self.config.get('query_prefix'):
            query = f"{self.config['query_prefix']} {query}"
            
        if self.config.get('query_suffix'):
            query = f"{query} {self.config['query_suffix']}"
            
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
    
    def _generate_openai(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Generate responses using OpenAI API.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results (used for multiple generations).
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Use the default system prompt if not overridden
        system_message = self.system_prompt
        
        # Check if there's a specific prompt for research questions
        if 'research_prompt' in self.config and any(term in query.lower() for term in ['research', 'study', 'paper', 'article']):
            system_message = self.config['research_prompt']
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "n": min(limit, 1)  # Most API keys have limitations on parallel generations
        }
        
        response = requests.post(
            self.base_url, 
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Format the results
        results = []
        for i, choice in enumerate(data.get('choices', [])):
            message = choice.get('message', {})
            content = message.get('content', '')
            
            result = {
                'id': f"ai:{self.provider}:{i}:{query}",
                'title': f"AI Response to: {query[:50]}{'...' if len(query) > 50 else ''}",
                'content': content,
                'model': self.model,
                'source_type': 'ai',
                'provider': self.provider,
                'query': query,
                'finish_reason': choice.get('finish_reason', ''),
                'usage': data.get('usage', {})
            }
            results.append(result)
        
        return results
    
    def _generate_anthropic(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Generate responses using Anthropic API.
        
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
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Use the default system prompt if not overridden
        system_message = self.system_prompt
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": query}
            ],
            "system": system_message,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        # Anthropic doesn't support generating multiple completions at once
        # We'll just generate one
        
        response = requests.post(
            self.base_url, 
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Format the results
        content = data.get('content', [{}])[0].get('text', '')
        
        result = {
            'id': f"ai:{self.provider}:0:{query}",
            'title': f"AI Response to: {query[:50]}{'...' if len(query) > 50 else ''}",
            'content': content,
            'model': self.model,
            'source_type': 'ai',
            'provider': self.provider,
            'query': query,
            'stop_reason': data.get('stop_reason', ''),
            'usage': {
                'input_tokens': data.get('usage', {}).get('input_tokens', 0),
                'output_tokens': data.get('usage', {}).get('output_tokens', 0)
            }
        }
        
        return [result]
    
    def _generate_cohere(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Generate responses using Cohere API.
        
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
            "Authorization": f"Bearer {self.api_key}"
        }
        
        prompt = f"{self.system_prompt}\n\nQuestion: {query}\n\nAnswer:"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "num_generations": min(limit, 1)  # Most API keys have limitations
        }
        
        response = requests.post(
            self.base_url, 
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Format the results
        results = []
        for i, generation in enumerate(data.get('generations', [])):
            content = generation.get('text', '')
            
            result = {
                'id': f"ai:{self.provider}:{i}:{query}",
                'title': f"AI Response to: {query[:50]}{'...' if len(query) > 50 else ''}",
                'content': content,
                'model': self.model,
                'source_type': 'ai',
                'provider': self.provider,
                'query': query,
                'likelihood': generation.get('likelihood', 0),
                'token_count': {
                    'prompt_tokens': data.get('meta', {}).get('billed_units', {}).get('input_tokens', 0),
                    'completion_tokens': data.get('meta', {}).get('billed_units', {}).get('output_tokens', 0)
                }
            }
            results.append(result)
        
        return results
    
    def _generate_local(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Generate responses using a local API (e.g. LLM running on the machine).
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Use the default system prompt if not overridden
        system_message = self.system_prompt
        
        # Format similar to OpenAI for compatibility with many local LLM servers
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": query}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "n": 1
        }
        
        response = requests.post(
            self.base_url, 
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        try:
            data = response.json()
            
            # Format the results - try to handle various local API formats
            results = []
            
            # Try OpenAI-compatible format first
            if 'choices' in data:
                for i, choice in enumerate(data.get('choices', [])):
                    message = choice.get('message', {})
                    content = message.get('content', '')
                    
                    result = {
                        'id': f"ai:{self.provider}:{i}:{query}",
                        'title': f"AI Response to: {query[:50]}{'...' if len(query) > 50 else ''}",
                        'content': content,
                        'model': self.model,
                        'source_type': 'ai',
                        'provider': self.provider,
                        'query': query,
                        'finish_reason': choice.get('finish_reason', '')
                    }
                    results.append(result)
            # Try direct response format
            elif 'response' in data:
                content = data.get('response', '')
                result = {
                    'id': f"ai:{self.provider}:0:{query}",
                    'title': f"AI Response to: {query[:50]}{'...' if len(query) > 50 else ''}",
                    'content': content,
                    'model': self.model,
                    'source_type': 'ai',
                    'provider': self.provider,
                    'query': query
                }
                results.append(result)
            # Fallback to raw response text
            else:
                result = {
                    'id': f"ai:{self.provider}:0:{query}",
                    'title': f"AI Response to: {query[:50]}{'...' if len(query) > 50 else ''}",
                    'content': str(data),
                    'model': self.model,
                    'source_type': 'ai',
                    'provider': self.provider,
                    'query': query
                }
                results.append(result)
            
            return results
        except ValueError:
            # If response is not JSON, return the raw text
            result = {
                'id': f"ai:{self.provider}:0:{query}",
                'title': f"AI Response to: {query[:50]}{'...' if len(query) > 50 else ''}",
                'content': response.text,
                'model': self.model,
                'source_type': 'ai',
                'provider': self.provider,
                'query': query
            }
            return [result]