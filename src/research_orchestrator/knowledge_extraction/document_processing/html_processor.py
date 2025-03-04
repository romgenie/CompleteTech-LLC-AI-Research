"""
HTML Processor for handling HTML documents.

This module provides the HTMLProcessor class that extracts and cleans content from
HTML documents and segments it for knowledge extraction.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)

class HTMLProcessor:
    """
    Processor for HTML documents that extracts and segments content.
    
    This class handles the extraction of text from HTML files, including
    cleaning, handling document structure, and extracting metadata.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the HTML processor.
        
        Args:
            config: Configuration dictionary with HTML processing settings.
        """
        self.config = config
        self.segment_min_length = config.get('segment_min_length', 100)
        self.segment_max_length = config.get('segment_max_length', 1000)
        
        # Default tags to exclude (navigation, scripts, etc.)
        self.exclude_tags = config.get('exclude_tags', [
            'script', 'style', 'nav', 'footer', 'header', 'noscript',
            'iframe', 'svg', 'canvas', 'button', 'form', 'input'
        ])
        
        # Content tags (main content typically found in these)
        self.content_tags = config.get('content_tags', [
            'article', 'section', 'main', 'div.content', 'div.main'
        ])
    
    def process(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an HTML document.
        
        Args:
            document: The document dictionary containing HTML content.
            
        Returns:
            The processed document with extracted text and segments.
        """
        logger.info(f"Processing HTML document: {document.get('id', 'unknown')}")
        
        # Get HTML content
        content = document.get('content')
        if not content:
            logger.warning("HTML document has no content")
            return document
        
        # If content is bytes, convert to string
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='replace')
        
        # Clean and extract text
        clean_text, metadata = self._clean_html(content)
        
        # Extract any additional metadata
        metadata.update(self._extract_metadata(content))
        
        # Segment the text
        segments = self._segment_content(clean_text)
        
        # Create the processed document
        processed_doc = document.copy()
        processed_doc.update({
            'extracted_text': clean_text,
            'metadata': metadata,
            'segments': segments
        })
        
        return processed_doc
    
    def _clean_html(self, html_content: str) -> tuple[str, Dict[str, Any]]:
        """
        Clean HTML and extract important text content.
        
        Args:
            html_content: The HTML content as string.
            
        Returns:
            Tuple of (cleaned text, metadata)
        """
        metadata = {}
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            if soup.title:
                metadata['title'] = soup.title.string.strip() if soup.title.string else ''
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '')
            
            # Extract meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                metadata['keywords'] = meta_keywords.get('content', '')
            
            # Remove excluded tags
            for tag_name in self.exclude_tags:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # Try to find main content
            main_content = None
            
            for selector in self.content_tags:
                if '.' in selector:
                    # Class selector (e.g., 'div.content')
                    tag_name, class_name = selector.split('.')
                    found = soup.find(tag_name, class_=class_name)
                else:
                    # Tag selector (e.g., 'article')
                    found = soup.find(selector)
                
                if found:
                    main_content = found
                    break
            
            # If main content found, use it; otherwise use the whole body
            if main_content:
                text = self._extract_text_from_element(main_content)
            else:
                # Use the whole body if available, otherwise the entire document
                body = soup.body if soup.body else soup
                text = self._extract_text_from_element(body)
            
            # Clean the text
            clean_text = self._clean_text(text)
            
            return clean_text, metadata
            
        except Exception as e:
            logger.error(f"HTML cleaning failed: {str(e)}")
            return html_content, metadata
    
    def _extract_text_from_element(self, element: Tag) -> str:
        """
        Extract text from a BeautifulSoup element with proper spacing.
        
        Args:
            element: The BeautifulSoup element.
            
        Returns:
            The extracted text.
        """
        texts = []
        
        # Process only elements that have text content
        for child in element.descendants:
            if isinstance(child, NavigableString) and child.strip():
                texts.append(child.strip())
            elif isinstance(child, Tag) and child.name in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
                # Add newlines for block elements
                if texts and not texts[-1].endswith('\n'):
                    texts.append('\n')
        
        # Join all text pieces with proper spacing
        return ' '.join(texts)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        
        Args:
            text: The extracted text.
            
        Returns:
            Cleaned text.
        """
        # Remove multiple spaces
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _extract_metadata(self, html_content: str) -> Dict[str, Any]:
        """
        Extract additional metadata from HTML.
        
        Args:
            html_content: The HTML content.
            
        Returns:
            Dictionary with metadata.
        """
        metadata = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract Open Graph metadata
            og_metadata = {}
            for meta in soup.find_all('meta', property=re.compile(r'^og:')):
                property_name = meta.get('property', '')[3:]  # Remove 'og:' prefix
                og_metadata[property_name] = meta.get('content', '')
            
            if og_metadata:
                metadata['open_graph'] = og_metadata
            
            # Extract Twitter Card metadata
            twitter_metadata = {}
            for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
                property_name = meta.get('name', '')[8:]  # Remove 'twitter:' prefix
                twitter_metadata[property_name] = meta.get('content', '')
            
            if twitter_metadata:
                metadata['twitter_card'] = twitter_metadata
            
            # Extract canonical URL
            canonical = soup.find('link', rel='canonical')
            if canonical:
                metadata['canonical_url'] = canonical.get('href', '')
            
            # Extract publication date (common patterns)
            date_meta = soup.find('meta', property='article:published_time')
            if date_meta:
                metadata['published_date'] = date_meta.get('content', '')
            else:
                # Try other common date patterns
                date_meta = soup.find('meta', attrs={'name': 'date'})
                if date_meta:
                    metadata['published_date'] = date_meta.get('content', '')
                else:
                    # Look for time elements
                    time_elem = soup.find('time')
                    if time_elem and time_elem.has_attr('datetime'):
                        metadata['published_date'] = time_elem['datetime']
            
            # Extract author information
            author_meta = soup.find('meta', attrs={'name': 'author'})
            if author_meta:
                metadata['author'] = author_meta.get('content', '')
            else:
                # Try structured data
                author_elem = soup.find(attrs={'rel': 'author'})
                if author_elem:
                    metadata['author'] = author_elem.get_text().strip()
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {str(e)}")
        
        return metadata
    
    def _segment_content(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment content into meaningful chunks for knowledge extraction.
        
        Args:
            text: The extracted text.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Skip empty text
        if not text:
            return segments
        
        # Segment by sections (headers)
        section_segments = self._segment_by_headers(text)
        
        if section_segments:
            # If we found headers, use those segments
            segments = section_segments
        else:
            # Otherwise, segment by paragraphs
            segments = self._segment_by_paragraphs(text)
        
        # Apply length constraints and further segmentation if needed
        processed_segments = []
        for segment in segments:
            content = segment['content']
            
            # Skip short segments
            if len(content) < self.segment_min_length:
                continue
            
            # Further segment long content
            if len(content) > self.segment_max_length:
                # Split by sentences while respecting max length
                sub_segments = self._split_by_length(content, self.segment_max_length)
                
                # Add each sub-segment with the same metadata
                for i, sub_content in enumerate(sub_segments):
                    if len(sub_content) >= self.segment_min_length:
                        sub_segment = segment.copy()
                        sub_segment['content'] = sub_content
                        sub_segment['segment_id'] = f"{segment.get('segment_id', 'seg')}.{i+1}"
                        processed_segments.append(sub_segment)
            else:
                # Add segment as is
                processed_segments.append(segment)
        
        # Ensure all segments have IDs
        for i, segment in enumerate(processed_segments):
            if 'segment_id' not in segment:
                segment['segment_id'] = f"segment_{i+1}"
        
        return processed_segments
    
    def _segment_by_headers(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by headers (# Header, ## Subheader, etc.).
        
        Args:
            text: The text to segment.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Pattern for Markdown-style headers
        header_pattern = re.compile(r'(#+\s+[^\n]+)', re.MULTILINE)
        
        # Find all headers
        headers = [(m.group(1), m.start()) for m in header_pattern.finditer(text)]
        
        # If no headers found, return empty list
        if not headers:
            return []
        
        # Extract sections
        for i, (header, start_pos) in enumerate(headers):
            # Determine section end
            if i < len(headers) - 1:
                end_pos = headers[i+1][1]
            else:
                end_pos = len(text)
            
            # Extract section content
            section_text = text[start_pos:end_pos].strip()
            
            # Create segment
            if section_text:
                segment = {
                    'segment_id': f"section_{i+1}",
                    'segment_type': 'section',
                    'section_header': header.strip('#').strip(),
                    'content': section_text
                }
                segments.append(segment)
        
        return segments
    
    def _segment_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by paragraphs.
        
        Args:
            text: The text to segment.
            
        Returns:
            List of segment dictionaries.
        """
        segments = []
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        
        for i, paragraph in enumerate(paragraphs):
            # Clean and skip empty paragraphs
            content = paragraph.strip()
            if not content:
                continue
            
            # Create segment
            segment = {
                'segment_id': f"paragraph_{i+1}",
                'segment_type': 'paragraph',
                'content': content
            }
            segments.append(segment)
        
        return segments
    
    def _split_by_length(self, text: str, max_length: int) -> List[str]:
        """
        Split text by sentences while respecting maximum length.
        
        Args:
            text: The text to split.
            max_length: Maximum length for each segment.
            
        Returns:
            List of text segments.
        """
        segments = []
        
        # Pattern for sentence endings
        sentence_end = re.compile(r'(?<=[.!?])\s+')
        
        # Split by sentences
        sentences = sentence_end.split(text)
        
        current_segment = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed max length and we already have content,
            # finalize the current segment and start a new one
            if current_segment and len(current_segment) + len(sentence) > max_length:
                segments.append(current_segment.strip())
                current_segment = sentence
            else:
                current_segment += " " + sentence if current_segment else sentence
        
        # Add the last segment if it has content
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments