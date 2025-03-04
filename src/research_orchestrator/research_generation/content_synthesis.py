"""
Content Synthesis Engine for Research Generation.

This module provides functionality for generating coherent text content for
research documents based on extracted knowledge and document structure.
"""

import logging
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Union
import json
import os
from pathlib import Path
import re
import random

from .report_structure import DocumentStructure, Section, SectionType, DocumentType

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
    
    def __init__(self, config: Optional[ContentGenerationConfig] = None):
        """
        Initialize the Content Synthesis Engine.
        
        Args:
            config: Configuration for content generation
        """
        self.config = config or ContentGenerationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize default templates
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """Initialize content templates."""
        os.makedirs(self.config.template_dir, exist_ok=True)
        
        # Create default templates if none exist
        if not os.listdir(self.config.template_dir):
            self._create_default_templates()
    
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
        
        # Fill any remaining placeholders with dummy text
        for placeholder in placeholders:
            if placeholder not in replacements:
                replacements[placeholder] = f"[Content for {placeholder}]"
        
        # Replace placeholders in the template
        for placeholder, replacement in replacements.items():
            template_text = template_text.replace(f"{{{placeholder}}}", replacement)
        
        return template_text
    
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
        # Use papers from research data if available
        if research_data.papers:
            references = []
            
            for i, paper in enumerate(research_data.papers[:10]):  # Limit to 10 references
                authors = paper.get("authors", ["Author"])
                if isinstance(authors, str):
                    authors_text = authors
                else:
                    if len(authors) == 1:
                        authors_text = authors[0]
                    elif len(authors) == 2:
                        authors_text = authors[0] + " and " + authors[1]
                    else:
                        authors_text = ", ".join(authors[:-1]) + ", and " + authors[-1]
                
                title = paper.get("title", "Paper Title")
                venue = paper.get("venue", "Conference/Journal")
                year = paper.get("year", "2023")
                
                reference = f"[{i+1}] {authors_text}. \"{title}.\" {venue}, {year}."
                references.append(reference)
            
            return "\n\n".join(references)
        
        # Generate dummy references if no papers are available
        return """[1] Smith, J. and Johnson, A. "A Novel Approach to Machine Learning." Journal of Artificial Intelligence, 2022.

[2] Brown, R., Davis, M., Wilson, E., and Thompson, K. "Advances in Neural Networks." Conference on Neural Information Processing Systems, 2021.

[3] Lee, S. "Deep Learning for Computer Vision: A Comprehensive Survey." IEEE Transactions on Pattern Analysis and Machine Intelligence, 2023."""