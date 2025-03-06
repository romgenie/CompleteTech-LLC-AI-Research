"""
Implementation Planning System for converting research papers to implementation plans.

This package provides functionality for:
- Converting research paper understanding into structured implementation plans
- Breaking down implementation into concrete tasks and dependencies
- Estimating effort and timeline for implementation components
- Managing and tracking implementation plans
"""

from .planner import ImplementationPlanner, ImplementationPlan, ImplementationComponent
from .task_planner import TaskPlanner, Task
from .service import PlanningService

__version__ = "0.1.0"

__all__ = [
    'ImplementationPlanner',
    'ImplementationPlan',
    'ImplementationComponent',
    'TaskPlanner',
    'Task',
    'PlanningService'
]