"""
TDAG (Task Decomposition Agent Generation) Adapter.

This module provides an adapter for integrating with the TDAG framework,
focusing on task decomposition and planning capabilities.
"""

import os
import sys
from typing import Dict, List, Any, Optional

# Add TDAG path to system path for importing
TDAG_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../external_repo/TDAG'))
if TDAG_PATH not in sys.path:
    sys.path.append(TDAG_PATH)

# Import TDAG components
from agents.agent_generator.agent import AgentGenerator
from agents.main_agent.agent import MainAgent

# Import adapter interfaces
from research_orchestrator.adapters.base_adapter import TaskDecompositionAdapter, PlanningAdapter

class TDAGAdapter(TaskDecompositionAdapter, PlanningAdapter):
    """
    Adapter for the TDAG framework to enable task decomposition and planning
    within the Research Orchestration Framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the TDAG adapter.
        
        Args:
            config: Configuration dictionary containing TDAG settings.
        """
        self.config = config
        self.model_name = config.get('model_name', 'gpt-3.5-turbo-0613')
        self.proxy = config.get('proxy', None)
        self.record_path = config.get('record_path', None)
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate the provided configuration.
        
        Args:
            config: Configuration dictionary to validate.
            
        Returns:
            True if configuration is valid, False otherwise.
        """
        required_keys = ['model_name']
        return all(key in config for key in required_keys)
    
    def decompose_task(self, task: str) -> List[Dict[str, str]]:
        """
        Decompose a complex research task into subtasks.
        
        Args:
            task: The research task to decompose.
            
        Returns:
            A list of subtask dictionaries with name and goal fields.
        """
        # Create an agent generator to decompose the task
        agent_generator = AgentGenerator(
            total_task=task,
            current_task=task,
            completed_task=[],
            record_path=self.record_path,
            model_name=self.model_name,
            proxy=self.proxy
        )
        
        # Generate response
        agent_generator.get_response()
        
        # Return the generated subtasks
        return agent_generator.subtasks
    
    def create_research_plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a research plan for a given task.
        
        Args:
            task: The research task to plan for.
            context: Optional context information to guide planning.
            
        Returns:
            A dictionary containing the research plan.
        """
        # Initialize a main agent for planning
        main_agent = MainAgent(
            task=task,
            system_prompt=self._generate_planning_prompt(context),
            record_path=self.record_path,
            model_name=self.model_name,
            proxy=self.proxy
        )
        
        # Generate the plan
        main_agent.get_response()
        
        # Extract the plan from the agent's response
        plan = self._extract_plan_from_agent(main_agent)
        
        return plan
    
    def _generate_planning_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a system prompt for research planning.
        
        Args:
            context: Optional context information to guide planning.
            
        Returns:
            A string containing the system prompt.
        """
        base_prompt = """
        You are a Research Planning Agent that creates detailed plans for conducting research on AI topics.
        Your task is to generate a comprehensive research plan that covers all aspects of the given topic.
        
        The plan should include:
        1. Key research questions to be answered
        2. Information sources to be consulted
        3. Specific methodologies to be applied
        4. Expected knowledge outcomes
        5. Timeline and dependencies between tasks
        
        For each step in the plan, specify:
        - Goal of the step
        - Resources needed
        - Expected output
        - Evaluation criteria for success
        
        Format your plan as JSON with clear structure.
        """
        
        # Add context if provided
        if context:
            context_str = "\nAdditional context:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            base_prompt += context_str
            
        return base_prompt
    
    def _extract_plan_from_agent(self, agent: MainAgent) -> Dict[str, Any]:
        """
        Extract the research plan from the agent's messages.
        
        Args:
            agent: The MainAgent containing the plan in its messages.
            
        Returns:
            A dictionary containing the structured research plan.
        """
        # Get the latest assistant message
        for message in reversed(agent.messages):
            if message.get('role') == 'assistant':
                content = message.get('content', '')
                
                # Try to extract JSON from the content
                import re
                import json
                
                # Look for JSON blocks in the response
                json_pattern = r'```json\s*([\s\S]*?)\s*```'
                json_match = re.search(json_pattern, content)
                
                if json_match:
                    try:
                        plan_json = json.loads(json_match.group(1))
                        return plan_json
                    except json.JSONDecodeError:
                        pass
                
                # If no JSON block or failed to parse, look for other structured content
                plan = {
                    "title": "Research Plan",
                    "steps": [],
                    "raw_content": content
                }
                
                # Extract subtasks if available
                plan["steps"] = agent.subtasks if hasattr(agent, 'subtasks') and agent.subtasks else []
                
                return plan
        
        # Return empty plan if no assistant message found
        return {"title": "Research Plan", "steps": []}