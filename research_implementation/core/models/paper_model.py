"""
Paper Model for Research Implementation System.

This module provides data models for representing research papers and their components
in the Research Implementation System.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid


@dataclass
class Author:
    """Represents an author of a research paper."""
    
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None


@dataclass
class Citation:
    """Represents a citation in a research paper."""
    
    text: str
    reference_id: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None


@dataclass
class Figure:
    """Represents a figure in a research paper."""
    
    id: str
    caption: str
    image_path: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Table:
    """Represents a table in a research paper."""
    
    id: str
    caption: str
    content: Any  # Can be various formats depending on the table
    description: Optional[str] = None


@dataclass
class Section:
    """Represents a section in a research paper."""
    
    id: str
    title: str
    content: str
    subsections: List['Section'] = field(default_factory=list)
    figures: List[Figure] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)


@dataclass
class Algorithm:
    """Represents an algorithm description in a research paper."""
    
    id: str
    name: str
    description: str
    pseudocode: Optional[str] = None
    complexity: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    references: List[Citation] = field(default_factory=list)
    source_section: Optional[str] = None  # ID of the section containing the algorithm


@dataclass
class ModelArchitecture:
    """Represents a model architecture in a research paper."""
    
    id: str
    name: str
    description: str
    components: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    diagram: Optional[Figure] = None
    references: List[Citation] = field(default_factory=list)
    source_section: Optional[str] = None  # ID of the section containing the architecture


@dataclass
class Dataset:
    """Represents a dataset described in a research paper."""
    
    id: str
    name: str
    description: str
    source: Optional[str] = None
    size: Optional[str] = None
    format: Optional[str] = None
    features: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    references: List[Citation] = field(default_factory=list)
    source_section: Optional[str] = None  # ID of the section containing the dataset


@dataclass
class EvaluationMetric:
    """Represents an evaluation metric used in a research paper."""
    
    id: str
    name: str
    description: str
    formula: Optional[str] = None
    references: List[Citation] = field(default_factory=list)
    source_section: Optional[str] = None  # ID of the section containing the metric


@dataclass
class ExperimentalResult:
    """Represents an experimental result in a research paper."""
    
    id: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    comparison: Dict[str, Any] = field(default_factory=dict)
    tables: List[Table] = field(default_factory=list)
    figures: List[Figure] = field(default_factory=list)
    source_section: Optional[str] = None  # ID of the section containing the result


@dataclass
class Paper:
    """Represents a research paper in the Research Implementation System."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    abstract: str = ""
    authors: List[Author] = field(default_factory=list)
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    venue: Optional[str] = None
    url: Optional[str] = None
    pdf_path: Optional[str] = None
    sections: List[Section] = field(default_factory=list)
    algorithms: List[Algorithm] = field(default_factory=list)
    architectures: List[ModelArchitecture] = field(default_factory=list)
    datasets: List[Dataset] = field(default_factory=list)
    metrics: List[EvaluationMetric] = field(default_factory=list)
    results: List[ExperimentalResult] = field(default_factory=list)
    references: List[Citation] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    processed_date: datetime = field(default_factory=datetime.now)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the paper to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "abstract": self.abstract,
            "authors": [vars(author) for author in self.authors],
            "publication_date": self.publication_date,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "venue": self.venue,
            "url": self.url,
            "pdf_path": self.pdf_path,
            "sections": self._sections_to_dict(self.sections),
            "algorithms": [vars(algo) for algo in self.algorithms],
            "architectures": [vars(arch) for arch in self.architectures],
            "datasets": [vars(ds) for ds in self.datasets],
            "metrics": [vars(metric) for metric in self.metrics],
            "results": [vars(result) for result in self.results],
            "references": [vars(ref) for ref in self.references],
            "keywords": self.keywords,
            "processed_date": self.processed_date.isoformat(),
            "processing_metadata": self.processing_metadata
        }
    
    def to_json(self) -> str:
        """Convert the paper to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @staticmethod
    def _sections_to_dict(sections: List[Section]) -> List[Dict[str, Any]]:
        """Convert sections to dictionaries, handling recursive structure."""
        result = []
        for section in sections:
            section_dict = vars(section).copy()
            section_dict["subsections"] = Paper._sections_to_dict(section.subsections)
            section_dict["figures"] = [vars(fig) for fig in section.figures]
            section_dict["tables"] = [vars(table) for table in section.tables]
            section_dict["citations"] = [vars(citation) for citation in section.citations]
            result.append(section_dict)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        """Create a paper from a dictionary."""
        authors = [Author(**author_data) for author_data in data.get("authors", [])]
        
        # Process sections recursively
        sections = Paper._dict_to_sections(data.get("sections", []))
        
        # Process other lists
        algorithms = [Algorithm(**algo_data) for algo_data in data.get("algorithms", [])]
        architectures = [ModelArchitecture(**arch_data) for arch_data in data.get("architectures", [])]
        datasets = [Dataset(**ds_data) for ds_data in data.get("datasets", [])]
        metrics = [EvaluationMetric(**metric_data) for metric_data in data.get("metrics", [])]
        results = [ExperimentalResult(**result_data) for result_data in data.get("results", [])]
        references = [Citation(**ref_data) for ref_data in data.get("references", [])]
        
        # Process date
        processed_date = datetime.now()
        if "processed_date" in data:
            try:
                processed_date = datetime.fromisoformat(data["processed_date"])
            except ValueError:
                pass
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            abstract=data.get("abstract", ""),
            authors=authors,
            publication_date=data.get("publication_date"),
            doi=data.get("doi"),
            arxiv_id=data.get("arxiv_id"),
            venue=data.get("venue"),
            url=data.get("url"),
            pdf_path=data.get("pdf_path"),
            sections=sections,
            algorithms=algorithms,
            architectures=architectures,
            datasets=datasets,
            metrics=metrics,
            results=results,
            references=references,
            keywords=data.get("keywords", []),
            processed_date=processed_date,
            processing_metadata=data.get("processing_metadata", {})
        )
    
    @staticmethod
    def _dict_to_sections(sections_data: List[Dict[str, Any]]) -> List[Section]:
        """Convert section dictionaries to Section objects, handling recursive structure."""
        result = []
        for section_data in sections_data:
            # Process figures, tables, and citations
            figures = [Figure(**fig_data) for fig_data in section_data.get("figures", [])]
            tables = [Table(**table_data) for table_data in section_data.get("tables", [])]
            citations = [Citation(**citation_data) for citation_data in section_data.get("citations", [])]
            
            # Process subsections recursively
            subsections = Paper._dict_to_sections(section_data.get("subsections", []))
            
            # Create section
            section = Section(
                id=section_data.get("id", str(uuid.uuid4())),
                title=section_data.get("title", ""),
                content=section_data.get("content", ""),
                subsections=subsections,
                figures=figures,
                tables=tables,
                citations=citations
            )
            result.append(section)
        return result
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Paper':
        """Create a paper from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)