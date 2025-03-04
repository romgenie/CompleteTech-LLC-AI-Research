"""
Tests for the AutoCodeAgent adapter.

This module contains tests for the AutoCodeAgent adapter, which provides integration
with the AutoCodeAgent2.0 repository for code generation and implementation.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json

# Add the src directory to the path so we can import the adapter
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../src'))

from research_orchestrator.external_adapters.autocode_agent.autocode_agent_adapter import AutoCodeAgentAdapter


class TestAutoCodeAgentAdapter(unittest.TestCase):
    """Tests for the AutoCodeAgentAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_repository_path = self.temp_dir.name
        
        # Create a mock repository structure
        os.makedirs(os.path.join(self.test_repository_path, "code_agent"))
        os.makedirs(os.path.join(self.test_repository_path, "deep_search"))
        
        # Create mock files
        with open(os.path.join(self.test_repository_path, "app.py"), "w") as f:
            f.write("# Mock app.py")
        
        with open(os.path.join(self.test_repository_path, "code_agent", "code_agent.py"), "w") as f:
            f.write("# Mock code_agent.py")
        
        with open(os.path.join(self.test_repository_path, "deep_search", "planner.py"), "w") as f:
            f.write("# Mock planner.py")
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test adapter initialization without repository."""
        with patch('os.path.exists', return_value=False):
            adapter = AutoCodeAgentAdapter(repository_path=None)
            self.assertFalse(adapter.available)
            self.assertFalse(adapter.initialized)
            
            # Try initializing with config
            config = {"mode": "intellichain", "model": "gpt-4"}
            self.assertTrue(adapter.initialize(config))
            self.assertTrue(adapter.initialized)
            self.assertFalse(adapter.available)
    
    def test_initialization_with_repository(self):
        """Test adapter initialization with repository."""
        adapter = AutoCodeAgentAdapter(repository_path=self.test_repository_path)
        
        # Test availability
        self.assertTrue(adapter.available)
        self.assertFalse(adapter.initialized)
        
        # Initialize adapter
        config = {"mode": "intellichain", "model": "gpt-4"}
        self.assertTrue(adapter.initialize(config))
        self.assertTrue(adapter.initialized)
    
    def test_capabilities(self):
        """Test capabilities reporting."""
        adapter = AutoCodeAgentAdapter()
        capabilities = adapter.get_capabilities()
        
        # Test that capabilities contains expected values
        expected_capabilities = [
            "code_generation",
            "algorithm_implementation",
            "code_execution",
            "task_decomposition"
        ]
        
        for capability in expected_capabilities:
            self.assertIn(capability, capabilities)
    
    def test_execute_code_generation(self):
        """Test code generation execution."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "intellichain"})
        
        params = {
            "specification": "Create a function to calculate the Fibonacci sequence",
            "language": "python",
            "include_tests": True
        }
        
        result = adapter.execute("generate_code", params)
        
        # Check that result contains expected fields
        self.assertTrue(result["success"])
        self.assertIn("task_id", result)
        self.assertIn("code", result)
        self.assertEqual(result["language"], "python")
        self.assertIn("execution_status", result)
    
    def test_execute_algorithm_implementation(self):
        """Test algorithm implementation execution."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "intellichain"})
        
        params = {
            "algorithm_name": "Quick Sort",
            "algorithm_description": "A divide-and-conquer sorting algorithm",
            "language": "python",
            "include_tests": True
        }
        
        result = adapter.execute("implement_algorithm", params)
        
        # Check that result contains expected fields
        self.assertTrue(result["success"])
        self.assertIn("algorithm_name", result)
        self.assertEqual(result["algorithm_name"], "Quick Sort")
        self.assertIn("code", result)
        self.assertEqual(result["language"], "python")
    
    def test_execute_task_decomposition(self):
        """Test task decomposition execution."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "intellichain"})
        
        params = {
            "task": "Build a web scraper for scientific articles",
            "max_subtasks": 5
        }
        
        result = adapter.execute("decompose_task", params)
        
        # Check that result contains expected fields
        self.assertTrue(result["success"])
        self.assertIn("plan", result)
        self.assertIn("subtasks", result["plan"])
        self.assertLessEqual(len(result["plan"]["subtasks"]), 5)
    
    def test_execute_web_search(self):
        """Test web search execution."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "deep_search"})
        
        params = {
            "query": "Transformer architecture in NLP",
            "search_type": "research",
            "max_results": 3
        }
        
        result = adapter.execute("web_search", params)
        
        # Check that result contains expected fields
        self.assertTrue(result["success"])
        self.assertIn("results", result)
        self.assertLessEqual(len(result["results"]), 3)
        self.assertIn("summary", result)
    
    def test_invalid_action(self):
        """Test that invalid actions raise a ValueError."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "intellichain"})
        
        with self.assertRaises(ValueError):
            adapter.execute("invalid_action", {})
    
    def test_shutdown(self):
        """Test adapter shutdown."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "intellichain"})
        
        self.assertTrue(adapter.shutdown())
        self.assertFalse(adapter.initialized)
    
    def test_code_execution(self):
        """Test code execution."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "intellichain"})
        
        # First generate some code
        params = {
            "specification": "Create a function to calculate the sum of a list",
            "language": "python"
        }
        
        gen_result = adapter.execute("generate_code", params)
        task_id = gen_result["task_id"]
        
        # Now execute the code
        exec_params = {
            "task_id": task_id,
            "timeout": 5
        }
        
        result = adapter.execute("execute_code", exec_params)
        
        # Check that result contains expected fields
        self.assertIn("execution_status", result)
        self.assertIn("execution_time", result)
        
        # Check that the task was updated
        task_status = adapter.execute("get_task_status", {"task_id": task_id})
        self.assertEqual(task_status["execution_status"], result["execution_status"])
    
    def test_code_validation(self):
        """Test code validation."""
        adapter = AutoCodeAgentAdapter()
        adapter.initialize({"mode": "intellichain"})
        
        # Create some code with a potential issue
        code = """
def potentially_unsafe_function():
    # This has a potential security issue
    eval("print('Hello')")
    
    return "Result"
"""
        
        params = {
            "code": code,
            "language": "python",
            "validation_type": "all"
        }
        
        result = adapter.execute("validate_code", params)
        
        # Check that result contains expected fields
        self.assertIn("validation_passed", result)
        self.assertIn("issues", result)
        self.assertIn("security_issues", result)
        self.assertIn("functionality_issues", result)
        
        # Should detect the eval as a security issue
        self.assertGreaterEqual(result["security_issues"], 1)


if __name__ == '__main__':
    unittest.main()