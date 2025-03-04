#!/usr/bin/env python3
"""
Research Understanding Engine Example.

This script demonstrates how to use the Research Understanding Engine 
to process research papers, extract algorithms, and generate implementations.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.research_orchestrator.research_understanding.understanding_engine import (
    ResearchUnderstandingEngine,
    PaperFormat
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the main example."""
    logger.info("Initializing Research Understanding Engine Example")
    
    # Create cache directory
    cache_dir = Path(__file__).parent / "cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Initialize the engine
    engine = ResearchUnderstandingEngine(
        config={
            "language_model_config": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 4000
            }
        },
        cache_dir=str(cache_dir)
    )
    
    # Example 1: Process a local paper (simulated in this example)
    process_local_paper(engine)
    
    # Example 2: Process an ArXiv paper (requires arxiv package)
    # process_arxiv_paper(engine)
    
    logger.info("Research Understanding Engine Example completed")

def process_local_paper(engine):
    """Process a local research paper."""
    logger.info("Example 1: Processing a local paper")
    
    # Create a simple example paper
    sample_paper_path = Path(__file__).parent / "sample_paper.md"
    
    # Only create the sample file if it doesn't exist
    if not sample_paper_path.exists():
        with open(sample_paper_path, 'w') as f:
            f.write("""# Sample Research Paper

## Abstract

This paper introduces a novel sorting algorithm called QuickMergeSort, which combines 
the benefits of QuickSort and MergeSort. Our algorithm achieves O(n log n) time complexity
in the average case while maintaining O(n log n) worst-case performance.

## 1. Introduction

Sorting algorithms are fundamental in computer science. QuickSort offers excellent average-case
performance but suffers from O(n²) worst-case complexity. MergeSort maintains O(n log n)
worst-case performance but requires additional memory. Our QuickMergeSort algorithm aims
to combine the strengths of both approaches.

## 2. The QuickMergeSort Algorithm

The QuickMergeSort algorithm works as follows:

```python
def quick_merge_sort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
        
    if low < high:
        # If the array segment is small, use insertion sort
        if high - low < 10:
            insertion_sort(arr, low, high)
            return
            
        # Otherwise use quicksort partitioning
        pivot = partition(arr, low, high)
        
        # Recursively sort the left half
        quick_merge_sort(arr, low, pivot-1)
        
        # Recursively sort the right half
        quick_merge_sort(arr, pivot+1, high)
        
        # Merge the two sorted halves if needed
        if is_merging_beneficial(arr, low, pivot, high):
            merge(arr, low, pivot, high)
```

The time complexity of QuickMergeSort is O(n log n) in both average and worst case.
The space complexity is O(n) in the worst case.

## 3. Experimental Results

We compared QuickMergeSort against standard QuickSort and MergeSort implementations
on randomly generated arrays of different sizes.

Our algorithm performed better than QuickSort on adversarial inputs and used less
memory than MergeSort on average.

## 4. Conclusion

QuickMergeSort offers a balanced approach to sorting, maintaining good performance
characteristics in both time and space complexity.

## References

1. Hoare, C. A. R. (1962). "Quicksort". The Computer Journal. 5 (1): 10–16.
2. Knuth, D. E. (1998). The Art of Computer Programming, Volume 3: Sorting and Searching.
""")
    
    # Process the paper
    result = engine.process_paper(
        paper_path=str(sample_paper_path),
        paper_format=PaperFormat.MARKDOWN,
        metadata={
            "title": "QuickMergeSort: A Hybrid Sorting Algorithm",
            "authors": ["Jane Smith", "John Doe"],
            "publication_date": "2023-01-15",
            "keywords": ["algorithms", "sorting", "computer science"]
        }
    )
    
    # Show paper summary
    paper = result["paper"]
    logger.info(f"Processed paper: {paper.title}")
    logger.info(f"Authors: {', '.join(paper.authors)}")
    logger.info(f"Number of sections: {len(paper.sections)}")
    
    # Show extracted algorithms
    algorithms = result["algorithms"]
    logger.info(f"Found {len(algorithms)} algorithms:")
    for algo in algorithms:
        logger.info(f"  - {algo.name}")
        if algo.complexity:
            logger.info(f"    Time complexity: {algo.complexity.get('time', 'Unknown')}")
            logger.info(f"    Space complexity: {algo.complexity.get('space', 'Unknown')}")
    
    # Generate algorithm implementation
    if algorithms:
        implementations = engine.generate_implementations(algorithms)
        for algo_id, implementation in implementations.items():
            logger.info(f"\nGenerated implementation for {algo_id}:")
            logger.info("-" * 40)
            print(implementation)
            logger.info("-" * 40)
    
    # Extract implementation details
    if "implementation_details" in result and result["implementation_details"]:
        details = result["implementation_details"]
        logger.info(f"\nImplementation details:")
        logger.info(f"Code snippets: {len(details.code_snippets)}")
        logger.info(f"Requirements: {len(details.requirements)}")
        logger.info(f"Datasets: {len(details.datasets)}")
        
        # Show libraries used if any
        if details.libraries_used:
            logger.info(f"Libraries used: {', '.join(details.libraries_used)}")

def process_arxiv_paper(engine):
    """Process a paper from ArXiv."""
    try:
        # Check if arxiv package is available
        import arxiv
    except ImportError:
        logger.error("ArXiv example requires the 'arxiv' package. Install with: pip install arxiv")
        return
    
    logger.info("Example 2: Processing an ArXiv paper")
    
    # Process an arxiv paper by its ID
    # Using a paper about sorting algorithms as an example
    arxiv_id = "2110.01111"  # Replace with a real ArXiv ID
    
    try:
        result = engine.process_arxiv_paper(
            arxiv_id=arxiv_id,
            extract_algorithms=True,
            collect_implementation_details=True
        )
        
        # Show paper summary
        paper = result["paper"]
        logger.info(f"Processed ArXiv paper: {paper.title}")
        logger.info(f"Authors: {', '.join(paper.authors)}")
        logger.info(f"Abstract: {paper.abstract[:100]}...")
        
        # Show extracted algorithms
        algorithms = result["algorithms"]
        logger.info(f"Found {len(algorithms)} algorithms")
        
        # Summary of implementation details
        if "implementation_details" in result and result["implementation_details"]:
            details = result["implementation_details"]
            logger.info(f"Code snippets: {len(details.code_snippets)}")
            logger.info(f"Datasets: {len(details.datasets)}")
            logger.info(f"Metrics: {len(details.metrics)}")
            
            # Export to knowledge graph format
            kg_export = engine.export_to_knowledge_graph(paper, details)
            logger.info(f"Knowledge graph export: {len(kg_export['entities'])} entities, {len(kg_export['relationships'])} relationships")
    
    except Exception as e:
        logger.error(f"Error processing ArXiv paper: {e}")

if __name__ == "__main__":
    main()