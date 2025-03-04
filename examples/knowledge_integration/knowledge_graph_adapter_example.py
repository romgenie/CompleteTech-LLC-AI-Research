"""
Example demonstrating the usage of the Knowledge Graph Adapter.

This example shows how to use the Knowledge Graph Adapter to integrate
extracted knowledge from research papers into a knowledge graph.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to sys.path to import from modules
project_root = Path(__file__).parents[2]
sys.path.append(str(project_root))

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_integration.knowledge_graph_adapter import KnowledgeGraphAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_entities():
    """Create sample entities for the example."""
    entities = [
        Entity(
            id="gpt4",
            text="GPT-4",
            type=EntityType.AI_MODEL,
            confidence=0.95,
            metadata={
                "organization": "OpenAI",
                "model_type": "language",
                "architecture": "Transformer",
                "parameters": "1.8 trillion"
            }
        ),
        Entity(
            id="claude3",
            text="Claude 3",
            type=EntityType.AI_MODEL,
            confidence=0.92,
            metadata={
                "organization": "Anthropic",
                "model_type": "language",
                "architecture": "Transformer",
                "parameters": "unknown"
            }
        ),
        Entity(
            id="mmlu",
            text="MMLU",
            type=EntityType.BENCHMARK,
            confidence=0.9,
            metadata={
                "domain": "language understanding",
                "description": "Multitask Language Understanding benchmark"
            }
        ),
        Entity(
            id="attention_paper",
            text="Attention Is All You Need",
            type=EntityType.PAPER,
            confidence=0.98,
            metadata={
                "authors": ["Vaswani et al."],
                "year": 2017,
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
            }
        )
    ]
    return entities


def create_sample_relationships(entities):
    """Create sample relationships between entities."""
    # Find entities by ID
    entity_dict = {entity.id: entity for entity in entities}
    
    relationships = [
        Relationship(
            id="gpt4_based_on_transformer",
            source_entity=entity_dict["gpt4"],
            target_entity=entity_dict["attention_paper"],
            relation_type=RelationType.BASED_ON,
            confidence=0.9,
            metadata={}
        ),
        Relationship(
            id="claude3_based_on_transformer",
            source_entity=entity_dict["claude3"],
            target_entity=entity_dict["attention_paper"],
            relation_type=RelationType.BASED_ON,
            confidence=0.85,
            metadata={}
        ),
        Relationship(
            id="gpt4_evaluated_on_mmlu",
            source_entity=entity_dict["gpt4"],
            target_entity=entity_dict["mmlu"],
            relation_type=RelationType.EVALUATED_ON,
            confidence=0.95,
            metadata={
                "metrics": {
                    "accuracy": 0.86
                }
            }
        ),
        Relationship(
            id="claude3_evaluated_on_mmlu",
            source_entity=entity_dict["claude3"],
            target_entity=entity_dict["mmlu"],
            relation_type=RelationType.EVALUATED_ON,
            confidence=0.92,
            metadata={
                "metrics": {
                    "accuracy": 0.85
                }
            }
        ),
        Relationship(
            id="gpt4_outperforms_claude3",
            source_entity=entity_dict["gpt4"],
            target_entity=entity_dict["claude3"],
            relation_type=RelationType.OUTPERFORMS,
            confidence=0.75,
            metadata={
                "metrics": {
                    "mmlu": 0.01
                },
                "margin": "slight"
            }
        )
    ]
    return relationships


def main():
    """Run the Knowledge Graph Adapter example."""
    logger.info("Starting Knowledge Graph Adapter example")
    
    # Create a temporary directory for local storage
    temp_dir = Path(os.path.join(os.getcwd(), "temp_knowledge_store"))
    os.makedirs(temp_dir, exist_ok=True)
    
    # Initialize the Knowledge Graph Adapter with local storage
    adapter = KnowledgeGraphAdapter(local_storage_path=str(temp_dir))
    
    # Create sample entities and relationships
    entities = create_sample_entities()
    relationships = create_sample_relationships(entities)
    
    logger.info(f"Created {len(entities)} sample entities and {len(relationships)} sample relationships")
    
    # Integrate the extracted knowledge
    integration_result = adapter.integrate_extracted_knowledge(entities, relationships)
    
    logger.info("Integration result:")
    for key, value in integration_result.items():
        logger.info(f"  {key}: {value}")
    
    # Query the knowledge graph
    entity_query = {
        "query_type": "entity",
        "filters": {},
        "limit": 10
    }
    
    entity_results = adapter.query_knowledge_graph(entity_query)
    logger.info(f"Found {len(entity_results.get('results', []))} entities in the knowledge graph")
    
    # Get statistics about the knowledge graph
    stats = adapter.get_statistics()
    logger.info("Knowledge graph statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("Example completed successfully")


if __name__ == "__main__":
    main()