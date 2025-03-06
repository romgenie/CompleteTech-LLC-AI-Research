"""
Code Repository Source.

This module provides implementation for accessing code repositories
like GitHub, GitLab, Hugging Face, PyPI, etc.
"""

import logging
import requests
import time
import json
import base64
from typing import Dict, List, Any, Optional, Union
from urllib.parse import quote_plus
from src.research_orchestrator.information_gathering.sources.base_source import BaseSource

logger = logging.getLogger(__name__)

class CodeSource(BaseSource):
    """
    Code repository information source.
    
    This class handles integration with code repositories and registries
    to retrieve code examples, libraries, and documentation.
    """
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize the code source.
        
        Args:
            source_id: Unique identifier for this source.
            config: Configuration dictionary for the source.
        """
        super().__init__(source_id, config)
        self.source_type = 'code'
        self.provider = config.get('provider', 'github')
        self.base_url = config.get('base_url')
        self.last_request_time = 0
        
        # Set provider-specific base URLs if not explicitly configured
        if not self.base_url:
            if self.provider == 'github':
                self.base_url = 'https://api.github.com'
            elif self.provider == 'gitlab':
                self.base_url = 'https://gitlab.com/api/v4'
            elif self.provider == 'huggingface':
                self.base_url = 'https://huggingface.co/api'
            elif self.provider == 'pypi':
                self.base_url = 'https://pypi.org/pypi'
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search the code source for repositories matching the query.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of search result dictionaries.
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Prepare the query for this specific code source
        processed_query = self.prepare_query(query)
        
        try:
            if self.provider == 'github':
                return self._search_github(processed_query, limit)
            elif self.provider == 'gitlab':
                return self._search_gitlab(processed_query, limit)
            elif self.provider == 'huggingface':
                return self._search_huggingface(processed_query, limit)
            elif self.provider == 'pypi':
                return self._search_pypi(processed_query, limit)
            else:
                logger.warning(f"Unsupported code provider: {self.provider}")
                return []
        except Exception as e:
            logger.error(f"Error searching {self.provider}: {str(e)}")
            return []
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific code document by ID.
        
        Args:
            document_id: The ID of the document to retrieve. Can be a 
                       repository ID, file path, or other identifier.
            
        Returns:
            The document as a dictionary.
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        try:
            if self.provider == 'github':
                return self._get_github_document(document_id)
            elif self.provider == 'gitlab':
                return self._get_gitlab_document(document_id)
            elif self.provider == 'huggingface':
                return self._get_huggingface_document(document_id)
            elif self.provider == 'pypi':
                return self._get_pypi_document(document_id)
            else:
                logger.warning(f"Unsupported code provider: {self.provider}")
                return {}
        except Exception as e:
            logger.error(f"Error retrieving document {document_id} from {self.provider}: {str(e)}")
            return {}
    
    def prepare_query(self, query: str) -> str:
        """
        Prepare a query for this specific code source.
        
        Args:
            query: The original search query.
            
        Returns:
            Processed query string optimized for the code source.
        """
        # Handle provider-specific query formatting
        if self.provider == 'github':
            # GitHub search uses specific syntax for advanced search
            if 'language:' not in query and self.config.get('default_language'):
                query += f" language:{self.config['default_language']}"
                
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
    
    def _search_github(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search GitHub for repositories.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'token {self.api_key}'
            
        # Search for repositories
        search_url = f"{self.base_url}/search/repositories"
        params = {
            'q': query,
            'per_page': limit,
            'sort': 'stars',
            'order': 'desc'
        }
        
        response = requests.get(
            search_url, 
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_github_repo_results(data, limit)
    
    def _search_gitlab(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search GitLab for repositories.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {}
        if self.api_key:
            headers['PRIVATE-TOKEN'] = self.api_key
            
        # Search for projects
        search_url = f"{self.base_url}/projects"
        params = {
            'search': query,
            'per_page': limit,
            'order_by': 'stars',
            'sort': 'desc'
        }
        
        response = requests.get(
            search_url, 
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_gitlab_repo_results(data, limit)
    
    def _search_huggingface(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search Hugging Face for models.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        # Search for models
        search_url = f"{self.base_url}/models"
        params = {
            'search': query,
            'limit': limit
        }
        
        response = requests.get(
            search_url, 
            headers=headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_huggingface_model_results(data, limit)
    
    def _search_pypi(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search PyPI for packages.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Record the query for result processing
        self._current_query = query
        
        # Search for packages
        search_url = f"https://pypi.org/search/"
        params = {
            'q': query
        }
        
        response = requests.get(
            search_url, 
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        # PyPI doesn't have a proper API for search, so we'd need to parse HTML
        # This is a simplified placeholder implementation
        
        # Return placeholder results
        return self._format_pypi_package_results(None, limit)
    
    def _get_github_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a specific GitHub document.
        
        Args:
            document_id: Can be a repository name, file path, or other identifier.
            
        Returns:
            Document details as a dictionary.
        """
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'token {self.api_key}'
            
        # Check if the document_id looks like a repo or a file path
        if '/' in document_id and len(document_id.split('/')) == 2:
            # Looks like a repo path (user/repo)
            repo_url = f"{self.base_url}/repos/{document_id}"
            
            response = requests.get(
                repo_url, 
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            repo_data = response.json()
            
            # Get README content
            readme_url = f"{self.base_url}/repos/{document_id}/readme"
            try:
                readme_response = requests.get(
                    readme_url, 
                    headers=headers,
                    timeout=self.timeout
                )
                readme_response.raise_for_status()
                readme_data = readme_response.json()
                
                # Decode content
                if 'content' in readme_data and readme_data.get('encoding') == 'base64':
                    readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
                else:
                    readme_content = "README content not available"
            except Exception as e:
                logger.warning(f"Error fetching README for {document_id}: {str(e)}")
                readme_content = "README content not available"
                
            # Format the result
            return {
                'id': repo_data.get('id', ''),
                'name': repo_data.get('name', ''),
                'full_name': repo_data.get('full_name', ''),
                'description': repo_data.get('description', ''),
                'url': repo_data.get('html_url', ''),
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'language': repo_data.get('language', ''),
                'readme': readme_content,
                'owner': repo_data.get('owner', {}).get('login', ''),
                'created_at': repo_data.get('created_at', ''),
                'updated_at': repo_data.get('updated_at', ''),
                'license': repo_data.get('license', {}).get('name', 'No license information'),
                'topics': repo_data.get('topics', []),
                'source_type': 'code',
                'provider': 'github'
            }
        else:
            # Assume it's a content path (user/repo/path/to/file)
            parts = document_id.split('/', 3)
            if len(parts) < 4:
                raise ValueError(f"Invalid GitHub document path: {document_id}")
                
            owner, repo, _, path = parts
            content_url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
            
            response = requests.get(
                content_url, 
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Decode content
            if 'content' in data and data.get('encoding') == 'base64':
                content = base64.b64decode(data['content']).decode('utf-8')
            else:
                content = "Content not available"
                
            # Format the result
            return {
                'id': document_id,
                'name': data.get('name', ''),
                'path': data.get('path', ''),
                'url': data.get('html_url', ''),
                'content': content,
                'size': data.get('size', 0),
                'type': data.get('type', 'file'),
                'encoding': data.get('encoding', ''),
                'sha': data.get('sha', ''),
                'source_type': 'code',
                'provider': 'github'
            }
    
    def _get_gitlab_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a specific GitLab document.
        
        Args:
            document_id: Can be a project ID, file path, or other identifier.
            
        Returns:
            Document details as a dictionary.
        """
        headers = {}
        if self.api_key:
            headers['PRIVATE-TOKEN'] = self.api_key
            
        # Try to parse the document_id
        if document_id.isdigit():
            # It's a project ID
            project_url = f"{self.base_url}/projects/{document_id}"
            
            response = requests.get(
                project_url, 
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            project_data = response.json()
            
            # Get README content if possible
            readme_url = f"{self.base_url}/projects/{document_id}/repository/files/README.md"
            try:
                readme_response = requests.get(
                    readme_url, 
                    headers=headers,
                    params={'ref': 'master'},
                    timeout=self.timeout
                )
                readme_response.raise_for_status()
                readme_data = readme_response.json()
                
                # Decode content
                if 'content' in readme_data and readme_data.get('encoding') == 'base64':
                    readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
                else:
                    readme_content = "README content not available"
            except Exception as e:
                logger.warning(f"Error fetching README for {document_id}: {str(e)}")
                readme_content = "README content not available"
                
            # Format the result
            return {
                'id': project_data.get('id', ''),
                'name': project_data.get('name', ''),
                'path_with_namespace': project_data.get('path_with_namespace', ''),
                'description': project_data.get('description', ''),
                'url': project_data.get('web_url', ''),
                'stars': project_data.get('star_count', 0),
                'forks': project_data.get('forks_count', 0),
                'readme': readme_content,
                'created_at': project_data.get('created_at', ''),
                'last_activity_at': project_data.get('last_activity_at', ''),
                'source_type': 'code',
                'provider': 'gitlab'
            }
        else:
            # Try to parse as a file path
            # Format should be: project_id/filepath
            parts = document_id.split('/', 1)
            if len(parts) < 2:
                raise ValueError(f"Invalid GitLab document path: {document_id}")
                
            project_id, file_path = parts
            
            # URL encode the file path
            encoded_path = quote_plus(file_path)
            file_url = f"{self.base_url}/projects/{project_id}/repository/files/{encoded_path}"
            
            response = requests.get(
                file_url, 
                headers=headers,
                params={'ref': 'master'},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Decode content
            if 'content' in data and data.get('encoding') == 'base64':
                content = base64.b64decode(data['content']).decode('utf-8')
            else:
                content = "Content not available"
                
            # Format the result
            return {
                'id': document_id,
                'name': data.get('file_name', ''),
                'path': data.get('file_path', ''),
                'content': content,
                'size': data.get('size', 0),
                'encoding': data.get('encoding', ''),
                'content_sha256': data.get('content_sha256', ''),
                'ref': data.get('ref', ''),
                'source_type': 'code',
                'provider': 'gitlab'
            }
    
    def _get_huggingface_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a specific Hugging Face model or dataset.
        
        Args:
            document_id: The model or dataset ID.
            
        Returns:
            Document details as a dictionary.
        """
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            
        # Determine if it's a model or dataset
        if '/' in document_id:
            # Check for model first
            model_url = f"{self.base_url}/models/{document_id}"
            
            try:
                response = requests.get(
                    model_url, 
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # It's a model
                return {
                    'id': document_id,
                    'name': data.get('modelId', document_id),
                    'description': data.get('description', ''),
                    'url': f"https://huggingface.co/{document_id}",
                    'downloads': data.get('downloads', 0),
                    'likes': data.get('likes', 0),
                    'author': data.get('author', ''),
                    'tags': data.get('tags', []),
                    'pipeline_tag': data.get('pipeline_tag', ''),
                    'source_type': 'code',
                    'provider': 'huggingface',
                    'type': 'model'
                }
            except requests.exceptions.HTTPError:
                # Try as a dataset
                dataset_url = f"{self.base_url}/datasets/{document_id}"
                
                try:
                    response = requests.get(
                        dataset_url, 
                        headers=headers,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # It's a dataset
                    return {
                        'id': document_id,
                        'name': data.get('id', document_id),
                        'description': data.get('description', ''),
                        'url': f"https://huggingface.co/datasets/{document_id}",
                        'downloads': data.get('downloads', 0),
                        'author': data.get('author', ''),
                        'citation': data.get('citation', ''),
                        'source_type': 'code',
                        'provider': 'huggingface',
                        'type': 'dataset'
                    }
                except requests.exceptions.HTTPError:
                    logger.error(f"Document not found on Hugging Face: {document_id}")
                    return {}
        else:
            logger.error(f"Invalid Hugging Face document ID: {document_id}")
            return {}
    
    def _get_pypi_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a specific PyPI package.
        
        Args:
            document_id: The package name.
            
        Returns:
            Document details as a dictionary.
        """
        # PyPI has a JSON API for package info
        package_url = f"{self.base_url}/{document_id}/json"
        
        response = requests.get(package_url, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        info = data.get('info', {})
        latest_version = info.get('version', '')
        releases = data.get('releases', {})
        latest_release_info = releases.get(latest_version, [{}])[0] if latest_version in releases else {}
        
        return {
            'id': document_id,
            'name': info.get('name', document_id),
            'version': latest_version,
            'summary': info.get('summary', ''),
            'description': info.get('description', ''),
            'url': info.get('project_url', ''),
            'author': info.get('author', ''),
            'author_email': info.get('author_email', ''),
            'license': info.get('license', ''),
            'requires_python': info.get('requires_python', ''),
            'keywords': info.get('keywords', ''),
            'classifiers': info.get('classifiers', []),
            'upload_time': latest_release_info.get('upload_time', ''),
            'package_size': latest_release_info.get('size', 0),
            'python_version': latest_release_info.get('python_version', ''),
            'downloads': {
                'last_day': -1,  # Not available in the API
                'last_week': -1,
                'last_month': -1
            },
            'source_type': 'code',
            'provider': 'pypi'
        }
    
    def _format_github_repo_results(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Format GitHub repository search results.
        
        Args:
            data: The JSON response from GitHub.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        items = data.get('items', [])
        for i, item in enumerate(items[:limit]):
            result = {
                'id': f"github:{item.get('id', i)}",
                'name': item.get('name', ''),
                'full_name': item.get('full_name', ''),
                'description': item.get('description', ''),
                'url': item.get('html_url', ''),
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'language': item.get('language', ''),
                'query': self._current_query,
                'owner': item.get('owner', {}).get('login', ''),
                'created_at': item.get('created_at', ''),
                'updated_at': item.get('updated_at', ''),
                'source_type': 'code',
                'provider': 'github'
            }
            results.append(result)
            
        return results
    
    def _format_gitlab_repo_results(self, data: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """
        Format GitLab repository search results.
        
        Args:
            data: The JSON response from GitLab.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        for i, item in enumerate(data[:limit]):
            result = {
                'id': f"gitlab:{item.get('id', i)}",
                'name': item.get('name', ''),
                'path_with_namespace': item.get('path_with_namespace', ''),
                'description': item.get('description', ''),
                'url': item.get('web_url', ''),
                'stars': item.get('star_count', 0),
                'forks': item.get('forks_count', 0),
                'query': self._current_query,
                'created_at': item.get('created_at', ''),
                'last_activity_at': item.get('last_activity_at', ''),
                'source_type': 'code',
                'provider': 'gitlab'
            }
            results.append(result)
            
        return results
    
    def _format_huggingface_model_results(self, data: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """
        Format Hugging Face model search results.
        
        Args:
            data: The JSON response from Hugging Face.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        results = []
        
        for i, item in enumerate(data[:limit]):
            result = {
                'id': f"huggingface:{item.get('modelId', i)}",
                'name': item.get('modelId', ''),
                'description': item.get('description', ''),
                'url': f"https://huggingface.co/{item.get('modelId', '')}",
                'downloads': item.get('downloads', 0),
                'likes': item.get('likes', 0),
                'query': self._current_query,
                'author': item.get('author', ''),
                'tags': item.get('tags', []),
                'pipeline_tag': item.get('pipeline_tag', ''),
                'source_type': 'code',
                'provider': 'huggingface'
            }
            results.append(result)
            
        return results
    
    def _format_pypi_package_results(self, data: Any, limit: int) -> List[Dict[str, Any]]:
        """
        Format PyPI package search results.
        
        Args:
            data: The response from PyPI.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        # Since PyPI doesn't have a proper search API, we're creating placeholder results
        # In a real implementation, this would parse the HTML results or use a third-party API
        
        # Generate placeholder results
        results = []
        packages = [
            {"name": f"ai-{self._current_query.replace(' ', '-')}", "description": f"AI library for {self._current_query}"},
            {"name": f"py{self._current_query.replace(' ', '')}", "description": f"Python implementation of {self._current_query}"},
            {"name": f"{self._current_query.replace(' ', '_')}-tools", "description": f"Toolkit for working with {self._current_query}"},
            {"name": f"{self._current_query.replace(' ', '').lower()}", "description": f"Implementation of {self._current_query} algorithms"},
            {"name": f"deep-{self._current_query.replace(' ', '-')}", "description": f"Deep learning approach to {self._current_query}"}
        ]
        
        for i, package in enumerate(packages[:limit]):
            result = {
                'id': f"pypi:{package['name']}",
                'name': package['name'],
                'description': package['description'],
                'url': f"https://pypi.org/project/{package['name']}/",
                'query': self._current_query,
                'source_type': 'code',
                'provider': 'pypi'
            }
            results.append(result)
            
        return results