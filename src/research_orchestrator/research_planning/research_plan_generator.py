"""
Research plan generation module for the Research Orchestration Framework.

This module generates structured research plans based on query analysis.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from research_orchestrator.core.utils import load_config
from research_orchestrator.research_planning.query_analyzer import QueryAnalysis, QueryAnalyzer


class Section:
    """
    Represents a section in a research plan.
    
    Attributes:
        title: Section title
        description: Section description
        subsections: List of subsections
        query: Specific query for this section
        scope: Scope parameters for information gathering
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        query: str,
        subsections: Optional[List[Dict[str, Any]]] = None,
        scope: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a section.
        
        Args:
            title: Section title
            description: Section description
            query: Specific query for this section
            subsections: List of subsections (optional)
            scope: Scope parameters for information gathering (optional)
        """
        self.title = title
        self.description = description
        self.query = query
        self.subsections = subsections or []
        self.scope = scope or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the section
        """
        return {
            "title": self.title,
            "description": self.description,
            "query": self.query,
            "subsections": self.subsections,
            "scope": self.scope,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Section":
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation of a section
            
        Returns:
            Section instance
        """
        return cls(
            title=data["title"],
            description=data["description"],
            query=data["query"],
            subsections=data.get("subsections", []),
            scope=data.get("scope", {}),
        )


class ResearchPlan:
    """
    Represents a complete research plan.
    
    Attributes:
        title: Research plan title
        description: Research plan description
        sections: List of sections
        estimated_time: Estimated time to complete (minutes)
        format: Output format
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        sections: Optional[Dict[str, Section]] = None,
        estimated_time: Optional[int] = None,
        format: str = "markdown",
    ):
        """
        Initialize a research plan.
        
        Args:
            title: Research plan title
            description: Research plan description
            sections: Dictionary of sections (ID -> Section)
            estimated_time: Estimated time to complete (minutes)
            format: Output format
        """
        self.title = title
        self.description = description
        self.sections = sections or {}
        self.estimated_time = estimated_time
        self.format = format
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the research plan
        """
        sections_dict = {
            section_id: section.to_dict() for section_id, section in self.sections.items()
        }
        
        return {
            "title": self.title,
            "description": self.description,
            "sections": sections_dict,
            "estimated_time": self.estimated_time,
            "format": self.format,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchPlan":
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation of a research plan
            
        Returns:
            ResearchPlan instance
        """
        sections = {}
        for section_id, section_data in data.get("sections", {}).items():
            sections[section_id] = Section.from_dict(section_data)
        
        return cls(
            title=data["title"],
            description=data["description"],
            sections=sections,
            estimated_time=data.get("estimated_time"),
            format=data.get("format", "markdown"),
        )
    
    def add_section(self, section_id: str, section: Section) -> None:
        """
        Add a section to the research plan.
        
        Args:
            section_id: Section identifier
            section: Section to add
        """
        self.sections[section_id] = section


