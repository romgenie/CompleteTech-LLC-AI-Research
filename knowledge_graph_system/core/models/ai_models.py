"""
AI-specific models for Knowledge Graph System.

This module provides specialized data models for AI research entities
in the Knowledge Graph System.
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime

from knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship


@dataclass
class AIModel(GraphEntity):
    """
    Entity class for AI models.
    
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
    parameters: Optional[int] = None
    architecture: Optional[str] = None
    training_data: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    repository: Optional[str] = None
    paper: Optional[str] = None
    
    def __post_init__(self):
        """Initialize the entity with AI model label and properties."""
        self.label = "AIModel"
        self.labels = {self.label}
        
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
        
        if self.parameters:
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
        
        # Call the parent's post init
        super().__post_init__()


@dataclass
class Dataset(GraphEntity):
    """
    Entity class for datasets.
    
    Attributes:
        name: Name of the dataset
        description: Description of the dataset
        domain: Domain of the dataset (e.g., computer vision, NLP)
        source: Source of the dataset
        size: Size of the dataset (e.g., number of examples)
        format: Format of the dataset
        license: License of the dataset
        url: URL to the dataset
        citation: Citation for the dataset
        features: List of features in the dataset
    """
    
    name: str = ""
    description: Optional[str] = None
    domain: Optional[str] = None
    dataset_source: Optional[str] = None
    size: Optional[str] = None
    format: Optional[str] = None
    license: Optional[str] = None
    url: Optional[str] = None
    citation: Optional[str] = None
    features: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the entity with Dataset label and properties."""
        self.label = "Dataset"
        self.labels = {self.label}
        
        # Update properties with dataset-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.description:
            self.properties["description"] = self.description
        
        if self.domain:
            self.properties["domain"] = self.domain
        
        if self.dataset_source:
            self.properties["dataset_source"] = self.dataset_source
        
        if self.size:
            self.properties["size"] = self.size
        
        if self.format:
            self.properties["format"] = self.format
        
        if self.license:
            self.properties["license"] = self.license
        
        if self.url:
            self.properties["url"] = self.url
        
        if self.citation:
            self.properties["citation"] = self.citation
        
        if self.features:
            self.properties["features"] = self.features
        
        # Call the parent's post init
        super().__post_init__()


@dataclass
class Algorithm(GraphEntity):
    """
    Entity class for algorithms.
    
    Attributes:
        name: Name of the algorithm
        description: Description of the algorithm
        category: Category of the algorithm (e.g., optimization, clustering)
        complexity: Computational complexity of the algorithm
        pseudo_code: Pseudo-code of the algorithm
        use_cases: List of use cases for the algorithm
        limitations: List of limitations of the algorithm
        references: List of references for the algorithm
    """
    
    name: str = ""
    description: Optional[str] = None
    category: Optional[str] = None
    complexity: Optional[str] = None
    pseudo_code: Optional[str] = None
    use_cases: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the entity with Algorithm label and properties."""
        self.label = "Algorithm"
        self.labels = {self.label}
        
        # Update properties with algorithm-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.description:
            self.properties["description"] = self.description
        
        if self.category:
            self.properties["category"] = self.category
        
        if self.complexity:
            self.properties["complexity"] = self.complexity
        
        if self.pseudo_code:
            self.properties["pseudo_code"] = self.pseudo_code
        
        if self.use_cases:
            self.properties["use_cases"] = self.use_cases
        
        if self.limitations:
            self.properties["limitations"] = self.limitations
        
        if self.references:
            self.properties["references"] = self.references
        
        # Call the parent's post init
        super().__post_init__()


