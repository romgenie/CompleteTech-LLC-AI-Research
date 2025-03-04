"""
Example script demonstrating the use of the Research Understanding Engine.

This example shows how to use the high-level ResearchUnderstandingEngine to:
1. Process a research paper end-to-end
2. Extract algorithms and implementation details
3. Generate code implementations
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
from research_orchestrator.research_understanding.paper_processing import PaperFormat
from paper_processing_example import create_sample_paper  # Reuse sample paper creation function


def run_engine_example():
    """Run the complete Research Understanding Engine example."""
    logger.info("Starting Research Understanding Engine example")
    
    # Create a temporary directory for caching
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = os.path.join(temp_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create a sample PDF file path (we won't actually create the file)
        sample_pdf_path = os.path.join(temp_dir, "sample_paper.pdf")
        
        # Configure the engine
        config = {
            "language_model_config": {
                "model": "claude-3-5-sonnet",
                "temperature": 0.2,
                "max_tokens": 4000
            },
            "document_processors": {
                "pdf": {
                    "use_ocr": False,
                    "extract_images": True
                }
            }
        }
        
        # Initialize the engine
        logger.info("Initializing Research Understanding Engine")
        engine = ResearchUnderstandingEngine(
            config=config,
            cache_dir=cache_dir
        )
        
        # In a real scenario, we would process an actual paper file
        # For this example, we'll mock the paper processing with a sample paper
        
        # Create sample paper and mock the paper processor
        logger.info("Creating sample paper")
        sample_paper = create_sample_paper()
        
        # Let's apply our engine's process_paper method with a mock
        # We'll monkey-patch the paper_processor.process_paper method to return our sample
        original_process_paper = engine.paper_processor.process_paper
        engine.paper_processor.process_paper = lambda **kwargs: sample_paper
        
        try:
            # Process the paper
            logger.info(f"Processing paper: {sample_pdf_path}")
            result = engine.process_paper(
                paper_path=sample_pdf_path,
                paper_format=PaperFormat.PDF,
                metadata={
                    "source": "example",
                    "keywords": ["transformers", "attention", "efficiency"]
                },
                extract_algorithms=True
            )
            
            # Display processing results
            paper = result["paper"]
            algorithms = result["algorithms"]
            
            logger.info(f"Processed paper: {paper.title}")
            logger.info(f"Authors: {', '.join(paper.authors)}")
            logger.info(f"Extracted {len(algorithms)} algorithms")
            
            # Generate implementations for the algorithms
            if algorithms:
                logger.info("Generating implementations")
                implementations = engine.generate_implementations(
                    algorithms=algorithms,
                    language="python",
                    include_comments=True
                )
                
                logger.info(f"Generated {len(implementations)} implementations")
                
                # Display a preview of each implementation
                for algo_id, impl in implementations.items():
                    algo = next(a for a in algorithms if a.algorithm_id == algo_id)
                    logger.info(f"Implementation for {algo.name}:")
                    
                    # Display the first few lines
                    preview_lines = impl.split('\n')[:8]
                    for line in preview_lines:
                        logger.info(f"  {line}")
                    logger.info("  ...")
                
                # Extract detailed implementation information for the first algorithm
                if algorithms:
                    logger.info("Extracting detailed implementation information")
                    algo = algorithms[0]
                    enriched_algo = engine.extract_implementation_details(
                        paper=paper,
                        algorithm_id=algo.algorithm_id
                    )
                    
                    logger.info(f"Enriched algorithm: {enriched_algo.name}")
                    logger.info(f"  Description: {enriched_algo.description[:100]}...")
                    if enriched_algo.complexity:
                        for complexity_type, complexity_value in enriched_algo.complexity.items():
                            logger.info(f"  {complexity_type.capitalize()} complexity: {complexity_value}")
            
            logger.info("Example completed successfully")
            
        finally:
            # Restore the original method
            engine.paper_processor.process_paper = original_process_paper


if __name__ == "__main__":
    run_engine_example()