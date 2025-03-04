"""
Tests for the TDAG adapter in the Research Orchestration Framework.

This module tests the functionality of the TDAGAdapter class, which
integrates with the TDAG framework for task decomposition and planning.
"""

import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from research_orchestrator.adapters.tdag_adapter import TDAGAdapter


class TestTDAGAdapter(unittest.TestCase):
    """Tests for the TDAGAdapter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create configuration for the adapter
        self.config = {
            'model_name': 'gpt-4',
            'proxy': None,
            'record_path': None
        }
        
        # Create patches for the TDAG classes
        self.agent_generator_patcher = patch('research_orchestrator.adapters.tdag_adapter.AgentGenerator')
        self.main_agent_patcher = patch('research_orchestrator.adapters.tdag_adapter.MainAgent')
        
        # Start the patches
        self.mock_agent_generator = self.agent_generator_patcher.start()
        self.mock_main_agent = self.main_agent_patcher.start()
        
        # Set up mock instances
        self.mock_agent_generator_instance = MagicMock()
        self.mock_main_agent_instance = MagicMock()
        
        # Configure the mock AgentGenerator class to return our mock instance
        self.mock_agent_generator.return_value = self.mock_agent_generator_instance
        self.mock_agent_generator_instance.subtasks = [
            {'subtask_name': 'Subtask 1', 'goal': 'Accomplish goal 1'},
            {'subtask_name': 'Subtask 2', 'goal': 'Accomplish goal 2'}
        ]
        
        # Configure the mock MainAgent class to return our mock instance
        self.mock_main_agent.return_value = self.mock_main_agent_instance
        self.mock_main_agent_instance.messages = [
            {'role': 'system', 'content': 'System prompt'},
            {'role': 'user', 'content': 'User query'},
            {'role': 'assistant', 'content': '''Here's the plan:
            ```json
            {
                "title": "Research Plan",
                "steps": [
                    {
                        "name": "Step 1",
                        "description": "Do step 1"
                    },
                    {
                        "name": "Step 2",
                        "description": "Do step 2"
                    }
                ]
            }
            ```
            '''}
        ]
        
        # Create the adapter
        self.adapter = TDAGAdapter(self.config)
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop the patches
        self.agent_generator_patcher.stop()
        self.main_agent_patcher.stop()
    
    def test_init(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.model_name, 'gpt-4')
        self.assertIsNone(self.adapter.proxy)
        self.assertIsNone(self.adapter.record_path)
    
    def test_validate_config(self):
        """Test configuration validation."""
        # Valid config
        self.assertTrue(self.adapter.validate_config({'model_name': 'gpt-4'}))
        
        # Invalid config (missing required key)
        self.assertFalse(self.adapter.validate_config({'proxy': None}))
    
    def test_decompose_task(self):
        """Test task decomposition functionality."""
        task = "Research the latest advancements in AI"
        subtasks = self.adapter.decompose_task(task)
        
        # Check that AgentGenerator was called with correct arguments
        self.mock_agent_generator.assert_called_once_with(
            total_task=task,
            current_task=task,
            completed_task=[],
            record_path=None,
            model_name='gpt-4',
            proxy=None
        )
        
        # Check that get_response was called on the agent
        self.mock_agent_generator_instance.get_response.assert_called_once()
        
        # Check that we get the expected subtasks
        self.assertEqual(len(subtasks), 2)
        self.assertEqual(subtasks[0]['subtask_name'], 'Subtask 1')
        self.assertEqual(subtasks[1]['subtask_name'], 'Subtask 2')
    
    def test_create_research_plan(self):
        """Test research plan creation functionality."""
        task = "Create a research plan on quantum computing"
        plan = self.adapter.create_research_plan(task)
        
        # Check that MainAgent was called with correct arguments
        self.mock_main_agent.assert_called_once()
        
        # Check that get_response was called on the agent
        self.mock_main_agent_instance.get_response.assert_called_once()
        
        # Check that we get a properly structured plan
        self.assertIn('title', plan)
        self.assertIn('steps', plan)
        self.assertEqual(len(plan['steps']), 2)
        self.assertEqual(plan['title'], 'Research Plan')
    
    def test_create_research_plan_with_context(self):
        """Test research plan creation with context."""
        task = "Create a research plan on quantum computing"
        context = {'focus_area': 'quantum algorithms', 'timeframe': '2 weeks'}
        
        # Call the method with context
        self.adapter.create_research_plan(task, context)
        
        # Check that the context was included in the system prompt
        system_prompt = self.mock_main_agent.call_args[1]['system_prompt']
        
        self.assertIn('Additional context', system_prompt)
        self.assertIn('focus_area', system_prompt)
        self.assertIn('quantum algorithms', system_prompt)
        self.assertIn('timeframe', system_prompt)
        self.assertIn('2 weeks', system_prompt)


if __name__ == '__main__':
    unittest.main()