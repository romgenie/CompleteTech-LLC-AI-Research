"""
Scientific Entity Recognizer module for the Knowledge Extraction Pipeline.

This module provides specialized functionality for identifying and categorizing
scientific entities within research documents, including concepts, theories,
methodologies, and scientific findings.
"""

import re
from typing import Dict, List, Optional, Set, Any, Tuple
import json
import logging
from pathlib import Path

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import EntityRecognizer, Entity
from src.research_orchestrator.adapters.karma_adapter.karma_adapter import KARMAAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scientific entity types
SCIENTIFIC_ENTITY_TYPES = [
    "concept",
    "theory",
    "methodology",
    "finding",
    "hypothesis",
    "experiment",
    "artifact",
    "tool",
    "property",
    "constraint",
    "limitation",
    "field",
    "author",
    "institution"
]

# Default patterns for some scientific entity types
DEFAULT_PATTERNS = {
    "methodology": [
        r'\b((?:cross-validation|k-fold validation|grid search|random search|bayesian optimization))\b',
        r'\b((?:ablation study|adversarial training|transfer learning|fine-tuning))\b',
        r'\b((?:qualitative analysis|quantitative analysis|comparative study))\b'
    ],
    "finding": [
        r'((?:we|our|this study|this paper) (?:demonstrate[sd]?|show[sd]?|found|discover[a-z]*|prove[sd]?)(?:\s+that)?\s+[^.;]{10,100})',
        r'((?:results|experiments) (?:show|demonstrate|reveal|indicate|suggest)(?:\s+that)?\s+[^.;]{10,100})'
    ],
    "hypothesis": [
        r'((?:we|our|this study|this paper) hypothesize[sd]?(?:\s+that)?\s+[^.;]{10,100})',
        r'(our (?:hypothesis|assumption)(?:\s+is)?\s+[^.;]{10,100})'
    ],
    "author": [
        r'([A-Z][a-z]+ et al\.)'
    ],
    "institution": [
        r'(University of [A-Za-z ]+)',
        r'([A-Za-z]+ University)',
        r'([A-Za-z]+ Institute of [A-Za-z ]+)'
    ]
}


