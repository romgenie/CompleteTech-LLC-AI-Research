"""
Example script demonstrating the Knowledge Extractor.

This script can be run directly to test the Knowledge Extraction Coordinator.
"""

import logging
import sys
import os
from typing import Dict, Any, List
import tempfile
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
from src.research_orchestrator.knowledge_extraction.entity_recognition import EntityRecognizerFactory
from src.research_orchestrator.knowledge_extraction.relationship_extraction import RelationshipExtractorFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_extraction_results(results: Dict[str, Any], title: str = "Extraction Results") -> None:
    """Print extraction results in a readable format.
    
    Args:
        results: Extraction results dictionary
        title: Title for the results section
    """
    print(f"\n--- {title} ---")
    
    print(f"Document ID: {results.get('document_id', 'Unknown')}")
    print(f"Document Type: {results.get('document_type', 'Unknown')}")
    print(f"Extraction Time: {results.get('extraction_time', 0):.2f} seconds")
    
    print("\nEntity Information:")
    print(f"  Total Entities: {results.get('entity_count', 0)}")
    print("  Entity Types:")
    for entity_type, count in results.get('entity_types', {}).items():
        print(f"    - {entity_type}: {count}")
    
    print("\nRelationship Information:")
    print(f"  Total Relationships: {results.get('relationship_count', 0)}")
    print("  Relationship Types:")
    for rel_type, count in results.get('relationship_types', {}).items():
        print(f"    - {rel_type}: {count}")
    
    print("\nConfidence Scores:")
    confidence = results.get('confidence', {})
    print(f"  Average Entity Confidence: {confidence.get('entity_avg', 0):.2f}")
    print(f"  Average Relationship Confidence: {confidence.get('relationship_avg', 0):.2f}")


def demo_text_extraction() -> None:
    """Demonstrate knowledge extraction from text."""
    # Example AI research paper abstract
    text = """
    Recent advances in large language models (LLMs) have demonstrated impressive capabilities across a wide range of tasks. In this paper, we introduce GPT-4, which improves upon previous models like GPT-3 and ChatGPT by incorporating more training data and an enhanced model architecture. GPT-4 was trained on a diverse corpus of text and code, enabling it to handle complex reasoning tasks and generate more coherent responses.
    
    We evaluate GPT-4 on various benchmarks, including MMLU, HumanEval, and GSM8K. Results show that GPT-4 outperforms previous models, achieving 86.4% on MMLU (compared to ChatGPT's 70.0%) and 92.0% on HumanEval (compared to GPT-3's 48.1%). The model shows particular strength in reasoning tasks and demonstrates emergent capabilities not present in smaller models.
    
    The architecture builds upon the transformer design but incorporates several modifications, including an improved attention mechanism and more efficient parameter utilization. We implement the model using PyTorch and fine-tune it using reinforcement learning from human feedback (RLHF).
    
    Our findings indicate that scaling up model size and training data continues to yield performance improvements, though with diminishing returns compared to previous generations. We also discuss ethical considerations and limitations of the model, including potential biases in the training data and the environmental impact of training such large models.
    """
    
    # Create entity and relationship extractors
    entity_recognizer = EntityRecognizerFactory.create_default_recognizer()
    relationship_extractor = RelationshipExtractorFactory.create_default_extractor()
    
    # Create a knowledge extractor with the explicit extractors
    extractor = KnowledgeExtractor(
        entity_recognizer=entity_recognizer,
        relationship_extractor=relationship_extractor
    )
    
    # Extract knowledge from the text
    results = extractor.extract_from_text(text, document_id="gpt4_abstract")
    
    # Print the results
    print_extraction_results(results, "Text Extraction Results")
    
    # Save extraction results to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = extractor.save_extraction_results(temp_dir)
        print(f"\nSaved extraction results to {output_dir}")
        
        # Summarize the knowledge graph
        graph_path = os.path.join(output_dir, "gpt4_abstract", "knowledge_graph.json")
        if os.path.exists(graph_path):
            with open(graph_path, 'r') as f:
                graph = json.load(f)
                print("\nKnowledge Graph Summary:")
                print(f"  Nodes: {len(graph.get('nodes', {}))} | Edges: {len(graph.get('edges', {}))}")
        
        # Query the knowledge graph
        print("\nPerforming queries on the knowledge graph:")
        
        # Query for GPT-4 performance
        gpt4_query = {
            "type": "entity",
            "entity_type": "model",
            "keywords": ["GPT-4"]
        }
        gpt4_results = extractor.query_knowledge_graph(gpt4_query)
        print(f"  Found {len(gpt4_results)} entities related to GPT-4")
        
        # Query for performance metrics
        metrics_query = {
            "type": "relationship",
            "relation_type": "achieves",
            "min_confidence": 0.7
        }
        metrics_results = extractor.query_knowledge_graph(metrics_query)
        print(f"  Found {len(metrics_results)} performance metric relationships")
        
        # Print a few example relationships
        if metrics_results:
            print("\nExample Performance Metrics:")
            for i, result in enumerate(metrics_results[:3]):
                rel = result["relationship"]
                src = result["source"]["label"]
                tgt = result["target"]["label"]
                print(f"  {i+1}. {src} → {rel['type']} → {tgt} (conf: {rel['confidence']:.2f})")
                if "metadata" in rel and "value" in rel["metadata"]:
                    print(f"     Value: {rel['metadata']['value']}")


