"""
Citation management system for research generation.

This module provides the core functionality for citation management,
including in-text citations, reference lists, and citation validation.
"""

import logging
import re
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union, Set, Tuple
import json
import os
from datetime import datetime
import hashlib

from .citation_formatter import CitationStyle, format_citation, format_reference, format_reference_list

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitationManager:
    """
    Citation Manager for handling citations and references in research documents.
    
    The Citation Manager maintains a database of papers, generates in-text citations
    and reference lists, performs citation validation, and interacts with external
    services like DOI and CrossRef.
    """
    
    def __init__(self, 
                 style: Union[CitationStyle, str] = CitationStyle.APA,
                 knowledge_graph_adapter = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the Citation Manager.
        
        Args:
            style: Citation style to use for formatting citations and references
            knowledge_graph_adapter: Adapter for accessing the knowledge graph
            cache_dir: Directory for caching paper metadata
        """
        # Set citation style
        if isinstance(style, str):
            self.style = CitationStyle.from_string(style)
        else:
            self.style = style
            
        self.knowledge_graph_adapter = knowledge_graph_adapter
        
        # Set cache directory
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "cache",
                "citations"
            )
            
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize citation database
        self.papers: List[Dict[str, Any]] = []
        self.citations: Dict[str, int] = {}  # Map citation keys to paper indices
        self.citation_count: int = 0
        self.logger = logging.getLogger(__name__)
    
    def load_papers_from_research_data(self, research_data: Dict[str, Any]) -> None:
        """
        Load papers from research data.
        
        Args:
            research_data: Research data containing paper information
        """
        if "papers" in research_data and isinstance(research_data["papers"], list):
            for paper in research_data["papers"]:
                self.add_paper(paper)
    
    def add_paper(self, paper: Dict[str, Any]) -> str:
        """
        Add a paper to the citation database.
        
        Args:
            paper: Paper metadata dictionary
            
        Returns:
            Citation key for the added paper
        """
        # Generate citation key if not provided
        if "citation_key" not in paper:
            paper["citation_key"] = self._generate_citation_key(paper)
        
        # Add paper to database
        self.papers.append(paper)
        paper_index = len(self.papers) - 1
        
        # Update citation mapping
        citation_key = paper["citation_key"]
        self.citations[citation_key] = paper_index
        
        # Save to cache
        self._save_paper_to_cache(paper)
        
        return citation_key
    
    def get_paper(self, citation_key: str) -> Optional[Dict[str, Any]]:
        """
        Get a paper by its citation key.
        
        Args:
            citation_key: Citation key for the paper
            
        Returns:
            Paper metadata dictionary if found, None otherwise
        """
        if citation_key in self.citations:
            paper_index = self.citations[citation_key]
            return self.papers[paper_index]
        
        # Try to load from cache
        paper = self._load_paper_from_cache(citation_key)
        if paper:
            self.add_paper(paper)
            return paper
        
        return None
    
    def add_citation(self, citation_key: str, context: Optional[str] = None) -> str:
        """
        Add a citation to the document and return the formatted in-text citation.
        
        Args:
            citation_key: Citation key for the paper
            context: Optional context information for the citation
            
        Returns:
            Formatted in-text citation
        """
        paper = self.get_paper(citation_key)
        
        if not paper:
            # Try to fetch paper from knowledge graph
            if self.knowledge_graph_adapter:
                try:
                    kg_paper = self._fetch_paper_from_knowledge_graph(citation_key)
                    if kg_paper:
                        paper = kg_paper
                        self.add_paper(paper)
                except Exception as e:
                    self.logger.error(f"Error fetching paper from knowledge graph: {e}")
        
        if not paper:
            # Paper not found
            self.logger.warning(f"Citation key not found: {citation_key}")
            return f"([?])"
        
        # Increment citation count
        self.citation_count += 1
        
        # For numbered citation styles, update citation ID
        if self.style in [CitationStyle.IEEE, CitationStyle.VANCOUVER]:
            paper["citation_id"] = self.citation_count
        
        # Format citation
        citation = format_citation(paper, self.style)
        
        return citation
    
    def generate_reference_list(self, title: str = "References") -> str:
        """
        Generate a formatted reference list for all cited papers.
        
        Args:
            title: Title for the reference section
            
        Returns:
            Formatted reference list as a string
        """
        # Get list of cited papers
        cited_papers = self.papers
        
        # Format reference list
        return format_reference_list(cited_papers, self.style, title)
    
    def validate_citations(self) -> List[Dict[str, Any]]:
        """
        Validate citations and identify potential issues.
        
        Returns:
            List of validation issues
        """
        validation_issues = []
        
        for paper in self.papers:
            # Check for missing required fields
            required_fields = ["title", "authors", "year"]
            for field in required_fields:
                if field not in paper or not paper[field]:
                    validation_issues.append({
                        "paper": paper.get("citation_key", "Unknown"),
                        "issue": f"Missing required field: {field}",
                        "severity": "error"
                    })
            
            # Check for incomplete fields
            recommended_fields = ["journal", "doi", "url"]
            for field in recommended_fields:
                if field not in paper or not paper[field]:
                    validation_issues.append({
                        "paper": paper.get("citation_key", "Unknown"),
                        "issue": f"Missing recommended field: {field}",
                        "severity": "warning"
                    })
            
            # Check for invalid DOI format
            if "doi" in paper and paper["doi"]:
                doi = paper["doi"]
                if not self._is_valid_doi(doi):
                    validation_issues.append({
                        "paper": paper.get("citation_key", "Unknown"),
                        "issue": f"Invalid DOI format: {doi}",
                        "severity": "warning"
                    })
            
            # Check for invalid URL format
            if "url" in paper and paper["url"]:
                url = paper["url"]
                if not self._is_valid_url(url):
                    validation_issues.append({
                        "paper": paper.get("citation_key", "Unknown"),
                        "issue": f"Invalid URL format: {url}",
                        "severity": "warning"
                    })
            
            # Check for invalid year format
            if "year" in paper and paper["year"]:
                year = paper["year"]
                if not self._is_valid_year(year):
                    validation_issues.append({
                        "paper": paper.get("citation_key", "Unknown"),
                        "issue": f"Invalid year format: {year}",
                        "severity": "error"
                    })
        
        return validation_issues
    
    def process_text_with_citations(self, text: str) -> str:
        """
        Process text with citation placeholders and replace them with actual citations.
        
        Args:
            text: Text with citation placeholders
            
        Returns:
            Processed text with formatted citations
        """
        # Define citation placeholder pattern
        # Format: [@citation_key] or [@citation_key:context]
        pattern = r'\[@([^:\]]+)(?::([^\]]+))?\]'
        
        # Find all citation placeholders
        matches = re.finditer(pattern, text)
        
        # Replace placeholders with formatted citations
        processed_text = text
        for match in reversed(list(matches)):  # Process from end to start to avoid index issues
            full_match = match.group(0)
            citation_key = match.group(1)
            context = match.group(2) if match.group(2) else None
            
            # Generate citation
            citation = self.add_citation(citation_key, context)
            
            # Replace placeholder with citation
            start, end = match.span()
            processed_text = processed_text[:start] + citation + processed_text[end:]
        
        return processed_text
    
    def find_papers_by_keywords(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find papers matching given keywords.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of papers to return
            
        Returns:
            List of matching papers
        """
        if not keywords:
            return []
        
        # Search in local database first
        matching_papers = []
        
        for paper in self.papers:
            matches = 0
            # Check title
            if "title" in paper and isinstance(paper["title"], str):
                for keyword in keywords:
                    if keyword.lower() in paper["title"].lower():
                        matches += 2  # Title matches are weighted more
            
            # Check abstract
            if "abstract" in paper and isinstance(paper["abstract"], str):
                for keyword in keywords:
                    if keyword.lower() in paper["abstract"].lower():
                        matches += 1
            
            # Check keywords
            if "keywords" in paper and isinstance(paper["keywords"], list):
                for keyword in keywords:
                    if keyword.lower() in [k.lower() for k in paper["keywords"]]:
                        matches += 3  # Keyword matches are weighted most
            
            if matches > 0:
                paper["relevance"] = matches
                matching_papers.append(paper)
        
        # Sort by relevance
        matching_papers.sort(key=lambda p: p.get("relevance", 0), reverse=True)
        
        # Limit results
        matching_papers = matching_papers[:limit]
        
        # If we don't have enough results and have access to knowledge graph, try that
        if len(matching_papers) < limit and self.knowledge_graph_adapter:
            try:
                # Get paper IDs we already have
                existing_ids = {p.get("id") for p in matching_papers if "id" in p}
                
                # Query knowledge graph for additional papers
                kg_papers = self._search_papers_in_knowledge_graph(
                    keywords, limit - len(matching_papers)
                )
                
                # Add new papers to results
                for paper in kg_papers:
                    if "id" in paper and paper["id"] not in existing_ids:
                        self.add_paper(paper)
                        matching_papers.append(paper)
                        existing_ids.add(paper["id"])
                
                # Re-sort by relevance
                matching_papers.sort(key=lambda p: p.get("relevance", 0), reverse=True)
                
                # Limit results again
                matching_papers = matching_papers[:limit]
                
            except Exception as e:
                self.logger.error(f"Error searching papers in knowledge graph: {e}")
        
        return matching_papers
    
    def find_citation_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Find a paper by its DOI.
        
        Args:
            doi: DOI to search for
            
        Returns:
            Paper metadata dictionary if found, None otherwise
        """
        # Search in local database first
        for paper in self.papers:
            if "doi" in paper and paper["doi"] == doi:
                return paper
        
        # Try to load from cache
        cache_key = f"doi_{doi.replace('/', '_')}"
        paper = self._load_paper_from_cache(cache_key)
        if paper:
            self.add_paper(paper)
            return paper
        
        # If we have access to knowledge graph, try that
        if self.knowledge_graph_adapter:
            try:
                kg_paper = self._fetch_paper_by_doi_from_knowledge_graph(doi)
                if kg_paper:
                    self.add_paper(kg_paper)
                    return kg_paper
            except Exception as e:
                self.logger.error(f"Error fetching paper by DOI from knowledge graph: {e}")
        
        return None
    
    def export_bibliography(self, format: str = "json", file_path: Optional[str] = None) -> Optional[str]:
        """
        Export bibliography in the specified format.
        
        Args:
            format: Export format (json, bibtex, csv)
            file_path: Optional file path to write to
            
        Returns:
            Exported bibliography as string if file_path is None, otherwise None
        """
        if format == "json":
            data = json.dumps(self.papers, indent=2)
        elif format == "bibtex":
            data = self._export_bibtex()
        elif format == "csv":
            data = self._export_csv()
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            return None
        else:
            return data
    
    def import_bibliography(self, data: Union[str, List[Dict[str, Any]]], format: str = "json") -> int:
        """
        Import bibliography from the specified format.
        
        Args:
            data: Bibliography data (string or parsed data)
            format: Import format (json, bibtex, csv)
            
        Returns:
            Number of papers imported
        """
        imported_count = 0
        
        if format == "json":
            if isinstance(data, str):
                papers = json.loads(data)
            else:
                papers = data
                
            for paper in papers:
                self.add_paper(paper)
                imported_count += 1
                
        elif format == "bibtex":
            papers = self._import_bibtex(data)
            for paper in papers:
                self.add_paper(paper)
                imported_count += 1
                
        elif format == "csv":
            papers = self._import_csv(data)
            for paper in papers:
                self.add_paper(paper)
                imported_count += 1
                
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        return imported_count
    
    def resolve_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Resolve a DOI to retrieve paper metadata.
        
        Args:
            doi: DOI to resolve
            
        Returns:
            Paper metadata dictionary if successful, None otherwise
        """
        # Check cache first
        cache_key = f"doi_{doi.replace('/', '_')}"
        paper = self._load_paper_from_cache(cache_key)
        if paper:
            return paper
        
        # Try to resolve using knowledge graph adapter
        if self.knowledge_graph_adapter:
            try:
                paper = self._fetch_paper_by_doi_from_knowledge_graph(doi)
                if paper:
                    self._save_paper_to_cache(paper)
                    return paper
            except Exception as e:
                self.logger.error(f"Error resolving DOI using knowledge graph: {e}")
        
        # Fallback: create minimal paper entry
        paper = {
            "doi": doi,
            "title": f"Paper with DOI: {doi}",
            "authors": ["Unknown"],
            "year": datetime.now().year,
            "citation_key": f"doi_{doi.replace('/', '_')}"
        }
        
        return paper
    
    def _generate_citation_key(self, paper: Dict[str, Any]) -> str:
        """
        Generate a citation key for a paper.
        
        Args:
            paper: Paper metadata dictionary
            
        Returns:
            Generated citation key
        """
        # Try to use existing identifiers
        if "citation_key" in paper:
            return paper["citation_key"]
        
        if "doi" in paper and paper["doi"]:
            return f"doi_{paper['doi'].replace('/', '_')}"
        
        # Generate key based on authors and year
        authors = paper.get("authors", [])
        year = paper.get("year", datetime.now().year)
        
        if authors and isinstance(authors, list) and len(authors) > 0:
            first_author = authors[0]
            # Extract last name
            last_name = first_author.split()[-1] if " " in first_author else first_author
            
            # Remove special characters
            last_name = re.sub(r'[^a-zA-Z0-9]', '', last_name)
            
            return f"{last_name.lower()}{year}"
        
        # Fallback to hash of title
        if "title" in paper and paper["title"]:
            title_hash = hashlib.md5(paper["title"].encode()).hexdigest()[:8]
            return f"paper_{title_hash}"
        
        # Final fallback
        return f"unknown_{len(self.papers)}"
    
    def _save_paper_to_cache(self, paper: Dict[str, Any]) -> None:
        """
        Save a paper to the cache.
        
        Args:
            paper: Paper metadata dictionary
        """
        try:
            citation_key = paper.get("citation_key")
            if not citation_key:
                return
            
            cache_file = os.path.join(self.cache_dir, f"{citation_key}.json")
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(paper, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving paper to cache: {e}")
    
    def _load_paper_from_cache(self, citation_key: str) -> Optional[Dict[str, Any]]:
        """
        Load a paper from the cache.
        
        Args:
            citation_key: Citation key for the paper
            
        Returns:
            Paper metadata dictionary if found in cache, None otherwise
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{citation_key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                paper = json.load(f)
                
            return paper
            
        except Exception as e:
            self.logger.error(f"Error loading paper from cache: {e}")
            return None
    
    def _fetch_paper_from_knowledge_graph(self, citation_key: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a paper from the knowledge graph.
        
        Args:
            citation_key: Citation key for the paper
            
        Returns:
            Paper metadata dictionary if found, None otherwise
        """
        if not self.knowledge_graph_adapter:
            return None
        
        try:
            # Try to parse DOI from citation key
            if citation_key.startswith("doi_"):
                doi = citation_key[4:].replace('_', '/')
                return self._fetch_paper_by_doi_from_knowledge_graph(doi)
            
            # Query knowledge graph for paper by citation key
            query = f"""
            MATCH (p:Paper)
            WHERE p.citation_key = '{citation_key}' OR p.id = '{citation_key}'
            RETURN p
            """
            
            result = self.knowledge_graph_adapter.query(query)
            
            if result and len(result) > 0:
                paper_data = result[0].get('p', {})
                
                # Convert to standard paper format
                paper = {
                    "citation_key": citation_key,
                    "title": paper_data.get("title", ""),
                    "authors": paper_data.get("authors", []),
                    "year": paper_data.get("year", datetime.now().year),
                    "journal": paper_data.get("venue", ""),
                    "doi": paper_data.get("doi", ""),
                    "url": paper_data.get("url", ""),
                    "abstract": paper_data.get("abstract", "")
                }
                
                return paper
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching paper from knowledge graph: {e}")
            return None
    
    def _fetch_paper_by_doi_from_knowledge_graph(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a paper by DOI from the knowledge graph.
        
        Args:
            doi: DOI for the paper
            
        Returns:
            Paper metadata dictionary if found, None otherwise
        """
        if not self.knowledge_graph_adapter:
            return None
        
        try:
            # Query knowledge graph for paper by DOI
            query = f"""
            MATCH (p:Paper)
            WHERE p.doi = '{doi}'
            RETURN p
            """
            
            result = self.knowledge_graph_adapter.query(query)
            
            if result and len(result) > 0:
                paper_data = result[0].get('p', {})
                
                # Convert to standard paper format
                paper = {
                    "citation_key": f"doi_{doi.replace('/', '_')}",
                    "title": paper_data.get("title", ""),
                    "authors": paper_data.get("authors", []),
                    "year": paper_data.get("year", datetime.now().year),
                    "journal": paper_data.get("venue", ""),
                    "doi": doi,
                    "url": paper_data.get("url", ""),
                    "abstract": paper_data.get("abstract", "")
                }
                
                return paper
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching paper by DOI from knowledge graph: {e}")
            return None
    
    def _search_papers_in_knowledge_graph(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers in the knowledge graph.
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of papers to return
            
        Returns:
            List of matching papers
        """
        if not self.knowledge_graph_adapter:
            return []
        
        try:
            # Create keyword pattern for Cypher query
            keyword_pattern = "|".join([f"(?i).*{keyword}.*" for keyword in keywords])
            
            # Query knowledge graph for papers matching keywords
            query = f"""
            MATCH (p:Paper)
            WHERE p.title =~ '{keyword_pattern}' OR p.abstract =~ '{keyword_pattern}'
            RETURN p
            LIMIT {limit}
            """
            
            result = self.knowledge_graph_adapter.query(query)
            
            papers = []
            for record in result:
                paper_data = record.get('p', {})
                
                # Convert to standard paper format
                paper = {
                    "citation_key": paper_data.get("citation_key", self._generate_citation_key(paper_data)),
                    "title": paper_data.get("title", ""),
                    "authors": paper_data.get("authors", []),
                    "year": paper_data.get("year", datetime.now().year),
                    "journal": paper_data.get("venue", ""),
                    "doi": paper_data.get("doi", ""),
                    "url": paper_data.get("url", ""),
                    "abstract": paper_data.get("abstract", ""),
                    "id": paper_data.get("id", "")
                }
                
                # Calculate relevance
                relevance = 0
                for keyword in keywords:
                    if "title" in paper and keyword.lower() in paper["title"].lower():
                        relevance += 2
                    if "abstract" in paper and keyword.lower() in paper.get("abstract", "").lower():
                        relevance += 1
                
                paper["relevance"] = relevance
                papers.append(paper)
            
            # Sort by relevance
            papers.sort(key=lambda p: p.get("relevance", 0), reverse=True)
            
            return papers
            
        except Exception as e:
            self.logger.error(f"Error searching papers in knowledge graph: {e}")
            return []
    
    def _export_bibtex(self) -> str:
        """
        Export bibliography in BibTeX format.
        
        Returns:
            BibTeX-formatted bibliography
        """
        bibtex = ""
        
        for paper in self.papers:
            # Generate BibTeX entry type
            if "journal" in paper and paper["journal"]:
                entry_type = "article"
            elif "booktitle" in paper and paper["booktitle"]:
                entry_type = "inproceedings"
            elif "publisher" in paper and paper["publisher"]:
                entry_type = "book"
            else:
                entry_type = "misc"
            
            # Generate citation key
            citation_key = paper.get("citation_key", self._generate_citation_key(paper))
            
            # Start BibTeX entry
            bibtex += f"@{entry_type}{{{citation_key},\n"
            
            # Add required fields
            if "title" in paper and paper["title"]:
                bibtex += f"  title = {{{paper['title']}}},\n"
            
            if "authors" in paper and paper["authors"]:
                authors = " and ".join(paper["authors"])
                bibtex += f"  author = {{{authors}}},\n"
            
            if "year" in paper and paper["year"]:
                bibtex += f"  year = {{{paper['year']}}},\n"
            
            # Add optional fields
            if "journal" in paper and paper["journal"]:
                bibtex += f"  journal = {{{paper['journal']}}},\n"
            
            if "volume" in paper and paper["volume"]:
                bibtex += f"  volume = {{{paper['volume']}}},\n"
            
            if "number" in paper and paper["number"]:
                bibtex += f"  number = {{{paper['number']}}},\n"
            
            if "pages" in paper and paper["pages"]:
                bibtex += f"  pages = {{{paper['pages']}}},\n"
            
            if "publisher" in paper and paper["publisher"]:
                bibtex += f"  publisher = {{{paper['publisher']}}},\n"
            
            if "doi" in paper and paper["doi"]:
                bibtex += f"  doi = {{{paper['doi']}}},\n"
            
            if "url" in paper and paper["url"]:
                bibtex += f"  url = {{{paper['url']}}},\n"
            
            # End BibTeX entry
            bibtex += "}\n\n"
        
        return bibtex
    
    def _export_csv(self) -> str:
        """
        Export bibliography in CSV format.
        
        Returns:
            CSV-formatted bibliography
        """
        # Define CSV header
        header = ["citation_key", "title", "authors", "year", "journal", "volume", "number", "pages", "publisher", "doi", "url"]
        
        # Start with header
        csv = ",".join(header) + "\n"
        
        # Add papers
        for paper in self.papers:
            row = []
            
            for field in header:
                if field in paper:
                    if field == "authors" and isinstance(paper[field], list):
                        value = "|".join(paper[field])
                    else:
                        value = str(paper[field])
                    
                    # Escape quotes and commas
                    value = value.replace('"', '""')
                    if "," in value:
                        value = f'"{value}"'
                    
                    row.append(value)
                else:
                    row.append("")
            
            csv += ",".join(row) + "\n"
        
        return csv
    
    def _import_bibtex(self, bibtex_data: str) -> List[Dict[str, Any]]:
        """
        Import bibliography from BibTeX format.
        
        Args:
            bibtex_data: BibTeX-formatted bibliography
            
        Returns:
            List of imported papers
        """
        papers = []
        
        # Define patterns for BibTeX parsing
        entry_pattern = r'@(\w+)\s*\{\s*([^,]+),\s*((?:[^@]*?))\s*\}'
        field_pattern = r'\s*(\w+)\s*=\s*\{((?:[^{}]|(?:\{[^{}]*\}))*)\}'
        
        # Find all entries
        for match in re.finditer(entry_pattern, bibtex_data, re.DOTALL):
            entry_type, citation_key, fields_text = match.groups()
            
            # Initialize paper entry
            paper = {
                "citation_key": citation_key,
                "entry_type": entry_type
            }
            
            # Parse fields
            for field_match in re.finditer(field_pattern, fields_text, re.DOTALL):
                field_name, field_value = field_match.groups()
                
                # Special handling for authors
                if field_name.lower() == "author":
                    authors = field_value.split(" and ")
                    paper["authors"] = [author.strip() for author in authors]
                else:
                    paper[field_name.lower()] = field_value.strip()
            
            papers.append(paper)
        
        return papers
    
    def _import_csv(self, csv_data: str) -> List[Dict[str, Any]]:
        """
        Import bibliography from CSV format.
        
        Args:
            csv_data: CSV-formatted bibliography
            
        Returns:
            List of imported papers
        """
        papers = []
        
        # Split into lines
        lines = csv_data.strip().split("\n")
        
        if not lines:
            return papers
        
        # Parse header
        header = self._parse_csv_line(lines[0])
        
        # Parse data rows
        for i in range(1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            
            # Parse CSV line
            values = self._parse_csv_line(line)
            
            # Create paper entry
            paper = {}
            for j, field in enumerate(header):
                if j < len(values):
                    # Special handling for authors
                    if field == "authors" and "|" in values[j]:
                        paper[field] = values[j].split("|")
                    else:
                        paper[field] = values[j]
            
            papers.append(paper)
        
        return papers
    
    def _parse_csv_line(self, line: str) -> List[str]:
        """
        Parse a CSV line into fields.
        
        Args:
            line: CSV line to parse
            
        Returns:
            List of field values
        """
        fields = []
        current_field = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                fields.append(current_field)
                current_field = ""
            else:
                current_field += char
        
        # Add the last field
        fields.append(current_field)
        
        # Unescape quotes
        for i in range(len(fields)):
            fields[i] = fields[i].replace('""', '"')
            
            # Remove surrounding quotes if present
            if fields[i].startswith('"') and fields[i].endswith('"'):
                fields[i] = fields[i][1:-1]
        
        return fields
    
    def _is_valid_doi(self, doi: str) -> bool:
        """
        Check if a DOI has a valid format.
        
        Args:
            doi: DOI to check
            
        Returns:
            True if the DOI has a valid format, False otherwise
        """
        # Basic DOI format validation
        doi_pattern = r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$'
        return bool(re.match(doi_pattern, doi, re.IGNORECASE))
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL has a valid format.
        
        Args:
            url: URL to check
            
        Returns:
            True if the URL has a valid format, False otherwise
        """
        # Basic URL format validation
        url_pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[\w._~:/?#[\]@!$&\'()*+,;=]*)?$'
        return bool(re.match(url_pattern, url))
    
    def _is_valid_year(self, year: Any) -> bool:
        """
        Check if a year value has a valid format.
        
        Args:
            year: Year value to check
            
        Returns:
            True if the year has a valid format, False otherwise
        """
        try:
            # Convert to integer
            year_int = int(year)
            
            # Check range (allow historical papers but not future papers)
            current_year = datetime.now().year
            return 1400 <= year_int <= current_year + 1  # Allow papers for next year
            
        except (ValueError, TypeError):
            return False