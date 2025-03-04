"""
Example script demonstrating the use of the Open Deep Research adapter.

This example shows how to:
1. Initialize the Open Deep Research adapter
2. Search for information from various sources
3. Generate research reports and sections
4. Use the human-in-the-loop feedback mechanism
"""

import os
import logging
import json
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the adapter
from research_orchestrator.external_adapters import OpenDeepResearchAdapter


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


def search_information_example(adapter: OpenDeepResearchAdapter) -> None:
    """Example of searching for information."""
    print_section("Searching for Information")
    
    # Define search parameters
    params = {
        "query": "recent advances in transformer models for natural language processing",
        "search_apis": ["tavily", "perplexity", "arxiv"],
        "max_results": 5,
        "include_academic": True,
        "filters": {"year": "2022-2023"}
    }
    
    # Execute the search
    result = adapter.execute("search_information", params)
    
    # Print the search metadata
    print("Search Query:", result["query"])
    print("Search ID:", result["search_id"])
    print("\nMetadata:")
    print(f"  APIs used: {', '.join(result['metadata']['apis_used'])}")
    print(f"  Total results: {result['metadata']['num_results']}")
    print(f"  Processing time: {result['metadata']['processing_time']:.2f} seconds")
    
    # Print search results
    print("\nTop Results:")
    for i, item in enumerate(result["results"][:3]):  # Show only first 3 results
        print(f"\n{i+1}. {item['title']}")
        print(f"   Source: {item['source']}")
        print(f"   URL: {item['url']}")
        if "snippet" in item:
            print(f"   Snippet: {item['snippet'][:100]}...")
        elif "abstract" in item:
            print(f"   Abstract: {item['abstract'][:100]}...")
        print(f"   Relevance: {item['relevance_score']:.2f}")


def get_search_apis_example(adapter: OpenDeepResearchAdapter) -> None:
    """Example of getting information about available search APIs."""
    print_section("Available Search APIs")
    
    # Get API information
    result = adapter.execute("get_search_apis", {})
    
    # Print the APIs
    print("Available Search APIs:")
    for api in result["apis"]:
        status = "✅ Enabled" if api["enabled"] else "❌ Disabled"
        api_type = api["type"].capitalize()
        quota = f"Quota: {api['quota_remaining']}" if api['quota_remaining'] is not None else "Unlimited"
        
        print(f"  - {api['name']} ({api_type}): {status}, {quota}")
    
    print("\nDefault APIs:")
    print(f"  {', '.join(result['default_apis'])}")


def configure_search_example(adapter: OpenDeepResearchAdapter) -> None:
    """Example of configuring search settings."""
    print_section("Configuring Search Settings")
    
    # Define configuration parameters
    params = {
        "max_results": 15,
        "default_apis": ["tavily", "arxiv", "pubmed"],
        "enabled_apis": {
            "perplexity": False,
            "arxiv": True,
            "pubmed": True
        }
    }
    
    # Configure search
    result = adapter.execute("configure_search", params)
    
    # Print the updated configuration
    print("Updated Search Configuration:")
    print(f"  Max results: {result['max_results']}")
    print(f"  Default APIs: {', '.join(result['default_apis'])}")
    
    print("\nAPI Status:")
    for api_name, api_info in result["api_status"].items():
        status = "✅ Enabled" if api_info["enabled"] else "❌ Disabled"
        print(f"  - {api_name}: {status}")


def get_report_plan_example(adapter: OpenDeepResearchAdapter) -> None:
    """Example of getting a report plan."""
    print_section("Getting Report Plan")
    
    # Define report plan parameters
    params = {
        "query": "impact of large language models on education",
        "depth": "comprehensive"
    }
    
    # Get report plan
    result = adapter.execute("get_report_plan", params)
    
    # Print the report plan
    print("Report Plan:")
    print(f"  Report ID: {result['report_id']}")
    print(f"  Query: {result['query']}")
    print(f"  Depth: {result['depth']}")
    print(f"  Estimated Length: {result['estimated_length']} words")
    print(f"  Estimated Sources: {result['estimated_sources']}")
    
    print("\nPlanned Sections:")
    for i, section in enumerate(result["sections"]):
        print(f"\n{i+1}. {section['title']}")
        print(f"   {section['content']}")
        print("   Search Queries:")
        for query in section["search_queries"]:
            print(f"     - {query}")


