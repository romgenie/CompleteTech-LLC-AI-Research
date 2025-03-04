"""
Academic Information Source.

This module provides implementation for academic sources like
ArXiv, PubMed, Semantic Scholar, etc.
"""

import logging
import requests
import time
from typing import Dict, List, Any, Optional, Union
from research_orchestrator.information_gathering.sources.base_source import BaseSource

logger = logging.getLogger(__name__)

class AcademicSource(BaseSource):
    """
    Academic information source for scholarly articles and papers.
    
    This class handles integration with academic databases and repositories
    to retrieve scientific papers and research articles.
    """
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize the academic source.
        
        Args:
            source_id: Unique identifier for this source.
            config: Configuration dictionary for the source.
        """
        super().__init__(source_id, config)
        self.source_type = 'academic'
        self.provider = config.get('provider', 'arxiv')
        self.base_url = config.get('base_url')
        self.last_request_time = 0
        
        # Set provider-specific base URLs if not explicitly configured
        if not self.base_url:
            if self.provider == 'arxiv':
                self.base_url = 'http://export.arxiv.org/api/query'
            elif self.provider == 'pubmed':
                self.base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
            elif self.provider == 'semantic_scholar':
                self.base_url = 'https://api.semanticscholar.org/v1'
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search the academic source for papers matching the query.
        
        Args:
            query: The search query.
            limit: Maximum number of results to return.
            
        Returns:
            A list of search result dictionaries.
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Prepare the query for this specific academic source
        processed_query = self.prepare_query(query)
        
        try:
            if self.provider == 'arxiv':
                return self._search_arxiv(processed_query, limit)
            elif self.provider == 'pubmed':
                return self._search_pubmed(processed_query, limit)
            elif self.provider == 'semantic_scholar':
                return self._search_semantic_scholar(processed_query, limit)
            else:
                logger.warning(f"Unsupported academic provider: {self.provider}")
                return []
        except Exception as e:
            logger.error(f"Error searching {self.provider}: {str(e)}")
            return []
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific academic document by ID.
        
        Args:
            document_id: The ID of the document to retrieve.
            
        Returns:
            The document as a dictionary.
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        try:
            if self.provider == 'arxiv':
                return self._get_arxiv_paper(document_id)
            elif self.provider == 'pubmed':
                return self._get_pubmed_paper(document_id)
            elif self.provider == 'semantic_scholar':
                return self._get_semantic_scholar_paper(document_id)
            else:
                logger.warning(f"Unsupported academic provider: {self.provider}")
                return {}
        except Exception as e:
            logger.error(f"Error retrieving document {document_id} from {self.provider}: {str(e)}")
            return {}
    
    def prepare_query(self, query: str) -> str:
        """
        Prepare a query for this specific academic source.
        
        Args:
            query: The original search query.
            
        Returns:
            Processed query string optimized for the academic source.
        """
        # Handle provider-specific query formatting
        if self.provider == 'arxiv':
            # ArXiv uses specific syntax for field-based searching
            return query.replace(' AND ', '+AND+').replace(' OR ', '+OR+').replace(' NOT ', '+NOT+')
        elif self.provider == 'pubmed':
            # PubMed uses specific syntax for field-based searching
            return query
        elif self.provider == 'semantic_scholar':
            # Semantic Scholar query formatting
            return query
        
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
    
    def _search_arxiv(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search ArXiv for papers.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Implementation would use ArXiv API
        # This is a placeholder - actual implementation would parse ArXiv XML responses
        
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': limit
        }
        
        # Record the query for result processing
        self._current_query = query
        
        response = requests.get(self.base_url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        # Parse ArXiv XML response (simplified for example)
        # In real implementation, would use a proper XML parser
        
        # Return formatted results
        return self._format_arxiv_results(response.text, limit)
    
    def _search_pubmed(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search PubMed for papers.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Implementation would use PubMed E-utilities API
        # This is a placeholder
        
        # Record the query for result processing
        self._current_query = query
        
        # First get IDs matching the query
        esearch_url = f"{self.base_url}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'retmode': 'json'
        }
        
        response = requests.get(esearch_url, params=params, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        ids = data.get('esearchresult', {}).get('idlist', [])
        
        if not ids:
            return []
        
        # Now fetch details for these IDs
        efetch_url = f"{self.base_url}/efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(ids),
            'retmode': 'xml'
        }
        
        fetch_response = requests.get(efetch_url, params=fetch_params, timeout=self.timeout)
        fetch_response.raise_for_status()
        
        # Parse PubMed XML response (simplified for example)
        # In real implementation, would use a proper XML parser
        
        # Return formatted results
        return self._format_pubmed_results(fetch_response.text, limit)
    
    def _search_semantic_scholar(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar for papers.
        
        Args:
            query: The processed search query.
            limit: Maximum number of results.
            
        Returns:
            List of search results.
        """
        # Implementation would use Semantic Scholar API
        # This is a placeholder
        
        # Record the query for result processing
        self._current_query = query
        
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        search_url = f"{self.base_url}/paper/search"
        params = {
            'query': query,
            'limit': limit
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        # Return formatted results
        return self._format_semantic_scholar_results(data, limit)
    
    def _get_arxiv_paper(self, paper_id: str) -> Dict[str, Any]:
        """
        Get a specific ArXiv paper by ID.
        
        Args:
            paper_id: The ArXiv paper ID.
            
        Returns:
            Paper details as a dictionary.
        """
        # Implementation would use ArXiv API to get a specific paper
        # This is a placeholder
        
        params = {
            'id_list': paper_id
        }
        
        response = requests.get(self.base_url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        # Parse ArXiv XML response (simplified for example)
        # In real implementation, would use a proper XML parser
        
        # Return formatted paper
        return self._format_arxiv_paper(response.text)
    
    def _get_pubmed_paper(self, paper_id: str) -> Dict[str, Any]:
        """
        Get a specific PubMed paper by ID.
        
        Args:
            paper_id: The PubMed paper ID.
            
        Returns:
            Paper details as a dictionary.
        """
        # Implementation would use PubMed E-utilities API to get a specific paper
        # This is a placeholder
        
        efetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': paper_id,
            'retmode': 'xml'
        }
        
        response = requests.get(efetch_url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        # Parse PubMed XML response (simplified for example)
        # In real implementation, would use a proper XML parser
        
        # Return formatted paper
        return self._format_pubmed_paper(response.text)
    
    def _get_semantic_scholar_paper(self, paper_id: str) -> Dict[str, Any]:
        """
        Get a specific Semantic Scholar paper by ID.
        
        Args:
            paper_id: The Semantic Scholar paper ID.
            
        Returns:
            Paper details as a dictionary.
        """
        # Implementation would use Semantic Scholar API to get a specific paper
        # This is a placeholder
        
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        paper_url = f"{self.base_url}/paper/{paper_id}"
        
        response = requests.get(paper_url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()
        
        # Return formatted paper
        return self._format_semantic_scholar_paper(data)
    
    def _format_arxiv_results(self, xml_content: str, limit: int) -> List[Dict[str, Any]]:
        """
        Format ArXiv search results.
        
        Args:
            xml_content: The XML response from ArXiv.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        # This would be a proper XML parser implementation
        # Simplified for example
        
        # In a real implementation, we would parse the XML properly
        # For now, just return a placeholder
        
        return [
            {
                'id': f'arxiv:2101.{i:05d}',
                'title': f'Sample ArXiv Paper {i}',
                'authors': ['Author A', 'Author B'],
                'abstract': f'This is a sample abstract for paper {i} related to {self._current_query}',
                'url': f'https://arxiv.org/abs/2101.{i:05d}',
                'published_date': '2023-01-15',
                'source_type': 'academic',
                'query': self._current_query
            }
            for i in range(1, min(limit + 1, 6))
        ]
    
    def _format_pubmed_results(self, xml_content: str, limit: int) -> List[Dict[str, Any]]:
        """
        Format PubMed search results.
        
        Args:
            xml_content: The XML response from PubMed.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        # This would be a proper XML parser implementation
        # Simplified for example
        
        return [
            {
                'id': f'pubmed:{123456 + i}',
                'title': f'Sample PubMed Paper {i}',
                'authors': ['Researcher C', 'Researcher D'],
                'abstract': f'This is a sample abstract for medical paper {i} related to {self._current_query}',
                'url': f'https://pubmed.ncbi.nlm.nih.gov/{123456 + i}/',
                'published_date': '2022-10-20',
                'journal': 'Journal of Medical Research',
                'source_type': 'academic',
                'query': self._current_query
            }
            for i in range(1, min(limit + 1, 6))
        ]
    
    def _format_semantic_scholar_results(self, data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Format Semantic Scholar search results.
        
        Args:
            data: The JSON response from Semantic Scholar.
            limit: Maximum number of results.
            
        Returns:
            List of formatted search results.
        """
        # This would process the actual Semantic Scholar JSON response
        # Simplified for example
        
        # Let's assume data has a 'papers' key with the results
        papers = data.get('papers', [])
        results = []
        
        for i, paper in enumerate(papers[:limit]):
            result = {
                'id': paper.get('paperId', f'ss:{789012 + i}'),
                'title': paper.get('title', f'Sample Semantic Scholar Paper {i}'),
                'authors': [author.get('name', f'Author {j}') for j, author in enumerate(paper.get('authors', []))],
                'abstract': paper.get('abstract', f'This is a sample abstract for paper {i} related to {self._current_query}'),
                'url': paper.get('url', f'https://www.semanticscholar.org/paper/{789012 + i}'),
                'published_date': paper.get('year', '2021'),
                'citation_count': paper.get('citationCount', i * 10),
                'source_type': 'academic',
                'query': self._current_query
            }
            results.append(result)
        
        # If no real data, return placeholders
        if not results:
            results = [
                {
                    'id': f'ss:{789012 + i}',
                    'title': f'Sample Semantic Scholar Paper {i}',
                    'authors': ['Scientist E', 'Scientist F'],
                    'abstract': f'This is a sample abstract for paper {i} related to {self._current_query}',
                    'url': f'https://www.semanticscholar.org/paper/{789012 + i}',
                    'published_date': '2022-05-18',
                    'citation_count': i * 10,
                    'source_type': 'academic',
                    'query': self._current_query
                }
                for i in range(1, min(limit + 1, 6))
            ]
        
        return results
    
    def _format_arxiv_paper(self, xml_content: str) -> Dict[str, Any]:
        """
        Format a single ArXiv paper.
        
        Args:
            xml_content: The XML response from ArXiv.
            
        Returns:
            Formatted paper dictionary.
        """
        # This would be a proper XML parser implementation
        # Simplified for example
        
        return {
            'id': 'arxiv:2101.12345',
            'title': 'Sample ArXiv Paper',
            'authors': ['Author A', 'Author B'],
            'abstract': 'This is a sample abstract for a detailed ArXiv paper.',
            'full_text': 'This would be the full text of the paper, obtained from the PDF.',
            'url': 'https://arxiv.org/abs/2101.12345',
            'pdf_url': 'https://arxiv.org/pdf/2101.12345.pdf',
            'published_date': '2023-01-15',
            'categories': ['cs.AI', 'cs.LG'],
            'source_type': 'academic'
        }
    
    def _format_pubmed_paper(self, xml_content: str) -> Dict[str, Any]:
        """
        Format a single PubMed paper.
        
        Args:
            xml_content: The XML response from PubMed.
            
        Returns:
            Formatted paper dictionary.
        """
        # This would be a proper XML parser implementation
        # Simplified for example
        
        return {
            'id': 'pubmed:123456',
            'title': 'Sample PubMed Paper',
            'authors': ['Researcher C', 'Researcher D'],
            'abstract': 'This is a sample abstract for a detailed PubMed paper.',
            'full_text': 'This would be the full text of the paper, if available.',
            'url': 'https://pubmed.ncbi.nlm.nih.gov/123456/',
            'published_date': '2022-10-20',
            'journal': 'Journal of Medical Research',
            'volume': '45',
            'issue': '3',
            'pages': '123-145',
            'doi': '10.1234/jmr.2022.45.3.123',
            'mesh_terms': ['Term1', 'Term2', 'Term3'],
            'source_type': 'academic'
        }
    
    def _format_semantic_scholar_paper(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a single Semantic Scholar paper.
        
        Args:
            data: The JSON response from Semantic Scholar.
            
        Returns:
            Formatted paper dictionary.
        """
        # This would process the actual Semantic Scholar JSON response
        # Simplified for example
        
        return {
            'id': data.get('paperId', 'ss:789012'),
            'title': data.get('title', 'Sample Semantic Scholar Paper'),
            'authors': [author.get('name', f'Author {i}') for i, author in enumerate(data.get('authors', []))],
            'abstract': data.get('abstract', 'This is a sample abstract for a detailed Semantic Scholar paper.'),
            'full_text': data.get('tldr', {}).get('text', 'Full text not available'),
            'url': data.get('url', 'https://www.semanticscholar.org/paper/789012'),
            'published_date': str(data.get('year', '2021')),
            'venue': data.get('venue', 'Unknown Venue'),
            'citation_count': data.get('citationCount', 42),
            'reference_count': data.get('referenceCount', 35),
            'fields_of_study': data.get('fieldsOfStudy', ['Computer Science', 'Artificial Intelligence']),
            'source_type': 'academic'
        }