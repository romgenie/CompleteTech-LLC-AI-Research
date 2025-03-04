"""
Citation formatter module for generating formatted citations and references.

This module provides functions for formatting citations and reference lists
in various citation styles (APA, MLA, Chicago, IEEE, etc.).
"""

import logging
import re
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitationStyle(Enum):
    """Citation styles for academic and technical writing."""
    APA = auto()  # American Psychological Association (7th edition)
    MLA = auto()  # Modern Language Association (9th edition)
    CHICAGO = auto()  # Chicago Manual of Style (17th edition)
    IEEE = auto()  # Institute of Electrical and Electronics Engineers
    HARVARD = auto()  # Harvard referencing style
    VANCOUVER = auto()  # Vancouver system (medical)
    NATURE = auto()  # Nature journal style
    
    @classmethod
    def from_string(cls, value: str) -> 'CitationStyle':
        """Convert a string to a CitationStyle enum value.
        
        Args:
            value: String representation of citation style
            
        Returns:
            Corresponding CitationStyle enum value or APA if not found
        """
        try:
            return cls[value.upper()]
        except (KeyError, AttributeError):
            # Default to APA if not found
            return cls.APA


def format_authors(authors: List[str], style: CitationStyle) -> str:
    """Format author names according to the specified citation style.
    
    Args:
        authors: List of author names
        style: Citation style to use
        
    Returns:
        Formatted author string
    """
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    if style == CitationStyle.APA:
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    elif style == CitationStyle.MLA:
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    elif style == CitationStyle.CHICAGO:
        if len(authors) == 1:
            return authors[0]
        elif len(authors) <= 3:
            return ", ".join(authors[:-1]) + ", and " + authors[-1]
        else:
            return f"{authors[0]} et al."
    
    elif style == CitationStyle.IEEE:
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]} et al."
    
    elif style == CitationStyle.HARVARD:
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        elif len(authors) == 3:
            return f"{authors[0]}, {authors[1]} and {authors[2]}"
        else:
            return f"{authors[0]} et al."
    
    elif style == CitationStyle.VANCOUVER:
        return ", ".join(authors[:6]) + (", et al." if len(authors) > 6 else "")
    
    elif style == CitationStyle.NATURE:
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        elif len(authors) <= 5:
            return ", ".join(authors[:-1]) + " & " + authors[-1]
        else:
            return f"{authors[0]} et al."
    
    # Default format if style not recognized
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    else:
        return f"{authors[0]} et al."


def format_citation(paper: Dict[str, Any], style: CitationStyle = CitationStyle.APA) -> str:
    """Format an in-text citation according to the specified citation style.
    
    Args:
        paper: Paper metadata dictionary
        style: Citation style to use
        
    Returns:
        Formatted in-text citation
    """
    try:
        # Extract paper metadata
        authors = paper.get("authors", [])
        year = paper.get("year", datetime.now().year)
        
        # Format based on citation style
        if style == CitationStyle.APA:
            author_text = format_authors(authors, style)
            return f"({author_text}, {year})"
        
        elif style == CitationStyle.MLA:
            author_text = format_authors(authors, style)
            return f"({author_text})"
        
        elif style == CitationStyle.CHICAGO:
            author_text = format_authors(authors, style)
            return f"({author_text} {year})"
        
        elif style == CitationStyle.IEEE:
            # IEEE uses numbered citations
            citation_id = paper.get("citation_id", 1)
            return f"[{citation_id}]"
        
        elif style == CitationStyle.HARVARD:
            author_text = format_authors(authors, style)
            return f"({author_text}, {year})"
        
        elif style == CitationStyle.VANCOUVER:
            # Vancouver uses numbered citations
            citation_id = paper.get("citation_id", 1)
            return f"({citation_id})"
        
        elif style == CitationStyle.NATURE:
            author_text = format_authors(authors, style)
            return f"{author_text}, {year}"
        
        # Default APA-like format
        author_text = format_authors(authors, CitationStyle.APA)
        return f"({author_text}, {year})"
        
    except Exception as e:
        logger.error(f"Error formatting citation: {e}")
        # Fallback citation format
        return "(Author, Year)"


