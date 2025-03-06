"""
AI-specific temporal models for Knowledge Graph System.

This module provides specialized temporal data models for AI research entities
in the Knowledge Graph System, extending the base temporal models with AI-specific
attributes and relationships.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from src.knowledge_graph_system.core.models.ai_models import AIModel, Dataset, Algorithm, Paper, Task
from src.knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)


@dataclass
class TemporalAIModel(TemporalEntityBase):
    """
    Temporal entity class for AI models with version tracking.
    
    Attributes:
        name: Name of the model
        organization: Organization that developed the model
        release_date: Date the model was released
        model_type: Type of model (e.g., language model, vision model)
        parameters: Number of parameters
        architecture: Model architecture
        training_data: Description of training data
        capabilities: List of model capabilities
        limitations: List of model limitations
        repository: URL to model repository
        paper: URL to model paper
    """
    
    name: str = ""
    organization: Optional[str] = None
    release_date: Optional[str] = None
    model_type: Optional[str] = None
    parameters: Optional[float] = None  # In billions
    architecture: Optional[str] = None
    training_data: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    repository: Optional[str] = None
    paper: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    is_open_source: bool = False
    license_type: Optional[str] = None
    
    def __post_init__(self):
        """Initialize the entity with AI model label and temporal properties."""
        self.label = "AIModel"
        self.labels = {"AIModel", "TemporalEntity"}
        
        # Update properties with model-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.organization:
            self.properties["organization"] = self.organization
        
        if self.release_date:
            self.properties["release_date"] = self.release_date
        
        if self.model_type:
            self.properties["model_type"] = self.model_type
        
        if self.parameters is not None:
            self.properties["parameters"] = self.parameters
        
        if self.architecture:
            self.properties["architecture"] = self.architecture
        
        if self.training_data:
            self.properties["training_data"] = self.training_data
        
        if self.capabilities:
            self.properties["capabilities"] = self.capabilities
        
        if self.limitations:
            self.properties["limitations"] = self.limitations
        
        if self.repository:
            self.properties["repository"] = self.repository
        
        if self.paper:
            self.properties["paper"] = self.paper
            
        if self.performance_metrics:
            self.properties["performance_metrics"] = self.performance_metrics
            
        self.properties["is_open_source"] = self.is_open_source
        
        if self.license_type:
            self.properties["license_type"] = self.license_type
        
        # Call the temporal entity's post init
        super().__post_init__()
    
    @classmethod
    def from_ai_model(cls, model: AIModel, version_number: float = 1.0, 
                     valid_from: datetime = None, entity_id: str = None) -> 'TemporalAIModel':
        """
        Create a temporal AI model from a standard AI model.
        
        Args:
            model: Source AI model
            version_number: Version number to assign
            valid_from: When this version became valid (defaults to model's creation date)
            entity_id: Stable entity ID across versions (defaults to new UUID)
            
        Returns:
            TemporalAIModel instance
        """
        # Use the model's creation date if valid_from not provided
        if valid_from is None:
            valid_from = model.created_at
            
        # Use the model's ID as entity_id if not provided
        if entity_id is None:
            entity_id = model.id
            
        # Create temporal model with attributes from source model
        temporal_model = cls(
            id=str(uuid.uuid4()),  # New ID for this version
            entity_id=entity_id,
            version_id=f"{entity_id}_v{version_number}",
            version_number=version_number,
            valid_from=valid_from,
            name=model.name,
            organization=model.properties.get("organization"),
            release_date=model.properties.get("release_date"),
            model_type=model.properties.get("model_type"),
            parameters=model.properties.get("parameters"),
            architecture=model.properties.get("architecture"),
            training_data=model.properties.get("training_data"),
            capabilities=model.properties.get("capabilities", []),
            limitations=model.properties.get("limitations", []),
            repository=model.properties.get("repository"),
            paper=model.properties.get("paper"),
            source=model.source,
            confidence=model.confidence,
            creation_source=model.source,
            creation_confidence=model.confidence
        )
        
        return temporal_model


@dataclass
class TemporalDataset(TemporalEntityBase):
    """
    Temporal entity class for datasets with version tracking.
    
    Attributes:
        name: Name of the dataset
        description: Description of the dataset
        domain: Domain of the dataset
        size: Size metrics of the dataset
        format: Format of the dataset
        license: License information
        version_changes: List of changes in this version
        access_url: URL to access the dataset
    """
    
    name: str = ""
    description: Optional[str] = None
    domain: Optional[str] = None
    size: Optional[str] = None
    format: Optional[str] = None
    license: Optional[str] = None
    version_changes: List[str] = field(default_factory=list)
    access_url: Optional[str] = None
    modalities: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the entity with Dataset label and temporal properties."""
        self.label = "Dataset"
        self.labels = {"Dataset", "TemporalEntity"}
        
        # Update properties with dataset-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.description:
            self.properties["description"] = self.description
        
        if self.domain:
            self.properties["domain"] = self.domain
        
        if self.size:
            self.properties["size"] = self.size
        
        if self.format:
            self.properties["format"] = self.format
        
        if self.license:
            self.properties["license"] = self.license
        
        if self.version_changes:
            self.properties["version_changes"] = self.version_changes
        
        if self.access_url:
            self.properties["access_url"] = self.access_url
            
        if self.modalities:
            self.properties["modalities"] = self.modalities
            
        if self.domains:
            self.properties["domains"] = self.domains
        
        # Call the temporal entity's post init
        super().__post_init__()
    
    @classmethod
    def from_dataset(cls, dataset: Dataset, version_number: float = 1.0, 
                   valid_from: datetime = None, entity_id: str = None) -> 'TemporalDataset':
        """
        Create a temporal dataset from a standard dataset.
        
        Args:
            dataset: Source dataset
            version_number: Version number to assign
            valid_from: When this version became valid (defaults to dataset's creation date)
            entity_id: Stable entity ID across versions (defaults to new UUID)
            
        Returns:
            TemporalDataset instance
        """
        # Use the dataset's creation date if valid_from not provided
        if valid_from is None:
            valid_from = dataset.created_at
            
        # Use the dataset's ID as entity_id if not provided
        if entity_id is None:
            entity_id = dataset.id
            
        # Create temporal dataset with attributes from source dataset
        temporal_dataset = cls(
            id=str(uuid.uuid4()),  # New ID for this version
            entity_id=entity_id,
            version_id=f"{entity_id}_v{version_number}",
            version_number=version_number,
            valid_from=valid_from,
            name=dataset.name,
            description=dataset.properties.get("description"),
            domain=dataset.properties.get("domain"),
            size=dataset.properties.get("size"),
            format=dataset.properties.get("format"),
            license=dataset.properties.get("license"),
            access_url=dataset.properties.get("url"),
            modalities=dataset.properties.get("features", []),
            domains=dataset.properties.get("domains", []),
            source=dataset.source,
            confidence=dataset.confidence,
            creation_source=dataset.source,
            creation_confidence=dataset.confidence
        )
        
        return temporal_dataset


@dataclass
class TemporalAlgorithm(TemporalEntityBase):
    """
    Temporal entity class for algorithms with version tracking.
    
    Attributes:
        name: Name of the algorithm
        description: Description of the algorithm
        complexity: Computational complexity
        pseudocode: Pseudocode representation
        improvements: Improvements over previous versions
        limitations: Known limitations
        variant_type: Nature of this variant
    """
    
    name: str = ""
    description: Optional[str] = None
    complexity: Optional[Dict[str, str]] = None
    pseudocode: Optional[str] = None
    improvements: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    variant_type: Optional[str] = None
    domains: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the entity with Algorithm label and temporal properties."""
        self.label = "Algorithm"
        self.labels = {"Algorithm", "TemporalEntity"}
        
        # Update properties with algorithm-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.description:
            self.properties["description"] = self.description
        
        if self.complexity:
            self.properties["complexity"] = self.complexity
        
        if self.pseudocode:
            self.properties["pseudocode"] = self.pseudocode
        
        if self.improvements:
            self.properties["improvements"] = self.improvements
        
        if self.limitations:
            self.properties["limitations"] = self.limitations
        
        if self.variant_type:
            self.properties["variant_type"] = self.variant_type
            
        if self.domains:
            self.properties["domains"] = self.domains
        
        # Call the temporal entity's post init
        super().__post_init__()
    
    @classmethod
    def from_algorithm(cls, algorithm: Algorithm, version_number: float = 1.0, 
                     valid_from: datetime = None, entity_id: str = None) -> 'TemporalAlgorithm':
        """
        Create a temporal algorithm from a standard algorithm.
        
        Args:
            algorithm: Source algorithm
            version_number: Version number to assign
            valid_from: When this version became valid (defaults to algorithm's creation date)
            entity_id: Stable entity ID across versions (defaults to new UUID)
            
        Returns:
            TemporalAlgorithm instance
        """
        # Use the algorithm's creation date if valid_from not provided
        if valid_from is None:
            valid_from = algorithm.created_at
            
        # Use the algorithm's ID as entity_id if not provided
        if entity_id is None:
            entity_id = algorithm.id
            
        # Create temporal algorithm with attributes from source algorithm
        temporal_algorithm = cls(
            id=str(uuid.uuid4()),  # New ID for this version
            entity_id=entity_id,
            version_id=f"{entity_id}_v{version_number}",
            version_number=version_number,
            valid_from=valid_from,
            name=algorithm.name,
            description=algorithm.properties.get("description"),
            complexity=algorithm.properties.get("complexity"),
            pseudocode=algorithm.properties.get("pseudo_code"),
            limitations=algorithm.properties.get("limitations", []),
            domains=algorithm.properties.get("domains", []),
            source=algorithm.source,
            confidence=algorithm.confidence,
            creation_source=algorithm.source,
            creation_confidence=algorithm.confidence
        )
        
        return temporal_algorithm


# Evolution-specific relationship types
@dataclass
class EvolvedInto(TemporalRelationshipBase):
    """
    Relationship indicating that one entity version evolved into another.
    
    Attributes:
        evolution_type: Type of evolution (gradual, revolutionary, etc.)
        has_breaking_changes: Whether changes are backwards-compatible
        evolution_metrics: Quantitative metrics of the evolution
    """
    
    evolution_type: str = "gradual"
    has_breaking_changes: bool = False
    evolution_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the relationship with EVOLVED_INTO type and evolution properties."""
        self.type = "EVOLVED_INTO"
        
        # Add evolution-specific properties
        self.properties.update({
            "evolution_type": self.evolution_type,
            "has_breaking_changes": self.has_breaking_changes
        })
        
        if self.evolution_metrics:
            self.properties["evolution_metrics"] = self.evolution_metrics
        
        # Call the temporal relationship's post init
        super().__post_init__()


@dataclass
class ReplacedBy(TemporalRelationshipBase):
    """
    Relationship indicating that one entity has been replaced by another.
    
    Attributes:
        replacement_reason: Reason for replacement
        compatibility: Level of compatibility (none, partial, full)
        transition_period: Time allowed for transition
    """
    
    replacement_reason: str = ""
    compatibility: str = "none"  # none, partial, full
    transition_period: Optional[int] = None  # Days
    
    def __post_init__(self):
        """Initialize the relationship with REPLACED_BY type and replacement properties."""
        self.type = "REPLACED_BY"
        
        # Add replacement-specific properties
        self.properties.update({
            "replacement_reason": self.replacement_reason,
            "compatibility": self.compatibility
        })
        
        if self.transition_period is not None:
            self.properties["transition_period"] = self.transition_period
        
        # Call the temporal relationship's post init
        super().__post_init__()


@dataclass
class Inspired(TemporalRelationshipBase):
    """
    Relationship indicating that one entity inspired another.
    
    Attributes:
        influence_strength: Degree of influence (0.0 to 1.0)
        influence_aspects: Specific aspects that were influenced
    """
    
    influence_strength: float = 0.5
    influence_aspects: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the relationship with INSPIRED type and influence properties."""
        self.type = "INSPIRED"
        
        # Add influence-specific properties
        self.properties.update({
            "influence_strength": self.influence_strength
        })
        
        if self.influence_aspects:
            self.properties["influence_aspects"] = self.influence_aspects
        
        # Call the temporal relationship's post init
        super().__post_init__()


@dataclass
class MergedWith(TemporalRelationshipBase):
    """
    Relationship indicating that multiple entities merged to form a new one.
    
    Attributes:
        contributing_entities: IDs of all entities involved in the merge
        contribution_proportions: Relative contribution of each entity
        merger_date: When the merger occurred
    """
    
    contributing_entities: List[str] = field(default_factory=list)
    contribution_proportions: Dict[str, float] = field(default_factory=dict)
    merger_date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize the relationship with MERGED_WITH type and merger properties."""
        self.type = "MERGED_WITH"
        
        # Add merger-specific properties
        self.properties.update({
            "merger_date": self.merger_date.isoformat()
        })
        
        if self.contributing_entities:
            self.properties["contributing_entities"] = self.contributing_entities
        
        if self.contribution_proportions:
            self.properties["contribution_proportions"] = self.contribution_proportions
        
        # Call the temporal relationship's post init
        super().__post_init__()