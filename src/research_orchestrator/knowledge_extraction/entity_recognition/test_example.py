"""
Example script demonstrating the entity recognition system.

This script can be run directly to test entity recognition on example text.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_entities(entities: List[Entity], title: str = "Recognized Entities") -> None:
    """Print entities in a readable format.
    
    Args:
        entities: List of entities to print
        title: Title for the section
    """
    print(f"\n--- {title} ---")
    if not entities:
        print("No entities found.")
        return
    
    # Group entities by type
    entities_by_type: Dict[EntityType, List[Entity]] = {}
    for entity in entities:
        if entity.type not in entities_by_type:
            entities_by_type[entity.type] = []
        entities_by_type[entity.type].append(entity)
    
    # Print entities by type
    for entity_type, type_entities in sorted(entities_by_type.items(), key=lambda x: str(x[0])):
        print(f"\n{entity_type}:")
        for entity in sorted(type_entities, key=lambda e: e.confidence, reverse=True):
            confidence_str = f"{entity.confidence:.2f}"
            print(f"  - {entity.text} (confidence: {confidence_str})")
            if entity.metadata:
                print(f"    metadata: {entity.metadata}")


def demo_ai_recognition() -> None:
    """Demonstrate AI entity recognition."""
    # Example text with AI concepts
    text = """
    The BERT model introduced by Devlin et al. (2019) significantly improved performance on multiple NLP tasks.
    GPT-3, developed by OpenAI, has 175 billion parameters and can generate human-like text.
    Researchers have trained ResNet-50 on the ImageNet dataset and achieved 76.3% accuracy.
    The Transformer architecture has become fundamental to modern NLP models.
    Using PyTorch and TensorFlow, we implemented a new approach to image classification.
    """
    
    # Create an AI entity recognizer
    recognizer = EntityRecognizerFactory.create_recognizer("ai")
    
    # Recognize entities
    entities = recognizer.recognize(text)
    
    # Print results
    print_entities(entities, "AI Entities")


def demo_scientific_recognition() -> None:
    """Demonstrate scientific entity recognition."""
    # Example text with scientific concepts
    text = """
    In this paper, we propose a novel methodology for graph-based learning.
    Our hypothesis is that attention mechanisms can improve model performance on low-resource tasks.
    The theory of distributed representations has influenced many modern NLP approaches.
    We found that increasing model capacity beyond 10 billion parameters yields diminishing returns.
    Smith and Johnson (2020) demonstrated that pre-training on domain-specific data improves performance.
    A limitation of our approach is the computational requirements for training large models.
    """
    
    # Create a scientific entity recognizer
    recognizer = EntityRecognizerFactory.create_recognizer("scientific")
    
    # Recognize entities
    entities = recognizer.recognize(text)
    
    # Print results
    print_entities(entities, "Scientific Entities")


def demo_combined_recognition() -> None:
    """Demonstrate combined entity recognition."""
    # Example text with both AI and scientific concepts
    text = """
    In this study, we investigate the application of BERT and GPT-3 to scientific text mining.
    Our methodology involves fine-tuning these models on a corpus of academic papers.
    We evaluate performance using precision, recall, and F1-score on the SCIERC dataset.
    The results show that GPT-3 achieved 87.2% accuracy, outperforming BERT by 5.3%.
    Johnson et al. (2021) proposed a similar approach using T5, but with different training objectives.
    A limitation of transformer-based models is their computational complexity, which scales quadratically.
    The concept of attention mechanisms is central to these architectures.
    Using PyTorch, we implemented both models with gradient accumulation to handle limited GPU memory.
    """
    
    # Create a combined entity recognizer
    recognizer = EntityRecognizerFactory.create_default_recognizer()
    
    # Recognize entities
    entities = recognizer.recognize(text)
    
    # Print results
    print_entities(entities, "Combined Entities")


if __name__ == "__main__":
    print("Entity Recognition System Demo")
    print("=============================")
    
    demo_ai_recognition()
    demo_scientific_recognition()
    demo_combined_recognition()
    
    print("\nDemo completed successfully.")