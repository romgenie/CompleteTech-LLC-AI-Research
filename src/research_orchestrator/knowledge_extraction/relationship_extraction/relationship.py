"""
Relationship data models for the Research Orchestration Framework.

This module defines the data structures for representing relationships between
entities extracted from research documents.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional, List
import uuid
import json
import os

# Import Entity from entity recognition
from ..entity_recognition.entity import Entity


class RelationType(Enum):
    """Enumeration of relationship types recognized by the system."""
    
    # General relationship types
    IS_A = auto()
    PART_OF = auto()
    USED_FOR = auto()
    BASED_ON = auto()
    DEVELOPED_BY = auto()
    EVALUATED_ON = auto()
    OUTPERFORMS = auto()
    IMPLEMENTS = auto()
    EXTENDS = auto()
    RELATED_TO = auto()
    
    # AI-specific relationship types
    TRAINED_ON = auto()
    ACHIEVES = auto()
    USES = auto()
    COMPARED_TO = auto()
    FEATURE_OF = auto()
    PARAMETER_OF = auto()
    APPLIED_TO = auto()
    OPTIMIZED_FOR = auto()
    BELONGS_TO = auto()
    SUPPORTED_BY = auto()
    IMPLEMENTED_IN = auto()
    COMPOSED_OF = auto()
    COMPATIBLE_WITH = auto()
    
    # Scientific relationship types
    HYPOTHESIZES = auto()
    PROVES = auto()
    DISPROVES = auto()
    CITES = auto()
    CONTRADICTS = auto()
    CONFIRMS = auto()
    STUDIES = auto()
    ANALYZES = auto()
    INTRODUCES = auto()
    IMPROVES_UPON = auto()
    EXPLAINS = auto()
    PRODUCES = auto()
    USED_BY = auto()
    BASIS_FOR = auto()
    OUTPERFORMED_BY = auto()
    IMPLEMENTED_BY = auto()
    CONTAINS = auto()
    HAS_FEATURE = auto()
    HAS_PARAMETER = auto()
    
    # Other/generic types
    UNKNOWN = auto()
    
    @classmethod
    def from_string(cls, type_str: str) -> 'RelationType':
        """Convert a string representation to a RelationType enum value.
        
        Args:
            type_str: String representation of the relationship type
            
        Returns:
            The corresponding RelationType enum value
        """
        try:
            return cls[type_str.upper()]
        except KeyError:
            return cls.UNKNOWN
    
    def __str__(self) -> str:
        """Return the lowercase string representation of the relationship type."""
        return self.name.lower()


@dataclass
class Relationship:
    """Representation of a relationship between two entities.
    
    Attributes:
        id: Unique identifier for the relationship
        source: The source entity in the relationship
        target: The target entity in the relationship
        relation_type: The type of relationship between the entities
        confidence: Confidence score (0.0-1.0) for this relationship
        context: The surrounding text context where the relationship was found
        bidirectional: Whether the relationship applies in both directions
        metadata: Additional information about the relationship
    """
    source: Entity
    target: Entity
    relation_type: RelationType
    confidence: float = 1.0
    context: Optional[str] = None
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Validate the relationship after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        # Ensure relation_type is a RelationType
        if isinstance(self.relation_type, str):
            self.relation_type = RelationType.from_string(self.relation_type)
        elif not isinstance(self.relation_type, RelationType):
            raise TypeError(f"Relation type must be a RelationType or string, got {type(self.relation_type)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary.
        
        Returns:
            Dictionary representation of the relationship
        """
        return {
            "id": self.id,
            "source": self.source.to_dict() if self.source else None,
            "target": self.target.to_dict() if self.target else None,
            "relation_type": str(self.relation_type),
            "confidence": self.confidence,
            "context": self.context,
            "bidirectional": self.bidirectional,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a relationship from a dictionary.
        
        Args:
            data: Dictionary representation of the relationship
            
        Returns:
            Relationship object
        """
        # Create entities from dictionary representations
        source_dict = data.pop("source", None)
        target_dict = data.pop("target", None)
        
        source = Entity.from_dict(source_dict) if source_dict else None
        target = Entity.from_dict(target_dict) if target_dict else None
        
        # Get relation type
        type_str = data.pop("relation_type", "unknown")
        relation_type = RelationType.from_string(type_str)
        
        # Create relationship
        return cls(source=source, target=target, relation_type=relation_type, **data)
    
    def get_inverse(self) -> Optional['Relationship']:
        """Get the inverse of this relationship, if applicable.
        
        For some relationship types, an inverse relationship can be automatically
        determined (e.g., the inverse of A PART_OF B is B COMPOSED_OF A).
        
        Returns:
            The inverse relationship, or None if no inverse exists
        """
        # Define inverse relationship types
        inverse_types = {
            RelationType.PART_OF: RelationType.COMPOSED_OF,
            RelationType.COMPOSED_OF: RelationType.PART_OF,
            RelationType.USES: RelationType.USED_BY,
            RelationType.TRAINED_ON: RelationType.USED_TO_TRAIN,
            RelationType.BASED_ON: RelationType.BASIS_FOR,
            RelationType.OUTPERFORMS: RelationType.OUTPERFORMED_BY,
            RelationType.IMPLEMENTS: RelationType.IMPLEMENTED_BY,
            RelationType.BELONGS_TO: RelationType.CONTAINS,
            RelationType.FEATURE_OF: RelationType.HAS_FEATURE,
            RelationType.PARAMETER_OF: RelationType.HAS_PARAMETER,
        }
        
        # If bidirectional, just swap source and target
        if self.bidirectional:
            return Relationship(
                source=self.target,
                target=self.source,
                relation_type=self.relation_type,
                confidence=self.confidence,
                context=self.context,
                bidirectional=True,
                metadata=self.metadata.copy(),
            )
        
        # Check if this relationship type has an inverse
        if self.relation_type in inverse_types:
            inverse_type = inverse_types[self.relation_type]
            return Relationship(
                source=self.target,
                target=self.source,
                relation_type=inverse_type,
                confidence=self.confidence,
                context=self.context,
                bidirectional=False,
                metadata=self.metadata.copy(),
            )
        
        return None
    
    @classmethod
    def save_relationships(cls, relationships: List['Relationship'], filepath: str) -> None:
        """Save a list of relationships to a JSON file.
        
        Args:
            relationships: List of relationships to save
            filepath: Path to the output JSON file
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                [rel.to_dict() for rel in relationships],
                f,
                indent=2
            )
    
    @classmethod
    def load_relationships(cls, filepath: str) -> List['Relationship']:
        """Load relationships from a JSON file.
        
        Args:
            filepath: Path to the input JSON file
            
        Returns:
            List of relationship objects
        """
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            rel_dicts = json.load(f)
        
        return [cls.from_dict(rel_dict) for rel_dict in rel_dicts]