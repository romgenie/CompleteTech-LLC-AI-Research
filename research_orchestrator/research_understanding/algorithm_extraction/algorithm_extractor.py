"""
Algorithm Extractor module for identifying and extracting algorithms from research papers.

This module provides functionality to extract algorithm descriptions, pseudocode,
and implementation details from research papers.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
import re
import os
import json
from pathlib import Path

from ..paper_processing.paper_processor import StructuredPaper, PaperSection, PaperAlgorithm


@dataclass
class AlgorithmParameter:
    """
    Represents a parameter used in an algorithm.
    """
    name: str
    description: Optional[str] = None
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    is_required: bool = True


@dataclass
class AlgorithmVariable:
    """
    Represents a variable used in an algorithm.
    """
    name: str
    purpose: Optional[str] = None
    type_hint: Optional[str] = None
    initialization: Optional[str] = None


@dataclass
class AlgorithmSubroutine:
    """
    Represents a subroutine or function used within an algorithm.
    """
    name: str
    description: Optional[str] = None
    parameters: Optional[List[AlgorithmParameter]] = None
    returns: Optional[str] = None
    pseudocode: Optional[str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []


@dataclass
class ExtractedAlgorithm:
    """
    Comprehensive representation of an extracted algorithm with implementation details.
    """
    algorithm_id: str
    name: str
    description: str
    purpose: Optional[str] = None
    pseudocode: Optional[str] = None
    parameters: Optional[List[AlgorithmParameter]] = None
    variables: Optional[List[AlgorithmVariable]] = None
    subroutines: Optional[List[AlgorithmSubroutine]] = None
    complexity: Optional[Dict[str, str]] = None
    optimization_notes: Optional[str] = None
    implementation_notes: Optional[str] = None
    usage_examples: Optional[List[str]] = None
    limitations: Optional[str] = None
    alternative_approaches: Optional[List[str]] = None
    paper_section_references: Optional[List[str]] = None
    source_paper_id: Optional[str] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
        if self.variables is None:
            self.variables = []
        if self.subroutines is None:
            self.subroutines = []
        if self.usage_examples is None:
            self.usage_examples = []
        if self.alternative_approaches is None:
            self.alternative_approaches = []
        if self.paper_section_references is None:
            self.paper_section_references = []
            
    def to_paper_algorithm(self) -> PaperAlgorithm:
        """
        Convert to a simpler PaperAlgorithm representation.
        
        Returns:
            PaperAlgorithm object
        """
        return PaperAlgorithm(
            algorithm_id=self.algorithm_id,
            name=self.name,
            description=self.description,
            pseudocode=self.pseudocode,
            complexity=self.complexity,
            referenced_by=self.paper_section_references
        )
    
    @classmethod
    def from_paper_algorithm(cls, paper_algorithm: PaperAlgorithm, source_paper_id: Optional[str] = None) -> 'ExtractedAlgorithm':
        """
        Create an ExtractedAlgorithm from a PaperAlgorithm.
        
        Args:
            paper_algorithm: Source PaperAlgorithm object
            source_paper_id: ID of the source paper
            
        Returns:
            ExtractedAlgorithm object
        """
        return cls(
            algorithm_id=paper_algorithm.algorithm_id,
            name=paper_algorithm.name,
            description=paper_algorithm.description,
            pseudocode=paper_algorithm.pseudocode,
            complexity=paper_algorithm.complexity,
            paper_section_references=paper_algorithm.referenced_by,
            source_paper_id=source_paper_id
        )


class AlgorithmExtractor:
    """
    Main class for extracting algorithms and their implementation details from research papers.
    """
    
    def __init__(self, 
                 language_model_config: Optional[Dict] = None,
                 cache_dir: Optional[str] = None):
        """
        Initialize the AlgorithmExtractor.
        
        Args:
            language_model_config: Configuration for language models used in extraction
            cache_dir: Directory to cache extracted algorithms
        """
        self.language_model_config = language_model_config or {}
        self.cache_dir = cache_dir
        
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def extract_algorithms(self, 
                           paper: StructuredPaper, 
                           force_reextract: bool = False) -> List[ExtractedAlgorithm]:
        """
        Extract algorithms from a structured paper.
        
        Args:
            paper: StructuredPaper object containing the paper content
            force_reextract: If True, force re-extraction even if cached
            
        Returns:
            List of ExtractedAlgorithm objects
        """
        # Check cache first if appropriate
        if self.cache_dir and not force_reextract:
            cached_result = self._check_cache(paper.paper_id)
            if cached_result:
                return cached_result
        
        # Initialize extraction context
        extraction_context = {
            "paper": paper,
            "algorithms": [],
            "potential_algorithm_sections": [],
            "extracted_pseudocode": []
        }
        
        # Identify potential algorithm sections
        self._identify_algorithm_sections(extraction_context)
        
        # Extract algorithms from identified sections
        self._extract_from_algorithm_sections(extraction_context)
        
        # Identify algorithms from pseudocode blocks
        self._extract_from_pseudocode(extraction_context)
        
        # Identify algorithms from algorithmic language
        self._extract_from_algorithmic_language(extraction_context)
        
        # Consolidate and process extracted algorithms
        algorithms = self._process_extracted_algorithms(extraction_context)
        
        # Enrich algorithms with implementation details
        enriched_algorithms = self._enrich_algorithms(algorithms, paper)
        
        # Cache results if appropriate
        if self.cache_dir:
            self._cache_result(enriched_algorithms, paper.paper_id)
        
        return enriched_algorithms
    
    def extract_implementation_details(self, 
                                      algorithm: ExtractedAlgorithm, 
                                      paper: StructuredPaper) -> ExtractedAlgorithm:
        """
        Extract detailed implementation information for a specific algorithm.
        
        Args:
            algorithm: Algorithm to enrich with implementation details
            paper: Source paper containing the algorithm
            
        Returns:
            Enriched ExtractedAlgorithm with implementation details
        """
        # This method would analyze the paper more deeply to extract implementation
        # details for a specific algorithm.
        
        # Here we would use language models and rule-based approaches to identify:
        # - Parameters and their descriptions
        # - Variables and their purposes
        # - Subroutines and their functionality
        # - Optimization techniques
        # - Implementation notes and considerations
        
        # For this stub implementation, we'll just return the original algorithm
        return algorithm
    
    def _check_cache(self, paper_id: str) -> Optional[List[ExtractedAlgorithm]]:
        """
        Check if algorithms for this paper have been extracted and cached.
        
        Args:
            paper_id: ID of the paper
            
        Returns:
            List of ExtractedAlgorithm objects if cached, None otherwise
        """
        if not self.cache_dir:
            return None
        
        cache_path = Path(self.cache_dir) / f"{paper_id}_algorithms.json"
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                
                # Convert cached JSON back to ExtractedAlgorithm objects
                return self._json_to_algorithms(cached_data)
            except Exception:
                # If any error occurs, return None to reprocess
                return None
        
        return None
    
    def _cache_result(self, algorithms: List[ExtractedAlgorithm], paper_id: str) -> None:
        """
        Cache the extraction result.
        
        Args:
            algorithms: Extracted algorithms
            paper_id: ID of the source paper
        """
        if not self.cache_dir:
            return
        
        cache_path = Path(self.cache_dir) / f"{paper_id}_algorithms.json"
        
        # Convert ExtractedAlgorithm objects to JSON-serializable dict
        algorithms_data = self._algorithms_to_json(algorithms)
        
        with open(cache_path, 'w') as f:
            json.dump(algorithms_data, f, indent=2)
    
    def _identify_algorithm_sections(self, context: Dict) -> None:
        """
        Identify sections in the paper that likely contain algorithms.
        
        Args:
            context: Extraction context
        """
        paper = context["paper"]
        potential_sections = []
        
        # Simple heuristic: look for sections with "algorithm" in the title
        for section in self._flatten_sections(paper.sections):
            if any(kw in section.title.lower() for kw in ["algorithm", "method", "approach", "procedure"]):
                potential_sections.append(section)
        
        context["potential_algorithm_sections"] = potential_sections
    
    def _extract_from_algorithm_sections(self, context: Dict) -> None:
        """
        Extract algorithms from sections identified as containing algorithms.
        
        Args:
            context: Extraction context
        """
        # This would be implemented to parse algorithm sections and extract
        # algorithm descriptions, pseudocode, etc.
        # For now, we'll use a simple placeholder approach
        
        for section in context["potential_algorithm_sections"]:
            # Simple regex to detect potential algorithm names - this is just illustrative
            # A real implementation would use more sophisticated NLP techniques
            algorithm_matches = re.finditer(r"(?:Algorithm|We propose)(?:\s+\d+)?(?:\s*:)?\s+([A-Z][A-Za-z0-9_]+)", section.content)
            
            for match in algorithm_matches:
                algo_name = match.group(1)
                context["algorithms"].append({
                    "name": algo_name,
                    "section": section,
                    "match_context": section.content[max(0, match.start() - 100):min(len(section.content), match.end() + 500)]
                })
    
    def _extract_from_pseudocode(self, context: Dict) -> None:
        """
        Extract algorithms from pseudocode blocks in the paper.
        
        Args:
            context: Extraction context
        """
        # This would identify and extract pseudocode blocks using patterns
        # like "begin" and "end" or code formatting in the paper.
        # For now, just a placeholder
        
        # Simple regex to detect pseudocode blocks - just illustrative
        pseudocode_pattern = r"(?:(?:Pseudocode|Algorithm)(?:\s+\d+)?(?:\s*:)?[\s\S]*?begin)([\s\S]*?)(?:end|return)"
        
        for section in self._flatten_sections(context["paper"].sections):
            pseudocode_matches = re.finditer(pseudocode_pattern, section.content, re.IGNORECASE)
            
            for match in pseudocode_matches:
                pseudocode = match.group(1).strip()
                context["extracted_pseudocode"].append({
                    "pseudocode": pseudocode,
                    "section": section,
                    "context": section.content[max(0, match.start() - 100):min(len(section.content), match.end() + 100)]
                })
    
    def _extract_from_algorithmic_language(self, context: Dict) -> None:
        """
        Extract algorithms from algorithmic language in the paper.
        
        Args:
            context: Extraction context
        """
        # This would use NLP to identify algorithm descriptions from natural language
        # For now, just a placeholder
        pass
    
    def _process_extracted_algorithms(self, context: Dict) -> List[ExtractedAlgorithm]:
        """
        Process and consolidate extracted algorithm information.
        
        Args:
            context: Extraction context
            
        Returns:
            List of ExtractedAlgorithm objects
        """
        # This would combine information from different extraction methods,
        # eliminate duplicates, and create ExtractedAlgorithm objects.
        # For now, just a placeholder implementation
        
        result = []
        
        # Process algorithms found in algorithm sections
        for i, algo_info in enumerate(context["algorithms"]):
            algo_id = f"algo_{i+1}"
            section = algo_info["section"]
            
            # Try to find matching pseudocode
            pseudocode = None
            for pc_info in context["extracted_pseudocode"]:
                if pc_info["section"] == section:
                    pseudocode = pc_info["pseudocode"]
                    break
            
            # Create ExtractedAlgorithm
            result.append(ExtractedAlgorithm(
                algorithm_id=algo_id,
                name=algo_info["name"],
                description=algo_info["match_context"],
                pseudocode=pseudocode,
                source_paper_id=context["paper"].paper_id,
                paper_section_references=[section.title]
            ))
        
        # Process pseudocode blocks that didn't match algorithm sections
        for i, pc_info in enumerate(context["extracted_pseudocode"]):
            # Skip if this pseudocode was already used
            if any(algo.pseudocode == pc_info["pseudocode"] for algo in result):
                continue
            
            algo_id = f"algo_pc_{i+1}"
            
            # Try to extract a name from the context
            name_match = re.search(r"(?:Algorithm|We propose)(?:\s+\d+)?(?:\s*:)?\s+([A-Z][A-Za-z0-9_]+)", pc_info["context"])
            name = name_match.group(1) if name_match else f"Algorithm {i+1}"
            
            # Create ExtractedAlgorithm
            result.append(ExtractedAlgorithm(
                algorithm_id=algo_id,
                name=name,
                description=pc_info["context"],
                pseudocode=pc_info["pseudocode"],
                source_paper_id=context["paper"].paper_id,
                paper_section_references=[pc_info["section"].title]
            ))
        
        return result
    
    def _enrich_algorithms(self, algorithms: List[ExtractedAlgorithm], paper: StructuredPaper) -> List[ExtractedAlgorithm]:
        """
        Enrich algorithms with implementation details.
        
        Args:
            algorithms: Extracted algorithms
            paper: Source paper
            
        Returns:
            Enriched algorithms
        """
        # This would analyze the algorithms and paper to extract implementation details
        # For now, just a placeholder that extracts complexity information
        
        for algo in algorithms:
            # Look for complexity information
            complexity_pattern = r"(?:time|space)(?:\s+)?complexity(?:\s+)?(?:is|of)(?:\s+)?([OΘΩo]\(?[^)]+\)?)"
            
            complexity = {}
            
            # Look in algorithm description
            time_matches = re.finditer(r"time(?:\s+)?complexity(?:\s+)?(?:is|of)(?:\s+)?([OΘΩo]\(?[^)]+\)?)", algo.description, re.IGNORECASE)
            space_matches = re.finditer(r"space(?:\s+)?complexity(?:\s+)?(?:is|of)(?:\s+)?([OΘΩo]\(?[^)]+\)?)", algo.description, re.IGNORECASE)
            
            for match in time_matches:
                complexity["time"] = match.group(1)
            
            for match in space_matches:
                complexity["space"] = match.group(1)
            
            if complexity:
                algo.complexity = complexity
        
        return algorithms
    
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
    
    def _algorithms_to_json(self, algorithms: List[ExtractedAlgorithm]) -> List[Dict]:
        """
        Convert ExtractedAlgorithm objects to JSON-serializable dicts.
        
        Args:
            algorithms: List of ExtractedAlgorithm objects
            
        Returns:
            List of JSON-serializable dictionaries
        """
        # This is a simplified implementation
        # A complete implementation would handle all nested objects
        result = []
        
        for algo in algorithms:
            result.append({
                "algorithm_id": algo.algorithm_id,
                "name": algo.name,
                "description": algo.description,
                "purpose": algo.purpose,
                "pseudocode": algo.pseudocode,
                "complexity": algo.complexity,
                "optimization_notes": algo.optimization_notes,
                "implementation_notes": algo.implementation_notes,
                "limitations": algo.limitations,
                "source_paper_id": algo.source_paper_id,
                "paper_section_references": algo.paper_section_references,
                # Other fields would be converted as well
            })
        
        return result
    
    def _json_to_algorithms(self, data: List[Dict]) -> List[ExtractedAlgorithm]:
        """
        Convert JSON data back to ExtractedAlgorithm objects.
        
        Args:
            data: List of JSON data
            
        Returns:
            List of ExtractedAlgorithm objects
        """
        # This is a simplified implementation
        # A complete implementation would recreate all nested objects
        result = []
        
        for item in data:
            algo = ExtractedAlgorithm(
                algorithm_id=item.get("algorithm_id", ""),
                name=item.get("name", ""),
                description=item.get("description", ""),
                purpose=item.get("purpose"),
                pseudocode=item.get("pseudocode"),
                complexity=item.get("complexity"),
                optimization_notes=item.get("optimization_notes"),
                implementation_notes=item.get("implementation_notes"),
                limitations=item.get("limitations"),
                source_paper_id=item.get("source_paper_id"),
                paper_section_references=item.get("paper_section_references", [])
            )
            result.append(algo)
        
        return result


class PseudocodeParser:
    """
    Parser for extracting structured information from algorithm pseudocode.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the pseudocode parser.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def parse_pseudocode(self, pseudocode: str) -> Dict:
        """
        Parse pseudocode into structured information.
        
        Args:
            pseudocode: Pseudocode string
            
        Returns:
            Dictionary with structured information
        """
        # This would parse pseudocode to extract inputs, outputs, variables, etc.
        # For now just a placeholder implementation
        
        result = {
            "parameters": [],
            "variables": [],
            "subroutines": [],
            "main_logic": pseudocode
        }
        
        # Extract input parameters
        param_matches = re.finditer(r"(?:Input|Parameters):?\s+([^\\n]+)", pseudocode)
        for match in param_matches:
            param_text = match.group(1)
            for param in param_text.split(','):
                param = param.strip()
                if param:
                    result["parameters"].append({"name": param})
        
        # Extract variables (this is highly simplified)
        var_pattern = r"(?:let|set)\s+([a-zA-Z][a-zA-Z0-9_]*)\s*(?:=|←|:=)\s*([^\\n;]+)"
        var_matches = re.finditer(var_pattern, pseudocode)
        for match in var_matches:
            var_name = match.group(1)
            initialization = match.group(2)
            result["variables"].append({
                "name": var_name,
                "initialization": initialization
            })
        
        return result


