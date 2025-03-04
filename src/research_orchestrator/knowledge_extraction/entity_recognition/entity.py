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
    # Core entity types
    MODEL = auto()               # Neural network architectures, LLMs, etc.
    ALGORITHM = auto()           # Specific algorithms and methods
    DATASET = auto()             # Benchmark and training datasets
    METRIC = auto()              # Evaluation metrics
    PAPER = auto()               # Research publications
    AUTHOR = auto()              # Researchers and paper authors
    INSTITUTION = auto()         # Research institutions, universities, labs
    CODE = auto()                # Implementation repositories or source code
    CONCEPT = auto()             # AI concepts, methods, techniques
    
    # AI-specific entity types
    ARCHITECTURE = auto()        # Neural network architectural patterns
    PARAMETER = auto()           # Model parameters and weights
    HYPERPARAMETER = auto()      # Training and model configuration parameters
    FRAMEWORK = auto()           # Software frameworks (TensorFlow, PyTorch)
    LIBRARY = auto()             # Software libraries
    TECHNIQUE = auto()           # Specific AI techniques
    TASK = auto()                # AI tasks (classification, generation)
    BENCHMARK = auto()           # Standard evaluation benchmarks
    COMPONENT = auto()           # Modular parts of larger systems
    FEATURE = auto()             # Features or attributes
    
    # Scientific entity types
    THEORY = auto()              # Scientific theories
    METHODOLOGY = auto()         # Research methodologies
    FINDING = auto()             # Research findings and results
    HYPOTHESIS = auto()          # Scientific hypotheses
    EXPERIMENT = auto()          # Experimental setups and procedures
    ARTIFACT = auto()            # Research artifacts
    TOOL = auto()                # Tools and instruments
    PROPERTY = auto()            # Properties and characteristics
    CONSTRAINT = auto()          # Limitations and constraints
    LIMITATION = auto()          # Known limitations
    FIELD = auto()               # Research fields and domains
    PROBLEM = auto()             # Research problems and challenges
    SOLUTION = auto()            # Proposed solutions
    
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