@dataclass
class Metric(GraphEntity):
    """
    Entity class for evaluation metrics.
    
    Attributes:
        name: Name of the metric
        description: Description of the metric
        domain: Domain the metric is used in
        formula: Formula for computing the metric
        range: Range of possible values
        interpretation: How to interpret the metric values
        use_cases: List of use cases for the metric
        limitations: List of limitations of the metric
    """
    
    name: str = ""
    description: Optional[str] = None
    domain: Optional[str] = None
    formula: Optional[str] = None
    range: Optional[str] = None
    interpretation: Optional[str] = None
    use_cases: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the entity with Metric label and properties."""
        self.label = "Metric"
        self.labels = {self.label}
        
        # Update properties with metric-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.description:
            self.properties["description"] = self.description
        
        if self.domain:
            self.properties["domain"] = self.domain
        
        if self.formula:
            self.properties["formula"] = self.formula
        
        if self.range:
            self.properties["range"] = self.range
        
        if self.interpretation:
            self.properties["interpretation"] = self.interpretation
        
        if self.use_cases:
            self.properties["use_cases"] = self.use_cases
        
        if self.limitations:
            self.properties["limitations"] = self.limitations
        
        # Call the parent's post init
        super().__post_init__()


@dataclass
class Paper(GraphEntity):
    """
    Entity class for research papers.
    
    Attributes:
        title: Title of the paper
        authors: List of authors
        abstract: Abstract of the paper
        year: Year of publication
        venue: Venue of publication
        doi: DOI of the paper
        url: URL to the paper
        citations: Number of citations
        keywords: List of keywords
    """
    
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    citations: Optional[int] = None
    keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the entity with Paper label and properties."""
        self.label = "Paper"
        self.labels = {self.label}
        
        # Update properties with paper-specific attributes
        self.properties = {
            "title": self.title
        }
        
        if self.authors:
            self.properties["authors"] = self.authors
        
        if self.abstract:
            self.properties["abstract"] = self.abstract
        
        if self.year:
            self.properties["year"] = self.year
        
        if self.venue:
            self.properties["venue"] = self.venue
        
        if self.doi:
            self.properties["doi"] = self.doi
        
        if self.url:
            self.properties["url"] = self.url
        
        if self.citations is not None:
            self.properties["citations"] = self.citations
        
        if self.keywords:
            self.properties["keywords"] = self.keywords
        
        # Call the parent's post init
        super().__post_init__()


@dataclass
class Task(GraphEntity):
    """
    Entity class for AI tasks.
    
    Attributes:
        name: Name of the task
        description: Description of the task
        domain: Domain of the task
        input_format: Format of the input
        output_format: Format of the output
        evaluation_metrics: List of evaluation metrics
        benchmarks: List of benchmarks for this task
        examples: List of example instances
    """
    
    name: str = ""
    description: Optional[str] = None
    domain: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    evaluation_metrics: List[str] = field(default_factory=list)
    benchmarks: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize the entity with Task label and properties."""
        self.label = "Task"
        self.labels = {self.label}
        
        # Update properties with task-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.description:
            self.properties["description"] = self.description
        
        if self.domain:
            self.properties["domain"] = self.domain
        
        if self.input_format:
            self.properties["input_format"] = self.input_format
        
        if self.output_format:
            self.properties["output_format"] = self.output_format
        
        if self.evaluation_metrics:
            self.properties["evaluation_metrics"] = self.evaluation_metrics
        
        if self.benchmarks:
            self.properties["benchmarks"] = self.benchmarks
        
        if self.examples:
            self.properties["examples"] = self.examples
        
        # Call the parent's post init
        super().__post_init__()


@dataclass
class Benchmark(GraphEntity):
    """
    Entity class for AI benchmarks.
    
    Attributes:
        name: Name of the benchmark
        description: Description of the benchmark
        tasks: List of tasks in the benchmark
        metrics: List of evaluation metrics
        dataset: Associated dataset
        leaderboard: URL to leaderboard
        state_of_the_art: Current state-of-the-art result
        citation: Citation for the benchmark
    """
    
    name: str = ""
    description: Optional[str] = None
    tasks: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    dataset: Optional[str] = None
    leaderboard: Optional[str] = None
    state_of_the_art: Optional[str] = None
    citation: Optional[str] = None
    
    def __post_init__(self):
        """Initialize the entity with Benchmark label and properties."""
        self.label = "Benchmark"
        self.labels = {self.label}
        
        # Update properties with benchmark-specific attributes
        self.properties = {
            "name": self.name
        }
        
        if self.description:
            self.properties["description"] = self.description
        
        if self.tasks:
            self.properties["tasks"] = self.tasks
        
        if self.metrics:
            self.properties["metrics"] = self.metrics
        
        if self.dataset:
            self.properties["dataset"] = self.dataset
        
        if self.leaderboard:
            self.properties["leaderboard"] = self.leaderboard
        
        if self.state_of_the_art:
            self.properties["state_of_the_art"] = self.state_of_the_art
        
        if self.citation:
            self.properties["citation"] = self.citation
        
        # Call the parent's post init
        super().__post_init__()


# AI-specific relationship types
@dataclass
class TrainedOn(GraphRelationship):
    """Relationship indicating that a model was trained on a dataset."""
    
    def __post_init__(self):
        """Initialize the relationship with TRAINED_ON type."""
        self.type = "TRAINED_ON"
        super().__post_init__()


@dataclass
class EvaluatedOn(GraphRelationship):
    """Relationship indicating that a model was evaluated on a benchmark."""
    
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the relationship with EVALUATED_ON type."""
        self.type = "EVALUATED_ON"
        
        # Add metrics to properties
        if self.metrics:
            self.properties["metrics"] = self.metrics
        
        super().__post_init__()


