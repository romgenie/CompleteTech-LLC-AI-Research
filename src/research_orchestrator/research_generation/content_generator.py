"""
Content Generator for Research Generation.

This module provides the ContentGenerator class, which coordinates the generation
of research content based on extracted knowledge and research plans.
"""

import logging
from typing import Any, Dict, List, Optional, Union
import json
import os
from pathlib import Path

from research_orchestrator.core.state_manager import Project
from research_orchestrator.research_generation.content_synthesis import ContentSynthesisEngine, ResearchData
from research_orchestrator.research_generation.report_structure import ReportStructurePlanner, DocumentStructure, Section, DocumentType, SectionType
from research_orchestrator.research_generation.citation.citation_manager import CitationManager, CitationStyle
from research_orchestrator.research_generation.visualization.visualization_generator import VisualizationGenerator, VisualizationType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    Generates research content based on knowledge extracted during the research process.
    Coordinates the document structure planning, content synthesis, visualization,
    and citation management.
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 knowledge_graph_adapter = None,
                 llm_provider: Optional[str] = None):
        """
        Initialize the content generator.
        
        Args:
            config: Configuration for content generation
            knowledge_graph_adapter: Adapter for accessing knowledge graph
            llm_provider: LLM provider for content generation
        """
        self.config = config or {}
        self.knowledge_graph_adapter = knowledge_graph_adapter
        
        # Initialize components
        self.structure_planner = ReportStructurePlanner()
        
        # Initialize citation manager with fallback for missing citation styles
        try:
            self.citation_manager = CitationManager(
                style=self.config.get("citation_style", "APA"),
                knowledge_graph_adapter=knowledge_graph_adapter
            )
        except Exception as e:
            self.logger.warning(f"Error initializing CitationManager with specified style: {e}")
            self.logger.info("Falling back to default APA style")
            self.citation_manager = CitationManager(
                style="APA",
                knowledge_graph_adapter=knowledge_graph_adapter
            )
        
        # Initialize visualization generator with fallback
        try:
            self.visualization_generator = VisualizationGenerator(
                knowledge_graph_adapter=knowledge_graph_adapter
            )
        except Exception as e:
            self.logger.warning(f"Error initializing VisualizationGenerator: {e}")
            self.logger.info("Creating minimal visualization generator")
            # Use a minimal implementation if the full one fails
            from research_orchestrator.research_generation.visualization.visualization_generator import VisualizationType
            class MinimalVisualizationGenerator:
                def create_visualization(self, **kwargs):
                    return f"[Visualization placeholder: {kwargs.get('title', 'Untitled')}]"
                def generate_chart_from_knowledge_graph(self, **kwargs):
                    return f"[Knowledge graph visualization placeholder: {kwargs.get('title', 'Untitled')}]"
            self.visualization_generator = MinimalVisualizationGenerator()
        
        # Initialize content synthesis engine with fallback
        try:
            self.content_engine = ContentSynthesisEngine(
                config=self.config.get("content_config"),
                knowledge_graph_adapter=knowledge_graph_adapter,
                citation_manager=self.citation_manager,
                visualization_generator=self.visualization_generator,
                llm_model=self.config.get("llm_model")
            )
        except Exception as e:
            self.logger.warning(f"Error initializing ContentSynthesisEngine: {e}")
            self.logger.info("Using template-based fallback for content generation")
            
            # Create a mock content synthesis engine if the real one fails
            class TemplateFallbackEngine:
                def __init__(self, citation_manager=None, visualization_generator=None):
                    self.citation_manager = citation_manager
                    self.visualization_generator = visualization_generator
                
                def generate_content_for_section(self, section, document_structure, research_data):
                    """Generate simple content from a template"""
                    topic = research_data.topic or "research topic"
                    facts = "\n".join([f"- {fact}" for fact in research_data.facts[:5]]) if research_data.facts else "No facts available."
                    
                    return f"""## {section.title}

This section discusses {topic}.

### Key Facts

{facts}

### Summary

This research area has significant implications for future developments.
"""
                
                def generate_complete_document(self, document_structure, research_data):
                    """Generate a complete document by combining sections"""
                    sections = []
                    for section in document_structure.sections:
                        content = self.generate_content_for_section(section, document_structure, research_data)
                        sections.append(content)
                    return "\n\n".join([f"# {document_structure.title}"] + sections)
                
                def process_citations(self, text):
                    """Process citation placeholders"""
                    if self.citation_manager:
                        try:
                            return self.citation_manager.process_text_with_citations(text)
                        except:
                            pass
                    return text
            
            # Create the fallback engine
            self.content_engine = TemplateFallbackEngine(
                citation_manager=self.citation_manager,
                visualization_generator=self.visualization_generator
            )
        
        self.logger = logging.getLogger(__name__)
        
    def generate_content(self, 
                         knowledge: Dict[str, Any],
                         section: Dict[str, Any],
                         format: str = "markdown") -> Dict[str, Any]:
        """
        Generate content for a specific section.
        
        Args:
            knowledge: Extracted knowledge for the section
            section: Section information from the research plan
            format: Output format (markdown, html, etc.)
            
        Returns:
            Generated content for the section
        """
        try:
            # Convert knowledge to research data
            research_data = self._create_research_data(knowledge)
            
            # Create section object
            section_obj = Section(
                section_type=SectionType.from_string(section.get("type", "CONTENT")),
                title=section.get("title", "Untitled Section"),
                description=section.get("description", ""),
                content_guidance=section.get("guidance", "")
            )
            
            # Create document structure (needed for section context)
            doc_structure = DocumentStructure(
                title=section.get("document_title", "Research Document"),
                document_type=DocumentType.from_string(section.get("document_type", "RESEARCH_PAPER")),
                sections=[section_obj],
                audience=section.get("audience", "Academic")
            )
            
            # Generate content
            content = self.content_engine.generate_content_for_section(
                section=section_obj,
                document_structure=doc_structure,
                research_data=research_data
            )
            
            # Process citations
            if self.config.get("process_citations", True):
                content = self.content_engine.process_citations(content)
            
            # Return result
            return {
                "content": content,
                "format": format,
                "section_id": section.get("id"),
                "section_title": section.get("title"),
                "metadata": {
                    "generator": "ContentGenerator",
                    "knowledge_entities": len(research_data.entities),
                    "knowledge_relationships": len(research_data.relationships)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            # Return error result
            return {
                "content": f"Error generating content: {e}",
                "format": format,
                "section_id": section.get("id"),
                "section_title": section.get("title"),
                "error": str(e)
            }
    
    def generate_report(self, 
                       project: Project,
                       format: str = "markdown") -> str:
        """
        Generate a complete research report from project results.
        
        Args:
            project: Project instance with results
            format: Output format (markdown, html, pdf)
            
        Returns:
            Complete report as a string
        """
        try:
            # Setup document structure
            document_structure = self._setup_document_structure(project)
            
            # Combine all section content
            sections = []
            for section_id, results in project.results.items():
                if results:
                    sections.append(results[-1].get("content", ""))
            
            # Generate complete document
            if self.config.get("regenerate_document", False):
                # Create combined research data from all sections
                combined_knowledge = self._combine_knowledge(project)
                research_data = self._create_research_data(combined_knowledge)
                
                # Generate complete document
                document = self.content_engine.generate_complete_document(
                    document_structure=document_structure,
                    research_data=research_data
                )
            else:
                # Simply join sections
                document = "\n\n".join(sections)
            
            # Process citations for whole document
            if self.config.get("process_citations", True):
                document = self.content_engine.process_citations(document)
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return f"Error generating report: {e}"
    
    def _setup_document_structure(self, 
                                 project: Project) -> DocumentStructure:
        """
        Create document structure based on project plan.
        
        Args:
            project: Project instance
            
        Returns:
            DocumentStructure object
        """
        # Get document type from plan
        document_type = project.plan.get("document_type", "RESEARCH_PAPER")
        
        # Create sections based on plan
        sections = []
        if "sections" in project.plan:
            for section_id, section_data in project.plan["sections"].items():
                section = Section(
                    section_type=SectionType.from_string(section_data.get("type", "CONTENT")),
                    title=section_data.get("title", "Untitled Section"),
                    description=section_data.get("description", ""),
                    content_guidance=section_data.get("guidance", "")
                )
                sections.append(section)
        
        # Create document structure
        return DocumentStructure(
            title=project.title,
            document_type=DocumentType.from_string(document_type),
            sections=sections,
            audience=project.plan.get("audience", "Academic"),
            target_length=project.plan.get("target_length", "")
        )
    
    def _create_research_data(self, 
                             knowledge: Dict[str, Any]) -> ResearchData:
        """
        Convert knowledge to research data for content synthesis.
        
        Args:
            knowledge: Extracted knowledge
            
        Returns:
            ResearchData object
        """
        # Extract topic from knowledge
        topic = knowledge.get("topic", knowledge.get("query", ""))
        
        # Extract entities
        entities = knowledge.get("entities", [])
        
        # Extract relationships
        relationships = knowledge.get("relationships", [])
        
        # Extract papers
        papers = knowledge.get("papers", [])
        
        # Extract facts
        facts = knowledge.get("facts", [])
        if not facts and "summary" in knowledge:
            # Try to extract facts from summary
            facts = [s.strip() for s in knowledge.get("summary", "").split(".") if s.strip()]
        
        # Extract statistics
        statistics = knowledge.get("statistics", {})
        
        # Extract figures
        figures = knowledge.get("figures", [])
        
        # Create metadata
        metadata = knowledge.get("metadata", {})
        
        # Create research data
        return ResearchData(
            topic=topic,
            entities=entities,
            relationships=relationships,
            papers=papers,
            facts=facts,
            statistics=statistics,
            figures=figures,
            metadata=metadata
        )
    
    def _combine_knowledge(self, project: Project) -> Dict[str, Any]:
        """
        Combine knowledge from all sections.
        
        Args:
            project: Project instance
            
        Returns:
            Combined knowledge dictionary
        """
        # Initialize combined knowledge
        combined = {
            "topic": project.query,
            "entities": [],
            "relationships": [],
            "papers": [],
            "facts": [],
            "statistics": {},
            "figures": [],
            "metadata": project.metadata.copy()
        }
        
        # Track seen entities and papers to avoid duplicates
        seen_entities = set()
        seen_papers = set()
        
        # Combine knowledge from all sections
        for section_id, results in project.results.items():
            if not results:
                continue
                
            # Get the latest result for this section
            result = results[-1]
            
            # Get knowledge for this section from project
            section_knowledge = project.plan.get("sections", {}).get(section_id, {}).get("knowledge", {})
            
            # Add entities
            for entity in section_knowledge.get("entities", []):
                entity_id = entity.get("id") or entity.get("name")
                if entity_id and entity_id not in seen_entities:
                    combined["entities"].append(entity)
                    seen_entities.add(entity_id)
            
            # Add relationships
            combined["relationships"].extend(section_knowledge.get("relationships", []))
            
            # Add papers
            for paper in section_knowledge.get("papers", []):
                paper_id = paper.get("id") or paper.get("title")
                if paper_id and paper_id not in seen_papers:
                    combined["papers"].append(paper)
                    seen_papers.add(paper_id)
            
            # Add facts
            combined["facts"].extend(section_knowledge.get("facts", []))
            
            # Add figures
            combined["figures"].extend(section_knowledge.get("figures", []))
            
            # Update statistics
            combined["statistics"].update(section_knowledge.get("statistics", {}))
        
        return combined