"""
Temporal Evolution Tracker for the Knowledge Graph Integration.

This module provides the TemporalEvolutionTracker class that tracks changes to entities
and relationships in the knowledge graph over time, enabling temporal analysis and
version history tracking.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from datetime import datetime
import uuid
import os
from pathlib import Path
import copy

logger = logging.getLogger(__name__)


class TemporalEvolutionTracker:
    """
    Tracks the evolution of entities and relationships in the knowledge graph over time.
    
    This class maintains version histories for both entities and relationships,
    enabling temporal queries and analysis of how knowledge evolves.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the temporal evolution tracker.
        
        Args:
            config: Configuration dictionary for temporal tracking
        """
        self.config = config or {}
        
        # Configure tracking options
        self.track_entity_changes = self.config.get("track_entity_changes", True)
        self.track_relationship_changes = self.config.get("track_relationship_changes", True)
        self.track_property_changes = self.config.get("track_property_changes", True)
        self.track_confidence_changes = self.config.get("track_confidence_changes", True)
        
        # Configure storage options
        self.use_local_storage = self.config.get("use_local_storage", True)
        self.local_storage_path = self.config.get("local_storage_path", "temporal_evolution")
        
        # Minimum confidence difference to consider a change significant
        self.min_confidence_difference = self.config.get("min_confidence_difference", 0.1)
        
        # Entity and relationship version history
        self.entity_versions: Dict[str, List[Dict[str, Any]]] = {}
        self.relationship_versions: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize local storage if needed
        if self.use_local_storage:
            os.makedirs(self.local_storage_path, exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "entities"), exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "relationships"), exist_ok=True)
            
            # Load existing versions if available
            self._load_version_history()
    
    def track_entity_change(
        self, 
        entity: Dict[str, Any],
        previous_version: Optional[Dict[str, Any]] = None,
        change_source: str = "knowledge_extraction",
        change_type: str = "update"
    ) -> Dict[str, Any]:
        """
        Track a change to an entity, storing the new version in the history.
        
        Args:
            entity: The entity with changes
            previous_version: The previous version of the entity, if known
            change_source: Source of the change (e.g., "knowledge_extraction", "manual")
            change_type: Type of change (e.g., "create", "update", "delete")
            
        Returns:
            Version metadata for the change
        """
        if not self.track_entity_changes:
            return {"tracked": False, "reason": "Entity tracking disabled"}
        
        entity_id = entity.get("id")
        if not entity_id:
            return {"tracked": False, "reason": "Entity missing ID"}
        
        # Find previous version if not provided
        if not previous_version and entity_id in self.entity_versions:
            versions = self.entity_versions[entity_id]
            if versions:
                previous_version = versions[-1]
        
        # If no previous version exists, this is a new entity
        is_new = previous_version is None
        if is_new:
            change_type = "create"
        
        # Create version metadata
        timestamp = datetime.utcnow().isoformat()
        version_id = str(uuid.uuid4())
        
        version_metadata = {
            "version_id": version_id,
            "entity_id": entity_id,
            "timestamp": timestamp,
            "change_type": change_type,
            "change_source": change_source,
            "is_new": is_new,
            "changes": {}
        }
        
        # Make a deep copy of the entity to avoid modifying the original
        entity_copy = copy.deepcopy(entity)
        
        # Add version metadata to the entity
        if "temporal_metadata" not in entity_copy:
            entity_copy["temporal_metadata"] = {}
        
        entity_copy["temporal_metadata"]["version_id"] = version_id
        entity_copy["temporal_metadata"]["version_timestamp"] = timestamp
        entity_copy["temporal_metadata"]["previous_version_id"] = (
            previous_version.get("temporal_metadata", {}).get("version_id") if previous_version else None
        )
        
        # Detect changes if previous version exists
        if previous_version:
            changes = self._detect_entity_changes(entity_copy, previous_version)
            version_metadata["changes"] = changes
            
            # If no significant changes detected, don't track this version
            if not changes:
                return {"tracked": False, "reason": "No significant changes detected"}
        
        # Update the version history
        if entity_id not in self.entity_versions:
            self.entity_versions[entity_id] = []
        
        self.entity_versions[entity_id].append(entity_copy)
        
        # Store to local storage if configured
        if self.use_local_storage:
            self._save_entity_version(entity_id, entity_copy)
        
        return version_metadata
    
    def track_relationship_change(
        self, 
        relationship: Dict[str, Any],
        previous_version: Optional[Dict[str, Any]] = None,
        change_source: str = "knowledge_extraction",
        change_type: str = "update"
    ) -> Dict[str, Any]:
        """
        Track a change to a relationship, storing the new version in the history.
        
        Args:
            relationship: The relationship with changes
            previous_version: The previous version of the relationship, if known
            change_source: Source of the change
            change_type: Type of change
            
        Returns:
            Version metadata for the change
        """
        if not self.track_relationship_changes:
            return {"tracked": False, "reason": "Relationship tracking disabled"}
        
        relationship_id = relationship.get("id")
        if not relationship_id:
            return {"tracked": False, "reason": "Relationship missing ID"}
        
        # Find previous version if not provided
        if not previous_version and relationship_id in self.relationship_versions:
            versions = self.relationship_versions[relationship_id]
            if versions:
                previous_version = versions[-1]
        
        # If no previous version exists, this is a new relationship
        is_new = previous_version is None
        if is_new:
            change_type = "create"
        
        # Create version metadata
        timestamp = datetime.utcnow().isoformat()
        version_id = str(uuid.uuid4())
        
        version_metadata = {
            "version_id": version_id,
            "relationship_id": relationship_id,
            "timestamp": timestamp,
            "change_type": change_type,
            "change_source": change_source,
            "is_new": is_new,
            "changes": {}
        }
        
        # Make a deep copy of the relationship to avoid modifying the original
        relationship_copy = copy.deepcopy(relationship)
        
        # Add version metadata to the relationship
        if "temporal_metadata" not in relationship_copy:
            relationship_copy["temporal_metadata"] = {}
        
        relationship_copy["temporal_metadata"]["version_id"] = version_id
        relationship_copy["temporal_metadata"]["version_timestamp"] = timestamp
        relationship_copy["temporal_metadata"]["previous_version_id"] = (
            previous_version.get("temporal_metadata", {}).get("version_id") if previous_version else None
        )
        
        # Detect changes if previous version exists
        if previous_version:
            changes = self._detect_relationship_changes(relationship_copy, previous_version)
            version_metadata["changes"] = changes
            
            # If no significant changes detected, don't track this version
            if not changes:
                return {"tracked": False, "reason": "No significant changes detected"}
        
        # Update the version history
        if relationship_id not in self.relationship_versions:
            self.relationship_versions[relationship_id] = []
        
        self.relationship_versions[relationship_id].append(relationship_copy)
        
        # Store to local storage if configured
        if self.use_local_storage:
            self._save_relationship_version(relationship_id, relationship_copy)
        
        return version_metadata
    
    def _detect_entity_changes(
        self, 
        new_entity: Dict[str, Any], 
        old_entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect changes between two versions of an entity.
        
        Args:
            new_entity: New version of the entity
            old_entity: Old version of the entity
            
        Returns:
            Dictionary of detected changes
        """
        changes = {}
        
        # Compare labels
        new_labels = set(new_entity.get("labels", []))
        old_labels = set(old_entity.get("labels", []))
        
        if new_labels != old_labels:
            changes["labels"] = {
                "added": list(new_labels - old_labels),
                "removed": list(old_labels - new_labels)
            }
        
        # Compare properties
        new_props = new_entity.get("properties", {})
        old_props = old_entity.get("properties", {})
        
        # Skip temporal_metadata and certain other properties
        skip_properties = {"temporal_metadata", "version_id", "version_timestamp", "previous_version_id"}
        
        property_changes = {}
        
        # Check for added, removed, or modified properties
        for prop in set(new_props.keys()) | set(old_props.keys()):
            if prop in skip_properties:
                continue
                
            # Property exists in both versions
            if prop in new_props and prop in old_props:
                new_value = new_props[prop]
                old_value = old_props[prop]
                
                # Skip if values are identical
                if new_value == old_value:
                    continue
                    
                # Special handling for confidence changes
                if prop == "confidence" and not self.track_confidence_changes:
                    continue
                    
                if prop == "confidence" and abs(new_value - old_value) < self.min_confidence_difference:
                    continue
                
                property_changes[prop] = {
                    "old_value": old_value,
                    "new_value": new_value
                }
            
            # Property added in new version
            elif prop in new_props:
                property_changes[prop] = {
                    "old_value": None,
                    "new_value": new_props[prop],
                    "status": "added"
                }
            
            # Property removed in new version
            else:  # prop in old_props
                property_changes[prop] = {
                    "old_value": old_props[prop],
                    "new_value": None,
                    "status": "removed"
                }
        
        if property_changes:
            changes["properties"] = property_changes
        
        return changes
    
    def _detect_relationship_changes(
        self, 
        new_relationship: Dict[str, Any], 
        old_relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect changes between two versions of a relationship.
        
        Args:
            new_relationship: New version of the relationship
            old_relationship: Old version of the relationship
            
        Returns:
            Dictionary of detected changes
        """
        changes = {}
        
        # Compare relationship type
        if new_relationship.get("type") != old_relationship.get("type"):
            changes["type"] = {
                "old_value": old_relationship.get("type"),
                "new_value": new_relationship.get("type")
            }
        
        # Compare source and target
        if new_relationship.get("source_id") != old_relationship.get("source_id"):
            changes["source_id"] = {
                "old_value": old_relationship.get("source_id"),
                "new_value": new_relationship.get("source_id")
            }
        
        if new_relationship.get("target_id") != old_relationship.get("target_id"):
            changes["target_id"] = {
                "old_value": old_relationship.get("target_id"),
                "new_value": new_relationship.get("target_id")
            }
        
        # Compare properties (similar to entity property comparison)
        new_props = new_relationship.get("properties", {})
        old_props = old_relationship.get("properties", {})
        
        # Skip temporal_metadata and certain other properties
        skip_properties = {"temporal_metadata", "version_id", "version_timestamp", "previous_version_id"}
        
        property_changes = {}
        
        # Check for added, removed, or modified properties
        for prop in set(new_props.keys()) | set(old_props.keys()):
            if prop in skip_properties:
                continue
                
            # Property exists in both versions
            if prop in new_props and prop in old_props:
                new_value = new_props[prop]
                old_value = old_props[prop]
                
                # Skip if values are identical
                if new_value == old_value:
                    continue
                    
                # Special handling for confidence changes
                if prop == "confidence" and not self.track_confidence_changes:
                    continue
                    
                if prop == "confidence" and abs(new_value - old_value) < self.min_confidence_difference:
                    continue
                
                property_changes[prop] = {
                    "old_value": old_value,
                    "new_value": new_value
                }
            
            # Property added in new version
            elif prop in new_props:
                property_changes[prop] = {
                    "old_value": None,
                    "new_value": new_props[prop],
                    "status": "added"
                }
            
            # Property removed in new version
            else:  # prop in old_props
                property_changes[prop] = {
                    "old_value": old_props[prop],
                    "new_value": None,
                    "status": "removed"
                }
        
        if property_changes:
            changes["properties"] = property_changes
        
        return changes
    
    def get_entity_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get the version history for a specific entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            List of entity versions in chronological order
        """
        if entity_id in self.entity_versions:
            return self.entity_versions[entity_id]
        
        if self.use_local_storage:
            # Try to load from local storage
            versions = self._load_entity_versions(entity_id)
            if versions:
                self.entity_versions[entity_id] = versions
                return versions
            
        return []
    
    def get_relationship_history(self, relationship_id: str) -> List[Dict[str, Any]]:
        """
        Get the version history for a specific relationship.
        
        Args:
            relationship_id: ID of the relationship
            
        Returns:
            List of relationship versions in chronological order
        """
        if relationship_id in self.relationship_versions:
            return self.relationship_versions[relationship_id]
        
        if self.use_local_storage:
            # Try to load from local storage
            versions = self._load_relationship_versions(relationship_id)
            if versions:
                self.relationship_versions[relationship_id] = versions
                return versions
            
        return []
    
    def get_entity_state_at_time(
        self, 
        entity_id: str, 
        timestamp: Union[str, datetime]
    ) -> Optional[Dict[str, Any]]:
        """
        Get the state of an entity at a specific point in time.
        
        Args:
            entity_id: ID of the entity
            timestamp: Timestamp to query (datetime object or ISO string)
            
        Returns:
            Entity state at the specified time, or None if not found
        """
        # Convert timestamp to string if needed
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.isoformat()
        else:
            timestamp_str = timestamp
        
        # Get the entity history
        versions = self.get_entity_history(entity_id)
        if not versions:
            return None
        
        # Find the version that was active at the specified time
        active_version = None
        for version in versions:
            version_timestamp = version.get("temporal_metadata", {}).get("version_timestamp")
            if version_timestamp and version_timestamp <= timestamp_str:
                active_version = version
            else:
                break
        
        return active_version
    
    def get_relationship_state_at_time(
        self, 
        relationship_id: str, 
        timestamp: Union[str, datetime]
    ) -> Optional[Dict[str, Any]]:
        """
        Get the state of a relationship at a specific point in time.
        
        Args:
            relationship_id: ID of the relationship
            timestamp: Timestamp to query (datetime object or ISO string)
            
        Returns:
            Relationship state at the specified time, or None if not found
        """
        # Convert timestamp to string if needed
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.isoformat()
        else:
            timestamp_str = timestamp
        
        # Get the relationship history
        versions = self.get_relationship_history(relationship_id)
        if not versions:
            return None
        
        # Find the version that was active at the specified time
        active_version = None
        for version in versions:
            version_timestamp = version.get("temporal_metadata", {}).get("version_timestamp")
            if version_timestamp and version_timestamp <= timestamp_str:
                active_version = version
            else:
                break
        
        return active_version
    
    def get_knowledge_graph_state_at_time(
        self, 
        timestamp: Union[str, datetime],
        entity_ids: Optional[List[str]] = None,
        relationship_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get the state of the entire knowledge graph (or a subset) at a specific point in time.
        
        Args:
            timestamp: Timestamp to query (datetime object or ISO string)
            entity_ids: Optional list of entity IDs to include (if None, include all)
            relationship_ids: Optional list of relationship IDs to include (if None, include all)
            
        Returns:
            Dictionary with entities and relationships at the specified time
        """
        # Convert timestamp to string if needed
        if isinstance(timestamp, datetime):
            timestamp_str = timestamp.isoformat()
        else:
            timestamp_str = timestamp
        
        result = {
            "entities": [],
            "relationships": [],
            "timestamp": timestamp_str
        }
        
        # Get entities at the specified time
        if entity_ids is not None:
            for entity_id in entity_ids:
                entity = self.get_entity_state_at_time(entity_id, timestamp_str)
                if entity:
                    result["entities"].append(entity)
        else:
            # Get all entities (this could be expensive for large graphs)
            all_entity_ids = set(self.entity_versions.keys())
            for entity_id in all_entity_ids:
                entity = self.get_entity_state_at_time(entity_id, timestamp_str)
                if entity:
                    result["entities"].append(entity)
        
        # Get relationships at the specified time
        if relationship_ids is not None:
            for relationship_id in relationship_ids:
                relationship = self.get_relationship_state_at_time(relationship_id, timestamp_str)
                if relationship:
                    result["relationships"].append(relationship)
        else:
            # Get all relationships (this could be expensive for large graphs)
            all_relationship_ids = set(self.relationship_versions.keys())
            for relationship_id in all_relationship_ids:
                relationship = self.get_relationship_state_at_time(relationship_id, timestamp_str)
                if relationship:
                    result["relationships"].append(relationship)
        
        return result
    
    def analyze_entity_evolution(self, entity_id: str) -> Dict[str, Any]:
        """
        Analyze how an entity has evolved over time.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Analysis of the entity's evolution
        """
        versions = self.get_entity_history(entity_id)
        if not versions:
            return {
                "entity_id": entity_id,
                "version_count": 0,
                "first_seen": None,
                "last_updated": None,
                "evolution_summary": "Entity not found or no history available"
            }
        
        # Basic statistics
        version_count = len(versions)
        first_version = versions[0]
        last_version = versions[-1]
        
        first_seen = first_version.get("temporal_metadata", {}).get("version_timestamp")
        last_updated = last_version.get("temporal_metadata", {}).get("version_timestamp")
        
        # Track property changes over time
        property_evolution = {}
        label_changes = []
        
        # Analyze each version transition
        for i in range(1, len(versions)):
            prev_version = versions[i-1]
            curr_version = versions[i]
            
            timestamp = curr_version.get("temporal_metadata", {}).get("version_timestamp")
            
            # Check for label changes
            prev_labels = set(prev_version.get("labels", []))
            curr_labels = set(curr_version.get("labels", []))
            
            if prev_labels != curr_labels:
                label_changes.append({
                    "timestamp": timestamp,
                    "added": list(curr_labels - prev_labels),
                    "removed": list(prev_labels - curr_labels)
                })
            
            # Check for property changes
            if "properties" in curr_version:
                for prop, value in curr_version["properties"].items():
                    if prop not in property_evolution:
                        property_evolution[prop] = []
                    
                    # Only add to history if the value changed
                    prev_value = prev_version.get("properties", {}).get(prop)
                    if prev_value != value:
                        property_evolution[prop].append({
                            "timestamp": timestamp,
                            "old_value": prev_value,
                            "new_value": value
                        })
        
        # Get the entity name for the summary
        entity_name = last_version.get("properties", {}).get("name", "Unknown")
        
        # Generate a summary of the evolution
        evolution_summary = (
            f"Entity '{entity_name}' has undergone {version_count} versions "
            f"since {first_seen}. "
        )
        
        if label_changes:
            evolution_summary += f"Its type/labels have changed {len(label_changes)} times. "
        
        most_changed_property = None
        most_changes = 0
        for prop, changes in property_evolution.items():
            if len(changes) > most_changes:
                most_changed_property = prop
                most_changes = len(changes)
        
        if most_changed_property:
            evolution_summary += (
                f"The most frequently changed property is '{most_changed_property}' "
                f"with {most_changes} changes."
            )
        
        return {
            "entity_id": entity_id,
            "entity_name": entity_name,
            "version_count": version_count,
            "first_seen": first_seen,
            "last_updated": last_updated,
            "label_changes": label_changes,
            "property_evolution": property_evolution,
            "evolution_summary": evolution_summary
        }
    
    def analyze_relationship_evolution(self, relationship_id: str) -> Dict[str, Any]:
        """
        Analyze how a relationship has evolved over time.
        
        Args:
            relationship_id: ID of the relationship
            
        Returns:
            Analysis of the relationship's evolution
        """
        versions = self.get_relationship_history(relationship_id)
        if not versions:
            return {
                "relationship_id": relationship_id,
                "version_count": 0,
                "first_seen": None,
                "last_updated": None,
                "evolution_summary": "Relationship not found or no history available"
            }
        
        # Basic statistics
        version_count = len(versions)
        first_version = versions[0]
        last_version = versions[-1]
        
        first_seen = first_version.get("temporal_metadata", {}).get("version_timestamp")
        last_updated = last_version.get("temporal_metadata", {}).get("version_timestamp")
        
        # Track changes over time
        type_changes = []
        property_evolution = {}
        endpoint_changes = []
        
        # Analyze each version transition
        for i in range(1, len(versions)):
            prev_version = versions[i-1]
            curr_version = versions[i]
            
            timestamp = curr_version.get("temporal_metadata", {}).get("version_timestamp")
            
            # Check for relationship type changes
            prev_type = prev_version.get("type")
            curr_type = curr_version.get("type")
            
            if prev_type != curr_type:
                type_changes.append({
                    "timestamp": timestamp,
                    "old_type": prev_type,
                    "new_type": curr_type
                })
            
            # Check for endpoint changes
            prev_source = prev_version.get("source_id")
            curr_source = curr_version.get("source_id")
            prev_target = prev_version.get("target_id")
            curr_target = curr_version.get("target_id")
            
            if prev_source != curr_source or prev_target != curr_target:
                endpoint_changes.append({
                    "timestamp": timestamp,
                    "old_source": prev_source,
                    "new_source": curr_source,
                    "old_target": prev_target,
                    "new_target": curr_target
                })
            
            # Check for property changes
            if "properties" in curr_version:
                for prop, value in curr_version["properties"].items():
                    if prop not in property_evolution:
                        property_evolution[prop] = []
                    
                    # Only add to history if the value changed
                    prev_value = prev_version.get("properties", {}).get(prop)
                    if prev_value != value:
                        property_evolution[prop].append({
                            "timestamp": timestamp,
                            "old_value": prev_value,
                            "new_value": value
                        })
        
        # Generate a summary of the evolution
        current_type = last_version.get("type", "Unknown")
        current_source = last_version.get("source_id", "Unknown")
        current_target = last_version.get("target_id", "Unknown")
        
        evolution_summary = (
            f"Relationship ({current_source}) -[{current_type}]-> ({current_target}) "
            f"has undergone {version_count} versions since {first_seen}. "
        )
        
        if type_changes:
            evolution_summary += f"Its type has changed {len(type_changes)} times. "
        
        if endpoint_changes:
            evolution_summary += f"Its endpoints have changed {len(endpoint_changes)} times. "
        
        most_changed_property = None
        most_changes = 0
        for prop, changes in property_evolution.items():
            if len(changes) > most_changes:
                most_changed_property = prop
                most_changes = len(changes)
        
        if most_changed_property:
            evolution_summary += (
                f"The most frequently changed property is '{most_changed_property}' "
                f"with {most_changes} changes."
            )
        
        return {
            "relationship_id": relationship_id,
            "current_type": current_type,
            "current_source": current_source,
            "current_target": current_target,
            "version_count": version_count,
            "first_seen": first_seen,
            "last_updated": last_updated,
            "type_changes": type_changes,
            "endpoint_changes": endpoint_changes,
            "property_evolution": property_evolution,
            "evolution_summary": evolution_summary
        }
    
    def _save_entity_version(self, entity_id: str, entity: Dict[str, Any]) -> None:
        """
        Save an entity version to local storage.
        
        Args:
            entity_id: ID of the entity
            entity: Entity data to save
        """
        entity_dir = os.path.join(self.local_storage_path, "entities", entity_id)
        os.makedirs(entity_dir, exist_ok=True)
        
        version_id = entity.get("temporal_metadata", {}).get("version_id")
        if not version_id:
            version_id = str(uuid.uuid4())
            
        file_path = os.path.join(entity_dir, f"{version_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entity, f, indent=2)
    
    def _save_relationship_version(self, relationship_id: str, relationship: Dict[str, Any]) -> None:
        """
        Save a relationship version to local storage.
        
        Args:
            relationship_id: ID of the relationship
            relationship: Relationship data to save
        """
        relationship_dir = os.path.join(self.local_storage_path, "relationships", relationship_id)
        os.makedirs(relationship_dir, exist_ok=True)
        
        version_id = relationship.get("temporal_metadata", {}).get("version_id")
        if not version_id:
            version_id = str(uuid.uuid4())
            
        file_path = os.path.join(relationship_dir, f"{version_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(relationship, f, indent=2)
    
    def _load_entity_versions(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Load entity versions from local storage.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            List of entity versions in chronological order
        """
        entity_dir = os.path.join(self.local_storage_path, "entities", entity_id)
        if not os.path.exists(entity_dir):
            return []
        
        versions = []
        
        for file_name in os.listdir(entity_dir):
            if not file_name.endswith(".json"):
                continue
                
            file_path = os.path.join(entity_dir, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    version = json.load(f)
                    versions.append(version)
            except Exception as e:
                logger.error(f"Error loading entity version from {file_path}: {e}")
        
        # Sort versions by timestamp
        versions.sort(key=lambda v: v.get("temporal_metadata", {}).get("version_timestamp", ""))
        
        return versions
    
    def _load_relationship_versions(self, relationship_id: str) -> List[Dict[str, Any]]:
        """
        Load relationship versions from local storage.
        
        Args:
            relationship_id: ID of the relationship
            
        Returns:
            List of relationship versions in chronological order
        """
        relationship_dir = os.path.join(self.local_storage_path, "relationships", relationship_id)
        if not os.path.exists(relationship_dir):
            return []
        
        versions = []
        
        for file_name in os.listdir(relationship_dir):
            if not file_name.endswith(".json"):
                continue
                
            file_path = os.path.join(relationship_dir, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    version = json.load(f)
                    versions.append(version)
            except Exception as e:
                logger.error(f"Error loading relationship version from {file_path}: {e}")
        
        # Sort versions by timestamp
        versions.sort(key=lambda v: v.get("temporal_metadata", {}).get("version_timestamp", ""))
        
        return versions
    
    def _load_version_history(self) -> None:
        """
        Load all entity and relationship version histories from local storage.
        This is called during initialization if use_local_storage is True.
        """
        entities_dir = os.path.join(self.local_storage_path, "entities")
        relationships_dir = os.path.join(self.local_storage_path, "relationships")
        
        # Load entity versions
        if os.path.exists(entities_dir):
            for entity_id in os.listdir(entities_dir):
                entity_dir = os.path.join(entities_dir, entity_id)
                if os.path.isdir(entity_dir):
                    versions = self._load_entity_versions(entity_id)
                    if versions:
                        self.entity_versions[entity_id] = versions
        
        # Load relationship versions
        if os.path.exists(relationships_dir):
            for relationship_id in os.listdir(relationships_dir):
                relationship_dir = os.path.join(relationships_dir, relationship_id)
                if os.path.isdir(relationship_dir):
                    versions = self._load_relationship_versions(relationship_id)
                    if versions:
                        self.relationship_versions[relationship_id] = versions