"""
Knowledge Graph Manager for Knowledge Graph System.

This module provides functionality for managing the knowledge graph,
including operations for adding, querying, and updating entities and relationships.
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple
import logging
from datetime import datetime
import uuid
import json

from knowledge_graph_system.core.db.neo4j_manager import Neo4jManager
from knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeGraphManager:
    """
    Manager for knowledge graph operations.
    
    This class provides methods for adding, querying, and updating entities and
    relationships in the knowledge graph.
    """
    
    def __init__(self, db_manager: Neo4jManager):
        """
        Initialize the knowledge graph manager.
        
        Args:
            db_manager: Neo4j database manager
        """
        self.db_manager = db_manager
        self.initialized = False
        
        # Initialize the knowledge graph schema
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Initialize the knowledge graph schema with constraints and indexes."""
        try:
            # Create constraints for unique IDs
            self.db_manager.create_constraints([
                {"name": "entity_id_unique", "label": "Entity", "property": "id"},
            ])
            
            # Create indexes for common properties
            self.db_manager.create_indexes([
                {"name": "entity_name_index", "label": "Entity", "properties": ["name"]},
                {"name": "entity_label_index", "label": "Entity", "properties": ["label"]},
                {"name": "entity_aliases_index", "label": "Entity", "properties": ["aliases"]},
                {"name": "entity_source_index", "label": "Entity", "properties": ["source"]},
            ])
            
            # Mark as initialized
            self.initialized = True
            logger.info("Knowledge graph schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge graph schema: {e}")
            raise
    
    def add_entity(self, entity: GraphEntity) -> Dict[str, Any]:
        """
        Add an entity to the knowledge graph.
        
        Args:
            entity: Entity to add
            
        Returns:
            Dictionary containing the result of the operation
        """
        try:
            # Get Cypher query and parameters
            query, params = entity.get_cypher_create()
            
            # Execute the query
            result = self.db_manager.execute_write_query(query, params)
            
            logger.info(f"Added entity {entity.id} with label {entity.label}")
            
            return {
                "success": True,
                "entity_id": entity.id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to add entity {entity.id}: {e}")
            return {
                "success": False,
                "entity_id": entity.id,
                "error": str(e)
            }
    
    def add_relationship(self, relationship: GraphRelationship) -> Dict[str, Any]:
        """
        Add a relationship to the knowledge graph.
        
        Args:
            relationship: Relationship to add
            
        Returns:
            Dictionary containing the result of the operation
        """
        try:
            # Get Cypher query and parameters
            query, params = relationship.get_cypher_create()
            
            # Execute the query
            result = self.db_manager.execute_write_query(query, params)
            
            # If relationship is bidirectional, create the reverse relationship
            if relationship.bidirectional:
                # Swap source and target
                reverse_relationship = GraphRelationship(
                    id=str(uuid.uuid4()),
                    type=f"REVERSE_{relationship.type}",
                    source_id=relationship.target_id,
                    target_id=relationship.source_id,
                    properties=dict(relationship.properties),
                    confidence=relationship.confidence,
                    source=relationship.source,
                    bidirectional=False  # Prevent infinite loop
                )
                
                # Get Cypher query and parameters for reverse relationship
                reverse_query, reverse_params = reverse_relationship.get_cypher_create()
                
                # Execute the query
                reverse_result = self.db_manager.execute_write_query(reverse_query, reverse_params)
                
                logger.info(f"Added bidirectional relationship {relationship.id} with type {relationship.type}")
            else:
                logger.info(f"Added relationship {relationship.id} with type {relationship.type}")
            
            return {
                "success": True,
                "relationship_id": relationship.id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to add relationship {relationship.id}: {e}")
            return {
                "success": False,
                "relationship_id": relationship.id,
                "error": str(e)
            }
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Dictionary containing entity data, or None if not found
        """
        query = """
        MATCH (e)
        WHERE e.id = $id
        RETURN e
        """
        
        try:
            result = self.db_manager.execute_read_query(query, {"id": entity_id})
            
            if not result:
                logger.warning(f"Entity {entity_id} not found")
                return None
            
            return result[0].get('e')
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            return None
    
    def get_entities_by_label(self, label: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get entities by label.
        
        Args:
            label: Label of the entities
            limit: Maximum number of entities to return
            
        Returns:
            List of dictionaries containing entity data
        """
        query = """
        MATCH (e)
        WHERE $label IN labels(e)
        RETURN e
        LIMIT $limit
        """
        
        try:
            result = self.db_manager.execute_read_query(query, {"label": label, "limit": limit})
            
            return [record.get('e') for record in result]
        except Exception as e:
            logger.error(f"Failed to get entities with label {label}: {e}")
            return []
    
    def get_entities_by_property(self, property_name: str, property_value: Any, 
                               limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get entities by property value.
        
        Args:
            property_name: Name of the property
            property_value: Value of the property
            limit: Maximum number of entities to return
            
        Returns:
            List of dictionaries containing entity data
        """
        query = """
        MATCH (e)
        WHERE e[$property] = $value
        RETURN e
        LIMIT $limit
        """
        
        try:
            result = self.db_manager.execute_read_query(query, {
                "property": property_name, 
                "value": property_value,
                "limit": limit
            })
            
            return [record.get('e') for record in result]
        except Exception as e:
            logger.error(f"Failed to get entities with {property_name} = {property_value}: {e}")
            return []
    
    def get_relationships_by_type(self, relationship_type: str, 
                                limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get relationships by type.
        
        Args:
            relationship_type: Type of the relationships
            limit: Maximum number of relationships to return
            
        Returns:
            List of dictionaries containing relationship data
        """
        query = """
        MATCH ()-[r]->()
        WHERE type(r) = $type
        RETURN r, startNode(r) as source, endNode(r) as target
        LIMIT $limit
        """
        
        try:
            result = self.db_manager.execute_read_query(query, {
                "type": relationship_type,
                "limit": limit
            })
            
            return [
                {
                    "relationship": record.get('r'),
                    "source": record.get('source'),
                    "target": record.get('target')
                }
                for record in result
            ]
        except Exception as e:
            logger.error(f"Failed to get relationships with type {relationship_type}: {e}")
            return []
    
    def get_relationships_for_entity(self, entity_id: str, 
                                   direction: str = "both",
                                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get relationships for an entity.
        
        Args:
            entity_id: ID of the entity
            direction: Direction of relationships ('outgoing', 'incoming', or 'both')
            limit: Maximum number of relationships to return
            
        Returns:
            List of dictionaries containing relationship data
        """
        if direction == "outgoing":
            query = """
            MATCH (e)-[r]->()
            WHERE e.id = $id
            RETURN r, startNode(r) as source, endNode(r) as target
            LIMIT $limit
            """
        elif direction == "incoming":
            query = """
            MATCH (e)<-[r]-()
            WHERE e.id = $id
            RETURN r, startNode(r) as source, endNode(r) as target
            LIMIT $limit
            """
        else:  # both
            query = """
            MATCH (e)-[r]-()
            WHERE e.id = $id
            RETURN r, startNode(r) as source, endNode(r) as target
            LIMIT $limit
            """
        
        try:
            result = self.db_manager.execute_read_query(query, {
                "id": entity_id,
                "limit": limit
            })
            
            return [
                {
                    "relationship": record.get('r'),
                    "source": record.get('source'),
                    "target": record.get('target')
                }
                for record in result
            ]
        except Exception as e:
            logger.error(f"Failed to get relationships for entity {entity_id}: {e}")
            return []
    
    def update_entity(self, entity_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an entity's properties.
        
        Args:
            entity_id: ID of the entity
            properties: Dictionary of properties to update
            
        Returns:
            Dictionary containing the result of the operation
        """
        query = """
        MATCH (e)
        WHERE e.id = $id
        SET e += $properties, e.updated_at = $updated_at
        RETURN e
        """
        
        try:
            result = self.db_manager.execute_write_query(query, {
                "id": entity_id,
                "properties": properties,
                "updated_at": datetime.now().isoformat()
            })
            
            if not result:
                logger.warning(f"Entity {entity_id} not found for update")
                return {
                    "success": False,
                    "entity_id": entity_id,
                    "error": "Entity not found"
                }
            
            logger.info(f"Updated entity {entity_id}")
            
            return {
                "success": True,
                "entity_id": entity_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to update entity {entity_id}: {e}")
            return {
                "success": False,
                "entity_id": entity_id,
                "error": str(e)
            }
    
    def update_relationship(self, relationship_id: str, 
                          properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a relationship's properties.
        
        Args:
            relationship_id: ID of the relationship
            properties: Dictionary of properties to update
            
        Returns:
            Dictionary containing the result of the operation
        """
        query = """
        MATCH ()-[r]->()
        WHERE r.id = $id
        SET r += $properties, r.updated_at = $updated_at
        RETURN r
        """
        
        try:
            result = self.db_manager.execute_write_query(query, {
                "id": relationship_id,
                "properties": properties,
                "updated_at": datetime.now().isoformat()
            })
            
            if not result:
                logger.warning(f"Relationship {relationship_id} not found for update")
                return {
                    "success": False,
                    "relationship_id": relationship_id,
                    "error": "Relationship not found"
                }
            
            logger.info(f"Updated relationship {relationship_id}")
            
            return {
                "success": True,
                "relationship_id": relationship_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to update relationship {relationship_id}: {e}")
            return {
                "success": False,
                "relationship_id": relationship_id,
                "error": str(e)
            }
    
    def delete_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        Delete an entity and its relationships.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Dictionary containing the result of the operation
        """
        query = """
        MATCH (e)
        WHERE e.id = $id
        DETACH DELETE e
        """
        
        try:
            result = self.db_manager.execute_write_query(query, {"id": entity_id})
            
            logger.info(f"Deleted entity {entity_id}")
            
            return {
                "success": True,
                "entity_id": entity_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            return {
                "success": False,
                "entity_id": entity_id,
                "error": str(e)
            }
    
    def delete_relationship(self, relationship_id: str) -> Dict[str, Any]:
        """
        Delete a relationship.
        
        Args:
            relationship_id: ID of the relationship
            
        Returns:
            Dictionary containing the result of the operation
        """
        query = """
        MATCH ()-[r]->()
        WHERE r.id = $id
        DELETE r
        """
        
        try:
            result = self.db_manager.execute_write_query(query, {"id": relationship_id})
            
            logger.info(f"Deleted relationship {relationship_id}")
            
            return {
                "success": True,
                "relationship_id": relationship_id,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to delete relationship {relationship_id}: {e}")
            return {
                "success": False,
                "relationship_id": relationship_id,
                "error": str(e)
            }
    
    def search_entities(self, search_text: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for entities matching the given text.
        
        Args:
            search_text: Text to search for
            limit: Maximum number of entities to return
            
        Returns:
            List of dictionaries containing entity data
        """
        # Prepare search pattern with wildcards
        search_pattern = f"(?i).*{search_text}.*"
        
        query = """
        MATCH (e)
        WHERE e.name =~ $pattern OR
              e.id =~ $pattern OR
              ANY(alias IN e.aliases WHERE alias =~ $pattern)
        RETURN e
        LIMIT $limit
        """
        
        try:
            result = self.db_manager.execute_read_query(query, {
                "pattern": search_pattern,
                "limit": limit
            })
            
            return [record.get('e') for record in result]
        except Exception as e:
            logger.error(f"Failed to search entities with text {search_text}: {e}")
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
        query = """
        MATCH path = (source)-[*1..%d]->(target)
        WHERE source.id = $source_id AND target.id = $target_id
        RETURN path
        LIMIT 10
        """ % max_depth
        
        try:
            result = self.db_manager.run_query(query, {
                "source_id": source_id,
                "target_id": target_id
            })
            
            paths = []
            for record in result:
                path = record["path"]
                path_elements = []
                
                # Extract nodes and relationships from the path
                for i, node in enumerate(path.nodes):
                    path_elements.append({"type": "node", "data": dict(node)})
                    
                    if i < len(path.relationships):
                        path_elements.append({"type": "relationship", "data": dict(path.relationships[i])})
                
                paths.append(path_elements)
            
            return paths
        except Exception as e:
            logger.error(f"Failed to find paths between {source_id} and {target_id}: {e}")
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
            List of dictionaries containing related entity data
        """
        relationship_clause = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            relationship_clause = f":{rel_types}"
        
        label_clause = ""
        if entity_labels:
            label_types = ":".join(entity_labels)
            label_clause = f":{label_types}"
        
        query = f"""
        MATCH (e)-[r{relationship_clause}]-(related{label_clause})
        WHERE e.id = $id
        RETURN related, type(r) as relationship_type, r.id as relationship_id,
               CASE WHEN startNode(r).id = $id THEN 'outgoing' ELSE 'incoming' END as direction
        LIMIT $limit
        """
        
        try:
            result = self.db_manager.execute_read_query(query, {
                "id": entity_id,
                "limit": limit
            })
            
            return [
                {
                    "entity": record.get('related'),
                    "relationship_type": record.get('relationship_type'),
                    "relationship_id": record.get('relationship_id'),
                    "direction": record.get('direction')
                }
                for record in result
            ]
        except Exception as e:
            logger.error(f"Failed to find related entities for {entity_id}: {e}")
            return []
    
    def find_similar_entities(self, entity_id: str, threshold: float = 0.5,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find entities similar to the given entity based on shared properties and relationships.
        
        Args:
            entity_id: ID of the entity
            threshold: Similarity threshold (0.0 to 1.0)
            limit: Maximum number of entities to return
            
        Returns:
            List of dictionaries containing similar entity data with similarity scores
        """
        query = """
        MATCH (e) WHERE e.id = $id
        MATCH (other) WHERE other.id <> $id AND labels(e) = labels(other)
        
        // Compute similarity based on shared properties
        WITH e, other, keys(e) as e_keys, keys(other) as other_keys
        WITH e, other, e_keys, other_keys, 
             [k in e_keys WHERE k in other_keys and e[k] = other[k]] as shared_props
        
        // Only consider entities with some shared properties
        WHERE size(shared_props) > 0
        
        // Compute property similarity
        WITH e, other, e_keys, other_keys, shared_props,
             toFloat(size(shared_props)) / toFloat(size(e_keys) + size(other_keys) - size(shared_props)) as prop_similarity
        
        // Find shared relationships
        OPTIONAL MATCH (e)-[r1]-()
        OPTIONAL MATCH (other)-[r2]-()
        WITH e, other, prop_similarity,
             collect(type(r1) + toString(startNode(r1).id) + toString(endNode(r1).id)) as e_rels,
             collect(type(r2) + toString(startNode(r2).id) + toString(endNode(r2).id)) as other_rels
        
        // Compute relationship similarity
        WITH e, other, prop_similarity, e_rels, other_rels,
             [rel in e_rels WHERE rel in other_rels] as shared_rels
        
        // Compute overall similarity
        WITH e, other, prop_similarity,
             CASE WHEN size(e_rels) + size(other_rels) - size(shared_rels) > 0
               THEN toFloat(size(shared_rels)) / toFloat(size(e_rels) + size(other_rels) - size(shared_rels))
               ELSE 0
             END as rel_similarity
        
        // Combine property and relationship similarity (weighted)
        WITH other, 0.7 * prop_similarity + 0.3 * rel_similarity as similarity
        WHERE similarity >= $threshold
        
        RETURN other, similarity
        ORDER BY similarity DESC
        LIMIT $limit
        """
        
        try:
            result = self.db_manager.execute_read_query(query, {
                "id": entity_id,
                "threshold": threshold,
                "limit": limit
            })
            
            return [
                {
                    "entity": record.get('other'),
                    "similarity": record.get('similarity')
                }
                for record in result
            ]
        except Exception as e:
            logger.error(f"Failed to find similar entities for {entity_id}: {e}")
            return []
    
    def find_contradictions(self) -> List[Dict[str, Any]]:
        """
        Find potential contradictions in the knowledge graph.
        
        Returns:
            List of dictionaries containing contradiction information
        """
        # Find contradicting relationships (A outperforms B, but B outperforms A)
        query = """
        MATCH (a)-[r1:OUTPERFORMS]->(b)-[r2:OUTPERFORMS]->(a)
        RETURN a, b, r1, r2
        """
        
        try:
            result = self.db_manager.execute_read_query(query)
            
            contradictions = []
            for record in result:
                contradictions.append({
                    "type": "contradicting_relationships",
                    "entity1": record.get('a'),
                    "entity2": record.get('b'),
                    "relationship1": record.get('r1'),
                    "relationship2": record.get('r2')
                })
            
            return contradictions
        except Exception as e:
            logger.error(f"Failed to find contradictions: {e}")
            return []
    
    def compute_graph_statistics(self) -> Dict[str, Any]:
        """
        Compute statistics about the knowledge graph.
        
        Returns:
            Dictionary containing graph statistics
        """
        # Get database size
        size_stats = self.db_manager.get_database_size()
        
        # Get schema information
        schema_stats = self.db_manager.get_schema()
        
        # Compute label statistics
        label_query = """
        MATCH (n)
        RETURN labels(n) as labels, count(*) as count
        """
        
        relationship_query = """
        MATCH ()-[r]->()
        RETURN type(r) as type, count(*) as count
        """
        
        try:
            label_result = self.db_manager.execute_read_query(label_query)
            relationship_result = self.db_manager.execute_read_query(relationship_query)
            
            label_stats = {}
            for record in label_result:
                for label in record.get('labels', []):
                    label_stats[label] = record.get('count', 0)
            
            relationship_stats = {}
            for record in relationship_result:
                relationship_stats[record.get('type', '')] = record.get('count', 0)
            
            # Compute overall statistics
            return {
                "size": size_stats,
                "schema": schema_stats,
                "labels": label_stats,
                "relationships": relationship_stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to compute graph statistics: {e}")
            return {
                "size": size_stats,
                "schema": schema_stats,
                "labels": {},
                "relationships": {},
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def batch_add_entities(self, entities: List[GraphEntity]) -> Dict[str, Any]:
        """
        Add multiple entities to the knowledge graph.
        
        Args:
            entities: List of entities to add
            
        Returns:
            Dictionary containing the results of the operations
        """
        results = {
            "success_count": 0,
            "failure_count": 0,
            "failures": []
        }
        
        for entity in entities:
            result = self.add_entity(entity)
            
            if result.get("success", False):
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
                results["failures"].append({
                    "entity_id": entity.id,
                    "error": result.get("error", "Unknown error")
                })
        
        logger.info(f"Batch added {results['success_count']} entities with {results['failure_count']} failures")
        
        return results
    
    def batch_add_relationships(self, relationships: List[GraphRelationship]) -> Dict[str, Any]:
        """
        Add multiple relationships to the knowledge graph.
        
        Args:
            relationships: List of relationships to add
            
        Returns:
            Dictionary containing the results of the operations
        """
        results = {
            "success_count": 0,
            "failure_count": 0,
            "failures": []
        }
        
        for relationship in relationships:
            result = self.add_relationship(relationship)
            
            if result.get("success", False):
                results["success_count"] += 1
            else:
                results["failure_count"] += 1
                results["failures"].append({
                    "relationship_id": relationship.id,
                    "error": result.get("error", "Unknown error")
                })
        
        logger.info(f"Batch added {results['success_count']} relationships with {results['failure_count']} failures")
        
        return results
    
    def close(self):
        """Close the database connection."""
        self.db_manager.close()
        logger.info("Knowledge graph manager closed")