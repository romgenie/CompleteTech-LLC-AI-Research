"""
Example demonstrating the usage of the AutoCodeAgent adapter.

This example shows how to use the AutoCodeAgent adapter to generate code,
implement algorithms, and perform web searches.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parents[2]
sys.path.append(str(project_root))

from src.research_orchestrator.external_adapters.autocode_agent import AutoCodeAgentAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_code_example(adapter):
    """Example of generating code with the adapter."""
    logger.info("===== Generating Code Example =====")
    
    # Parameters for code generation
    params = {
        "specification": "Create a function that calculates the Fibonacci sequence up to n terms",
        "language": "python",
        "include_tests": True,
        "add_documentation": True
    }
    
    # Execute the action
    result = adapter.execute("generate_code", params)
    
    # Check result
    if result["success"]:
        logger.info(f"Generated code (Task ID: {result['task_id']}):")
        logger.info(f"\n{result['code']}")
    else:
        logger.error(f"Code generation failed: {result.get('error', 'Unknown error')}")
    
    return result


def implement_algorithm_example(adapter):
    """Example of implementing an algorithm with the adapter."""
    logger.info("===== Implementing Algorithm Example =====")
    
    # Parameters for algorithm implementation
    params = {
        "algorithm_name": "Quick Sort",
        "algorithm_description": "A divide-and-conquer sorting algorithm that works by selecting a 'pivot' element and partitioning the array around the pivot.",
        "pseudocode": """
function quicksort(array, low, high)
    if low < high
        pivot_index = partition(array, low, high)
        quicksort(array, low, pivot_index - 1)
        quicksort(array, pivot_index + 1, high)

function partition(array, low, high)
    pivot = array[high]
    i = low - 1
    for j = low to high - 1
        if array[j] <= pivot
            i = i + 1
            swap array[i] with array[j]
    swap array[i + 1] with array[high]
    return i + 1
        """,
        "language": "python",
        "include_tests": True,
        "paper_references": ["Hoare, C. A. R. (1962). Quicksort. The Computer Journal, 5(1), 10-16."]
    }
    
    # Execute the action
    result = adapter.execute("implement_algorithm", params)
    
    # Check result
    if result["success"]:
        logger.info(f"Implemented algorithm (Task ID: {result['task_id']}):")
        logger.info(f"\n{result['code']}")
    else:
        logger.error(f"Algorithm implementation failed: {result.get('error', 'Unknown error')}")
    
    return result


def task_decomposition_example(adapter):
    """Example of decomposing a complex task with the adapter."""
    logger.info("===== Task Decomposition Example =====")
    
    # Parameters for task decomposition
    params = {
        "task": "Build a web application that collects research papers from ArXiv, extracts key information, and visualizes research trends over time",
        "max_subtasks": 7
    }
    
    # Execute the action
    result = adapter.execute("decompose_task", params)
    
    # Check result
    if result["success"]:
        logger.info(f"Task decomposition (Task ID: {result['task_id']}):")
        
        # Print the main task
        logger.info(f"Main task: {result['plan']['main_task']}")
        
        # Print the subtasks
        logger.info("Subtasks:")
        for subtask in result['plan']['subtasks']:
            logger.info(f"  - {subtask['name']}: {subtask['description']}")
            if subtask['dependencies']:
                logger.info(f"    Dependencies: {', '.join(subtask['dependencies'])}")
            logger.info(f"    Complexity: {subtask['estimated_complexity']}, Time: {subtask['estimated_time']}")
        
        # Print execution order
        logger.info(f"Execution order: {' -> '.join(result['plan']['execution_order'])}")
        logger.info(f"Estimated total time: {result['plan']['estimated_total_time']}")
    else:
        logger.error(f"Task decomposition failed: {result.get('error', 'Unknown error')}")
    
    return result


def web_search_example(adapter):
    """Example of performing a web search with the adapter."""
    logger.info("===== Web Search Example =====")
    
    # Parameters for web search
    params = {
        "query": "Recent advancements in transformer architectures for NLP",
        "search_type": "research",
        "max_results": 5
    }
    
    # Execute the action
    result = adapter.execute("web_search", params)
    
    # Check result
    if result["success"]:
        logger.info(f"Web search results (Task ID: {result['task_id']}):")
        
        # Print the summary
        logger.info(f"Summary: {result['summary']}")
        
        # Print the results
        logger.info(f"Found {len(result['results'])} results:")
        for i, res in enumerate(result['results']):
            logger.info(f"  {i+1}. {res['title']}")
            logger.info(f"     Source: {res['source']}")
            if 'authors' in res:
                logger.info(f"     Authors: {', '.join(res['authors'])}")
            if 'abstract' in res:
                logger.info(f"     Abstract: {res['abstract'][:100]}...")
            logger.info(f"     URL: {res['url']}")
            logger.info(f"     Relevance: {res['relevance']:.2f}")
            logger.info("")
    else:
        logger.error(f"Web search failed: {result.get('error', 'Unknown error')}")
    
    return result


def code_execution_example(adapter, task_id):
    """Example of executing generated code with the adapter."""
    logger.info("===== Code Execution Example =====")
    
    # Parameters for code execution
    params = {
        "task_id": task_id,
        "timeout": 10
    }
    
    # Execute the action
    result = adapter.execute("execute_code", params)
    
    # Check result
    if result["success"]:
        logger.info(f"Code execution result:")
        logger.info(f"  Status: {result['execution_status']}")
        logger.info(f"  Execution time: {result['execution_time']:.2f} seconds")
        logger.info(f"  Output: {result['output']}")
        if 'resources_used' in result:
            logger.info(f"  Resources used: CPU: {result['resources_used']['cpu']}, Memory: {result['resources_used']['memory']}")
    else:
        logger.error(f"Code execution failed: {result.get('error', 'Unknown error')}")
    
    return result


def main():
    """Run the AutoCodeAgent adapter examples."""
    logger.info("Starting AutoCodeAgent adapter examples")
    
    # Initialize the adapter
    # If you have a specific repository path, you can specify it here
    adapter = AutoCodeAgentAdapter()
    
    # Configure the adapter
    config = {
        "mode": "intellichain",  # Use intellichain mode for code generation
        "model": "gpt-4",        # Use GPT-4 as the model
        "enable_execution": True # Enable code execution
    }
    
    # Initialize the adapter
    if not adapter.initialize(config):
        logger.error("Failed to initialize AutoCodeAgent adapter")
        return
    
    logger.info(f"Adapter initialized: {adapter}")
    logger.info(f"Capabilities: {', '.join(adapter.get_capabilities())}")
    
    # Run the examples
    try:
        # Generate code example
        code_result = generate_code_example(adapter)
        
        # Implement algorithm example
        algorithm_result = implement_algorithm_example(adapter)
        
        # Execute the generated code
        if code_result["success"]:
            execution_result = code_execution_example(adapter, code_result["task_id"])
        
        # Task decomposition example
        task_result = task_decomposition_example(adapter)
        
        # Switch to deep_search mode for web search
        adapter.shutdown()
        adapter.initialize({"mode": "deep_search", "model": "gpt-4"})
        
        # Web search example
        search_result = web_search_example(adapter)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
    
    # Shutdown the adapter
    adapter.shutdown()
    logger.info("Examples completed")


if __name__ == "__main__":
    main()