class ResearchPlanGenerator:
    """
    Generates structured research plans based on query analysis.
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize the research plan generator.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Load configuration
        if config_path:
            self.config = load_config(config_path)
        else:
            self.config = {}
        
        # Initialize query analyzer
        self.query_analyzer = QueryAnalyzer(self.config.get("query_analyzer", {}))
        
        # Load templates
        self.templates = self._load_templates()
        
        logger.debug("Initialized ResearchPlanGenerator")
    
    def generate_plan(
        self, query: str, depth: str = "standard", focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a research plan based on a query.
        
        Args:
            query: Research query
            depth: Research depth ("quick", "standard", "comprehensive")
            focus_areas: Specific areas to focus on (optional)
            
        Returns:
            Research plan as a dictionary
        """
        logger.info(f"Generating research plan for query: {query}")
        
        # Analyze the query
        analysis = self.query_analyzer.analyze(query)
        
        # Validate depth
        valid_depths = ["quick", "standard", "comprehensive"]
        if depth not in valid_depths:
            logger.warning(f"Invalid depth '{depth}', using '{analysis.complexity}'")
            depth = analysis.complexity
        
        # Create research plan
        plan = self._create_plan(analysis, depth, focus_areas or [])
        
        logger.debug(f"Generated research plan: {plan.title}")
        return plan.to_dict()
    
    def _create_plan(
        self, analysis: QueryAnalysis, depth: str, focus_areas: List[str]
    ) -> ResearchPlan:
        """
        Create a research plan based on query analysis.
        
        Args:
            analysis: Query analysis
            depth: Research depth
            focus_areas: Specific areas to focus on
            
        Returns:
            ResearchPlan instance
        """
        # Generate title and description
        title = f"Research Plan: {analysis.query}"
        description = f"A {depth} research plan covering {', '.join(analysis.topics)}"
        
        # Create plan
        plan = ResearchPlan(title=title, description=description)
        
        # Generate sections based on domain and depth
        sections = self._generate_sections(analysis, depth, focus_areas)
        
        # Add sections to plan
        for section_id, section in sections.items():
            plan.add_section(section_id, section)
        
        # Estimate time
        plan.estimated_time = self._estimate_time(plan, depth)
        
        return plan
    
    def _generate_sections(
        self, analysis: QueryAnalysis, depth: str, focus_areas: List[str]
    ) -> Dict[str, Section]:
        """
        Generate sections for the research plan.
        
        Args:
            analysis: Query analysis
            depth: Research depth
            focus_areas: Specific areas to focus on
            
        Returns:
            Dictionary of sections (ID -> Section)
        """
        # Get template based on domain and depth
        template_key = f"{analysis.domain}_{depth}"
        if template_key not in self.templates:
            template_key = f"default_{depth}"
        
        template = self.templates.get(template_key, self.templates.get("default_standard", {}))
        
        # Create sections
        sections = {}
        
        # Add introduction section
        intro_section = Section(
            title="Introduction",
            description="An overview of the research topic and key concepts",
            query=analysis.query,
            scope={"depth": "overview", "focus": "background"},
        )
        sections["introduction"] = intro_section
        
        # Add template sections
        for i, section_template in enumerate(template.get("sections", [])):
            section_id = f"section_{i+1}"
            
            # Check if this section is in focus areas
            is_focused = not focus_areas or any(
                focus.lower() in section_template["title"].lower() for focus in focus_areas
            )
            
            if is_focused:
                # Customize query for this section
                section_query = f"{analysis.query} {section_template.get('query_suffix', '')}"
                
                section = Section(
                    title=section_template["title"],
                    description=section_template["description"],
                    query=section_query,
                    subsections=section_template.get("subsections", []),
                    scope=section_template.get("scope", {}),
                )
                
                sections[section_id] = section
        
        # Add conclusion section
        conclusion_section = Section(
            title="Conclusion",
            description="Summary of findings and future directions",
            query=f"conclude {analysis.query}",
            scope={"depth": "synthesis", "focus": "summary"},
        )
        sections["conclusion"] = conclusion_section
        
        return sections
    
    def _estimate_time(self, plan: ResearchPlan, depth: str) -> int:
        """
        Estimate the time required to complete the research plan.
        
        Args:
            plan: Research plan
            depth: Research depth
            
        Returns:
            Estimated time in minutes
        """
        # Base time per section
        base_times = {
            "quick": 15,
            "standard": 30,
            "comprehensive": 60,
        }
        
        base_time = base_times.get(depth, 30)
        
        # Calculate total time
        total_time = 0
        for section_id, section in plan.sections.items():
            # Add base time for each section
            section_time = base_time
            
            # Add time for subsections
            section_time += len(section.subsections) * (base_time / 2)
            
            total_time += section_time
        
        return total_time
    
    def _load_templates(self) -> Dict[str, Any]:
        """
        Load research plan templates.
        
        Returns:
            Dictionary of templates
        """
        # Define template paths
        template_paths = [
            Path("templates/research_plans"),
            Path(__file__).parent / "templates",
        ]
        
        templates = {}
        
        # Try to load templates from paths
        for path in template_paths:
            if path.exists() and path.is_dir():
                for template_file in path.glob("*.json"):
                    try:
                        with open(template_file, "r") as f:
                            template_data = json.load(f)
                            template_id = template_file.stem
                            templates[template_id] = template_data
                    except Exception as e:
                        logger.warning(f"Error loading template {template_file}: {e}")
        
        # If no templates found, use default templates
        if not templates:
            templates = self._get_default_templates()
        
        return templates
    
    def _get_default_templates(self) -> Dict[str, Any]:
        """
        Get default research plan templates.
        
        Returns:
            Dictionary of default templates
        """
        return {
            "default_quick": {
                "sections": [
                    {
                        "title": "Key Concepts",
                        "description": "Overview of the main concepts and terminology",
                        "query_suffix": "key concepts and terminology",
                        "scope": {"depth": "overview", "focus": "concepts"},
                    },
                    {
                        "title": "Current State",
                        "description": "Summary of the current state of research",
                        "query_suffix": "current state and recent developments",
                        "scope": {"depth": "overview", "focus": "current"},
                    },
                ],
            },
            "default_standard": {
                "sections": [
                    {
                        "title": "Background and Concepts",
                        "description": "Overview of the main concepts and terminology",
                        "query_suffix": "background and key concepts",
                        "scope": {"depth": "detailed", "focus": "background"},
                        "subsections": [
                            {
                                "title": "Historical Context",
                                "description": "Brief history and evolution of the field",
                            },
                            {
                                "title": "Key Terminology",
                                "description": "Definitions of important terms and concepts",
                            },
                        ],
                    },
                    {
                        "title": "Current Approaches",
                        "description": "Analysis of current approaches and methodologies",
                        "query_suffix": "current approaches and methodologies",
                        "scope": {"depth": "detailed", "focus": "approaches"},
                        "subsections": [
                            {
                                "title": "Leading Methods",
                                "description": "Overview of the leading methods and techniques",
                            },
                            {
                                "title": "Comparative Analysis",
                                "description": "Comparison of different approaches",
                            },
                        ],
                    },
                    {
                        "title": "Challenges and Limitations",
                        "description": "Discussion of challenges and limitations",
                        "query_suffix": "challenges, limitations, and open problems",
                        "scope": {"depth": "detailed", "focus": "challenges"},
                    },
                    {
                        "title": "Future Directions",
                        "description": "Analysis of future research directions",
                        "query_suffix": "future directions and emerging trends",
                        "scope": {"depth": "detailed", "focus": "future"},
                    },
                ],
            },
            "default_comprehensive": {
                "sections": [
                    {
                        "title": "Historical Context and Evolution",
                        "description": "Detailed history and evolution of the field",
                        "query_suffix": "historical context and evolution",
                        "scope": {"depth": "comprehensive", "focus": "history"},
                        "subsections": [
                            {
                                "title": "Origins and Early Developments",
                                "description": "Early history and foundational work",
                            },
                            {
                                "title": "Major Milestones",
                                "description": "Key breakthroughs and advancements",
                            },
                            {
                                "title": "Paradigm Shifts",
                                "description": "Major changes in approach or understanding",
                            },
                        ],
                    },
                    {
                        "title": "Theoretical Foundations",
                        "description": "Detailed analysis of theoretical foundations",
                        "query_suffix": "theoretical foundations and principles",
                        "scope": {"depth": "comprehensive", "focus": "theory"},
                        "subsections": [
                            {
                                "title": "Core Principles",
                                "description": "Fundamental principles and assumptions",
                            },
                            {
                                "title": "Mathematical Framework",
                                "description": "Mathematical models and formalisms",
                            },
                            {
                                "title": "Theoretical Limitations",
                                "description": "Inherent limitations and constraints",
                            },
                        ],
                    },
                    {
                        "title": "Current State of the Art",
                        "description": "Comprehensive analysis of current approaches",
                        "query_suffix": "current state of the art approaches",
                        "scope": {"depth": "comprehensive", "focus": "current"},
                        "subsections": [
                            {
                                "title": "Leading Approaches",
                                "description": "Detailed analysis of leading approaches",
                            },
                            {
                                "title": "Comparative Analysis",
                                "description": "In-depth comparison of different methods",
                            },
                            {
                                "title": "Performance Benchmarks",
                                "description": "Benchmark results and performance metrics",
                            },
                            {
                                "title": "Implementation Strategies",
                                "description": "Practical implementation considerations",
                            },
                        ],
                    },
                    {
                        "title": "Applications and Use Cases",
                        "description": "Analysis of applications and use cases",
                        "query_suffix": "applications and real-world use cases",
                        "scope": {"depth": "comprehensive", "focus": "applications"},
                        "subsections": [
                            {
                                "title": "Industry Applications",
                                "description": "Applications in industry and business",
                            },
                            {
                                "title": "Research Applications",
                                "description": "Applications in research and academia",
                            },
                            {
                                "title": "Case Studies",
                                "description": "Detailed case studies of successful implementations",
                            },
                        ],
                    },
                    {
                        "title": "Challenges and Open Problems",
                        "description": "Comprehensive analysis of challenges and open problems",
                        "query_suffix": "challenges, open problems, and research gaps",
                        "scope": {"depth": "comprehensive", "focus": "challenges"},
                        "subsections": [
                            {
                                "title": "Technical Challenges",
                                "description": "Technical and implementation challenges",
                            },
                            {
                                "title": "Theoretical Challenges",
                                "description": "Theoretical and conceptual challenges",
                            },
                            {
                                "title": "Ethical and Societal Issues",
                                "description": "Ethical, social, and policy implications",
                            },
                        ],
                    },
                    {
                        "title": "Future Research Directions",
                        "description": "In-depth analysis of future research directions",
                        "query_suffix": "future research directions and emerging trends",
                        "scope": {"depth": "comprehensive", "focus": "future"},
                        "subsections": [
                            {
                                "title": "Emerging Approaches",
                                "description": "Promising new approaches and methodologies",
                            },
                            {
                                "title": "Long-term Research Agenda",
                                "description": "Long-term research goals and objectives",
                            },
                            {
                                "title": "Cross-disciplinary Opportunities",
                                "description": "Opportunities for cross-disciplinary research",
                            },
                        ],
                    },
                ],
            },
            "ai_standard": {
                "sections": [
                    {
                        "title": "AI Fundamentals",
                        "description": "Overview of fundamental AI concepts",
                        "query_suffix": "fundamental AI concepts related to",
                        "scope": {"depth": "detailed", "focus": "fundamentals"},
                    },
                    {
                        "title": "Current AI Approaches",
                        "description": "Analysis of current AI approaches",
                        "query_suffix": "current AI approaches for",
                        "scope": {"depth": "detailed", "focus": "approaches"},
                    },
                    {
                        "title": "AI Models and Architectures",
                        "description": "Overview of AI models and architectures",
                        "query_suffix": "AI models and architectures for",
                        "scope": {"depth": "detailed", "focus": "models"},
                    },
                    {
                        "title": "AI Applications",
                        "description": "Analysis of AI applications",
                        "query_suffix": "AI applications in",
                        "scope": {"depth": "detailed", "focus": "applications"},
                    },
                    {
                        "title": "AI Challenges and Limitations",
                        "description": "Discussion of AI challenges and limitations",
                        "query_suffix": "AI challenges and limitations in",
                        "scope": {"depth": "detailed", "focus": "challenges"},
                    },
                    {
                        "title": "Future of AI",
                        "description": "Analysis of future AI directions",
                        "query_suffix": "future directions for AI in",
                        "scope": {"depth": "detailed", "focus": "future"},
                    },
                ],
            },
            "nlp_standard": {
                "sections": [
                    {
                        "title": "NLP Fundamentals",
                        "description": "Overview of fundamental NLP concepts",
                        "query_suffix": "fundamental NLP concepts related to",
                        "scope": {"depth": "detailed", "focus": "fundamentals"},
                    },
                    {
                        "title": "Language Models",
                        "description": "Analysis of language models",
                        "query_suffix": "language models for",
                        "scope": {"depth": "detailed", "focus": "models"},
                    },
                    {
                        "title": "NLP Architectures",
                        "description": "Overview of NLP architectures",
                        "query_suffix": "NLP architectures for",
                        "scope": {"depth": "detailed", "focus": "architectures"},
                    },
                    {
                        "title": "NLP Tasks and Applications",
                        "description": "Analysis of NLP tasks and applications",
                        "query_suffix": "NLP tasks and applications in",
                        "scope": {"depth": "detailed", "focus": "applications"},
                    },
                    {
                        "title": "NLP Challenges and Limitations",
                        "description": "Discussion of NLP challenges and limitations",
                        "query_suffix": "NLP challenges and limitations in",
                        "scope": {"depth": "detailed", "focus": "challenges"},
                    },
                ],
            },
            "cv_standard": {
                "sections": [
                    {
                        "title": "Computer Vision Fundamentals",
                        "description": "Overview of fundamental computer vision concepts",
                        "query_suffix": "fundamental computer vision concepts related to",
                        "scope": {"depth": "detailed", "focus": "fundamentals"},
                    },
                    {
                        "title": "Vision Models",
                        "description": "Analysis of computer vision models",
                        "query_suffix": "computer vision models for",
                        "scope": {"depth": "detailed", "focus": "models"},
                    },
                    {
                        "title": "Vision Tasks",
                        "description": "Overview of computer vision tasks",
                        "query_suffix": "computer vision tasks in",
                        "scope": {"depth": "detailed", "focus": "tasks"},
                        "subsections": [
                            {
                                "title": "Object Detection",
                                "description": "Object detection approaches and methods",
                            },
                            {
                                "title": "Segmentation",
                                "description": "Image segmentation approaches and methods",
                            },
                            {
                                "title": "Recognition",
                                "description": "Recognition and classification approaches",
                            },
                        ],
                    },
                    {
                        "title": "Vision Applications",
                        "description": "Analysis of computer vision applications",
                        "query_suffix": "computer vision applications in",
                        "scope": {"depth": "detailed", "focus": "applications"},
                    },
                    {
                        "title": "Computer Vision Challenges",
                        "description": "Discussion of computer vision challenges",
                        "query_suffix": "computer vision challenges in",
                        "scope": {"depth": "detailed", "focus": "challenges"},
                    },
                ],
            },
        }