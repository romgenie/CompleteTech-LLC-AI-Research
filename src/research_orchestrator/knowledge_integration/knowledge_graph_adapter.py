"""
Knowledge Graph Adapter for integrating the Knowledge Extraction Pipeline with the Knowledge Graph System.

This module provides the main integration point between the Knowledge Extraction Pipeline
and the Knowledge Graph System, coordinating the conversion, validation, storage, and retrieval
of extracted knowledge.
"""

from typing import Dict, List, Optional, Set, Any, Union, Tuple
import logging
import uuid
from pathlib import Path
import os

from research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from research_orchestrator.knowledge_integration.entity_converter import EntityConverter
from research_orchestrator.knowledge_integration.relationship_converter import RelationshipConverter
from research_orchestrator.knowledge_integration.conflict_resolver import ConflictResolver
from research_orchestrator.knowledge_integration.connection_discovery import ConnectionDiscoveryEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from knowledge_graph_system if available
try:
    from knowledge_graph_system.core.knowledge_graph_manager import KnowledgeGraphManager
    from knowledge_graph_system.core.db.neo4j_manager import Neo4jManager
    from knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship
    
    KNOWLEDGE_GRAPH_AVAILABLE = True
except ImportError:
    KNOWLEDGE_GRAPH_AVAILABLE = False
    logger.warning("Knowledge Graph System not available. Using local storage.")
    
    # Define placeholder classes for type hints
    class GraphEntity:
        pass
    
    class GraphRelationship:
        pass
    
    class KnowledgeGraphManager:
        pass
    
    class Neo4jManager:
        pass