@dataclass
class Outperforms(GraphRelationship):
    """Relationship indicating that one model outperforms another."""
    
    metrics: Dict[str, float] = field(default_factory=dict)
    margin: Optional[float] = None
    
    def __post_init__(self):
        """Initialize the relationship with OUTPERFORMS type."""
        self.type = "OUTPERFORMS"
        
        # Add metrics and margin to properties
        if self.metrics:
            self.properties["metrics"] = self.metrics
        
        if self.margin is not None:
            self.properties["margin"] = self.margin
        
        super().__post_init__()


@dataclass
class BasedOn(GraphRelationship):
    """Relationship indicating that one entity is based on another."""
    
    def __post_init__(self):
        """Initialize the relationship with BASED_ON type."""
        self.type = "BASED_ON"
        super().__post_init__()


@dataclass
class Cites(GraphRelationship):
    """Relationship indicating that a paper cites another paper."""
    
    def __post_init__(self):
        """Initialize the relationship with CITES type."""
        self.type = "CITES"
        super().__post_init__()


@dataclass
class UsesAlgorithm(GraphRelationship):
    """Relationship indicating that a model uses an algorithm."""
    
    def __post_init__(self):
        """Initialize the relationship with USES_ALGORITHM type."""
        self.type = "USES_ALGORITHM"
        super().__post_init__()


@dataclass
class AppliedTo(GraphRelationship):
    """Relationship indicating that a model is applied to a task."""
    
    def __post_init__(self):
        """Initialize the relationship with APPLIED_TO type."""
        self.type = "APPLIED_TO"
        super().__post_init__()


@dataclass
class Introduces(GraphRelationship):
    """Relationship indicating that a paper introduces a model, algorithm, or other entity."""
    
    def __post_init__(self):
        """Initialize the relationship with INTRODUCES type."""
        self.type = "INTRODUCES"
        super().__post_init__()


@dataclass
class Contains(GraphRelationship):
    """Relationship indicating that one entity contains another."""
    
    def __post_init__(self):
        """Initialize the relationship with CONTAINS type."""
        self.type = "CONTAINS"
        super().__post_init__()


@dataclass
class HasMetric(GraphRelationship):
    """Relationship indicating that a benchmark uses a specific metric."""
    
    def __post_init__(self):
        """Initialize the relationship with HAS_METRIC type."""
        self.type = "HAS_METRIC"
        super().__post_init__()