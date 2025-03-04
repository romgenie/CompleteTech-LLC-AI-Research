"""
Example script demonstrating the use of the Paper Processing and Algorithm Extraction modules.

This example shows how to:
1. Process a research paper to extract structured information
2. Extract algorithms and their implementation details
3. Generate code implementations from the extracted algorithms
"""

import os
from pathlib import Path
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the necessary modules
from research_orchestrator.research_understanding.paper_processing import (
    PaperProcessor, PaperFormat, PaperSection, PaperAlgorithm, StructuredPaper
)
from research_orchestrator.research_understanding.algorithm_extraction import (
    AlgorithmExtractor, ExtractedAlgorithm, AlgorithmImplementationGenerator
)


def create_sample_paper() -> StructuredPaper:
    """
    Create a sample structured paper for demonstration purposes.
    
    In a real application, this would come from processing an actual PDF/HTML paper.
    
    Returns:
        StructuredPaper object with sample content
    """
    # Create sample sections
    intro_section = PaperSection(
        title="Introduction",
        content="""
        In this paper, we present a novel approach to natural language processing
        that leverages recent advances in transformer architectures. Our method,
        called TransformerPlus, builds upon the standard transformer model with
        several key enhancements that improve performance on a range of NLP tasks.
        """
    )
    
    methods_section = PaperSection(
        title="Methodology",
        content="""
        We propose Algorithm TransformerPlus for enhanced language understanding.
        
        The core insight of our approach is to modify the attention mechanism to better
        capture long-range dependencies. The time complexity of our approach is O(n log n)
        where n is the sequence length, which is more efficient than the standard O(n²)
        complexity of vanilla transformers.
        
        Pseudocode for TransformerPlus:
        begin
          Input: Sequence X of length n, model parameters θ
          Let H₀ = Embedding(X)
          for i = 1 to L do
            A = MultiHeadAttention(H_{i-1})
            B = EfficiencyAttention(H_{i-1})  // Our novel component
            C = Combine(A, B)
            H_i = LayerNorm(H_{i-1} + C)
            H_i = LayerNorm(H_i + FeedForward(H_i))
          end for
          return H_L
        end
        
        Our space complexity is O(n) which matches the standard transformer.
        """
    )
    
    results_section = PaperSection(
        title="Experimental Results",
        content="""
        We evaluated TransformerPlus on multiple benchmarks including GLUE and SQuAD.
        Table 1 shows our results compared to baseline models.
        """
    )
    
    conclusion_section = PaperSection(
        title="Conclusion",
        content="""
        We presented TransformerPlus, a novel transformer architecture with improved
        efficiency and performance. Future work will explore applications to
        multimodal learning.
        """
    )
    
    # Create algorithm
    algorithm = PaperAlgorithm(
        algorithm_id="algo_1",
        name="TransformerPlus",
        description="Enhanced transformer architecture with improved attention mechanism",
        pseudocode="""
        Input: Sequence X of length n, model parameters θ
        Let H₀ = Embedding(X)
        for i = 1 to L do
          A = MultiHeadAttention(H_{i-1})
          B = EfficiencyAttention(H_{i-1})  // Our novel component
          C = Combine(A, B)
          H_i = LayerNorm(H_{i-1} + C)
          H_i = LayerNorm(H_i + FeedForward(H_i))
        end for
        return H_L
        """,
        complexity={"time": "O(n log n)", "space": "O(n)"},
        referenced_by=["Methodology"]
    )
    
    # Create structured paper
    paper = StructuredPaper(
        paper_id="sample_paper_2023",
        title="TransformerPlus: An Enhanced Transformer Architecture for Efficient NLP",
        authors=["Jane Smith", "John Doe"],
        abstract="""
        We present TransformerPlus, an enhanced transformer architecture that improves
        upon the standard transformer model with more efficient attention mechanisms.
        Our approach achieves state-of-the-art results on several NLP benchmarks
        while reducing computational complexity from O(n²) to O(n log n).
        """,
        sections=[intro_section, methods_section, results_section, conclusion_section],
        references=[],
        algorithms=[algorithm],
        keywords=["transformers", "attention mechanism", "efficiency", "NLP"]
    )
    
    return paper


def run_paper_processing_example():
    """Run the complete paper processing and algorithm extraction example."""
    logger.info("Starting paper processing and algorithm extraction example")
    
    # Create a temporary directory for caching
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = os.path.join(temp_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize the paper processor and algorithm extractor
        paper_processor = PaperProcessor(cache_dir=cache_dir)
        algorithm_extractor = AlgorithmExtractor(cache_dir=cache_dir)
        implementation_generator = AlgorithmImplementationGenerator()
        
        # In a real scenario, we would process an actual paper file
        # For this example, we'll use a pre-created sample paper
        logger.info("Creating sample paper")
        paper = create_sample_paper()
        
        logger.info(f"Sample paper created: {paper.title} by {', '.join(paper.authors)}")
        logger.info(f"Abstract: {paper.abstract[:100]}...")
        
        # Extract algorithms from paper
        logger.info("Extracting algorithms from paper")
        algorithms = algorithm_extractor.extract_algorithms(paper)
        
        # Display extracted algorithms
        logger.info(f"Extracted {len(algorithms)} algorithms")
        for i, algorithm in enumerate(algorithms):
            logger.info(f"Algorithm {i+1}: {algorithm.name}")
            logger.info(f"  Description: {algorithm.description[:100]}...")
            logger.info(f"  Complexity: {algorithm.complexity}")
            if algorithm.pseudocode:
                logger.info(f"  Has pseudocode: Yes ({len(algorithm.pseudocode.split('n'))} lines)")
            else:
                logger.info(f"  Has pseudocode: No")
        
        # Generate implementation for each algorithm
        if algorithms:
            logger.info("Generating implementations")
            for i, algorithm in enumerate(algorithms):
                implementation = implementation_generator.generate_implementation(
                    algorithm, language="python", include_comments=True
                )
                
                logger.info(f"Generated implementation for {algorithm.name}")
                logger.info("Implementation preview:")
                
                # Display the first few lines of the implementation
                preview_lines = implementation.split('\n')[:10]
                for line in preview_lines:
                    logger.info(f"  {line}")
                logger.info("  ...")
        
        logger.info("Example completed successfully")


if __name__ == "__main__":
    run_paper_processing_example()