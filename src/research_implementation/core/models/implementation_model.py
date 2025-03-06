"""
Implementation Model for Research Implementation System.

This module provides data models for representing implementations of research papers
in the Research Implementation System.
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

from src.research_implementation.core.models.paper_model import Paper


@dataclass
class CodeFile:
    """Represents a code file in an implementation."""
    
    id: str
    filename: str
    content: str
    language: str
    purpose: str
    source_algorithm: Optional[str] = None  # ID of the algorithm this file implements
    dependencies: List[str] = field(default_factory=list)  # IDs of other code files
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dependency:
    """Represents a dependency for an implementation."""
    
    name: str
    version: str
    source: str
    purpose: str
    installation_command: Optional[str] = None


@dataclass
class DataResource:
    """Represents a data resource used in an implementation."""
    
    id: str
    name: str
    description: str
    source: str
    format: str
    path: Optional[str] = None
    size: Optional[str] = None
    preprocessing_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Experiment:
    """Represents an experiment in an implementation."""
    
    id: str
    name: str
    description: str
    setup: Dict[str, Any]
    parameters: Dict[str, Any]
    metrics: List[str]
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "planned"  # planned, running, completed, failed
    run_command: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    logs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Represents a verification result for an implementation."""
    
    id: str
    description: str
    paper_result: Any
    implementation_result: Any
    comparison: Dict[str, Any]
    is_verified: bool
    notes: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Implementation:
    """Represents an implementation of a research paper in the Research Implementation System."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    paper: Optional[Paper] = None
    paper_path: Optional[str] = None
    status: str = "created"  # created, understood, planned, implemented, evaluated, verified, error
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Understanding
    algorithms: List[Dict[str, Any]] = field(default_factory=list)
    architectures: List[Dict[str, Any]] = field(default_factory=list)
    implementation_details: Dict[str, Any] = field(default_factory=dict)
    evaluation_methodology: Dict[str, Any] = field(default_factory=dict)
    
    # Planning
    plan: Dict[str, Any] = field(default_factory=dict)
    
    # Implementation
    code_files: List[CodeFile] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    data_resources: List[DataResource] = field(default_factory=list)
    entry_points: Dict[str, str] = field(default_factory=dict)
    
    # Evaluation
    experiments: List[Experiment] = field(default_factory=list)
    
    # Verification
    verification_results: List[VerificationResult] = field(default_factory=list)
    overall_verification: Dict[str, Any] = field(default_factory=dict)
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the implementation to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "paper": self.paper.to_dict() if self.paper else None,
            "paper_path": self.paper_path,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            
            # Understanding
            "algorithms": self.algorithms,
            "architectures": self.architectures,
            "implementation_details": self.implementation_details,
            "evaluation_methodology": self.evaluation_methodology,
            
            # Planning
            "plan": self.plan,
            
            # Implementation
            "code_files": [vars(cf) for cf in self.code_files],
            "dependencies": [vars(dep) for dep in self.dependencies],
            "data_resources": [vars(dr) for dr in self.data_resources],
            "entry_points": self.entry_points,
            
            # Evaluation
            "experiments": [self._experiment_to_dict(exp) for exp in self.experiments],
            
            # Verification
            "verification_results": [vars(vr) for vr in self.verification_results],
            "overall_verification": self.overall_verification,
            
            # Additional metadata
            "tags": self.tags,
            "notes": self.notes,
            "metadata": self.metadata
        }
    
    @staticmethod
    def _experiment_to_dict(experiment: Experiment) -> Dict[str, Any]:
        """Convert an experiment to a dictionary, handling datetime fields."""
        exp_dict = vars(experiment).copy()
        if experiment.start_time:
            exp_dict["start_time"] = experiment.start_time.isoformat()
        if experiment.end_time:
            exp_dict["end_time"] = experiment.end_time.isoformat()
        return exp_dict
    
    def to_json(self) -> str:
        """Convert the implementation to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Implementation':
        """Create an implementation from a dictionary."""
        # Process paper
        paper = None
        if data.get("paper"):
            from src.research_implementation.core.models.paper_model import Paper
            paper = Paper.from_dict(data["paper"])
        
        # Process created_at and updated_at
        created_at = datetime.now()
        if "created_at" in data:
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except ValueError:
                pass
        
        updated_at = datetime.now()
        if "updated_at" in data:
            try:
                updated_at = datetime.fromisoformat(data["updated_at"])
            except ValueError:
                pass
        
        # Process code files
        code_files = [CodeFile(**cf_data) for cf_data in data.get("code_files", [])]
        
        # Process dependencies
        dependencies = [Dependency(**dep_data) for dep_data in data.get("dependencies", [])]
        
        # Process data resources
        data_resources = [DataResource(**dr_data) for dr_data in data.get("data_resources", [])]
        
        # Process experiments
        experiments = []
        for exp_data in data.get("experiments", []):
            exp_data_copy = exp_data.copy()
            
            # Process datetime fields
            if "start_time" in exp_data_copy and exp_data_copy["start_time"]:
                try:
                    exp_data_copy["start_time"] = datetime.fromisoformat(exp_data_copy["start_time"])
                except ValueError:
                    exp_data_copy["start_time"] = None
            
            if "end_time" in exp_data_copy and exp_data_copy["end_time"]:
                try:
                    exp_data_copy["end_time"] = datetime.fromisoformat(exp_data_copy["end_time"])
                except ValueError:
                    exp_data_copy["end_time"] = None
            
            experiments.append(Experiment(**exp_data_copy))
        
        # Process verification results
        verification_results = [VerificationResult(**vr_data) for vr_data in data.get("verification_results", [])]
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            paper=paper,
            paper_path=data.get("paper_path"),
            status=data.get("status", "created"),
            created_at=created_at,
            updated_at=updated_at,
            
            # Understanding
            algorithms=data.get("algorithms", []),
            architectures=data.get("architectures", []),
            implementation_details=data.get("implementation_details", {}),
            evaluation_methodology=data.get("evaluation_methodology", {}),
            
            # Planning
            plan=data.get("plan", {}),
            
            # Implementation
            code_files=code_files,
            dependencies=dependencies,
            data_resources=data_resources,
            entry_points=data.get("entry_points", {}),
            
            # Evaluation
            experiments=experiments,
            
            # Verification
            verification_results=verification_results,
            overall_verification=data.get("overall_verification", {}),
            
            # Additional metadata
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Implementation':
        """Create an implementation from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)