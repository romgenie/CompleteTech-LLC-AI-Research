"""
Temporal models for Knowledge Graph System.

This module provides base data models for temporal entities and relationships
in the Knowledge Graph System.
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
import uuid
from datetime import datetime
import json
import logging

from knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TemporalEntityBase(GraphEntity):
    """
    Base class for temporal entities with versioning support.
    
    Attributes:
        entity_id: Stable identifier across versions (different from id which is version-specific)
        version_id: Unique identifier for this specific version
        version_number: Sequential version number (e.g., 1.0, 2.0)
        version_name: Human-readable version name
        valid_from: When this version became valid
        valid_to: When this version became invalid (null if current)
        predecessor_version_id: Parent version ID
        successor_version_ids: Child version IDs
        branch_name: Branch name for parallel development
        is_current: Whether this is the current version
        creation_source: Source of this version information
        creation_confidence: Confidence in this version information
    """
    
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version_number: float = 1.0
    version_name: Optional[str] = None
    valid_from: datetime = field(default_factory=datetime.now)
    valid_to: Optional[datetime] = None
    predecessor_version_id: Optional[str] = None
    successor_version_ids: List[str] = field(default_factory=list)
    branch_name: str = "main"
    is_current: bool = True
    creation_source: Optional[str] = None
    creation_confidence: float = 1.0
    
    def __post_init__(self):
        """Perform post-initialization validation and setup."""
        # Ensure label includes Temporal marker
        if "TemporalEntity" not in self.labels:
            self.labels.add("TemporalEntity")
        
        # Call parent post-init to ensure all labels are set up properly
        super().__post_init__()
        
        # Update properties with temporal attributes
        self.properties.update({
            "entity_id": self.entity_id,
            "version_id": self.version_id,
            "version_number": self.version_number,
            "valid_from": self.valid_from.isoformat(),
        })
        
        if self.version_name:
            self.properties["version_name"] = self.version_name
            
        if self.valid_to:
            self.properties["valid_to"] = self.valid_to.isoformat()
            
        if self.predecessor_version_id:
            self.properties["predecessor_version_id"] = self.predecessor_version_id
            
        if self.successor_version_ids:
            self.properties["successor_version_ids"] = self.successor_version_ids
            
        self.properties["branch_name"] = self.branch_name
        self.properties["is_current"] = self.is_current
        
        if self.creation_source:
            self.properties["creation_source"] = self.creation_source
            
        self.properties["creation_confidence"] = self.creation_confidence
    
    def has_expired(self) -> bool:
        """
        Check if this entity version has expired.
        
        Returns:
            True if this version has expired, False otherwise
        """
        return self.valid_to is not None and self.valid_to < datetime.now()
    
    def is_successor_of(self, version_id: str) -> bool:
        """
        Check if this entity is a direct successor of another version.
        
        Args:
            version_id: Version ID to check against
            
        Returns:
            True if this entity is a direct successor of the given version, False otherwise
        """
        return self.predecessor_version_id == version_id
    
    def is_predecessor_of(self, version_id: str) -> bool:
        """
        Check if this entity is a direct predecessor of another version.
        
        Args:
            version_id: Version ID to check against
            
        Returns:
            True if this entity is a direct predecessor of the given version, False otherwise
        """
        return version_id in self.successor_version_ids
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the temporal entity to a dictionary.
        
        Returns:
            Dictionary representation of the temporal entity
        """
        data = super().to_dict()
        
        # Convert datetime objects to ISO format strings
        if self.valid_to:
            data['valid_to'] = self.valid_to.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporalEntityBase':
        """
        Create a temporal entity from a dictionary.
        
        Args:
            data: Dictionary containing entity data
            
        Returns:
            TemporalEntityBase instance
        """
        # Convert ISO format strings to datetime objects
        if 'valid_from' in data and isinstance(data['valid_from'], str):
            data['valid_from'] = datetime.fromisoformat(data['valid_from'])
        
        if 'valid_to' in data and isinstance(data['valid_to'], str) and data['valid_to'] is not None:
            data['valid_to'] = datetime.fromisoformat(data['valid_to'])
        
        return super().from_dict(data)
    
    def add_successor(self, version_id: str) -> 'TemporalEntityBase':
        """
        Add a successor version to this entity.
        
        Args:
            version_id: Version ID of the successor
            
        Returns:
            Updated TemporalEntityBase instance
        """
        if version_id not in self.successor_version_ids:
            self.successor_version_ids.append(version_id)
            self.properties["successor_version_ids"] = self.successor_version_ids
            self.updated_at = datetime.now()
            self.is_current = False
            self.properties["is_current"] = False
        
        return self
    
    def mark_as_deprecated(self, end_time: Optional[datetime] = None) -> 'TemporalEntityBase':
        """
        Mark this entity version as deprecated.
        
        Args:
            end_time: When this version became invalid (defaults to now)
            
        Returns:
            Updated TemporalEntityBase instance
        """
        self.valid_to = end_time or datetime.now()
        self.properties["valid_to"] = self.valid_to.isoformat()
        self.is_current = False
        self.properties["is_current"] = False
        self.updated_at = datetime.now()
        
        return self
    
    def get_cypher_create(self) -> tuple[str, Dict[str, Any]]:
        """
        Generate a Cypher query to create this temporal entity.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        params = self.to_cypher_params()
        labels_str = ':'.join(self.labels)
        
        # Build the query
        query = f"""
        CREATE (e:{labels_str} {{
            id: $id,
            entity_id: $entity_id,
            version_id: $version_id,
            version_number: $version_number,
            valid_from: $valid_from,
            branch_name: $branch_name,
            is_current: $is_current,
            created_at: $created_at,
            updated_at: $updated_at,
            confidence: $confidence,
            creation_confidence: $creation_confidence
        """
        
        # Add optional properties
        if self.version_name:
            query += ",\n            version_name: $version_name"
        
        if self.valid_to:
            query += ",\n            valid_to: $valid_to"
        
        if self.predecessor_version_id:
            query += ",\n            predecessor_version_id: $predecessor_version_id"
        
        if self.successor_version_ids:
            query += ",\n            successor_version_ids: $successor_version_ids"
        
        if self.aliases:
            query += ",\n            aliases: $aliases"
        
        if self.source:
            query += ",\n            source: $source"
        
        if self.creation_source:
            query += ",\n            creation_source: $creation_source"
        
        # Add custom properties
        for key in self.properties:
            if key not in {"id", "entity_id", "version_id", "version_number", "valid_from", 
                         "valid_to", "branch_name", "is_current", "created_at", "updated_at", 
                         "confidence", "aliases", "source", "predecessor_version_id", 
                         "successor_version_ids", "creation_confidence", "creation_source", 
                         "version_name"}:
                query += f",\n            {key}: ${key}"
        
        query += "\n        })\n        RETURN e"
        
        return query, params
    
    def to_cypher_params(self) -> Dict[str, Any]:
        """
        Convert the entity to parameters for a Cypher query.
        
        Returns:
            Dictionary of parameters for Cypher query
        """
        # Get base parameters
        params = super().to_cypher_params()
        
        # Add temporal-specific parameters
        params.update({
            'entity_id': self.entity_id,
            'version_id': self.version_id,
            'version_number': self.version_number,
            'valid_from': self.valid_from.isoformat(),
            'branch_name': self.branch_name,
            'is_current': self.is_current,
            'creation_confidence': self.creation_confidence
        })
        
        # Add optional parameters
        if self.version_name:
            params['version_name'] = self.version_name
        
        if self.valid_to:
            params['valid_to'] = self.valid_to.isoformat()
        
        if self.predecessor_version_id:
            params['predecessor_version_id'] = self.predecessor_version_id
        
        if self.successor_version_ids:
            params['successor_version_ids'] = self.successor_version_ids
        
        if self.creation_source:
            params['creation_source'] = self.creation_source
        
        return params


@dataclass
class TemporalRelationshipBase(GraphRelationship):
    """
    Base class for temporal relationships.
    
    Attributes:
        valid_from: When this relationship became valid
        valid_to: When this relationship became invalid (null if current)
        initial_confidence: Confidence when created
        current_confidence: Current confidence score
        decay_rate: Annual confidence decay rate
        creation_source: Source of this relationship information
        verification_status: Verification status
    """
    
    valid_from: datetime = field(default_factory=datetime.now)
    valid_to: Optional[datetime] = None
    initial_confidence: float = 1.0
    current_confidence: float = 1.0
    decay_rate: Optional[float] = None
    creation_source: Optional[str] = None
    verification_status: str = "unverified"
    
    def __post_init__(self):
        """Perform post-initialization validation and setup."""
        # Call parent post-init
        super().__post_init__()
        
        # Update properties with temporal attributes
        self.properties.update({
            "valid_from": self.valid_from.isoformat(),
            "initial_confidence": self.initial_confidence,
            "current_confidence": self.current_confidence,
            "verification_status": self.verification_status
        })
        
        if self.valid_to:
            self.properties["valid_to"] = self.valid_to.isoformat()
            
        if self.decay_rate is not None:
            self.properties["decay_rate"] = self.decay_rate
            
        if self.creation_source:
            self.properties["creation_source"] = self.creation_source
    
    def recalculate_confidence(self) -> float:
        """
        Recalculate confidence based on decay rate and age.
        
        Returns:
            Updated confidence score
        """
        if not self.decay_rate:
            return self.initial_confidence
            
        age_in_years = (datetime.now() - self.valid_from).days / 365.0
        updated_confidence = self.initial_confidence * (1.0 - self.decay_rate * age_in_years)
        
        # Ensure confidence stays within bounds
        self.current_confidence = max(0.01, min(updated_confidence, 1.0))
        
        # Update property
        self.properties["current_confidence"] = self.current_confidence
        
        return self.current_confidence
    
    def is_active(self) -> bool:
        """
        Check if this relationship is currently active.
        
        Returns:
            True if this relationship is currently active, False otherwise
        """
        return self.valid_to is None or self.valid_to > datetime.now()
    
    def mark_as_deprecated(self, end_time: Optional[datetime] = None) -> 'TemporalRelationshipBase':
        """
        Mark this relationship as deprecated.
        
        Args:
            end_time: When this relationship became invalid (defaults to now)
            
        Returns:
            Updated TemporalRelationshipBase instance
        """
        self.valid_to = end_time or datetime.now()
        self.properties["valid_to"] = self.valid_to.isoformat()
        self.updated_at = datetime.now()
        
        return self
    
    def verify(self, verification_status: str = "verified") -> 'TemporalRelationshipBase':
        """
        Mark this relationship as verified.
        
        Args:
            verification_status: New verification status
            
        Returns:
            Updated TemporalRelationshipBase instance
        """
        self.verification_status = verification_status
        self.properties["verification_status"] = verification_status
        self.updated_at = datetime.now()
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the temporal relationship to a dictionary.
        
        Returns:
            Dictionary representation of the temporal relationship
        """
        data = super().to_dict()
        
        # Convert datetime objects to ISO format strings
        if self.valid_to:
            data['valid_to'] = self.valid_to.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporalRelationshipBase':
        """
        Create a temporal relationship from a dictionary.
        
        Args:
            data: Dictionary containing relationship data
            
        Returns:
            TemporalRelationshipBase instance
        """
        # Convert ISO format strings to datetime objects
        if 'valid_from' in data and isinstance(data['valid_from'], str):
            data['valid_from'] = datetime.fromisoformat(data['valid_from'])
        
        if 'valid_to' in data and isinstance(data['valid_to'], str) and data['valid_to'] is not None:
            data['valid_to'] = datetime.fromisoformat(data['valid_to'])
        
        return super().from_dict(data)
    
    def to_cypher_params(self) -> Dict[str, Any]:
        """
        Convert the relationship to parameters for a Cypher query.
        
        Returns:
            Dictionary of parameters for Cypher query
        """
        # Get base parameters
        params = super().to_cypher_params()
        
        # Add temporal-specific parameters
        params.update({
            'valid_from': self.valid_from.isoformat(),
            'initial_confidence': self.initial_confidence,
            'current_confidence': self.current_confidence,
            'verification_status': self.verification_status
        })
        
        # Add optional parameters
        if self.valid_to:
            params['valid_to'] = self.valid_to.isoformat()
        
        if self.decay_rate is not None:
            params['decay_rate'] = self.decay_rate
        
        if self.creation_source:
            params['creation_source'] = self.creation_source
        
        return params
    
    def get_cypher_create(self) -> tuple[str, Dict[str, Any]]:
        """
        Generate a Cypher query to create this temporal relationship.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        params = self.to_cypher_params()
        
        # Build the query
        query = f"""
        MATCH (source), (target)
        WHERE source.id = $source_id AND target.id = $target_id
        CREATE (source)-[r:{self.type} {{
            id: $id,
            valid_from: $valid_from,
            initial_confidence: $initial_confidence,
            current_confidence: $current_confidence,
            verification_status: $verification_status,
            created_at: $created_at,
            updated_at: $updated_at,
            confidence: $confidence
        """
        
        # Add optional properties
        if self.valid_to:
            query += ",\n            valid_to: $valid_to"
        
        if self.decay_rate is not None:
            query += ",\n            decay_rate: $decay_rate"
        
        if self.source:
            query += ",\n            source: $source"
        
        if self.creation_source:
            query += ",\n            creation_source: $creation_source"
        
        # Add bidirectional flag
        query += f",\n            bidirectional: {str(self.bidirectional).lower()}"
        
        # Add custom properties
        for key in self.properties:
            if key not in {"id", "valid_from", "valid_to", "initial_confidence", 
                         "current_confidence", "verification_status", "created_at", 
                         "updated_at", "confidence", "source", "decay_rate", 
                         "creation_source", "bidirectional", "source_id", "target_id"}:
                query += f",\n            {key}: ${key}"
        
        query += "\n        }}]->(target)\n        RETURN r"
        
        return query, params