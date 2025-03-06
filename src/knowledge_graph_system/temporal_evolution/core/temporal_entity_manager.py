"""
Temporal Entity Manager for handling version control of entities in the knowledge graph.

This module provides the core functionality for managing temporal entity versions,
including creation, updating, and querying entities across time.
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime, timedelta
import logging
import uuid

from src.knowledge_graph_system.core.db.neo4j_manager import Neo4jManager
from src.knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)
from src.knowledge_graph_system.temporal_evolution.models.temporal_ai_models import (
    TemporalAIModel, TemporalDataset, TemporalAlgorithm,
    EvolvedInto, ReplacedBy, Inspired, MergedWith
)

# Configure logging
logger = logging.getLogger(__name__)


class TemporalEntityManager:
    """
    Manages temporal entities with version control in the knowledge graph.
    
    This class provides functionality for creating, updating, and querying
    temporal entities across time, handling versioning and evolution tracking.
    """
    
    def __init__(self, graph_manager: Optional[Neo4jManager] = None):
        """
        Initialize the Temporal Entity Manager.
        
        Args:
            graph_manager: Neo4j graph manager instance
        """
        self.graph_manager = graph_manager
        
        # Ensure necessary indices and constraints for temporal entities
        if self.graph_manager:
            self._ensure_indices_and_constraints()
    
    def _ensure_indices_and_constraints(self) -> None:
        """Create necessary indices and constraints for temporal entities."""
        # Constraint for unique version IDs
        self.graph_manager.execute_query("""
            CREATE CONSTRAINT temporal_entity_version_id IF NOT EXISTS
            FOR (e:TemporalEntity) REQUIRE e.version_id IS UNIQUE
        """)
        
        # Index for entity_id (stable ID across versions)
        self.graph_manager.execute_query("""
            CREATE INDEX temporal_entity_id IF NOT EXISTS
            FOR (e:TemporalEntity) ON (e.entity_id)
        """)
        
        # Index for temporal querying
        self.graph_manager.execute_query("""
            CREATE INDEX temporal_entity_valid_from IF NOT EXISTS
            FOR (e:TemporalEntity) ON (e.valid_from)
        """)
        
        self.graph_manager.execute_query("""
            CREATE INDEX temporal_entity_valid_to IF NOT EXISTS
            FOR (e:TemporalEntity) ON (e.valid_to)
        """)
        
        # Index for current versions
        self.graph_manager.execute_query("""
            CREATE INDEX temporal_entity_current IF NOT EXISTS
            FOR (e:TemporalEntity) ON (e.is_current)
        """)
        
        # Composite indices
        self.graph_manager.execute_query("""
            CREATE INDEX temporal_entity_composite IF NOT EXISTS
            FOR (e:TemporalEntity) ON (e.entity_id, e.version_number)
        """)
    
    def create_entity(self, entity: TemporalEntityBase) -> TemporalEntityBase:
        """
        Create a new temporal entity.
        
        Args:
            entity: Temporal entity to create
            
        Returns:
            Created temporal entity
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning entity without persistence")
            return entity
        
        # Generate Cypher query for entity creation
        query, params = entity.get_cypher_create()
        
        # Execute the query
        result = self.graph_manager.execute_query(query, params)
        
        if result and result[0] and 'e' in result[0]:
            # Return the created entity
            return entity
        else:
            raise Exception(f"Failed to create temporal entity: {entity.id}")
    
    def get_entity(self, version_id: str) -> Optional[TemporalEntityBase]:
        """
        Get a temporal entity by its version ID.
        
        Args:
            version_id: Version ID of the entity
            
        Returns:
            TemporalEntityBase or None if not found
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning None")
            return None
        
        # Query the entity by version ID
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.version_id = $version_id
        RETURN e
        """
        
        result = self.graph_manager.execute_query(query, {"version_id": version_id})
        
        if result and result[0] and 'e' in result[0]:
            # Convert to appropriate entity type based on labels
            entity_data = result[0]['e']
            return self._create_entity_from_data(entity_data)
        
        return None
    
    def get_entity_at_time(self, entity_id: str, point_in_time: datetime) -> Optional[TemporalEntityBase]:
        """
        Get the version of an entity that was valid at a specific point in time.
        
        Args:
            entity_id: Entity ID (stable across versions)
            point_in_time: Point in time to query
            
        Returns:
            TemporalEntityBase valid at the specified time or None if not found
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning None")
            return None
        
        # Query the entity version valid at the point in time
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.entity_id = $entity_id
        AND e.valid_from <= $point_in_time
        AND (e.valid_to IS NULL OR e.valid_to > $point_in_time)
        RETURN e
        """
        
        result = self.graph_manager.execute_query(query, {
            "entity_id": entity_id,
            "point_in_time": point_in_time.isoformat()
        })
        
        if result and result[0] and 'e' in result[0]:
            # Convert to appropriate entity type based on labels
            entity_data = result[0]['e']
            return self._create_entity_from_data(entity_data)
        
        return None
    
    def get_entity_versions(self, entity_id: str, include_expired: bool = True) -> List[TemporalEntityBase]:
        """
        Get all versions of an entity.
        
        Args:
            entity_id: Entity ID (stable across versions)
            include_expired: Whether to include expired (non-current) versions
            
        Returns:
            List of entity versions sorted by version number
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty list")
            return []
        
        # Query all versions of the entity
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.entity_id = $entity_id
        """
        
        if not include_expired:
            query += " AND e.is_current = true"
        
        query += """
        RETURN e
        ORDER BY e.version_number
        """
        
        result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        versions = []
        for record in result:
            if 'e' in record:
                # Convert to appropriate entity type based on labels
                entity_data = record['e']
                entity = self._create_entity_from_data(entity_data)
                if entity:
                    versions.append(entity)
        
        return versions
    
    def get_current_version(self, entity_id: str) -> Optional[TemporalEntityBase]:
        """
        Get the current version of an entity.
        
        Args:
            entity_id: Entity ID (stable across versions)
            
        Returns:
            Current version of the entity or None if not found
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning None")
            return None
        
        # Query the current version of the entity
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.entity_id = $entity_id AND e.is_current = true
        RETURN e
        """
        
        result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        if result and result[0] and 'e' in result[0]:
            # Convert to appropriate entity type based on labels
            entity_data = result[0]['e']
            return self._create_entity_from_data(entity_data)
        
        return None
    
    def create_new_version(self, 
                          previous_version_id: str, 
                          updated_properties: Dict[str, Any],
                          version_number: Optional[float] = None,
                          valid_from: Optional[datetime] = None) -> Optional[TemporalEntityBase]:
        """
        Create a new version of an existing entity.
        
        Args:
            previous_version_id: Version ID of the previous version
            updated_properties: Properties to update in the new version
            version_number: Version number for the new version (auto-incremented if None)
            valid_from: Timestamp when the new version becomes valid (defaults to now)
            
        Returns:
            New version of the entity or None if previous version not found
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning None")
            return None
        
        # Get the previous version
        previous_version = self.get_entity(previous_version_id)
        if not previous_version:
            logger.error(f"Previous version not found: {previous_version_id}")
            return None
        
        # Use auto-incremented version number if not provided
        if version_number is None:
            version_number = previous_version.version_number + 1.0
            
        # Use current time if valid_from not provided
        if valid_from is None:
            valid_from = datetime.now()
        
        # Create a dictionary representation of the previous version
        entity_dict = previous_version.to_dict()
        
        # Update with new values
        entity_dict.update({
            "id": str(uuid.uuid4()),  # New ID for this version
            "version_id": f"{previous_version.entity_id}_v{version_number}",
            "version_number": version_number,
            "valid_from": valid_from,
            "valid_to": None,
            "predecessor_version_id": previous_version.version_id,
            "successor_version_ids": [],
            "is_current": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        # Apply property updates
        for key, value in updated_properties.items():
            if key not in ["id", "entity_id", "version_id", "version_number", 
                          "valid_from", "valid_to", "predecessor_version_id", 
                          "successor_version_ids", "is_current", "created_at", "updated_at"]:
                entity_dict[key] = value
                
                # Also update properties if it exists
                if "properties" in entity_dict and isinstance(entity_dict["properties"], dict):
                    entity_dict["properties"][key] = value
        
        # Create new version entity from the dictionary
        new_version = self._create_entity_from_dict(entity_dict)
        if not new_version:
            logger.error("Failed to create new version from dictionary")
            return None
        
        # Mark the previous version as deprecated
        updated_previous = self.deprecate_entity_version(
            previous_version.version_id, 
            end_time=valid_from,
            successor_id=new_version.version_id
        )
        
        if not updated_previous:
            logger.warning(f"Failed to mark previous version as deprecated: {previous_version.version_id}")
        
        # Create the new version in the database
        created_version = self.create_entity(new_version)
        
        # Create EVOLVED_INTO relationship between versions
        self._create_evolution_relationship(previous_version, new_version)
        
        return created_version
    
    def deprecate_entity_version(self, 
                                version_id: str, 
                                end_time: Optional[datetime] = None,
                                successor_id: Optional[str] = None) -> Optional[TemporalEntityBase]:
        """
        Mark an entity version as deprecated.
        
        Args:
            version_id: Version ID of the entity to deprecate
            end_time: Timestamp when the version became invalid (defaults to now)
            successor_id: Version ID of the successor (if any)
            
        Returns:
            Updated entity or None if not found
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning None")
            return None
        
        # Set default end time if not provided
        if end_time is None:
            end_time = datetime.now()
        
        # Update the entity in the database
        query = """
        MATCH (e:TemporalEntity {version_id: $version_id})
        SET e.valid_to = $end_time,
            e.is_current = false,
            e.updated_at = $now
        """
        
        params = {
            "version_id": version_id,
            "end_time": end_time.isoformat(),
            "now": datetime.now().isoformat()
        }
        
        # Add successor if provided
        if successor_id:
            query += ", e.successor_version_ids = CASE WHEN e.successor_version_ids IS NULL THEN [$successor_id] ELSE e.successor_version_ids + $successor_id END"
            params["successor_id"] = successor_id
        
        query += " RETURN e"
        
        result = self.graph_manager.execute_query(query, params)
        
        if result and result[0] and 'e' in result[0]:
            # Return the updated entity
            entity_data = result[0]['e']
            return self._create_entity_from_data(entity_data)
        
        return None
    
    def get_version_tree(self, entity_id: str) -> Dict[str, Any]:
        """
        Get the version tree for an entity showing all versions and their relationships.
        
        Args:
            entity_id: Entity ID (stable across versions)
            
        Returns:
            Dictionary representing the version tree
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty tree")
            return {"entity_id": entity_id, "versions": [], "relationships": []}
        
        # Query all versions of the entity
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.entity_id = $entity_id
        RETURN e
        ORDER BY e.version_number
        """
        
        version_result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        versions = []
        for record in version_result:
            if 'e' in record:
                entity_data = record['e']
                versions.append({
                    "version_id": entity_data.get("version_id"),
                    "version_number": entity_data.get("version_number"),
                    "version_name": entity_data.get("version_name"),
                    "valid_from": entity_data.get("valid_from"),
                    "valid_to": entity_data.get("valid_to"),
                    "is_current": entity_data.get("is_current"),
                    "branch_name": entity_data.get("branch_name")
                })
        
        # Query relationships between versions
        query = """
        MATCH (e1:TemporalEntity)-[r]->(e2:TemporalEntity)
        WHERE e1.entity_id = $entity_id AND e2.entity_id = $entity_id
        RETURN e1.version_id as source, e2.version_id as target, type(r) as type, r as properties
        """
        
        rel_result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        relationships = []
        for record in rel_result:
            relationships.append({
                "source": record.get("source"),
                "target": record.get("target"),
                "type": record.get("type"),
                "properties": record.get("properties")
            })
        
        return {
            "entity_id": entity_id,
            "versions": versions,
            "relationships": relationships
        }
    
    def find_entity_at_time(self, 
                           entity_type: str, 
                           properties: Dict[str, Any], 
                           point_in_time: datetime) -> Optional[TemporalEntityBase]:
        """
        Find an entity of a specific type with matching properties at a point in time.
        
        Args:
            entity_type: Type of entity to find
            properties: Properties to match
            point_in_time: Point in time to query
            
        Returns:
            Matching entity or None if not found
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning None")
            return None
        
        # Build the query
        query = f"""
        MATCH (e:{entity_type})
        WHERE e.valid_from <= $point_in_time
        AND (e.valid_to IS NULL OR e.valid_to > $point_in_time)
        """
        
        params = {
            "point_in_time": point_in_time.isoformat()
        }
        
        # Add property conditions
        for i, (key, value) in enumerate(properties.items()):
            param_name = f"prop_{i}"
            query += f" AND e.{key} = ${param_name}"
            params[param_name] = value
        
        query += " RETURN e"
        
        result = self.graph_manager.execute_query(query, params)
        
        if result and result[0] and 'e' in result[0]:
            # Convert to appropriate entity type based on labels
            entity_data = result[0]['e']
            return self._create_entity_from_data(entity_data)
        
        return None
    
    def get_entity_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get the full history of changes for an entity.
        
        Args:
            entity_id: Entity ID (stable across versions)
            
        Returns:
            List of historical events with timestamps
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty history")
            return []
        
        # Get all versions of the entity
        versions = self.get_entity_versions(entity_id)
        
        # Get all relationships between versions
        query = """
        MATCH (e1:TemporalEntity)-[r]->(e2:TemporalEntity)
        WHERE e1.entity_id = $entity_id AND e2.entity_id = $entity_id
        RETURN e1.version_id as source, e2.version_id as target, 
               type(r) as type, r as properties, r.valid_from as timestamp
        """
        
        rel_result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        # Build the history
        history = []
        
        # Add version creation events
        for version in versions:
            history.append({
                "event_type": "VERSION_CREATED",
                "timestamp": version.valid_from,
                "version_id": version.version_id,
                "version_number": version.version_number,
                "changes": {"created": True}
            })
            
            # Add version expiration events if applicable
            if version.valid_to:
                history.append({
                    "event_type": "VERSION_EXPIRED",
                    "timestamp": version.valid_to,
                    "version_id": version.version_id,
                    "version_number": version.version_number,
                    "changes": {"expired": True}
                })
        
        # Add relationship events
        for record in rel_result:
            history.append({
                "event_type": "RELATIONSHIP_CREATED",
                "timestamp": datetime.fromisoformat(record.get("timestamp")) if record.get("timestamp") else None,
                "source_version_id": record.get("source"),
                "target_version_id": record.get("target"),
                "relationship_type": record.get("type"),
                "properties": record.get("properties")
            })
        
        # Sort history by timestamp
        history.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min)
        
        return history
    
    def get_temporal_entities_of_type(self, 
                                     entity_type: str, 
                                     current_only: bool = False,
                                     limit: int = 100) -> List[TemporalEntityBase]:
        """
        Get temporal entities of a specific type.
        
        Args:
            entity_type: Type of entities to retrieve
            current_only: Whether to retrieve only current versions
            limit: Maximum number of entities to retrieve
            
        Returns:
            List of matching entities
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty list")
            return []
        
        # Build the query
        query = f"""
        MATCH (e:{entity_type})
        WHERE e:TemporalEntity
        """
        
        if current_only:
            query += " AND e.is_current = true"
        
        query += f"""
        RETURN e
        LIMIT {limit}
        """
        
        result = self.graph_manager.execute_query(query)
        
        entities = []
        for record in result:
            if 'e' in record:
                # Convert to appropriate entity type based on labels
                entity_data = record['e']
                entity = self._create_entity_from_data(entity_data)
                if entity:
                    entities.append(entity)
        
        return entities
    
    def create_evolutionary_relationship(self,
                                        source_version_id: str,
                                        target_version_id: str,
                                        relationship_type: str,
                                        properties: Dict[str, Any] = None) -> Optional[TemporalRelationshipBase]:
        """
        Create an evolutionary relationship between entity versions.
        
        Args:
            source_version_id: Source version ID
            target_version_id: Target version ID
            relationship_type: Type of relationship (EVOLVED_INTO, REPLACED_BY, etc.)
            properties: Additional properties for the relationship
            
        Returns:
            Created relationship or None if creation failed
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning None")
            return None
        
        # Get the source and target entities
        source = self.get_entity(source_version_id)
        target = self.get_entity(target_version_id)
        
        if not source or not target:
            logger.error(f"Source or target entity not found: {source_version_id}, {target_version_id}")
            return None
        
        # Create the relationship based on the type
        properties = properties or {}
        
        relationship = None
        if relationship_type == "EVOLVED_INTO":
            relationship = EvolvedInto(
                source_id=source.id,
                target_id=target.id,
                **properties
            )
        elif relationship_type == "REPLACED_BY":
            relationship = ReplacedBy(
                source_id=source.id,
                target_id=target.id,
                **properties
            )
        elif relationship_type == "INSPIRED":
            relationship = Inspired(
                source_id=source.id,
                target_id=target.id,
                **properties
            )
        elif relationship_type == "MERGED_WITH":
            relationship = MergedWith(
                source_id=source.id,
                target_id=target.id,
                **properties
            )
        else:
            # Generic temporal relationship
            relationship = TemporalRelationshipBase(
                source_id=source.id,
                target_id=target.id,
                type=relationship_type,
                **properties
            )
        
        # Create the relationship in the database
        query, params = relationship.get_cypher_create()
        
        result = self.graph_manager.execute_query(query, params)
        
        if result and result[0] and 'r' in result[0]:
            return relationship
        
        return None
    
    def _create_evolution_relationship(self, 
                                     source_entity: TemporalEntityBase, 
                                     target_entity: TemporalEntityBase,
                                     evolution_type: str = "gradual") -> Optional[EvolvedInto]:
        """
        Create an EVOLVED_INTO relationship between two entity versions.
        
        Args:
            source_entity: Source entity version
            target_entity: Target entity version
            evolution_type: Type of evolution
            
        Returns:
            Created relationship or None if creation failed
        """
        # Create evolution relationship
        relationship = EvolvedInto(
            source_id=source_entity.id,
            target_id=target_entity.id,
            evolution_type=evolution_type,
            has_breaking_changes=False,
            valid_from=target_entity.valid_from
        )
        
        # Create the relationship in the database
        query, params = relationship.get_cypher_create()
        
        result = self.graph_manager.execute_query(query, params)
        
        if result and result[0] and 'r' in result[0]:
            return relationship
        
        return None
    
    def get_evolution_path(self, entity_id: str) -> Dict[str, Any]:
        """
        Get the complete evolution path for an entity.
        
        Args:
            entity_id: Entity ID (stable across versions)
            
        Returns:
            Dictionary with forward and backward evolution paths
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty paths")
            return {"forward_path": [], "backward_path": []}
        
        # Query the evolution paths
        query = """
        MATCH (e:TemporalEntity {entity_id: $entity_id})
        CALL {
            WITH e
            MATCH path = (e)-[:EVOLVED_INTO*]->(latest)
            WHERE latest.entity_id = $entity_id
            AND NOT (latest)-[:EVOLVED_INTO]->(:TemporalEntity {entity_id: $entity_id})
            RETURN path as forward_path
            UNION
            WITH e
            MATCH path = (earliest)-[:EVOLVED_INTO*]->(e)
            WHERE earliest.entity_id = $entity_id
            AND NOT (:TemporalEntity {entity_id: $entity_id})-[:EVOLVED_INTO]->(earliest)
            RETURN path as backward_path
        }
        RETURN forward_path, backward_path
        """
        
        result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        forward_paths = []
        backward_paths = []
        
        for record in result:
            if 'forward_path' in record and record['forward_path']:
                forward_paths.append(self._extract_path_data(record['forward_path']))
            
            if 'backward_path' in record and record['backward_path']:
                backward_paths.append(self._extract_path_data(record['backward_path']))
        
        return {
            "forward_paths": forward_paths,
            "backward_paths": backward_paths
        }
    
    def _extract_path_data(self, path_data: Any) -> List[Dict[str, Any]]:
        """
        Extract node and relationship data from a path.
        
        Args:
            path_data: Path data from Neo4j
            
        Returns:
            List of nodes and relationships in the path
        """
        path = []
        
        try:
            # Extract nodes and relationships
            nodes = path_data.nodes
            relationships = path_data.relationships
            
            # Add nodes and relationships to the path
            for i, node in enumerate(nodes):
                path.append({
                    "type": "node",
                    "data": dict(node)
                })
                
                if i < len(relationships):
                    path.append({
                        "type": "relationship",
                        "data": dict(relationships[i])
                    })
        except Exception as e:
            logger.error(f"Error extracting path data: {e}")
        
        return path
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """
        Compare two versions of an entity to identify differences.
        
        Args:
            version_id1: First version ID
            version_id2: Second version ID
            
        Returns:
            Dictionary of differences between the versions
        """
        # Get the entities
        entity1 = self.get_entity(version_id1)
        entity2 = self.get_entity(version_id2)
        
        if not entity1 or not entity2:
            logger.error(f"One or both entities not found: {version_id1}, {version_id2}")
            return {
                "error": "One or both entities not found",
                "version_id1": version_id1,
                "version_id2": version_id2
            }
        
        # Check if they are versions of the same entity
        if entity1.entity_id != entity2.entity_id:
            return {
                "error": "Entities are not versions of the same entity",
                "entity_id1": entity1.entity_id,
                "entity_id2": entity2.entity_id
            }
        
        # Compare properties
        added_props = {}
        removed_props = {}
        changed_props = {}
        unchanged_props = {}
        
        # Get all keys from both entities
        all_keys = set(entity1.properties.keys()) | set(entity2.properties.keys())
        
        # Exclude standard temporal keys from comparison
        excluded_keys = {
            "id", "entity_id", "version_id", "version_number", "valid_from", 
            "valid_to", "predecessor_version_id", "successor_version_ids", 
            "branch_name", "is_current", "created_at", "updated_at"
        }
        
        for key in all_keys:
            if key in excluded_keys:
                continue
                
            # Check if property exists in both entities
            if key in entity1.properties and key in entity2.properties:
                if entity1.properties[key] == entity2.properties[key]:
                    unchanged_props[key] = entity1.properties[key]
                else:
                    changed_props[key] = {
                        "old": entity1.properties[key],
                        "new": entity2.properties[key]
                    }
            elif key in entity1.properties:
                removed_props[key] = entity1.properties[key]
            else:
                added_props[key] = entity2.properties[key]
        
        # Determine if this is a minor or major change
        is_major_change = len(changed_props) > 0 or len(added_props) > 0 or len(removed_props) > 0
        
        # Get the evolution relationship if it exists
        evolution_rel = None
        if self.graph_manager:
            query = """
            MATCH (e1:TemporalEntity {version_id: $version_id1})-[r:EVOLVED_INTO]->(e2:TemporalEntity {version_id: $version_id2})
            RETURN r
            """
            
            rel_result = self.graph_manager.execute_query(query, {
                "version_id1": version_id1,
                "version_id2": version_id2
            })
            
            if rel_result and rel_result[0] and 'r' in rel_result[0]:
                evolution_rel = rel_result[0]['r']
        
        return {
            "entity_id": entity1.entity_id,
            "version_id1": version_id1,
            "version_id2": version_id2,
            "version_number1": entity1.version_number,
            "version_number2": entity2.version_number,
            "added_properties": added_props,
            "removed_properties": removed_props,
            "changed_properties": changed_props,
            "unchanged_properties": unchanged_props,
            "is_major_change": is_major_change,
            "evolution_relationship": evolution_rel
        }
    
    def _create_entity_from_data(self, entity_data: Dict[str, Any]) -> Optional[TemporalEntityBase]:
        """
        Create an appropriate entity instance from database data.
        
        Args:
            entity_data: Entity data from the database
            
        Returns:
            Appropriate entity subclass instance
        """
        if not entity_data:
            return None
        
        # Get the entity type from labels
        labels = entity_data.get("labels", [])
        
        # Remove TemporalEntity label for type determination
        if "TemporalEntity" in labels:
            labels.remove("TemporalEntity")
        
        entity_type = labels[0] if labels else None
        
        # Convert to dictionary to pass to from_dict
        entity_dict = dict(entity_data)
        
        return self._create_entity_from_dict(entity_dict, entity_type)
    
    def _create_entity_from_dict(self, entity_dict: Dict[str, Any], entity_type: Optional[str] = None) -> Optional[TemporalEntityBase]:
        """
        Create an appropriate entity instance from a dictionary.
        
        Args:
            entity_dict: Entity data as a dictionary
            entity_type: Optional entity type (determined from labels if None)
            
        Returns:
            Appropriate entity subclass instance
        """
        if not entity_dict:
            return None
        
        # Determine entity type if not provided
        if not entity_type:
            labels = entity_dict.get("labels", [])
            
            # Remove TemporalEntity label for type determination
            if "TemporalEntity" in labels:
                labels.remove("TemporalEntity")
            
            entity_type = labels[0] if labels else None
        
        # Create the appropriate entity type
        if entity_type == "AIModel":
            return TemporalAIModel.from_dict(entity_dict)
        elif entity_type == "Dataset":
            return TemporalDataset.from_dict(entity_dict)
        elif entity_type == "Algorithm":
            return TemporalAlgorithm.from_dict(entity_dict)
        else:
            # Default to base temporal entity
            return TemporalEntityBase.from_dict(entity_dict)