def demo_document_directory() -> None:
    """Demonstrate knowledge extraction from a directory of documents."""
    # We'll use a temporary directory as an example
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a sample text document
        sample_doc_path = os.path.join(temp_dir, "sample.txt")
        with open(sample_doc_path, 'w') as f:
            f.write("""
                The Vision Transformer (ViT) model applies the transformer architecture to image classification tasks.
                It was developed by researchers at Google Brain and achieves 88.55% accuracy on the ImageNet dataset.
                The model is implemented in TensorFlow and significantly outperforms conventional CNN-based approaches.
                
                Recent improvements to ViT include hierarchical structures and improved token mixing, which further
                enhance performance on various computer vision benchmarks.
                """)
        
        # Create entity and relationship extractors
        entity_recognizer = EntityRecognizerFactory.create_default_recognizer()
        relationship_extractor = RelationshipExtractorFactory.create_default_extractor()
        
        # Create a knowledge extractor with the explicit extractors
        extractor = KnowledgeExtractor(
            entity_recognizer=entity_recognizer,
            relationship_extractor=relationship_extractor
        )
        
        # Extract knowledge from all documents in the directory
        results = extractor.extract_from_directory(temp_dir)
        
        # Print results for each document
        for doc_id, extraction_results in results.items():
            print_extraction_results(extraction_results, f"Document Extraction Results: {doc_id}")
        
        # Get overall statistics
        stats = extractor.get_extraction_statistics()
        print("\nOverall Extraction Statistics:")
        print(f"  Documents Processed: {stats.get('documents', {}).get('count', 0)}")
        print(f"  Total Entities: {stats.get('entities', {}).get('count', 0)}")
        print(f"  Total Relationships: {stats.get('relationships', {}).get('count', 0)}")
        print(f"  Total Knowledge Graph Nodes: {stats.get('knowledge_graph', {}).get('total_nodes', 0)}")
        print(f"  Total Knowledge Graph Edges: {stats.get('knowledge_graph', {}).get('total_edges', 0)}")


if __name__ == "__main__":
    print("Knowledge Extractor Demo")
    print("=======================")
    
    print("\nDemo 1: Knowledge Extraction from Text")
    print("-------------------------------------")
    demo_text_extraction()
    
    print("\n\nDemo 2: Knowledge Extraction from Document Directory")
    print("--------------------------------------------------")
    demo_document_directory()
    
    print("\nDemo completed successfully.")