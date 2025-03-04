"""
Scientific Entity Recognizer for the Research Orchestration Framework.

This module provides a specialized entity recognizer for identifying scientific
concepts in research documents, such as theories, methodologies, findings, and
hypotheses.
"""

import re
from typing import List, Dict, Any, Set, Pattern, Optional, Tuple
import logging
import os
import json

from .base_recognizer import EntityRecognizer
from .entity import Entity, EntityType

logger = logging.getLogger(__name__)


class ScientificEntityRecognizer(EntityRecognizer):
    """Entity recognizer specialized for scientific research concepts.
    
    This recognizer identifies scientific entities like concepts, theories,
    methodologies, findings, hypotheses, and authors in research documents.
    """
    
    # Default patterns for common scientific entity types
    DEFAULT_PATTERNS = {
        EntityType.CONCEPT: [
            r"\b(?:the )?concept of ([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*)\b",
            r"\b([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*) (?:concept|conceptualization)\b"
        ],
        EntityType.THEORY: [
            r"\b(?:the )?theory of ([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*)\b",
            r"\b([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*) theory\b"
        ],
        EntityType.METHODOLOGY: [
            r"\b(?:the )?methodology of ([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*)\b",
            r"\b([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*) methodology\b",
            r"\b(?:the )?method of ([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*)\b",
            r"\b([A-Z][a-z]+(?:[ -][A-Z]?[a-z]+)*) method\b"
        ],
        EntityType.FINDING: [
            r"\bwe found that\b[^.!?]*",
            r"\bthe results show that\b[^.!?]*",
            r"\bour findings indicate that\b[^.!?]*",
            r"\bevidence suggests that\b[^.!?]*"
        ],
        EntityType.HYPOTHESIS: [
            r"\bwe hypothesize that\b[^.!?]*",
            r"\bour hypothesis (?:is|was) that\b[^.!?]*",
            r"\bthe hypothesis that\b[^.!?]*"
        ],
        EntityType.AUTHOR: [
            r"\b(?:[A-Z][a-z]+ (?:et al\.)|(?:[A-Z][a-z]+ and [A-Z][a-z]+))(?: \([0-9]{4}\))?\b"
        ],
        EntityType.LIMITATION: [
            r"\blimitation(?:s)? of (?:this|our) (?:work|study|approach|method)\b[^.!?]*",
            r"\bour (?:work|study|approach|method) is limited by\b[^.!?]*"
        ]
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Scientific Entity Recognizer.
        
        Args:
            config: Configuration dictionary that can include custom patterns,
                   confidence thresholds, and other recognition parameters
        """
        # Initialize instance variables before calling super().__init__
        # Compiled regex patterns for each entity type
        self.patterns: Dict[EntityType, List[Pattern]] = {}
        # Dictionary of known scientific terms with their types
        self.known_terms: Dict[str, Tuple[EntityType, float]] = {}
        
        # Now call the parent constructor which will call _initialize_from_config
        super().__init__(config)
    
    def _initialize_from_config(self) -> None:
        """Initialize recognizer patterns and dictionaries from configuration."""
        # Load custom patterns from config
        custom_patterns = self.config.get("patterns", {})
        
        # Compile the default and custom patterns
        for entity_type in EntityType:
            if entity_type in self.DEFAULT_PATTERNS or str(entity_type) in custom_patterns:
                type_str = str(entity_type)
                # Combine default and custom patterns
                patterns = self.DEFAULT_PATTERNS.get(entity_type, []) + custom_patterns.get(type_str, [])
                self.patterns[entity_type] = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        # Load known scientific terms from a dictionary file if specified
        dict_path = self.config.get("terminology_path")
        if dict_path and os.path.exists(dict_path):
            self._load_terminology_dictionary(dict_path)
    
    def _load_terminology_dictionary(self, filepath: str) -> None:
        """Load a dictionary of known scientific terms from a JSON file.
        
        The dictionary file should have the format:
        {
            "term_text": {"type": "entity_type", "confidence": 0.9},
            ...
        }
        
        Args:
            filepath: Path to the terminology dictionary JSON file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                term_dict = json.load(f)
            
            for term_text, info in term_dict.items():
                entity_type = EntityType.from_string(info["type"])
                confidence = info.get("confidence", 1.0)
                self.known_terms[term_text.lower()] = (entity_type, confidence)
            
            logger.info(f"Loaded {len(self.known_terms)} scientific terms from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load terminology dictionary from {filepath}: {e}")
    
    def recognize(self, text: str) -> List[Entity]:
        """Recognize scientific entities in the provided text.
        
        Args:
            text: The text to analyze for scientific entities
            
        Returns:
            A list of recognized scientific entities
        """
        all_entities = []
        
        # Pattern-based recognition
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    # For patterns with capture groups, use the first group
                    # Otherwise use the whole match
                    if match.lastindex and match.lastindex >= 1:
                        entity_text = match.group(1)
                        # Adjust positions for capture group
                        start_pos = match.start(1)
                        end_pos = match.end(1)
                    else:
                        entity_text = match.group(0)
                        start_pos = match.start()
                        end_pos = match.end()
                    
                    # Compute confidence based on heuristics
                    confidence = self._compute_confidence(entity_text, entity_type, start_pos, end_pos, text)
                    
                    # Create and add the entity
                    entity = Entity(
                        text=entity_text,
                        type=entity_type,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos
                    )
                    all_entities.append(entity)
        
        # Terminology dictionary-based recognition
        for term, (term_type, base_confidence) in self.known_terms.items():
            # Find all occurrences of the term in the text
            for match in re.finditer(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                start_pos = match.start()
                end_pos = match.end()
                
                # Get the actual matched text from the original text
                matched_text = text[start_pos:end_pos]
                
                # Create and add the entity
                entity = Entity(
                    text=matched_text,
                    type=term_type,
                    confidence=base_confidence,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    metadata={"source": "terminology_dictionary"}
                )
                all_entities.append(entity)
        
        # Apply additional recognition for citations and references
        self._recognize_citations(text, all_entities)
        
        # Resolve overlapping entities
        all_entities = self.merge_overlapping_entities(all_entities)
        
        # Save the entities for later use
        self.entities = all_entities
        
        return all_entities
    
    def _compute_confidence(
        self, 
        entity_text: str, 
        entity_type: EntityType, 
        start_pos: int, 
        end_pos: int,
        context: str
    ) -> float:
        """Compute confidence score for a scientific entity based on heuristics.
        
        Args:
            entity_text: The text of the entity
            entity_type: The type of the entity
            start_pos: Start position in the original text
            end_pos: End position in the original text
            context: The surrounding text context
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.7  # Base confidence
        
        # Adjust confidence based on entity length
        if len(entity_text) < 3:
            confidence -= 0.2
        elif len(entity_text) > 100:  # Findings and hypotheses can be long sentences
            if entity_type not in [EntityType.FINDING, EntityType.HYPOTHESIS]:
                confidence -= 0.2
        
        # Increase confidence for properly capitalized entities
        if entity_text[0].isupper() and entity_type in [
            EntityType.CONCEPT, EntityType.THEORY, EntityType.METHODOLOGY
        ]:
            confidence += 0.1
        
        # Adjust confidence based on context
        context_window = context[max(0, start_pos-50):min(len(context), end_pos+50)]
        
        # Check for scientific discourse markers
        scientific_markers = [
            "study", "research", "paper", "experiment", "analysis", 
            "investigate", "examine", "demonstrate", "propose"
        ]
        
        for marker in scientific_markers:
            if marker in context_window.lower():
                confidence += 0.05
                break
        
        # Special handling for findings and hypotheses
        if entity_type == EntityType.FINDING:
            # Higher confidence for findings with numerical results
            if re.search(r'\b[0-9]+(?:\.[0-9]+)?%?\b', entity_text):
                confidence += 0.15
        elif entity_type == EntityType.HYPOTHESIS:
            # Higher confidence for clear hypothesis statements
            if "if" in entity_text.lower() and "then" in entity_text.lower():
                confidence += 0.1
        
        # Ensure confidence is within valid range
        return max(0.0, min(1.0, confidence))
    
    def _recognize_citations(self, text: str, entities: List[Entity]) -> None:
        """Recognize citations and related author entities in the text.
        
        Args:
            text: The input text
            entities: List of already recognized entities (will be modified)
        """
        # Pattern for author citations in parentheses
        citation_pattern = re.compile(r'\(([A-Z][a-z]+(?:[\s,]+(?:and )?[A-Z][a-z]+)*),?\s+(\d{4}[a-z]?)\)')
        
        for match in citation_pattern.finditer(text):
            author_text = match.group(1)
            year = match.group(2)
            full_citation = match.group(0)
            
            # Create author entity
            author_entity = Entity(
                text=author_text,
                type=EntityType.AUTHOR,
                confidence=0.9,
                start_pos=match.start(1),
                end_pos=match.end(1),
                metadata={"year": year, "citation_type": "parenthetical"}
            )
            entities.append(author_entity)
            
            # Look for the cited finding in the preceding and following text
            citation_pos = match.start()
            
            # Context window: sentence containing the citation and the next one
            pre_context = text[max(0, citation_pos-200):citation_pos]
            post_context = text[match.end():min(len(text), match.end()+200)]
            
            # Try to find the finding being cited
            pre_sentences = pre_context.split('.')
            if pre_sentences:
                cited_text = pre_sentences[-1].strip()
                if cited_text:
                    finding_entity = Entity(
                        text=cited_text,
                        type=EntityType.FINDING,
                        confidence=0.6,
                        metadata={
                            "author": author_text,
                            "year": year,
                            "citation_type": "cited_finding"
                        }
                    )
                    entities.append(finding_entity)