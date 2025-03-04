"""
Contradiction Resolution System for handling conflicting information in the knowledge graph.
"""
from typing import Dict, List, Optional, Set, Tuple, Any
import logging
from pathlib import Path
import json
from datetime import datetime
from enum import Enum

class ConflictType(Enum):
    """Enum for different types of knowledge conflicts"""
    BINARY_CONTRADICTION = "binary_contradiction"  # A or not A
    NUMERIC_DISCREPANCY = "numeric_discrepancy"    # Value differences beyond tolerance
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"  # Impossible timeline
    CATEGORICAL_MISMATCH = "categorical_mismatch"  # Different categorical assignments
    SOURCE_DISAGREEMENT = "source_disagreement"  # Different sources claim different things
    DEFINITIONAL_CONFLICT = "definitional_conflict"  # Different definitions for same concept

class ConflictResolutionStrategy(Enum):
    """Enum for different conflict resolution strategies"""
    NEWEST_SOURCE = "newest_source"  # Prefer the newest source
    HIGHEST_CITATION = "highest_citation"  # Prefer the most cited source
    MAJORITY_VOTE = "majority_vote"  # Go with what most sources claim
    WEIGHTED_AVERAGE = "weighted_average"  # For numeric values, weighted by source reliability
    KEEP_ALL_MARK_CONFLICT = "keep_all_mark_conflict"  # Keep all, but mark as conflicting
    HUMAN_REVIEW = "human_review"  # Flag for human review
    CONTEXT_DEPENDENT = "context_dependent"  # Different contexts, not actually conflicting