def provide_feedback_example(adapter: OpenDeepResearchAdapter) -> None:
    """Example of providing feedback on a report plan."""
    print_section("Providing Feedback on Report Plan")
    
    # First get a report plan
    plan_result = adapter.execute("get_report_plan", {
        "query": "ethical considerations in artificial intelligence",
        "depth": "comprehensive"
    })
    
    report_id = plan_result["report_id"]
    print(f"Received report plan with ID: {report_id}")
    
    # Define feedback parameters
    params = {
        "report_id": report_id,
        "feedback_type": "plan",
        "approved": True,
        "feedback": "The plan looks good, but please add a section on AI regulation and governance."
    }
    
    # Provide feedback
    result = adapter.execute("provide_feedback", params)
    
    # Print the result
    print("\nFeedback Result:")
    print(f"  Report ID: {result['report_id']}")
    print(f"  Feedback Type: {result['feedback_type']}")
    print(f"  Approved: {result['approved']}")
    print(f"  Action Taken: {result['action_taken']}")
    print(f"  Next Steps: {result['next_steps']}")


def generate_section_example(adapter: OpenDeepResearchAdapter) -> None:
    """Example of generating a section for a report."""
    print_section("Generating Report Section")
    
    # First get a report plan
    plan_result = adapter.execute("get_report_plan", {
        "query": "applications of reinforcement learning in robotics",
        "depth": "comprehensive"
    })
    
    report_id = plan_result["report_id"]
    section_title = plan_result["sections"][0]["title"]
    search_queries = plan_result["sections"][0]["search_queries"]
    
    # Define section generation parameters
    params = {
        "report_id": report_id,
        "section_title": section_title,
        "search_queries": search_queries,
        "max_length": 500
    }
    
    # Generate section
    result = adapter.execute("generate_section", params)
    
    # Print the section information
    print(f"Generated Section: {result['section_title']}")
    print(f"For Report: {result['report_id']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Processing Time: {result['processing_time']:.2f} seconds")
    print(f"Sources Used: {len(result['sources'])}")
    
    # Print section content
    print("\nSection Content Preview:")
    content_lines = result["content"].strip().split('\n')
    for line in content_lines[:10]:  # Show first 10 lines
        print(line)
    if len(content_lines) > 10:
        print("...")


def generate_report_example(adapter: OpenDeepResearchAdapter) -> None:
    """Example of generating a complete report."""
    print_section("Generating Complete Report")
    
    # Define report generation parameters
    params = {
        "query": "current state of quantum computing",
        "depth": "comprehensive",
        "format": "markdown",
        "max_length": 3000,
        "search_apis": ["tavily", "arxiv", "pubmed"]
    }
    
    # Generate report
    result = adapter.execute("generate_report", params)
    
    # Print report information
    print(f"Generated Report: {result['title']}")
    print(f"Report ID: {result['report_id']}")
    print(f"Query: {result['query']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Processing Time: {result['processing_time']:.2f} seconds")
    print(f"Format: {result['format']}")
    print(f"Number of Sections: {len(result['sections'])}")
    print(f"Number of Sources: {len(result['sources'])}")
    
    # Print section titles
    print("\nReport Sections:")
    for i, section in enumerate(result["sections"]):
        print(f"  {i+1}. {section['title']} ({section['word_count']} words, {section['sources']} sources)")


def run_open_deep_research_example() -> None:
    """Run the Open Deep Research adapter examples."""
    logger.info("Starting Open Deep Research adapter examples")
    
    # Initialize the adapter
    # In a real scenario, you would provide the actual repository path
    adapter = OpenDeepResearchAdapter()
    
    # Initialize the adapter with configuration
    config = {
        "planning_model": "gpt-4-turbo",
        "writing_model": "claude-3-opus",
        "use_academic_sources": True,
        "use_web_sources": True,
        "max_sources": 20,
        "max_search_results": 10
    }
    
    if not adapter.initialize(config):
        logger.error("Failed to initialize Open Deep Research adapter")
        return
    
    # Check if the adapter is available
    if not adapter.is_available():
        logger.warning("Open Deep Research adapter is not available (repository may not be found)")
        # For demonstration purposes, we'll continue anyway since we're using mock implementations
    
    # Get the adapter capabilities
    print_section("Adapter Capabilities")
    capabilities = adapter.get_capabilities()
    print("Available capabilities:")
    for capability in capabilities:
        print(f"  - {capability}")
    
    # Run example actions
    get_search_apis_example(adapter)
    configure_search_example(adapter)
    search_information_example(adapter)
    get_report_plan_example(adapter)
    provide_feedback_example(adapter)
    generate_section_example(adapter)
    generate_report_example(adapter)
    
    # Shut down the adapter
    adapter.shutdown()
    logger.info("Open Deep Research adapter examples completed")


if __name__ == "__main__":
    run_open_deep_research_example()