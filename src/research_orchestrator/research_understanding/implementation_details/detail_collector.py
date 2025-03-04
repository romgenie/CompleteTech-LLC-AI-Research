"""
Implementation Detail Collector module.

This module provides functionality to extract detailed implementation information
from research papers to facilitate accurate code generation.
"""

from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
import re
import os
import json
import logging
from pathlib import Path

from ..paper_processing.paper_processor import StructuredPaper, PaperSection
from ..algorithm_extraction.algorithm_extractor import ExtractedAlgorithm, AlgorithmParameter, AlgorithmSubroutine

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class CodeSnippet:
    """
    Represents a code snippet found in a research paper.
    """
    snippet_id: str
    language: str
    code: str
    description: Optional[str] = None
    line_numbers: Optional[bool] = False
    is_pseudocode: bool = False
    source_section: Optional[str] = None
    related_algorithm: Optional[str] = None


@dataclass
class ImplementationRequirement:
    """
    Represents a specific requirement for implementing an algorithm.
    """
    requirement_id: str
    description: str
    priority: str = "medium"  # "low", "medium", "high", "critical"
    type: str = "functional"  # "functional", "performance", "accuracy", "other"
    source_section: Optional[str] = None
    related_algorithm: Optional[str] = None


@dataclass
class DatasetInfo:
    """
    Information about a dataset mentioned in a paper.
    """
    dataset_id: str
    name: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    format: Optional[str] = None
    size: Optional[str] = None
    features: Optional[List[str]] = None
    preprocessing: Optional[str] = None
    splits: Optional[Dict[str, Any]] = None
    source_section: Optional[str] = None


@dataclass
class EvaluationMetric:
    """
    Information about an evaluation metric used in a paper.
    """
    metric_id: str
    name: str
    description: Optional[str] = None
    formula: Optional[str] = None
    range: Optional[Tuple[float, float]] = None
    higher_is_better: Optional[bool] = None
    source_section: Optional[str] = None


@dataclass
class HyperparameterInfo:
    """
    Information about a hyperparameter mentioned in a paper.
    """
    param_id: str
    name: str
    description: Optional[str] = None
    data_type: Optional[str] = None
    default_value: Optional[Any] = None
    range: Optional[Any] = None
    tuning_strategy: Optional[str] = None
    impact: Optional[str] = None
    source_section: Optional[str] = None
    related_algorithm: Optional[str] = None


@dataclass
class EnvironmentInfo:
    """
    Information about the computing environment used in a paper.
    """
    hardware: Optional[Dict[str, Any]] = None
    software: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    setup_instructions: Optional[str] = None
    source_section: Optional[str] = None


@dataclass
class ImplementationDetail:
    """
    Comprehensive collection of implementation details extracted from a paper.
    """
    paper_id: str
    algorithms: List[ExtractedAlgorithm] = field(default_factory=list)
    code_snippets: List[CodeSnippet] = field(default_factory=list)
    requirements: List[ImplementationRequirement] = field(default_factory=list)
    datasets: List[DatasetInfo] = field(default_factory=list)
    metrics: List[EvaluationMetric] = field(default_factory=list)
    hyperparameters: List[HyperparameterInfo] = field(default_factory=list)
    environment: Optional[EnvironmentInfo] = None
    libraries_used: List[str] = field(default_factory=list)
    references_to_existing_implementations: List[Dict[str, Any]] = field(default_factory=list)
    notes: Optional[str] = None


