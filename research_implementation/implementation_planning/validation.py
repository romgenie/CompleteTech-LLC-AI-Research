"""
Validation utilities for implementation planning.

This module provides validation functions and error handling for the implementation
planning system, ensuring plans and tasks meet requirements and constraints.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from .planner import ImplementationPlan, ImplementationComponent
from .task_planner import Task

@dataclass
class ValidationError:
    """Represents a validation error."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now(timezone.utc)

class PlanningValidator:
    """
    Validates implementation plans and tasks.
    """
    
    @staticmethod
    def validate_options(options: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate planning options.
        
        Args:
            options: Planning options dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate language if present
        if "language" in options and not isinstance(options["language"], str):
            errors.append(ValidationError(
                code="INVALID_LANGUAGE",
                message="Language must be a string",
                field="language"
            ))
            
        # Validate framework if present
        if "framework" in options and not isinstance(options["framework"], str):
            errors.append(ValidationError(
                code="INVALID_FRAMEWORK",
                message="Framework must be a string",
                field="framework"
            ))
            
        # Validate max_tasks if present
        if "max_tasks" in options:
            max_tasks = options["max_tasks"]
            if not isinstance(max_tasks, int) or max_tasks <= 0:
                errors.append(ValidationError(
                    code="INVALID_MAX_TASKS",
                    message="max_tasks must be a positive integer",
                    field="max_tasks",
                    details={"value": max_tasks}
                ))
                
        # Validate priority_factors if present
        if "priority_factors" in options:
            factors = options["priority_factors"]
            if not isinstance(factors, dict):
                errors.append(ValidationError(
                    code="INVALID_PRIORITY_FACTORS",
                    message="priority_factors must be a dictionary",
                    field="priority_factors"
                ))
            else:
                for key, value in factors.items():
                    if not isinstance(value, (int, float)):
                        errors.append(ValidationError(
                            code="INVALID_FACTOR_VALUE",
                            message=f"Priority factor {key} must be a number",
                            field=f"priority_factors.{key}",
                            details={"value": value}
                        ))
        
        # Validate custom_requirements if present
        if "custom_requirements" in options:
            requirements = options["custom_requirements"]
            if not isinstance(requirements, list):
                errors.append(ValidationError(
                    code="INVALID_CUSTOM_REQUIREMENTS",
                    message="custom_requirements must be a list",
                    field="custom_requirements"
                ))
            else:
                for i, req in enumerate(requirements):
                    if not isinstance(req, str):
                        errors.append(ValidationError(
                            code="INVALID_REQUIREMENT",
                            message=f"Requirement at index {i} must be a string",
                            field=f"custom_requirements[{i}]",
                            details={"value": req}
                        ))
        
        return errors
    
    @staticmethod
    def validate_understanding(understanding: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate research paper understanding input.
        
        Args:
            understanding: Paper understanding dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required fields
        required_fields = ["id", "title", "description"]
        for field in required_fields:
            if field not in understanding:
                errors.append(ValidationError(
                    code="MISSING_FIELD",
                    message=f"Missing required field: {field}",
                    field=field
                ))
        
        # Check components exist
        if not understanding.get("algorithms") and not understanding.get("architecture"):
            errors.append(ValidationError(
                code="NO_COMPONENTS",
                message="No algorithms or architecture components found",
                details={"found_fields": list(understanding.keys())}
            ))
            
        # Validate algorithms if present
        for algo in understanding.get("algorithms", []):
            if not algo.get("name"):
                errors.append(ValidationError(
                    code="INVALID_ALGORITHM",
                    message="Algorithm missing name",
                    field="algorithms"
                ))
                
        # Validate architecture if present
        for name, component in understanding.get("architecture", {}).items():
            if not component.get("description"):
                errors.append(ValidationError(
                    code="INVALID_COMPONENT",
                    message=f"Architecture component {name} missing description",
                    field="architecture"
                ))
                
        return errors
    
    @staticmethod
    def validate_plan(plan: ImplementationPlan) -> List[ValidationError]:
        """
        Validate an implementation plan.
        
        Args:
            plan: The plan to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check required fields
        if not plan.id:
            errors.append(ValidationError(
                code="MISSING_ID",
                message="Plan missing ID",
                field="id"
            ))
            
        if not plan.title:
            errors.append(ValidationError(
                code="MISSING_TITLE",
                message="Plan missing title",
                field="title"
            ))
            
        # Check components
        if not plan.components:
            errors.append(ValidationError(
                code="NO_COMPONENTS",
                message="Plan has no components defined"
            ))
        else:
            # Validate individual components
            component_names = {c.name for c in plan.components}
            for component in plan.components:
                # Check dependencies
                for dep in component.dependencies:
                    if dep not in component_names:
                        errors.append(ValidationError(
                            code="INVALID_DEPENDENCY",
                            message=f"Component {component.name} has unknown dependency {dep}",
                            field="dependencies",
                            details={"component": component.name, "dependency": dep}
                        ))
                        
                # Check effort estimation
                if component.estimated_effort not in ["low", "medium", "high"]:
                    errors.append(ValidationError(
                        code="INVALID_EFFORT",
                        message=f"Invalid effort level for component {component.name}",
                        field="estimated_effort",
                        details={"component": component.name, "value": component.estimated_effort}
                    ))
                    
        # Check requirements are defined
        if not plan.requirements:
            errors.append(ValidationError(
                code="NO_REQUIREMENTS",
                message="Plan has no requirements defined"
            ))
            
        return errors
    
    @staticmethod
    def validate_tasks(tasks: Dict[str, Task], plan: ImplementationPlan) -> List[ValidationError]:
        """
        Validate generated tasks.
        
        Args:
            tasks: Dictionary of tasks to validate
            plan: The implementation plan the tasks were generated from
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not tasks:
            errors.append(ValidationError(
                code="NO_TASKS",
                message="No tasks generated from plan"
            ))
            return errors
            
        # Track task IDs for dependency validation
        task_ids = set(tasks.keys())
        
        # Check each task
        for task_id, task in tasks.items():
            # Validate dependencies
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    errors.append(ValidationError(
                        code="INVALID_TASK_DEPENDENCY",
                        message=f"Task {task.name} has unknown dependency {dep_id}",
                        field="dependencies",
                        details={"task": task.name, "dependency": dep_id}
                    ))
                    
            # Validate estimated hours
            if task.estimated_hours <= 0:
                errors.append(ValidationError(
                    code="INVALID_HOURS",
                    message=f"Invalid estimated hours for task {task.name}",
                    field="estimated_hours",
                    details={"task": task.name, "value": task.estimated_hours}
                ))
                
            # Validate priority
            if not 1 <= task.priority <= 5:
                errors.append(ValidationError(
                    code="INVALID_PRIORITY",
                    message=f"Invalid priority for task {task.name}",
                    field="priority",
                    details={"task": task.name, "value": task.priority}
                ))
                
            # Validate status
            if task.status not in ["todo", "in_progress", "completed", "blocked"]:
                errors.append(ValidationError(
                    code="INVALID_STATUS",
                    message=f"Invalid status for task {task.name}",
                    field="status",
                    details={"task": task.name, "value": task.status}
                ))
                
        return errors
    
    @staticmethod
    def validate_critical_path(critical_path: List[Task], tasks: Dict[str, Task]) -> List[ValidationError]:
        """
        Validate a critical path through tasks.
        
        Args:
            critical_path: List of tasks in the critical path
            tasks: Dictionary of all tasks
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not critical_path:
            errors.append(ValidationError(
                code="EMPTY_CRITICAL_PATH",
                message="Critical path is empty"
            ))
            return errors
            
        # Check path continuity
        for i in range(len(critical_path) - 1):
            current = critical_path[i]
            next_task = critical_path[i + 1]
            
            # Next task should depend on current task
            if current.id not in next_task.dependencies:
                errors.append(ValidationError(
                    code="INVALID_PATH",
                    message=f"Break in critical path between {current.name} and {next_task.name}",
                    details={
                        "current_task": current.name,
                        "next_task": next_task.name
                    }
                ))
                
        return errors