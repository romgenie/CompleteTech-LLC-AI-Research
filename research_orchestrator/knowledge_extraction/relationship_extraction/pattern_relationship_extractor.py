"""
Pattern-based Relationship Extractor module for the Knowledge Extraction Pipeline.

This module provides functionality for extracting relationships between entities
using pattern-based approaches, including regex patterns and lexical patterns.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any, Pattern
import logging

from research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import Entity
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship_extractor import RelationshipExtractor, Relationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default relation types
DEFAULT_RELATION_TYPES = [
    "is_a",
    "part_of",
    "used_for",
    "based_on",
    "developed_by",
    "evaluated_on",
    "outperforms",
    "implements",
    "extends",
    "similar_to",
    "prerequisite_for",
    "alternative_to",
    "inspired_by",
    "component_of",
    "achieves"
]

# Default relation patterns
DEFAULT_RELATION_PATTERNS = {
    "is_a": [
        r"(\w+) is (?:a|an) (\w+)",
        r"(\w+) are (?:a|an) (\w+)",
        r"(\w+),? (?:a|an) (\w+)"
    ],
    "part_of": [
        r"(\w+) is part of (\w+)",
        r"(\w+) are part of (\w+)",
        r"(\w+) contains (\w+)",
        r"(\w+) contain (\w+)"
    ],
    "used_for": [
        r"(\w+) is used for (\w+)",
        r"(\w+) are used for (\w+)",
        r"(\w+) is used to (\w+)",
        r"(\w+) are used to (\w+)"
    ],
    "based_on": [
        r"(\w+) is based on (\w+)",
        r"(\w+) are based on (\w+)",
        r"(\w+) builds upon (\w+)",
        r"(\w+) build upon (\w+)"
    ],
    "developed_by": [
        r"(\w+) (?:was|is) developed by (\w+)",
        r"(\w+) (?:were|are) developed by (\w+)",
        r"(\w+) created (\w+)",
        r"(\w+) created the (\w+)"
    ],
    "evaluated_on": [
        r"(\w+) (?:was|is) evaluated on (\w+)",
        r"(\w+) (?:were|are) evaluated on (\w+)",
        r"(\w+) tested on (\w+)",
        r"(\w+) tested using (\w+)"
    ],
    "outperforms": [
        r"(\w+) outperforms (\w+)",
        r"(\w+) outperform (\w+)",
        r"(\w+) performs better than (\w+)",
        r"(\w+) perform better than (\w+)"
    ],
    "implements": [
        r"(\w+) implements (\w+)",
        r"(\w+) implement (\w+)",
        r"(\w+) is an implementation of (\w+)",
        r"(\w+) are an implementation of (\w+)"
    ],
    "extends": [
        r"(\w+) extends (\w+)",
        r"(\w+) extend (\w+)",
        r"(\w+) is an extension of (\w+)",
        r"(\w+) are an extension of (\w+)"
    ],
    "achieves": [
        r"(\w+) achieves (\w+)",
        r"(\w+) achieve (\w+)",
        r"(\w+) reaches (\w+)",
        r"(\w+) reach (\w+)"
    ]
}


class PatternRelationshipExtractor(RelationshipExtractor):
    """
    Relationship extractor that uses pattern-based approaches to identify
    relationships between entities in text.
    """
    
    def __init__(self, relation_types: Optional[List[str]] = None,
                 config_path: Optional[str] = None,
                 custom_patterns: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the pattern-based relationship extractor.
        
        Args:
            relation_types: List of relationship types to extract
            config_path: Path to configuration file
            custom_patterns: Custom patterns for extracting relationships
        """
        self.relation_types = relation_types or DEFAULT_RELATION_TYPES
        self.custom_patterns = custom_patterns or {}
        
        # Initialize parent class
        super().__init__(self.relation_types, config_path)
        
        # Initialize patterns
        self.patterns = self._initialize_patterns()
        
        # Compile patterns for efficiency
        self.compiled_patterns = self._compile_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for each relationship type."""
        patterns = {relation_type: [] for relation_type in self.relation_types}
        
        # Load default patterns
        for relation_type in self.relation_types:
            if relation_type in DEFAULT_RELATION_PATTERNS:
                patterns[relation_type].extend(DEFAULT_RELATION_PATTERNS[relation_type])
        
        # Load patterns from configuration
        config_patterns = self.config.get("patterns", {})
        for relation_type, rel_patterns in config_patterns.items():
            if relation_type in self.relation_types:
                patterns[relation_type].extend(rel_patterns)
        
        # Add custom patterns
        for relation_type, rel_patterns in self.custom_patterns.items():
            if relation_type in self.relation_types:
                patterns[relation_type].extend(rel_patterns)
        
        return patterns
    
    def _compile_patterns(self) -> Dict[str, List[Pattern]]:
        """Compile regex patterns for efficiency."""
        compiled = {}
        for relation_type, rel_patterns in self.patterns.items():
            compiled[relation_type] = [re.compile(pattern, re.IGNORECASE) for pattern in rel_patterns]
        return compiled
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract relationships between entities in the given text.
        
        Args:
            text: The text to analyze
            entities: List of entities to find relationships between
            
        Returns:
            List of extracted relationships
        """
        # Find potential entity pairs
        entity_pairs = self.find_entity_pairs(entities)
        
        # Extract relationships for each pair
        relationships = []
        relationship_id = 0
        
        for entity1, entity2 in entity_pairs:
            # Get context for the entity pair
            context = self.get_entity_pair_context(text, entity1, entity2)
            
            # Check if the context matches any relationship pattern
            for relation_type, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    match = pattern.search(context)
                    if match:
                        # Extract the relationship with confidence
                        confidence = self._calculate_confidence(match, entity1, entity2, relation_type)
                        
                        relationship = Relationship(
                            id=f"relationship_{relationship_id}",
                            source_entity=entity1,
                            target_entity=entity2,
                            relation_type=relation_type,
                            confidence=confidence,
                            context=context,
                            metadata={"pattern": pattern.pattern}
                        )
                        
                        relationships.append(relationship)
                        relationship_id += 1
                        
                        # Break the pattern loop - we found a relationship for this pair
                        break
        
        # Additionally, find relationships directly using the patterns
        pattern_relationships = self._extract_relationships_from_patterns(text, entities)
        relationships.extend(pattern_relationships)
        
        return relationships
    
    def _extract_relationships_from_patterns(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract relationships directly using patterns, without relying on entity pairs.
        
        Args:
            text: The text to analyze
            entities: List of entities
            
        Returns:
            List of extracted relationships
        """
        relationships = []
        relationship_id = 0
        
        # Create entity lookup dictionary for faster access
        entity_by_text = {}
        for entity in entities:
            entity_text = entity.text.lower()
            if entity_text not in entity_by_text:
                entity_by_text[entity_text] = []
            entity_by_text[entity_text].append(entity)
        
        # Check each pattern for matches
        for relation_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    # Extract the entities from the match
                    entity1_text = match.group(1)
                    entity2_text = match.group(2)
                    
                    # Look up the entities by text
                    entity1_candidates = entity_by_text.get(entity1_text.lower(), [])
                    entity2_candidates = entity_by_text.get(entity2_text.lower(), [])
                    
                    # If we found both entities, create a relationship
                    if entity1_candidates and entity2_candidates:
                        # Use the first entity for simplicity
                        # In a real system, we'd use a more sophisticated approach
                        entity1 = entity1_candidates[0]
                        entity2 = entity2_candidates[0]
                        
                        # Extract the context
                        start_pos = max(0, match.start() - 50)
                        end_pos = min(len(text), match.end() + 50)
                        context = text[start_pos:end_pos]
                        
                        # Calculate confidence
                        confidence = self._calculate_confidence(match, entity1, entity2, relation_type)
                        
                        relationship = Relationship(
                            id=f"pattern_relationship_{relationship_id}",
                            source_entity=entity1,
                            target_entity=entity2,
                            relation_type=relation_type,
                            confidence=confidence,
                            context=context,
                            metadata={"pattern": pattern.pattern}
                        )
                        
                        relationships.append(relationship)
                        relationship_id += 1
        
        return relationships
    
    def _calculate_confidence(self, match: re.Match, entity1: Entity, entity2: Entity, 
                             relation_type: str) -> float:
        """
        Calculate the confidence score for a relationship.
        
        Args:
            match: The regex match
            entity1: The source entity
            entity2: The target entity
            relation_type: The type of relationship
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence
        confidence = 0.7
        
        # Adjust based on match length
        match_length = match.end() - match.start()
        if match_length < 10:
            confidence -= 0.1
        elif match_length > 50:
            confidence += 0.1
        
        # Adjust based on entity confidence
        entity_confidence = (entity1.confidence + entity2.confidence) / 2
        confidence = (confidence + entity_confidence) / 2
        
        # Adjust based on relation type
        # Some relation types are more reliable than others
        if relation_type in ["is_a", "part_of"]:
            confidence += 0.1
        
        # Clamp the confidence between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def add_pattern(self, relation_type: str, pattern: str):
        """
        Add a new pattern for a relationship type.
        
        Args:
            relation_type: The relationship type
            pattern: The regex pattern
        """
        if relation_type not in self.relation_types:
            logger.warning(f"Relation type '{relation_type}' is not recognized")
            return
        
        # Add to patterns
        if relation_type not in self.patterns:
            self.patterns[relation_type] = []
        self.patterns[relation_type].append(pattern)
        
        # Compile the pattern
        if relation_type not in self.compiled_patterns:
            self.compiled_patterns[relation_type] = []
        self.compiled_patterns[relation_type].append(re.compile(pattern, re.IGNORECASE))
        
        logger.info(f"Added pattern for relation type '{relation_type}': {pattern}")
    
    def add_relation_type(self, relation_type: str, patterns: List[str] = None):
        """
        Add a new relationship type with optional patterns.
        
        Args:
            relation_type: The relationship type to add
            patterns: List of regex patterns for the relationship type
        """
        if relation_type in self.relation_types:
            logger.warning(f"Relation type '{relation_type}' already exists")
            return
        
        # Add the relation type
        self.relation_types.append(relation_type)
        
        # Add patterns if provided
        if patterns:
            self.patterns[relation_type] = patterns
            self.compiled_patterns[relation_type] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        else:
            self.patterns[relation_type] = []
            self.compiled_patterns[relation_type] = []
        
        logger.info(f"Added relation type '{relation_type}' with {len(patterns or [])} patterns")
    
    def get_relationship_stats(self, relationships: List[Relationship]) -> Dict[str, int]:
        """
        Get statistics about the extracted relationships.
        
        Args:
            relationships: List of relationships
            
        Returns:
            Dictionary mapping relationship types to counts
        """
        stats = {relation_type: 0 for relation_type in self.relation_types}
        
        for relationship in relationships:
            if relationship.relation_type in stats:
                stats[relationship.relation_type] += 1
        
        return stats