class ImplementationDetailCollector:
    """
    Main class for collecting detailed implementation information from research papers.
    
    This class extracts fine-grained details needed for accurate code generation,
    including code snippets, implementation requirements, datasets, evaluation metrics,
    hyperparameters, and environment information.
    """
    
    def __init__(self,
                 language_model_config: Optional[Dict] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the Implementation Detail Collector.
        
        Args:
            language_model_config: Configuration for language models used in extraction
            cache_dir: Directory to cache extracted implementation details
        """
        self.language_model_config = language_model_config or {}
        self.cache_dir = cache_dir
        
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def collect_details(self,
                       paper: StructuredPaper,
                       algorithms: Optional[List[ExtractedAlgorithm]] = None,
                       force_recollect: bool = False) -> ImplementationDetail:
        """
        Collect implementation details from a research paper.
        
        Args:
            paper: Structured paper to analyze
            algorithms: Pre-extracted algorithms (will be extracted if None)
            force_recollect: If True, force re-collection even if cached
            
        Returns:
            ImplementationDetail object containing all extracted information
        """
        # Check cache first if appropriate
        if self.cache_dir and not force_recollect:
            cached_result = self._check_cache(paper.paper_id)
            if cached_result:
                return cached_result
        
        # Initialize collector context
        collector_context = {
            "paper": paper,
            "algorithms": algorithms or [],
            "code_snippets": [],
            "requirements": [],
            "datasets": [],
            "metrics": [],
            "hyperparameters": [],
            "environment": None,
            "libraries_used": set(),
            "references_to_existing_implementations": []
        }
        
        # Extract different types of implementation details
        self._collect_code_snippets(collector_context)
        self._collect_requirements(collector_context)
        self._collect_datasets(collector_context)
        self._collect_metrics(collector_context)
        self._collect_hyperparameters(collector_context)
        self._collect_environment_info(collector_context)
        self._collect_libraries_used(collector_context)
        self._collect_implementation_references(collector_context)
        
        # Create implementation detail object
        details = ImplementationDetail(
            paper_id=paper.paper_id,
            algorithms=collector_context["algorithms"],
            code_snippets=collector_context["code_snippets"],
            requirements=collector_context["requirements"],
            datasets=collector_context["datasets"],
            metrics=collector_context["metrics"],
            hyperparameters=collector_context["hyperparameters"],
            environment=collector_context["environment"],
            libraries_used=list(collector_context["libraries_used"]),
            references_to_existing_implementations=collector_context["references_to_existing_implementations"]
        )
        
        # Cache results if appropriate
        if self.cache_dir:
            self._cache_result(details, paper.paper_id)
        
        return details
    
    def enhance_algorithm(self,
                         algorithm: ExtractedAlgorithm,
                         paper: StructuredPaper) -> ExtractedAlgorithm:
        """
        Enhance an algorithm with additional implementation details.
        
        Args:
            algorithm: Algorithm to enhance
            paper: Source paper
            
        Returns:
            Enhanced algorithm with more implementation details
        """
        # This is a simplified implementation for the example
        
        # Collect full details first to get context
        details = self.collect_details(paper, [algorithm])
        
        # Find algorithm-specific information
        related_snippets = [s for s in details.code_snippets 
                           if s.related_algorithm == algorithm.algorithm_id]
        
        related_requirements = [r for r in details.requirements 
                               if r.related_algorithm == algorithm.algorithm_id]
        
        related_hyperparams = [h for h in details.hyperparameters 
                              if h.related_algorithm == algorithm.algorithm_id]
        
        # Extract parameters from code snippets and requirements
        if not algorithm.parameters:
            algorithm.parameters = []
            
        self._extract_parameters_from_snippets(algorithm, related_snippets)
        
        # Extract subroutines from code snippets
        if not algorithm.subroutines:
            algorithm.subroutines = []
            
        self._extract_subroutines_from_snippets(algorithm, related_snippets)
        
        # Add implementation notes based on requirements
        if related_requirements:
            notes = "Implementation requirements:\n"
            for req in related_requirements:
                notes += f"- {req.description} (Priority: {req.priority})\n"
            
            if algorithm.implementation_notes:
                algorithm.implementation_notes += "\n\n" + notes
            else:
                algorithm.implementation_notes = notes
        
        # Add hyperparameter information
        if related_hyperparams:
            hyperparams_note = "Hyperparameters:\n"
            for param in related_hyperparams:
                default_str = f", default: {param.default_value}" if param.default_value is not None else ""
                range_str = f", range: {param.range}" if param.range is not None else ""
                hyperparams_note += f"- {param.name}: {param.description}{default_str}{range_str}\n"
            
            if algorithm.implementation_notes:
                algorithm.implementation_notes += "\n\n" + hyperparams_note
            else:
                algorithm.implementation_notes = hyperparams_note
        
        return algorithm
    
    def _check_cache(self, paper_id: str) -> Optional[ImplementationDetail]:
        """
        Check if implementation details for this paper have been collected and cached.
        
        Args:
            paper_id: ID of the paper
            
        Returns:
            ImplementationDetail object if cached, None otherwise
        """
        if not self.cache_dir:
            return None
        
        cache_path = Path(self.cache_dir) / f"{paper_id}_implementation_details.json"
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                
                # Convert cached JSON back to ImplementationDetail object
                return self._json_to_implementation_detail(cached_data)
            except Exception as e:
                logger.warning(f"Error loading cache: {e}")
                return None
        
        return None
    
    def _cache_result(self, details: ImplementationDetail, paper_id: str) -> None:
        """
        Cache the collection result.
        
        Args:
            details: Implementation details
            paper_id: ID of the source paper
        """
        if not self.cache_dir:
            return
        
        cache_path = Path(self.cache_dir) / f"{paper_id}_implementation_details.json"
        
        # Convert ImplementationDetail object to JSON-serializable dict
        details_data = self._implementation_detail_to_json(details)
        
        with open(cache_path, 'w') as f:
            json.dump(details_data, f, indent=2)
    
    def _collect_code_snippets(self, context: Dict) -> None:
        """
        Collect code snippets from the paper.
        
        Args:
            context: Collector context
        """
        paper = context["paper"]
        snippets = []
        
        # Look for code blocks in paper sections
        for i, section in enumerate(self._flatten_sections(paper.sections)):
            # Simple heuristic to detect code blocks - this is just illustrative
            # A real implementation would use more sophisticated detection methods
            
            # Look for code blocks marked with common programming language indicators
            code_pattern = r"```(python|java|c\+\+|javascript|r|julia)?(.*?)```"
            code_matches = re.finditer(code_pattern, section.content, re.DOTALL)
            
            for j, match in enumerate(code_matches):
                language = match.group(1) or "unknown"
                code = match.group(2).strip()
                
                # Skip if it's too short to be meaningful code
                if len(code.split('\n')) < 2:
                    continue
                
                snippet_id = f"snippet_{i}_{j}"
                
                # Try to determine if it's related to an algorithm
                related_algorithm = None
                for algo in context["algorithms"]:
                    if algo.name.lower() in code.lower() or algo.name.lower() in section.title.lower():
                        related_algorithm = algo.algorithm_id
                        break
                
                snippets.append(CodeSnippet(
                    snippet_id=snippet_id,
                    language=language,
                    code=code,
                    source_section=section.title,
                    related_algorithm=related_algorithm
                ))
            
            # Also look for indented code blocks (common in papers)
            indented_code_pattern = r"(?:^|\n)( {4,}|\t+)(.+)(?:\n\1.+)+"
            indented_matches = re.finditer(indented_code_pattern, section.content)
            
            for j, match in enumerate(indented_matches):
                indent = match.group(1)
                lines = [line[len(indent):] for line in match.group(0).split('\n') if line.startswith(indent)]
                code = '\n'.join(lines)
                
                # Skip if it's too short
                if len(lines) < 2:
                    continue
                
                # Try to guess the language
                language = "unknown"
                if "def " in code and ":" in code:
                    language = "python"
                elif "{" in code and "}" in code and ";" in code:
                    language = "c-like"
                
                snippet_id = f"snippet_indented_{i}_{j}"
                
                # Try to determine if it's related to an algorithm
                related_algorithm = None
                for algo in context["algorithms"]:
                    if algo.name.lower() in code.lower() or algo.name.lower() in section.title.lower():
                        related_algorithm = algo.algorithm_id
                        break
                
                snippets.append(CodeSnippet(
                    snippet_id=snippet_id,
                    language=language,
                    code=code,
                    source_section=section.title,
                    related_algorithm=related_algorithm
                ))
        
        context["code_snippets"] = snippets
    
    def _collect_requirements(self, context: Dict) -> None:
        """
        Collect implementation requirements from the paper.
        
        Args:
            context: Collector context
        """
        paper = context["paper"]
        requirements = []
        
        # Look for requirement-related content in paper
        for i, section in enumerate(self._flatten_sections(paper.sections)):
            # Look for sections that might contain requirements
            if any(kw in section.title.lower() for kw in ["implementation", "requirement", "constraint", "approach"]):
                # Extract potential requirements using simple NLP patterns (simplified for example)
                # Real implementation would use more sophisticated NLP
                
                # Look for statements like "must", "should", "needs to", etc.
                requirement_patterns = [
                    r"(?:must|should|need to|has to|requires) ([^\.\n]+)",
                    r"(?:important|essential|critical|necessary) (?:to|that) ([^\.\n]+)",
                    r"(?:constraint|requirement) (?:is|:) ([^\.\n]+)"
                ]
                
                req_id_counter = 0
                for pattern in requirement_patterns:
                    matches = re.finditer(pattern, section.content, re.IGNORECASE)
                    for match in matches:
                        req_text = match.group(1).strip()
                        
                        # Skip if too short
                        if len(req_text) < 10:
                            continue
                        
                        # Determine priority
                        priority = "medium"
                        if any(kw in match.group(0).lower() for kw in ["critical", "essential", "must", "crucial"]):
                            priority = "high"
                        elif any(kw in match.group(0).lower() for kw in ["ideally", "preferably", "can", "could"]):
                            priority = "low"
                        
                        # Determine type
                        req_type = "functional"
                        if any(kw in req_text.lower() for kw in ["fast", "speed", "efficient", "complexity", "time", "memory"]):
                            req_type = "performance"
                        elif any(kw in req_text.lower() for kw in ["accuracy", "precision", "recall", "score", "metric"]):
                            req_type = "accuracy"
                        
                        # Try to determine if it's related to an algorithm
                        related_algorithm = None
                        for algo in context["algorithms"]:
                            if algo.name.lower() in req_text.lower() or algo.name.lower() in section.title.lower():
                                related_algorithm = algo.algorithm_id
                                break
                        
                        req_id = f"req_{i}_{req_id_counter}"
                        req_id_counter += 1
                        
                        requirements.append(ImplementationRequirement(
                            requirement_id=req_id,
                            description=req_text,
                            priority=priority,
                            type=req_type,
                            source_section=section.title,
                            related_algorithm=related_algorithm
                        ))
        
        context["requirements"] = requirements
    
    def _collect_datasets(self, context: Dict) -> None:
        """
        Collect dataset information from the paper.
        
        Args:
            context: Collector context
        """
        paper = context["paper"]
        datasets = []
        
        # Look for dataset-related content in paper
        for i, section in enumerate(self._flatten_sections(paper.sections)):
            # Focus on sections that typically describe datasets
            if any(kw in section.title.lower() for kw in ["dataset", "data", "experiment", "evaluation"]):
                # Look for dataset names using simple patterns
                # A real implementation would use more sophisticated NLP
                
                # Common dataset name patterns
                dataset_patterns = [
                    r"dataset (?:called|named) ([A-Z][A-Za-z0-9\-]+)",
                    r"([A-Z][A-Za-z0-9\-]+) dataset",
                    r"experiments (?:on|with) (?:the )?([A-Z][A-Za-z0-9\-]+)"
                ]
                
                for pattern in dataset_patterns:
                    matches = re.finditer(pattern, section.content)
                    for match in matches:
                        dataset_name = match.group(1).strip()
                        
                        # Skip common English words that might be false positives
                        if dataset_name.lower() in ["this", "that", "these", "those", "our", "their"]:
                            continue
                        
                        # Skip if we already found this dataset
                        if any(d.name == dataset_name for d in datasets):
                            continue
                        
                        # Try to extract description - simplified approach
                        description = None
                        desc_match = re.search(
                            r"{}.*?(?:which|that|is|contains|consists of) ([^\.]+)".format(re.escape(dataset_name)), 
                            section.content
                        )
                        if desc_match:
                            description = desc_match.group(1).strip()
                        
                        dataset_id = f"dataset_{i}_{len(datasets)}"
                        
                        datasets.append(DatasetInfo(
                            dataset_id=dataset_id,
                            name=dataset_name,
                            description=description,
                            source_section=section.title
                        ))
        
        context["datasets"] = datasets
    
    def _collect_metrics(self, context: Dict) -> None:
        """
        Collect evaluation metrics from the paper.
        
        Args:
            context: Collector context
        """
        paper = context["paper"]
        metrics = []
        
        # Look for metrics-related content in paper
        for i, section in enumerate(self._flatten_sections(paper.sections)):
            # Focus on sections that typically describe evaluation
            if any(kw in section.title.lower() for kw in ["evaluat", "metric", "result", "performance", "experiment"]):
                # Look for common metric names
                common_metrics = [
                    "accuracy", "precision", "recall", "f1 score", "mse", "rmse", "mae", "auc",
                    "map", "bleu", "rouge", "perplexity", "psnr", "ssim", "iou", "ap"
                ]
                
                for metric in common_metrics:
                    # Check if the metric is mentioned
                    metric_pattern = r"(?:{})\b".format(re.escape(metric))
                    if re.search(metric_pattern, section.content, re.IGNORECASE):
                        # Extract description if available
                        description = None
                        desc_pattern = r"(?:{})[^\.\n]*(?:is|as|which is|defined as)[^\.\n]+".format(re.escape(metric))
                        desc_match = re.search(desc_pattern, section.content, re.IGNORECASE)
                        if desc_match:
                            description = desc_match.group(0).strip()
                        
                        # Check if higher is better is mentioned
                        higher_is_better = None
                        if re.search(r"(?:{})[^\.\n]*?(?:higher|larger|greater)[^\.\n]+(?:better|preferred|desired)".format(re.escape(metric)), 
                                     section.content, 
                                     re.IGNORECASE):
                            higher_is_better = True
                        elif re.search(r"(?:{})[^\.\n]*?(?:lower|smaller|lesser)[^\.\n]+(?:better|preferred|desired)".format(re.escape(metric)), 
                                      section.content, 
                                      re.IGNORECASE):
                            higher_is_better = False
                        
                        metric_id = f"metric_{metric.replace(' ', '_')}"
                        
                        # Skip if we already added this metric
                        if any(m.metric_id == metric_id for m in metrics):
                            continue
                        
                        metrics.append(EvaluationMetric(
                            metric_id=metric_id,
                            name=metric,
                            description=description,
                            higher_is_better=higher_is_better,
                            source_section=section.title
                        ))
        
        context["metrics"] = metrics
    
    def _collect_hyperparameters(self, context: Dict) -> None:
        """
        Collect hyperparameter information from the paper.
        
        Args:
            context: Collector context
        """
        paper = context["paper"]
        hyperparams = []
        
        # Look for hyperparameter-related content in paper
        for i, section in enumerate(self._flatten_sections(paper.sections)):
            # Focus on sections that typically describe hyperparameters
            if any(kw in section.title.lower() for kw in ["parameter", "hyperparameter", "setting", "configuration", "setup", "experiment"]):
                # Look for hyperparameter specifications
                # This is a simplified approach - real implementation would use more sophisticated NLP
                
                # Common patterns for hyperparameter descriptions
                hyperparam_patterns = [
                    r"(?:set|used|chose|selected|tuned) (?:the )?([a-zA-Z][a-zA-Z0-9\s]*) (?:to|as) ([0-9\.]+)",
                    r"([a-zA-Z][a-zA-Z0-9\s]*) (?:is|was|=) ([0-9\.]+)",
                    r"([a-zA-Z][a-zA-Z0-9\s]*) (?:in|of|from) \{([^\}]+)\}",
                    r"([a-zA-Z][a-zA-Z0-9\s]*) (?:in|of|from) \[([^\]]+)\]"
                ]
                
                for pattern in hyperparam_patterns:
                    matches = re.finditer(pattern, section.content)
                    for match in matches:
                        param_name = match.group(1).strip()
                        param_value = match.group(2).strip()
                        
                        # Skip common English words that might be false positives
                        if param_name.lower() in ["the", "a", "an", "this", "that", "these", "those"]:
                            continue
                        
                        # Determine data type and structure value
                        data_type = None
                        structured_value = None
                        
                        # If value is a number
                        if re.match(r"^[0-9]+(?:\.[0-9]+)?$", param_value):
                            if "." in param_value:
                                data_type = "float"
                                structured_value = float(param_value)
                            else:
                                data_type = "int"
                                structured_value = int(param_value)
                        # If value is a list/set
                        elif "," in param_value:
                            values = [v.strip() for v in param_value.split(",")]
                            
                            # Check if all values are numeric
                            if all(re.match(r"^[0-9]+(?:\.[0-9]+)?$", v) for v in values):
                                data_type = "numeric_list"
                                structured_value = [float(v) if "." in v else int(v) for v in values]
                            else:
                                data_type = "categorical"
                                structured_value = values
                        # If value is a range
                        elif "-" in param_value and len(param_value.split("-")) == 2:
                            parts = param_value.split("-")
                            if all(re.match(r"^[0-9]+(?:\.[0-9]+)?$", p.strip()) for p in parts):
                                data_type = "range"
                                structured_value = [
                                    float(parts[0].strip()) if "." in parts[0] else int(parts[0].strip()),
                                    float(parts[1].strip()) if "." in parts[1] else int(parts[1].strip())
                                ]
                        
                        # Try to determine if it's related to an algorithm
                        related_algorithm = None
                        for algo in context["algorithms"]:
                            if algo.name.lower() in param_name.lower() or algo.name.lower() in section.title.lower():
                                related_algorithm = algo.algorithm_id
                                break
                        
                        param_id = f"hyperparam_{param_name.replace(' ', '_').lower()}"
                        
                        # Skip if we already added this parameter with the same related algorithm
                        if any(h.param_id == param_id and h.related_algorithm == related_algorithm for h in hyperparams):
                            continue
                        
                        hyperparams.append(HyperparameterInfo(
                            param_id=param_id,
                            name=param_name,
                            data_type=data_type,
                            default_value=structured_value if data_type not in ["range", "numeric_list", "categorical"] else None,
                            range=structured_value if data_type in ["range", "numeric_list", "categorical"] else None,
                            source_section=section.title,
                            related_algorithm=related_algorithm
                        ))
        
        context["hyperparameters"] = hyperparams
    
    def _collect_environment_info(self, context: Dict) -> None:
        """
        Collect information about computing environment from the paper.
        
        Args:
            context: Collector context
        """
        paper = context["paper"]
        hardware = {}
        software = {}
        dependencies = []
        
        # Look for environment-related content in paper
        for section in self._flatten_sections(paper.sections):
            # Focus on sections that typically describe computing environment
            if any(kw in section.title.lower() for kw in ["experiment", "implementation", "setup", "environment", "hardware", "software"]):
                # Look for hardware information
                hw_patterns = {
                    "gpu": r"(?:used|ran on|performed on|executed on|implemented on)[^\.]*?([A-Z][A-Za-z0-9]* GPU|NVIDIA [A-Za-z0-9]+|AMD [A-Za-z0-9]+)",
                    "cpu": r"(?:used|ran on|performed on|executed on|implemented on)[^\.]*?([A-Z][A-Za-z0-9]* CPU|Intel [A-Za-z0-9]+|AMD [A-Za-z0-9]+)",
                    "ram": r"(?:with|using)[^\.]*?(\d+\s*(?:GB|MB|TB) (?:of )?(?:RAM|memory))"
                }
                
                for hw_type, pattern in hw_patterns.items():
                    match = re.search(pattern, section.content, re.IGNORECASE)
                    if match:
                        hardware[hw_type] = match.group(1).strip()
                
                # Look for software information
                sw_patterns = {
                    "os": r"(?:used|ran on|performed on|executed on|implemented on)[^\.]*?(Windows [^\.\,]+|Ubuntu [^\.\,]+|CentOS [^\.\,]+|macOS [^\.\,]+|Linux [^\.\,]+)",
                    "framework": r"(?:used|implemented in|implemented with|built with|built using)[^\.]*?(TensorFlow|PyTorch|Keras|scikit-learn|MXNet|JAX|Theano)[^\.\,]*"
                }
                
                for sw_type, pattern in sw_patterns.items():
                    match = re.search(pattern, section.content, re.IGNORECASE)
                    if match:
                        software[sw_type] = match.group(1).strip()
                
                # Look for dependencies/libraries
                lib_pattern = r"(?:used|using|utilizes|depends on|requires|built with)(?:[^\.]*?)(?:library|libraries|framework|package|packages|module|modules)[^\.]*?([A-Za-z0-9\-\, ]+)"
                match = re.search(lib_pattern, section.content, re.IGNORECASE)
                if match:
                    libs_text = match.group(1).strip()
                    libs = [lib.strip() for lib in re.split(r"[,\s]+and\s+|[,\s]+", libs_text) if lib.strip()]
                    dependencies.extend(libs)
        
        # Create environment info object if we found any information
        if hardware or software or dependencies:
            context["environment"] = EnvironmentInfo(
                hardware=hardware or None,
                software=software or None,
                dependencies=dependencies or None
            )
    
    def _collect_libraries_used(self, context: Dict) -> None:
        """
        Collect information about libraries used in the implementation.
        
        Args:
            context: Collector context
        """
        libraries = set()
        
        # Check code snippets for import statements
        for snippet in context["code_snippets"]:
            if snippet.language.lower() == "python":
                # Extract Python imports
                import_patterns = [
                    r"import\s+([a-zA-Z0-9_\.]+)",
                    r"from\s+([a-zA-Z0-9_\.]+)\s+import"
                ]
                
                for pattern in import_patterns:
                    matches = re.finditer(pattern, snippet.code)
                    for match in matches:
                        lib = match.group(1).strip()
                        # Get top-level package name
                        top_level = lib.split('.')[0]
                        libraries.add(top_level)
            
            elif "c++" in snippet.language.lower() or snippet.language.lower() == "c-like":
                # Extract C++ includes
                include_pattern = r"#include\s*[<\"]([a-zA-Z0-9_\.]+)[>\"]"
                matches = re.finditer(include_pattern, snippet.code)
                for match in matches:
                    lib = match.group(1).strip()
                    # Remove file extension if present
                    if "." in lib:
                        lib = lib.split('.')[0]
                    libraries.add(lib)
            
            elif snippet.language.lower() == "java":
                # Extract Java imports
                import_pattern = r"import\s+([a-zA-Z0-9_\.]+)(?:\.[a-zA-Z0-9_\*]+);"
                matches = re.finditer(import_pattern, snippet.code)
                for match in matches:
                    lib = match.group(1).strip()
                    # Extract top-level package
                    top_level = lib.split('.')[0]
                    libraries.add(top_level)
        
        # Also check if environment info has dependencies
        if context["environment"] and context["environment"].dependencies:
            libraries.update(context["environment"].dependencies)
        
        context["libraries_used"] = libraries
    
    def _collect_implementation_references(self, context: Dict) -> None:
        """
        Collect references to existing implementations mentioned in the paper.
        
        Args:
            context: Collector context
        """
        paper = context["paper"]
        references = []
        
        # Look for references to code or implementations
        for section in self._flatten_sections(paper.sections):
            # Look for common patterns that reference code
            code_ref_patterns = [
                r"code is available at[^\.\n]+([^\.\n]+)",
                r"implementation is available at[^\.\n]+([^\.\n]+)",
                r"code/implementation[^\.\n]+(?:at|from|in)[^\.\n]+([^\.\n]+)",
                r"(?:our|the) implementation[^\.\n]+(?:at|from|in)[^\.\n]+([^\.\n]+)",
                r"(?:our|the) code[^\.\n]+(?:at|from|in)[^\.\n]+([^\.\n]+)",
                r"publicly available[^\.\n]+(?:at|from|in)[^\.\n]+([^\.\n]+)",
                r"source code[^\.\n]+(?:at|from|in)[^\.\n]+([^\.\n]+)",
                r"github(?:\.\s*com)?[/:]([a-zA-Z0-9\-]+/[a-zA-Z0-9\-_\.]+)",
                r"(https?://(?:github|gitlab|bitbucket)\.com/[a-zA-Z0-9\-_\./]+)"
            ]
            
            for pattern in code_ref_patterns:
                matches = re.finditer(pattern, section.content, re.IGNORECASE)
                for match in matches:
                    ref_text = match.group(1).strip()
                    
                    # Basic cleaning
                    ref_text = ref_text.rstrip(".,:;'\"")
                    
                    # See if this is a URL
                    is_url = bool(re.match(r"https?://", ref_text, re.IGNORECASE))
                    
                    # Is it a GitHub reference?
                    is_github = "github" in ref_text.lower()
                    
                    # Try to determine if it's related to an algorithm
                    related_algorithm = None
                    for algo in context["algorithms"]:
                        if algo.name.lower() in section.content.lower():
                            related_algorithm = algo.algorithm_id
                            break
                    
                    references.append({
                        "reference": ref_text,
                        "type": "url" if is_url else "github" if is_github else "other",
                        "source_section": section.title,
                        "related_algorithm": related_algorithm
                    })
        
        context["references_to_existing_implementations"] = references
    
    def _extract_parameters_from_snippets(self, algorithm: ExtractedAlgorithm, snippets: List[CodeSnippet]) -> None:
        """
        Extract algorithm parameters from code snippets.
        
        Args:
            algorithm: Algorithm to enrich with parameters
            snippets: Code snippets related to the algorithm
        """
        if not snippets:
            return
        
        # Set of parameter names we've already found
        existing_param_names = {param.name for param in algorithm.parameters}
        
        for snippet in snippets:
            if snippet.language.lower() == "python":
                # Look for function definitions that might implement the algorithm
                func_pattern = r"def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)"
                matches = re.finditer(func_pattern, snippet.code)
                
                for match in matches:
                    func_name = match.group(1)
                    params_text = match.group(2)
                    
                    # Skip if the function doesn't seem related to the algorithm
                    name_similarity = self._name_similarity(func_name, algorithm.name)
                    if name_similarity < 0.5 and algorithm.name.lower() not in func_name.lower():
                        continue
                    
                    # Parse parameters
                    if params_text.strip():
                        params = [p.strip() for p in params_text.split(',')]
                        for param in params:
                            # Skip self parameter
                            if param.strip() == "self":
                                continue
                            
                            # Parse parameter with type hint and default value
                            param_parts = param.split('=')
                            param_name = param_parts[0].strip()
                            default_value = param_parts[1].strip() if len(param_parts) > 1 else None
                            
                            # Check for type hints
                            if ':' in param_name:
                                name_type_parts = param_name.split(':')
                                param_name = name_type_parts[0].strip()
                                type_hint = name_type_parts[1].strip()
                            else:
                                type_hint = None
                            
                            # Skip if we already have this parameter
                            if param_name in existing_param_names:
                                continue
                            
                            # Add the parameter
                            algorithm.parameters.append(AlgorithmParameter(
                                name=param_name,
                                type_hint=type_hint,
                                default_value=default_value,
                                is_required=default_value is None
                            ))
                            existing_param_names.add(param_name)
    
    def _extract_subroutines_from_snippets(self, algorithm: ExtractedAlgorithm, snippets: List[CodeSnippet]) -> None:
        """
        Extract algorithm subroutines from code snippets.
        
        Args:
            algorithm: Algorithm to enrich with subroutines
            snippets: Code snippets related to the algorithm
        """
        if not snippets:
            return
        
        # Set of subroutine names we've already found
        existing_subroutine_names = {sub.name for sub in algorithm.subroutines}
        
        for snippet in snippets:
            if snippet.language.lower() == "python":
                # Look for all function definitions
                func_pattern = r"def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->.*?)?\s*:"
                matches = re.finditer(func_pattern, snippet.code)
                
                main_func = None
                other_funcs = []
                
                # First pass: identify the main function and helper functions
                for match in matches:
                    func_name = match.group(1)
                    params_text = match.group(2)
                    
                    # Check if this might be the main algorithm function
                    name_similarity = self._name_similarity(func_name, algorithm.name)
                    if name_similarity > 0.5 or algorithm.name.lower() in func_name.lower():
                        main_func = func_name
                    else:
                        other_funcs.append(func_name)
                
                # Second pass: get helper functions (excluding the main one)
                if main_func:
                    for func_name in other_funcs:
                        # Skip if we already have this subroutine
                        if func_name in existing_subroutine_names:
                            continue
                        
                        # Extract the function body and parameters
                        func_pattern = r"def\s+{}[^\n]*\(([^)]*)\)(?:\s*->.*?)?\s*:(.*?)(?=\n\S|\Z)".format(
                            re.escape(func_name)
                        )
                        func_match = re.search(func_pattern, snippet.code, re.DOTALL)
                        
                        if func_match:
                            params_text = func_match.group(1)
                            body = func_match.group(2).strip()
                            
                            # Parse parameters
                            params = []
                            if params_text.strip():
                                param_list = [p.strip() for p in params_text.split(',')]
                                for param in param_list:
                                    # Skip self parameter
                                    if param.strip() == "self":
                                        continue
                                    
                                    # Parse parameter with type hint and default value
                                    param_parts = param.split('=')
                                    param_name = param_parts[0].strip()
                                    default_value = param_parts[1].strip() if len(param_parts) > 1 else None
                                    
                                    # Check for type hints
                                    if ':' in param_name:
                                        name_type_parts = param_name.split(':')
                                        param_name = name_type_parts[0].strip()
                                        type_hint = name_type_parts[1].strip()
                                    else:
                                        type_hint = None
                                    
                                    params.append(AlgorithmParameter(
                                        name=param_name,
                                        type_hint=type_hint,
                                        default_value=default_value,
                                        is_required=default_value is None
                                    ))
                            
                            # Try to extract a description from docstring
                            description = None
                            docstring_match = re.search(r'"""(.*?)"""', body, re.DOTALL)
                            if docstring_match:
                                description = docstring_match.group(1).strip()
                            
                            # Add the subroutine
                            algorithm.subroutines.append(AlgorithmSubroutine(
                                name=func_name,
                                description=description,
                                parameters=params,
                                pseudocode=body
                            ))
                            existing_subroutine_names.add(func_name)
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate a simple similarity score between two names.
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score between 0 and 1
        """
        # Convert to lowercase and remove non-alphanumeric characters
        name1 = re.sub(r'[^a-z0-9]', '', name1.lower())
        name2 = re.sub(r'[^a-z0-9]', '', name2.lower())
        
        # If either is empty after cleaning, return 0
        if not name1 or not name2:
            return 0
        
        # Check if one is a substring of the other
        if name1 in name2 or name2 in name1:
            return 0.8
        
        # Calculate Jaccard similarity of character sets
        set1 = set(name1)
        set2 = set(name2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0
        
        return intersection / union
    
    def _flatten_sections(self, sections: List[PaperSection]) -> List[PaperSection]:
        """
        Flatten a hierarchical section structure.
        
        Args:
            sections: Hierarchical section list
            
        Returns:
            Flattened section list
        """
        result = []
        
        for section in sections:
            result.append(section)
            if section.subsections:
                result.extend(self._flatten_sections(section.subsections))
        
        return result
    
    def _implementation_detail_to_json(self, details: ImplementationDetail) -> Dict:
        """
        Convert ImplementationDetail object to JSON-serializable dict.
        
        Args:
            details: ImplementationDetail object
            
        Returns:
            JSON-serializable dictionary
        """
        # This is a simplified implementation
        # A complete implementation would handle all nested objects
        return {
            "paper_id": details.paper_id,
            "algorithms": [], # Would convert algorithm data
            "code_snippets": [self._code_snippet_to_json(snippet) for snippet in details.code_snippets],
            "requirements": [self._requirement_to_json(req) for req in details.requirements],
            "datasets": [self._dataset_to_json(dataset) for dataset in details.datasets],
            "metrics": [self._metric_to_json(metric) for metric in details.metrics],
            "hyperparameters": [self._hyperparameter_to_json(param) for param in details.hyperparameters],
            "environment": self._environment_to_json(details.environment) if details.environment else None,
            "libraries_used": details.libraries_used,
            "references_to_existing_implementations": details.references_to_existing_implementations,
            "notes": details.notes
        }
    
    def _code_snippet_to_json(self, snippet: CodeSnippet) -> Dict:
        """Convert code snippet to JSON."""
        return {
            "snippet_id": snippet.snippet_id,
            "language": snippet.language,
            "code": snippet.code,
            "description": snippet.description,
            "line_numbers": snippet.line_numbers,
            "is_pseudocode": snippet.is_pseudocode,
            "source_section": snippet.source_section,
            "related_algorithm": snippet.related_algorithm
        }
    
    def _requirement_to_json(self, req: ImplementationRequirement) -> Dict:
        """Convert requirement to JSON."""
        return {
            "requirement_id": req.requirement_id,
            "description": req.description,
            "priority": req.priority,
            "type": req.type,
            "source_section": req.source_section,
            "related_algorithm": req.related_algorithm
        }
    
    def _dataset_to_json(self, dataset: DatasetInfo) -> Dict:
        """Convert dataset to JSON."""
        return {
            "dataset_id": dataset.dataset_id,
            "name": dataset.name,
            "description": dataset.description,
            "source_url": dataset.source_url,
            "format": dataset.format,
            "size": dataset.size,
            "features": dataset.features,
            "preprocessing": dataset.preprocessing,
            "splits": dataset.splits,
            "source_section": dataset.source_section
        }
    
    def _metric_to_json(self, metric: EvaluationMetric) -> Dict:
        """Convert metric to JSON."""
        return {
            "metric_id": metric.metric_id,
            "name": metric.name,
            "description": metric.description,
            "formula": metric.formula,
            "range": metric.range,
            "higher_is_better": metric.higher_is_better,
            "source_section": metric.source_section
        }
    
    def _hyperparameter_to_json(self, param: HyperparameterInfo) -> Dict:
        """Convert hyperparameter to JSON."""
        return {
            "param_id": param.param_id,
            "name": param.name,
            "description": param.description,
            "data_type": param.data_type,
            "default_value": param.default_value,
            "range": param.range,
            "tuning_strategy": param.tuning_strategy,
            "impact": param.impact,
            "source_section": param.source_section,
            "related_algorithm": param.related_algorithm
        }
    
    def _environment_to_json(self, env: EnvironmentInfo) -> Dict:
        """Convert environment to JSON."""
        return {
            "hardware": env.hardware,
            "software": env.software,
            "dependencies": env.dependencies,
            "setup_instructions": env.setup_instructions,
            "source_section": env.source_section
        }
    
    def _json_to_implementation_detail(self, data: Dict) -> ImplementationDetail:
        """
        Convert JSON data back to ImplementationDetail object.
        
        Args:
            data: JSON data
            
        Returns:
            ImplementationDetail object
        """
        # This is a simplified implementation
        # A complete implementation would handle all nested objects
        return ImplementationDetail(
            paper_id=data.get("paper_id", ""),
            algorithms=[],  # Would parse algorithm data
            code_snippets=[self._json_to_code_snippet(snippet) for snippet in data.get("code_snippets", [])],
            requirements=[self._json_to_requirement(req) for req in data.get("requirements", [])],
            datasets=[self._json_to_dataset(dataset) for dataset in data.get("datasets", [])],
            metrics=[self._json_to_metric(metric) for metric in data.get("metrics", [])],
            hyperparameters=[self._json_to_hyperparameter(param) for param in data.get("hyperparameters", [])],
            environment=self._json_to_environment(data.get("environment")) if data.get("environment") else None,
            libraries_used=data.get("libraries_used", []),
            references_to_existing_implementations=data.get("references_to_existing_implementations", []),
            notes=data.get("notes")
        )
    
    def _json_to_code_snippet(self, data: Dict) -> CodeSnippet:
        """Convert JSON to code snippet."""
        return CodeSnippet(
            snippet_id=data.get("snippet_id", ""),
            language=data.get("language", ""),
            code=data.get("code", ""),
            description=data.get("description"),
            line_numbers=data.get("line_numbers", False),
            is_pseudocode=data.get("is_pseudocode", False),
            source_section=data.get("source_section"),
            related_algorithm=data.get("related_algorithm")
        )
    
    def _json_to_requirement(self, data: Dict) -> ImplementationRequirement:
        """Convert JSON to requirement."""
        return ImplementationRequirement(
            requirement_id=data.get("requirement_id", ""),
            description=data.get("description", ""),
            priority=data.get("priority", "medium"),
            type=data.get("type", "functional"),
            source_section=data.get("source_section"),
            related_algorithm=data.get("related_algorithm")
        )
    
    def _json_to_dataset(self, data: Dict) -> DatasetInfo:
        """Convert JSON to dataset."""
        return DatasetInfo(
            dataset_id=data.get("dataset_id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            source_url=data.get("source_url"),
            format=data.get("format"),
            size=data.get("size"),
            features=data.get("features"),
            preprocessing=data.get("preprocessing"),
            splits=data.get("splits"),
            source_section=data.get("source_section")
        )
    
    def _json_to_metric(self, data: Dict) -> EvaluationMetric:
        """Convert JSON to metric."""
        return EvaluationMetric(
            metric_id=data.get("metric_id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            formula=data.get("formula"),
            range=data.get("range"),
            higher_is_better=data.get("higher_is_better"),
            source_section=data.get("source_section")
        )
    
    def _json_to_hyperparameter(self, data: Dict) -> HyperparameterInfo:
        """Convert JSON to hyperparameter."""
        return HyperparameterInfo(
            param_id=data.get("param_id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            data_type=data.get("data_type"),
            default_value=data.get("default_value"),
            range=data.get("range"),
            tuning_strategy=data.get("tuning_strategy"),
            impact=data.get("impact"),
            source_section=data.get("source_section"),
            related_algorithm=data.get("related_algorithm")
        )
    
    def _json_to_environment(self, data: Dict) -> Optional[EnvironmentInfo]:
        """Convert JSON to environment."""
        if not data:
            return None
        
        return EnvironmentInfo(
            hardware=data.get("hardware"),
            software=data.get("software"),
            dependencies=data.get("dependencies"),
            setup_instructions=data.get("setup_instructions"),
            source_section=data.get("source_section")
        )