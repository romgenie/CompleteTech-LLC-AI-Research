"""
Tests for the Task Planning functionality.
"""

import unittest
from datetime import datetime

from research_implementation.implementation_planning.planner import (
    ImplementationPlan,
    ImplementationComponent
)
from research_implementation.implementation_planning.task_planner import (
    TaskPlanner,
    Task
)

class TestTaskPlanner(unittest.TestCase):
    """Test cases for the TaskPlanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task_planner = TaskPlanner()
        self.sample_plan = ImplementationPlan(
            id="test_1",
            title="Test Plan",
            description="A test implementation plan",
            components=[
                ImplementationComponent(
                    name="DataProcessor",
                    description="Processes input data",
                    dependencies=[],
                    estimated_effort="medium",
                    priority="high"
                ),
                ImplementationComponent(
                    name="ModelTrainer",
                    description="Trains the model",
                    dependencies=["DataProcessor"],
                    estimated_effort="high",
                    priority="medium"
                )
            ],
            requirements={
                "frameworks": ["pytorch"],
                "libraries": ["numpy", "pandas"]
            }
        )

    def test_task_generation(self):
        """Test basic task generation from a plan."""
        tasks = self.task_planner.generate_tasks(self.sample_plan)
        
        # Should generate:
        # 1 setup task + (3 tasks per component: impl, test, doc) * 2 components
        self.assertEqual(len(tasks), 7)
        
        # Verify setup task
        setup_tasks = [t for t in tasks.values() if t.name == "Setup Development Environment"]
        self.assertEqual(len(setup_tasks), 1)
        setup_task = setup_tasks[0]
        self.assertEqual(setup_task.priority, 5)
        self.assertEqual(setup_task.estimated_hours, 4)
        
        # Verify component tasks
        for component in ["DataProcessor", "ModelTrainer"]:
            impl_tasks = [t for t in tasks.values() if t.name == f"Implement {component}"]
            test_tasks = [t for t in tasks.values() if t.name == f"Test {component}"]
            doc_tasks = [t for t in tasks.values() if t.name == f"Document {component}"]
            
            self.assertEqual(len(impl_tasks), 1)
            self.assertEqual(len(test_tasks), 1)
            self.assertEqual(len(doc_tasks), 1)
            
            impl_task = impl_tasks[0]
            test_task = test_tasks[0]
            doc_task = doc_tasks[0]
            
            # Test tasks should depend on implementation
            self.assertIn(impl_task.id, test_task.dependencies)
            self.assertIn(impl_task.id, doc_task.dependencies)

    def test_task_dependencies(self):
        """Test that task dependencies are set up correctly."""
        tasks = self.task_planner.generate_tasks(self.sample_plan)
        
        # Find the implementation tasks
        data_processor_task = next(
            t for t in tasks.values() 
            if t.name == "Implement DataProcessor"
        )
        model_trainer_task = next(
            t for t in tasks.values()
            if t.name == "Implement ModelTrainer"
        )
        
        # ModelTrainer should depend on DataProcessor
        self.assertIn(data_processor_task.id, model_trainer_task.dependencies)

    def test_critical_path(self):
        """Test critical path calculation."""
        tasks = self.task_planner.generate_tasks(self.sample_plan)
        critical_path = self.task_planner.get_critical_path()
        
        # Convert to task names for easier testing
        path_names = [task.name for task in critical_path]
        
        # Setup should be first
        self.assertEqual(path_names[0], "Setup Development Environment")
        
        # DataProcessor implementation should come before ModelTrainer
        dp_impl_index = path_names.index("Implement DataProcessor")
        mt_impl_index = path_names.index("Implement ModelTrainer")
        self.assertTrue(dp_impl_index < mt_impl_index)

    def test_effort_estimation(self):
        """Test effort estimation for tasks."""
        tasks = self.task_planner.generate_tasks(self.sample_plan)
        
        # Get implementation tasks
        dp_task = next(
            t for t in tasks.values() 
            if t.name == "Implement DataProcessor"
        )
        mt_task = next(
            t for t in tasks.values()
            if t.name == "Implement ModelTrainer"
        )
        
        # High effort should take more hours than medium
        self.assertGreater(mt_task.estimated_hours, dp_task.estimated_hours)
        
        # Test tasks should take about half the implementation time
        dp_test = next(
            t for t in tasks.values()
            if t.name == "Test DataProcessor"
        )
        self.assertAlmostEqual(
            dp_test.estimated_hours,
            max(4, dp_task.estimated_hours * 0.5)
        )

    def test_empty_plan(self):
        """Test handling of empty implementation plan."""
        empty_plan = ImplementationPlan(
            id="empty_1",
            title="Empty Plan",
            description="Plan with no components",
            components=[],
            requirements={}
        )
        tasks = self.task_planner.generate_tasks(empty_plan)
        self.assertEqual(len(tasks), 0)
        
        critical_path = self.task_planner.get_critical_path()
        self.assertEqual(len(critical_path), 0)

    def test_circular_dependencies(self):
        """Test handling of circular dependencies in components."""
        circular_plan = ImplementationPlan(
            id="circular_1",
            title="Circular Dependencies",
            description="Plan with circular component dependencies",
            components=[
                ImplementationComponent(
                    name="ComponentA",
                    description="Component A",
                    dependencies=["ComponentB"],
                    estimated_effort="medium",
                    priority="high"
                ),
                ImplementationComponent(
                    name="ComponentB",
                    description="Component B",
                    dependencies=["ComponentA"],
                    estimated_effort="medium",
                    priority="high"
                )
            ],
            requirements={}
        )
        tasks = self.task_planner.generate_tasks(circular_plan)
        
        # Tasks should still be generated
        self.assertEqual(len(tasks), 6)  # 3 tasks per component
        
        # Critical path should still be calculable
        critical_path = self.task_planner.get_critical_path()
        self.assertGreater(len(critical_path), 0)

    def test_task_priority_inheritance(self):
        """Test that tasks inherit priority from their components."""
        tasks = self.task_planner.generate_tasks(self.sample_plan)
        
        # Find all tasks for DataProcessor (high priority)
        dp_tasks = [t for t in tasks.values() if t.component == "DataProcessor"]
        
        # All tasks should have inherited high priority
        for task in dp_tasks:
            self.assertGreater(task.priority, 3, f"Task {task.name} should have high priority")

if __name__ == '__main__':
    unittest.main()