class ContradictionResolutionSystem:
    """
    Detects and resolves contradictions in the knowledge graph.
    
    This class provides functionality for identifying contradictory information
    in the knowledge graph, analyzing the nature of contradictions, and applying
    resolution strategies to maintain knowledge integrity.
    """
    
    def __init__(self, graph_manager, config_path: Optional[Path] = None):
        """
        Initialize the ContradictionResolutionSystem with a graph manager and optional configuration.
        
        Args:
            graph_manager: The knowledge graph manager instance
            config_path: Optional path to a configuration file
        """
        self.graph_manager = graph_manager
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.config = {
            'numeric_tolerance': 0.05,         # Tolerance for numeric value differences (proportion)
            'temporal_tolerance_days': 30,      # Tolerance for date differences (in days)
            'min_confidence_threshold': 0.7,    # Minimum confidence to consider for resolution
            'max_conflicts_per_batch': 100,     # Maximum conflicts to process in one batch
            'enable_auto_resolution': True,     # Whether to automatically resolve conflicts
            'default_resolution_strategy': ConflictResolutionStrategy.KEEP_ALL_MARK_CONFLICT.value,
            'source_trust_scores': {},          # Trust scores for different sources (0-1)
            'source_recency_weight': 0.6,       # Weight given to recency in source evaluation
            'source_citation_weight': 0.4       # Weight given to citation count in source evaluation
        }
        
        # Load custom configuration if provided
        if config_path:
            self._load_config(config_path)
            
        # Initialize detection strategies
        self.detection_strategies = {
            'attribute_value_conflict': self._detect_attribute_conflicts,
            'relationship_conflict': self._detect_relationship_conflicts,
            'definitional_conflict': self._detect_definitional_conflicts,
            'temporal_inconsistency': self._detect_temporal_inconsistencies
        }
        
        # Initialize resolution strategies
        self.resolution_strategies = {
            ConflictResolutionStrategy.NEWEST_SOURCE.value: self._resolve_by_newest_source,
            ConflictResolutionStrategy.HIGHEST_CITATION.value: self._resolve_by_highest_citation,
            ConflictResolutionStrategy.MAJORITY_VOTE.value: self._resolve_by_majority_vote,
            ConflictResolutionStrategy.WEIGHTED_AVERAGE.value: self._resolve_by_weighted_average,
            ConflictResolutionStrategy.KEEP_ALL_MARK_CONFLICT.value: self._resolve_by_marking_conflict,
            ConflictResolutionStrategy.HUMAN_REVIEW.value: self._flag_for_human_review,
            ConflictResolutionStrategy.CONTEXT_DEPENDENT.value: self._resolve_context_dependent
        }
        
        # Track conflict history
        self.conflict_history = []
    
    def _load_config(self, config_path: Path) -> None:
        """
        Load custom configuration for contradiction detection and resolution.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Update configuration with provided values
            for key, value in config.items():
                if key in self.config:
                    self.config[key] = value
                    
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Error loading configuration: {e}")
    
    def detect_contradictions(
        self, 
        entity_ids: Optional[List[str]] = None, 
        entity_types: Optional[List[str]] = None,
        strategies: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect contradictions in the knowledge graph.
        
        Args:
            entity_ids: Optional list of entity IDs to focus on
            entity_types: Optional list of entity types to focus on
            strategies: Optional list of detection strategies to use
            
        Returns:
            List of detected contradictions with metadata
        """
        # Determine which strategies to use
        if strategies is None:
            strategies = list(self.detection_strategies.keys())
        
        # Validate strategies
        valid_strategies = [s for s in strategies if s in self.detection_strategies]
        
        # Get entities to analyze
        entities = self._get_entities_for_analysis(entity_ids, entity_types)
        
        # Apply each selected strategy and collect results
        contradictions = []
        for strategy in valid_strategies:
            strategy_func = self.detection_strategies[strategy]
            strategy_contradictions = strategy_func(entities)
            
            for contradiction in strategy_contradictions:
                contradiction['detection_method'] = strategy
                contradictions.append(contradiction)
        
        # Sort by severity and limit results
        contradictions.sort(key=lambda x: x.get('severity', 0), reverse=True)
        
        # Add to conflict history
        self.conflict_history.extend(contradictions)
        
        return contradictions[:self.config['max_conflicts_per_batch']]
    
    def _get_entities_for_analysis(
        self, 
        entity_ids: Optional[List[str]], 
        entity_types: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Get entities for contradiction analysis based on filters.
        
        Args:
            entity_ids: Optional list of entity IDs to focus on
            entity_types: Optional list of entity types to focus on
            
        Returns:
            List of entities for analysis
        """
        if entity_ids:
            # Get specific entities by ID
            entities = []
            for entity_id in entity_ids:
                entity = self.graph_manager.get_entity(entity_id)
                if entity:
                    entities.append(entity)
        elif entity_types:
            # Get entities by type
            entities = []
            for entity_type in entity_types:
                type_entities = self.graph_manager.get_entities_by_type(entity_type)
                entities.extend(type_entities)
        else:
            # Get a sample of entities if no specific filter
            entities = self.graph_manager.get_entities(limit=1000)
        
        return entities
    
    def _detect_attribute_conflicts(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect conflicts in entity attribute values.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of attribute value conflicts
        """
        conflicts = []
        
        # Define conflict detection rules by entity and attribute type
        conflict_rules = {
            'AIModel': {
                'numeric': ['accuracy', 'performance', 'parameters'],
                'categorical': ['architecture_type', 'category', 'framework'],
                'binary': ['is_supervised', 'is_deterministic']
            },
            'Paper': {
                'numeric': ['publication_year', 'citation_count'],
                'categorical': ['venue', 'domain', 'publication_type'],
                'binary': ['is_peer_reviewed']
            },
            'Dataset': {
                'numeric': ['size', 'dimensions', 'sample_count'],
                'categorical': ['domain', 'data_type', 'license'],
                'binary': ['is_public', 'has_bias']
            },
            'Researcher': {
                'categorical': ['affiliation', 'position', 'expertise'],
            },
            'Concept': {
                'categorical': ['domain', 'category', 'concept_type'],
            }
        }
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity.get('type')
            if entity_type:
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append(entity)
        
        # For each entity type, check for conflicts using the rules
        for entity_type, type_entities in entities_by_type.items():
            if entity_type in conflict_rules:
                rules = conflict_rules[entity_type]
                
                for attr_type, attributes in rules.items():
                    for attr in attributes:
                        conflicts.extend(self._check_attribute_conflicts(
                            type_entities, attr, attr_type))
        
        return conflicts
    
    def _check_attribute_conflicts(
        self, 
        entities: List[Dict[str, Any]], 
        attribute: str, 
        attr_type: str
    ) -> List[Dict[str, Any]]:
        """
        Check for conflicts in a specific attribute across entities.
        
        Args:
            entities: List of entities to check
            attribute: The attribute to check
            attr_type: Type of attribute (numeric, categorical, binary)
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Filter entities that have this attribute
        entities_with_attr = [e for e in entities if attribute in e]
        
        # Group by entity ID in case multiple versions of the same entity exist
        entities_by_id = {}
        for entity in entities_with_attr:
            entity_id = entity['id']
            if entity_id not in entities_by_id:
                entities_by_id[entity_id] = []
            entities_by_id[entity_id].append(entity)
        
        # Check each entity with multiple versions
        for entity_id, entity_versions in entities_by_id.items():
            if len(entity_versions) > 1:
                # Extract values and sources
                values_with_sources = [(e[attribute], e.get('source', 'unknown')) for e in entity_versions]
                
                # Check for conflicts based on attribute type
                if attr_type == 'numeric':
                    conflict = self._check_numeric_conflict(values_with_sources)
                elif attr_type == 'categorical':
                    conflict = self._check_categorical_conflict(values_with_sources)
                elif attr_type == 'binary':
                    conflict = self._check_binary_conflict(values_with_sources)
                else:
                    conflict = None
                
                if conflict:
                    # Add conflict information
                    conflict_info = {
                        'entity_id': entity_id,
                        'entity_type': entity_versions[0].get('type'),
                        'attribute': attribute,
                        'conflict_type': conflict['type'],
                        'values': values_with_sources,
                        'severity': conflict['severity'],
                        'description': conflict['description']
                    }
                    conflicts.append(conflict_info)
        
        return conflicts
    
    def _check_numeric_conflict(self, values_with_sources: List[Tuple[Any, str]]) -> Optional[Dict[str, Any]]:
        """
        Check for conflicts in numeric attribute values.
        
        Args:
            values_with_sources: List of (value, source) tuples
            
        Returns:
            Conflict information if conflict detected, None otherwise
        """
        # Extract numeric values
        try:
            numeric_values = [float(val) for val, _ in values_with_sources]
        except (ValueError, TypeError):
            # If values can't be converted to float, treat as categorical
            return self._check_categorical_conflict(values_with_sources)
        
        # Calculate range and check if it exceeds tolerance
        min_val = min(numeric_values)
        max_val = max(numeric_values)
        
        if min_val == 0:
            # Avoid division by zero
            relative_diff = float('inf') if max_val > 0 else 0
        else:
            relative_diff = (max_val - min_val) / min_val
        
        if relative_diff > self.config['numeric_tolerance']:
            # Calculate severity based on the degree of discrepancy
            severity = min(1.0, relative_diff / (self.config['numeric_tolerance'] * 10))
            
            return {
                'type': ConflictType.NUMERIC_DISCREPANCY.value,
                'severity': severity,
                'description': f"Numeric values differ by {relative_diff:.2%}, which exceeds the tolerance of {self.config['numeric_tolerance']:.2%}."
            }
        
        return None
    
    def _check_categorical_conflict(self, values_with_sources: List[Tuple[Any, str]]) -> Optional[Dict[str, Any]]:
        """
        Check for conflicts in categorical attribute values.
        
        Args:
            values_with_sources: List of (value, source) tuples
            
        Returns:
            Conflict information if conflict detected, None otherwise
        """
        # Extract unique values
        unique_values = set(str(val).lower() for val, _ in values_with_sources)
        
        # Multiple different values indicate a conflict
        if len(unique_values) > 1:
            # Severity depends on number of distinct categories
            severity = min(1.0, (len(unique_values) - 1) / 3)
            
            return {
                'type': ConflictType.CATEGORICAL_MISMATCH.value,
                'severity': severity,
                'description': f"Categorical values disagree: {', '.join(unique_values)}"
            }
        
        return None
    
    def _check_binary_conflict(self, values_with_sources: List[Tuple[Any, str]]) -> Optional[Dict[str, Any]]:
        """
        Check for conflicts in binary attribute values.
        
        Args:
            values_with_sources: List of (value, source) tuples
            
        Returns:
            Conflict information if conflict detected, None otherwise
        """
        # Extract boolean values (convert to bool if needed)
        bool_values = []
        for val, _ in values_with_sources:
            if isinstance(val, bool):
                bool_values.append(val)
            elif isinstance(val, str):
                # Handle string representations of booleans
                if val.lower() in ('true', 'yes', '1'):
                    bool_values.append(True)
                elif val.lower() in ('false', 'no', '0'):
                    bool_values.append(False)
            elif isinstance(val, (int, float)):
                # Handle numeric representations
                bool_values.append(bool(val))
        
        # Check if we have both True and False
        if True in bool_values and False in bool_values:
            return {
                'type': ConflictType.BINARY_CONTRADICTION.value,
                'severity': 1.0,  # Binary contradictions are always severe
                'description': "Direct contradiction: both True and False values exist for the same attribute."
            }
        
        return None
    
    def _detect_relationship_conflicts(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect conflicts in entity relationships.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of relationship conflicts
        """
        conflicts = []
        
        # Define mutually exclusive relationship types
        exclusive_relationships = {
            'TRAINED_ON': ['EVALUATED_ON'],  # Can't train and evaluate on same dataset
            'OUTPERFORMS': ['UNDERPERFORMS'],  # Can't outperform and underperform same model
            'DERIVED_FROM': ['PREDECESSOR_OF'],  # Can't be derived from and predecessor of
            'SUPPORTS': ['CONTRADICTS'],  # Can't support and contradict
            'INCLUDES': ['MUTUALLY_EXCLUSIVE']  # Can't include and be mutually exclusive
        }
        
        # Expand exclusive relationships to create a symmetric map
        symmetric_exclusions = {}
        for rel, exclusions in exclusive_relationships.items():
            symmetric_exclusions[rel] = exclusions
            for excl in exclusions:
                if excl not in symmetric_exclusions:
                    symmetric_exclusions[excl] = []
                symmetric_exclusions[excl].append(rel)
        
        # Check each entity for conflicting relationships
        for entity in entities:
            entity_id = entity['id']
            
            # Get all relationships for this entity
            relationships = self.graph_manager.get_relationships(entity_id)
            
            # Group relationships by target entity and relationship type
            rel_by_target = {}
            for rel in relationships:
                target_id = rel.get('target_id')
                if not target_id:
                    continue
                    
                if target_id not in rel_by_target:
                    rel_by_target[target_id] = []
                
                rel_by_target[target_id].append(rel)
            
            # Check for exclusive relationship conflicts
            for target_id, target_rels in rel_by_target.items():
                if len(target_rels) > 1:
                    rel_types = [rel['relationship_type'] for rel in target_rels]
                    
                    # Check each relationship type against its exclusions
                    conflict_pairs = []
                    for i, rel_type in enumerate(rel_types):
                        if rel_type in symmetric_exclusions:
                            exclusions = symmetric_exclusions[rel_type]
                            for excl in exclusions:
                                if excl in rel_types:
                                    conflict_pairs.append((rel_type, excl))
                    
                    if conflict_pairs:
                        # Get the conflicting relationships
                        conflict_rels = []
                        for rel in target_rels:
                            rel_type = rel['relationship_type']
                            for type1, type2 in conflict_pairs:
                                if rel_type in (type1, type2):
                                    conflict_rels.append(rel)
                        
                        conflicts.append({
                            'entity_id': entity_id,
                            'entity_type': entity.get('type'),
                            'target_id': target_id,
                            'conflict_type': 'exclusive_relationship',
                            'relationship_pairs': conflict_pairs,
                            'conflicting_relationships': conflict_rels,
                            'severity': 0.8,
                            'description': f"Entity has mutually exclusive relationships: {', '.join([f'{t1}-{t2}' for t1, t2 in conflict_pairs])}"
                        })
        
        return conflicts
    
    def _detect_definitional_conflicts(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect conflicts in concept definitions.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of definitional conflicts
        """
        conflicts = []
        
        # Filter only Concept entities
        concepts = [e for e in entities if e.get('type') == 'Concept']
        
        # Group concepts by name/id to find different versions of the same concept
        concepts_by_name = {}
        for concept in concepts:
            name = concept.get('name', concept['id']).lower()
            if name not in concepts_by_name:
                concepts_by_name[name] = []
            concepts_by_name[name].append(concept)
        
        # Check each concept with multiple definitions
        for name, concept_versions in concepts_by_name.items():
            if len(concept_versions) > 1:
                # Extract definitions and sources
                defs_with_sources = []
                for c in concept_versions:
                    definition = c.get('definition', '')
                    source = c.get('source', 'unknown')
                    if definition:
                        defs_with_sources.append((definition, source))
                
                if len(defs_with_sources) > 1:
                    # Calculate similarity between definitions
                    if self._check_definition_conflict(defs_with_sources):
                        conflicts.append({
                            'entity_type': 'Concept',
                            'name': name,
                            'conflict_type': ConflictType.DEFINITIONAL_CONFLICT.value,
                            'definitions': defs_with_sources,
                            'severity': 0.7,
                            'description': f"Multiple incompatible definitions exist for concept '{name}'"
                        })
        
        return conflicts
    
    def _check_definition_conflict(self, definitions_with_sources: List[Tuple[str, str]]) -> bool:
        """
        Check if multiple definitions are in conflict.
        
        Args:
            definitions_with_sources: List of (definition, source) tuples
            
        Returns:
            True if conflict detected, False otherwise
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP techniques
        # to detect semantic conflicts between definitions
        
        # Extract unique definitions
        unique_defs = set(d.lower() for d, _ in definitions_with_sources)
        
        # Calculate basic word overlap between all definition pairs
        all_similar = True
        
        for i, (def1, _) in enumerate(definitions_with_sources):
            for j, (def2, _) in enumerate(definitions_with_sources):
                if i < j:  # Only compare each pair once
                    # Tokenize into words
                    words1 = set(def1.lower().split())
                    words2 = set(def2.lower().split())
                    
                    # Calculate Jaccard similarity
                    if words1 and words2:  # Avoid empty sets
                        overlap = len(words1.intersection(words2))
                        total = len(words1.union(words2))
                        similarity = overlap / total
                        
                        # If similarity below threshold, consider conflicting
                        if similarity < 0.5:  # Arbitrary threshold
                            all_similar = False
                            break
            
            if not all_similar:
                break
        
        # If not all definitions are similar, we have a conflict
        return not all_similar
    
    def _detect_temporal_inconsistencies(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect temporal inconsistencies in entity relationships.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of temporal inconsistencies
        """
        conflicts = []
        
        # Time-dependent relationship types
        temporal_relationships = {
            'CITES': {'source_later': True},            # Source must be later than target
            'DERIVED_FROM': {'source_later': True},     # Source must be later than target
            'SUCCEEDED_BY': {'source_earlier': True},   # Source must be earlier than target
            'EVOLVED_INTO': {'source_earlier': True},   # Source must be earlier than target
            'REPLACED': {'source_later': True}          # Source must be later than target
        }
        
        # Check each entity for temporal relationships
        for entity in entities:
            entity_id = entity['id']
            entity_date = self._extract_entity_date(entity)
            
            # Skip entities without date information
            if not entity_date:
                continue
                
            # Get all outgoing relationships for this entity
            outgoing = self.graph_manager.get_outgoing_relationships(entity_id)
            
            # Check each relationship for temporal consistency
            for rel in outgoing:
                rel_type = rel.get('relationship_type')
                target_id = rel.get('target_id')
                
                # Skip if not a temporal relationship type
                if rel_type not in temporal_relationships:
                    continue
                    
                # Get target entity
                target = self.graph_manager.get_entity(target_id)
                if not target:
                    continue
                    
                # Extract date from target
                target_date = self._extract_entity_date(target)
                if not target_date:
                    continue
                    
                # Check temporal consistency
                constraints = temporal_relationships[rel_type]
                
                inconsistency = False
                if constraints.get('source_later') and entity_date <= target_date:
                    inconsistency = True
                elif constraints.get('source_earlier') and entity_date >= target_date:
                    inconsistency = True
                
                if inconsistency:
                    conflicts.append({
                        'entity_id': entity_id,
                        'entity_type': entity.get('type'),
                        'entity_date': entity_date,
                        'target_id': target_id,
                        'target_type': target.get('type'),
                        'target_date': target_date,
                        'relationship_type': rel_type,
                        'conflict_type': ConflictType.TEMPORAL_INCONSISTENCY.value,
                        'severity': 0.9,
                        'description': f"Temporal inconsistency in {rel_type} relationship: {entity_date} {'should be after' if constraints.get('source_later') else 'should be before'} {target_date}"
                    })
        
        return conflicts
    
    def _extract_entity_date(self, entity: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract date information from an entity.
        
        Args:
            entity: Entity to extract date from
            
        Returns:
            Datetime object if available, None otherwise
        """
        # Different entity types may have different date fields
        date_fields = {
            'Paper': ['publication_date', 'year', 'date'],
            'AIModel': ['release_date', 'date', 'timestamp'],
            'Dataset': ['release_date', 'date', 'timestamp'],
            'Concept': ['first_introduced', 'date'],
            'Researcher': ['active_since', 'date']
        }
        
        entity_type = entity.get('type', 'unknown')
        fields_to_check = date_fields.get(entity_type, ['date', 'timestamp'])
        
        # Check each possible field
        for field in fields_to_check:
            if field in entity:
                date_value = entity[field]
                
                # Handle different date formats
                if isinstance(date_value, str):
                    try:
                        # Try common date formats
                        formats = [
                            '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y',
                            '%Y-%m-%dT%H:%M:%S', '%Y'
                        ]
                        
                        for fmt in formats:
                            try:
                                return datetime.strptime(date_value, fmt)
                            except ValueError:
                                continue
                                
                    except Exception:
                        continue
                        
                elif isinstance(date_value, int):
                    # Assume it's a year if 4 digits
                    if 1900 <= date_value <= 2100:
                        return datetime(date_value, 1, 1)
                    # Or a timestamp
                    else:
                        try:
                            return datetime.fromtimestamp(date_value)
                        except Exception:
                            continue
                            
                elif isinstance(date_value, datetime):
                    return date_value
        
        return None
    
    def resolve_contradictions(
        self, 
        contradictions: List[Dict[str, Any]], 
        strategy_override: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Resolve detected contradictions using appropriate strategies.
        
        Args:
            contradictions: List of contradictions to resolve
            strategy_override: Optional strategy to override default
            
        Returns:
            List of resolution results
        """
        if not self.config['enable_auto_resolution']:
            # If auto-resolution disabled, mark all for human review
            return [self._flag_for_human_review(c) for c in contradictions]
        
        # Process each contradiction
        resolutions = []
        for contradiction in contradictions:
            # Determine resolution strategy
            if strategy_override:
                strategy = strategy_override
            else:
                strategy = self._select_resolution_strategy(contradiction)
            
            # Apply the strategy
            if strategy in self.resolution_strategies:
                strategy_func = self.resolution_strategies[strategy]
                resolution = strategy_func(contradiction)
                resolutions.append(resolution)
            else:
                # Fallback to default strategy
                default_strategy = self.config['default_resolution_strategy']
                strategy_func = self.resolution_strategies[default_strategy]
                resolution = strategy_func(contradiction)
                resolutions.append(resolution)
        
        return resolutions
    
    def _select_resolution_strategy(self, contradiction: Dict[str, Any]) -> str:
        """
        Select the most appropriate resolution strategy for a contradiction.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Selected resolution strategy
        """
        conflict_type = contradiction.get('conflict_type')
        
        # Strategy selection based on conflict type
        if conflict_type == ConflictType.NUMERIC_DISCREPANCY.value:
            return ConflictResolutionStrategy.WEIGHTED_AVERAGE.value
            
        elif conflict_type == ConflictType.BINARY_CONTRADICTION.value:
            return ConflictResolutionStrategy.MAJORITY_VOTE.value
            
        elif conflict_type == ConflictType.CATEGORICAL_MISMATCH.value:
            # If high severity, use highest citation or newest source
            if contradiction.get('severity', 0) > 0.7:
                return ConflictResolutionStrategy.HIGHEST_CITATION.value
            else:
                return ConflictResolutionStrategy.MAJORITY_VOTE.value
                
        elif conflict_type == ConflictType.TEMPORAL_INCONSISTENCY.value:
            # Temporal inconsistencies often need human review
            return ConflictResolutionStrategy.HUMAN_REVIEW.value
            
        elif conflict_type == ConflictType.DEFINITIONAL_CONFLICT.value:
            # Consider these potentially context-dependent
            return ConflictResolutionStrategy.CONTEXT_DEPENDENT.value
            
        else:
            # Default strategy
            return self.config['default_resolution_strategy']
    
    def _resolve_by_newest_source(self, contradiction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve contradiction by preferring the newest source.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Resolution result
        """
        # Extract values and sources
        if 'values' in contradiction:
            values_with_sources = contradiction['values']
        elif 'definitions' in contradiction:
            values_with_sources = contradiction['definitions']
        else:
            # Fallback for relationship conflicts
            return self._resolve_by_marking_conflict(contradiction)
        
        # Get source dates
        source_dates = []
        for _, source in values_with_sources:
            source_date = self._get_source_date(source)
            source_dates.append((source, source_date))
        
        # Find newest source
        newest_source = None
        newest_date = None
        
        for source, date in source_dates:
            if date is not None:
                if newest_date is None or date > newest_date:
                    newest_date = date
                    newest_source = source
        
        if newest_source:
            # Find value from newest source
            selected_value = None
            for value, source in values_with_sources:
                if source == newest_source:
                    selected_value = value
                    break
            
            if selected_value is not None:
                resolution = {
                    'contradiction_id': contradiction.get('id', id(contradiction)),
                    'resolution_strategy': ConflictResolutionStrategy.NEWEST_SOURCE.value,
                    'selected_value': selected_value,
                    'selected_source': newest_source,
                    'justification': f"Selected value from newest source ({newest_source}, {newest_date})",
                    'status': 'resolved',
                    'requires_update': True
                }
                return resolution
        
        # Fallback if no dates available
        return self._resolve_by_marking_conflict(contradiction)
    
    def _get_source_date(self, source: str) -> Optional[datetime]:
        """
        Get the date of a source.
        
        Args:
            source: Source identifier
            
        Returns:
            Datetime of the source if available, None otherwise
        """
        # This is a simplified implementation
        # In a real system, this would query a source database
        
        # Try to extract year from source string (e.g., Paper2023)
        import re
        year_match = re.search(r'(19|20)\d{2}', source)
        if year_match:
            year = int(year_match.group(0))
            return datetime(year, 1, 1)
        
        # Try to get source entity from graph
        source_entity = self.graph_manager.get_entity(source)
        if source_entity:
            return self._extract_entity_date(source_entity)
        
        return None
    
    def _resolve_by_highest_citation(self, contradiction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve contradiction by preferring the most cited source.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Resolution result
        """
        # Extract values and sources
        if 'values' in contradiction:
            values_with_sources = contradiction['values']
        elif 'definitions' in contradiction:
            values_with_sources = contradiction['definitions']
        else:
            # Fallback for relationship conflicts
            return self._resolve_by_marking_conflict(contradiction)
        
        # Get citation counts
        source_citations = []
        for _, source in values_with_sources:
            citation_count = self._get_source_citation_count(source)
            source_citations.append((source, citation_count))
        
        # Find most cited source
        most_cited_source = None
        highest_citations = -1
        
        for source, citations in source_citations:
            if citations > highest_citations:
                highest_citations = citations
                most_cited_source = source
        
        if most_cited_source:
            # Find value from most cited source
            selected_value = None
            for value, source in values_with_sources:
                if source == most_cited_source:
                    selected_value = value
                    break
            
            if selected_value is not None:
                resolution = {
                    'contradiction_id': contradiction.get('id', id(contradiction)),
                    'resolution_strategy': ConflictResolutionStrategy.HIGHEST_CITATION.value,
                    'selected_value': selected_value,
                    'selected_source': most_cited_source,
                    'justification': f"Selected value from most cited source ({most_cited_source}, {highest_citations} citations)",
                    'status': 'resolved',
                    'requires_update': True
                }
                return resolution
        
        # Fallback if no citation info available
        return self._resolve_by_marking_conflict(contradiction)
    
    def _get_source_citation_count(self, source: str) -> int:
        """
        Get the citation count of a source.
        
        Args:
            source: Source identifier
            
        Returns:
            Citation count of the source
        """
        # This is a simplified implementation
        # In a real system, this would query a source database or API
        
        # Try to get source entity from graph
        source_entity = self.graph_manager.get_entity(source)
        if source_entity and 'citation_count' in source_entity:
            citation_count = source_entity['citation_count']
            if isinstance(citation_count, (int, float)):
                return int(citation_count)
        
        # Check if we have a trust score for this source
        if source in self.config['source_trust_scores']:
            # Convert trust score (0-1) to a proxy citation count (0-1000)
            trust_score = self.config['source_trust_scores'][source]
            return int(trust_score * 1000)
        
        # Default to 0 if no information available
        return 0
    
    def _resolve_by_majority_vote(self, contradiction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve contradiction by majority vote across sources.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Resolution result
        """
        # Extract values and sources
        if 'values' in contradiction:
            values_with_sources = contradiction['values']
        elif 'definitions' in contradiction:
            values_with_sources = contradiction['definitions']
        else:
            # Fallback for relationship conflicts
            return self._resolve_by_marking_conflict(contradiction)
        
        # Count occurrences of each value
        value_counts = {}
        for value, _ in values_with_sources:
            # Convert to string for comparison
            str_value = str(value).lower()
            value_counts[str_value] = value_counts.get(str_value, 0) + 1
        
        # Find majority value
        majority_value_str = max(value_counts.items(), key=lambda x: x[1])[0]
        
        # Find original value (not lowercased string) and its source
        selected_value = None
        selected_source = None
        for value, source in values_with_sources:
            if str(value).lower() == majority_value_str:
                selected_value = value
                selected_source = source
                break
        
        resolution = {
            'contradiction_id': contradiction.get('id', id(contradiction)),
            'resolution_strategy': ConflictResolutionStrategy.MAJORITY_VOTE.value,
            'selected_value': selected_value,
            'selected_source': selected_source,
            'justification': f"Selected value by majority vote ({value_counts[majority_value_str]} out of {len(values_with_sources)} sources)",
            'status': 'resolved',
            'requires_update': True
        }
        return resolution
    
    def _resolve_by_weighted_average(self, contradiction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve numeric contradiction by weighted average.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Resolution result
        """
        # Only applicable to numeric discrepancies
        if contradiction.get('conflict_type') != ConflictType.NUMERIC_DISCREPANCY.value:
            return self._resolve_by_marking_conflict(contradiction)
        
        # Extract values and sources
        values_with_sources = contradiction.get('values', [])
        
        # Calculate weighted average
        weighted_sum = 0
        total_weight = 0
        
        for value, source in values_with_sources:
            try:
                numeric_value = float(value)
                source_weight = self._calculate_source_weight(source)
                
                weighted_sum += numeric_value * source_weight
                total_weight += source_weight
            except (ValueError, TypeError):
                continue
        
        if total_weight > 0:
            average_value = weighted_sum / total_weight
            
            resolution = {
                'contradiction_id': contradiction.get('id', id(contradiction)),
                'resolution_strategy': ConflictResolutionStrategy.WEIGHTED_AVERAGE.value,
                'selected_value': average_value,
                'selected_source': 'weighted_average',
                'justification': f"Calculated weighted average across {len(values_with_sources)} sources",
                'status': 'resolved',
                'requires_update': True
            }
            return resolution
        
        # Fallback if not possible to calculate average
        return self._resolve_by_marking_conflict(contradiction)
    
    def _calculate_source_weight(self, source: str) -> float:
        """
        Calculate weight for a source based on recency and citations.
        
        Args:
            source: Source identifier
            
        Returns:
            Weight for the source (higher is more reliable)
        """
        # Base weight
        weight = 1.0
        
        # Get source data
        citation_count = self._get_source_citation_count(source)
        source_date = self._get_source_date(source)
        
        # Adjust weight based on citations
        if citation_count > 0:
            citation_factor = min(5, math.log10(citation_count + 1)) / 5
            weight += citation_factor * self.config['source_citation_weight']
        
        # Adjust weight based on recency
        if source_date:
            current_year = datetime.now().year
            years_old = current_year - source_date.year
            
            if years_old <= 2:
                # Very recent sources get a boost
                recency_factor = 1.0
            else:
                # Older sources get less weight
                recency_factor = max(0, 1 - ((years_old - 2) / 10))
                
            weight += recency_factor * self.config['source_recency_weight']
        
        # Apply any explicit trust scores
        if source in self.config['source_trust_scores']:
            trust_score = self.config['source_trust_scores'][source]
            weight *= (1 + trust_score)
        
        return weight
    
    def _resolve_by_marking_conflict(self, contradiction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve by keeping all values but marking the conflict.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Resolution result
        """
        resolution = {
            'contradiction_id': contradiction.get('id', id(contradiction)),
            'resolution_strategy': ConflictResolutionStrategy.KEEP_ALL_MARK_CONFLICT.value,
            'selected_value': None,  # Keep all values
            'justification': "Keeping all values and marking as conflicting for transparency",
            'status': 'marked_as_conflict',
            'requires_update': True,
            'original_contradiction': contradiction
        }
        return resolution
    
    def _flag_for_human_review(self, contradiction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flag contradiction for human review.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Resolution result
        """
        resolution = {
            'contradiction_id': contradiction.get('id', id(contradiction)),
            'resolution_strategy': ConflictResolutionStrategy.HUMAN_REVIEW.value,
            'selected_value': None,  # No automatic selection
            'justification': "Flagged for human review due to complexity or severity",
            'status': 'pending_review',
            'requires_update': False,
            'original_contradiction': contradiction
        }
        return resolution
    
    def _resolve_context_dependent(self, contradiction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve by treating the contradiction as context-dependent.
        
        Args:
            contradiction: The contradiction to resolve
            
        Returns:
            Resolution result
        """
        # Extract values and sources
        if 'values' in contradiction:
            values_with_sources = contradiction['values']
        elif 'definitions' in contradiction:
            values_with_sources = contradiction['definitions']
        else:
            # Fallback for relationship conflicts
            return self._resolve_by_marking_conflict(contradiction)
        
        # For definitional conflicts, try to extract contexts
        contexts = []
        for value, source in values_with_sources:
            context = self._extract_context(value, source)
            contexts.append((value, source, context))
        
        # If we found distinct contexts, mark as context-dependent
        distinct_contexts = set(c for _, _, c in contexts if c)
        
        if len(distinct_contexts) > 1:
            resolution = {
                'contradiction_id': contradiction.get('id', id(contradiction)),
                'resolution_strategy': ConflictResolutionStrategy.CONTEXT_DEPENDENT.value,
                'selected_value': None,  # Keep all with context
                'justification': f"Values are context-dependent across {len(distinct_contexts)} different contexts",
                'status': 'resolved_as_context_dependent',
                'requires_update': True,
                'contexts': [(value, source, context) for value, source, context in contexts if context]
            }
            return resolution
        
        # If no distinct contexts found, fallback to marking conflict
        return self._resolve_by_marking_conflict(contradiction)
    
    def _extract_context(self, value: Any, source: str) -> Optional[str]:
        """
        Extract context information from a value or source.
        
        Args:
            value: The value to analyze
            source: The source of the value
            
        Returns:
            Context string if available, None otherwise
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated NLP techniques
        
        # For string values, look for context indicators
        if isinstance(value, str):
            context_indicators = [
                "in the context of", "when considering", "in terms of",
                "with respect to", "in the field of", "within", "for"
            ]
            
            for indicator in context_indicators:
                if indicator in value.lower():
                    parts = value.lower().split(indicator, 1)
                    if len(parts) > 1:
                        context = parts[1].strip()
                        if context:
                            return context
        
        # Extract domain from source if available
        source_entity = self.graph_manager.get_entity(source)
        if source_entity:
            if 'domain' in source_entity:
                return source_entity['domain']
            elif 'field' in source_entity:
                return source_entity['field']
        
        return None
    
    def apply_resolutions(self, resolutions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply resolved contradictions to the knowledge graph.
        
        Args:
            resolutions: List of contradiction resolutions
            
        Returns:
            List of results from applying resolutions
        """
        results = []
        
        for resolution in resolutions:
            # Skip if no update required
            if not resolution.get('requires_update', False):
                results.append({
                    'resolution_id': resolution.get('contradiction_id'),
                    'status': 'skipped',
                    'message': 'No update required'
                })
                continue
            
            # Get original contradiction
            contradiction = resolution.get('original_contradiction')
            if not contradiction:
                results.append({
                    'resolution_id': resolution.get('contradiction_id'),
                    'status': 'error',
                    'message': 'Missing original contradiction data'
                })
                continue
            
            # Apply based on resolution strategy
            strategy = resolution.get('resolution_strategy')
            
            if strategy == ConflictResolutionStrategy.KEEP_ALL_MARK_CONFLICT.value:
                result = self._apply_mark_conflict(contradiction, resolution)
            elif strategy == ConflictResolutionStrategy.CONTEXT_DEPENDENT.value:
                result = self._apply_context_dependent(contradiction, resolution)
            elif resolution.get('selected_value') is not None:
                result = self._apply_selected_value(contradiction, resolution)
            else:
                result = {
                    'resolution_id': resolution.get('contradiction_id'),
                    'status': 'error',
                    'message': 'Unhandled resolution strategy or missing selected value'
                }
            
            results.append(result)
        
        return results
    
    def _apply_mark_conflict(
        self, 
        contradiction: Dict[str, Any], 
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply resolution by marking conflict without changing values.
        
        Args:
            contradiction: Original contradiction
            resolution: Resolution data
            
        Returns:
            Result of applying the resolution
        """
        # For attribute conflicts
        if 'entity_id' in contradiction and 'attribute' in contradiction:
            entity_id = contradiction['entity_id']
            attribute = contradiction['attribute']
            
            # Mark the attribute as conflicting in the entity
            self.graph_manager.add_entity_metadata(
                entity_id,
                {
                    f"conflict_{attribute}": True,
                    f"conflict_description_{attribute}": contradiction.get('description', 'Conflicting values'),
                    f"conflict_values_{attribute}": contradiction.get('values', [])
                }
            )
            
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'applied',
                'entity_id': entity_id,
                'attribute': attribute,
                'action': 'marked_conflict'
            }
            
        # For relationship conflicts
        elif 'entity_id' in contradiction and 'target_id' in contradiction:
            entity_id = contradiction['entity_id']
            target_id = contradiction['target_id']
            
            # Mark the relationships as conflicting
            for rel in contradiction.get('conflicting_relationships', []):
                rel_id = rel.get('id')
                if rel_id:
                    self.graph_manager.add_relationship_metadata(
                        rel_id,
                        {
                            'conflict': True,
                            'conflict_description': contradiction.get('description', 'Conflicting relationship'),
                            'conflict_pairs': contradiction.get('relationship_pairs', [])
                        }
                    )
            
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'applied',
                'entity_id': entity_id,
                'target_id': target_id,
                'action': 'marked_relationship_conflict'
            }
            
        # For definitional conflicts
        elif 'name' in contradiction and contradiction.get('entity_type') == 'Concept':
            concept_name = contradiction['name']
            
            # Find all concept entities with this name
            concept_entities = self.graph_manager.get_entities_by_property(
                'name', concept_name, entity_type='Concept'
            )
            
            for entity in concept_entities:
                self.graph_manager.add_entity_metadata(
                    entity['id'],
                    {
                        'conflict_definition': True,
                        'conflict_description': contradiction.get('description', 'Conflicting definitions'),
                        'conflict_definitions': contradiction.get('definitions', [])
                    }
                )
            
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'applied',
                'concept_name': concept_name,
                'entities_updated': len(concept_entities),
                'action': 'marked_definition_conflict'
            }
            
        else:
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'error',
                'message': 'Unknown contradiction type for marking conflict'
            }
    
    def _apply_context_dependent(
        self, 
        contradiction: Dict[str, Any], 
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply resolution for context-dependent values.
        
        Args:
            contradiction: Original contradiction
            resolution: Resolution data
            
        Returns:
            Result of applying the resolution
        """
        contexts = resolution.get('contexts', [])
        
        # For definitional conflicts (most common case for context-dependent)
        if 'name' in contradiction and contradiction.get('entity_type') == 'Concept':
            concept_name = contradiction['name']
            
            # Find all concept entities with this name
            concept_entities = self.graph_manager.get_entities_by_property(
                'name', concept_name, entity_type='Concept'
            )
            
            # Update each entity with context information
            for entity in concept_entities:
                entity_id = entity['id']
                
                # Find matching context for this entity
                for value, source, context in contexts:
                    if entity.get('source') == source:
                        self.graph_manager.update_entity(
                            entity_id,
                            {
                                'context': context,
                                'is_context_dependent': True
                            }
                        )
                        break
            
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'applied',
                'concept_name': concept_name,
                'entities_updated': len(concept_entities),
                'action': 'added_context_information'
            }
            
        else:
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'error',
                'message': 'Unknown contradiction type for context-dependent resolution'
            }
    
    def _apply_selected_value(
        self, 
        contradiction: Dict[str, Any], 
        resolution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply resolution by setting the selected value.
        
        Args:
            contradiction: Original contradiction
            resolution: Resolution data
            
        Returns:
            Result of applying the resolution
        """
        selected_value = resolution.get('selected_value')
        selected_source = resolution.get('selected_source')
        
        # For attribute conflicts
        if 'entity_id' in contradiction and 'attribute' in contradiction:
            entity_id = contradiction['entity_id']
            attribute = contradiction['attribute']
            
            # Update the entity with selected value
            update_data = {
                attribute: selected_value,
                f"{attribute}_source": selected_source,
                f"{attribute}_resolution": resolution.get('resolution_strategy')
            }
            
            self.graph_manager.update_entity(entity_id, update_data)
            
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'applied',
                'entity_id': entity_id,
                'attribute': attribute,
                'selected_value': selected_value,
                'action': 'updated_attribute'
            }
            
        # For definitional conflicts
        elif 'name' in contradiction and contradiction.get('entity_type') == 'Concept':
            concept_name = contradiction['name']
            
            # Find the concept entity with matching source
            concept_entities = self.graph_manager.get_entities_by_property(
                'name', concept_name, entity_type='Concept'
            )
            
            updated = False
            for entity in concept_entities:
                if entity.get('source') == selected_source:
                    # Use this entity's definition as the primary
                    self.graph_manager.update_entity(
                        entity['id'],
                        {
                            'is_primary_definition': True,
                            'resolution_strategy': resolution.get('resolution_strategy')
                        }
                    )
                    updated = True
                else:
                    # Mark other entities as non-primary
                    self.graph_manager.update_entity(
                        entity['id'],
                        {
                            'is_primary_definition': False
                        }
                    )
            
            if updated:
                return {
                    'resolution_id': resolution.get('contradiction_id'),
                    'status': 'applied',
                    'concept_name': concept_name,
                    'action': 'selected_primary_definition'
                }
            else:
                return {
                    'resolution_id': resolution.get('contradiction_id'),
                    'status': 'error',
                    'message': 'Could not find matching concept entity for selected source'
                }
                
        else:
            return {
                'resolution_id': resolution.get('contradiction_id'),
                'status': 'error',
                'message': 'Unknown contradiction type for applying selected value'
            }
    
    def get_contradiction_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about contradictions in the knowledge graph.
        
        Returns:
            Dictionary of contradiction statistics
        """
        stats = {}
        
        # Count contradictions by type
        contradiction_types = {}
        for conflict in self.conflict_history:
            conflict_type = conflict.get('conflict_type', 'unknown')
            contradiction_types[conflict_type] = contradiction_types.get(conflict_type, 0) + 1
        
        stats['contradiction_types'] = contradiction_types
        
        # Count by resolution strategy
        resolution_strategies = {}
        for conflict in self.conflict_history:
            if 'resolution' in conflict:
                strategy = conflict['resolution'].get('resolution_strategy', 'unknown')
                resolution_strategies[strategy] = resolution_strategies.get(strategy, 0) + 1
        
        stats['resolution_strategies'] = resolution_strategies
        
        # Count by entity type
        entity_types = {}
        for conflict in self.conflict_history:
            entity_type = conflict.get('entity_type', 'unknown')
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        stats['entity_types'] = entity_types
        
        # Overall statistics
        stats['total_contradictions'] = len(self.conflict_history)
        
        resolved_count = sum(
            1 for c in self.conflict_history 
            if c.get('resolution', {}).get('status') in ('resolved', 'resolved_as_context_dependent')
        )
        
        stats['resolved_contradictions'] = resolved_count
        stats['resolution_rate'] = resolved_count / len(self.conflict_history) if self.conflict_history else 0
        
        return stats