class ScientificEntityRecognizer(EntityRecognizer):
    """
    Specialized entity recognizer for scientific research documents that identifies
    concepts, theories, methodologies, and other scientific entities.
    """
    
    def __init__(self, 
                 entity_types: Optional[List[str]] = None,
                 config_path: Optional[str] = None,
                 custom_patterns: Optional[Dict[str, List[str]]] = None,
                 use_karma: bool = False,
                 karma_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the scientific entity recognizer.
        
        Args:
            entity_types: List of scientific entity types to recognize (if None, use all)
            config_path: Path to configuration file
            custom_patterns: Dictionary of custom regex patterns for each entity type
            use_karma: Whether to use the KARMA adapter for entity recognition
            karma_config: Configuration for the KARMA adapter
        """
        self.entity_types = entity_types or SCIENTIFIC_ENTITY_TYPES
        self.custom_patterns = custom_patterns or {}
        self.use_karma = use_karma
        
        # Initialize parent class
        super().__init__(self.entity_types, config_path)
        
        # Initialize patterns dictionary with defaults
        self.patterns = {entity_type: [] for entity_type in self.entity_types}
        self._load_patterns()
        
        # Compile regex patterns
        self.compiled_patterns = self._compile_patterns()
        
        # Initialize KARMA adapter if needed
        self.karma_adapter = None
        if self.use_karma:
            try:
                self.karma_adapter = KARMAAdapter(**(karma_config or {}))
            except Exception as e:
                logger.error(f"Failed to initialize KARMA adapter: {e}")
                self.use_karma = False
                
        # Initialize keyword dictionaries for entity types that are 
        # difficult to capture with regex patterns
        self.keywords = self._initialize_keywords()
    
    def _load_patterns(self):
        """Load patterns from configuration and custom patterns."""
        # Load default patterns for the entity types we're interested in
        for entity_type in self.entity_types:
            if entity_type in DEFAULT_PATTERNS:
                self.patterns[entity_type].extend(DEFAULT_PATTERNS[entity_type])
        
        # Load patterns from configuration file
        config_patterns = self.config.get("patterns", {})
        for entity_type, patterns in config_patterns.items():
            if entity_type in self.entity_types:
                self.patterns[entity_type].extend(patterns)
        
        # Add custom patterns
        for entity_type, patterns in self.custom_patterns.items():
            if entity_type in self.entity_types:
                self.patterns[entity_type].extend(patterns)
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficiency."""
        compiled = {}
        for entity_type, patterns in self.patterns.items():
            compiled[entity_type] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        return compiled
    
    def _initialize_keywords(self) -> Dict[str, Set[str]]:
        """Initialize keyword dictionaries for entity types."""
        keywords = {}
        
        # Load theory keywords
        keywords["theory"] = {
            "theory of", "theoretical framework", "theoretical model",
            "theoretical approach", "theoretical foundation",
            "paradigm", "principle", "theorem", "law of", "model of"
        }
        
        # Load concept keywords
        keywords["concept"] = {
            "concept of", "notion of", "idea of", 
            "framework", "approach", "paradigm",
            "perspective", "viewpoint", "understanding of"
        }
        
        # Load field keywords
        keywords["field"] = {
            "field of", "domain of", "area of", 
            "discipline", "subfield", "subdomain",
            "computer science", "artificial intelligence", "machine learning",
            "natural language processing", "computer vision", "robotics",
            "deep learning", "reinforcement learning", "unsupervised learning",
            "supervised learning", "information retrieval", "data mining"
        }
        
        return keywords
    
    def recognize_entities(self, text: str) -> List[Entity]:
        """
        Recognize scientific entities in the given text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of recognized entities
        """
        entities = []
        
        # Use rule-based approach with regex patterns
        entities.extend(self._recognize_with_patterns(text))
        
        # Use keyword-based approach for certain entity types
        entities.extend(self._recognize_with_keywords(text))
        
        # Use KARMA adapter if available
        if self.use_karma and self.karma_adapter:
            karma_entities = self._recognize_with_karma(text)
            entities.extend(karma_entities)
        
        # Use specific heuristics for finding certain types of entities
        entities.extend(self._recognize_with_heuristics(text))
        
        # Merge overlapping entities
        merged_entities = self.merge_overlapping_entities(entities)
        
        return merged_entities
    
    def _recognize_with_patterns(self, text: str) -> List[Entity]:
        """Recognize entities using regex patterns."""
        entities = []
        entity_id = 0
        
        for entity_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    start_pos, end_pos = match.span()
                    entity_text = match.group(0)
                    
                    # Simple confidence calculation based on heuristics
                    # In a real system, this would be more sophisticated
                    confidence = self._calculate_confidence(entity_text, entity_type)
                    
                    entity = Entity(
                        id=f"scientific_entity_{entity_id}",
                        text=entity_text,
                        type=entity_type,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        metadata={"source": "pattern", "pattern": pattern.pattern}
                    )
                    
                    entities.append(entity)
                    entity_id += 1
        
        return entities
    
    def _recognize_with_keywords(self, text: str) -> List[Entity]:
        """Recognize entities using keyword-based approach."""
        entities = []
        entity_id = 0
        
        for entity_type, keyword_set in self.keywords.items():
            for keyword in keyword_set:
                # Search for the keyword in the text
                for match in re.finditer(r'\b' + re.escape(keyword) + r'\b\s+([A-Za-z][\w\s,\-\']{2,50})', text, re.IGNORECASE):
                    start_pos, end_pos = match.span()
                    entity_text = match.group(1).strip()
                    
                    # Calculate confidence
                    confidence = 0.7  # Default confidence for keyword matches
                    
                    entity = Entity(
                        id=f"keyword_entity_{entity_id}",
                        text=entity_text,
                        type=entity_type,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        metadata={"source": "keyword", "keyword": keyword}
                    )
                    
                    entities.append(entity)
                    entity_id += 1
        
        return entities
    
    def _recognize_with_karma(self, text: str) -> List[Entity]:
        """Recognize entities using the KARMA adapter."""
        entities = []
        entity_id = 0
        
        try:
            # Extract entities using KARMA
            karma_entities = self.karma_adapter.extract_entities(text)
            
            for karma_entity in karma_entities:
                # Map KARMA entity type to our entity types
                entity_type = self._map_karma_entity_type(karma_entity.get("type", ""))
                
                if entity_type in self.entity_types:
                    entity = Entity(
                        id=f"karma_scientific_entity_{entity_id}",
                        text=karma_entity.get("text", ""),
                        type=entity_type,
                        confidence=karma_entity.get("confidence", 0.8),
                        start_pos=karma_entity.get("start_pos", 0),
                        end_pos=karma_entity.get("end_pos", 0),
                        metadata={"source": "karma", "original_type": karma_entity.get("type", "")}
                    )
                    
                    entities.append(entity)
                    entity_id += 1
                    
        except Exception as e:
            logger.error(f"Error recognizing entities with KARMA: {e}")
        
        return entities
    
    def _recognize_with_heuristics(self, text: str) -> List[Entity]:
        """Recognize entities using specific heuristics."""
        entities = []
        entity_id = 0
        
        # Heuristic for finding scientific artifacts (like published papers)
        # Look for text in parentheses that might be paper citations
        citation_pattern = re.compile(r'\(([A-Z][a-z]+ et al\.,? \d{4}[a-z]?)\)')
        for match in citation_pattern.finditer(text):
            start_pos, end_pos = match.span()
            entity_text = match.group(1)
            
            entity = Entity(
                id=f"heuristic_entity_{entity_id}",
                text=entity_text,
                type="artifact",
                confidence=0.85,
                start_pos=start_pos,
                end_pos=end_pos,
                metadata={"source": "heuristic", "heuristic_type": "citation"}
            )
            
            entities.append(entity)
            entity_id += 1
        
        # Heuristic for finding scientific constraints or limitations
        # Look for sentences containing constraint-related terms
        limitations_pattern = re.compile(r'([^.!?]*\b(?:limitation|constraint|drawback|shortcoming|challenge|limitation|bottleneck)\b[^.!?]*[.!?])')
        for match in limitations_pattern.finditer(text):
            start_pos, end_pos = match.span()
            entity_text = match.group(1).strip()
            
            entity = Entity(
                id=f"heuristic_entity_{entity_id}",
                text=entity_text,
                type="limitation",
                confidence=0.75,
                start_pos=start_pos,
                end_pos=end_pos,
                metadata={"source": "heuristic", "heuristic_type": "limitations"}
            )
            
            entities.append(entity)
            entity_id += 1
        
        return entities
    
    def _map_karma_entity_type(self, karma_type: str) -> str:
        """Map KARMA entity type to our entity types."""
        # This is a simple mapping - in a real system this would be more comprehensive
        mapping = {
            "concept": "concept",
            "theory": "theory",
            "method": "methodology",
            "finding": "finding",
            "hypothesis": "hypothesis",
            "experiment": "experiment",
            "tool": "tool",
            "limitation": "limitation",
            "constraint": "constraint",
            "field": "field",
            "author": "author",
            "institution": "institution"
        }
        
        return mapping.get(karma_type.lower(), "")
    
    def _calculate_confidence(self, entity_text: str, entity_type: str) -> float:
        """
        Calculate confidence score for an entity based on heuristics.
        
        Args:
            entity_text: The text of the entity
            entity_type: The type of the entity
            
        Returns:
            Confidence score between 0 and 1
        """
        # Basic confidence calculation
        confidence = 0.7  # Default confidence
        
        # Adjust based on entity text length
        text_length = len(entity_text)
        if text_length < 5:
            confidence -= 0.2  # Very short entities are less reliable
        elif text_length > 100:
            confidence -= 0.1  # Very long entities are less reliable
        
        # Adjust based on capitalization for certain entity types
        if entity_type in ["theory", "concept", "methodology"] and entity_text[0].isupper():
            confidence += 0.1  # Capitalized theories/concepts/methods are more likely to be valid
        
        # Adjust for finding and hypothesis entities
        if entity_type in ["finding", "hypothesis"]:
            # More confident if it includes certain phrases
            confident_phrases = ["significant", "demonstrate", "prove", "show", "result"]
            if any(phrase in entity_text.lower() for phrase in confident_phrases):
                confidence += 0.1
        
        # Return final confidence, clamped between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def add_custom_pattern(self, entity_type: str, pattern: str):
        """
        Add a custom regex pattern for an entity type.
        
        Args:
            entity_type: The entity type to add the pattern for
            pattern: The regex pattern to add
        """
        if entity_type not in self.entity_types:
            logger.warning(f"Entity type '{entity_type}' is not recognized")
            return
        
        # Add to patterns dictionary
        if entity_type not in self.patterns:
            self.patterns[entity_type] = []
        self.patterns[entity_type].append(pattern)
        
        # Compile the new pattern
        if entity_type not in self.compiled_patterns:
            self.compiled_patterns[entity_type] = []
        self.compiled_patterns[entity_type].append(re.compile(pattern, re.IGNORECASE))
        
        logger.info(f"Added custom pattern for entity type '{entity_type}': {pattern}")
    
    def extract_findings(self, entities: List[Entity]) -> List[str]:
        """
        Extract all findings from the list of entities.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of finding statements, sorted by confidence
        """
        findings = [(e.text, e.confidence) for e in entities if e.type == "finding"]
        findings.sort(key=lambda x: x[1], reverse=True)
        
        return [finding for finding, _ in findings]
    
    def extract_theory_concepts(self, entities: List[Entity]) -> Dict[str, List[str]]:
        """
        Extract theories and related concepts from the list of entities.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            Dictionary mapping theory names to lists of related concepts
        """
        # Get all theories
        theories = [e.text for e in entities if e.type == "theory"]
        
        # Get all concepts
        concepts = [e.text for e in entities if e.type == "concept"]
        
        # Simple approach - just associate each concept with all theories
        # In a real system, we would use more sophisticated relationship detection
        result = {}
        for theory in theories:
            result[theory] = concepts
        
        return result