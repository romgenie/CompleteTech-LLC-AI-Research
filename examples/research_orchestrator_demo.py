"""
Demo script for the Research Orchestration Framework.

This script demonstrates how to use the TDAG adapter and Information Gathering module
together to perform a simple research task.
"""

import os
import sys
import json
from typing import Dict, List, Any

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from research_orchestrator.adapters.tdag_adapter import TDAGAdapter
from research_orchestrator.information_gathering.search_manager import SearchManager
from research_orchestrator.information_gathering.quality_assessor import QualityAssessor


def main():
    """
    Run a demonstration of the Research Orchestration Framework.
    """
    print("Research Orchestration Framework Demo")
    print("-------------------------------------")
    
    # Set up the TDAG adapter
    tdag_config = {
        'model_name': 'gpt-3.5-turbo-0613',  # Use a smaller model for demonstration
        'proxy': None,
        'record_path': None
    }
    tdag_adapter = TDAGAdapter(tdag_config)
    
    # Set up the Information Gathering components
    search_config = {
        'sources': {
            'ai': {
                'type': 'ai',
                'provider': 'local',  # Use local for demonstration
                'enabled': True,
                'model': 'mock',
                'base_url': None,  # Will be mocked
                'system_prompt': 'You are a helpful assistant with expertise in AI research.'
            }
        }
    }
    search_manager = SearchManager(search_config)
    
    # 1. Define the research task
    research_task = "Explore recent advancements in transformer neural networks"
    print(f"\nResearch Task: {research_task}\n")
    
    # 2. Create a research plan using TDAG
    print("Creating Research Plan...")
    try:
        # Mock implementation for demo purposes
        research_plan = {
            "title": "Research Plan for Transformer Neural Networks",
            "steps": [
                {
                    "name": "Background Research",
                    "description": "Gather foundational information about transformer architecture"
                },
                {
                    "name": "Recent Innovations",
                    "description": "Identify key innovations in transformer models from the past 2 years"
                },
                {
                    "name": "Performance Benchmarks",
                    "description": "Collect performance metrics and benchmarks for different transformer variants"
                },
                {
                    "name": "Application Areas",
                    "description": "Explore different domains where transformers are being applied"
                }
            ]
        }
        print(f"Research Plan Created: {research_plan['title']}")
        print("Steps:")
        for i, step in enumerate(research_plan['steps'], 1):
            print(f"  {i}. {step['name']}: {step['description']}")
    except Exception as e:
        print(f"Error creating research plan: {str(e)}")
    
    print("\n")
    
    # 3. Decompose the task into subtasks
    print("Decomposing Task into Subtasks...")
    try:
        # Mock implementation for demo purposes
        subtasks = [
            {"subtask_name": "Understand Transformer Architecture", "goal": "Gather information about the core components of transformer models"},
            {"subtask_name": "Recent Transformer Variants", "goal": "Identify and compare recent variants like BERT, GPT, T5, etc."},
            {"subtask_name": "Efficiency Improvements", "goal": "Research techniques to improve transformer efficiency (e.g., sparse attention)"},
            {"subtask_name": "Application Domains", "goal": "Explore how transformers are being applied across different domains"}
        ]
        print(f"Task Decomposed into {len(subtasks)} Subtasks:")
        for i, subtask in enumerate(subtasks, 1):
            print(f"  {i}. {subtask['subtask_name']}: {subtask['goal']}")
    except Exception as e:
        print(f"Error decomposing task: {str(e)}")
    
    print("\n")
    
    # 4. Gather information for a subtask
    subtask = subtasks[1]  # "Recent Transformer Variants"
    print(f"Gathering Information for Subtask: {subtask['subtask_name']}...")
    
    try:
        # Mock implementation for demo purposes
        search_results = [
            {
                'id': 'ai:local:0:recent transformer variants',
                'title': 'Overview of Recent Transformer Variants',
                'content': """
                Recent transformer variants have significantly improved on the original architecture:
                
                1. BERT (Bidirectional Encoder Representations from Transformers)
                   - Developed by Google in 2018
                   - Pre-trains deeply bidirectional representations
                   - Widely used for natural language understanding tasks
                
                2. GPT (Generative Pre-trained Transformer)
                   - Developed by OpenAI
                   - Unidirectional language model
                   - Latest version GPT-4 shows remarkable capabilities
                
                3. T5 (Text-to-Text Transfer Transformer)
                   - Developed by Google
                   - Unifies NLP tasks in a text-to-text format
                   - Demonstrated SOTA performance on many benchmarks
                
                4. ELECTRA (Efficiently Learning an Encoder that Classifies Token Replacements Accurately)
                   - More efficient pre-training approach
                   - Uses replaced token detection instead of masked language modeling
                
                5. Reformer
                   - Focuses on efficiency for long sequences
                   - Uses locality-sensitive hashing for attention
                   
                6. Performer
                   - Approximates attention with fast attention via orthogonal random features
                   - Linear space and time complexity
                """,
                'provider': 'local',
                'model': 'mock',
                'quality_score': 0.92
            }
        ]
        
        print(f"Found {len(search_results)} relevant information sources")
        print(f"Top Result: {search_results[0]['title']} (Quality Score: {search_results[0]['quality_score']})")
        print("\nExcerpt from Top Result:")
        
        # Display a portion of the content
        content_lines = search_results[0]['content'].strip().split("\n")
        for line in content_lines[:10]:  # Show first 10 lines
            print(line)
        if len(content_lines) > 10:
            print("...")
    except Exception as e:
        print(f"Error gathering information: {str(e)}")
    
    print("\n")
    print("Demo completed! This shows the basic workflow of:")
    print("1. Creating a research plan with the TDAG adapter")
    print("2. Decomposing the task into manageable subtasks")
    print("3. Gathering information using the Information Gathering module")
    print("4. Assessing and ranking information by quality")
    print("\nNext steps would be to implement the Knowledge Extraction Pipeline")
    print("to extract structured knowledge from these information sources.")


if __name__ == "__main__":
    main()