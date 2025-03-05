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
    
    # Core relationship types
    IS_A = auto()                # Subclass/superclass relationship
    PART_OF = auto()             # Component or membership relationship
    USED_FOR = auto()            # Purpose-based relationship
    BUILDS_ON = auto()           # Based on prior work
    DEVELOPED_BY = auto()        # Creator/developer relationship
    EVALUATED_ON = auto()        # Evaluation relationship
    OUTPERFORMS = auto()         # Performance comparison
    IMPLEMENTS = auto()          # Implementation relationship
    EXTENDS = auto()             # Extension of existing work
    RELATED_TO = auto()          # General-purpose relationship
    BASED_ON = auto()            # Based on relationship
    
    # AI research relationships
    TRAINED_ON = auto()          # Model trained on dataset
    ACHIEVES = auto()            # Achieves results/performance
    USES = auto()                # Uses a technique/method
    COMPARED_TO = auto()         # Comparison relationship
    FEATURE_OF = auto()          # Feature/property relationship
    PARAMETER_OF = auto()        # Parameter-based relationship
    APPLIED_TO = auto()          # Applied to a problem domain
    OPTIMIZED_FOR = auto()       # Optimization target
    BELONGS_TO = auto()          # Domain/field membership
    SUPPORTED_BY = auto()        # Support/funding relationship
    IMPLEMENTED_IN = auto()      # Implementation language/framework
    COMPOSED_OF = auto()         # Compositional relationship
    COMPATIBLE_WITH = auto()     # Compatibility relationship
    
    # Scientific relationships
    HYPOTHESIZES = auto()        # Proposes a hypothesis
    PROVES = auto()              # Proves a theorem/concept
    DISPROVES = auto()           # Disproves a hypothesis
    CITES = auto()               # Citation relationship
    CITED_BY = auto()            # Inverse of cites
    CONTRADICTS = auto()         # Contradiction relationship
    CONTRADICTED_BY = auto()     # Inverse of contradicts
    CONFIRMS = auto()            # Confirmation relationship
    REPLICATES = auto()          # Replicates results from a previous study
    STUDIES = auto()             # Studies a phenomenon
    ANALYZES = auto()            # Analysis relationship
    INTRODUCES = auto()          # Introduction of new concept
    IMPROVES_UPON = auto()       # Improvement relationship
    
    # Additional academic relationships
    PROPOSES = auto()            # Proposes a new theory/approach
    AUTHORED_BY = auto()         # Authorship relationship
    AUTHOR_OF = auto()           # Inverse of authored_by
    AFFILIATED_WITH = auto()     # Institutional affiliation
    HAS_MEMBER = auto()          # Inverse of affiliated_with
    COLLABORATES_WITH = auto()   # Collaboration between researchers
    HAS_CODE = auto()            # Link to implementation code
    EXPLAINS = auto()            # Explanation relationship
    PRODUCES = auto()            # Production relationship
    PRODUCED = auto()            # Inverse of produces/developed_by
    USED_BY = auto()             # Usage relationship
    BASIS_FOR = auto()           # Foundation relationship
    DERIVED_FROM = auto()        # Derivation relationship for algorithms/models/datasets
    OUTPERFORMED_BY = auto()     # Inverse of outperforms
    IMPLEMENTED_BY = auto()      # Inverse of implements
    CONTAINS = auto()            # Container relationship
    HAS_FEATURE = auto()         # Feature relationship
    HAS_PARAMETER = auto()       # Parameter relationship
    
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
            RelationType.PART_OF: RelationType.CONTAINS,
            RelationType.CONTAINS: RelationType.PART_OF,
            RelationType.COMPOSED_OF: RelationType.PART_OF,
            RelationType.USES: RelationType.USED_BY,
            RelationType.USED_BY: RelationType.USES,
            RelationType.TRAINED_ON: RelationType.USED_FOR,
            RelationType.BUILDS_ON: RelationType.BASIS_FOR,
            RelationType.BASIS_FOR: RelationType.BUILDS_ON,
            RelationType.DERIVED_FROM: RelationType.BASIS_FOR,
            RelationType.DEVELOPED_BY: RelationType.PRODUCED,
            RelationType.OUTPERFORMS: RelationType.OUTPERFORMED_BY,
            RelationType.OUTPERFORMED_BY: RelationType.OUTPERFORMS,
            RelationType.IMPLEMENTS: RelationType.IMPLEMENTED_BY,
            RelationType.IMPLEMENTED_BY: RelationType.IMPLEMENTS,
            RelationType.BELONGS_TO: RelationType.CONTAINS,
            RelationType.FEATURE_OF: RelationType.HAS_FEATURE,
            RelationType.HAS_FEATURE: RelationType.FEATURE_OF,
            RelationType.PARAMETER_OF: RelationType.HAS_PARAMETER,
            RelationType.HAS_PARAMETER: RelationType.PARAMETER_OF,
            RelationType.AUTHORED_BY: RelationType.AUTHOR_OF,
            RelationType.AUTHOR_OF: RelationType.AUTHORED_BY,
            RelationType.AFFILIATED_WITH: RelationType.HAS_MEMBER,
            RelationType.HAS_MEMBER: RelationType.AFFILIATED_WITH,
            RelationType.COLLABORATES_WITH: RelationType.COLLABORATES_WITH,
            RelationType.CITES: RelationType.CITED_BY,
            RelationType.CITED_BY: RelationType.CITES,
            RelationType.CONTRADICTS: RelationType.CONTRADICTED_BY,
            RelationType.CONTRADICTED_BY: RelationType.CONTRADICTS,
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