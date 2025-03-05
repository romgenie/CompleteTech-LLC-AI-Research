"""
Tests for the implementation planning validation system.
"""

import unittest
from datetime import datetime

from research_implementation.implementation_planning.planner import (
    ImplementationPlan,
    ImplementationComponent
)
from research_implementation.implementation_planning.task_planner import Task
from research_implementation.implementation_planning.validation import (
    PlanningValidator,
    ValidationError
)

class TestPlanningValidator(unittest.TestCase):
    """Test cases for the PlanningValidator class."""
    
    def setUp(self):
        self.validator = PlanningValidator()
        self.valid_understanding = {
            "id": "test_1",
            "title": "Test Paper",
            "description": "A test paper",
            "algorithms": [
                {
                    "name": "TestAlgorithm",
                    "description": "A test algorithm"
                }
            ],
            "architecture": {
                "TestComponent": {
                    "description": "A test component",
                    "dependencies": []
                }
            }
        }
        
    def test_validate_understanding(self):
        """Test validation of paper understanding input."""
        # Test valid understanding
        errors = self.validator.validate_understanding(self.valid_understanding)
        self.assertEqual(len(errors), 0)
        
        # Test missing required fields
        invalid_understanding = {
            "algorithms": [{"name": "Test"}]
        }
        errors = self.validator.validate_understanding(invalid_understanding)
        self.assertTrue(any(e.code == "MISSING_FIELD" for e in errors))
        self.assertTrue(any(e.field == "id" for e in errors))
        self.assertTrue(any(e.field == "title" for e in errors))
        self.assertTrue(any(e.field == "description" for e in errors))
        
        # Test missing components
        invalid_understanding = {
            "id": "test_1",
            "title": "Test",
            "description": "Test"
        }
        errors = self.validator.validate_understanding(invalid_understanding)
        self.assertTrue(any(e.code == "NO_COMPONENTS" for e in errors))
        
        # Test invalid algorithm
        invalid_understanding = {
            "id": "test_1",
            "title": "Test",
            "description": "Test",
            "algorithms": [{"description": "Missing name"}]
        }
        errors = self.validator.validate_understanding(invalid_understanding)
        self.assertTrue(any(e.code == "INVALID_ALGORITHM" for e in errors))
        
        # Test invalid component
        invalid_understanding = {
            "id": "test_1",
            "title": "Test",
            "description": "Test",
            "architecture": {
                "TestComponent": {}  # Missing description
            }
        }
        errors = self.validator.validate_understanding(invalid_understanding)
        self.assertTrue(any(e.code == "INVALID_COMPONENT" for e in errors))
        
    def test_validate_plan(self):
        """Test validation of implementation plans."""
        # Test valid plan
        valid_plan = ImplementationPlan(
            id="test_1",
            title="Test Plan",
            description="A test plan",
            components=[
                ImplementationComponent(
                    name="ComponentA",
                    description="Component A",
                    dependencies=[],
                    estimated_effort="medium"
                ),
                ImplementationComponent(
                    name="ComponentB",
                    description="Component B",
                    dependencies=["ComponentA"],
                    estimated_effort="high"
                )
            ],
            requirements={
                "frameworks": ["pytorch"],
                "libraries": ["numpy"]
            }
        )
        errors = self.validator.validate_plan(valid_plan)
        self.assertEqual(len(errors), 0)
        
        # Test missing ID
        invalid_plan = ImplementationPlan(
            id="",
            title="Test Plan",
            description="Test plan",
            components=[],
            requirements={}
        )
        errors = self.validator.validate_plan(invalid_plan)
        self.assertTrue(any(e.code == "MISSING_ID" for e in errors))
        
        # Test missing title
        invalid_plan = ImplementationPlan(
            id="test_1",
            title="",
            description="Test plan",
            components=[],
            requirements={}
        )
        errors = self.validator.validate_plan(invalid_plan)
        self.assertTrue(any(e.code == "MISSING_TITLE" for e in errors))
        
        # Test no components
        invalid_plan = ImplementationPlan(
            id="test_1",
            title="Test Plan",
            description="Test plan",
            components=[],
            requirements={}
        )
        errors = self.validator.validate_plan(invalid_plan)
        self.assertTrue(any(e.code == "NO_COMPONENTS" for e in errors))
        
        # Test invalid dependency
        invalid_plan = ImplementationPlan(
            id="test_1",
            title="Test Plan",
            description="Test plan",
            components=[
                ImplementationComponent(
                    name="ComponentA",
                    description="Component A",
                    dependencies=["NonexistentComponent"],
                    estimated_effort="medium"
                )
            ],
            requirements={}
        )
        errors = self.validator.validate_plan(invalid_plan)
        self.assertTrue(any(e.code == "INVALID_DEPENDENCY" for e in errors))
        
        # Test invalid effort level
        invalid_plan = ImplementationPlan(
            id="test_1",
            title="Test Plan",
            description="Test plan",
            components=[
                ImplementationComponent(
                    name="ComponentA",
                    description="Component A",
                    dependencies=[],
                    estimated_effort="invalid"
                )
            ],
            requirements={}
        )
        errors = self.validator.validate_plan(invalid_plan)
        self.assertTrue(any(e.code == "INVALID_EFFORT" for e in errors))
        
    def test_validate_tasks(self):
        """Test validation of implementation tasks."""
        plan = ImplementationPlan(
            id="test_1",
            title="Test Plan",
            description="Test plan",
            components=[
                ImplementationComponent(
                    name="ComponentA",
                    description="Component A",
                    dependencies=[]
                )
            ],
            requirements={}
        )
        
        # Test valid tasks
        valid_tasks = {
            "task_1": Task(
                id="task_1",
                name="Task 1",
                description="Test task",
                component="ComponentA",
                dependencies=[],
                estimated_hours=8,
                priority=3,
                status="todo"
            )
        }
        errors = self.validator.validate_tasks(valid_tasks, plan)
        self.assertEqual(len(errors), 0)
        
        # Test no tasks
        errors = self.validator.validate_tasks({}, plan)
        self.assertTrue(any(e.code == "NO_TASKS" for e in errors))
        
        # Test invalid task dependency
        invalid_tasks = {
            "task_1": Task(
                id="task_1",
                name="Task 1",
                description="Test task",
                component="ComponentA",
                dependencies=["nonexistent_task"],
                estimated_hours=8,
                priority=3,
                status="todo"
            )
        }
        errors = self.validator.validate_tasks(invalid_tasks, plan)
        self.assertTrue(any(e.code == "INVALID_TASK_DEPENDENCY" for e in errors))
        
        # Test invalid hours
        invalid_tasks = {
            "task_1": Task(
                id="task_1",
                name="Task 1",
                description="Test task",
                component="ComponentA",
                dependencies=[],
                estimated_hours=0,
                priority=3,
                status="todo"
            )
        }
        errors = self.validator.validate_tasks(invalid_tasks, plan)
        self.assertTrue(any(e.code == "INVALID_HOURS" for e in errors))
        
        # Test invalid priority
        invalid_tasks = {
            "task_1": Task(
                id="task_1",
                name="Task 1",
                description="Test task",
                component="ComponentA",
                dependencies=[],
                estimated_hours=8,
                priority=6,  # Should be 1-5
                status="todo"
            )
        }
        errors = self.validator.validate_tasks(invalid_tasks, plan)
        self.assertTrue(any(e.code == "INVALID_PRIORITY" for e in errors))
        
        # Test invalid status
        invalid_tasks = {
            "task_1": Task(
                id="task_1",
                name="Task 1",
                description="Test task",
                component="ComponentA",
                dependencies=[],
                estimated_hours=8,
                priority=3,
                status="invalid"
            )
        }
        errors = self.validator.validate_tasks(invalid_tasks, plan)
        self.assertTrue(any(e.code == "INVALID_STATUS" for e in errors))
        
    def test_validate_critical_path(self):
        """Test validation of critical path."""
        tasks = {
            "task_1": Task(
                id="task_1",
                name="Task 1",
                description="Task 1",
                component="ComponentA",
                dependencies=[],
                estimated_hours=8
            ),
            "task_2": Task(
                id="task_2",
                name="Task 2", 
                description="Task 2",
                component="ComponentB",
                dependencies=["task_1"],
                estimated_hours=8
            ),
            "task_3": Task(
                id="task_3",
                name="Task 3",
                description="Task 3",
                component="ComponentC",
                dependencies=["task_2"],
                estimated_hours=8
            )
        }
        
        # Test valid critical path
        valid_path = [
            tasks["task_1"],
            tasks["task_2"],
            tasks["task_3"]
        ]
        errors = self.validator.validate_critical_path(valid_path, tasks)
        self.assertEqual(len(errors), 0)
        
        # Test empty path
        errors = self.validator.validate_critical_path([], tasks)
        self.assertTrue(any(e.code == "EMPTY_CRITICAL_PATH" for e in errors))
        
        # Test invalid path (break in dependencies)
        invalid_path = [
            tasks["task_1"],
            tasks["task_3"],  # Missing task_2 which task_3 depends on
            tasks["task_2"]
        ]
        errors = self.validator.validate_critical_path(invalid_path, tasks)
        self.assertTrue(any(e.code == "INVALID_PATH" for e in errors))

if __name__ == '__main__':
    unittest.main()