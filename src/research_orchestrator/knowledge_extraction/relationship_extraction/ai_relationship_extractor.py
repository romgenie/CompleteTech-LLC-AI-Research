"""
AI-specific Relationship Extractor module for the Knowledge Extraction Pipeline.

This module provides specialized functionality for extracting relationships between
AI-specific entities in research papers, such as model-dataset relationships,
method-performance relationships, and architecture relationships.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any, Pattern
import logging

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import Entity
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship_extractor import RelationshipExtractor, Relationship
from src.research_orchestrator.knowledge_extraction.relationship_extraction.pattern_relationship_extractor import PatternRelationshipExtractor
from src.research_orchestrator.adapters.karma_adapter.karma_adapter import KARMAAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI-specific relation types
AI_RELATION_TYPES = [
    "trained_on",
    "evaluated_on",
    "outperforms",
    "based_on",
    "implements",
    "uses",
    "achieves",
    "compared_to",
    "feature_of",
    "parameter_of",
    "hyperparameter_of",
    "variation_of",
    "improved_version_of",
    "applied_to"
]

# Default AI-specific relation patterns
DEFAULT_AI_RELATION_PATTERNS = {
    "trained_on": [
        r"(\w+) (?:was|is|were|are) trained on (?:the )?([\w\-\s]+) dataset",
        r"(\w+) (?:was|is|were|are) trained using (?:the )?([\w\-\s]+) dataset",
        r"train(?:ed|ing) (?:the )?([\w\-\s]+) (?:model|algorithm|architecture) on (?:the )?([\w\-\s]+)"
    ],
    "evaluated_on": [
        r"(\w+) (?:was|is|were|are) evaluated on (?:the )?([\w\-\s]+)",
        r"(\w+) (?:was|is|were|are) tested on (?:the )?([\w\-\s]+)",
        r"evaluation of (?:the )?([\w\-\s]+) on (?:the )?([\w\-\s]+)"
    ],
    "outperforms": [
        r"(\w+) outperform(?:s|ed) (?:the )?([\w\-\s]+)",
        r"(\w+) (?:achieve|achieves|achieved) better (?:results|performance) than (?:the )?([\w\-\s]+)",
        r"(\w+) (?:is|was|are|were) superior to (?:the )?([\w\-\s]+)"
    ],
    "based_on": [
        r"(\w+) (?:is|was|are|were) based on (?:the )?([\w\-\s]+)",
        r"(\w+) extend(?:s|ed) (?:the )?([\w\-\s]+)",
        r"(\w+) (?:is|was|are|were) an extension of (?:the )?([\w\-\s]+)"
    ],
    "achieves": [
        r"(\w+) achieve(?:s|d) ([\d\.]+\%?) (?:on|in) ([\w\-\s]+)",
        r"(\w+) reach(?:es|ed) ([\d\.]+\%?) (?:on|in) ([\w\-\s]+)",
        r"(\w+) obtain(?:s|ed) ([\d\.]+\%?) (?:on|in) ([\w\-\s]+)"
    ],
    "uses": [
        r"(\w+) use(?:s|d) (?:the )?([\w\-\s]+)",
        r"(\w+) employ(?:s|ed) (?:the )?([\w\-\s]+)",
        r"(\w+) utilize(?:s|d) (?:the )?([\w\-\s]+)"
    ]
}


class AIRelationshipExtractor(RelationshipExtractor):
    """
    Specialized relationship extractor for AI research papers that identifies
    relationships between AI-specific entities such as models, datasets, metrics, etc.
    """
    
    def __init__(self, relation_types: Optional[List[str]] = None,
                 config_path: Optional[str] = None,
                 custom_patterns: Optional[Dict[str, List[str]]] = None,
                 use_karma: bool = False,
                 karma_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI relationship extractor.
        
        Args:
            relation_types: List of AI relationship types to extract
            config_path: Path to configuration file
            custom_patterns: Custom patterns for extracting relationships
            use_karma: Whether to use the KARMA adapter for relationship extraction
            karma_config: Configuration for the KARMA adapter
        """
        self.relation_types = relation_types or AI_RELATION_TYPES
        self.custom_patterns = custom_patterns or {}
        self.use_karma = use_karma
        
        # Initialize parent class
        super().__init__(self.relation_types, config_path)
        
        # Initialize pattern-based extractor
        self.pattern_extractor = PatternRelationshipExtractor(
            relation_types=self.relation_types,
            config_path=config_path,
            custom_patterns=self._prepare_ai_patterns()
        )
        
        # Initialize KARMA adapter if needed
        self.karma_adapter = None
        if self.use_karma:
            try:
                self.karma_adapter = KARMAAdapter(**(karma_config or {}))
            except Exception as e:
                logger.error(f"Failed to initialize KARMA adapter: {e}")
                self.use_karma = False
        
        # Initialize AI-specific entity type pairs that commonly form relationships
        self.entity_type_pairs = self._initialize_entity_type_pairs()
    
    def _prepare_ai_patterns(self) -> Dict[str, List[str]]:
        """Prepare AI-specific patterns by combining default and custom patterns."""
        patterns = {}
        
        # Add default AI patterns
        for relation_type in self.relation_types:
            if relation_type in DEFAULT_AI_RELATION_PATTERNS:
                patterns[relation_type] = DEFAULT_AI_RELATION_PATTERNS[relation_type].copy()
        
        # Add custom patterns
        for relation_type, rel_patterns in self.custom_patterns.items():
            if relation_type in self.relation_types:
                if relation_type not in patterns:
                    patterns[relation_type] = []
                patterns[relation_type].extend(rel_patterns)
        
        return patterns
    
    def _initialize_entity_type_pairs(self) -> List[Tuple[str, str, str]]:
        """
        Initialize common entity type pairs that form relationships.
        
        Returns:
            List of (source_type, target_type, relation_type) tuples
        """
        return [
            ("model", "dataset", "trained_on"),
            ("model", "dataset", "evaluated_on"),
            ("model", "model", "outperforms"),
            ("model", "model", "based_on"),
            ("algorithm", "algorithm", "based_on"),
            ("model", "metric", "achieves"),
            ("model", "task", "applied_to"),
            ("algorithm", "task", "applied_to"),
            ("model", "framework", "uses"),
            ("model", "technique", "uses")
        ]
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract AI-specific relationships between entities in the given text.
        
        Args:
            text: The text to analyze
            entities: List of entities to find relationships between
            
        Returns:
            List of extracted relationships
        """
        relationships = []
        
        # Use pattern-based extraction
        pattern_relationships = self.pattern_extractor.extract_relationships(text, entities)
        relationships.extend(pattern_relationships)
        
        # Use entity type pair heuristics
        pair_relationships = self._extract_relationships_from_entity_pairs(text, entities)
        relationships.extend(pair_relationships)
        
        # Use KARMA adapter if available
        if self.use_karma and self.karma_adapter:
            karma_relationships = self._extract_relationships_with_karma(text, entities)
            relationships.extend(karma_relationships)
        
        # Extract performance relationships
        performance_relationships = self._extract_performance_relationships(text, entities)
        relationships.extend(performance_relationships)
        
        # Remove duplicates
        unique_relationships = self._remove_duplicate_relationships(relationships)
        
        return unique_relationships
    
    def _extract_relationships_from_entity_pairs(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract relationships based on entity type pairs and proximity.
        
        Args:
            text: The text to analyze
            entities: List of entities
            
        Returns:
            List of extracted relationships
        """
        relationships = []
        relationship_id = 0
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            if entity.type not in entities_by_type:
                entities_by_type[entity.type] = []
            entities_by_type[entity.type].append(entity)
        
        # Find entity pairs based on common type pairs
        for source_type, target_type, relation_type in self.entity_type_pairs:
            if source_type not in entities_by_type or target_type not in entities_by_type:
                continue
            
            for source_entity in entities_by_type[source_type]:
                for target_entity in entities_by_type[target_type]:
                    # Skip self-relationships
                    if source_entity.id == target_entity.id:
                        continue
                    
                    # Check if entities are close to each other
                    distance = abs(source_entity.start_pos - target_entity.start_pos)
                    if distance > 500:  # Arbitrary distance threshold
                        continue
                    
                    # Get context
                    context = self.get_entity_pair_context(text, source_entity, target_entity)
                    
                    # Calculate confidence based on distance and entity types
                    confidence = self._calculate_pair_confidence(source_entity, target_entity, distance)
                    
                    # Create relationship
                    relationship = Relationship(
                        id=f"pair_relationship_{relationship_id}",
                        source_entity=source_entity,
                        target_entity=target_entity,
                        relation_type=relation_type,
                        confidence=confidence,
                        context=context,
                        metadata={"distance": distance}
                    )
                    
                    relationships.append(relationship)
                    relationship_id += 1
        
        return relationships
    
    def _extract_relationships_with_karma(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract relationships using the KARMA adapter.
        
        Args:
            text: The text to analyze
            entities: List of entities
            
        Returns:
            List of extracted relationships
        """
        relationships = []
        relationship_id = 0
        
        try:
            # Extract relationships using KARMA
            karma_triples = self.karma_adapter.extract_relationships(text)
            
            # Create entity lookup dictionary for faster access
            entity_by_text = {}
            for entity in entities:
                entity_text = entity.text.lower()
                if entity_text not in entity_by_text:
                    entity_by_text[entity_text] = []
                entity_by_text[entity_text].append(entity)
            
            for triple in karma_triples:
                subject = triple.get("subject", "")
                relation = triple.get("relation", "")
                object_ = triple.get("object", "")
                
                # Map KARMA relation to our relation types
                relation_type = self._map_karma_relation(relation)
                if not relation_type:
                    continue
                
                # Look up entities by text
                subject_entities = entity_by_text.get(subject.lower(), [])
                object_entities = entity_by_text.get(object_.lower(), [])
                
                # If we found both entities, create a relationship
                if subject_entities and object_entities:
                    source_entity = subject_entities[0]
                    target_entity = object_entities[0]
                    
                    confidence = triple.get("confidence", 0.8)
                    
                    relationship = Relationship(
                        id=f"karma_relationship_{relationship_id}",
                        source_entity=source_entity,
                        target_entity=target_entity,
                        relation_type=relation_type,
                        confidence=confidence,
                        context=triple.get("context", ""),
                        metadata={"source": "karma", "original_relation": relation}
                    )
                    
                    relationships.append(relationship)
                    relationship_id += 1
                    
        except Exception as e:
            logger.error(f"Error extracting relationships with KARMA: {e}")
        
        return relationships
    
    def _extract_performance_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """
        Extract model-performance relationships.
        
        Args:
            text: The text to analyze
            entities: List of entities
            
        Returns:
            List of extracted relationships
        """
        relationships = []
        relationship_id = 0
        
        # Find model entities
        model_entities = [e for e in entities if e.type == "model"]
        # Find metric entities
        metric_entities = [e for e in entities if e.type == "metric"]
        
        # Performance pattern
        performance_pattern = re.compile(r"([\w\-]+)(?:\s+model)?\s+(?:achieves|achieved|obtains|obtained|reaches|reached|reports|reported)\s+([\d\.]+\%?)\s+(?:on|in)\s+([\w\-]+)")
        
        for match in performance_pattern.finditer(text):
            model_name = match.group(1)
            performance_value = match.group(2)
            metric_name = match.group(3)
            
            # Find model entity
            model_entity = None
            for entity in model_entities:
                if model_name.lower() in entity.text.lower():
                    model_entity = entity
                    break
            
            # Find metric entity
            metric_entity = None
            for entity in metric_entities:
                if metric_name.lower() in entity.text.lower():
                    metric_entity = entity
                    break
            
            # If we found both entities, create a relationship
            if model_entity and metric_entity:
                # Get context
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(text), match.end() + 50)
                context = text[start_pos:end_pos]
                
                # Create relationship
                relationship = Relationship(
                    id=f"performance_relationship_{relationship_id}",
                    source_entity=model_entity,
                    target_entity=metric_entity,
                    relation_type="achieves",
                    confidence=0.85,
                    context=context,
                    metadata={"performance_value": performance_value}
                )
                
                relationships.append(relationship)
                relationship_id += 1
        
        return relationships
    
    def _calculate_pair_confidence(self, source_entity: Entity, target_entity: Entity, 
                                  distance: int) -> float:
        """
        Calculate confidence score for an entity pair relationship.
        
        Args:
            source_entity: The source entity
            target_entity: The target entity
            distance: The distance between the entities
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence
        confidence = 0.6
        
        # Adjust based on entity confidence
        entity_confidence = (source_entity.confidence + target_entity.confidence) / 2
        confidence = (confidence + entity_confidence) / 2
        
        # Adjust based on distance
        if distance < 50:
            confidence += 0.2
        elif distance < 200:
            confidence += 0.1
        elif distance > 400:
            confidence -= 0.1
        
        # Clamp the confidence between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _map_karma_relation(self, karma_relation: str) -> Optional[str]:
        """
        Map KARMA relation to our relation types.
        
        Args:
            karma_relation: The KARMA relation
            
        Returns:
            Mapped relation type, or None if not mappable
        """
        # Normalize the karma relation
        karma_relation = karma_relation.lower()
        
        # Mapping of KARMA relations to our relation types
        mapping = {
            "trained on": "trained_on",
            "evaluated on": "evaluated_on",
            "outperforms": "outperforms",
            "based on": "based_on",
            "implements": "implements",
            "uses": "uses",
            "achieves": "achieves",
            "compared to": "compared_to",
            "feature of": "feature_of",
            "parameter of": "parameter_of",
            "variation of": "variation_of",
            "improved version of": "improved_version_of",
            "applied to": "applied_to"
        }
        
        # Try exact match first
        if karma_relation in mapping:
            return mapping[karma_relation]
        
        # Try substring match
        for karma_key, relation_type in mapping.items():
            if karma_key in karma_relation or karma_relation in karma_key:
                return relation_type
        
        return None
    
    def _remove_duplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """
        Remove duplicate relationships, keeping the one with the highest confidence.
        
        Args:
            relationships: List of relationships
            
        Returns:
            List of unique relationships
        """
        unique_relationships = {}
        
        for relationship in relationships:
            # Create a key for the relationship
            key = (relationship.source_entity.id, relationship.target_entity.id, relationship.relation_type)
            
            # Check if we've seen this relationship before
            if key in unique_relationships:
                # Keep the relationship with the highest confidence
                if relationship.confidence > unique_relationships[key].confidence:
                    unique_relationships[key] = relationship
            else:
                unique_relationships[key] = relationship
        
        return list(unique_relationships.values())
    
    def extract_model_performance(self, relationships: List[Relationship]) -> Dict[str, Dict[str, float]]:
        """
        Extract model performance from relationships.
        
        Args:
            relationships: List of relationships
            
        Returns:
            Dictionary mapping model names to dictionaries of metric:value pairs
        """
        model_performance = {}
        
        for relationship in relationships:
            if relationship.relation_type == "achieves" and "performance_value" in relationship.metadata:
                model_name = relationship.source_entity.text
                metric_name = relationship.target_entity.text
                performance_value = relationship.metadata["performance_value"]
                
                # Convert percentage string to float if possible
                try:
                    if performance_value.endswith("%"):
                        performance_value = float(performance_value[:-1]) / 100
                    else:
                        performance_value = float(performance_value)
                except ValueError:
                    continue
                
                # Add to model performance dictionary
                if model_name not in model_performance:
                    model_performance[model_name] = {}
                
                model_performance[model_name][metric_name] = performance_value
        
        return model_performance
    
    def extract_model_hierarchy(self, relationships: List[Relationship]) -> Dict[str, List[str]]:
        """
        Extract model hierarchy from relationships.
        
        Args:
            relationships: List of relationships
            
        Returns:
            Dictionary mapping model names to lists of base models
        """
        model_hierarchy = {}
        
        for relationship in relationships:
            if relationship.relation_type == "based_on":
                model_name = relationship.source_entity.text
                base_model = relationship.target_entity.text
                
                if model_name not in model_hierarchy:
                    model_hierarchy[model_name] = []
                
                model_hierarchy[model_name].append(base_model)
        
        return model_hierarchy