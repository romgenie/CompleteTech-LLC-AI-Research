"""
Example script demonstrating the use of the GDesigner adapter.

This example shows how to:
1. Initialize the GDesigner adapter
2. Create and configure agent graphs
3. Execute actions using the graph-based multi-agent system
4. Get results and statistics from the execution
"""

import os
import logging
import json
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the adapter
from research_orchestrator.external_adapters import GDesignerAdapter


def print_section(title: str) -> None:
    """Print a section heading."""
    print("\n" + "=" * 40)
    print(f" {title} ".center(40, "="))
    print("=" * 40 + "\n")


def print_result(result: Dict[str, Any], indent: int = 0) -> None:
    """Print a result dictionary in a readable format."""
    indent_str = " " * indent
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"{indent_str}{key}:")
            print_result(value, indent + 2)
        elif isinstance(value, list):
            print(f"{indent_str}{key}: [{len(value)} items]")
            if value and not isinstance(value[0], dict):
                print(f"{indent_str}  {value}")
        else:
            print(f"{indent_str}{key}: {value}")


def create_graph_example(adapter: GDesignerAdapter) -> None:
    """Example of creating a graph."""
    print_section("Creating Agent Graph")
    
    # Define graph creation parameters
    params = {
        "graph_type": "standard",
        "topology": "Star",
        "num_agents": 5,
        "agent_types": ["coordinator", "researcher", "evaluator", "summarizer", "critic"]
    }
    
    # Create the graph
    result = adapter.execute("create_graph", params)
    
    # Print the result
    print_result(result)


def add_agent_example(adapter: GDesignerAdapter) -> None:
    """Example of adding an agent to the graph."""
    print_section("Adding Agent to Graph")
    
    # Define agent parameters
    params = {
        "agent_type": "synthesizer",
        "agent_config": {
            "model": "claude-3-haiku",
            "temperature": 0.2,
            "max_tokens": 4000
        },
        "connections": [
            {"from": 0, "bidirectional": True},  # Connect to coordinator
            {"from": 3, "bidirectional": True}   # Connect to summarizer
        ]
    }
    
    # Add the agent
    result = adapter.execute("add_agent", params)
    
    # Print the result
    print_result(result)


def change_topology_example(adapter: GDesignerAdapter) -> None:
    """Example of changing the graph topology."""
    print_section("Changing Graph Topology")
    
    # Define topology parameters
    params = {
        "topology": "FullConnected"
    }
    
    # Change the topology
    result = adapter.execute("change_topology", params)
    
    # Print the result
    print_result(result)


def execute_graph_example(adapter: GDesignerAdapter) -> None:
    """Example of executing the graph."""
    print_section("Executing Agent Graph")
    
    # Define execution parameters
    params = {
        "query": "Analyze the advantages and limitations of transformer architectures in NLP",
        "max_steps": 15,
        "timeout": 60
    }
    
    # Execute the graph
    result = adapter.execute("execute_graph", params)
    
    # Print the result
    print("Query: " + params["query"])
    print("\nResponse Summary:")
    print(result["response"])
    print("\nExecution Statistics:")
    print(f"Steps executed: {result['steps_executed']}")
    print(f"Execution time: {result['execution_time']:.2f} seconds")
    
    # Print agent statistics
    print("\nAgent Statistics:")
    for agent_stat in result["agent_stats"]:
        print(f"  {agent_stat['agent_id']}:")
        print(f"    Messages sent: {agent_stat['messages_sent']}")
        print(f"    Messages received: {agent_stat['messages_received']}")
        print(f"    Processing time: {agent_stat['processing_time']:.2f} seconds")


def optimize_graph_example(adapter: GDesignerAdapter) -> None:
    """Example of optimizing the graph."""
    print_section("Optimizing Agent Graph")
    
    # Define optimization parameters
    params = {
        "optimization_level": "high",
        "optimization_target": "performance"
    }
    
    # Optimize the graph
    result = adapter.execute("optimize_graph", params)
    
    # Print the result
    print_result(result)


def enable_gnn_example(adapter: GDesignerAdapter) -> None:
    """Example of enabling GNN-based coordination."""
    print_section("Enabling GNN-based Coordination")
    
    # Define GNN parameters
    params = {
        "enable": True,
        "gnn_config": {
            "layers": 3,
            "hidden_dim": 128,
            "aggregation": "sum",
            "activation": "leaky_relu"
        }
    }
    
    # Enable GNN
    result = adapter.execute("enable_gnn", params)
    
    # Print the result
    print_result(result)


def get_stats_example(adapter: GDesignerAdapter) -> None:
    """Example of getting execution statistics."""
    print_section("Getting Execution Statistics")
    
    # Define statistics parameters
    params = {
        "include_agents": True,
        "include_edges": True,
        "include_history": True
    }
    
    # Get statistics
    result = adapter.execute("get_execution_stats", params)
    
    # Print the result
    print("Graph Statistics:")
    print(f"Topology: {result['topology']}")
    print(f"Number of agents: {result['num_agents']}")
    print(f"Number of edges: {result['num_edges']}")
    print(f"GNN enabled: {result['gnn_enabled']}")
    print(f"Execution count: {result['execution_count']}")
    print(f"Average execution time: {result['average_execution_time']:.2f} seconds")
    
    print("\nLast Execution:")
    print(f"Timestamp: {result['last_execution']['timestamp']}")
    print(f"Execution time: {result['last_execution']['execution_time']:.2f} seconds")
    print(f"Success: {result['last_execution']['success']}")
    
    # Print execution history
    if "execution_history" in result:
        print("\nExecution History:")
        for i, execution in enumerate(result["execution_history"]):
            print(f"  {i+1}. {execution['timestamp']} - {execution['query']}")
            print(f"     Time: {execution['execution_time']:.2f}s, Success: {execution['success']}")


def run_gdesigner_example() -> None:
    """Run the GDesigner adapter examples."""
    logger.info("Starting GDesigner adapter examples")
    
    # Initialize the adapter
    # In a real scenario, you would provide the actual repository path
    adapter = GDesignerAdapter()
    
    # Initialize the adapter with configuration
    config = {
        "graph_type": "standard",
        "enable_gnn": False,
        "optimization_level": "medium",
        "agent_types": ["coordinator", "researcher", "evaluator", "summarizer", "critic", "synthesizer"]
    }
    
    if not adapter.initialize(config):
        logger.error("Failed to initialize GDesigner adapter")
        return
    
    # Check if the adapter is available
    if not adapter.is_available():
        logger.warning("GDesigner adapter is not available (repository may not be found)")
        # For demonstration purposes, we'll continue anyway since we're using mock implementations
    
    # Get the adapter capabilities
    print_section("Adapter Capabilities")
    capabilities = adapter.get_capabilities()
    print("Available capabilities:")
    for capability in capabilities:
        print(f"  - {capability}")
    
    # Run example actions
    create_graph_example(adapter)
    add_agent_example(adapter)
    change_topology_example(adapter)
    optimize_graph_example(adapter)
    enable_gnn_example(adapter)
    execute_graph_example(adapter)
    get_stats_example(adapter)
    
    # Shut down the adapter
    adapter.shutdown()
    logger.info("GDesigner adapter examples completed")


if __name__ == "__main__":
    run_gdesigner_example()