def format_reference(paper: Dict[str, Any], style: CitationStyle = CitationStyle.APA) -> str:
    """Format a reference entry according to the specified citation style.
    
    Args:
        paper: Paper metadata dictionary
        style: Citation style to use
        
    Returns:
        Formatted reference entry
    """
    try:
        # Extract paper metadata
        authors = paper.get("authors", [])
        title = paper.get("title", "Untitled")
        year = paper.get("year", datetime.now().year)
        journal = paper.get("journal", paper.get("venue", "Unknown Journal"))
        volume = paper.get("volume", "")
        issue = paper.get("issue", "")
        pages = paper.get("pages", "")
        publisher = paper.get("publisher", "")
        doi = paper.get("doi", "")
        url = paper.get("url", "")
        citation_id = paper.get("citation_id", "")
        
        # Format authors based on citation style
        if style == CitationStyle.APA:
            # APA style authors: Last, F. M., Last, F. M., & Last, F. M.
            author_text = _format_apa_authors(authors)
            
            # Format APA reference
            reference = f"{author_text} ({year}). {title}. "
            
            if journal:
                if volume and pages:
                    reference += f"{journal}, {volume}"
                    if issue:
                        reference += f"({issue})"
                    reference += f", {pages}. "
                else:
                    reference += f"{journal}. "
            
            if publisher:
                reference += f"{publisher}. "
            
            if doi:
                reference += f"https://doi.org/{doi}"
            elif url:
                reference += f"Retrieved from {url}"
            
            return reference
        
        elif style == CitationStyle.MLA:
            # MLA style authors: Last, First M., et al.
            author_text = _format_mla_authors(authors)
            
            # Format MLA reference
            reference = f"{author_text}. \"{title}.\" "
            
            if journal:
                reference += f"{journal}, "
                if volume:
                    reference += f"vol. {volume}, "
                if issue:
                    reference += f"no. {issue}, "
                reference += f"{year}, "
                if pages:
                    reference += f"pp. {pages}. "
            
            if publisher:
                reference += f"{publisher}, {year}. "
            
            if doi:
                reference += f"DOI: {doi}."
            elif url:
                reference += f"Accessed {datetime.now().strftime('%d %b. %Y')}."
            
            return reference
        
        elif style == CitationStyle.CHICAGO:
            # Chicago style authors: Last, First M., First M. Last, and First M. Last
            author_text = _format_chicago_authors(authors)
            
            # Format Chicago reference
            reference = f"{author_text}. \"{title}.\" "
            
            if journal:
                reference += f"{journal} "
                if volume:
                    reference += f"{volume}, "
                if issue:
                    reference += f"no. {issue} "
                reference += f"({year}): "
                if pages:
                    reference += f"{pages}. "
            else:
                reference += f"{publisher}, {year}. "
            
            if doi:
                reference += f"https://doi.org/{doi}."
            elif url:
                reference += f"{url}."
            
            return reference
        
        elif style == CitationStyle.IEEE:
            # IEEE style reference
            if citation_id:
                reference = f"[{citation_id}] "
            else:
                reference = ""
            
            # IEEE style authors: F. Last, F. Last, and F. Last
            author_text = _format_ieee_authors(authors)
            
            reference += f"{author_text}, \"{title},\" "
            
            if journal:
                reference += f"{journal}, "
                if volume:
                    reference += f"vol. {volume}, "
                if issue:
                    reference += f"no. {issue}, "
                if pages:
                    reference += f"pp. {pages}, "
                reference += f"{year}. "
            else:
                reference += f"{publisher}, {year}. "
            
            if doi:
                reference += f"doi: {doi}."
            elif url:
                reference += f"[Online]. Available: {url}."
            
            return reference
        
        elif style == CitationStyle.HARVARD:
            # Harvard style authors: Last, F., Last, F. and Last, F.
            author_text = _format_harvard_authors(authors)
            
            # Format Harvard reference
            reference = f"{author_text} {year}. {title}. "
            
            if journal:
                reference += f"{journal}, "
                if volume:
                    reference += f"{volume}"
                    if issue:
                        reference += f"({issue})"
                    reference += ", "
                if pages:
                    reference += f"pp. {pages}. "
            
            if publisher:
                reference += f"{publisher}. "
            
            if doi:
                reference += f"DOI: {doi}."
            elif url:
                reference += f"Available at: {url} (Accessed: {datetime.now().strftime('%d %B %Y')})."
            
            return reference
        
        elif style == CitationStyle.VANCOUVER:
            # Vancouver style reference
            if citation_id:
                reference = f"{citation_id}. "
            else:
                reference = ""
            
            # Vancouver style authors: Last FM, Last FM, Last FM
            author_text = _format_vancouver_authors(authors)
            
            reference += f"{author_text}. {title}. "
            
            if journal:
                reference += f"{journal}. {year}"
                if volume:
                    reference += f";{volume}"
                if issue:
                    reference += f"({issue})"
                if pages:
                    reference += f":{pages}"
                reference += ". "
            else:
                reference += f"{publisher}; {year}. "
            
            if doi:
                reference += f"doi: {doi}."
            elif url:
                reference += f"Available from: {url}."
            
            return reference
        
        elif style == CitationStyle.NATURE:
            # Nature style authors: Last, F. M., Last, F. M. & Last, F. M.
            author_text = _format_nature_authors(authors)
            
            # Format Nature reference
            reference = f"{author_text} {title}. "
            
            if journal:
                reference += f"{journal} "
                if volume:
                    reference += f"{volume}, "
                if pages:
                    reference += f"{pages} "
                reference += f"({year})."
            else:
                reference += f"({publisher}, {year})."
            
            if doi:
                reference += f" https://doi.org/{doi}."
            
            return reference
        
        # Default to APA format
        return format_reference(paper, CitationStyle.APA)
        
    except Exception as e:
        logger.error(f"Error formatting reference: {e}")
        # Fallback reference format
        return f"Author. (Year). Title. Journal."