class KnowledgeGraphAdapter:
    """
    Main coordinator for integrating the Knowledge Extraction Pipeline with the Knowledge Graph System.
    
    This adapter handles the conversion, validation, storage, and retrieval of extracted knowledge,
    using the EntityConverter, RelationshipConverter, ConflictResolver, and ConnectionDiscoveryEngine.
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 db_connection_params: Optional[Dict[str, Any]] = None,
                 local_storage_path: Optional[str] = None):
        """
        Initialize the Knowledge Graph Adapter.
        
        Args:
            config_path: Path to configuration file for the Knowledge Graph System
            db_connection_params: Connection parameters for the graph database
            local_storage_path: Path for local storage fallback if Knowledge Graph System is unavailable
        """
        self.entity_converter = EntityConverter()
        self.relationship_converter = RelationshipConverter()
        self.conflict_resolver = ConflictResolver()
        self.connection_discovery = ConnectionDiscoveryEngine()
        
        # Initialize storage backend
        self.kg_manager = None
        self.local_storage_path = local_storage_path or os.path.join(os.getcwd(), "knowledge_store")
        self.using_local_storage = not KNOWLEDGE_GRAPH_AVAILABLE
        
        if KNOWLEDGE_GRAPH_AVAILABLE:
            try:
                # Initialize database connection based on available parameters
                if config_path and os.path.exists(config_path):
                    db_manager = Neo4jManager.from_config(config_path)
                elif db_connection_params:
                    db_manager = Neo4jManager(**db_connection_params)
                else:
                    db_manager = Neo4jManager.from_env()
                
                # Initialize Knowledge Graph Manager
                self.kg_manager = KnowledgeGraphManager(db_manager)
                logger.info("Successfully connected to Knowledge Graph System")
            except Exception as e:
                logger.error(f"Failed to initialize Knowledge Graph System: {e}")
                self.using_local_storage = True
        
        # Initialize local storage if needed
        if self.using_local_storage:
            logger.info(f"Using local storage at: {self.local_storage_path}")
            os.makedirs(self.local_storage_path, exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "entities"), exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "relationships"), exist_ok=True)
            os.makedirs(os.path.join(self.local_storage_path, "connections"), exist_ok=True)
    
    def integrate_extracted_knowledge(self, 
                                      entities: List[Entity], 
                                      relationships: List[Relationship]) -> Dict[str, Any]:
        """
        Integrate extracted knowledge into the knowledge graph.
        
        This method handles the entire integration process:
        1. Convert entities and relationships to knowledge graph format
        2. Detect and resolve conflicts with existing knowledge
        3. Store the validated knowledge in the graph database
        4. Discover non-obvious connections between entities
        5. Return comprehensive results of the integration process
        
        Args:
            entities: List of extracted entities to integrate
            relationships: List of extracted relationships to integrate
            
        Returns:
            Dictionary containing the results of the integration process
        """
        logger.info(f"Integrating {len(entities)} entities and {len(relationships)} relationships")
        
        # 1. Convert entities to knowledge graph format
        converted_entities = []
        for entity in entities:
            converted_entity = self.entity_converter.convert_entity(entity)
            converted_entities.append(converted_entity)
        
        # 2. Convert relationships to knowledge graph format
        converted_relationships = []
        for relationship in relationships:
            converted_relationship = self.relationship_converter.convert_relationship(relationship)
            converted_relationships.append(converted_relationship)
        
        # 3. Detect and resolve conflicts
        entity_conflicts = self.conflict_resolver.detect_entity_conflicts(converted_entities)
        relationship_conflicts = self.conflict_resolver.detect_relationship_conflicts(converted_relationships)
        
        resolved_entities = []
        for entity, conflicts in entity_conflicts.items():
            if conflicts:
                resolved_entity = self.conflict_resolver.resolve_entity_conflict(entity, conflicts)
                resolved_entities.append(resolved_entity)
            else:
                resolved_entities.append(entity)
        
        resolved_relationships = []
        for relationship, conflicts in relationship_conflicts.items():
            if conflicts:
                resolved_relationship = self.conflict_resolver.resolve_relationship_conflict(relationship, conflicts)
                resolved_relationships.append(resolved_relationship)
            else:
                resolved_relationships.append(relationship)
        
        # 4. Store entities and relationships
        entity_results = self._store_entities(resolved_entities)
        relationship_results = self._store_relationships(resolved_relationships)
        
        # 5. Discover connections
        connections = self.connection_discovery.discover_connections(
            resolved_entities, resolved_relationships
        )
        
        # 6. Store discovered connections
        connection_results = self._store_connections(connections)
        
        # 7. Return comprehensive results
        return {
            "integrated_entities": len(entity_results.get("success", [])),
            "failed_entities": entity_results.get("failed", []),
            "integrated_relationships": len(relationship_results.get("success", [])),
            "failed_relationships": relationship_results.get("failed", []),
            "discovered_connections": len(connection_results.get("success", [])),
            "failed_connections": connection_results.get("failed", []),
            "entity_conflicts": len(entity_conflicts),
            "relationship_conflicts": len(relationship_conflicts)
        }
    
    def _store_entities(self, entities: List[Any]) -> Dict[str, List[Any]]:
        """
        Store entities in the knowledge graph or local storage.
        
        Args:
            entities: List of entities to store
            
        Returns:
            Dictionary containing successful and failed entities
        """
        results = {"success": [], "failed": []}
        
        if self.using_local_storage:
            # Store in local storage
            entities_dir = os.path.join(self.local_storage_path, "entities")
            for entity in entities:
                try:
                    entity_id = getattr(entity, "id", str(uuid.uuid4()))
                    entity_file = os.path.join(entities_dir, f"{entity_id}.json")
                    
                    # Convert entity to serializable format
                    entity_data = self._serialize_entity(entity)
                    
                    # Write to file
                    with open(entity_file, 'w') as f:
                        import json
                        json.dump(entity_data, f, indent=2)
                    
                    results["success"].append(entity)
                except Exception as e:
                    logger.error(f"Failed to store entity locally: {e}")
                    results["failed"].append((entity, str(e)))
        else:
            # Store in Knowledge Graph System
            try:
                for entity in entities:
                    try:
                        result = self.kg_manager.add_entity(entity)
                        if result.get("success", False):
                            results["success"].append(entity)
                        else:
                            results["failed"].append((entity, result.get("error", "Unknown error")))
                    except Exception as e:
                        logger.error(f"Failed to add entity to knowledge graph: {e}")
                        results["failed"].append((entity, str(e)))
            except Exception as e:
                logger.error(f"Error storing entities in Knowledge Graph System: {e}")
                results["failed"].extend([(entity, str(e)) for entity in entities])
        
        return results
    
    def _store_relationships(self, relationships: List[Any]) -> Dict[str, List[Any]]:
        """
        Store relationships in the knowledge graph or local storage.
        
        Args:
            relationships: List of relationships to store
            
        Returns:
            Dictionary containing successful and failed relationships
        """
        results = {"success": [], "failed": []}
        
        if self.using_local_storage:
            # Store in local storage
            relationships_dir = os.path.join(self.local_storage_path, "relationships")
            for relationship in relationships:
                try:
                    relationship_id = getattr(relationship, "id", str(uuid.uuid4()))
                    relationship_file = os.path.join(relationships_dir, f"{relationship_id}.json")
                    
                    # Convert relationship to serializable format
                    relationship_data = self._serialize_relationship(relationship)
                    
                    # Write to file
                    with open(relationship_file, 'w') as f:
                        import json
                        json.dump(relationship_data, f, indent=2)
                    
                    results["success"].append(relationship)
                except Exception as e:
                    logger.error(f"Failed to store relationship locally: {e}")
                    results["failed"].append((relationship, str(e)))
        else:
            # Store in Knowledge Graph System
            try:
                for relationship in relationships:
                    try:
                        result = self.kg_manager.add_relationship(relationship)
                        if result.get("success", False):
                            results["success"].append(relationship)
                        else:
                            results["failed"].append((relationship, result.get("error", "Unknown error")))
                    except Exception as e:
                        logger.error(f"Failed to add relationship to knowledge graph: {e}")
                        results["failed"].append((relationship, str(e)))
            except Exception as e:
                logger.error(f"Error storing relationships in Knowledge Graph System: {e}")
                results["failed"].extend([(relationship, str(e)) for relationship in relationships])
        
        return results
    
    def _store_connections(self, connections: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """
        Store discovered connections in the knowledge graph or local storage.
        
        Args:
            connections: List of connections to store
            
        Returns:
            Dictionary containing successful and failed connections
        """
        results = {"success": [], "failed": []}
        
        if self.using_local_storage:
            # Store in local storage
            connections_dir = os.path.join(self.local_storage_path, "connections")
            for connection in connections:
                try:
                    connection_id = connection.get("id", str(uuid.uuid4()))
                    connection_file = os.path.join(connections_dir, f"{connection_id}.json")
                    
                    # Write to file
                    with open(connection_file, 'w') as f:
                        import json
                        json.dump(connection, f, indent=2)
                    
                    results["success"].append(connection)
                except Exception as e:
                    logger.error(f"Failed to store connection locally: {e}")
                    results["failed"].append((connection, str(e)))
        else:
            # Store connections in Knowledge Graph System
            # Note: This may involve creating relationships, entities, or both
            try:
                for connection in connections:
                    try:
                        # Create relationship from connection if it represents a relationship
                        if "source_id" in connection and "target_id" in connection and "type" in connection:
                            relationship = GraphRelationship(
                                id=connection.get("id", str(uuid.uuid4())),
                                type=connection["type"],
                                source_id=connection["source_id"],
                                target_id=connection["target_id"],
                                properties=connection.get("properties", {}),
                                confidence=connection.get("confidence", 0.5),
                                source="connection_discovery_engine"
                            )
                            
                            result = self.kg_manager.add_relationship(relationship)
                            if result.get("success", False):
                                results["success"].append(connection)
                            else:
                                results["failed"].append((connection, result.get("error", "Unknown error")))
                        else:
                            # This is not a standard relationship, store as a connection
                            results["success"].append(connection)
                    except Exception as e:
                        logger.error(f"Failed to add connection to knowledge graph: {e}")
                        results["failed"].append((connection, str(e)))
            except Exception as e:
                logger.error(f"Error storing connections in Knowledge Graph System: {e}")
                results["failed"].extend([(connection, str(e)) for connection in connections])
        
        return results
    
    def query_knowledge_graph(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the knowledge graph for relevant information.
        
        Args:
            query_params: Dictionary containing query parameters
                - query_type: Type of query (entity, relationship, path, etc.)
                - filters: Dictionary of filters to apply
                - limit: Maximum number of results to return
                
        Returns:
            Dictionary containing query results
        """
        query_type = query_params.get("query_type", "entity")
        filters = query_params.get("filters", {})
        limit = query_params.get("limit", 100)
        
        if self.using_local_storage:
            # Query from local storage
            return self._query_local_storage(query_type, filters, limit)
        else:
            # Query from Knowledge Graph System
            try:
                if query_type == "entity":
                    # Entity query
                    results = self.kg_manager.find_entities(filters, limit)
                elif query_type == "relationship":
                    # Relationship query
                    results = self.kg_manager.find_relationships(filters, limit)
                elif query_type == "path":
                    # Path query
                    source_id = filters.get("source_id")
                    target_id = filters.get("target_id")
                    max_depth = filters.get("max_depth", 3)
                    
                    if source_id and target_id:
                        results = self.kg_manager.find_paths(source_id, target_id, max_depth)
                    else:
                        results = {"error": "source_id and target_id are required for path queries"}
                else:
                    results = {"error": f"Unsupported query type: {query_type}"}
                
                return results
            except Exception as e:
                logger.error(f"Error querying Knowledge Graph System: {e}")
                return {"error": str(e)}
    
    def _query_local_storage(self, query_type: str, filters: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """
        Query the local storage for relevant information.
        
        Args:
            query_type: Type of query (entity, relationship, path, etc.)
            filters: Dictionary of filters to apply
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing query results
        """
        results = []
        
        try:
            if query_type == "entity":
                # Entity query
                entities_dir = os.path.join(self.local_storage_path, "entities")
                entity_files = os.listdir(entities_dir)
                
                for entity_file in entity_files[:limit]:
                    with open(os.path.join(entities_dir, entity_file), 'r') as f:
                        import json
                        entity_data = json.load(f)
                        
                        # Apply filters
                        if self._matches_filters(entity_data, filters):
                            results.append(entity_data)
            
            elif query_type == "relationship":
                # Relationship query
                relationships_dir = os.path.join(self.local_storage_path, "relationships")
                relationship_files = os.listdir(relationships_dir)
                
                for relationship_file in relationship_files[:limit]:
                    with open(os.path.join(relationships_dir, relationship_file), 'r') as f:
                        import json
                        relationship_data = json.load(f)
                        
                        # Apply filters
                        if self._matches_filters(relationship_data, filters):
                            results.append(relationship_data)
            
            elif query_type == "connection":
                # Connection query
                connections_dir = os.path.join(self.local_storage_path, "connections")
                connection_files = os.listdir(connections_dir)
                
                for connection_file in connection_files[:limit]:
                    with open(os.path.join(connections_dir, connection_file), 'r') as f:
                        import json
                        connection_data = json.load(f)
                        
                        # Apply filters
                        if self._matches_filters(connection_data, filters):
                            results.append(connection_data)
            
            return {"results": results, "count": len(results)}
        
        except Exception as e:
            logger.error(f"Error querying local storage: {e}")
            return {"error": str(e)}
    
    def _matches_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if the data matches the given filters.
        
        Args:
            data: Dictionary of data to check
            filters: Dictionary of filters to apply
            
        Returns:
            True if the data matches the filters, False otherwise
        """
        for key, value in filters.items():
            # Handle nested filters with dot notation
            if "." in key:
                parts = key.split(".")
                current = data
                for part in parts[:-1]:
                    if part not in current:
                        return False
                    current = current[part]
                
                if parts[-1] not in current or current[parts[-1]] != value:
                    return False
            
            # Handle simple filters
            elif key not in data or data[key] != value:
                return False
        
        return True
    
    def _serialize_entity(self, entity: Any) -> Dict[str, Any]:
        """
        Convert an entity to a serializable format.
        
        Args:
            entity: Entity to serialize
            
        Returns:
            Serializable entity data
        """
        # If this is a GraphEntity from the Knowledge Graph System
        if hasattr(entity, "__dict__"):
            entity_data = {
                "id": getattr(entity, "id", str(uuid.uuid4())),
                "label": getattr(entity, "label", "Entity"),
                "properties": getattr(entity, "properties", {}),
                "confidence": getattr(entity, "confidence", 1.0),
                "source": getattr(entity, "source", "unknown")
            }
        # If this is already a dictionary or similar
        elif hasattr(entity, "items"):
            entity_data = dict(entity)
            if "id" not in entity_data:
                entity_data["id"] = str(uuid.uuid4())
        # If this is something else
        else:
            entity_data = {
                "id": str(uuid.uuid4()),
                "label": "Entity",
                "value": str(entity),
                "confidence": 1.0,
                "source": "unknown"
            }
        
        return entity_data
    
    def _serialize_relationship(self, relationship: Any) -> Dict[str, Any]:
        """
        Convert a relationship to a serializable format.
        
        Args:
            relationship: Relationship to serialize
            
        Returns:
            Serializable relationship data
        """
        # If this is a GraphRelationship from the Knowledge Graph System
        if hasattr(relationship, "__dict__"):
            relationship_data = {
                "id": getattr(relationship, "id", str(uuid.uuid4())),
                "type": getattr(relationship, "type", "RELATED_TO"),
                "source_id": getattr(relationship, "source_id", ""),
                "target_id": getattr(relationship, "target_id", ""),
                "properties": getattr(relationship, "properties", {}),
                "confidence": getattr(relationship, "confidence", 1.0),
                "source": getattr(relationship, "source", "unknown")
            }
        # If this is already a dictionary or similar
        elif hasattr(relationship, "items"):
            relationship_data = dict(relationship)
            if "id" not in relationship_data:
                relationship_data["id"] = str(uuid.uuid4())
        # If this is something else
        else:
            relationship_data = {
                "id": str(uuid.uuid4()),
                "type": "RELATED_TO",
                "source_id": "",
                "target_id": "",
                "value": str(relationship),
                "confidence": 1.0,
                "source": "unknown"
            }
        
        return relationship_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dictionary containing statistics about the knowledge graph
        """
        if self.using_local_storage:
            # Get statistics from local storage
            try:
                entities_dir = os.path.join(self.local_storage_path, "entities")
                relationships_dir = os.path.join(self.local_storage_path, "relationships")
                connections_dir = os.path.join(self.local_storage_path, "connections")
                
                entity_count = len(os.listdir(entities_dir))
                relationship_count = len(os.listdir(relationships_dir))
                connection_count = len(os.listdir(connections_dir))
                
                return {
                    "entity_count": entity_count,
                    "relationship_count": relationship_count,
                    "connection_count": connection_count,
                    "storage_type": "local"
                }
            except Exception as e:
                logger.error(f"Error getting statistics from local storage: {e}")
                return {"error": str(e)}
        else:
            # Get statistics from Knowledge Graph System
            try:
                stats = self.kg_manager.get_statistics()
                return stats
            except Exception as e:
                logger.error(f"Error getting statistics from Knowledge Graph System: {e}")
                return {"error": str(e)}
    
    def clear_knowledge_store(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Clear the knowledge store (for testing or resetting).
        
        Args:
            confirm: Confirmation flag to prevent accidental clearing
            
        Returns:
            Dictionary containing the result of the operation
        """
        if not confirm:
            return {"success": False, "error": "Confirmation required"}
        
        if self.using_local_storage:
            # Clear local storage
            try:
                import shutil
                
                entities_dir = os.path.join(self.local_storage_path, "entities")
                relationships_dir = os.path.join(self.local_storage_path, "relationships")
                connections_dir = os.path.join(self.local_storage_path, "connections")
                
                for directory in [entities_dir, relationships_dir, connections_dir]:
                    for filename in os.listdir(directory):
                        file_path = os.path.join(directory, filename)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                
                return {"success": True, "message": "Local storage cleared"}
            except Exception as e:
                logger.error(f"Error clearing local storage: {e}")
                return {"success": False, "error": str(e)}
        else:
            # Clear Knowledge Graph System
            try:
                result = self.kg_manager.clear()
                return result
            except Exception as e:
                logger.error(f"Error clearing Knowledge Graph System: {e}")
                return {"success": False, "error": str(e)}