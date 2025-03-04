"""
Quality Assessor for the Information Gathering Module.

This module assesses the quality of search results based on 
various criteria to prioritize the most relevant and reliable information.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

class QualityAssessor:
    """
    Assesses the quality of search results.
    
    This class evaluates search results based on multiple quality dimensions
    including relevance, recency, authority, and completeness.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the quality assessor.
        
        Args:
            config: Configuration dictionary with quality assessment settings.
        """
        self.config = config
        self.metric_weights = config.get('metric_weights', {
            'relevance': 0.4,
            'recency': 0.2,
            'authority': 0.2,
            'completeness': 0.2
        })
        
        # Make sure weights sum to 1.0
        total_weight = sum(self.metric_weights.values())
        if total_weight != 1.0:
            for key in self.metric_weights:
                self.metric_weights[key] /= total_weight
    
    def assess_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assess the quality of search results.
        
        Args:
            results: List of search result dictionaries.
            
        Returns:
            The same list with quality scores added.
        """
        assessed_results = []
        
        for result in results:
            quality_scores = self._assess_result(result)
            result.update(quality_scores)
            assessed_results.append(result)
        
        return assessed_results
    
    def _assess_result(self, result: Dict[str, Any]) -> Dict[str, float]:
        """
        Assess the quality of a single search result.
        
        Args:
            result: A search result dictionary.
            
        Returns:
            Dictionary with quality scores.
        """
        relevance_score = self._assess_relevance(result)
        recency_score = self._assess_recency(result)
        authority_score = self._assess_authority(result)
        completeness_score = self._assess_completeness(result)
        
        # Calculate weighted composite score
        quality_score = (
            self.metric_weights['relevance'] * relevance_score +
            self.metric_weights['recency'] * recency_score +
            self.metric_weights['authority'] * authority_score +
            self.metric_weights['completeness'] * completeness_score
        )
        
        return {
            'quality_score': quality_score,
            'relevance_score': relevance_score,
            'recency_score': recency_score,
            'authority_score': authority_score,
            'completeness_score': completeness_score
        }
    
    def _assess_relevance(self, result: Dict[str, Any]) -> float:
        """
        Assess the relevance of a search result.
        
        Args:
            result: A search result dictionary.
            
        Returns:
            Relevance score between 0.0 and 1.0.
        """
        # Basic implementation - can be enhanced with more sophisticated algorithms
        relevance = result.get('relevance', 0.0)
        
        # If no explicit relevance score provided, estimate from other fields
        if relevance == 0.0:
            # Use the source's relevance score if available
            if 'source_relevance' in result:
                relevance = result['source_relevance']
            # Otherwise, estimate based on title/snippet match with query terms
            elif 'query' in result and ('title' in result or 'snippet' in result):
                query_terms = set(result['query'].lower().split())
                
                # Check title for matches
                title_score = 0.0
                if 'title' in result:
                    title_terms = set(result['title'].lower().split())
                    if query_terms and title_terms:
                        matches = len(query_terms.intersection(title_terms))
                        title_score = min(1.0, matches / len(query_terms))
                
                # Check snippet for matches
                snippet_score = 0.0
                if 'snippet' in result:
                    snippet_terms = set(result['snippet'].lower().split())
                    if query_terms and snippet_terms:
                        matches = len(query_terms.intersection(snippet_terms))
                        snippet_score = min(1.0, matches / len(query_terms))
                
                # Combine scores with title having higher weight
                relevance = title_score * 0.6 + snippet_score * 0.4
        
        return max(0.0, min(1.0, relevance))
    
    def _assess_recency(self, result: Dict[str, Any]) -> float:
        """
        Assess the recency of a search result.
        
        Args:
            result: A search result dictionary.
            
        Returns:
            Recency score between 0.0 and 1.0.
        """
        # Check if result has date information
        if 'date' not in result and 'published_date' not in result:
            # No date info, return neutral score
            return 0.5
        
        date_str = result.get('date') or result.get('published_date')
        
        try:
            # Try to parse the date
            date_formats = [
                '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y',
                '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                # No matching format found
                return 0.5
            
            # Calculate age in days
            age_days = (datetime.now() - date).days
            
            # Score based on recency tiers
            if age_days < 7:  # Within a week
                return 1.0
            elif age_days < 30:  # Within a month
                return 0.9
            elif age_days < 90:  # Within 3 months
                return 0.8
            elif age_days < 365:  # Within a year
                return 0.6
            elif age_days < 730:  # Within 2 years
                return 0.4
            elif age_days < 1825:  # Within 5 years
                return 0.2
            else:  # Older than 5 years
                return 0.1
                
        except Exception:
            # Failed to process date
            return 0.5
    
    def _assess_authority(self, result: Dict[str, Any]) -> float:
        """
        Assess the authority/credibility of a search result.
        
        Args:
            result: A search result dictionary.
            
        Returns:
            Authority score between 0.0 and 1.0.
        """
        # Check for explicit authority score
        if 'authority' in result:
            return max(0.0, min(1.0, result['authority']))
        
        # Check source reputation
        source_id = result.get('source_id', '')
        source_name = result.get('source_name', '')
        
        # Default score based on source type
        score = 0.5
        
        # Academic sources generally have higher authority
        if 'arxiv' in source_id.lower() or 'pubmed' in source_id.lower():
            score = 0.8
        elif 'github' in source_id.lower():
            score = 0.7
        
        # Adjust based on domain if URL is present
        url = result.get('url', '')
        
        # Academic and government domains tend to be more authoritative
        if url.endswith('.edu') or url.endswith('.gov'):
            score = max(score, 0.85)
        elif url.endswith('.org'):
            score = max(score, 0.7)
            
        # Consider citation count if available
        if 'citation_count' in result:
            citation_count = result['citation_count']
            if citation_count > 100:
                citation_score = 1.0
            elif citation_count > 50:
                citation_score = 0.9
            elif citation_count > 20:
                citation_score = 0.8
            elif citation_count > 10:
                citation_score = 0.7
            elif citation_count > 5:
                citation_score = 0.6
            else:
                citation_score = 0.5
                
            # Combine scores
            score = (score + citation_score) / 2
                
        return max(0.0, min(1.0, score))
    
    def _assess_completeness(self, result: Dict[str, Any]) -> float:
        """
        Assess the completeness of a search result.
        
        Args:
            result: A search result dictionary.
            
        Returns:
            Completeness score between 0.0 and 1.0.
        """
        # Start with base score
        score = 0.5
        
        # Required fields for a complete result
        required_fields = ['title', 'url']
        optional_fields = ['snippet', 'date', 'author', 'publisher']
        
        # Calculate score based on field presence
        required_count = sum(1 for field in required_fields if field in result)
        optional_count = sum(1 for field in optional_fields if field in result)
        
        if len(required_fields) > 0:
            # Required fields have higher weight
            required_score = required_count / len(required_fields)
        else:
            required_score = 1.0
            
        if len(optional_fields) > 0:
            # Optional fields have lower weight
            optional_score = optional_count / len(optional_fields)
        else:
            optional_score = 1.0
        
        # Weight required fields more heavily
        score = required_score * 0.7 + optional_score * 0.3
        
        # Bonus for content length if available
        if 'content_length' in result:
            length = result['content_length']
            if length > 5000:  # Long, detailed content
                score = min(1.0, score + 0.2)
            elif length > 2000:  # Moderate length
                score = min(1.0, score + 0.1)
                
        return max(0.0, min(1.0, score))