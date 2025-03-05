"""
Test script for the knowledge extraction and integration pipeline.
"""

import os
import logging
from pathlib import Path

from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor
from src.research_orchestrator.knowledge_integration.knowledge_graph_adapter import KnowledgeGraphAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pipeline():
    """Run a test of the complete pipeline."""
    logger.info("Starting pipeline test")
    
    # Initialize components
    extractor = KnowledgeExtractor()
    
    # Create a temporary directory for knowledge graph storage
    temp_dir = Path(os.path.join(os.getcwd(), "temp_knowledge_store"))
    os.makedirs(temp_dir, exist_ok=True)
    
    # Initialize knowledge graph adapter with local storage
    adapter = KnowledgeGraphAdapter(local_storage_path=str(temp_dir))
    
    # Extract knowledge from test paper
    test_paper_path = "test_papers/test_paper_content.txt"
    
    # Read the paper content
    with open(test_paper_path, 'r') as f:
        paper_content = f.read()
    
    # Extract entities and relationships
    entities = extractor.extract_entities(paper_content)
    relationships = extractor.extract_relationships(paper_content, entities)
    
    logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
    
    # Integrate knowledge into graph
    integration_result = adapter.integrate_extracted_knowledge(entities, relationships)
    
    logger.info("Integration results:")
    for key, value in integration_result.items():
        logger.info(f"  {key}: {value}")
        
    # Query the knowledge graph
    query = {
        "query_type": "entity",
        "filters": {},
        "limit": 10
    }
    
    query_result = adapter.query_knowledge_graph(query)
    logger.info(f"Found {len(query_result.get('results', []))} entities in knowledge graph")
    
    # Get statistics
    stats = adapter.get_statistics()
    logger.info("Knowledge graph statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
        
    # Look for knowledge gaps
    gaps = adapter.identify_knowledge_gaps()
    if "error" not in gaps:
        logger.info("Identified knowledge gaps:")
        for gap_type, items in gaps.items():
            if gap_type != "research_opportunities":
                logger.info(f"  {gap_type}: {len(items)} items")
        
        if "research_opportunities" in gaps:
            logger.info(f"Generated {len(gaps['research_opportunities'])} research opportunities")
    
    logger.info("Pipeline test completed")

if __name__ == "__main__":
    test_pipeline()