def format_reference_list(
    papers: List[Dict[str, Any]], 
    style: CitationStyle = CitationStyle.APA, 
    title: str = "References"
) -> str:
    """Format a complete reference list according to the specified citation style.
    
    Args:
        papers: List of paper metadata dictionaries
        style: Citation style to use
        title: Title for the reference section
        
    Returns:
        Formatted reference list as a string
    """
    if not papers:
        return f"# {title}\n\nNo references."
    
    # Assign citation IDs for numbered reference styles (IEEE, Vancouver)
    if style in [CitationStyle.IEEE, CitationStyle.VANCOUVER]:
        for i, paper in enumerate(papers):
            paper["citation_id"] = i + 1
    
    # Format references based on style
    formatted_references = []
    for paper in papers:
        reference = format_reference(paper, style)
        formatted_references.append(reference)
    
    # Sort references based on style
    if style in [CitationStyle.APA, CitationStyle.MLA, CitationStyle.CHICAGO, CitationStyle.HARVARD]:
        # Sort alphabetically by first author's last name
        formatted_references.sort()
    
    # Format the complete reference list
    reference_list = f"# {title}\n\n"
    
    for reference in formatted_references:
        reference_list += reference + "\n\n"
    
    return reference_list


# Helper functions for formatting author names in different styles

def _format_apa_authors(authors: List[str]) -> str:
    """Format authors according to APA style."""
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    # APA uses "&" for the final author
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return f"{authors[0]} & {authors[1]}"
    elif len(authors) <= 20:
        return ", ".join(authors[:-1]) + ", & " + authors[-1]
    else:
        # APA 7th edition: for 21+ authors, list first 19, then ellipsis, then final author
        return ", ".join(authors[:19]) + ", ... " + authors[-1]


def _format_mla_authors(authors: List[str]) -> str:
    """Format authors according to MLA style."""
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    # MLA uses "and" for the final author
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    elif len(authors) == 3:
        return f"{authors[0]}, {authors[1]}, and {authors[2]}"
    else:
        # MLA 9th edition: for 4+ authors, list first author followed by "et al."
        return f"{authors[0]} et al."


def _format_chicago_authors(authors: List[str]) -> str:
    """Format authors according to Chicago style."""
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    # Chicago uses "and" for the final author
    if len(authors) == 1:
        return authors[0]
    elif len(authors) <= 10:
        return ", ".join(authors[:-1]) + ", and " + authors[-1]
    else:
        # Chicago style: for 11+ authors, list first 7, then "et al."
        return ", ".join(authors[:7]) + ", et al."


def _format_ieee_authors(authors: List[str]) -> str:
    """Format authors according to IEEE style."""
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    # IEEE uses commas and "and" for the final author
    if len(authors) == 1:
        return authors[0]
    elif len(authors) <= 6:
        return ", ".join(authors[:-1]) + ", and " + authors[-1]
    else:
        # IEEE style: for 7+ authors, list first author followed by "et al."
        return f"{authors[0]} et al."


def _format_harvard_authors(authors: List[str]) -> str:
    """Format authors according to Harvard style."""
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    # Harvard uses "and" for the final author
    if len(authors) == 1:
        return authors[0]
    elif len(authors) <= 3:
        return ", ".join(authors[:-1]) + " and " + authors[-1]
    else:
        # Harvard style: for 4+ authors, list first author followed by "et al."
        return f"{authors[0]} et al."


def _format_vancouver_authors(authors: List[str]) -> str:
    """Format authors according to Vancouver style."""
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    # Vancouver separates all authors with commas
    if len(authors) <= 6:
        return ", ".join(authors)
    else:
        # Vancouver style: for 7+ authors, list first 6 followed by "et al."
        return ", ".join(authors[:6]) + ", et al."


def _format_nature_authors(authors: List[str]) -> str:
    """Format authors according to Nature style."""
    if not authors:
        return "Unknown"
    
    if isinstance(authors, str):
        return authors
    
    if len(authors) == 0:
        return "Unknown"
    
    # Nature uses "&" for the final author
    if len(authors) == 1:
        return authors[0]
    elif len(authors) <= 5:
        return ", ".join(authors[:-1]) + " & " + authors[-1]
    else:
        # Nature style: for 6+ authors, list first author followed by "et al."
        return f"{authors[0]} et al."