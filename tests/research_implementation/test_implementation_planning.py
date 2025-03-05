"""
Tests for the Implementation Planning System.
"""

import unittest
from datetime import datetime
import tempfile
from pathlib import Path

from research_implementation.implementation_planning.planner import (
    ImplementationPlanner, 
    ImplementationPlan,
    ImplementationComponent
)
from research_implementation.implementation_planning.task_planner import (
    TaskPlanner,
    Task
)
from research_implementation.implementation_planning.service import PlanningService

class TestImplementationPlanner(unittest.TestCase):
    """Test cases for the ImplementationPlanner class."""
    
    def setUp(self):
        self.planner = ImplementationPlanner()
        self.sample_understanding = {
            "id": "test_1",
            "title": "Test Paper",
            "description": "A test paper implementation",
            "algorithms": [
                {
                    "name": "TestAlgorithm",
                    "description": "A test algorithm",
                    "inputs": ["input_data"],
                    "outputs": ["output_data"],
                    "parameters": {"param1": "value1"}
                }
            ],
            "architecture": {
                "DataProcessor": {
                    "description": "Processes input data",
                    "dependencies": []
                },
                "ModelTrainer": {
                    "description": "Trains the model",
                    "dependencies": ["DataProcessor"]
                }
            },
            "implementation_details": {
                "frameworks": ["pytorch"],
                "libraries": ["numpy", "pandas"],
                "compute_requirements": {"gpu": True},
                "datasets": ["test_dataset"]
            },
            "evaluation_methodology": {
                "metrics": ["accuracy", "f1_score"]
            }
        }
        
    def test_create_plan(self):
        """Test creating an implementation plan."""
        plan = self.planner.create_plan(self.sample_understanding)
        
        # Check basic plan properties
        self.assertEqual(plan.id, "test_1")
        self.assertTrue(plan.title.startswith("Implementation Plan:"))
        self.assertEqual(plan.description, "A test paper implementation")
        
        # Check components
        self.assertEqual(len(plan.components), 3)  # Algorithm + 2 architecture components
        component_names = {c.name for c in plan.components}
        self.assertIn("TestAlgorithm", component_names)
        self.assertIn("DataProcessor", component_names)
        self.assertIn("ModelTrainer", component_names)
        
        # Check requirements
        self.assertEqual(plan.requirements["frameworks"], ["pytorch"])
        self.assertEqual(plan.requirements["libraries"], ["numpy", "pandas"])
        self.assertTrue(plan.requirements["compute_requirements"]["gpu"])
        self.assertEqual(plan.requirements["datasets"], ["test_dataset"])
        self.assertEqual(plan.requirements["evaluation_metrics"], ["accuracy", "f1_score"])
        
    def test_validate_plan(self):
        """Test plan validation."""
        # Create a valid plan
        plan = self.planner.create_plan(self.sample_understanding)
        validation = self.planner.validate_plan(plan)
        self.assertTrue(validation["is_valid"])
        self.assertEqual(len(validation["issues"]), 0)
        
        # Create an invalid plan (no components)
        invalid_plan = ImplementationPlan(
            id="invalid_1",
            title="Invalid Plan",
            description="Invalid plan with no components"
        )
        validation = self.planner.validate_plan(invalid_plan)
        self.assertFalse(validation["is_valid"])
        self.assertTrue(any("no components" in issue for issue in validation["issues"]))

