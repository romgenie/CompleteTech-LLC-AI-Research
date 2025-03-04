"""
Main orchestration controller for the Research Orchestration Framework.

This module contains the ResearchOrchestrator class, which coordinates the execution
of research workflows across all modules.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from research_orchestrator.core.state_manager import Project, StateManager
from research_orchestrator.core.utils import load_config, setup_logging


class ResearchOrchestrator:
    """
    Main controller class that coordinates the research workflow.
    
    This class manages the interaction between different modules of the
    Research Orchestration Framework and executes the research workflow.
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize the research orchestrator.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        # Set up logging
        setup_logging()
        
        # Load configuration
        if config_path:
            self.config = load_config(config_path)
        else:
            # Try to load from default locations
            default_paths = [
                "config/default_config.yaml",
                "../config/default_config.yaml",
                os.path.expanduser("~/.config/research_orchestrator/config.yaml"),
            ]
            
            for path in default_paths:
                try:
                    self.config = load_config(path)
                    logger.info(f"Loaded configuration from {path}")
                    break
                except FileNotFoundError:
                    continue
            else:
                # No configuration found, use defaults
                self.config = {
                    "storage_dir": "data/projects",
                    "log_level": "INFO",
                }
                logger.warning("No configuration file found, using defaults")
        
        # Initialize state manager
        self.state_manager = StateManager(self.config.get("storage_dir", "data/projects"))
        
        # Initialize module controllers (will be loaded on demand)
        self._research_planning = None
        self._information_gathering = None
        self._knowledge_extraction = None
        self._knowledge_integration = None
        self._research_generation = None
        
        logger.info("Research Orchestrator initialized")
    
    def create_project(
        self,
        query: str,
        title: Optional[str] = None,
        depth: str = "standard",
        focus_areas: Optional[List[str]] = None,
    ) -> Project:
        """
        Create a new research project.
        
        Args:
            query: Research query
            title: Project title (optional)
            depth: Research depth ("quick", "standard", "comprehensive")
            focus_areas: Specific areas to focus on (optional)
            
        Returns:
            Newly created Project instance
        """
        logger.info(f"Creating new project for query: {query}")
        
        # Validate depth
        valid_depths = ["quick", "standard", "comprehensive"]
        if depth not in valid_depths:
            logger.warning(f"Invalid depth '{depth}', using 'standard'")
            depth = "standard"
        
        # Create project
        project = Project(
            query=query,
            title=title,
            depth=depth,
            focus_areas=focus_areas,
        )
        
        # Save project
        self.state_manager.save_project(project)
        logger.info(f"Created project {project.id}")
        
        return project
    
    def get_project(self, project_id: str) -> Project:
        """
        Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project instance
            
        Raises:
            FileNotFoundError: If the project doesn't exist
        """
        return self.state_manager.load_project(project_id)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of project summary dictionaries
        """
        return self.state_manager.list_projects()
    
    def delete_project(self, project_id: str) -> None:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Raises:
            FileNotFoundError: If the project doesn't exist
        """
        self.state_manager.delete_project(project_id)
    
    def generate_research_plan(self, project_id: str) -> Dict[str, Any]:
        """
        Generate a research plan for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Research plan
            
        Raises:
            FileNotFoundError: If the project doesn't exist
            ValueError: If the research planning module is not available
        """
        # Load the project
        project = self.get_project(project_id)
        logger.info(f"Generating research plan for project {project_id}")
        
        # Get the research planning module
        research_planning = self._get_research_planning()
        
        # Generate the plan
        plan = research_planning.generate_plan(
            query=project.query,
            depth=project.depth,
            focus_areas=project.focus_areas,
        )
        
        # Update and save the project
        project.set_plan(plan)
        self.state_manager.save_project(project)
        
        return plan
    
    def execute_workflow(self, project_id: str) -> None:
        """
        Execute the research workflow for a project.
        
        This method coordinates the execution of the research workflow across all modules.
        
        Args:
            project_id: Project ID
            
        Raises:
            FileNotFoundError: If the project doesn't exist
            ValueError: If the project doesn't have a research plan
        """
        # Load the project
        project = self.get_project(project_id)
        logger.info(f"Executing research workflow for project {project_id}")
        
        # Check if the project has a plan
        if not project.plan:
            raise ValueError(f"Project {project_id} doesn't have a research plan")
        
        # Update project status
        project.update_status("in_progress")
        self.state_manager.save_project(project)
        
        # Execute the workflow
        try:
            # For each section in the plan, gather information, extract knowledge,
            # integrate it, and generate research content
            for section_id, section in project.plan.get("sections", {}).items():
                logger.info(f"Processing section {section_id}: {section.get('title')}")
                
                try:
                    # Gather information with error handling
                    try:
                        information = self._get_information_gathering().gather_information(
                            query=section.get("query", ""),
                            scope=section.get("scope", {}),
                        )
                    except Exception as info_error:
                        logger.error(f"Error gathering information for section {section_id}: {info_error}")
                        information = {"error": str(info_error), "content": f"Failed to gather information: {info_error}"}
                    
                    # Extract knowledge with error handling
                    try:
                        knowledge = self._get_knowledge_extraction().extract_knowledge(
                            information=information,
                            query=section.get("query", ""),
                        )
                    except Exception as extract_error:
                        logger.error(f"Error extracting knowledge for section {section_id}: {extract_error}")
                        knowledge = {
                            "error": str(extract_error),
                            "topic": section.get("query", ""),
                            "summary": f"Failed to extract knowledge: {extract_error}"
                        }
                    
                    # Integrate knowledge with error handling
                    try:
                        integrated_knowledge = self._get_knowledge_integration().integrate_knowledge(
                            knowledge=knowledge,
                            context=project.plan,
                        )
                    except Exception as integrate_error:
                        logger.error(f"Error integrating knowledge for section {section_id}: {integrate_error}")
                        integrated_knowledge = knowledge
                        integrated_knowledge["error"] = str(integrate_error)
                    
                    # Generate research content with error handling
                    try:
                        result = self._get_research_generation().generate_content(
                            knowledge=integrated_knowledge,
                            section=section,
                            format=project.plan.get("format", "markdown"),
                        )
                    except Exception as generate_error:
                        logger.error(f"Error generating content for section {section_id}: {generate_error}")
                        result = {
                            "content": f"# {section.get('title', 'Section')}\n\nError generating content: {generate_error}",
                            "format": project.plan.get("format", "markdown"),
                            "section_id": section_id,
                            "section_title": section.get("title", "Section"),
                            "error": str(generate_error)
                        }
                    
                    # Store knowledge in section for later use in report generation
                    if "sections" in project.plan and section_id in project.plan["sections"]:
                        if "knowledge" not in project.plan["sections"][section_id]:
                            project.plan["sections"][section_id]["knowledge"] = {}
                        
                        # Store the integrated knowledge
                        project.plan["sections"][section_id]["knowledge"] = integrated_knowledge
                    
                    # Add result to project
                    project.add_result(section_id, result)
                    self.state_manager.save_project(project)
                    
                except Exception as section_error:
                    logger.error(f"Error processing section {section_id}: {section_error}")
                    # Create a minimal error result for this section
                    error_result = {
                        "content": f"# {section.get('title', 'Section')}\n\nError processing section: {section_error}",
                        "format": project.plan.get("format", "markdown"),
                        "section_id": section_id,
                        "section_title": section.get("title", "Section"),
                        "error": str(section_error)
                    }
                    project.add_result(section_id, error_result)
                    self.state_manager.save_project(project)
                    
                    # Continue processing other sections instead of failing the whole workflow
                    continue
            
            # Generate the full research report
            try:
                logger.info(f"Generating complete research report for project {project_id}")
                report = self._get_research_generation().generate_report(
                    project=project,
                    format=project.plan.get("format", "markdown")
                )
                
                # Add the full report as a special result
                project.add_result("full_report", {
                    "content": report,
                    "format": project.plan.get("format", "markdown"),
                    "section_id": "full_report",
                    "section_title": "Complete Research Report",
                    "metadata": {
                        "generator": "ContentGenerator",
                        "timestamp": self.state_manager.timestamp()
                    }
                })
            except Exception as report_error:
                logger.error(f"Error generating complete report: {report_error}")
                # The workflow can still be considered completed even if the report generation fails
                
            # Update project status to completed
            project.update_status("completed")
            self.state_manager.save_project(project)
            logger.info(f"Research workflow completed for project {project_id}")
            
        except Exception as e:
            # Update project status to failed
            project.update_status("failed")
            project.metadata["error"] = str(e)
            self.state_manager.save_project(project)
            logger.error(f"Research workflow failed for project {project_id}: {e}")
            raise
    
    def get_report(self, project_id: str, format: str = "markdown") -> str:
        """
        Get the final research report for a project.
        
        Args:
            project_id: Project ID
            format: Report format ("markdown", "html", "pdf")
            
        Returns:
            Research report as a string
            
        Raises:
            FileNotFoundError: If the project doesn't exist
            ValueError: If the project doesn't have results or is not completed
        """
        # Load the project
        project = self.get_project(project_id)
        
        # Check if the project is completed
        if project.status != "completed":
            raise ValueError(f"Project {project_id} is not completed (status: {project.status})")
        
        # Check if the project has results
        if not project.results:
            raise ValueError(f"Project {project_id} doesn't have results")
        
        # Generate the report
        return self._get_research_generation().generate_report(
            project=project,
            format=format,
        )
    
    def _get_research_planning(self):
        """
        Get the research planning module.
        
        Returns:
            Research planning module instance
            
        Raises:
            ValueError: If the research planning module is not available
        """
        if self._research_planning is None:
            try:
                # Dynamically import to avoid circular imports
                from research_orchestrator.research_planning.research_plan_generator import ResearchPlanGenerator
                self._research_planning = ResearchPlanGenerator()
            except ImportError:
                logger.error("Research planning module not available")
                raise ValueError("Research planning module not available")
        
        return self._research_planning
    
    def _get_information_gathering(self):
        """
        Get the information gathering module.
        
        Returns:
            Information gathering module instance
            
        Raises:
            ValueError: If the information gathering module is not available
        """
        if self._information_gathering is None:
            try:
                # Dynamically import to avoid circular imports
                from research_orchestrator.information_gathering.information_gatherer import InformationGatherer
                self._information_gathering = InformationGatherer()
            except ImportError:
                # Create a mock implementation for development
                logger.warning("Using mock information gathering module")
                
                class MockInformationGatherer:
                    def gather_information(self, query, scope):
                        return {"sources": [], "content": f"Mock information for query: {query}"}
                
                self._information_gathering = MockInformationGatherer()
        
        return self._information_gathering
    
    def _get_knowledge_extraction(self):
        """
        Get the knowledge extraction module.
        
        Returns:
            Knowledge extraction module instance
            
        Raises:
            ValueError: If the knowledge extraction module is not available
        """
        if self._knowledge_extraction is None:
            try:
                # Dynamically import to avoid circular imports
                from research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
                self._knowledge_extraction = KnowledgeExtractor()
            except ImportError:
                # Create a mock implementation for development
                logger.warning("Using mock knowledge extraction module")
                
                class MockKnowledgeExtractor:
                    def extract_knowledge(self, information, query):
                        return {"entities": [], "relationships": [], "summary": f"Mock knowledge for query: {query}"}
                
                self._knowledge_extraction = MockKnowledgeExtractor()
        
        return self._knowledge_extraction
    
    def _get_knowledge_integration(self):
        """
        Get the knowledge integration module.
        
        Returns:
            Knowledge integration module instance
            
        Raises:
            ValueError: If the knowledge integration module is not available
        """
        if self._knowledge_integration is None:
            try:
                # Dynamically import to avoid circular imports
                from research_orchestrator.knowledge_integration.knowledge_integrator import KnowledgeIntegrator
                self._knowledge_integration = KnowledgeIntegrator()
            except ImportError:
                # Create a mock implementation for development
                logger.warning("Using mock knowledge integration module")
                
                class MockKnowledgeIntegrator:
                    def integrate_knowledge(self, knowledge, context):
                        return {"integrated": True, "content": knowledge.get("summary", "")}
                
                self._knowledge_integration = MockKnowledgeIntegrator()
        
        return self._knowledge_integration
    
    def _get_research_generation(self):
        """
        Get the research generation module.
        
        Returns:
            Research generation module instance
            
        Raises:
            ValueError: If the research generation module is not available
        """
        if self._research_generation is None:
            try:
                # Dynamically import to avoid circular imports
                from research_orchestrator.research_generation.content_generator import ContentGenerator
                self._research_generation = ContentGenerator()
            except ImportError:
                # Create a mock implementation for development
                logger.warning("Using mock research generation module")
                
                class MockContentGenerator:
                    def generate_content(self, knowledge, section, format):
                        return {
                            "content": f"# {section.get('title', 'Section')}\n\n{knowledge.get('content', '')}",
                            "format": format,
                        }
                    
                    def generate_report(self, project, format):
                        sections = []
                        for section_id, results in project.results.items():
                            if results:
                                sections.append(results[-1].get("content", ""))
                        
                        return "\n\n".join(sections)
                
                self._research_generation = MockContentGenerator()
        
        return self._research_generation