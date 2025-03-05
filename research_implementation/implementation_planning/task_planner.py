"""
Task planning and organization for implementation plans.

This module handles breaking down implementation plans into concrete tasks,
organizing them into a dependency graph, and generating execution schedules.
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from .planner import ImplementationPlan, ImplementationComponent

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """An implementation task derived from a component."""
    id: str
    name: str
    description: str
    component: str  # Name of parent component
    dependencies: List[str] = field(default_factory=list)
    estimated_hours: float = 0
    priority: int = 1  # 1-5, higher is more important
    status: str = "todo"
    assignee: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __hash__(self):
        """Make Task hashable by using the id as the hash."""
        return hash(self.id)
    
    def __eq__(self, other):
        """Compare Tasks by id."""
        if not isinstance(other, Task):
            return False
        return self.id == other.id

class TaskPlanner:
    """
    Plans and organizes implementation tasks based on component requirements.
    """
    
    def __init__(self):
        """Initialize the task planner."""
        self.tasks: Dict[str, Task] = {}
        self.task_counter = 0
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        self.task_counter += 1
        return f"task_{self.task_counter}"
    
    def generate_tasks(self, plan: ImplementationPlan) -> Dict[str, Task]:
        """
        Generate implementation tasks from a plan.
        
        Args:
            plan: The implementation plan to generate tasks for
            
        Returns:
            Dictionary mapping task IDs to Task objects
        """
        tasks = {}
        
        # Create setup tasks for requirements
        setup_task_id = None
        if plan.requirements.get("frameworks") or plan.requirements.get("libraries"):
            setup_task_id = self._generate_task_id()
            tasks[setup_task_id] = Task(
                id=setup_task_id,
                name="Setup Development Environment",
                description="Install required frameworks and libraries",
                component="setup",
                estimated_hours=4,
                priority=5  # Highest priority since other tasks depend on this
            )
            
        # Create tasks for each component
        for component in plan.components:
            # Core implementation task
            impl_task_id = self._generate_task_id()
            impl_deps = []
            # Add dependency on setup task if it exists
            if setup_task_id:
                impl_deps.append(setup_task_id)
                
            tasks[impl_task_id] = Task(
                id=impl_task_id,
                name=f"Implement {component.name}",
                description=f"Implement core functionality for {component.name}",
                component=component.name,
                estimated_hours=self._estimate_component_effort(component),
                priority=self._calculate_priority(component),
                dependencies=impl_deps  # Will be updated further after all tasks are created
            )
            
            # Testing task
            test_task_id = self._generate_task_id()
            tasks[test_task_id] = Task(
                id=test_task_id,
                name=f"Test {component.name}",
                description=f"Implement and run tests for {component.name}",
                component=component.name,
                estimated_hours=max(4, self._estimate_component_effort(component) * 0.5),
                priority=self._calculate_priority(component),
                dependencies=[impl_task_id]
            )
            
            # Documentation task
            doc_task_id = self._generate_task_id()
            tasks[doc_task_id] = Task(
                id=doc_task_id,
                name=f"Document {component.name}",
                description=f"Create documentation for {component.name}",
                component=component.name,
                estimated_hours=4,
                priority=self._calculate_priority(component),
                dependencies=[impl_task_id]
            )
            
        # Update dependencies based on component dependencies
        component_to_impl_task = {
            task.component: task.id 
            for task in tasks.values() 
            if task.name.startswith("Implement")
        }
        
        for component in plan.components:
            if component.dependencies:
                impl_task = next(
                    task for task in tasks.values() 
                    if task.component == component.name and task.name.startswith("Implement")
                )
                for dep in component.dependencies:
                    if dep in component_to_impl_task:
                        impl_task.dependencies.append(component_to_impl_task[dep])
                        
        self.tasks = tasks
        return tasks
    
    def _estimate_component_effort(self, component: ImplementationComponent) -> float:
        """Estimate hours needed for a component based on its properties."""
        base_hours = {
            "low": 8,
            "medium": 16,
            "high": 32
        }.get(component.estimated_effort, 16)
        
        # Adjust for dependencies
        dep_factor = 1 + (len(component.dependencies) * 0.2)
        
        # Adjust for requirements complexity
        req_factor = 1 + (len(component.requirements) * 0.1)
        
        return base_hours * dep_factor * req_factor
    
    def _calculate_priority(self, component: ImplementationComponent) -> int:
        """Calculate priority score (1-5) for a component."""
        base_priority = {
            "low": 1,
            "medium": 3,
            "high": 4
        }.get(component.priority, 2)
        
        # Increase priority if other components depend on this
        if len(component.dependencies) > 2:
            base_priority = min(5, base_priority + 1)
            
        return base_priority
    
    def get_critical_path(self) -> List[Task]:
        """
        Calculate the critical path of tasks that determine the minimum timeline.
        
        Returns:
            List of tasks on the critical path
        """
        if not self.tasks:
            return []
            
        # Calculate earliest completion times
        earliest_completion: Dict[str, float] = {}
        for task in self._topological_sort():
            earliest = 0
            for dep_id in task.dependencies:
                if dep_id in earliest_completion:
                    earliest = max(earliest, earliest_completion[dep_id])
            earliest_completion[task.id] = earliest + task.estimated_hours
            
        # Find critical path by backtracking from end
        critical_path = []
        current_time = max(earliest_completion.values())
        remaining_tasks = set(self.tasks.values())
        
        while remaining_tasks:
            # Find task that completes at current_time
            current_task = None
            for task in remaining_tasks:
                if abs(earliest_completion[task.id] - current_time) < 0.001:
                    current_task = task
                    break
                    
            if not current_task:
                break
                
            critical_path.append(current_task)
            remaining_tasks.remove(current_task)
            
            # Move to the latest dependency
            if current_task.dependencies:
                current_time = max(
                    earliest_completion[dep_id] 
                    for dep_id in current_task.dependencies
                )
            else:
                break
                
        return list(reversed(critical_path))
    
    def _topological_sort(self) -> List[Task]:
        """Return tasks in topologically sorted order."""
        # Track visited nodes and sort order
        visited: Set[str] = set()
        sort_order: List[Task] = []
        
        def visit(task_id: str):
            if task_id in visited:
                return
            visited.add(task_id)
            task = self.tasks[task_id]
            for dep in task.dependencies:
                visit(dep)
            sort_order.append(task)
            
        # Visit all tasks
        for task_id in self.tasks:
            visit(task_id)
            
        return sort_order