class TestTaskPlanner(unittest.TestCase):
    """Test cases for the TaskPlanner class."""
    
    def setUp(self):
        self.task_planner = TaskPlanner()
        self.sample_plan = ImplementationPlan(
            id="test_1",
            title="Test Plan",
            description="A test plan",
            components=[
                ImplementationComponent(
                    name="ComponentA",
                    description="Component A",
                    dependencies=[]
                ),
                ImplementationComponent(
                    name="ComponentB",
                    description="Component B",
                    dependencies=["ComponentA"]
                )
            ],
            requirements={
                "frameworks": ["pytorch"],
                "libraries": ["numpy"]
            }
        )
        
    def test_generate_tasks(self):
        """Test generating tasks from a plan."""
        tasks = self.task_planner.generate_tasks(self.sample_plan)
        
        # Should create setup task + 3 tasks per component (impl, test, doc)
        self.assertEqual(len(tasks), 7)
        
        # Check task types
        task_names = [t.name for t in tasks.values()]
        self.assertIn("Setup Development Environment", task_names)
        self.assertIn("Implement ComponentA", task_names)
        self.assertIn("Test ComponentA", task_names)
        self.assertIn("Document ComponentA", task_names)
        self.assertIn("Implement ComponentB", task_names)
        self.assertIn("Test ComponentB", task_names)
        self.assertIn("Document ComponentB", task_names)
        
        # Check dependencies
        for task in tasks.values():
            if task.name == "Implement ComponentB":
                impl_a = next(
                    t.id for t in tasks.values() 
                    if t.name == "Implement ComponentA"
                )
                self.assertIn(impl_a, task.dependencies)
            elif task.name.startswith("Test "):
                impl_task = next(
                    t.id for t in tasks.values()
                    if t.name == f"Implement {task.component}"
                )
                self.assertIn(impl_task, task.dependencies)
                
    def test_critical_path(self):
        """Test calculating the critical path."""
        tasks = self.task_planner.generate_tasks(self.sample_plan)
        critical_path = self.task_planner.get_critical_path()
        
        # Critical path should start with setup and include ComponentA before ComponentB
        task_names = [t.name for t in critical_path]
        setup_index = task_names.index("Setup Development Environment")
        comp_a_index = next(
            i for i, name in enumerate(task_names)
            if "ComponentA" in name
        )
        comp_b_index = next(
            i for i, name in enumerate(task_names)
            if "ComponentB" in name
        )
        
        self.assertEqual(setup_index, 0)  # Setup should be first
        self.assertTrue(comp_a_index < comp_b_index)  # A should come before B

class TestPlanningService(unittest.TestCase):
    """Test cases for the PlanningService class."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = PlanningService(storage_dir=self.temp_dir)
        self.sample_understanding = {
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
        
    def tearDown(self):
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_create_implementation_plan(self):
        """Test creating and storing an implementation plan."""
        result = self.service.create_implementation_plan(self.sample_understanding)
        
        # Check result structure
        self.assertIn("plan", result)
        self.assertIn("tasks", result)
        self.assertIn("critical_path", result)
        self.assertIn("validation", result)
        self.assertIn("metadata", result)
        
        # Check plan was stored
        plan_file = Path(self.temp_dir) / f"{result['plan']['id']}.json"
        self.assertTrue(plan_file.exists())
        
    def test_get_plan(self):
        """Test retrieving a stored plan."""
        # Create a plan first
        result = self.service.create_implementation_plan(self.sample_understanding)
        plan_id = result["plan"]["id"]
        
        # Retrieve the plan
        loaded_plan = self.service.get_plan(plan_id)
        self.assertIsNotNone(loaded_plan)
        self.assertEqual(loaded_plan["plan"]["id"], plan_id)
        
    def test_update_plan(self):
        """Test updating a plan."""
        # Create a plan first
        result = self.service.create_implementation_plan(self.sample_understanding)
        plan_id = result["plan"]["id"]
        
        # Update the plan
        updates = {"status": "in_progress"}
        updated_plan = self.service.update_plan(plan_id, updates)
        
        self.assertIsNotNone(updated_plan)
        self.assertEqual(updated_plan["plan"]["status"], "in_progress")
        
    def test_update_task(self):
        """Test updating a task in a plan."""
        # Create a plan first
        result = self.service.create_implementation_plan(self.sample_understanding)
        plan_id = result["plan"]["id"]
        task_id = result["tasks"][0]["id"]
        
        # Update the task
        updates = {"status": "in_progress", "assignee": "test_user"}
        updated_plan = self.service.update_task(plan_id, task_id, updates)
        
        self.assertIsNotNone(updated_plan)
        updated_task = next(
            task for task in updated_plan["tasks"] 
            if task["id"] == task_id
        )
        self.assertEqual(updated_task["status"], "in_progress")
        self.assertEqual(updated_task["assignee"], "test_user")

if __name__ == '__main__':
    unittest.main()