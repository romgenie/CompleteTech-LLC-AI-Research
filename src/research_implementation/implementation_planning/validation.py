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
class ValidationIssue:
    """Represents a validation issue."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now(timezone.utc)

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, issues: List['ValidationIssue']):
        self.issues = issues
        issue_messages = "; ".join(issue.message for issue in issues)
        super().__init__(f"Validation failed: {issue_messages}")

class PlanningValidator:
    """
    Validates implementation plans and tasks.
    """
    
    @staticmethod
    def validate_options(options: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate planning options.
        
        Args:
            options: Planning options dictionary
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Validate language if present
        if "language" in options and not isinstance(options["language"], str):
            issues.append(ValidationIssue(
                code="INVALID_LANGUAGE",
                message="Language must be a string",
                field="language"
            ))
            
        # Validate framework if present
        if "framework" in options and not isinstance(options["framework"], str):
            issues.append(ValidationIssue(
                code="INVALID_FRAMEWORK",
                message="Framework must be a string",
                field="framework"
            ))
            
        # Validate max_tasks if present
        if "max_tasks" in options:
            max_tasks = options["max_tasks"]
            if not isinstance(max_tasks, int) or max_tasks <= 0:
                issues.append(ValidationIssue(
                    code="INVALID_MAX_TASKS",
                    message="max_tasks must be a positive integer",
                    field="max_tasks",
                    details={"value": max_tasks}
                ))
                
        # Validate priority_factors if present
        if "priority_factors" in options:
            factors = options["priority_factors"]
            if not isinstance(factors, dict):
                issues.append(ValidationIssue(
                    code="INVALID_PRIORITY_FACTORS",
                    message="priority_factors must be a dictionary",
                    field="priority_factors"
                ))
            else:
                for key, value in factors.items():
                    if not isinstance(value, (int, float)):
                        issues.append(ValidationIssue(
                            code="INVALID_FACTOR_VALUE",
                            message=f"Priority factor {key} must be a number",
                            field=f"priority_factors.{key}",
                            details={"value": value}
                        ))
        
        # Validate custom_requirements if present
        if "custom_requirements" in options:
            requirements = options["custom_requirements"]
            if not isinstance(requirements, list):
                issues.append(ValidationIssue(
                    code="INVALID_CUSTOM_REQUIREMENTS",
                    message="custom_requirements must be a list",
                    field="custom_requirements"
                ))
            else:
                for i, req in enumerate(requirements):
                    if not isinstance(req, str):
                        issues.append(ValidationIssue(
                            code="INVALID_REQUIREMENT",
                            message=f"Requirement at index {i} must be a string",
                            field=f"custom_requirements[{i}]",
                            details={"value": req}
                        ))
        
        return issues
    
    @staticmethod
    def validate_understanding(understanding: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate research paper understanding input.
        
        Args:
            understanding: Paper understanding dictionary
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check required fields
        required_fields = ["id", "title", "description"]
        for field in required_fields:
            if field not in understanding:
                issues.append(ValidationIssue(
                    code="MISSING_FIELD",
                    message=f"Missing required field: {field}",
                    field=field
                ))
        
        # Check components exist
        if not understanding.get("algorithms") and not understanding.get("architecture"):
            issues.append(ValidationIssue(
                code="NO_COMPONENTS",
                message="No algorithms or architecture components found",
                details={"found_fields": list(understanding.keys())}
            ))
            
        # Validate algorithms if present
        for algo in understanding.get("algorithms", []):
            if not algo.get("name"):
                issues.append(ValidationIssue(
                    code="INVALID_ALGORITHM",
                    message="Algorithm missing name",
                    field="algorithms"
                ))
                
        # Validate architecture if present
        for name, component in understanding.get("architecture", {}).items():
            if not component.get("description"):
                issues.append(ValidationIssue(
                    code="INVALID_COMPONENT",
                    message=f"Architecture component {name} missing description",
                    field="architecture"
                ))
                
        return issues
    
    @staticmethod
    def validate_plan(plan: ImplementationPlan) -> List[ValidationIssue]:
        """
        Validate an implementation plan.
        
        Args:
            plan: The plan to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check required fields
        if not plan.id:
            issues.append(ValidationIssue(
                code="MISSING_ID",
                message="Plan missing ID",
                field="id"
            ))
            
        if not plan.title:
            issues.append(ValidationIssue(
                code="MISSING_TITLE",
                message="Plan missing title",
                field="title"
            ))
            
        # Check components
        if not plan.components:
            issues.append(ValidationIssue(
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
                        issues.append(ValidationIssue(
                            code="INVALID_DEPENDENCY",
                            message=f"Component {component.name} has unknown dependency {dep}",
                            field="dependencies",
                            details={"component": component.name, "dependency": dep}
                        ))
                        
                # Check effort estimation
                if component.estimated_effort not in ["low", "medium", "high"]:
                    issues.append(ValidationIssue(
                        code="INVALID_EFFORT",
                        message=f"Invalid effort level for component {component.name}",
                        field="estimated_effort",
                        details={"component": component.name, "value": component.estimated_effort}
                    ))
                    
        # Check requirements are defined
        if not plan.requirements:
            issues.append(ValidationIssue(
                code="NO_REQUIREMENTS",
                message="Plan has no requirements defined"
            ))
            
        return issues
    
    @staticmethod
    def validate_tasks(tasks: Dict[str, Task], plan: ImplementationPlan) -> List[ValidationIssue]:
        """
        Validate generated tasks.
        
        Args:
            tasks: Dictionary of tasks to validate
            plan: The implementation plan the tasks were generated from
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not tasks:
            issues.append(ValidationIssue(
                code="NO_TASKS",
                message="No tasks generated from plan"
            ))
            return issues
            
        # Track task IDs for dependency validation
        task_ids = set(tasks.keys())
        
        # Check each task
        for task_id, task in tasks.items():
            # Validate dependencies
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    issues.append(ValidationIssue(
                        code="INVALID_TASK_DEPENDENCY",
                        message=f"Task {task.name} has unknown dependency {dep_id}",
                        field="dependencies",
                        details={"task": task.name, "dependency": dep_id}
                    ))
                    
            # Validate estimated hours
            if task.estimated_hours <= 0:
                issues.append(ValidationIssue(
                    code="INVALID_HOURS",
                    message=f"Invalid estimated hours for task {task.name}",
                    field="estimated_hours",
                    details={"task": task.name, "value": task.estimated_hours}
                ))
                
            # Validate priority
            if not 1 <= task.priority <= 5:
                issues.append(ValidationIssue(
                    code="INVALID_PRIORITY",
                    message=f"Invalid priority for task {task.name}",
                    field="priority",
                    details={"task": task.name, "value": task.priority}
                ))
                
            # Validate status
            if task.status not in ["todo", "in_progress", "completed", "blocked"]:
                issues.append(ValidationIssue(
                    code="INVALID_STATUS",
                    message=f"Invalid status for task {task.name}",
                    field="status",
                    details={"task": task.name, "value": task.status}
                ))
                
        return issues
    
    @staticmethod
    def validate_critical_path(critical_path: List[Task], tasks: Dict[str, Task]) -> List[ValidationIssue]:
        """
        Validate a critical path through tasks.
        
        Args:
            critical_path: List of tasks in the critical path
            tasks: Dictionary of all tasks
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not critical_path:
            issues.append(ValidationIssue(
                code="EMPTY_CRITICAL_PATH",
                message="Critical path is empty"
            ))
            return issues
            
        # Check path continuity
        for i in range(len(critical_path) - 1):
            current = critical_path[i]
            next_task = critical_path[i + 1]
            
            # Next task should depend on current task
            if current.id not in next_task.dependencies:
                issues.append(ValidationIssue(
                    code="INVALID_PATH",
                    message=f"Break in critical path between {current.name} and {next_task.name}",
                    details={
                        "current_task": current.name,
                        "next_task": next_task.name
                    }
                ))
                
        return issues