class AlgorithmImplementationGenerator:
    """
    Generator for creating actual code implementations from algorithm descriptions.
    """
    
    def __init__(self, 
                 language_model_config: Optional[Dict] = None,
                 template_dir: Optional[str] = None):
        """
        Initialize the implementation generator.
        
        Args:
            language_model_config: Configuration for language models
            template_dir: Directory containing code templates
        """
        self.language_model_config = language_model_config or {}
        self.template_dir = template_dir
    
    def generate_implementation(self, 
                               algorithm: ExtractedAlgorithm, 
                               language: str = "python", 
                               include_comments: bool = True) -> str:
        """
        Generate code implementation of an algorithm.
        
        Args:
            algorithm: Algorithm to implement
            language: Target programming language
            include_comments: Whether to include detailed comments
            
        Returns:
            Code implementation as string
        """
        # This would generate actual code from algorithm description
        # For now just a placeholder implementation
        
        if language.lower() == "python":
            return self._generate_python_implementation(algorithm, include_comments)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _generate_python_implementation(self, algorithm: ExtractedAlgorithm, include_comments: bool) -> str:
        """
        Generate Python implementation of an algorithm.
        
        Args:
            algorithm: Algorithm to implement
            include_comments: Whether to include detailed comments
            
        Returns:
            Python code as string
        """
        # This is a placeholder implementation
        # A real implementation would analyze the algorithm and generate actual code
        
        lines = []
        
        # Add header comment
        if include_comments:
            lines.append(f"# {algorithm.name}")
            lines.append("#")
            lines.append(f"# {algorithm.description[:100]}..." if len(algorithm.description) > 100 else f"# {algorithm.description}")
            if algorithm.complexity:
                for complexity_type, complexity_value in algorithm.complexity.items():
                    lines.append(f"# {complexity_type.capitalize()} complexity: {complexity_value}")
            lines.append("")
        
        # Create function signature
        params = []
        if algorithm.parameters:
            for param in algorithm.parameters:
                param_str = param.name
                if param.type_hint:
                    param_str = f"{param.name}: {param.type_hint}"
                if not param.is_required and param.default_value is not None:
                    param_str = f"{param_str} = {param.default_value}"
                params.append(param_str)
        
        lines.append(f"def {algorithm.name.lower().replace(' ', '_')}({', '.join(params)}):")
        
        # Add docstring
        if include_comments:
            lines.append(f'    """')
            lines.append(f"    {algorithm.name}")
            lines.append("")
            if algorithm.description:
                # Wrap description at 70 chars and indent
                import textwrap
                wrapped = textwrap.wrap(algorithm.description, width=70)
                for line in wrapped:
                    lines.append(f"    {line}")
                lines.append("")
            
            # Parameters
            if algorithm.parameters:
                lines.append("    Args:")
                for param in algorithm.parameters:
                    lines.append(f"        {param.name}: {param.description or 'No description'}")
                lines.append("")
            
            # Return value
            lines.append("    Returns:")
            lines.append("        Implementation result")
            
            lines.append('    """')
        
        # Add placeholder implementation or try to convert pseudocode
        if algorithm.pseudocode:
            # Simple conversion of pseudocode to Python comments
            pseudocode_lines = algorithm.pseudocode.split('\n')
            lines.append("    # Implementation based on pseudocode:")
            for pc_line in pseudocode_lines:
                lines.append(f"    # {pc_line}")
            lines.append("")
            lines.append("    # TODO: Implement this algorithm")
            lines.append("    pass")
        else:
            lines.append("    # TODO: Implement this algorithm")
            lines.append("    pass")
        
        return "\n".join(lines)