"""
Content Synthesis Engine for Research Generation.

This module provides functionality for generating coherent text content for
research documents based on extracted knowledge and document structure.
"""

import logging
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Union, Tuple, Set
import json
import os
from pathlib import Path
import re
import random
import asyncio
from functools import lru_cache

from .report_structure import DocumentStructure, Section, SectionType, DocumentType
from .citation import CitationManager, CitationStyle
from .visualization import VisualizationGenerator, VisualizationType, ChartType, DiagramType

# Try to import LLM-related modules
try:
    from langchain.llms import BaseLLM
    from langchain.prompts import PromptTemplate
    from langchain.schema import AIMessage, HumanMessage, SystemMessage
    from langchain.chat_models import ChatAnthropic, ChatOpenAI
    from langchain.chains import LLMChain
    from langchain.callbacks import get_openai_callback
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentStyle(Enum):
    """Styles for content generation."""
    ACADEMIC = auto()       # Formal academic style
    TECHNICAL = auto()      # Technical documentation style
    EDUCATIONAL = auto()    # Educational/instructional style
    BUSINESS = auto()       # Business/professional style
    JOURNALISTIC = auto()   # News/journalistic style
    
    @classmethod
    def from_string(cls, value: str) -> 'ContentStyle':
        """Convert a string to a ContentStyle enum value.
        
        Args:
            value: String representation of content style
            
        Returns:
            Corresponding ContentStyle enum value or ACADEMIC if not found
        """
        try:
            return cls[value.upper()]
        except (KeyError, AttributeError):
            # Default to ACADEMIC if not found
            return cls.ACADEMIC


class TechnicalLevel(Enum):
    """Technical level of the content."""
    BEGINNER = auto()     # For beginners, minimal technical jargon
    INTERMEDIATE = auto() # For those with some knowledge
    ADVANCED = auto()     # For experts, can include complex technical details
    EXPERT = auto()       # For specialists, highly technical with domain expertise
    
    @classmethod
    def from_string(cls, value: str) -> 'TechnicalLevel':
        """Convert a string to a TechnicalLevel enum value.
        
        Args:
            value: String representation of technical level
            
        Returns:
            Corresponding TechnicalLevel enum value or INTERMEDIATE if not found
        """
        try:
            return cls[value.upper()]
        except (KeyError, AttributeError):
            # Default to INTERMEDIATE if not found
            return cls.INTERMEDIATE


class ContentGenerationConfig:
    """Configuration for content generation."""
    
    def __init__(self, 
                 style: Union[ContentStyle, str] = ContentStyle.ACADEMIC,
                 technical_level: Union[TechnicalLevel, str] = TechnicalLevel.INTERMEDIATE,
                 audience: str = "Academic",
                 max_section_length: int = 1000,
                 include_citations: bool = True,
                 include_figures: bool = True,
                 llm_model: Optional[str] = None,
                 template_dir: Optional[str] = None):
        """
        Initialize the content generation configuration.
        
        Args:
            style: Style for content generation
            technical_level: Technical level of the content
            audience: Target audience for the content
            max_section_length: Maximum length of a section in words
            include_citations: Whether to include citations
            include_figures: Whether to include figures
            llm_model: LLM model to use for generation
            template_dir: Directory containing content templates
        """
        # Convert string to enum if needed
        if isinstance(style, str):
            style = ContentStyle.from_string(style)
        if isinstance(technical_level, str):
            technical_level = TechnicalLevel.from_string(technical_level)
        
        self.style = style
        self.technical_level = technical_level
        self.audience = audience
        self.max_section_length = max_section_length
        self.include_citations = include_citations
        self.include_figures = include_figures
        self.llm_model = llm_model
        
        # Set template directory
        if template_dir:
            self.template_dir = template_dir
        else:
            # Use default templates directory
            self.template_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "templates",
                "content_templates"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary representation.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "style": self.style.name,
            "technical_level": self.technical_level.name,
            "audience": self.audience,
            "max_section_length": self.max_section_length,
            "include_citations": self.include_citations,
            "include_figures": self.include_figures,
            "llm_model": self.llm_model,
            "template_dir": self.template_dir
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentGenerationConfig':
        """
        Create a ContentGenerationConfig from a dictionary representation.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            ContentGenerationConfig object
        """
        return cls(
            style=data.get("style", ContentStyle.ACADEMIC),
            technical_level=data.get("technical_level", TechnicalLevel.INTERMEDIATE),
            audience=data.get("audience", "Academic"),
            max_section_length=data.get("max_section_length", 1000),
            include_citations=data.get("include_citations", True),
            include_figures=data.get("include_figures", True),
            llm_model=data.get("llm_model"),
            template_dir=data.get("template_dir")
        )


