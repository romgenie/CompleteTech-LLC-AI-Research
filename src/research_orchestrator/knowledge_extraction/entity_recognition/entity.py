"""
Entity data model for the Research Orchestration Framework.

This module defines the data structures for representing entities extracted
from research documents.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional
import uuid


class EntityType(Enum):
    """Enumeration of entity types recognized by the system."""
    # AI-specific entity types
    MODEL = auto()
    ALGORITHM = auto()
    ARCHITECTURE = auto()
    DATASET = auto()
    METRIC = auto()
    PARAMETER = auto()
    HYPERPARAMETER = auto()
    FRAMEWORK = auto()
    LIBRARY = auto()
    TECHNIQUE = auto()
    TASK = auto()
    BENCHMARK = auto()
    
    # Scientific entity types
    CONCEPT = auto()
    THEORY = auto()
    METHODOLOGY = auto()
    FINDING = auto()
    HYPOTHESIS = auto()
    EXPERIMENT = auto()
    ARTIFACT = auto()
    TOOL = auto()
    PROPERTY = auto()
    CONSTRAINT = auto()
    LIMITATION = auto()
    FIELD = auto()
    AUTHOR = auto()
    INSTITUTION = auto()
    
    # Other/generic types
    UNKNOWN = auto()
    
    @classmethod
    def from_string(cls, type_str: str) -> 'EntityType':
        """Convert a string representation to an EntityType enum value.
        
        Args:
            type_str: String representation of the entity type
            
        Returns:
            The corresponding EntityType enum value
        """
        try:
            return cls[type_str.upper()]
        except KeyError:
            return cls.UNKNOWN
    
    def __str__(self) -> str:
        """Return the lowercase string representation of the entity type."""
        return self.name.lower()


@dataclass
class Entity:
    """Representation of an entity extracted from text.
    
    Attributes:
        id: Unique identifier for the entity
        text: The actual text of the entity
        type: The type of entity (from EntityType enum)
        confidence: Confidence score (0.0-1.0) for this entity
        start_pos: Starting position in the source text
        end_pos: Ending position in the source text
        metadata: Additional information about the entity
    """
    text: str
    type: EntityType
    confidence: float = 1.0
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        """Validate the entity after initialization."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        # Ensure type is an EntityType
        if isinstance(self.type, str):
            self.type = EntityType.from_string(self.type)
        elif not isinstance(self.type, EntityType):
            raise TypeError(f"Type must be an EntityType or string, got {type(self.type)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary.
        
        Returns:
            Dictionary representation of the entity
        """
        return {
            "id": self.id,
            "text": self.text,
            "type": str(self.type),
            "confidence": self.confidence,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create an entity from a dictionary.
        
        Args:
            data: Dictionary representation of the entity
            
        Returns:
            Entity object
        """
        type_str = data.pop("type")
        entity_type = EntityType.from_string(type_str)
        return cls(type=entity_type, **data)
    
    def overlaps_with(self, other: 'Entity') -> bool:
        """Check if this entity overlaps with another entity in the source text.
        
        Args:
            other: Another entity to check for overlap
            
        Returns:
            True if the entities overlap, False otherwise
        """
        if self.start_pos is None or self.end_pos is None or \
           other.start_pos is None or other.end_pos is None:
            return False
        
        return (
            (self.start_pos <= other.start_pos < self.end_pos) or
            (self.start_pos < other.end_pos <= self.end_pos) or
            (other.start_pos <= self.start_pos < other.end_pos) or
            (other.start_pos < self.end_pos <= other.end_pos)
        )
    
    def contains(self, other: 'Entity') -> bool:
        """Check if this entity fully contains another entity.
        
        Args:
            other: Another entity to check
            
        Returns:
            True if this entity contains the other, False otherwise
        """
        if self.start_pos is None or self.end_pos is None or \
           other.start_pos is None or other.end_pos is None:
            return False
        
        return (
            self.start_pos <= other.start_pos and
            self.end_pos >= other.end_pos
        )
    
    def __len__(self) -> int:
        """Get the length of the entity text."""
        return len(self.text)