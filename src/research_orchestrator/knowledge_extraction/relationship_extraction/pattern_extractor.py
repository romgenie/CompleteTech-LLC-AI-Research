"""
Pattern-based relationship extractor for the Research Orchestration Framework.

This module provides a relationship extractor that uses pattern matching to identify
relationships between entities in research documents.
"""

import re
from typing import List, Dict, Any, Optional, Pattern as RegexPattern, Tuple, Set
import logging
import os
import json

from ..entity_recognition.entity import Entity, EntityType
from .base_extractor import RelationshipExtractor
from .relationship import Relationship, RelationType

logger = logging.getLogger(__name__)


class PatternRelationshipExtractor(RelationshipExtractor):
    """Relationship extractor that uses pattern matching.
    
    This extractor uses regular expression patterns to identify relationships
    between entities based on the text between and around them.
    """
    
    # Default patterns for common relationship types
    DEFAULT_PATTERNS = {
        RelationType.TRAINED_ON: [
            r"(?:was |were |is |are )?(?:trained|pre-trained|fine-tuned)(?: on| using| with)(?: the)? \{target\}",
            r"\{target\}(?:-trained| trained)",
            r"training \{source\}(?: on| using| with)(?: the)? \{target\}"
        ],
        RelationType.EVALUATED_ON: [
            r"(?:was |were |is |are )?(?:evaluated|tested|assessed|validated)(?: on| using| with)(?: the)? \{target\}",
            r"(?:evaluating|testing)(?: on| using| with)(?: the)? \{target\}"
        ],
        RelationType.OUTPERFORMS: [
            r"(?:outperforms|surpasses|exceeds|beats|improves upon|performs better than)(?: the)? \{target\}",
            r"(?:higher|better|greater|improved)(?:[ a-z]+?)(?:compared to|versus|against|than)(?: the)? \{target\}",
            r"(?:achieved|showed|demonstrated|obtained|exhibited)(?:[^.]*?)(?:improvements)(?:[^.]*?)(?:compared to|versus|over|against|than)(?: the)? \{target\}"
        ],
        RelationType.BASED_ON: [
            r"(?:is |are )?(?:based on|derived from|built upon|an extension of|a variant of)(?: the)? \{target\}",
            r"(?:extends|modifies|adapts|refines|builds on|improves upon)(?: the)? \{target\}"
        ],
        RelationType.IMPLEMENTED_IN: [
            r"(?:is |are )?(?:implemented in|built with|developed with|created using|written in)(?: the)? \{target\}",
            r"(?:implementation|code)(?: is | was )?(?:available|provided|developed)(?: in| using| with)(?: the)? \{target\}"
        ],
        RelationType.USES: [
            r"(?:uses|utilizes|employs|leverages|applies|incorporates)(?: the)? \{target\}",
            r"(?:using|utilizing|employing|leveraging|applying)(?: the)? \{target\}"
        ],
        RelationType.ACHIEVES: [
            r"(?:achieves|reaches|attains|shows|demonstrates|reports|yields)(?: a| an)? ([0-9.]+%?)(?:[ a-z]+?)?\{target\}",
            r"(?:achieves|reaches|attains|shows|demonstrates|reports|has|with)(?: a| an)? \{target\}(?:[ a-z]+?)?(?:of|at|around)? ([0-9.]+%?)"
        ],
        RelationType.PART_OF: [
            r"(?:is |are )?(?:part of|included in|contained in|a component of|a module in)(?: the)? \{target\}",
            r"\{target\}(?:[ a-z]+?)(?:consists of|contains|includes|incorporates)(?: the)? \{source\}"
        ],
        RelationType.COMPOSED_OF: [
            r"(?:consists of|contains|includes|incorporates|is composed of|is made up of|comprises)(?: the)? \{target\}",
            r"\{target\}(?:[ a-z]+?)(?:is|are)(?: a)?(?: part of| component of| element of) \{source\}"
        ],
        RelationType.DEVELOPED_BY: [
            r"(?:developed|created|proposed|introduced|designed|implemented|built|invented)(?: by)(?: the)? \{target\}",
            r"\{target\}(?:[ a-z]+?)(?:developed|created|proposed|introduced|designed)(?: the)? \{source\}"
        ],
        RelationType.APPLIED_TO: [
            r"(?:applied to|used for|employed for|utilized for|designed for|intended for)(?: the)? \{target\}",
            r"(?:applying|using|employing|utilizing)(?: the)? \{source\}(?:[ a-z]+?)(?:to|for|in)(?: the)? \{target\}"
        ]
    }
    
    # Map of entity type pairs to likely relationship types
    ENTITY_TYPE_RELATIONSHIPS = {
        (EntityType.MODEL, EntityType.DATASET): [RelationType.TRAINED_ON, RelationType.EVALUATED_ON],
        (EntityType.MODEL, EntityType.MODEL): [RelationType.OUTPERFORMS, RelationType.BASED_ON, RelationType.COMPARED_TO],
        (EntityType.MODEL, EntityType.METRIC): [RelationType.ACHIEVES],
        (EntityType.MODEL, EntityType.FRAMEWORK): [RelationType.IMPLEMENTED_IN, RelationType.USES],
        (EntityType.MODEL, EntityType.LIBRARY): [RelationType.USES],
        (EntityType.MODEL, EntityType.ARCHITECTURE): [RelationType.BASED_ON],
        (EntityType.ALGORITHM, EntityType.TASK): [RelationType.APPLIED_TO],
        (EntityType.ARCHITECTURE, EntityType.ARCHITECTURE): [RelationType.BASED_ON, RelationType.COMPARED_TO],
        (EntityType.TECHNIQUE, EntityType.TASK): [RelationType.APPLIED_TO],
        (EntityType.AUTHOR, EntityType.MODEL): [RelationType.DEVELOPED_BY],
        (EntityType.AUTHOR, EntityType.ALGORITHM): [RelationType.DEVELOPED_BY],
        (EntityType.AUTHOR, EntityType.METHODOLOGY): [RelationType.DEVELOPED_BY],
        # Scientific relationships
        (EntityType.THEORY, EntityType.FINDING): [RelationType.EXPLAINS],
        (EntityType.METHODOLOGY, EntityType.FINDING): [RelationType.PRODUCES],
        (EntityType.CONCEPT, EntityType.CONCEPT): [RelationType.IS_A, RelationType.PART_OF]
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Pattern Relationship Extractor.
        
        Args:
            config: Configuration dictionary that can include custom patterns,
                   match thresholds, and other extraction parameters
        """
        # Initialize instance variables before calling super().__init__
        # Compiled regex patterns for each relationship type
        self.patterns: Dict[RelationType, List[RegexPattern]] = {}
        # Custom patterns defined at runtime
        self.custom_patterns: Dict[RelationType, List[str]] = {}
        # Context window size for relationship extraction
        self.context_window_size = 150
        # Maximum distance between entities for relationship consideration
        self.max_entity_distance = 500
        
        # Now call the parent constructor which will call _initialize_from_config
        super().__init__(config)
        
    def _initialize_from_config(self) -> None:
        """Initialize the extractor based on configuration."""
        # Load custom patterns from config
        custom_patterns = self.config.get("patterns", {})
        
        # Update instance variables
        self.context_window_size = self.config.get("context_window_size", self.context_window_size)
        self.max_entity_distance = self.config.get("max_entity_distance", self.max_entity_distance)
        
        # Load custom entity type relationship mappings
        entity_relationships = self.config.get("entity_type_relationships", {})
        if entity_relationships:
            for key, values in entity_relationships.items():
                try:
                    entity_type_pair = tuple(map(lambda x: EntityType.from_string(x), key.split(",")))
                    relation_types = [RelationType.from_string(rel) for rel in values]
                    self.ENTITY_TYPE_RELATIONSHIPS[entity_type_pair] = relation_types
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid entity type relationship mapping: {key} -> {values}. Error: {e}")
        
        # Combine default and custom patterns
        all_patterns = {rel_type: patterns.copy() for rel_type, patterns in self.DEFAULT_PATTERNS.items()}
        
        # Add custom patterns
        for rel_type_str, patterns in custom_patterns.items():
            try:
                rel_type = RelationType.from_string(rel_type_str)
                if rel_type not in all_patterns:
                    all_patterns[rel_type] = []
                all_patterns[rel_type].extend(patterns)
            except Exception as e:
                logger.warning(f"Invalid pattern configuration for {rel_type_str}: {e}")
        
        # Compile the patterns
        for rel_type, patterns in all_patterns.items():
            self.patterns[rel_type] = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        # Load patterns from file if specified
        patterns_file = self.config.get("patterns_file")
        if patterns_file and os.path.exists(patterns_file):
            self._load_patterns_from_file(patterns_file)
            
    def _load_patterns_from_file(self, filepath: str) -> None:
        """Load relationship patterns from a JSON file.
        
        The file should have the format:
        {
            "relationship_type": [
                "pattern1",
                "pattern2"
            ],
            ...
        }
        
        Args:
            filepath: Path to the patterns JSON file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                patterns_dict = json.load(f)
            
            for rel_type_str, patterns in patterns_dict.items():
                try:
                    rel_type = RelationType.from_string(rel_type_str)
                    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
                    
                    if rel_type not in self.patterns:
                        self.patterns[rel_type] = []
                    
                    self.patterns[rel_type].extend(compiled_patterns)
                    
                except Exception as e:
                    logger.warning(f"Error loading pattern for {rel_type_str}: {e}")
            
            logger.info(f"Loaded relationship patterns from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load patterns from {filepath}: {e}")
    
    def add_pattern(self, relation_type: RelationType, pattern: str) -> None:
        """Add a new pattern for a relationship type.
        
        Args:
            relation_type: The relationship type for the pattern
            pattern: Regular expression pattern string
        """
        if relation_type not in self.patterns:
            self.patterns[relation_type] = []
        
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        self.patterns[relation_type].append(compiled_pattern)
        
        # Also store the original pattern string
        if relation_type not in self.custom_patterns:
            self.custom_patterns[relation_type] = []
        self.custom_patterns[relation_type].append(pattern)
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships between entities in the provided text.
        
        Args:
            text: The text to analyze for relationships
            entities: List of entities to find relationships between
            
        Returns:
            A list of detected relationships
        """
        # Find potential entity pairs based on proximity
        entity_pairs = self.find_entity_pairs(entities, self.max_entity_distance)
        
        # Extract relationships from the pairs
        all_relationships = []
        
        for source, target in entity_pairs:
            # Get context window for this entity pair
            context = self.get_entity_pair_context(
                text, source, target, self.context_window_size
            )
            
            if not context:
                continue
            
            # Get potential relationship types based on entity types
            possible_relations = self._get_possible_relation_types(source, target)
            
            # Try to match patterns for the possible relationship types
            relationships = self._match_patterns(
                context, source, target, possible_relations
            )
            
            all_relationships.extend(relationships)
        
        # Remove duplicate relationships
        unique_relationships = self._remove_duplicates(all_relationships)
        
        # Save the relationships for later use
        self.relationships = unique_relationships
        
        return unique_relationships
    
    def _get_possible_relation_types(
        self, source: Entity, target: Entity
    ) -> List[RelationType]:
        """Get possible relationship types based on entity types.
        
        Args:
            source: Source entity
            target: Target entity
            
        Returns:
            List of possible relationship types
        """
        # Try to find a matching entity type pair
        entity_pair = (source.type, target.type)
        
        # Check if we have predefined relationships for this entity type pair
        if entity_pair in self.ENTITY_TYPE_RELATIONSHIPS:
            return self.ENTITY_TYPE_RELATIONSHIPS[entity_pair]
        
        # If no specific mapping, return all relationship types
        return list(self.patterns.keys())
    
    def _match_patterns(
        self,
        context: str,
        source: Entity,
        target: Entity,
        relation_types: List[RelationType]
    ) -> List[Relationship]:
        """Try to match relationship patterns in the context.
        
        Args:
            context: Text context between and around the entities
            source: Source entity
            target: Target entity
            relation_types: List of relationship types to check
            
        Returns:
            List of detected relationships
        """
        results = []
        
        # Prepare entity texts for substitution
        source_text = re.escape(source.text)
        target_text = re.escape(target.text)
        
        for rel_type in relation_types:
            # Skip if we don't have patterns for this relationship type
            if rel_type not in self.patterns:
                continue
            
            for pattern in self.patterns[rel_type]:
                # Substitute the entity placeholders with the actual entity texts
                entity_pattern_str = pattern.pattern
                entity_pattern_str = entity_pattern_str.replace(r'\{source\}', source_text)
                entity_pattern_str = entity_pattern_str.replace(r'\{target\}', target_text)
                
                try:
                    entity_pattern = re.compile(entity_pattern_str, re.IGNORECASE)
                    
                    # Look for the pattern in the context
                    matches = list(entity_pattern.finditer(context))
                    
                    if matches:
                        # Create a relationship for each match
                        for match in matches:
                            # Calculate confidence based on match quality
                            confidence = self._calculate_confidence(
                                match, context, source, target, rel_type
                            )
                            
                            # Extract any numeric values for certain relationship types
                            metadata = {}
                            if rel_type == RelationType.ACHIEVES and match.lastindex and match.lastindex >= 1:
                                metadata["value"] = match.group(1)
                            
                            # Get the matched context
                            match_context = match.group(0)
                            
                            # Create the relationship
                            relationship = Relationship(
                                source=source,
                                target=target,
                                relation_type=rel_type,
                                confidence=confidence,
                                context=match_context,
                                metadata=metadata
                            )
                            
                            results.append(relationship)
                
                except re.error as e:
                    logger.warning(f"Invalid pattern after substitution: {e}")
                    continue
        
        return results
    
    def _calculate_confidence(
        self,
        match: re.Match,
        context: str,
        source: Entity,
        target: Entity,
        relation_type: RelationType
    ) -> float:
        """Calculate confidence score for a relationship match.
        
        Args:
            match: The regex match object
            context: The full context string
            source: Source entity
            target: Target entity
            relation_type: Type of relationship
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence
        confidence = 0.7
        
        # Adjust based on match quality
        match_length = len(match.group(0))
        context_length = len(context)
        
        # Longer matches relative to context are better
        if match_length > 20:
            confidence += 0.1
        
        # Adjust based on entity confidence
        source_confidence = getattr(source, 'confidence', 1.0)
        target_confidence = getattr(target, 'confidence', 1.0)
        entity_confidence = (source_confidence + target_confidence) / 2
        confidence *= entity_confidence
        
        # Adjust based on word distance between entities
        if source.start_pos is not None and source.end_pos is not None and \
           target.start_pos is not None and target.end_pos is not None:
            
            # Entities closer together are more likely to be related
            distance = abs(target.start_pos - source.end_pos)
            if distance < 50:
                confidence += 0.1
            elif distance > 200:
                confidence -= 0.1
        
        # Ensure confidence is within valid range
        return max(0.0, min(1.0, confidence))
    
    def _remove_duplicates(self, relationships: List[Relationship]) -> List[Relationship]:
        """Remove duplicate relationships based on source, target, and type.
        
        When duplicates are found, keep the one with the highest confidence.
        
        Args:
            relationships: List of relationships that may contain duplicates
            
        Returns:
            List with duplicates removed
        """
        unique_relationships = {}
        
        for rel in relationships:
            # Create a key based on source, target, and relation type
            key = (rel.source.id, rel.target.id, rel.relation_type)
            
            # Keep the relationship with the highest confidence
            if key not in unique_relationships or rel.confidence > unique_relationships[key].confidence:
                unique_relationships[key] = rel
        
        return list(unique_relationships.values())