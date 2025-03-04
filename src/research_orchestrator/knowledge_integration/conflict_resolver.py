"""
Conflict Resolver for integrating Knowledge Extraction with the Knowledge Graph System.

This module provides the ConflictResolver class that detects and resolves conflicts
between existing knowledge graph entries and newly extracted information.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
import json

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Detects and resolves conflicts in knowledge graph integration.
    
    This class identifies potential conflicts between existing knowledge in the
    graph and newly extracted information, applying resolution strategies to
    maintain data consistency and quality.
    """
    
    # Default conflict resolution strategies
    DEFAULT_STRATEGIES = {
        "entity_name": "use_highest_confidence",
        "entity_type": "use_existing",
        "entity_properties": "merge_with_existing",
        "relationship_type": "use_highest_confidence",
        "relationship_properties": "merge_with_existing",
        "contradictory_relationships": "keep_both_with_metadata"
    }
    
    # Known contradictory relationship pairs
    CONTRADICTORY_RELATIONSHIPS = [
        ("OUTPERFORMS", "OUTPERFORMED_BY"),
        ("CONFIRMS", "CONTRADICTS"),
        ("PROVES", "DISPROVES")
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the conflict resolver.
        
        Args:
            config: Configuration dictionary for conflict resolution
        """
        self.config = config or {}
        
        # Use provided strategies or defaults
        self.strategies = self.config.get("strategies", {})
        for key, default_strategy in self.DEFAULT_STRATEGIES.items():
            if key not in self.strategies:
                self.strategies[key] = default_strategy
        
        # Additional configuration
        self.detection_enabled = self.config.get("detection_enabled", True)
        self.resolution_enabled = self.config.get("resolution_enabled", True)
        self.track_conflicts = self.config.get("track_conflicts", True)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.1)
        
        # Storage for detected conflicts
        self.detected_conflicts = []
    
    def detect_entity_conflicts(
        self,
        new_entity: Dict[str, Any],
        existing_entity: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between a new entity and an existing entity.
        
        Args:
            new_entity: New entity in knowledge graph format
            existing_entity: Existing entity in knowledge graph format
            
        Returns:
            List of detected conflicts as dictionaries
        """
        if not self.detection_enabled or existing_entity is None:
            return []
        
        conflicts = []
        
        # Check for name conflicts
        if "name" in existing_entity.get("properties", {}) and "name" in new_entity.get("properties", {}):
            existing_name = existing_entity["properties"]["name"]
            new_name = new_entity["properties"]["name"]
            
            if existing_name != new_name:
                conflicts.append({
                    "type": "entity_name",
                    "entity_id": existing_entity.get("id"),
                    "existing_value": existing_name,
                    "new_value": new_name,
                    "existing_confidence": existing_entity.get("properties", {}).get("confidence", 1.0),
                    "new_confidence": new_entity.get("properties", {}).get("confidence", 1.0)
                })
        
        # Check for label/type conflicts
        existing_labels = set(existing_entity.get("labels", []))
        new_labels = set(new_entity.get("labels", []))
        
        if existing_labels != new_labels:
            conflicts.append({
                "type": "entity_type",
                "entity_id": existing_entity.get("id"),
                "existing_value": list(existing_labels),
                "new_value": list(new_labels),
                "existing_confidence": existing_entity.get("properties", {}).get("confidence", 1.0),
                "new_confidence": new_entity.get("properties", {}).get("confidence", 1.0)
            })
        
        # Check for property conflicts (excluding name and confidence)
        for prop, new_value in new_entity.get("properties", {}).items():
            if prop not in ["name", "confidence", "id"]:
                existing_value = existing_entity.get("properties", {}).get(prop)
                
                # Only consider it a conflict if the existing property has a value and it's different
                if existing_value is not None and existing_value != new_value:
                    confidence_diff = abs(
                        existing_entity.get("properties", {}).get("confidence", 1.0) - 
                        new_entity.get("properties", {}).get("confidence", 1.0)
                    )
                    
                    # Only report as conflict if confidence difference exceeds threshold
                    if confidence_diff >= self.confidence_threshold:
                        conflicts.append({
                            "type": "entity_property",
                            "entity_id": existing_entity.get("id"),
                            "property": prop,
                            "existing_value": existing_value,
                            "new_value": new_value,
                            "existing_confidence": existing_entity.get("properties", {}).get("confidence", 1.0),
                            "new_confidence": new_entity.get("properties", {}).get("confidence", 1.0)
                        })
        
        # Store conflicts if tracking enabled
        if self.track_conflicts:
            self.detected_conflicts.extend(conflicts)
        
        return conflicts
    
    def detect_relationship_conflicts(
        self,
        new_relationship: Dict[str, Any],
        existing_relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect conflicts between a new relationship and existing relationships.
        
        Args:
            new_relationship: New relationship in knowledge graph format
            existing_relationships: List of existing relationships in knowledge graph format
            
        Returns:
            List of detected conflicts as dictionaries
        """
        if not self.detection_enabled or not existing_relationships:
            return []
        
        conflicts = []
        
        # Extract key information for the new relationship
        new_source_id = new_relationship.get("source_id")
        new_target_id = new_relationship.get("target_id")
        new_type = new_relationship.get("type")
        
        # Check for conflicts against each existing relationship
        for existing_rel in existing_relationships:
            # Same source and target?
            if (existing_rel.get("source_id") == new_source_id and 
                existing_rel.get("target_id") == new_target_id):
                
                # Type conflict?
                if existing_rel.get("type") != new_type:
                    conflicts.append({
                        "type": "relationship_type",
                        "relationship_id": existing_rel.get("id"),
                        "source_id": new_source_id,
                        "target_id": new_target_id,
                        "existing_value": existing_rel.get("type"),
                        "new_value": new_type,
                        "existing_confidence": existing_rel.get("properties", {}).get("confidence", 1.0),
                        "new_confidence": new_relationship.get("properties", {}).get("confidence", 1.0)
                    })
                
                # Property conflicts?
                for prop, new_value in new_relationship.get("properties", {}).items():
                    if prop not in ["confidence", "id"]:
                        existing_value = existing_rel.get("properties", {}).get(prop)
                        
                        # Only consider it a conflict if the existing property has a value and it's different
                        if existing_value is not None and existing_value != new_value:
                            confidence_diff = abs(
                                existing_rel.get("properties", {}).get("confidence", 1.0) - 
                                new_relationship.get("properties", {}).get("confidence", 1.0)
                            )
                            
                            # Only report as conflict if confidence difference exceeds threshold
                            if confidence_diff >= self.confidence_threshold:
                                conflicts.append({
                                    "type": "relationship_property",
                                    "relationship_id": existing_rel.get("id"),
                                    "property": prop,
                                    "existing_value": existing_value,
                                    "new_value": new_value,
                                    "existing_confidence": existing_rel.get("properties", {}).get("confidence", 1.0),
                                    "new_confidence": new_relationship.get("properties", {}).get("confidence", 1.0)
                                })
            
            # Check for contradictory relationships
            # (e.g., A OUTPERFORMS B vs B OUTPERFORMS A)
            elif (existing_rel.get("source_id") == new_target_id and 
                  existing_rel.get("target_id") == new_source_id):
                
                # Check if relationship types form a contradictory pair
                existing_type = existing_rel.get("type")
                for type1, type2 in self.CONTRADICTORY_RELATIONSHIPS:
                    if ((existing_type == type1 and new_type == type2) or
                        (existing_type == type2 and new_type == type1)):
                        conflicts.append({
                            "type": "contradictory_relationships",
                            "existing_relationship_id": existing_rel.get("id"),
                            "new_relationship_id": new_relationship.get("id"),
                            "source_target_pair": (new_source_id, new_target_id),
                            "reverse_pair": (new_target_id, new_source_id),
                            "existing_type": existing_type,
                            "new_type": new_type,
                            "existing_confidence": existing_rel.get("properties", {}).get("confidence", 1.0),
                            "new_confidence": new_relationship.get("properties", {}).get("confidence", 1.0)
                        })
        
        # Store conflicts if tracking enabled
        if self.track_conflicts:
            self.detected_conflicts.extend(conflicts)
        
        return conflicts
    
    def resolve_entity_conflict(
        self, 
        conflict: Dict[str, Any],
        new_entity: Dict[str, Any],
        existing_entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve a conflict between entities.
        
        Args:
            conflict: The detected conflict
            new_entity: New entity in knowledge graph format
            existing_entity: Existing entity in knowledge graph format
            
        Returns:
            Resolved entity in knowledge graph format
        """
        if not self.resolution_enabled:
            return existing_entity
        
        conflict_type = conflict.get("type")
        strategy = self.strategies.get(conflict_type, "use_existing")
        
        # Create a copy of the existing entity to modify
        resolved_entity = {
            "id": existing_entity.get("id"),
            "labels": existing_entity.get("labels", []).copy(),
            "properties": existing_entity.get("properties", {}).copy()
        }
        
        # Apply resolution strategy based on conflict type
        if conflict_type == "entity_name":
            if strategy == "use_highest_confidence":
                if new_entity.get("properties", {}).get("confidence", 0) > existing_entity.get("properties", {}).get("confidence", 0):
                    resolved_entity["properties"]["name"] = new_entity["properties"]["name"]
            elif strategy == "use_newest":
                resolved_entity["properties"]["name"] = new_entity["properties"]["name"]
            # For "use_existing", we do nothing as we're already using the existing entity as base
            
            # Add conflict metadata
            if self.track_conflicts:
                if "conflict_metadata" not in resolved_entity["properties"]:
                    resolved_entity["properties"]["conflict_metadata"] = {}
                resolved_entity["properties"]["conflict_metadata"]["name_conflict"] = {
                    "alternative_name": new_entity["properties"]["name"],
                    "confidence": new_entity.get("properties", {}).get("confidence", 0)
                }
        
        elif conflict_type == "entity_type":
            if strategy == "use_highest_confidence":
                if new_entity.get("properties", {}).get("confidence", 0) > existing_entity.get("properties", {}).get("confidence", 0):
                    resolved_entity["labels"] = new_entity["labels"]
            elif strategy == "use_newest":
                resolved_entity["labels"] = new_entity["labels"]
            elif strategy == "merge_labels":
                # Combine labels from both entities
                resolved_entity["labels"] = list(set(existing_entity.get("labels", []) + new_entity.get("labels", [])))
            
            # Add conflict metadata
            if self.track_conflicts:
                if "conflict_metadata" not in resolved_entity["properties"]:
                    resolved_entity["properties"]["conflict_metadata"] = {}
                resolved_entity["properties"]["conflict_metadata"]["type_conflict"] = {
                    "alternative_types": new_entity.get("labels", []),
                    "confidence": new_entity.get("properties", {}).get("confidence", 0)
                }
        
        elif conflict_type == "entity_property":
            property_name = conflict.get("property")
            if property_name:
                if strategy == "use_highest_confidence":
                    if new_entity.get("properties", {}).get("confidence", 0) > existing_entity.get("properties", {}).get("confidence", 0):
                        resolved_entity["properties"][property_name] = new_entity["properties"].get(property_name)
                elif strategy == "use_newest":
                    resolved_entity["properties"][property_name] = new_entity["properties"].get(property_name)
                elif strategy == "merge_with_existing":
                    # If both are dictionaries, merge them
                    existing_value = existing_entity["properties"].get(property_name)
                    new_value = new_entity["properties"].get(property_name)
                    if isinstance(existing_value, dict) and isinstance(new_value, dict):
                        merged = existing_value.copy()
                        merged.update(new_value)
                        resolved_entity["properties"][property_name] = merged
                    elif isinstance(existing_value, list) and isinstance(new_value, list):
                        # For lists, combine and deduplicate
                        resolved_entity["properties"][property_name] = list(set(existing_value + new_value))
                
                # Add conflict metadata
                if self.track_conflicts:
                    if "conflict_metadata" not in resolved_entity["properties"]:
                        resolved_entity["properties"]["conflict_metadata"] = {}
                    if "property_conflicts" not in resolved_entity["properties"]["conflict_metadata"]:
                        resolved_entity["properties"]["conflict_metadata"]["property_conflicts"] = {}
                    resolved_entity["properties"]["conflict_metadata"]["property_conflicts"][property_name] = {
                        "alternative_value": new_entity["properties"].get(property_name),
                        "confidence": new_entity.get("properties", {}).get("confidence", 0)
                    }
        
        return resolved_entity
    
    def resolve_relationship_conflict(
        self, 
        conflict: Dict[str, Any],
        new_relationship: Dict[str, Any],
        existing_relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve a conflict between relationships.
        
        Args:
            conflict: The detected conflict
            new_relationship: New relationship in knowledge graph format
            existing_relationship: Existing relationship in knowledge graph format
            
        Returns:
            Resolved relationship in knowledge graph format
        """
        if not self.resolution_enabled:
            return existing_relationship
        
        conflict_type = conflict.get("type")
        strategy = self.strategies.get(conflict_type, "use_existing")
        
        # Create a copy of the existing relationship to modify
        resolved_relationship = {
            "id": existing_relationship.get("id"),
            "type": existing_relationship.get("type"),
            "source_id": existing_relationship.get("source_id"),
            "target_id": existing_relationship.get("target_id"),
            "properties": existing_relationship.get("properties", {}).copy()
        }
        
        # Apply resolution strategy based on conflict type
        if conflict_type == "relationship_type":
            if strategy == "use_highest_confidence":
                if new_relationship.get("properties", {}).get("confidence", 0) > existing_relationship.get("properties", {}).get("confidence", 0):
                    resolved_relationship["type"] = new_relationship["type"]
            elif strategy == "use_newest":
                resolved_relationship["type"] = new_relationship["type"]
            # For "use_existing", we do nothing as we're already using the existing relationship as base
            
            # Add conflict metadata
            if self.track_conflicts:
                if "conflict_metadata" not in resolved_relationship["properties"]:
                    resolved_relationship["properties"]["conflict_metadata"] = {}
                resolved_relationship["properties"]["conflict_metadata"]["type_conflict"] = {
                    "alternative_type": new_relationship["type"],
                    "confidence": new_relationship.get("properties", {}).get("confidence", 0)
                }
        
        elif conflict_type == "relationship_property":
            property_name = conflict.get("property")
            if property_name:
                if strategy == "use_highest_confidence":
                    if new_relationship.get("properties", {}).get("confidence", 0) > existing_relationship.get("properties", {}).get("confidence", 0):
                        resolved_relationship["properties"][property_name] = new_relationship["properties"].get(property_name)
                elif strategy == "use_newest":
                    resolved_relationship["properties"][property_name] = new_relationship["properties"].get(property_name)
                elif strategy == "merge_with_existing":
                    # If both are dictionaries, merge them
                    existing_value = existing_relationship["properties"].get(property_name)
                    new_value = new_relationship["properties"].get(property_name)
                    if isinstance(existing_value, dict) and isinstance(new_value, dict):
                        merged = existing_value.copy()
                        merged.update(new_value)
                        resolved_relationship["properties"][property_name] = merged
                    elif isinstance(existing_value, list) and isinstance(new_value, list):
                        # For lists, combine and deduplicate
                        resolved_relationship["properties"][property_name] = list(set(existing_value + new_value))
                
                # Add conflict metadata
                if self.track_conflicts:
                    if "conflict_metadata" not in resolved_relationship["properties"]:
                        resolved_relationship["properties"]["conflict_metadata"] = {}
                    if "property_conflicts" not in resolved_relationship["properties"]["conflict_metadata"]:
                        resolved_relationship["properties"]["conflict_metadata"]["property_conflicts"] = {}
                    resolved_relationship["properties"]["conflict_metadata"]["property_conflicts"][property_name] = {
                        "alternative_value": new_relationship["properties"].get(property_name),
                        "confidence": new_relationship.get("properties", {}).get("confidence", 0)
                    }
        
        # Contradictory relationships are handled separately since they involve two different relationships
        
        return resolved_relationship
    
    def handle_contradictory_relationships(
        self, 
        conflict: Dict[str, Any],
        new_relationship: Dict[str, Any],
        existing_relationship: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Handle contradictory relationships.
        
        Args:
            conflict: The detected conflict
            new_relationship: New relationship in knowledge graph format
            existing_relationship: Existing relationship in knowledge graph format
            
        Returns:
            List of relationships to keep (may include both, one, or neither)
        """
        if not self.resolution_enabled:
            return [existing_relationship]
        
        strategy = self.strategies.get("contradictory_relationships", "keep_both_with_metadata")
        
        if strategy == "use_highest_confidence":
            # Keep only the relationship with higher confidence
            if new_relationship.get("properties", {}).get("confidence", 0) > existing_relationship.get("properties", {}).get("confidence", 0):
                return [new_relationship]
            else:
                return [existing_relationship]
        
        elif strategy == "keep_both_with_metadata":
            # Keep both, but add contradiction metadata to each
            
            # Create copies to modify
            modified_existing = {
                "id": existing_relationship.get("id"),
                "type": existing_relationship.get("type"),
                "source_id": existing_relationship.get("source_id"),
                "target_id": existing_relationship.get("target_id"),
                "properties": existing_relationship.get("properties", {}).copy()
            }
            
            modified_new = {
                "id": new_relationship.get("id"),
                "type": new_relationship.get("type"),
                "source_id": new_relationship.get("source_id"),
                "target_id": new_relationship.get("target_id"),
                "properties": new_relationship.get("properties", {}).copy()
            }
            
            # Add conflict metadata
            if self.track_conflicts:
                # Add metadata to existing relationship
                if "conflict_metadata" not in modified_existing["properties"]:
                    modified_existing["properties"]["conflict_metadata"] = {}
                modified_existing["properties"]["conflict_metadata"]["contradicted_by"] = {
                    "relationship_id": new_relationship.get("id"),
                    "relationship_type": new_relationship.get("type"),
                    "confidence": new_relationship.get("properties", {}).get("confidence", 0)
                }
                
                # Add metadata to new relationship
                if "conflict_metadata" not in modified_new["properties"]:
                    modified_new["properties"]["conflict_metadata"] = {}
                modified_new["properties"]["conflict_metadata"]["contradicts"] = {
                    "relationship_id": existing_relationship.get("id"),
                    "relationship_type": existing_relationship.get("type"),
                    "confidence": existing_relationship.get("properties", {}).get("confidence", 0)
                }
            
            return [modified_existing, modified_new]
        
        elif strategy == "create_contradiction_node":
            # In a more advanced implementation, we would create a special "Contradiction" node
            # that links to both conflicting relationships and provides context
            # This is a placeholder for that strategy
            
            # For now, just return both relationships
            return [existing_relationship, new_relationship]
        
        else:  # Default to just keeping existing
            return [existing_relationship]
    
    def get_detected_conflicts(self) -> List[Dict[str, Any]]:
        """Get all detected conflicts.
        
        Returns:
            List of all conflicts detected during resolution
        """
        return self.detected_conflicts
    
    def clear_detected_conflicts(self) -> None:
        """Clear the list of detected conflicts."""
        self.detected_conflicts = []