class ContentTemplate:
    """Content template for generating text."""
    
    def __init__(self, 
                 section_type: SectionType,
                 document_type: DocumentType,
                 template_text: str,
                 style: ContentStyle = ContentStyle.ACADEMIC,
                 technical_level: TechnicalLevel = TechnicalLevel.INTERMEDIATE,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a content template.
        
        Args:
            section_type: Type of section for this template
            document_type: Type of document for this template
            template_text: Template text with placeholders
            style: Style for this template
            technical_level: Technical level for this template
            metadata: Additional metadata for the template
        """
        self.section_type = section_type
        self.document_type = document_type
        self.template_text = template_text
        self.style = style
        self.technical_level = technical_level
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to a dictionary representation.
        
        Returns:
            Dictionary representation of the template
        """
        return {
            "section_type": self.section_type.name,
            "document_type": self.document_type.name,
            "template_text": self.template_text,
            "style": self.style.name,
            "technical_level": self.technical_level.name,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentTemplate':
        """
        Create a ContentTemplate from a dictionary representation.
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            ContentTemplate object
        """
        section_type = SectionType.from_string(data.get("section_type", "INTRODUCTION"))
        document_type = DocumentType.from_string(data.get("document_type", "RESEARCH_PAPER"))
        style = ContentStyle.from_string(data.get("style", "ACADEMIC"))
        technical_level = TechnicalLevel.from_string(data.get("technical_level", "INTERMEDIATE"))
        
        return cls(
            section_type=section_type,
            document_type=document_type,
            template_text=data.get("template_text", ""),
            style=style,
            technical_level=technical_level,
            metadata=data.get("metadata", {})
        )
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save template to a JSON file.
        
        Args:
            file_path: Path to save the file
        """
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ContentTemplate':
        """
        Load template from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            ContentTemplate object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


class ResearchData:
    """
    Research data for content generation, including knowledge extracted
    from papers, entities, and relationships.
    """
    
    def __init__(self, 
                 topic: str,
                 entities: Optional[List[Dict[str, Any]]] = None,
                 relationships: Optional[List[Dict[str, Any]]] = None,
                 papers: Optional[List[Dict[str, Any]]] = None,
                 facts: Optional[List[str]] = None,
                 statistics: Optional[Dict[str, Any]] = None,
                 figures: Optional[List[Dict[str, Any]]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize research data.
        
        Args:
            topic: Research topic
            entities: List of entities extracted from research
            relationships: List of relationships between entities
            papers: List of papers referenced in the research
            facts: List of extracted facts
            statistics: Statistics and numerical data
            figures: List of figures and visualizations
            metadata: Additional metadata
        """
        self.topic = topic
        self.entities = entities or []
        self.relationships = relationships or []
        self.papers = papers or []
        self.facts = facts or []
        self.statistics = statistics or {}
        self.figures = figures or []
        self.metadata = metadata or {}
    
    def get_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get entities of a specific type.
        
        Args:
            entity_type: Type of entities to retrieve
            
        Returns:
            List of entities of the specified type
        """
        return [entity for entity in self.entities if entity.get("type", "").lower() == entity_type.lower()]
    
    def get_relationships_by_type(self, relationship_type: str) -> List[Dict[str, Any]]:
        """
        Get relationships of a specific type.
        
        Args:
            relationship_type: Type of relationships to retrieve
            
        Returns:
            List of relationships of the specified type
        """
        return [rel for rel in self.relationships if rel.get("type", "").lower() == relationship_type.lower()]
    
    def get_papers_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Get papers containing a specific keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of papers containing the keyword
        """
        keyword_lower = keyword.lower()
        return [
            paper for paper in self.papers 
            if keyword_lower in paper.get("title", "").lower() 
            or keyword_lower in paper.get("abstract", "").lower()
        ]
    
    def get_facts_by_keyword(self, keyword: str) -> List[str]:
        """
        Get facts containing a specific keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of facts containing the keyword
        """
        keyword_lower = keyword.lower()
        return [fact for fact in self.facts if keyword_lower in fact.lower()]


class ContentSynthesisEngine:
    """
    Content Synthesis Engine for generating coherent text content for
    research documents based on extracted knowledge and document structure.
    """
    
    def __init__(self, 
                 config: Optional[ContentGenerationConfig] = None,
                 llm: Optional[Any] = None,
                 knowledge_graph_adapter = None,
                 citation_manager: Optional[CitationManager] = None,
                 citation_style: Union[CitationStyle, str] = CitationStyle.APA,
                 visualization_generator: Optional['VisualizationGenerator'] = None):
        """
        Initialize the Content Synthesis Engine.
        
        Args:
            config: Configuration for content generation
            llm: Language model to use for content generation (optional)
            knowledge_graph_adapter: Adapter for accessing knowledge graph (optional)
            citation_manager: Citation manager for handling citations (optional)
            citation_style: Citation style to use for formatting citations
            visualization_generator: Generator for creating visualizations (optional)
        """
        self.config = config or ContentGenerationConfig()
        self.logger = logging.getLogger(__name__)
        self.llm = llm
        self.knowledge_graph_adapter = knowledge_graph_adapter
        
        # Initialize citation manager
        if citation_manager:
            self.citation_manager = citation_manager
        else:
            self.citation_manager = CitationManager(
                style=citation_style,
                knowledge_graph_adapter=knowledge_graph_adapter
            )
            
        # Initialize visualization generator
        if visualization_generator:
            self.visualization_generator = visualization_generator
        else:
            self.visualization_generator = VisualizationGenerator(
                knowledge_graph_adapter=knowledge_graph_adapter
            )
        
        # Initialize default templates
        self._initialize_templates()
        
        # Initialize language model if not provided
        if self.llm is None and LANGCHAIN_AVAILABLE:
            self._initialize_llm()
    
    def _initialize_templates(self) -> None:
        """Initialize content templates."""
        os.makedirs(self.config.template_dir, exist_ok=True)
        
        # Create default templates if none exist
        if not os.listdir(self.config.template_dir):
            self._create_default_templates()
            
    def _initialize_llm(self) -> None:
        """Initialize language model for content generation."""
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain is not available. Content will be generated using templates only.")
            return
        
        try:
            # Default to OpenAI if no model is specified
            model_name = self.config.llm_model or "gpt-4"
            
            if "claude" in model_name.lower():
                self.llm = ChatAnthropic(model=model_name, temperature=0.7)
                self.logger.info(f"Initialized Claude model: {model_name}")
            else:
                self.llm = ChatOpenAI(model=model_name, temperature=0.7)
                self.logger.info(f"Initialized OpenAI model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize language model: {e}")
            self.logger.warning("Content will be generated using templates only.")
    
    def _create_default_templates(self) -> None:
        """Create default content templates."""
        # Create introduction template
        intro_template = ContentTemplate(
            section_type=SectionType.INTRODUCTION,
            document_type=DocumentType.RESEARCH_PAPER,
            template_text=self._get_introduction_template(),
            style=ContentStyle.ACADEMIC,
            technical_level=TechnicalLevel.INTERMEDIATE
        )
        intro_template.save_to_file(os.path.join(self.config.template_dir, "introduction_academic.json"))
        
        # Create methodology template
        method_template = ContentTemplate(
            section_type=SectionType.METHODOLOGY,
            document_type=DocumentType.RESEARCH_PAPER,
            template_text=self._get_methodology_template(),
            style=ContentStyle.ACADEMIC,
            technical_level=TechnicalLevel.INTERMEDIATE
        )
        method_template.save_to_file(os.path.join(self.config.template_dir, "methodology_academic.json"))
        
        # Create results template
        results_template = ContentTemplate(
            section_type=SectionType.RESULTS,
            document_type=DocumentType.RESEARCH_PAPER,
            template_text=self._get_results_template(),
            style=ContentStyle.ACADEMIC,
            technical_level=TechnicalLevel.INTERMEDIATE
        )
        results_template.save_to_file(os.path.join(self.config.template_dir, "results_academic.json"))
        
        # Create discussion template
        discussion_template = ContentTemplate(
            section_type=SectionType.DISCUSSION,
            document_type=DocumentType.RESEARCH_PAPER,
            template_text=self._get_discussion_template(),
            style=ContentStyle.ACADEMIC,
            technical_level=TechnicalLevel.INTERMEDIATE
        )
        discussion_template.save_to_file(os.path.join(self.config.template_dir, "discussion_academic.json"))
        
        # Create conclusion template
        conclusion_template = ContentTemplate(
            section_type=SectionType.CONCLUSION,
            document_type=DocumentType.RESEARCH_PAPER,
            template_text=self._get_conclusion_template(),
            style=ContentStyle.ACADEMIC,
            technical_level=TechnicalLevel.INTERMEDIATE
        )
        conclusion_template.save_to_file(os.path.join(self.config.template_dir, "conclusion_academic.json"))
        
        self.logger.info(f"Created default templates in {self.config.template_dir}")
    
    def _get_introduction_template(self) -> str:
        """Get template text for introduction section."""
        return """# Introduction

In recent years, {topic} has emerged as a crucial area of research in {field}. 
{background_context}

Despite significant progress in this domain, several challenges remain unresolved. 
{problem_statement}

This paper addresses these challenges by {proposed_approach}. 
Our work makes the following contributions:

{contributions}

The remainder of this paper is organized as follows. Section 2 discusses related work in {topic}. 
Section 3 describes our methodology. Section 4 presents the results of our experiments. 
Section 5 discusses the implications of our findings, and Section 6 concludes the paper with 
a summary of our contributions and directions for future work.
"""
    
    def _get_methodology_template(self) -> str:
        """Get template text for methodology section."""
        return """# Methodology

This section describes our approach to addressing the challenges outlined in the introduction.

## {methodology_subsection_1}

{methodology_content_1}

## {methodology_subsection_2}

{methodology_content_2}

## Experimental Setup

{experimental_setup}

Our experiments were conducted using {experimental_environment}, with the following parameters:

{experimental_parameters}

We evaluate our approach using {evaluation_metrics}, which are standard metrics in this domain.
"""
    
    def _get_results_template(self) -> str:
        """Get template text for results section."""
        return """# Results

This section presents the results of our experiments on {topic}.

## {results_subsection_1}

{results_content_1}

{figure_1}

As shown in {figure_reference_1}, our approach {result_interpretation_1}.

## {results_subsection_2}

{results_content_2}

{table_1}

Table {table_number} demonstrates that {result_interpretation_2}.

## Comparative Analysis

{comparative_analysis}

Overall, these results indicate that {overall_result_interpretation}.
"""
    
    def _get_discussion_template(self) -> str:
        """Get template text for discussion section."""
        return """# Discussion

In this section, we discuss the implications of our results and their broader significance.

## {discussion_subsection_1}

{discussion_content_1}

## {discussion_subsection_2}

{discussion_content_2}

## Limitations

Our approach has several limitations that should be acknowledged:

{limitations}

Despite these limitations, our work {discussion_conclusion}.
"""
    
    def _get_conclusion_template(self) -> str:
        """Get template text for conclusion section."""
        return """# Conclusion

In this paper, we presented {summary_of_approach} for addressing {problem_summary}.

Our main contributions include:

{contributions_summary}

The results of our experiments demonstrate that {results_summary}.

Future work could explore {future_work_directions}.

In conclusion, this work advances the state of the art in {topic} by {final_conclusion}.
"""
    
    def get_template(self, 
                     section_type: SectionType, 
                     document_type: DocumentType,
                     style: ContentStyle = ContentStyle.ACADEMIC,
                     technical_level: TechnicalLevel = TechnicalLevel.INTERMEDIATE) -> Optional[ContentTemplate]:
        """
        Get a content template for a specific section type and document type.
        
        Args:
            section_type: Type of section
            document_type: Type of document
            style: Content style
            technical_level: Technical level
            
        Returns:
            ContentTemplate if found, None otherwise
        """
        # Try to find a template that matches the exact specifications
        template_files = os.listdir(self.config.template_dir)
        
        # First try to find an exact match
        for file_name in template_files:
            if not file_name.endswith(".json"):
                continue
            
            try:
                template = ContentTemplate.load_from_file(os.path.join(self.config.template_dir, file_name))
                
                if (template.section_type == section_type and 
                    template.document_type == document_type and
                    template.style == style and
                    template.technical_level == technical_level):
                    return template
            except Exception as e:
                self.logger.warning(f"Error loading template {file_name}: {e}")
        
        # If no exact match, try to find a template with matching section type and document type
        for file_name in template_files:
            if not file_name.endswith(".json"):
                continue
            
            try:
                template = ContentTemplate.load_from_file(os.path.join(self.config.template_dir, file_name))
                
                if (template.section_type == section_type and 
                    template.document_type == document_type):
                    return template
            except Exception as e:
                self.logger.warning(f"Error loading template {file_name}: {e}")
        
        # If still no match, try to find a template with matching section type only
        for file_name in template_files:
            if not file_name.endswith(".json"):
                continue
            
            try:
                template = ContentTemplate.load_from_file(os.path.join(self.config.template_dir, file_name))
                
                if template.section_type == section_type:
                    return template
            except Exception as e:
                self.logger.warning(f"Error loading template {file_name}: {e}")
        
        return None
    
    def create_template(self, 
                        section_type: SectionType, 
                        document_type: DocumentType,
                        template_text: str,
                        style: ContentStyle = ContentStyle.ACADEMIC,
                        technical_level: TechnicalLevel = TechnicalLevel.INTERMEDIATE,
                        metadata: Optional[Dict[str, Any]] = None) -> ContentTemplate:
        """
        Create a new content template.
        
        Args:
            section_type: Type of section
            document_type: Type of document
            template_text: Template text with placeholders
            style: Content style
            technical_level: Technical level
            metadata: Additional metadata
            
        Returns:
            Created ContentTemplate
        """
        template = ContentTemplate(
            section_type=section_type,
            document_type=document_type,
            template_text=template_text,
            style=style,
            technical_level=technical_level,
            metadata=metadata or {}
        )
        
        # Generate a file name
        file_name = f"{section_type.name.lower()}_{document_type.name.lower()}_{style.name.lower()}.json"
        file_path = os.path.join(self.config.template_dir, file_name)
        
        # Save the template
        template.save_to_file(file_path)
        
        self.logger.info(f"Created new template: {file_path}")
        
        return template
    
    def _fill_template_with_research_data(self, 
                                         template: ContentTemplate, 
                                         research_data: ResearchData,
                                         section: Section) -> str:
        """
        Fill a template with research data.
        
        Args:
            template: Content template to fill
            research_data: Research data to use
            section: Section information
            
        Returns:
            Filled template text
        """
        template_text = template.template_text
        
        # Extract placeholders from the template
        placeholders = re.findall(r'\{([^}]+)\}', template_text)
        
        # Create a dictionary of replacements
        replacements = {}
        
        # First, add basic replacements
        replacements["topic"] = research_data.topic
        replacements["field"] = research_data.metadata.get("field", "artificial intelligence")
        
        # Add section-specific replacements based on the section type
        if section.section_type == SectionType.INTRODUCTION:
            replacements["background_context"] = self._generate_background_context(research_data)
            replacements["problem_statement"] = self._generate_problem_statement(research_data)
            replacements["proposed_approach"] = self._generate_proposed_approach(research_data)
            replacements["contributions"] = self._generate_contributions(research_data)
        
        elif section.section_type == SectionType.METHODOLOGY:
            # Generate methodology subsections
            if "methodology_subsection_1" in placeholders:
                replacements["methodology_subsection_1"] = "Proposed Approach"
                replacements["methodology_content_1"] = self._generate_methodology_content(research_data, 1)
            
            if "methodology_subsection_2" in placeholders:
                replacements["methodology_subsection_2"] = "Algorithm Details"
                replacements["methodology_content_2"] = self._generate_methodology_content(research_data, 2)
            
            replacements["experimental_setup"] = self._generate_experimental_setup(research_data)
            replacements["experimental_environment"] = research_data.metadata.get("experimental_environment", "a standard benchmarking environment")
            replacements["experimental_parameters"] = self._generate_experimental_parameters(research_data)
            replacements["evaluation_metrics"] = self._generate_evaluation_metrics(research_data)
        
        elif section.section_type == SectionType.RESULTS:
            # Generate results subsections
            if "results_subsection_1" in placeholders:
                replacements["results_subsection_1"] = "Main Results"
                replacements["results_content_1"] = self._generate_results_content(research_data, 1)
            
            if "results_subsection_2" in placeholders:
                replacements["results_subsection_2"] = "Ablation Studies"
                replacements["results_content_2"] = self._generate_results_content(research_data, 2)
            
            if "figure_1" in placeholders:
                replacements["figure_1"] = "[Figure 1: Performance comparison of our approach with baseline methods]"
            
            replacements["figure_reference_1"] = "Figure 1"
            replacements["result_interpretation_1"] = self._generate_result_interpretation(research_data, 1)
            replacements["result_interpretation_2"] = self._generate_result_interpretation(research_data, 2)
            replacements["table_1"] = "[Table 1: Performance metrics across different datasets]"
            replacements["table_number"] = "1"
            replacements["comparative_analysis"] = self._generate_comparative_analysis(research_data)
            replacements["overall_result_interpretation"] = self._generate_overall_result_interpretation(research_data)
        
        elif section.section_type == SectionType.DISCUSSION:
            # Generate discussion subsections
            if "discussion_subsection_1" in placeholders:
                replacements["discussion_subsection_1"] = "Implications of Results"
                replacements["discussion_content_1"] = self._generate_discussion_content(research_data, 1)
            
            if "discussion_subsection_2" in placeholders:
                replacements["discussion_subsection_2"] = "Comparison with Prior Work"
                replacements["discussion_content_2"] = self._generate_discussion_content(research_data, 2)
            
            replacements["limitations"] = self._generate_limitations(research_data)
            replacements["discussion_conclusion"] = self._generate_discussion_conclusion(research_data)
        
        elif section.section_type == SectionType.CONCLUSION:
            replacements["summary_of_approach"] = self._generate_summary_of_approach(research_data)
            replacements["problem_summary"] = self._generate_problem_summary(research_data)
            replacements["contributions_summary"] = self._generate_contributions_summary(research_data)
            replacements["results_summary"] = self._generate_results_summary(research_data)
            replacements["future_work_directions"] = self._generate_future_work_directions(research_data)
            replacements["final_conclusion"] = self._generate_final_conclusion(research_data)
        
        # Try to use LLM to fill placeholders if available
        if self.llm and LANGCHAIN_AVAILABLE:
            # First try to fill placeholders with LLM
            missing_placeholders = [p for p in placeholders if p not in replacements]
            if missing_placeholders:
                llm_replacements = self._generate_content_with_llm(
                    missing_placeholders, 
                    section, 
                    research_data, 
                    template
                )
                replacements.update(llm_replacements)
        
        # Fill any remaining placeholders with dummy text
        for placeholder in placeholders:
            if placeholder not in replacements:
                replacements[placeholder] = f"[Content for {placeholder}]"
        
        # Replace placeholders in the template
        for placeholder, replacement in replacements.items():
            template_text = template_text.replace(f"{{{placeholder}}}", replacement)
        
        return template_text
    
    def _generate_content_with_llm(self,
                                  placeholders: List[str],
                                  section: Section,
                                  research_data: ResearchData,
                                  template: ContentTemplate) -> Dict[str, str]:
        """
        Generate content for placeholders using a language model.
        
        Args:
            placeholders: List of placeholders to fill
            section: Section information
            research_data: Research data to use
            template: Content template
            
        Returns:
            Dictionary of placeholder replacements
        """
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return {}
        
        replacements = {}
        
        try:
            # Create context for LLM
            context = self._create_llm_context(section, research_data, template)
            
            # Create prompt for batch generation of placeholders
            prompt = self._create_llm_prompt(placeholders, context, section, research_data)
            
            # Generate content
            messages = [
                SystemMessage(content=f"You are a research content generator specialized in {research_data.topic}. "
                                    f"Generate content for a {section.section_type.name.lower()} section of a "
                                    f"{template.document_type.name.lower().replace('_', ' ')} with a "
                                    f"{template.technical_level.name.lower()} technical level and "
                                    f"{template.style.name.lower()} style."),
                HumanMessage(content=prompt)
            ]
            
            # Get response from LLM
            response = self.llm(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response to extract content for each placeholder
            for placeholder in placeholders:
                pattern = rf"{placeholder}:\s*(.+?)(?=\n\n|\n[A-Z_]+:|\Z)"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    replacements[placeholder] = match.group(1).strip()
                else:
                    self.logger.warning(f"Could not extract content for placeholder: {placeholder}")
            
            # If parsing failed, try a different approach
            if not replacements and placeholders:
                # If we couldn't extract structured content, we'll use the whole response
                # for the first placeholder, which is better than nothing
                replacements[placeholders[0]] = content.strip()
                
            return replacements
        
        except Exception as e:
            self.logger.error(f"Error generating content with LLM: {e}")
            return {}
    
    def _create_llm_context(self, 
                           section: Section, 
                           research_data: ResearchData, 
                           template: ContentTemplate) -> str:
        """
        Create context information for LLM content generation.
        
        Args:
            section: Section information
            research_data: Research data to use
            template: Content template
            
        Returns:
            Context information as string
        """
        context = f"Topic: {research_data.topic}\n"
        context += f"Section: {section.title} ({section.section_type.name})\n"
        context += f"Document Type: {template.document_type.name.replace('_', ' ').title()}\n"
        context += f"Style: {template.style.name.title()}\n"
        context += f"Technical Level: {template.technical_level.name.title()}\n\n"
        
        # Add facts
        if research_data.facts and len(research_data.facts) > 0:
            context += "Key Facts:\n"
            for i, fact in enumerate(research_data.facts[:5]):  # Limit to 5 facts
                context += f"- {fact}\n"
            context += "\n"
        
        # Add entities
        if research_data.entities and len(research_data.entities) > 0:
            context += "Key Entities:\n"
            entities_by_type = {}
            for entity in research_data.entities:
                entity_type = entity.get("type", "UNKNOWN")
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append(entity)
            
            for entity_type, entities in entities_by_type.items():
                context += f"- {entity_type}: "
                entity_names = [e.get("name", "") or e.get("text", "") for e in entities[:3]]
                context += ", ".join(filter(None, entity_names)) + "\n"
            
            context += "\n"
        
        # Add papers
        if research_data.papers and len(research_data.papers) > 0:
            context += "Related Papers:\n"
            for i, paper in enumerate(research_data.papers[:3]):  # Limit to 3 papers
                title = paper.get("title", "Untitled")
                authors = paper.get("authors", [])
                if isinstance(authors, list) and authors:
                    author_text = authors[0] + (" et al." if len(authors) > 1 else "")
                else:
                    author_text = "Unknown"
                year = paper.get("year", "")
                
                context += f"- {title} ({author_text}, {year})\n"
            
            context += "\n"
        
        # Add metadata
        if research_data.metadata:
            context += "Additional Information:\n"
            for key, value in list(research_data.metadata.items())[:5]:  # Limit to 5 metadata items
                if isinstance(value, (list, tuple)):
                    value_text = ", ".join(str(v) for v in value)
                else:
                    value_text = str(value)
                context += f"- {key}: {value_text}\n"
        
        # Add knowledge graph context if available
        if self.knowledge_graph_adapter:
            try:
                kg_context = self._get_knowledge_graph_context(research_data.topic)
                if kg_context:
                    context += "\nKnowledge Graph Context:\n" + kg_context + "\n"
            except Exception as e:
                self.logger.error(f"Error getting knowledge graph context: {e}")
        
        return context
    
    def _create_llm_prompt(self, 
                          placeholders: List[str], 
                          context: str, 
                          section: Section, 
                          research_data: ResearchData) -> str:
        """
        Create a prompt for LLM content generation.
        
        Args:
            placeholders: List of placeholders to fill
            context: Context information
            section: Section information
            research_data: Research data to use
            
        Returns:
            Prompt for LLM
        """
        prompt = f"Please generate content for the following placeholders in a {section.section_type.name.lower()} section "
        prompt += f"about {research_data.topic}. Use the provided context information to inform your response.\n\n"
        prompt += f"CONTEXT INFORMATION:\n{context}\n\n"
        
        prompt += "PLACEHOLDERS TO FILL:\n"
        for placeholder in placeholders:
            # Convert placeholder from snake_case to a more readable format
            readable_placeholder = placeholder.replace("_", " ").title()
            prompt += f"- {readable_placeholder} ({placeholder})\n"
        
        prompt += "\nPlease provide content for each placeholder in the following format:\n"
        prompt += "PLACEHOLDER_NAME: Your generated content here.\n\n"
        prompt += "Make sure your generated content is appropriate for the specified section type, document type, style, and technical level.\n"
        prompt += "Keep each placeholder's content concise (2-3 paragraphs maximum) but informative and substantive.\n"
        
        return prompt
    
    def _get_knowledge_graph_context(self, topic: str) -> str:
        """
        Get relevant context information from the knowledge graph.
        
        Args:
            topic: Research topic
            
        Returns:
            Context information from knowledge graph
        """
        if not self.knowledge_graph_adapter:
            return ""
        
        try:
            # Query the knowledge graph for relevant entities and relationships
            entities = self.knowledge_graph_adapter.query_entities_by_keyword(topic, limit=5)
            relationships = self.knowledge_graph_adapter.query_relationships_by_entities(
                [e.get("id") for e in entities if "id" in e], limit=10
            )
            
            # Format the information
            context = ""
            
            if entities:
                context += "Related Entities:\n"
                for entity in entities:
                    name = entity.get("name", entity.get("id", "Unknown"))
                    type_name = entity.get("type", "Unknown")
                    properties = ", ".join([f"{k}: {v}" for k, v in entity.items() 
                                          if k not in ["id", "name", "type"] and len(str(v)) < 50][:3])
                    
                    context += f"- {name} ({type_name}): {properties}\n"
                
                context += "\n"
            
            if relationships:
                context += "Key Relationships:\n"
                for rel in relationships:
                    source = rel.get("source_name", rel.get("source_id", "Unknown"))
                    target = rel.get("target_name", rel.get("target_id", "Unknown"))
                    rel_type = rel.get("type", "related_to")
                    
                    context += f"- {source} {rel_type.replace('_', ' ')} {target}\n"
            
            return context
        
        except Exception as e:
            self.logger.error(f"Error querying knowledge graph: {e}")
            return ""
    
    def _generate_section_with_llm(self,
                                 section: Section,
                                 document_structure: DocumentStructure,
                                 research_data: ResearchData) -> str:
        """
        Generate content for a section directly using a language model.
        
        Args:
            section: Section to generate content for
            document_structure: Overall document structure
            research_data: Research data to use
            
        Returns:
            Generated content for the section
        """
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return ""
        
        try:
            # Create context for LLM
            template = ContentTemplate(
                section_type=section.section_type,
                document_type=document_structure.document_type,
                template_text="",
                style=self.config.style,
                technical_level=self.config.technical_level
            )
            context = self._create_llm_context(section, research_data, template)
            
            # Create system message
            system_message = (
                f"You are a research content generator specialized in {research_data.topic}. "
                f"Generate content for a {section.section_type.name.lower()} section titled '{section.title}' "
                f"of a {document_structure.document_type.name.lower().replace('_', ' ')}. "
                f"Use a {self.config.technical_level.name.lower()} technical level and "
                f"{self.config.style.name.lower()} style. "
                f"The content should be comprehensive, well-structured, and include appropriate "
                f"headings, paragraphs, and formatting using Markdown syntax."
            )
            
            # Create user message
            user_message = (
                f"Please generate the complete content for the '{section.title}' section "
                f"of our {document_structure.document_type.name.lower().replace('_', ' ')} about {research_data.topic}.\n\n"
                f"CONTEXT INFORMATION:\n{context}\n\n"
                f"The section should cover all relevant aspects expected in a {section.section_type.name.lower()} "
                f"section of a {document_structure.document_type.name.lower().replace('_', ' ')}. "
                f"Use appropriate headings, paragraphs, and formatting with Markdown syntax. "
                f"If applicable, include references to papers, models, datasets, and methods from the context information."
            )
            
            # Add section-specific instructions
            if section.section_type == SectionType.INTRODUCTION:
                user_message += (
                    "\n\nThis introduction should include background context, problem statement, "
                    "proposed approach, and main contributions."
                )
            elif section.section_type == SectionType.METHODOLOGY:
                user_message += (
                    "\n\nThis methodology section should describe the approach, algorithms, "
                    "experimental setup, evaluation metrics, and implementation details."
                )
            elif section.section_type == SectionType.RESULTS:
                user_message += (
                    "\n\nThis results section should present main findings, comparisons with baseline methods, "
                    "performance metrics, and interpretation of results."
                )
            elif section.section_type == SectionType.DISCUSSION:
                user_message += (
                    "\n\nThis discussion section should cover implications of the results, comparison with prior work, "
                    "limitations of the approach, and future directions."
                )
            elif section.section_type == SectionType.CONCLUSION:
                user_message += (
                    "\n\nThis conclusion should summarize the approach, main contributions, results, "
                    "and suggest future work directions."
                )
            
            # Generate content
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_message)
            ]
            
            # Set max tokens based on section length
            max_tokens = self.config.max_section_length * 4  # Approximate word-to-token ratio
            
            # Get response from LLM
            response = self.llm(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Ensure section title is at the beginning
            if not content.startswith(f"# {section.title}") and not content.startswith(f"## {section.title}"):
                content = f"## {section.title}\n\n{content}"
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error generating section with LLM: {e}")
            return ""
    
    def generate_content_for_section(self, 
                                    section: Section,
                                    document_structure: DocumentStructure,
                                    research_data: ResearchData) -> str:
        """
        Generate content for a section based on research data.
        
        Args:
            section: Section to generate content for
            document_structure: Overall document structure
            research_data: Research data to use
            
        Returns:
            Generated content for the section
        """
        # Get template for the section
        template = self.get_template(
            section_type=section.section_type,
            document_type=document_structure.document_type,
            style=self.config.style,
            technical_level=self.config.technical_level
        )
        
        # If no template is found, create a simple one based on section type
        if template is None:
            template_text = f"# {section.title}\n\n[Content for {section.title}]"
            template = ContentTemplate(
                section_type=section.section_type,
                document_type=document_structure.document_type,
                template_text=template_text,
                style=self.config.style,
                technical_level=self.config.technical_level
            )
        
        # Try direct LLM generation if available
        content = ""
        if self.llm and LANGCHAIN_AVAILABLE and self.config.llm_model:
            try:
                content = self._generate_section_with_llm(section, document_structure, research_data)
            except Exception as e:
                self.logger.error(f"Error generating section with LLM: {e}")
                content = ""
        
        # Fall back to template-based generation if LLM generation failed or was not available
        if not content:
            # Fill the template with research data
            content = self._fill_template_with_research_data(template, research_data, section)
        
        # Generate content for subsections recursively
        if section.subsections:
            subsection_content = ""
            for subsection in section.subsections:
                subsection_content += "\n\n" + self.generate_content_for_section(
                    subsection, document_structure, research_data
                )
            
            # Add subsection content if it doesn't already exist in the content
            if subsection_content.strip() and "# " + section.subsections[0].title not in content:
                content += "\n" + subsection_content
        
        return content
    
    def generate_content_for_document(self, 
                                    document_structure: DocumentStructure,
                                    research_data: ResearchData) -> Dict[str, str]:
        """
        Generate content for all sections in a document.
        
        Args:
            document_structure: Document structure
            research_data: Research data to use
            
        Returns:
            Dictionary mapping section title to generated content
        """
        section_content = {}
        
        for section in document_structure.sections:
            # Skip certain sections that don't need generated content
            if section.section_type in [SectionType.TITLE, SectionType.REFERENCES]:
                continue
            
            content = self.generate_content_for_section(section, document_structure, research_data)
            section_content[section.title] = content
        
        return section_content
    
    def generate_complete_document(self, 
                                  document_structure: DocumentStructure,
                                  research_data: ResearchData) -> str:
        """
        Generate a complete document.
        
        Args:
            document_structure: Document structure
            research_data: Research data to use
            
        Returns:
            Complete document as a string
        """
        document = f"# {document_structure.title}\n\n"
        
        # Try to generate the entire document with LLM if available
        if self.llm and LANGCHAIN_AVAILABLE and self.config.llm_model:
            try:
                llm_document = self._generate_document_with_llm(document_structure, research_data)
                if llm_document:
                    return llm_document
            except Exception as e:
                self.logger.error(f"Error generating document with LLM: {e}")
        
        # Fall back to section-by-section generation
        for section in document_structure.sections:
            # Skip title section since we already added it
            if section.section_type == SectionType.TITLE:
                continue
            
            # Handle abstract section specially
            if section.section_type == SectionType.ABSTRACT:
                document += f"## {section.title}\n\n"
                document += self._generate_abstract(research_data) + "\n\n"
                continue
            
            # Handle references section specially
            if section.section_type == SectionType.REFERENCES:
                document += f"## {section.title}\n\n"
                document += self._generate_references(research_data) + "\n\n"
                continue
            
            # Generate content for other sections
            content = self.generate_content_for_section(section, document_structure, research_data)
            
            # Remove the heading if it's already in the content
            if content.startswith(f"# {section.title}"):
                document += content + "\n\n"
            else:
                document += f"## {section.title}\n\n" + content + "\n\n"
        
        return document
        
    def _generate_document_with_llm(self,
                                  document_structure: DocumentStructure,
                                  research_data: ResearchData) -> str:
        """
        Generate an entire document using a language model.
        
        Args:
            document_structure: Document structure
            research_data: Research data to use
            
        Returns:
            Complete document as a string
        """
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return ""
        
        try:
            # Create template
            template = ContentTemplate(
                section_type=SectionType.TITLE,  # Placeholder
                document_type=document_structure.document_type,
                template_text="",
                style=self.config.style,
                technical_level=self.config.technical_level
            )
            
            # Create context
            context = self._create_llm_context(
                Section(title=document_structure.title, section_type=SectionType.TITLE),
                research_data,
                template
            )
            
            # Create document structure information
            structure_info = f"Document Title: {document_structure.title}\n"
            structure_info += f"Document Type: {document_structure.document_type.name.replace('_', ' ').title()}\n"
            structure_info += "Document Sections:\n"
            
            for section in document_structure.sections:
                structure_info += f"- {section.title} ({section.section_type.name})\n"
                if section.subsections:
                    for subsection in section.subsections:
                        structure_info += f"  - {subsection.title} ({subsection.section_type.name})\n"
            
            # Load papers from research data into citation manager
            if research_data.papers:
                self.citation_manager.load_papers_from_research_data(research_data)
            
            # Create citation instructions
            citation_instructions = (
                f"For citations, use the format [@citation_key] where citation_key is one of the following:\n"
            )
            
            # Include available citation keys
            for i, paper in enumerate(self.citation_manager.papers[:10]):  # Limit to 10 papers
                citation_key = paper.get("citation_key", "")
                title = paper.get("title", "Unknown")
                authors = paper.get("authors", ["Unknown"])
                if isinstance(authors, list) and len(authors) > 0:
                    author = authors[0]
                else:
                    author = "Unknown"
                year = paper.get("year", "")
                
                citation_instructions += f"- {citation_key}: {title} by {author} ({year})\n"
            
            # Create system message
            system_message = (
                f"You are a research document generator specialized in {research_data.topic}. "
                f"Generate a complete {document_structure.document_type.name.lower().replace('_', ' ')} "
                f"with the specified structure. Use a {self.config.technical_level.name.lower()} technical level "
                f"and {self.config.style.name.lower()} style. "
                f"The document should be comprehensive, well-structured, and include appropriate "
                f"headings, paragraphs, and formatting using Markdown syntax."
            )
            
            # Create user message
            user_message = (
                f"Please generate a complete {document_structure.document_type.name.lower().replace('_', ' ')} "
                f"titled '{document_structure.title}' about {research_data.topic}.\n\n"
                f"DOCUMENT STRUCTURE:\n{structure_info}\n\n"
                f"CONTEXT INFORMATION:\n{context}\n\n"
                f"CITATION INSTRUCTIONS:\n{citation_instructions}\n\n"
                f"Generate the complete document with all sections specified in the structure. "
                f"Use Markdown formatting with appropriate headings (# for title, ## for main sections, ### for subsections). "
                f"Include all typical content expected in each section of a {document_structure.document_type.name.lower().replace('_', ' ')}. "
                f"If applicable, include references to papers, models, datasets, and methods from the context information. "
                f"Use citations in the format [@citation_key] when referring to specific papers. "
                f"Make sure to include all specified sections and maintain the correct heading structure."
            )
            
            # Generate content
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=user_message)
            ]
            
            # Get response from LLM
            response = self.llm(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Ensure document title is at the beginning if not already
            if not content.startswith(f"# {document_structure.title}"):
                content = f"# {document_structure.title}\n\n{content}"
            
            # Process citation placeholders
            content = self.process_citations(content)
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error generating document with LLM: {e}")
            return ""
    
    # Helper methods for generating section content
    
    def _generate_background_context(self, research_data: ResearchData) -> str:
        """Generate background context for introduction."""
        # Use facts related to the topic
        facts = research_data.get_facts_by_keyword(research_data.topic)
        
        if facts:
            selected_facts = facts[:2]  # Use up to 2 facts
            return " ".join(selected_facts)
        
        return f"This area has gained significant attention due to its potential applications in various domains including {', '.join(research_data.metadata.get('domains', ['computer vision', 'natural language processing']))}."
    
    def _generate_problem_statement(self, research_data: ResearchData) -> str:
        """Generate problem statement for introduction."""
        # Use entities of type "problem" if available
        problems = research_data.get_entities_by_type("problem")
        
        if problems:
            selected_problem = problems[0]
            return f"One of the main challenges is {selected_problem.get('text', 'the optimization of performance across diverse datasets')}."
        
        return f"These challenges include limitations in existing approaches regarding scalability, accuracy, and generalization capabilities."
    
    def _generate_proposed_approach(self, research_data: ResearchData) -> str:
        """Generate proposed approach for introduction."""
        # Use entities of type "solution" if available
        solutions = research_data.get_entities_by_type("solution")
        
        if solutions:
            selected_solution = solutions[0]
            return f"proposing {selected_solution.get('text', 'a novel approach')} that addresses these limitations"
        
        return f"proposing a novel approach that combines {' and '.join(research_data.metadata.get('techniques', ['advanced optimization techniques', 'robust feature extraction']))}"
    
    def _generate_contributions(self, research_data: ResearchData) -> str:
        """Generate contributions for introduction."""
        # Generate a list of contributions
        contributions_list = ["A novel approach for addressing the challenges in " + research_data.topic]
        
        # Add methodology-related contribution
        methodology = research_data.metadata.get("methodology", "")
        if methodology:
            contributions_list.append(f"A detailed {methodology} methodology for evaluating performance")
        
        # Add results-related contribution
        results = research_data.metadata.get("results", "")
        if results:
            contributions_list.append(f"Experimental results demonstrating {results}")
        
        # Format as a bulleted list
        return "\n".join(f"- {contribution}" for contribution in contributions_list)
    
    def _generate_abstract(self, research_data: ResearchData) -> str:
        """Generate abstract for the document."""
        return f"""Recent advancements in {research_data.topic} have highlighted the need for more effective approaches. 
In this paper, we propose a novel method for addressing challenges in {research_data.topic} by leveraging {' and '.join(research_data.metadata.get('techniques', ['advanced techniques']))}.
Our approach demonstrates significant improvements over existing methods, with performance gains of {research_data.metadata.get('performance_improvement', '10-15%')} on standard benchmarks.
We validate our approach through extensive experiments on {research_data.metadata.get('datasets', 'multiple datasets')}, demonstrating its effectiveness and generalizability.
These results highlight the potential of our approach for advancing the state of the art in {research_data.topic}."""
    
    def _generate_methodology_content(self, research_data: ResearchData, section_number: int) -> str:
        """Generate methodology content for the document."""
        if section_number == 1:
            # Generate content for the first methodology subsection
            return f"""Our approach addresses the challenges of {research_data.topic} through a novel methodology.
The key insight of our work is that {research_data.metadata.get('key_insight', 'by carefully designing the architecture and optimization process, we can achieve better performance and generalization')}.

Specifically, we propose a {research_data.metadata.get('model_type', 'model')} that incorporates {research_data.metadata.get('key_feature', 'several innovative components')} to address the limitations of existing approaches."""
        else:
            # Generate content for the second methodology subsection
            return f"""The key algorithm for our approach can be summarized as follows:

1. Initialize the model with {research_data.metadata.get('initialization', 'pre-trained weights')}
2. Process the input data using {research_data.metadata.get('processing', 'our feature extraction pipeline')}
3. Apply the {research_data.metadata.get('algorithm', 'core algorithm')} to generate predictions
4. Optimize the model using {research_data.metadata.get('optimization', 'our custom loss function')}

This approach allows us to effectively {research_data.metadata.get('advantage', 'balance performance and computational efficiency')}, which is crucial for applications in {research_data.topic}."""
    
    def _generate_experimental_setup(self, research_data: ResearchData) -> str:
        """Generate experimental setup description."""
        datasets = research_data.metadata.get('datasets', ['standard benchmark datasets'])
        if isinstance(datasets, str):
            datasets = [datasets]
        
        dataset_text = ", ".join(datasets[:-1]) + " and " + datasets[-1] if len(datasets) > 1 else datasets[0]
        
        return f"""To evaluate our approach, we conducted extensive experiments on {dataset_text}.
These datasets were chosen to ensure a comprehensive evaluation across different {research_data.metadata.get('evaluation_dimension', 'scenarios and challenges')}.
We compare our method against several state-of-the-art baselines to demonstrate its effectiveness."""
    
    def _generate_experimental_parameters(self, research_data: ResearchData) -> str:
        """Generate experimental parameters description."""
        # Create a list of parameters
        parameters = []
        
        # Add batch size
        batch_size = research_data.metadata.get('batch_size', '32')
        parameters.append(f"- Batch size: {batch_size}")
        
        # Add learning rate
        learning_rate = research_data.metadata.get('learning_rate', '0.001')
        parameters.append(f"- Learning rate: {learning_rate}")
        
        # Add optimizer
        optimizer = research_data.metadata.get('optimizer', 'Adam')
        parameters.append(f"- Optimizer: {optimizer}")
        
        # Add number of epochs
        epochs = research_data.metadata.get('epochs', '100')
        parameters.append(f"- Number of epochs: {epochs}")
        
        return "\n".join(parameters)
    
    def _generate_evaluation_metrics(self, research_data: ResearchData) -> str:
        """Generate evaluation metrics description."""
        metrics = research_data.metadata.get('metrics', ['accuracy', 'precision', 'recall', 'F1-score'])
        if isinstance(metrics, str):
            metrics = [metrics]
        
        return ", ".join(metrics)
    
    def _generate_results_content(self, research_data: ResearchData, section_number: int) -> str:
        """Generate results content for the document."""
        if section_number == 1:
            # Generate content for the first results subsection
            performance = research_data.metadata.get('performance', 'significant improvements over baseline methods')
            return f"""We evaluated our approach on multiple datasets and compared it with state-of-the-art methods.
Table 1 presents the performance of our approach compared to baseline methods across different datasets.
As shown in the table, our approach achieves {performance} across all datasets."""
        else:
            # Generate content for the second results subsection
            ablation_results = research_data.metadata.get('ablation_results', 'each component of our approach contributes to its overall performance')
            return f"""To understand the contribution of each component of our approach, we conducted ablation studies.
We systematically removed each component of our model and evaluated the resulting performance.
The results indicate that {ablation_results}."""
    
    def _generate_result_interpretation(self, research_data: ResearchData, section_number: int) -> str:
        """Generate result interpretation for the document."""
        if section_number == 1:
            return f"consistently outperforms baseline methods by {research_data.metadata.get('improvement', '10-15%')} on average"
        else:
            return f"the {research_data.metadata.get('key_component', 'key component')} of our approach contributes most significantly to its performance, with a {research_data.metadata.get('component_contribution', '5-7%')} increase in overall accuracy"
    
    def _generate_comparative_analysis(self, research_data: ResearchData) -> str:
        """Generate comparative analysis for results section."""
        return f"""We compared our approach with several state-of-the-art methods including {research_data.metadata.get('baselines', 'baseline methods')}.
The results demonstrate that our approach consistently outperforms these methods across all datasets and metrics.
In particular, our approach achieves {research_data.metadata.get('best_result', 'state-of-the-art performance')} on {research_data.metadata.get('best_dataset', 'the most challenging dataset')}, surpassing the previous state of the art by {research_data.metadata.get('improvement_over_sota', '5%')}."""
    
    def _generate_overall_result_interpretation(self, research_data: ResearchData) -> str:
        """Generate overall result interpretation for the document."""
        return f"our approach effectively addresses the challenges in {research_data.topic} and provides a significant advancement over existing methods"
    
    def _generate_discussion_content(self, research_data: ResearchData, section_number: int) -> str:
        """Generate discussion content for the document."""
        if section_number == 1:
            # Generate content for the first discussion subsection
            return f"""Our results have several important implications for {research_data.topic}.
First, they demonstrate that {research_data.metadata.get('implication_1', 'the proposed approach can effectively address the challenges in this domain')}.
Second, the performance improvements suggest that {research_data.metadata.get('implication_2', 'there is significant potential for further advancements in this area')}.
These findings contribute to the broader understanding of {research_data.metadata.get('broader_field', 'the field')} by {research_data.metadata.get('contribution', 'providing insights into effective approaches for addressing complex challenges')}."""
        else:
            # Generate content for the second discussion subsection
            return f"""Our work builds upon and extends prior research in {research_data.topic}.
Previous approaches such as {research_data.metadata.get('prior_work', 'earlier methods')} have addressed some aspects of the problem, but they {research_data.metadata.get('prior_work_limitation', 'often struggle with generalizing across diverse datasets')}.
Our approach addresses these limitations by {research_data.metadata.get('improvement_over_prior', 'incorporating novel components that enhance both performance and generalizability')}.
This represents a significant advancement over existing methods and provides a foundation for future work in this area."""
    
    def _generate_limitations(self, research_data: ResearchData) -> str:
        """Generate limitations for discussion section."""
        # Create a list of limitations
        limitations = []
        
        # Add computational complexity limitation
        limitations.append(f"- {research_data.metadata.get('limitation_1', 'Our approach requires significant computational resources, which may limit its applicability in resource-constrained environments')}")
        
        # Add dataset limitation
        limitations.append(f"- {research_data.metadata.get('limitation_2', 'While our approach performs well on the evaluated datasets, its performance on other domains remains to be explored')}")
        
        # Add theoretical limitation
        limitations.append(f"- {research_data.metadata.get('limitation_3', 'The theoretical understanding of why our approach works so well is still incomplete')}")
        
        return "\n".join(limitations)
    
    def _generate_discussion_conclusion(self, research_data: ResearchData) -> str:
        """Generate discussion conclusion for the document."""
        return f"makes significant contributions to the field of {research_data.topic} by {research_data.metadata.get('contribution', 'providing a more effective approach for addressing key challenges')}"
    
    def _generate_summary_of_approach(self, research_data: ResearchData) -> str:
        """Generate summary of approach for conclusion section."""
        return f"a novel approach for {research_data.topic} that {research_data.metadata.get('approach_summary', 'incorporates innovative components to address key challenges')}"
    
    def _generate_problem_summary(self, research_data: ResearchData) -> str:
        """Generate problem summary for conclusion section."""
        return f"the challenges in {research_data.topic}, particularly {research_data.metadata.get('problem_summary', 'the limitations of existing approaches in terms of performance and generalizability')}"
    
    def _generate_contributions_summary(self, research_data: ResearchData) -> str:
        """Generate contributions summary for conclusion section."""
        # Create a list of contributions
        contributions = []
        
        # Add approach contribution
        contributions.append(f"- {research_data.metadata.get('contribution_1', 'A novel approach that addresses key challenges in ' + research_data.topic)}")
        
        # Add methodology contribution
        contributions.append(f"- {research_data.metadata.get('contribution_2', 'A comprehensive evaluation methodology that demonstrates the effectiveness of our approach')}")
        
        # Add empirical contribution
        contributions.append(f"- {research_data.metadata.get('contribution_3', 'Empirical results showing significant improvements over state-of-the-art methods')}")
        
        return "\n".join(contributions)
    
    def _generate_results_summary(self, research_data: ResearchData) -> str:
        """Generate results summary for conclusion section."""
        return f"our approach {research_data.metadata.get('results_summary', 'significantly outperforms existing methods across multiple datasets and metrics')}"
    
    def _generate_future_work_directions(self, research_data: ResearchData) -> str:
        """Generate future work directions for conclusion section."""
        # Create a list of future work directions
        future_work = []
        
        # Add theoretical direction
        future_work.append(research_data.metadata.get('future_work_1', 'developing a deeper theoretical understanding of the proposed approach'))
        
        # Add application direction
        future_work.append(research_data.metadata.get('future_work_2', 'extending the approach to other domains and applications'))
        
        # Add efficiency direction
        future_work.append(research_data.metadata.get('future_work_3', 'improving the computational efficiency of the approach'))
        
        return ", ".join(future_work)
    
    def _generate_final_conclusion(self, research_data: ResearchData) -> str:
        """Generate final conclusion for the document."""
        return f"{research_data.metadata.get('final_conclusion', 'providing a more effective solution that significantly improves upon existing methods')}"
    
    def _generate_references(self, research_data: ResearchData) -> str:
        """Generate references for the document."""
        # Load papers from research data into citation manager
        if research_data.papers:
            self.citation_manager.load_papers_from_research_data(research_data)
        
        # Generate reference list using citation manager
        return self.citation_manager.generate_reference_list("References")
        
    def _generate_references_with_llm(self, research_data: ResearchData) -> str:
        """Generate references using a language model and format them with citation manager."""
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return ""
        
        try:
            # Create prompt
            prompt = (
                f"Generate a list of 5-7 realistic academic references for a research paper on {research_data.topic}. "
                f"Include influential papers, recent developments, and seminal works in this field. "
                f"Each reference should include full details with this exact JSON format for each paper:\n\n"
                f"{{'title': 'Paper Title', 'authors': ['Author 1', 'Author 2'], 'year': '2023', "
                f"'journal': 'Journal Name', 'volume': '10', 'issue': '2', 'pages': '123-145', "
                f"'doi': '10.xxxx/xxxxx', 'url': 'https://doi.org/...' }}\n\n"
                f"Return ONLY the JSON array of references, properly formatted for parsing."
            )
            
            # Create messages
            messages = [
                SystemMessage(content="You are an academic reference generator with extensive knowledge of research literature."),
                HumanMessage(content=prompt)
            ]
            
            # Get response
            response = self.llm(messages)
            references_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse JSON (might need cleaning)
            try:
                # Extract JSON array from response (may be surrounded by markdown code blocks or other text)
                json_pattern = r'\[\s*\{.+\}\s*\]'
                json_match = re.search(json_pattern, references_text, re.DOTALL)
                
                if json_match:
                    references_json = json_match.group(0)
                    references = json.loads(references_json)
                    
                    # Add papers to citation manager
                    for paper in references:
                        self.citation_manager.add_paper(paper)
                    
                    # Generate reference list
                    return self.citation_manager.generate_reference_list("References")
            except Exception as e:
                self.logger.error(f"Error parsing LLM-generated references: {e}")
            
            # If JSON parsing fails, try to use the raw text as a fallback
            return references_text
            
        except Exception as e:
            self.logger.error(f"Error generating references with LLM: {e}")
            return ""
            
    def process_citations(self, text: str) -> str:
        """
        Process citation placeholders in text and replace with formatted citations.
        
        Args:
            text: Text with citation placeholders
            
        Returns:
            Text with formatted citations
        """
        return self.citation_manager.process_text_with_citations(text)
        
    def generate_visualization(self,
                              data: Union[Dict[str, Any], List[Dict[str, Any]]],
                              vis_type: Union[VisualizationType, str],
                              subtype: Optional[Union[ChartType, DiagramType, str]] = None,
                              title: str = "",
                              x_label: str = "",
                              y_label: str = "",
                              x_column: Optional[str] = None,
                              y_column: Optional[str] = None,
                              category_column: Optional[str] = None,
                              file_name: Optional[str] = None,
                              **kwargs) -> str:
        """
        Generate a visualization for research content.
        
        Args:
            data: Data for the visualization (dict or list of dicts)
            vis_type: Type of visualization (CHART, DIAGRAM, NETWORK, TABLE)
            subtype: Subtype of visualization (e.g., BAR, LINE, FLOWCHART)
            title: Title for the visualization
            x_label: Label for x-axis
            y_label: Label for y-axis
            x_column: Column name for x-axis data
            y_column: Column name for y-axis data
            category_column: Column name for categorization
            file_name: Name for the output file
            **kwargs: Additional parameters for the visualization
            
        Returns:
            Path to the generated visualization file, markdown, or base64-encoded visualization
        """
        return self.visualization_generator.create_visualization(
            data=data,
            vis_type=vis_type,
            subtype=subtype,
            title=title,
            x_label=x_label,
            y_label=y_label,
            x_column=x_column,
            y_column=y_column,
            category_column=category_column,
            file_name=file_name,
            **kwargs
        )
    
    def generate_knowledge_graph_visualization(self,
                                             query: str,
                                             chart_type: Union[ChartType, str] = "NETWORK",
                                             title: str = "",
                                             file_name: Optional[str] = None,
                                             **kwargs) -> str:
        """
        Generate a visualization based on data from the knowledge graph.
        
        Args:
            query: Cypher query for the knowledge graph
            chart_type: Type of chart to create
            title: Title for the visualization
            file_name: Name for the output file
            **kwargs: Additional parameters for the visualization
            
        Returns:
            Path to the generated visualization file, markdown, or base64-encoded visualization
        """
        return self.visualization_generator.generate_chart_from_knowledge_graph(
            query=query,
            chart_type=chart_type,
            title=title,
            file_name=file_name,
            **kwargs
        )