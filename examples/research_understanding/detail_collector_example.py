"""
Example script demonstrating the use of the Implementation Detail Collector.

This example shows how to:
1. Collect implementation details from a research paper
2. Enhance algorithms with additional implementation details
3. Access detailed implementation information
"""

import os
import tempfile
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the necessary modules
from research_orchestrator.research_understanding import ResearchUnderstandingEngine
from research_orchestrator.research_understanding.implementation_details import ImplementationDetailCollector
from paper_processing_example import create_sample_paper  # Reuse sample paper creation function


def run_detail_collector_example():
    """Run the Implementation Detail Collector example."""
    logger.info("Starting Implementation Detail Collector example")
    
    # Create a temporary directory for caching
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = os.path.join(temp_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a sample paper
        logger.info("Creating sample paper")
        sample_paper = create_sample_paper()
        
        # Initialize the Implementation Detail Collector
        logger.info("Initializing Implementation Detail Collector")
        collector = ImplementationDetailCollector(
            language_model_config={
                "model": "claude-3-5-sonnet",
                "temperature": 0.2,
            },
            cache_dir=cache_dir
        )
        
        # Collect implementation details
        logger.info(f"Collecting implementation details from paper: {sample_paper.paper_id}")
        details = collector.collect_details(
            paper=sample_paper,
            algorithms=sample_paper.algorithms
        )
        
        # Display the collected details
        logger.info("Collected implementation details:")
        logger.info(f"  Code snippets: {len(details.code_snippets)}")
        logger.info(f"  Requirements: {len(details.requirements)}")
        logger.info(f"  Datasets: {len(details.datasets)}")
        logger.info(f"  Metrics: {len(details.metrics)}")
        logger.info(f"  Hyperparameters: {len(details.hyperparameters)}")
        logger.info(f"  Libraries used: {details.libraries_used}")
        
        if details.environment:
            logger.info("  Environment information:")
            if details.environment.hardware:
                logger.info(f"    Hardware: {details.environment.hardware}")
            if details.environment.software:
                logger.info(f"    Software: {details.environment.software}")
            if details.environment.dependencies:
                logger.info(f"    Dependencies: {details.environment.dependencies}")
        
        # Enhance an algorithm with implementation details
        if sample_paper.algorithms:
            algorithm = sample_paper.algorithms[0]
            logger.info(f"Enhancing algorithm: {algorithm.name}")
            enhanced_algorithm = collector.enhance_algorithm(
                algorithm=algorithm,
                paper=sample_paper
            )
            
            logger.info("Enhanced algorithm:")
            if enhanced_algorithm.parameters:
                logger.info(f"  Parameters: {len(enhanced_algorithm.parameters)}")
                for param in enhanced_algorithm.parameters:
                    type_hint = f": {param.type_hint}" if param.type_hint else ""
                    default = f" = {param.default_value}" if param.default_value is not None else ""
                    logger.info(f"    {param.name}{type_hint}{default}")
            
            if enhanced_algorithm.subroutines:
                logger.info(f"  Subroutines: {len(enhanced_algorithm.subroutines)}")
                for subroutine in enhanced_algorithm.subroutines:
                    logger.info(f"    {subroutine.name}")
            
            if enhanced_algorithm.implementation_notes:
                logger.info("  Implementation notes preview:")
                notes_preview = enhanced_algorithm.implementation_notes.split('\n')[:3]
                for line in notes_preview:
                    logger.info(f"    {line}")
                if len(enhanced_algorithm.implementation_notes.split('\n')) > 3:
                    logger.info("    ...")
        
        # Use the Research Understanding Engine
        logger.info("Using Research Understanding Engine for end-to-end processing")
        engine = ResearchUnderstandingEngine(
            config={
                "language_model_config": {
                    "model": "claude-3-5-sonnet",
                    "temperature": 0.2,
                }
            },
            cache_dir=cache_dir
        )
        
        # Mock the paper processor to return our sample paper
        original_process_paper = engine.paper_processor.process_paper
        engine.paper_processor.process_paper = lambda **kwargs: sample_paper
        
        try:
            # Process the paper
            sample_path = os.path.join(temp_dir, "sample_paper.pdf")
            logger.info(f"Processing paper: {sample_path}")
            result = engine.process_paper(
                paper_path=sample_path,
                collect_implementation_details=True
            )
            
            # Display the results
            paper = result["paper"]
            implementation_details = result["implementation_details"]
            
            logger.info(f"Processed paper: {paper.title}")
            logger.info(f"Implementation details collected: {implementation_details is not None}")
            
            if implementation_details:
                logger.info(f"  Total code snippets: {len(implementation_details.code_snippets)}")
                logger.info(f"  Total requirements: {len(implementation_details.requirements)}")
                
                # Use the new method to enhance an algorithm
                if result["algorithms"]:
                    algorithm = result["algorithms"][0]
                    logger.info(f"Enhancing algorithm with details: {algorithm.name}")
                    enhanced_algorithm = engine.enhance_algorithm_with_details(
                        algorithm=algorithm,
                        paper=paper
                    )
                    
                    logger.info(f"  Enhanced algorithm: {enhanced_algorithm.name}")
                    logger.info(f"  Parameters: {len(enhanced_algorithm.parameters) if enhanced_algorithm.parameters else 0}")
                    logger.info(f"  Subroutines: {len(enhanced_algorithm.subroutines) if enhanced_algorithm.subroutines else 0}")
                    
                    # Generate implementation
                    logger.info("Generating implementation with enriched details")
                    implementation = engine.implementation_generator.generate_implementation(
                        algorithm=enhanced_algorithm,
                        language="python",
                        include_comments=True
                    )
                    
                    logger.info("Implementation preview:")
                    preview_lines = implementation.split('\n')[:8]
                    for line in preview_lines:
                        logger.info(f"  {line}")
                    logger.info("  ...")
        
        finally:
            # Restore the original method
            engine.paper_processor.process_paper = original_process_paper
        
        logger.info("Example completed successfully")


if __name__ == "__main__":
    run_detail_collector_example()