"""
Example script demonstrating the relationship extraction system.

This script can be run directly to test relationship extraction on example text.
"""

import logging
import sys
import os
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from src.research_orchestrator.knowledge_extraction.entity_recognition import (
    EntityRecognizerFactory,
    Entity,
    EntityType
)

from src.research_orchestrator.knowledge_extraction.relationship_extraction import (
    RelationshipExtractorFactory,
    Relationship,
    RelationType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_relationships(relationships: List[Relationship], title: str = "Extracted Relationships") -> None:
    """Print relationships in a readable format.
    
    Args:
        relationships: List of relationships to print
        title: Title for the section
    """
    print(f"\n--- {title} ---")
    if not relationships:
        print("No relationships found.")
        return
    
    # Group relationships by type
    relationships_by_type: Dict[RelationType, List[Relationship]] = {}
    for rel in relationships:
        if rel.relation_type not in relationships_by_type:
            relationships_by_type[rel.relation_type] = []
        relationships_by_type[rel.relation_type].append(rel)
    
    # Print relationships by type
    for rel_type, type_rels in sorted(relationships_by_type.items(), key=lambda x: str(x[0])):
        print(f"\n{rel_type}:")
        for rel in sorted(type_rels, key=lambda r: r.confidence, reverse=True):
            confidence_str = f"{rel.confidence:.2f}"
            print(f"  - {rel.source.text} → {rel.target.text} (confidence: {confidence_str})")
            if rel.context:
                print(f"    context: \"{rel.context}\"")
            if rel.metadata:
                print(f"    metadata: {rel.metadata}")


def demo_pattern_extraction() -> None:
    """Demonstrate pattern-based relationship extraction."""
    # Example text with relationships
    text = """
    BERT was trained on the BookCorpus and Wikipedia dataset.
    GPT-3 outperforms previous models on several natural language tasks.
    ResNet-50 achieved 76.3% accuracy on the ImageNet dataset.
    The EfficientNet model is based on the Transformer architecture.
    T5 was implemented in TensorFlow and fine-tuned on multiple datasets.
    """
    
    # First extract entities
    entity_recognizer = EntityRecognizerFactory.create_default_recognizer()
    entities = entity_recognizer.recognize(text)
    
    # Create a pattern relationship extractor
    relationship_extractor = RelationshipExtractorFactory.create_pattern_extractor()
    
    # Extract relationships
    relationships = relationship_extractor.extract_relationships(text, entities)
    
    # Filter to higher confidence relationships
    filtered_relationships = relationship_extractor.filter_relationships(
        relationships, min_confidence=0.8
    )
    
    # Print results
    print_relationships(filtered_relationships, "Pattern-Based Relationships (High Confidence)")


def demo_ai_extraction() -> None:
    """Demonstrate AI-specific relationship extraction."""
    # Example text with AI relationships
    text = """
    BERT was fine-tuned on the SQuAD dataset and achieved state-of-the-art performance.
    GPT-3 has 175 billion parameters and was trained on a diverse corpus of text.
    ResNet-50 reports 92.1% top-5 accuracy on ImageNet classification.
    Using PyTorch, researchers implemented a new vision transformer model that outperforms CNNs.
    The LSTM architecture is particularly effective for sequential data processing.
    """
    
    # First extract entities
    entity_recognizer = EntityRecognizerFactory.create_default_recognizer()
    entities = entity_recognizer.recognize(text)
    
    # Create an AI relationship extractor
    relationship_extractor = RelationshipExtractorFactory.create_ai_extractor()
    
    # Extract relationships
    relationships = relationship_extractor.extract_relationships(text, entities)
    
    # Filter to higher confidence relationships
    filtered_relationships = relationship_extractor.filter_relationships(
        relationships, min_confidence=0.75
    )
    
    # Print results
    print_relationships(filtered_relationships, "AI-Specific Relationships (High Confidence)")


def demo_combined_extraction() -> None:
    """Demonstrate combined relationship extraction."""
    # Example text with both general and AI-specific relationships
    text = """
    BERT was developed by Google and trained on a large corpus of text data. It outperforms traditional NLP models on a variety of tasks.
    
    ResNet-50 achieved 76.3% top-1 accuracy and 93.1% top-5 accuracy on the ImageNet dataset. It was implemented in PyTorch and is widely used for computer vision tasks.
    
    GPT-3 is based on the Transformer architecture and has 175 billion parameters. It was trained on a diverse corpus including books, websites, and scientific papers.
    
    The vision transformer (ViT) model uses a pure transformer approach to image classification and outperforms CNNs while requiring fewer computational resources.
    
    T5 (Text-to-Text Transfer Transformer) treats all NLP tasks as a text-to-text problem and was evaluated on the GLUE benchmark, achieving state-of-the-art results.
    """
    
    # First extract entities
    entity_recognizer = EntityRecognizerFactory.create_default_recognizer()
    entities = entity_recognizer.recognize(text)
    
    # Create a combined relationship extractor
    relationship_extractor = RelationshipExtractorFactory.create_default_extractor()
    
    # Extract relationships
    relationships = relationship_extractor.extract_relationships(text, entities)
    
    # Filter to higher confidence relationships
    filtered_relationships = relationship_extractor.filter_relationships(
        relationships, min_confidence=0.75
    )
    
    # Print results
    print_relationships(filtered_relationships, "Combined Relationships (High Confidence)")
    
    # Print relationship statistics
    stats = relationship_extractor.get_relationship_statistics()
    print("\nRelationship Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Average confidence: {stats['avg_confidence']:.2f}")


if __name__ == "__main__":
    print("Relationship Extraction System Demo")
    print("===================================")
    
    demo_pattern_extraction()
    demo_ai_extraction()
    demo_combined_extraction()
    
    print("\nDemo completed successfully.")