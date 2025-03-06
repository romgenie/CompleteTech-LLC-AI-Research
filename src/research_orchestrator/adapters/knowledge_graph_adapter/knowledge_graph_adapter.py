"""
Knowledge Graph System adapter for the Research Orchestration Framework.

This module provides an adapter for integrating the Knowledge Graph System
with the Research Orchestration Framework, allowing for knowledge storage,
retrieval, and enrichment during the research process.
"""

from typing import Dict, List, Optional, Set, Any, Union
import logging
from pathlib import Path
import json
import os

from src.research_orchestrator.adapters.base_adapter import BaseAdapter
from src.research_orchestrator.knowledge_extraction.entity_recognition.entity_recognizer import Entity
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship_extractor import Relationship

# Import from knowledge_graph_system
try:
    from src.knowledge_graph_system.core.knowledge_graph_manager import KnowledgeGraphManager
    from src.knowledge_graph_system.core.db.neo4j_manager import Neo4jManager
    from src.knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship
    from src.knowledge_graph_system.core.models.ai_models import (
        AIModel, Dataset, Algorithm, Metric, Paper, Task, Benchmark,
        TrainedOn, EvaluatedOn, Outperforms, BasedOn, Cites
    )
    from src.knowledge_graph_system.core.utils.schema_utils import SchemaDefinition
    
    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError:
    KNOWLEDGE_GRAPH_AVAILABLE = False
    # Define placeholder classes for type hints
    class GraphEntity:
        pass
    
    class GraphRelationship:
        pass
    
    class KnowledgeGraphManager:
        pass
    
    class Neo4jManager:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeGraphAdapter(BaseAdapter):
    """
    Adapter for integrating the Knowledge Graph System with the Research Orchestration Framework.
    
    This adapter provides methods for storing, retrieving, and enriching knowledge
    during the research process, using the Knowledge Graph System as a backend.
    """
    
    def __init__(self, config_path: Optional[str] = None,
                neo4j_uri: Optional[str] = None,
                neo4j_username: Optional[str] = None,
                neo4j_password: Optional[str] = None,
                neo4j_database: str = "neo4j"):
        """
        Initialize the Knowledge Graph Adapter.
        
        Args:
            config_path: Path to configuration file (if None, use env vars or params)
            neo4j_uri: Neo4j connection URI (overrides config file)
            neo4j_username: Neo4j username (overrides config file)
            neo4j_password: Neo4j password (overrides config file)
            neo4j_database: Neo4j database name (overrides config file)
        """
        super().__init__("KnowledgeGraphAdapter")
        
        if not KNOWLEDGE_GRAPH_AVAILABLE:
            logger.warning("Knowledge Graph System not available. Adapter will operate in stub mode.")
            self.available = False
            self.kg_manager = None
            return
        
        self.available = True
        self.db_manager = None
        self.kg_manager = None
        
        # Initialize Neo4j connection
        try:
            if config_path and os.path.exists(config_path):
                # Use config file
                self.db_manager = Neo4jManager.from_config(config_path)
            elif neo4j_uri and neo4j_username and neo4j_password:
                # Use provided parameters
                self.db_manager = Neo4jManager(
                    uri=neo4j_uri,
                    username=neo4j_username,
                    password=neo4j_password,
                    database=neo4j_database
                )
            else:
                # Try environment variables
                self.db_manager = Neo4jManager.from_env()
            
            # Initialize knowledge graph manager
            self.kg_manager = KnowledgeGraphManager(self.db_manager)
            
            logger.info("Knowledge Graph Adapter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Graph Adapter: {e}")
            self.available = False
    
    def __del__(self):
        """Clean up resources when the adapter is deleted."""
        if self.available and self.db_manager:
            try:
                self.db_manager.close()
            except Exception as e:
                logger.error(f"Error closing Neo4j connection: {e}")
    
    def is_available(self) -> bool:
        """
        Check if the Knowledge Graph System is available.
        
        Returns:
            True if the Knowledge Graph System is available, False otherwise
        """
        return self.available
    
    def _convert_to_graph_entity(self, entity: Entity) -> GraphEntity:
        """
        Convert an Entity from the Research Orchestration Framework to a GraphEntity.
        
        Args:
            entity: Entity from the Research Orchestration Framework
            
        Returns:
            GraphEntity for the Knowledge Graph System
        """
        # Create a base GraphEntity
        graph_entity = GraphEntity(
            id=entity.id,
            label=entity.type,
            properties={"name": entity.text},
            confidence=entity.confidence,
            source=entity.metadata.get("source", "research_orchestrator")
        )
        
        # Add metadata as properties
        for key, value in entity.metadata.items():
            if key != "source":
                graph_entity.properties[key] = value
        
        return graph_entity
    
    def _convert_to_specific_entity(self, entity: Entity) -> GraphEntity:
        """
        Convert an Entity to a specific GraphEntity type based on its type.
        
        Args:
            entity: Entity from the Research Orchestration Framework
            
        Returns:
            Specific GraphEntity for the Knowledge Graph System
        """
        entity_type = entity.type.lower()
        
        if entity_type == "model" or entity_type == "aimodel":
            return AIModel(
                id=entity.id,
                name=entity.text,
                model_type=entity.metadata.get("model_type", ""),
                organization=entity.metadata.get("organization", ""),
                parameters=entity.metadata.get("parameters", None),
                architecture=entity.metadata.get("architecture", ""),
                confidence=entity.confidence,
                source=entity.metadata.get("source", "research_orchestrator")
            )
        elif entity_type == "dataset":
            return Dataset(
                id=entity.id,
                name=entity.text,
                description=entity.metadata.get("description", ""),
                domain=entity.metadata.get("domain", ""),
                size=entity.metadata.get("size", ""),
                confidence=entity.confidence,
                source=entity.metadata.get("source", "research_orchestrator")
            )
        elif entity_type == "algorithm":
            return Algorithm(
                id=entity.id,
                name=entity.text,
                description=entity.metadata.get("description", ""),
                category=entity.metadata.get("category", ""),
                confidence=entity.confidence,
                source=entity.metadata.get("source", "research_orchestrator")
            )
        elif entity_type == "metric":
            return Metric(
                id=entity.id,
                name=entity.text,
                description=entity.metadata.get("description", ""),
                domain=entity.metadata.get("domain", ""),
                confidence=entity.confidence,
                source=entity.metadata.get("source", "research_orchestrator")
            )
        elif entity_type == "paper":
            return Paper(
                id=entity.id,
                title=entity.text,
                authors=entity.metadata.get("authors", []),
                abstract=entity.metadata.get("abstract", ""),
                year=entity.metadata.get("year", None),
                confidence=entity.confidence,
                source=entity.metadata.get("source", "research_orchestrator")
            )
        else:
            # Default to base GraphEntity
            return self._convert_to_graph_entity(entity)
    
    def _convert_to_graph_relationship(self, relationship: Relationship) -> GraphRelationship:
        """
        Convert a Relationship from the Research Orchestration Framework to a GraphRelationship.
        
        Args:
            relationship: Relationship from the Research Orchestration Framework
            
        Returns:
            GraphRelationship for the Knowledge Graph System
        """
        relationship_type = relationship.relation_type.upper()
        
        # Create the base relationship
        graph_relationship = GraphRelationship(
            id=relationship.id,
            type=relationship_type,
            source_id=relationship.source_entity.id,
            target_id=relationship.target_entity.id,
            properties={},
            confidence=relationship.confidence,
            source=relationship.metadata.get("source", "research_orchestrator")
        )
        
        # Add metadata as properties
        for key, value in relationship.metadata.items():
            if key != "source":
                graph_relationship.properties[key] = value
        
        return graph_relationship
    
    def _convert_to_specific_relationship(self, relationship: Relationship) -> GraphRelationship:
        """
        Convert a Relationship to a specific GraphRelationship type based on its type.
        
        Args:
            relationship: Relationship from the Research Orchestration Framework
            
        Returns:
            Specific GraphRelationship for the Knowledge Graph System
        """
        relation_type = relationship.relation_type.lower()
        
        if relation_type == "trained_on":
            return TrainedOn(
                id=relationship.id,
                source_id=relationship.source_entity.id,
                target_id=relationship.target_entity.id,
                confidence=relationship.confidence,
                source=relationship.metadata.get("source", "research_orchestrator")
            )
        elif relation_type == "evaluated_on":
            metrics = relationship.metadata.get("metrics", {})
            return EvaluatedOn(
                id=relationship.id,
                source_id=relationship.source_entity.id,
                target_id=relationship.target_entity.id,
                metrics=metrics,
                confidence=relationship.confidence,
                source=relationship.metadata.get("source", "research_orchestrator")
            )
        elif relation_type == "outperforms":
            metrics = relationship.metadata.get("metrics", {})
            margin = relationship.metadata.get("margin", None)
            return Outperforms(
                id=relationship.id,
                source_id=relationship.source_entity.id,
                target_id=relationship.target_entity.id,
                metrics=metrics,
                margin=margin,
                confidence=relationship.confidence,
                source=relationship.metadata.get("source", "research_orchestrator")
            )
        elif relation_type == "based_on":
            return BasedOn(
                id=relationship.id,
                source_id=relationship.source_entity.id,
                target_id=relationship.target_entity.id,
                confidence=relationship.confidence,
                source=relationship.metadata.get("source", "research_orchestrator")
            )
        elif relation_type == "cites":
            return Cites(
                id=relationship.id,
                source_id=relationship.source_entity.id,
                target_id=relationship.target_entity.id,
                confidence=relationship.confidence,
                source=relationship.metadata.get("source", "research_orchestrator")
            )
        else:
            # Default to base GraphRelationship
            return self._convert_to_graph_relationship(relationship)
    
    def add_entity(self, entity: Entity) -> Dict[str, Any]:
        """
        Add an entity to the knowledge graph.
        
        Args:
            entity: Entity to add
            
        Returns:
            Dictionary containing the result of the operation
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Entity not added.")
            return {"success": False, "error": "Knowledge Graph System not available"}
        
        try:
            # Convert to a specific entity type if possible
            graph_entity = self._convert_to_specific_entity(entity)
            
            # Add to the knowledge graph
            result = self.kg_manager.add_entity(graph_entity)
            
            return result
        except Exception as e:
            logger.error(f"Error adding entity to knowledge graph: {e}")
            return {"success": False, "error": str(e)}
    
    def add_relationship(self, relationship: Relationship) -> Dict[str, Any]:
        """
        Add a relationship to the knowledge graph.
        
        Args:
            relationship: Relationship to add
            
        Returns:
            Dictionary containing the result of the operation
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Relationship not added.")
            return {"success": False, "error": "Knowledge Graph System not available"}
        
        try:
            # Convert to a specific relationship type if possible
            graph_relationship = self._convert_to_specific_relationship(relationship)
            
            # Add to the knowledge graph
            result = self.kg_manager.add_relationship(graph_relationship)
            
            return result
        except Exception as e:
            logger.error(f"Error adding relationship to knowledge graph: {e}")
            return {"success": False, "error": str(e)}
    
    def add_extracted_knowledge(self, entities: List[Entity], 
                              relationships: List[Relationship]) -> Dict[str, Any]:
        """
        Add extracted knowledge to the knowledge graph.
        
        Args:
            entities: List of entities to add
            relationships: List of relationships to add
            
        Returns:
            Dictionary containing the result of the operation
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Knowledge not added.")
            return {"success": False, "error": "Knowledge Graph System not available"}
        
        try:
            # Convert entities
            graph_entities = [self._convert_to_specific_entity(entity) for entity in entities]
            
            # Add entities to the knowledge graph
            entity_result = self.kg_manager.batch_add_entities(graph_entities)
            
            # Convert relationships
            graph_relationships = [self._convert_to_specific_relationship(rel) for rel in relationships]
            
            # Add relationships to the knowledge graph
            relationship_result = self.kg_manager.batch_add_relationships(graph_relationships)
            
            return {
                "success": True,
                "entity_result": entity_result,
                "relationship_result": relationship_result
            }
        except Exception as e:
            logger.error(f"Error adding extracted knowledge to knowledge graph: {e}")
            return {"success": False, "error": str(e)}
    
    def search_entities(self, search_text: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for entities in the knowledge graph.
        
        Args:
            search_text: Text to search for
            limit: Maximum number of entities to return
            
        Returns:
            List of matching entities
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Search not executed.")
            return []
        
        try:
            results = self.kg_manager.search_entities(search_text, limit)
            return results
        except Exception as e:
            logger.error(f"Error searching entities in knowledge graph: {e}")
            return []
    
    def find_related_entities(self, entity_id: str, 
                            relationship_types: Optional[List[str]] = None,
                            entity_labels: Optional[List[str]] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find entities related to the given entity.
        
        Args:
            entity_id: ID of the entity
            relationship_types: Types of relationships to follow (if None, follow all)
            entity_labels: Labels of entities to return (if None, return all)
            limit: Maximum number of entities to return
            
        Returns:
            List of related entities
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Cannot find related entities.")
            return []
        
        try:
            results = self.kg_manager.find_related_entities(
                entity_id, relationship_types, entity_labels, limit
            )
            return results
        except Exception as e:
            logger.error(f"Error finding related entities in knowledge graph: {e}")
            return []
    
    def find_paths(self, source_id: str, target_id: str, 
                 max_depth: int = 4) -> List[List[Dict[str, Any]]]:
        """
        Find paths between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            max_depth: Maximum path length
            
        Returns:
            List of paths, where each path is a list of dictionaries containing nodes and relationships
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Cannot find paths.")
            return []
        
        try:
            results = self.kg_manager.find_paths(source_id, target_id, max_depth)
            return results
        except Exception as e:
            logger.error(f"Error finding paths in knowledge graph: {e}")
            return []
    
    def find_similar_entities(self, entity_id: str, threshold: float = 0.5,
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find entities similar to the given entity.
        
        Args:
            entity_id: ID of the entity
            threshold: Similarity threshold (0.0 to 1.0)
            limit: Maximum number of entities to return
            
        Returns:
            List of similar entities with similarity scores
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Cannot find similar entities.")
            return []
        
        try:
            results = self.kg_manager.find_similar_entities(entity_id, threshold, limit)
            return results
        except Exception as e:
            logger.error(f"Error finding similar entities in knowledge graph: {e}")
            return []
    
    def enrich_research_context(self, research_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a research context with knowledge from the knowledge graph.
        
        Args:
            research_context: Dictionary containing research context information
            
        Returns:
            Enriched research context
        """
        if not self.available:
            logger.warning("Knowledge Graph System not available. Context not enriched.")
            return research_context
        
        try:
            # Extract key entities from the research context
            key_entities = research_context.get("key_entities", [])
            
            # Find related information in the knowledge graph
            enriched_entities = []
            
            for entity in key_entities:
                entity_id = entity.get("id")
                if entity_id:
                    # Find related entities
                    related = self.find_related_entities(entity_id)
                    
                    # Add related information to the entity
                    entity["related_entities"] = related
                    
                    # Find similar entities
                    similar = self.find_similar_entities(entity_id)
                    
                    # Add similar entities to the entity
                    entity["similar_entities"] = similar
                
                enriched_entities.append(entity)
            
            # Update the research context
            research_context["key_entities"] = enriched_entities
            research_context["knowledge_graph_enriched"] = True
            
            return research_context
        except Exception as e:
            logger.error(f"Error enriching research context: {e}")
            return research_context