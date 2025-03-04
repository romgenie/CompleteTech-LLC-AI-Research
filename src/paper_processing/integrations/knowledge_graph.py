"""
Knowledge Graph integration for the Paper Processing Pipeline.

This module provides an adapter for integrating the Paper Processing Pipeline
with the Knowledge Graph System. It handles converting paper entities and
relationships to knowledge graph format and managing the graph integration.

Current Implementation Status:
- Adapter interface defined ✓
- Entity conversion methods defined ✓
- Relationship mapping defined ✓

Upcoming Development:
- Complete integration with Neo4j backend
- Batch operations for efficiency
- Citation network construction
- Cross-paper relationship discovery
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import uuid

# Import the Knowledge Graph System interfaces
from knowledge_graph_system.core.knowledge_graph.manager import KnowledgeGraphManager
from knowledge_graph_system.core.models.entity import GraphEntity
from knowledge_graph_system.core.models.relationship import GraphRelationship

# Import the Paper Processing models
from ..models.paper import Paper, Entity, Relationship


logger = logging.getLogger(__name__)


class KnowledgeGraphAdapter:
    """
    Adapter for Knowledge Graph integration.
    
    This class provides methods for integrating papers with the Knowledge Graph
    System, converting entities and relationships, and managing the graph.
    """
    
    def __init__(self, knowledge_graph_manager: KnowledgeGraphManager):
        """
        Initialize the Knowledge Graph adapter.
        
        Args:
            knowledge_graph_manager: Knowledge Graph System manager
        """
        self.kg_manager = knowledge_graph_manager
    
    async def create_paper_node(self, paper: Paper) -> str:
        """
        Create a paper node in the knowledge graph.
        
        Args:
            paper: The paper to create a node for
            
        Returns:
            The ID of the created node
            
        Raises:
            Exception: If node creation fails
        """
        try:
            # Create paper properties
            properties = {
                'title': paper.title,
                'abstract': paper.abstract,
                'year': paper.year,
                'doi': paper.doi,
                'url': paper.url,
                'uploaded_at': paper.uploaded_at.isoformat(),
                'status': paper.status.value
            }
            
            # Add authors as properties
            if paper.authors:
                properties['author_names'] = [author.name for author in paper.authors]
            
            # Create the paper entity
            paper_entity = GraphEntity(
                id=f"paper-{paper.id}",
                type="PAPER",
                properties=properties
            )
            
            # Add the entity to the knowledge graph
            node_id = await self.kg_manager.add_entity(paper_entity)
            logger.info(f"Created paper node {node_id} for paper {paper.id}")
            
            return node_id
        except Exception as e:
            logger.error(f"Failed to create paper node for paper {paper.id}: {e}")
            raise
    
    async def convert_entity(self, paper_id: str, entity: Entity) -> GraphEntity:
        """
        Convert a paper entity to a knowledge graph entity.
        
        Args:
            paper_id: The ID of the paper the entity belongs to
            entity: The entity to convert
            
        Returns:
            The converted graph entity
        """
        # Create a unique ID for the entity
        entity_id = f"{entity.type.lower()}-{uuid.uuid4()}"
        
        # Create the properties
        properties = {
            'name': entity.name,
            'confidence': entity.confidence,
            'source_paper_id': paper_id
        }
        
        # Add context if available
        if entity.context:
            properties['context'] = entity.context
        
        # Add any additional metadata
        if entity.metadata:
            for key, value in entity.metadata.items():
                properties[f"meta_{key}"] = value
        
        # Create the graph entity
        graph_entity = GraphEntity(
            id=entity_id,
            type=entity.type,
            properties=properties
        )
        
        return graph_entity
    
    async def convert_relationship(
        self,
        paper_id: str,
        relationship: Relationship,
        source_id: str,
        target_id: str
    ) -> GraphRelationship:
        """
        Convert a paper relationship to a knowledge graph relationship.
        
        Args:
            paper_id: The ID of the paper the relationship belongs to
            relationship: The relationship to convert
            source_id: The ID of the source entity in the graph
            target_id: The ID of the target entity in the graph
            
        Returns:
            The converted graph relationship
        """
        # Create a unique ID for the relationship
        rel_id = f"{relationship.type.lower()}-{uuid.uuid4()}"
        
        # Create the properties
        properties = {
            'confidence': relationship.confidence,
            'source_paper_id': paper_id
        }
        
        # Add context if available
        if relationship.context:
            properties['context'] = relationship.context
        
        # Add any additional metadata
        if relationship.metadata:
            for key, value in relationship.metadata.items():
                properties[f"meta_{key}"] = value
        
        # Create the graph relationship
        graph_relationship = GraphRelationship(
            id=rel_id,
            type=relationship.type,
            source_id=source_id,
            target_id=target_id,
            properties=properties
        )
        
        return graph_relationship
    
    async def add_paper_to_knowledge_graph(self, paper: Paper) -> Dict[str, Any]:
        """
        Add a paper and its entities/relationships to the knowledge graph.
        
        Args:
            paper: The paper to add
            
        Returns:
            Dict with results of the operation
            
        Raises:
            Exception: If adding to the knowledge graph fails
        """
        try:
            # First, create the paper node
            paper_node_id = await self.create_paper_node(paper)
            
            # Track entity IDs
            entity_id_map = {}
            
            # Add entities
            for entity in paper.entities:
                graph_entity = await self.convert_entity(paper.id, entity)
                entity_id = await self.kg_manager.add_entity(graph_entity)
                entity_id_map[entity.id] = entity_id
                
                # Create relationship to paper
                extracted_from_rel = GraphRelationship(
                    id=f"extracted_from-{uuid.uuid4()}",
                    type="EXTRACTED_FROM",
                    source_id=entity_id,
                    target_id=paper_node_id,
                    properties={
                        'confidence': entity.confidence
                    }
                )
                
                await self.kg_manager.add_relationship(extracted_from_rel)
            
            # Add relationships
            relationship_count = 0
            for relationship in paper.relationships:
                # Skip if source or target not found in map
                if relationship.source_id not in entity_id_map or relationship.target_id not in entity_id_map:
                    logger.warning(f"Skipping relationship {relationship.id} due to missing source or target")
                    continue
                
                source_id = entity_id_map[relationship.source_id]
                target_id = entity_id_map[relationship.target_id]
                
                graph_relationship = await self.convert_relationship(
                    paper.id, relationship, source_id, target_id
                )
                
                await self.kg_manager.add_relationship(graph_relationship)
                relationship_count += 1
            
            result = {
                'paper_node_id': paper_node_id,
                'entity_count': len(entity_id_map),
                'relationship_count': relationship_count,
                'status': 'success'
            }
            
            logger.info(f"Added paper {paper.id} to knowledge graph with {len(entity_id_map)} entities and {relationship_count} relationships")
            
            return result
        except Exception as e:
            logger.error(f"Failed to add paper {paper.id} to knowledge graph: {e}")
            raise


# Note: This is a placeholder for the actual implementation
# The adapter will be initialized with the actual KnowledgeGraphManager instance
kg_adapter = None