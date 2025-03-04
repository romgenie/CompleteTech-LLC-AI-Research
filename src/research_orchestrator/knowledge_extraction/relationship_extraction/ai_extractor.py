"""
AI-specific relationship extractor for the Research Orchestration Framework.

This module provides a specialized relationship extractor for identifying relationships
specific to AI research, such as model performance, architecture comparisons, etc.
"""

import re
from typing import List, Dict, Any, Optional, Pattern as RegexPattern, Tuple, Set
import logging
from collections import defaultdict

from ..entity_recognition.entity import Entity, EntityType
from .base_extractor import RelationshipExtractor
from .relationship import Relationship, RelationType

logger = logging.getLogger(__name__)


class AIRelationshipExtractor(RelationshipExtractor):
    """Relationship extractor specialized for AI research relationships.
    
    This extractor focuses on finding relationships specific to AI research,
    such as model performance comparisons, architecture lineage, and more.
    """
    
    # Special patterns for AI-specific relationship extraction
    AI_PATTERNS = {
        # Performance-related patterns
        "performance": [
            r"([\w\-]+) (?:achieves|reaches|attains|reports|shows) (?:an? )?([\d.]+\%?)(?:[ \w]+)?(accuracy|precision|recall|F1|score|performance|error rate|perplexity)",
            r"([\w\-]+) (?:outperforms|exceeds|beats|improves upon) ([\w\-]+)",
            r"([\d.]+\%?)(?:[ \w]+)?(accuracy|precision|recall|F1|score|mAP) (?:of|for|on|using) ([\w\-]+)"
        ],
        # Architecture-related patterns
        "architecture": [
            r"([\w\-]+) (?:is based on|extends|builds upon|modifies) ([\w\-]+)",
            r"([\w\-]+) (?:architecture|model) (?:with|using|based on) ([\w\-]+)",
            r"([\w\-]+) (?:incorporates|integrates|uses) ([\w\-]+)"
        ],
        # Dataset-related patterns
        "dataset": [
            r"([\w\-]+) (?:trained|fine-tuned|evaluated|tested) on(?: the)? ([\w\-]+)(?: dataset)?",
            r"([\w\-]+) dataset (?:contains|includes|consists of) ([\d,]+) (images|samples|examples|instances)"
        ],
        # Framework-related patterns
        "framework": [
            r"([\w\-]+) implemented (?:in|using|with) ([\w\-]+)",
            r"([\w\-]+) code (?:in|using) ([\w\-]+)"
        ]
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI Relationship Extractor.
        
        Args:
            config: Configuration dictionary for customized extraction
        """
        # Initialize instance variables before calling super().__init__
        self.compiled_patterns: Dict[str, List[RegexPattern]] = {}
        self.performance_metrics = [
            "accuracy", "precision", "recall", "F1", "mAP", "BLEU", "ROUGE", 
            "perplexity", "error rate", "WER", "CER", "IoU", "AUC"
        ]
        
        # Now call the parent constructor which will call _initialize_from_config
        super().__init__(config)
    
    def _initialize_from_config(self) -> None:
        """Initialize extractor patterns and settings from configuration."""
        # Compile the patterns
        for category, patterns in self.AI_PATTERNS.items():
            self.compiled_patterns[category] = [re.compile(p, re.IGNORECASE) for p in patterns]
        
        # Override performance metrics if provided in config
        if "performance_metrics" in self.config:
            self.performance_metrics = self.config["performance_metrics"]
    
    def extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract AI-specific relationships from text.
        
        This method combines several specialized extraction techniques focused
        on AI research relationships.
        
        Args:
            text: Text to analyze
            entities: List of extracted entities
            
        Returns:
            List of extracted relationships
        """
        # Extract relationships using various techniques
        all_relationships = []
        
        # 1. Extract performance relationships
        performance_rels = self._extract_performance_relationships(text, entities)
        all_relationships.extend(performance_rels)
        
        # 2. Extract model-dataset relationships
        dataset_rels = self._extract_model_dataset_relationships(text, entities)
        all_relationships.extend(dataset_rels)
        
        # 3. Extract architecture lineage
        architecture_rels = self._extract_architecture_relationships(text, entities)
        all_relationships.extend(architecture_rels)
        
        # 4. Extract implementation relationships
        implementation_rels = self._extract_implementation_relationships(text, entities)
        all_relationships.extend(implementation_rels)
        
        # 5. Extract entity context-based relationships
        context_rels = self._extract_entity_context_relationships(text, entities)
        all_relationships.extend(context_rels)
        
        # Deduplicate and store
        unique_relationships = self._deduplicate_relationships(all_relationships)
        self.relationships = unique_relationships
        
        return unique_relationships
    
    def _extract_performance_relationships(
        self, text: str, entities: List[Entity]
    ) -> List[Relationship]:
        """Extract relationships related to model performance.
        
        Args:
            text: Text to analyze
            entities: List of extracted entities
            
        Returns:
            List of performance-related relationships
        """
        relationships = []
        
        # Find model entities
        model_entities = [e for e in entities if e.type == EntityType.MODEL]
        metric_entities = [e for e in entities if e.type == EntityType.METRIC]
        
        # Extract relationships using performance patterns
        for pattern in self.compiled_patterns.get("performance", []):
            for match in pattern.finditer(text):
                # Try to match entities to the captured groups
                if match.lastindex and match.lastindex >= 2:
                    # This could be a performance metric pattern
                    model_name = match.group(1)
                    metric_value = None
                    metric_name = None
                    
                    # Parse different pattern formats
                    if match.lastindex == 2:
                        # Model + Metric Value pattern
                        metric_value = match.group(2)
                    elif match.lastindex >= 3:
                        if any(metric in match.group(3).lower() for metric in self.performance_metrics):
                            # Model + Value + Metric pattern
                            metric_value = match.group(2)
                            metric_name = match.group(3)
                        else:
                            # Model + Compares to + Model pattern
                            second_model = match.group(2)
                            rel_type = RelationType.OUTPERFORMS
                            
                            # Find matching model entities
                            source_model = self._find_best_match(model_name, model_entities)
                            target_model = self._find_best_match(second_model, model_entities)
                            
                            if source_model and target_model:
                                rel = Relationship(
                                    source=source_model,
                                    target=target_model,
                                    relation_type=rel_type,
                                    confidence=0.8,
                                    context=match.group(0)
                                )
                                relationships.append(rel)
                    
                    # Handle performance metric relationships
                    if metric_value:
                        source_model = self._find_best_match(model_name, model_entities)
                        
                        if source_model:
                            # Try to find a matching metric entity
                            target_metric = None
                            if metric_name:
                                target_metric = self._find_matching_metric(metric_name, metric_entities)
                            
                            if not target_metric and metric_entities:
                                # Use the first metric entity if available
                                target_metric = metric_entities[0]
                            
                            if not target_metric:
                                # Create a new metric entity if needed
                                from ..entity_recognition.entity import Entity
                                metric_text = metric_name or "accuracy"
                                target_metric = Entity(
                                    text=metric_text,
                                    type=EntityType.METRIC,
                                    confidence=0.7
                                )
                            
                            # Create the relationship
                            rel = Relationship(
                                source=source_model,
                                target=target_metric,
                                relation_type=RelationType.ACHIEVES,
                                confidence=0.8,
                                context=match.group(0),
                                metadata={"value": metric_value}
                            )
                            relationships.append(rel)
        
        return relationships
    
    def _extract_model_dataset_relationships(
        self, text: str, entities: List[Entity]
    ) -> List[Relationship]:
        """Extract relationships between models and datasets.
        
        Args:
            text: Text to analyze
            entities: List of extracted entities
            
        Returns:
            List of model-dataset relationships
        """
        relationships = []
        
        # Find model and dataset entities
        model_entities = [e for e in entities if e.type == EntityType.MODEL]
        dataset_entities = [e for e in entities if e.type == EntityType.DATASET]
        
        if not model_entities or not dataset_entities:
            return relationships
        
        # Extract relationships using dataset patterns
        for pattern in self.compiled_patterns.get("dataset", []):
            for match in pattern.finditer(text):
                if match.lastindex and match.lastindex >= 2:
                    first_group = match.group(1)
                    second_group = match.group(2)
                    
                    # Determine if this is a model-dataset relationship
                    model_entity = self._find_best_match(first_group, model_entities)
                    dataset_entity = self._find_best_match(second_group, dataset_entities)
                    
                    if model_entity and dataset_entity:
                        rel = Relationship(
                            source=model_entity,
                            target=dataset_entity,
                            relation_type=RelationType.TRAINED_ON,
                            confidence=0.8,
                            context=match.group(0)
                        )
                        relationships.append(rel)
        
        # Also look for train/evaluation keywords near model-dataset pairs
        for model in model_entities:
            for dataset in dataset_entities:
                # Skip entities without position information
                if model.start_pos is None or model.end_pos is None or \
                   dataset.start_pos is None or dataset.end_pos is None:
                    continue
                
                # Check for proximity
                if abs(model.start_pos - dataset.end_pos) <= 100 or \
                   abs(dataset.start_pos - model.end_pos) <= 100:
                    
                    # Get context between entities
                    start = min(model.start_pos, dataset.start_pos)
                    end = max(model.end_pos, dataset.end_pos)
                    context = text[max(0, start-50):min(len(text), end+50)]
                    
                    relation_type = None
                    confidence = 0.6
                    
                    # Determine relationship type from context
                    if re.search(r'train|trained|fine-tun|pretrain', context, re.IGNORECASE):
                        relation_type = RelationType.TRAINED_ON
                        confidence = 0.8
                    elif re.search(r'evaluat|test|validat|benchmark', context, re.IGNORECASE):
                        relation_type = RelationType.EVALUATED_ON
                        confidence = 0.8
                    elif re.search(r'experimen|stud|analyz', context, re.IGNORECASE):
                        relation_type = RelationType.EVALUATED_ON
                        confidence = 0.6
                    
                    if relation_type:
                        rel = Relationship(
                            source=model,
                            target=dataset,
                            relation_type=relation_type,
                            confidence=confidence,
                            context=context
                        )
                        relationships.append(rel)
        
        return relationships
    
    def _extract_architecture_relationships(
        self, text: str, entities: List[Entity]
    ) -> List[Relationship]:
        """Extract relationships between architectures and models.
        
        Args:
            text: Text to analyze
            entities: List of extracted entities
            
        Returns:
            List of architecture relationships
        """
        relationships = []
        
        # Find relevant entities
        model_entities = [e for e in entities if e.type == EntityType.MODEL]
        architecture_entities = [e for e in entities if e.type == EntityType.ARCHITECTURE]
        
        # Extract relationships using architecture patterns
        for pattern in self.compiled_patterns.get("architecture", []):
            for match in pattern.finditer(text):
                if match.lastindex and match.lastindex >= 2:
                    first = match.group(1)
                    second = match.group(2)
                    
                    # Try to match as model-architecture
                    source = self._find_best_match(first, model_entities)
                    target = self._find_best_match(second, architecture_entities)
                    
                    if source and target:
                        rel = Relationship(
                            source=source,
                            target=target,
                            relation_type=RelationType.BASED_ON,
                            confidence=0.8,
                            context=match.group(0)
                        )
                        relationships.append(rel)
                    else:
                        # Try to match as model-model
                        source = self._find_best_match(first, model_entities)
                        target = self._find_best_match(second, model_entities)
                        
                        if source and target:
                            rel = Relationship(
                                source=source,
                                target=target,
                                relation_type=RelationType.BASED_ON,
                                confidence=0.7,
                                context=match.group(0)
                            )
                            relationships.append(rel)
        
        return relationships
    
    def _extract_implementation_relationships(
        self, text: str, entities: List[Entity]
    ) -> List[Relationship]:
        """Extract relationships between models and frameworks/libraries.
        
        Args:
            text: Text to analyze
            entities: List of extracted entities
            
        Returns:
            List of implementation relationships
        """
        relationships = []
        
        # Find relevant entities
        model_entities = [e for e in entities if e.type == EntityType.MODEL]
        framework_entities = [e for e in entities if e.type == EntityType.FRAMEWORK]
        library_entities = [e for e in entities if e.type == EntityType.LIBRARY]
        
        # Combine framework and library entities
        implementation_entities = framework_entities + library_entities
        
        # Extract relationships using framework patterns
        for pattern in self.compiled_patterns.get("framework", []):
            for match in pattern.finditer(text):
                if match.lastindex and match.lastindex >= 2:
                    first = match.group(1)
                    second = match.group(2)
                    
                    # Try to match as model-framework
                    source = self._find_best_match(first, model_entities)
                    target = self._find_best_match(second, implementation_entities)
                    
                    if source and target:
                        rel = Relationship(
                            source=source,
                            target=target,
                            relation_type=RelationType.IMPLEMENTED_IN,
                            confidence=0.8,
                            context=match.group(0)
                        )
                        relationships.append(rel)
        
        return relationships
    
    def _extract_entity_context_relationships(
        self, text: str, entities: List[Entity]
    ) -> List[Relationship]:
        """Extract relationships based on entity context analysis.
        
        This method examines the context around entities to identify
        relationships that may not be captured by specific patterns.
        
        Args:
            text: Text to analyze
            entities: List of extracted entities
            
        Returns:
            List of context-based relationships
        """
        relationships = []
        
        # Find entity pairs that are close to each other
        entity_pairs = self.find_entity_pairs(entities, 150)
        
        for source, target in entity_pairs:
            # Skip if entities are the same
            if source.id == target.id:
                continue
            
            # Get context between entities
            if source.start_pos is None or source.end_pos is None or \
               target.start_pos is None or target.end_pos is None:
                continue
            
            start = min(source.start_pos, target.start_pos)
            end = max(source.end_pos, target.end_pos)
            context = text[max(0, start-30):min(len(text), end+30)]
            
            # Try to infer relationship type from entity types and context
            rel_type, confidence = self._infer_relationship_from_context(
                source, target, context
            )
            
            if rel_type:
                rel = Relationship(
                    source=source,
                    target=target,
                    relation_type=rel_type,
                    confidence=confidence,
                    context=context
                )
                relationships.append(rel)
        
        return relationships
    
    def _infer_relationship_from_context(
        self, source: Entity, target: Entity, context: str
    ) -> Tuple[Optional[RelationType], float]:
        """Infer relationship type from entity types and context.
        
        Args:
            source: Source entity
            target: Target entity
            context: Text context between entities
            
        Returns:
            Tuple of (relationship type, confidence)
        """
        # Check common entity type pairings
        source_type = source.type
        target_type = target.type
        
        # Default values
        rel_type = None
        confidence = 0.5
        
        # MODEL + DATASET
        if source_type == EntityType.MODEL and target_type == EntityType.DATASET:
            # Check for training context
            if re.search(r'train|fine-tun|pretrain', context, re.IGNORECASE):
                rel_type = RelationType.TRAINED_ON
                confidence = 0.7
            # Check for evaluation context
            elif re.search(r'evaluat|test|validat|benchmark', context, re.IGNORECASE):
                rel_type = RelationType.EVALUATED_ON
                confidence = 0.7
        
        # MODEL + MODEL
        elif source_type == EntityType.MODEL and target_type == EntityType.MODEL:
            # Check for comparison context
            if re.search(r'outperform|better|improv|exceed|surpass', context, re.IGNORECASE):
                rel_type = RelationType.OUTPERFORMS
                confidence = 0.7
            # Check for architecture lineage
            elif re.search(r'based on|derived from|exten|modif|inspir|build upon', context, re.IGNORECASE):
                rel_type = RelationType.BASED_ON
                confidence = 0.7
        
        # MODEL + METRIC
        elif source_type == EntityType.MODEL and target_type == EntityType.METRIC:
            # Check for performance reporting
            if re.search(r'achiev|report|reach|score|obtain|show', context, re.IGNORECASE):
                rel_type = RelationType.ACHIEVES
                confidence = 0.7
                
                # Try to extract the numeric value
                value_match = re.search(r'(\d+\.\d+|\d+)%?', context)
                if value_match:
                    value = value_match.group(1)
                    confidence = 0.8
        
        # ALGORITHM + TASK
        elif source_type == EntityType.ALGORITHM and target_type == EntityType.TASK:
            # Check for application context
            if re.search(r'appli|use|solv|address|tackle', context, re.IGNORECASE):
                rel_type = RelationType.APPLIED_TO
                confidence = 0.7
        
        # MODEL + FRAMEWORK/LIBRARY
        elif source_type == EntityType.MODEL and target_type in [EntityType.FRAMEWORK, EntityType.LIBRARY]:
            # Check for implementation context
            if re.search(r'implement|develop|code|built|written|using', context, re.IGNORECASE):
                rel_type = RelationType.IMPLEMENTED_IN
                confidence = 0.7
        
        return rel_type, confidence
    
    def _find_best_match(self, text: str, entities: List[Entity]) -> Optional[Entity]:
        """Find the entity that best matches the given text.
        
        Args:
            text: Text to match
            entities: List of entities to search
            
        Returns:
            Best matching entity or None
        """
        if not entities:
            return None
        
        # Try exact match first
        for entity in entities:
            if entity.text.lower() == text.lower():
                return entity
        
        # Try partial match
        best_match = None
        highest_ratio = 0.0
        
        for entity in entities:
            # Simple contained check
            if text.lower() in entity.text.lower() or entity.text.lower() in text.lower():
                ratio = len(min(text, entity.text, key=len)) / len(max(text, entity.text, key=len))
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    best_match = entity
        
        # Return match if it's good enough
        if highest_ratio > 0.5:
            return best_match
        
        return None
    
    def _find_matching_metric(self, metric_name: str, metric_entities: List[Entity]) -> Optional[Entity]:
        """Find a metric entity that matches the given metric name.
        
        Args:
            metric_name: Name of the metric
            metric_entities: List of metric entities
            
        Returns:
            Matching metric entity or None
        """
        if not metric_entities:
            return None
        
        metric_name = metric_name.lower()
        
        for entity in metric_entities:
            entity_text = entity.text.lower()
            
            # Check for exact or close matches
            if entity_text == metric_name or \
               entity_text in metric_name or \
               metric_name in entity_text:
                return entity
        
        return None
    
    def _deduplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Remove duplicate relationships, keeping the highest confidence ones.
        
        Args:
            relationships: List of potentially duplicate relationships
            
        Returns:
            Deduplicated list of relationships
        """
        unique_rels = {}
        
        for rel in relationships:
            # Create a key based on source, target, and relation type
            key = (rel.source.id, rel.target.id, rel.relation_type)
            
            # Keep the relationship with the highest confidence
            if key not in unique_rels or rel.confidence > unique_rels[key].confidence:
                unique_rels[key] = rel
        
        return list(unique_rels.values())
    
    def extract_model_performance(self, relationships: Optional[List[Relationship]] = None) -> Dict[str, Any]:
        """Extract and organize model performance information.
        
        This method aggregates performance metrics for models from the relationships.
        
        Args:
            relationships: List of relationships to analyze (defaults to self.relationships)
            
        Returns:
            Dictionary mapping models to their performance metrics
        """
        relationships = relationships or self.relationships
        
        # Filter to only ACHIEVES relationships
        achieves_rels = [
            rel for rel in relationships
            if rel.relation_type == RelationType.ACHIEVES
        ]
        
        # Group by source model
        model_performance = defaultdict(list)
        
        for rel in achieves_rels:
            model_name = rel.source.text
            metric_name = rel.target.text
            metric_value = rel.metadata.get("value", "N/A")
            
            model_performance[model_name].append({
                "metric": metric_name,
                "value": metric_value,
                "confidence": rel.confidence
            })
        
        return dict(model_performance)
    
    def extract_model_hierarchy(self, relationships: Optional[List[Relationship]] = None) -> Dict[str, Any]:
        """Extract model hierarchy and lineage information.
        
        This method builds a graph of model relationships showing which models
        are based on or derived from others.
        
        Args:
            relationships: List of relationships to analyze (defaults to self.relationships)
            
        Returns:
            Dictionary representing the model hierarchy
        """
        relationships = relationships or self.relationships
        
        # Filter to only BASED_ON relationships
        based_on_rels = [
            rel for rel in relationships
            if rel.relation_type == RelationType.BASED_ON
        ]
        
        # Build hierarchy
        model_hierarchy = defaultdict(list)
        
        for rel in based_on_rels:
            source_model = rel.source.text
            base_model = rel.target.text
            
            model_hierarchy[base_model].append({
                "model": source_model,
                "confidence": rel.confidence
            })
        
        return dict(model_hierarchy)