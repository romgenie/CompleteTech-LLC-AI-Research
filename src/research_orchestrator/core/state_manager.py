"""
State management for the Research Orchestration Framework.

This module handles project state persistence and retrieval for the Research
Orchestration Framework.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from src.research_orchestrator.core.utils import ensure_dir, generate_id, load_json, save_json, timestamp


class Project:
    """
    Represents a research project.
    
    Attributes:
        id: Unique identifier for the project
        query: Original research query
        title: Project title
        created_at: Timestamp when the project was created
        updated_at: Timestamp when the project was last updated
        status: Current project status
        plan: Research plan
        results: Research results
        metadata: Additional project metadata
    """
    
    def __init__(
        self,
        query: str,
        title: Optional[str] = None,
        project_id: Optional[str] = None,
        depth: str = "standard",
        focus_areas: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new project.
        
        Args:
            query: Research query
            title: Project title (generated from query if not provided)
            project_id: Unique identifier (generated if not provided)
            depth: Research depth ("quick", "standard", "comprehensive")
            focus_areas: Specific areas to focus on
            metadata: Additional project metadata
        """
        self.id = project_id or generate_id()
        self.query = query
        self.title = title or f"Research: {query[:50]}..."
        self.created_at = timestamp()
        self.updated_at = self.created_at
        self.status = "created"
        self.depth = depth
        self.focus_areas = focus_areas or []
        self.plan = {}
        self.results = {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the project to a dictionary.
        
        Returns:
            Dictionary representation of the project
        """
        return {
            "id": self.id,
            "query": self.query,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
            "depth": self.depth,
            "focus_areas": self.focus_areas,
            "plan": self.plan,
            "results": self.results,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """
        Create a project from a dictionary.
        
        Args:
            data: Dictionary containing project data
            
        Returns:
            Project instance
        """
        project = cls(
            query=data["query"],
            title=data["title"],
            project_id=data["id"],
            depth=data.get("depth", "standard"),
            focus_areas=data.get("focus_areas", []),
            metadata=data.get("metadata", {}),
        )
        project.created_at = data["created_at"]
        project.updated_at = data["updated_at"]
        project.status = data["status"]
        project.plan = data.get("plan", {})
        project.results = data.get("results", {})
        return project
    
    def update_status(self, status: str) -> None:
        """
        Update the project status.
        
        Args:
            status: New project status
        """
        self.status = status
        self.updated_at = timestamp()
    
    def set_plan(self, plan: Dict[str, Any]) -> None:
        """
        Set the research plan.
        
        Args:
            plan: Research plan
        """
        self.plan = plan
        self.updated_at = timestamp()
        if self.status == "created":
            self.update_status("planned")
    
    def add_result(self, section: str, result: Dict[str, Any]) -> None:
        """
        Add a research result.
        
        Args:
            section: Section identifier
            result: Research result
        """
        if section not in self.results:
            self.results[section] = []
        self.results[section].append(result)
        self.updated_at = timestamp()
        
        # Update status if all sections have results
        if self.plan and "sections" in self.plan:
            if all(section in self.results for section in self.plan["sections"]):
                self.update_status("completed")
            else:
                self.update_status("in_progress")


class StateManager:
    """
    Manages project state persistence and retrieval.
    """
    
    def __init__(self, storage_dir: Union[str, Path] = "data/projects"):
        """
        Initialize the state manager.
        
        Args:
            storage_dir: Directory to store project data
        """
        self.storage_dir = ensure_dir(storage_dir)
        logger.info(f"Initialized StateManager with storage directory: {self.storage_dir}")
    
    def save_project(self, project: Project) -> None:
        """
        Save a project to storage.
        
        Args:
            project: Project to save
        """
        project_path = self.storage_dir / f"{project.id}.json"
        save_json(project.to_dict(), project_path)
        logger.debug(f"Saved project {project.id} to {project_path}")
    
    def load_project(self, project_id: str) -> Project:
        """
        Load a project from storage.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project instance
            
        Raises:
            FileNotFoundError: If the project doesn't exist
        """
        project_path = self.storage_dir / f"{project_id}.json"
        try:
            project_data = load_json(project_path)
            return Project.from_dict(project_data)
        except FileNotFoundError:
            logger.error(f"Project {project_id} not found at {project_path}")
            raise
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of project summary dictionaries
        """
        projects = []
        for project_file in self.storage_dir.glob("*.json"):
            try:
                project_data = load_json(project_file)
                projects.append({
                    "id": project_data["id"],
                    "title": project_data["title"],
                    "created_at": project_data["created_at"],
                    "updated_at": project_data["updated_at"],
                    "status": project_data["status"],
                })
            except Exception as e:
                logger.warning(f"Error loading project from {project_file}: {e}")
        
        # Sort by updated_at in descending order
        projects.sort(key=lambda p: p["updated_at"], reverse=True)
        return projects
    
    def delete_project(self, project_id: str) -> None:
        """
        Delete a project.
        
        Args:
            project_id: Project ID
            
        Raises:
            FileNotFoundError: If the project doesn't exist
        """
        project_path = self.storage_dir / f"{project_id}.json"
        if not project_path.exists():
            raise FileNotFoundError(f"Project {project_id} not found at {project_path}")
        
        project_path.unlink()
        logger.info(f"Deleted project {project_id}")