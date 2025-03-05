"""
Implementation Planning System for converting research paper understanding into actionable plans.

This module provides the core planning functionality for converting paper understanding
into structured implementation plans with components, tasks, and requirements.
"""

from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ImplementationComponent:
    """A component identified for implementation."""
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    estimated_effort: str = "medium"
    priority: str = "medium"
    status: str = "planned"

@dataclass 
class ImplementationPlan:
    """Complete implementation plan for a research paper."""
    id: str
    title: str
    description: str
    components: List[ImplementationComponent] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    estimated_timeline: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "draft"

class ImplementationPlanner:
    """
    Plans the implementation of research papers based on paper understanding results.
    """
    
    def __init__(self):
        """Initialize the implementation planner."""
        self.current_plan = None
    
    def create_plan(self, understanding: Dict[str, Any]) -> ImplementationPlan:
        """
        Create an implementation plan from paper understanding results.
        
        Args:
            understanding: Results from paper understanding phase
            
        Returns:
            ImplementationPlan with components and requirements
        """
        # Extract key information
        algorithms = understanding.get("algorithms", [])
        architecture = understanding.get("architecture", {})
        implementation_details = understanding.get("implementation_details", {})
        evaluation = understanding.get("evaluation_methodology", {})
        
        # Create plan
        plan = ImplementationPlan(
            id=understanding.get("id", ""),
            title=f"Implementation Plan: {understanding.get('title', 'Untitled')}",
            description=understanding.get("description", ""),
        )
        
        # Add components from algorithms
        for algo in algorithms:
            component = ImplementationComponent(
                name=algo.get("name", ""),
                description=algo.get("description", ""),
                requirements={
                    "inputs": algo.get("inputs", []),
                    "outputs": algo.get("outputs", []),
                    "parameters": algo.get("parameters", {})
                }
            )
            plan.components.append(component)
            
        # Add components from architecture
        for component_name, component_details in architecture.items():
            component = ImplementationComponent(
                name=component_name,
                description=component_details.get("description", ""),
                dependencies=component_details.get("dependencies", [])
            )
            plan.components.append(component)
            
        # Add overall requirements
        plan.requirements = {
            "frameworks": implementation_details.get("frameworks", []),
            "libraries": implementation_details.get("libraries", []),
            "compute_requirements": implementation_details.get("compute_requirements", {}),
            "datasets": implementation_details.get("datasets", []),
            "evaluation_metrics": evaluation.get("metrics", [])
        }
        
        # Set timeline based on complexity
        complexity = len(plan.components)
        if complexity <= 3:
            plan.estimated_timeline = "1-2 weeks"
        elif complexity <= 6:
            plan.estimated_timeline = "2-4 weeks"
        else:
            plan.estimated_timeline = "4+ weeks"
            
        return plan
    
    def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> Optional[ImplementationPlan]:
        """
        Update an existing implementation plan.
        
        Args:
            plan_id: ID of plan to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated ImplementationPlan or None if not found
        """
        if not self.current_plan or self.current_plan.id != plan_id:
            logger.warning(f"No plan found with ID {plan_id}")
            return None
            
        # Apply updates
        for key, value in updates.items():
            if hasattr(self.current_plan, key):
                setattr(self.current_plan, key, value)
                
        self.current_plan.updated_at = datetime.now()
        return self.current_plan
    
    def validate_plan(self, plan: ImplementationPlan) -> Dict[str, Any]:
        """
        Validate an implementation plan.
        
        Args:
            plan: ImplementationPlan to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        
        # Check components
        if not plan.components:
            issues.append("Plan has no components defined")
            
        # Check requirements
        if not plan.requirements:
            issues.append("Plan has no requirements defined")
            
        # Check dependencies
        component_names = {c.name for c in plan.components}
        for component in plan.components:
            for dep in component.dependencies:
                if dep not in component_names:
                    issues.append(f"Component {component.name} has unknown dependency {dep}")
                    
        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }