"""
Base models for Knowledge Graph System.

This module provides the base data models for entities and relationships
in the Knowledge Graph System.
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field, asdict
import uuid
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GraphEntity:
    """
    Base class for all graph entities (nodes).
    
    Attributes:
        id: Unique identifier for the entity
        label: Primary label/type of the entity
        properties: Dictionary of entity properties
        created_at: Timestamp when the entity was created
        updated_at: Timestamp when the entity was last updated
        aliases: Alternative identifiers for the entity
        confidence: Confidence score for this entity (0.0 to 1.0)
        source: Source of the entity information
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = "Entity"
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    aliases: List[str] = field(default_factory=list)
    confidence: float = 1.0
    source: Optional[str] = None
    labels: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Perform post-initialization validation and setup."""
        if not self.labels:
            self.labels = {self.label}
        elif self.label not in self.labels:
            self.labels.add(self.label)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the entity to a dictionary.
        
        Returns:
            Dictionary representation of the entity
        """
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        # Convert set to list for JSON serialization
        data['labels'] = list(data['labels'])
        
        return data
    
    def to_json(self) -> str:
        """
        Convert the entity to a JSON string.
        
        Returns:
            JSON string representation of the entity
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphEntity':
        """
        Create an entity from a dictionary.
        
        Args:
            data: Dictionary containing entity data
            
        Returns:
            GraphEntity instance
        """
        # Convert ISO format strings to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Convert list to set for labels
        if 'labels' in data and isinstance(data['labels'], list):
            data['labels'] = set(data['labels'])
        
        return cls(**data)
    
    def update(self, properties: Dict[str, Any]) -> 'GraphEntity':
        """
        Update entity properties.
        
        Args:
            properties: Dictionary of properties to update
            
        Returns:
            Updated GraphEntity instance
        """
        for key, value in properties.items():
            if key in ['id', 'created_at']:
                # Don't allow updating id or created_at
                continue
            
            if key == 'properties':
                # Merge properties dictionary
                self.properties.update(value)
            elif key == 'labels':
                # Update labels set
                if isinstance(value, list):
                    self.labels.update(set(value))
                elif isinstance(value, set):
                    self.labels.update(value)
            else:
                # Update regular attribute
                setattr(self, key, value)
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now()
        
        return self
    
    def add_alias(self, alias: str) -> 'GraphEntity':
        """
        Add an alias to the entity.
        
        Args:
            alias: Alias to add
            
        Returns:
            Updated GraphEntity instance
        """
        if alias not in self.aliases:
            self.aliases.append(alias)
            self.updated_at = datetime.now()
        
        return self
    
    def add_label(self, label: str) -> 'GraphEntity':
        """
        Add a label to the entity.
        
        Args:
            label: Label to add
            
        Returns:
            Updated GraphEntity instance
        """
        if label not in self.labels:
            self.labels.add(label)
            self.updated_at = datetime.now()
        
        return self
    
    def to_cypher_params(self) -> Dict[str, Any]:
        """
        Convert the entity to parameters for a Cypher query.
        
        Returns:
            Dictionary of parameters for Cypher query
        """
        # Start with the properties
        params = dict(self.properties)
        
        # Add the core attributes
        params.update({
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confidence': self.confidence
        })
        
        # Add optional attributes
        if self.aliases:
            params['aliases'] = self.aliases
        
        if self.source:
            params['source'] = self.source
        
        return params
    
    def get_cypher_create(self) -> tuple[str, Dict[str, Any]]:
        """
        Generate a Cypher query to create this entity.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        params = self.to_cypher_params()
        labels_str = ':'.join(self.labels)
        
        # Build the query
        query = f"""
        CREATE (e:{labels_str} {{
            id: $id,
            created_at: $created_at,
            updated_at: $updated_at,
            confidence: $confidence
        """
        
        # Add optional properties
        if self.aliases:
            query += ",\n            aliases: $aliases"
        
        if self.source:
            query += ",\n            source: $source"
        
        # Add custom properties
        for key in self.properties:
            query += f",\n            {key}: ${key}"
        
        query += "\n        })\n        RETURN e"
        
        return query, params


@dataclass
class GraphRelationship:
    """
    Base class for all graph relationships (edges).
    
    Attributes:
        id: Unique identifier for the relationship
        type: Type of the relationship
        source_id: ID of the source entity
        target_id: ID of the target entity
        properties: Dictionary of relationship properties
        created_at: Timestamp when the relationship was created
        updated_at: Timestamp when the relationship was last updated
        confidence: Confidence score for this relationship (0.0 to 1.0)
        source: Source of the relationship information
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "RELATED_TO"
    source_id: str = ""
    target_id: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    source: Optional[str] = None
    bidirectional: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the relationship to a dictionary.
        
        Returns:
            Dictionary representation of the relationship
        """
        data = asdict(self)
        
        # Convert datetime objects to ISO format strings
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        return data
    
    def to_json(self) -> str:
        """
        Convert the relationship to a JSON string.
        
        Returns:
            JSON string representation of the relationship
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphRelationship':
        """
        Create a relationship from a dictionary.
        
        Args:
            data: Dictionary containing relationship data
            
        Returns:
            GraphRelationship instance
        """
        # Convert ISO format strings to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def update(self, properties: Dict[str, Any]) -> 'GraphRelationship':
        """
        Update relationship properties.
        
        Args:
            properties: Dictionary of properties to update
            
        Returns:
            Updated GraphRelationship instance
        """
        for key, value in properties.items():
            if key in ['id', 'created_at']:
                # Don't allow updating id or created_at
                continue
            
            if key == 'properties':
                # Merge properties dictionary
                self.properties.update(value)
            else:
                # Update regular attribute
                setattr(self, key, value)
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now()
        
        return self
    
    def to_cypher_params(self) -> Dict[str, Any]:
        """
        Convert the relationship to parameters for a Cypher query.
        
        Returns:
            Dictionary of parameters for Cypher query
        """
        # Start with the properties
        params = dict(self.properties)
        
        # Add the core attributes
        params.update({
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confidence': self.confidence,
            'source_id': self.source_id,
            'target_id': self.target_id
        })
        
        # Add optional attributes
        if self.source:
            params['source'] = self.source
        
        params['bidirectional'] = self.bidirectional
        
        return params
    
    def get_cypher_create(self) -> tuple[str, Dict[str, Any]]:
        """
        Generate a Cypher query to create this relationship.
        
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
            created_at: $created_at,
            updated_at: $updated_at,
            confidence: $confidence
        """
        
        # Add optional properties
        if self.source:
            query += ",\n            source: $source"
        
        # Add custom properties
        for key in self.properties:
            query += f",\n            {key}: ${key}"
        
        query += "\n        }}]->(target)\n        RETURN r"
        
        return query, params