"""
Planning service that coordinates implementation planning activities.

This module provides the service layer for implementation planning, coordinating
between different planning components and integrating with other systems.
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timezone
import json
from pathlib import Path

from .planner import ImplementationPlanner, ImplementationPlan, ImplementationComponent
from .task_planner import TaskPlanner, Task
from .validation import PlanningValidator, ValidationError

logger = logging.getLogger(__name__)

class PlanningError(Exception):
    """Base exception for planning errors."""
    pass

class ValidationError(PlanningError):
    """Raised when validation fails."""
    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        error_messages = "; ".join(e.message for e in errors)
        super().__init__(f"Validation failed: {error_messages}")

class StorageError(PlanningError):
    """Raised when storage operations fail."""
    pass

class PlanningService:
    """
    Service for coordinating implementation planning activities.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the planning service.
        
        Args:
            storage_dir: Directory for storing plans (optional)
        """
        self.planner = ImplementationPlanner()
        self.task_planner = TaskPlanner()
        self.validator = PlanningValidator()
        
        # Set storage directory
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".research_implementation" / "plans"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_implementation_plan(
        self, 
        understanding: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete implementation plan with tasks.
        
        Args:
            understanding: Results from paper understanding phase
            options: Additional planning options
            
        Returns:
            Dictionary containing the plan and generated tasks
            
        Raises:
            ValidationError: If validation fails
            PlanningError: If plan creation fails
            StorageError: If plan storage fails
        """
        # Validate understanding input
        validation_errors = self.validator.validate_understanding(understanding)
        if validation_errors:
            raise ValidationError(validation_errors)
            
        # Validate options if provided
        if options:
            validation_errors = self.validator.validate_options(options)
            if validation_errors:
                raise ValidationError(validation_errors)
        
        try:
            # Generate basic implementation plan
            plan = self.planner.create_plan(understanding)
            
            # Validate plan
            validation_errors = self.validator.validate_plan(plan)
            if validation_errors:
                raise ValidationError(validation_errors)
            
            # Generate tasks
            tasks = self.task_planner.generate_tasks(plan)
            
            # Validate tasks
            validation_errors = self.validator.validate_tasks(tasks, plan)
            if validation_errors:
                raise ValidationError(validation_errors)
            
            # Calculate critical path
            critical_path = self.task_planner.get_critical_path()
            
            # Validate critical path
            validation_errors = self.validator.validate_critical_path(critical_path, tasks)
            if validation_errors:
                raise ValidationError(validation_errors)
            
            # Organize results
            result = {
                "plan": {
                    "id": plan.id,
                    "title": plan.title,
                    "description": plan.description,
                    "components": [
                        {
                            "name": c.name,
                            "description": c.description,
                            "dependencies": c.dependencies,
                            "requirements": c.requirements,
                            "estimated_effort": c.estimated_effort,
                            "priority": c.priority,
                            "status": c.status
                        }
                        for c in plan.components
                    ],
                    "requirements": plan.requirements,
                    "estimated_timeline": plan.estimated_timeline,
                    "status": plan.status
                },
                "tasks": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "description": t.description,
                        "component": t.component,
                        "dependencies": t.dependencies,
                        "estimated_hours": t.estimated_hours,
                        "priority": t.priority,
                        "status": t.status
                    }
                    for t in tasks.values()
                ],
                "critical_path": [t.id for t in critical_path],
                "validation": {
                    "is_valid": True,
                    "plan_issues": self.validator.validate_plan(plan),
                    "task_issues": self.validator.validate_tasks(tasks, plan),
                    "critical_path_issues": self.validator.validate_critical_path(critical_path, tasks)
                },
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source_paper": understanding.get("paper_id", "unknown"),
                    "planning_options": options or {}
                }
            }
            
            # Save plan
            try:
                self._save_plan(plan.id, result)
            except Exception as e:
                raise StorageError(f"Failed to save plan: {str(e)}")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            raise PlanningError(f"Failed to create implementation plan: {str(e)}")
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a saved implementation plan.
        
        Args:
            plan_id: ID of plan to retrieve
            
        Returns:
            Dictionary containing the plan or None if not found
            
        Raises:
            StorageError: If plan retrieval fails
        """
        plan_file = self.storage_dir / f"{plan_id}.json"
        if not plan_file.exists():
            return None
            
        try:
            with open(plan_file) as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load plan {plan_id}: {str(e)}")
    
    def update_plan(
        self, 
        plan_id: str, 
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing implementation plan.
        
        Args:
            plan_id: ID of plan to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated plan dictionary or None if plan not found
            
        Raises:
            ValidationError: If validation fails
            StorageError: If plan storage fails
        """
        current_plan = self.get_plan(plan_id)
        if not current_plan:
            return None
            
        # Apply updates
        for key, value in updates.items():
            if key in current_plan["plan"]:
                current_plan["plan"][key] = value
                
        # Update metadata
        current_plan["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Validate updated plan
        plan_obj = ImplementationPlan(
            id=current_plan["plan"]["id"],
            title=current_plan["plan"]["title"],
            description=current_plan["plan"]["description"],
            components=[
                ImplementationComponent(
                    name=c["name"],
                    description=c["description"],
                    dependencies=c.get("dependencies", []),
                    requirements=c.get("requirements", {}),
                    estimated_effort=c.get("estimated_effort", "medium"),
                    priority=c.get("priority", "medium"),
                    status=c.get("status", "planned")
                )
                for c in current_plan["plan"]["components"]
            ],
            requirements=current_plan["plan"]["requirements"]
        )
        validation_errors = self.validator.validate_plan(plan_obj)
        if validation_errors:
            raise ValidationError(validation_errors)
        
        # Save updated plan
        try:
            self._save_plan(plan_id, current_plan)
        except Exception as e:
            raise StorageError(f"Failed to save updated plan: {str(e)}")
        
        return current_plan
    
    def update_task(
        self,
        plan_id: str,
        task_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a task in an implementation plan.
        
        Args:
            plan_id: ID of the plan containing the task
            task_id: ID of task to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated plan dictionary or None if not found
            
        Raises:
            ValidationError: If validation fails
            StorageError: If plan storage fails
        """
        current_plan = self.get_plan(plan_id)
        if not current_plan:
            return None
            
        # Find and update task
        task_found = False
        for task in current_plan["tasks"]:
            if task["id"] == task_id:
                task_found = True
                for key, value in updates.items():
                    task[key] = value  # Allow adding new fields like 'assignee'
                break
                
        if not task_found:
            logger.warning(f"Task {task_id} not found in plan {plan_id}")
            return None
            
        # Validate updated tasks
        tasks = {}
        for t in current_plan["tasks"]:
            # Extract the core fields needed for Task
            task_kwargs = {
                "id": t["id"],
                "name": t["name"],
                "description": t["description"],
                "component": t.get("component", ""),
                "dependencies": t.get("dependencies", []),
                "estimated_hours": t.get("estimated_hours", 1.0),
                "priority": t.get("priority", 3),
                "status": t.get("status", "todo")
            }
            
            # Create the Task
            tasks[t["id"]] = Task(**task_kwargs)
        plan_obj = ImplementationPlan(
            id=current_plan["plan"]["id"],
            title=current_plan["plan"]["title"],
            description=current_plan["plan"]["description"],
            components=[
                ImplementationComponent(
                    name=c["name"],
                    description=c["description"],
                    dependencies=c.get("dependencies", []),
                    requirements=c.get("requirements", {}),
                    estimated_effort=c.get("estimated_effort", "medium"),
                    priority=c.get("priority", "medium"),
                    status=c.get("status", "planned")
                )
                for c in current_plan["plan"]["components"]
            ],
            requirements=current_plan["plan"]["requirements"]
        )
        validation_errors = self.validator.validate_tasks(tasks, plan_obj)
        if validation_errors:
            raise ValidationError(validation_errors)
            
        # Update metadata
        current_plan["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Save updated plan
        try:
            self._save_plan(plan_id, current_plan)
        except Exception as e:
            raise StorageError(f"Failed to save updated plan: {str(e)}")
        
        return current_plan
    
    def delete_plan(self, plan_id: str) -> bool:
        """
        Delete a saved implementation plan.
        
        Args:
            plan_id: ID of plan to delete
            
        Returns:
            True if plan was deleted, False otherwise
            
        Raises:
            StorageError: If plan deletion fails
        """
        plan_file = self.storage_dir / f"{plan_id}.json"
        try:
            if plan_file.exists():
                plan_file.unlink()
                return True
            return False
        except Exception as e:
            raise StorageError(f"Failed to delete plan {plan_id}: {str(e)}")
    
    def list_plans(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List implementation plans with pagination and filtering.
        
        Args:
            skip: Number of plans to skip for pagination
            limit: Maximum number of plans to return
            filters: Dictionary of filters to apply
            
        Returns:
            List of plan dictionaries
            
        Raises:
            StorageError: If plan listing fails
        """
        try:
            # Get all plan files
            plan_files = list(self.storage_dir.glob("*.json"))
            
            # Load each plan
            plans = []
            for file_path in plan_files:
                try:
                    with open(file_path) as f:
                        plan_data = json.load(f)
                        plans.append(plan_data)
                except Exception as e:
                    logger.warning(f"Failed to load plan {file_path.stem}: {str(e)}")
            
            # Apply filters if provided
            if filters:
                filtered_plans = []
                for plan in plans:
                    include_plan = True
                    
                    # Filter by status
                    if "status" in filters and plan["plan"]["status"] != filters["status"]:
                        include_plan = False
                        
                    # Filter by search term
                    if "search" in filters:
                        search_term = filters["search"].lower()
                        title = plan["plan"]["title"].lower()
                        description = plan["plan"]["description"].lower()
                        
                        if search_term not in title and search_term not in description:
                            include_plan = False
                    
                    if include_plan:
                        filtered_plans.append(plan)
                        
                plans = filtered_plans
            
            # Apply pagination
            paginated_plans = plans[skip:skip + limit]
            
            return paginated_plans
            
        except Exception as e:
            raise StorageError(f"Failed to list plans: {str(e)}")
    
    def count_plans(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count plans matching the given filters.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Number of matching plans
            
        Raises:
            StorageError: If plan counting fails
        """
        try:
            # Get filtered plans
            filtered_plans = self.list_plans(skip=0, limit=1000, filters=filters)
            return len(filtered_plans)
            
        except Exception as e:
            raise StorageError(f"Failed to count plans: {str(e)}")
    
    def _save_plan(self, plan_id: str, plan_data: Dict[str, Any]) -> None:
        """Save plan data to storage."""
        plan_file = self.storage_dir / f"{plan_id}.json"
        try:
            with open(plan_file, 'w') as f:
                json.dump(plan_data, f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save plan {plan_id}: {str(e)}")