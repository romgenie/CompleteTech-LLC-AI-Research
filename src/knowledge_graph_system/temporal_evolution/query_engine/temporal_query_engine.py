"""
Temporal Query Engine for time-based queries on the knowledge graph.

This module provides functionality for querying the knowledge graph at different
points in time, finding temporal paths, and generating temporal snapshots.
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime, timedelta
import logging
import uuid
import json

from src.knowledge_graph_system.core.db.neo4j_manager import Neo4jManager
from src.knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)

# Configure logging
logger = logging.getLogger(__name__)


class TemporalQueryEngine:
    """
    Engine for executing temporal queries on the knowledge graph.
    
    This class provides functionality for time-based queries, including point-in-time
    snapshots, time window queries, and temporal path finding.
    """
    
    def __init__(self, graph_manager: Optional[Neo4jManager] = None):
        """
        Initialize the Temporal Query Engine.
        
        Args:
            graph_manager: Neo4j graph manager instance
        """
        self.graph_manager = graph_manager
    
    def query_entities_at_time(self, 
                              entity_type: str, 
                              point_in_time: datetime,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query entities of a specific type at a point in time.
        
        Args:
            entity_type: Type of entities to query
            point_in_time: Point in time to query
            limit: Maximum number of entities to return
            
        Returns:
            List of entities valid at the specified time
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty list")
            return []
        
        # Build the query
        query = f"""
        MATCH (e:{entity_type})
        WHERE e:TemporalEntity
        AND e.valid_from <= $point_in_time
        AND (e.valid_to IS NULL OR e.valid_to > $point_in_time)
        RETURN e
        LIMIT {limit}
        """
        
        params = {
            "point_in_time": point_in_time.isoformat()
        }
        
        result = self.graph_manager.execute_query(query, params)
        
        entities = []
        for record in result:
            if 'e' in record:
                entity_data = record['e']
                entities.append(dict(entity_data))
        
        return entities
    
    def query_relationships_at_time(self,
                                   relationship_type: Optional[str],
                                   point_in_time: datetime,
                                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query relationships at a point in time.
        
        Args:
            relationship_type: Type of relationships to query (or None for all)
            point_in_time: Point in time to query
            limit: Maximum number of relationships to return
            
        Returns:
            List of relationships valid at the specified time
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty list")
            return []
        
        # Build the query
        query = """
        MATCH (src)-[r]->(tgt)
        WHERE r.valid_from <= $point_in_time
        AND (r.valid_to IS NULL OR r.valid_to > $point_in_time)
        """
        
        # Add relationship type filter if provided
        if relationship_type:
            query = f"""
            MATCH (src)-[r:{relationship_type}]->(tgt)
            WHERE r.valid_from <= $point_in_time
            AND (r.valid_to IS NULL OR r.valid_to > $point_in_time)
            """
        
        query += f"""
        RETURN src.id as source_id, tgt.id as target_id, type(r) as type, r as properties
        LIMIT {limit}
        """
        
        params = {
            "point_in_time": point_in_time.isoformat()
        }
        
        result = self.graph_manager.execute_query(query, params)
        
        relationships = []
        for record in result:
            rel = {
                "source_id": record.get("source_id"),
                "target_id": record.get("target_id"),
                "type": record.get("type"),
                "properties": dict(record.get("properties", {}))
            }
            relationships.append(rel)
        
        return relationships
    
    def get_knowledge_graph_snapshot(self,
                                   point_in_time: datetime,
                                   entity_types: Optional[List[str]] = None,
                                   relationship_types: Optional[List[str]] = None,
                                   include_inactive: bool = False) -> Dict[str, Any]:
        """
        Get a snapshot of the knowledge graph at a specific point in time.
        
        Args:
            point_in_time: Point in time for the snapshot
            entity_types: Types of entities to include (or None for all)
            relationship_types: Types of relationships to include (or None for all)
            include_inactive: Whether to include inactive entities and relationships
            
        Returns:
            Dictionary with entities and relationships in the snapshot
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty snapshot")
            return {"entities": [], "relationships": []}
        
        # Build entity query
        entity_query = """
        MATCH (e)
        WHERE e:TemporalEntity
        """
        
        if not include_inactive:
            entity_query += """
            AND e.valid_from <= $point_in_time
            AND (e.valid_to IS NULL OR e.valid_to > $point_in_time)
            """
        
        # Add entity type filter if provided
        if entity_types:
            type_conditions = []
            for entity_type in entity_types:
                type_conditions.append(f"e:{entity_type}")
            
            if type_conditions:
                entity_query += " AND (" + " OR ".join(type_conditions) + ")"
        
        entity_query += """
        RETURN e
        """
        
        # Build relationship query
        rel_query = """
        MATCH (src)-[r]->(tgt)
        WHERE src:TemporalEntity AND tgt:TemporalEntity
        """
        
        if not include_inactive:
            rel_query += """
            AND r.valid_from <= $point_in_time
            AND (r.valid_to IS NULL OR r.valid_to > $point_in_time)
            AND src.valid_from <= $point_in_time
            AND (src.valid_to IS NULL OR src.valid_to > $point_in_time)
            AND tgt.valid_from <= $point_in_time
            AND (tgt.valid_to IS NULL OR tgt.valid_to > $point_in_time)
            """
        
        # Add relationship type filter if provided
        if relationship_types:
            type_conditions = []
            for rel_type in relationship_types:
                type_conditions.append(f"type(r) = '{rel_type}'")
            
            if type_conditions:
                rel_query += " AND (" + " OR ".join(type_conditions) + ")"
        
        rel_query += """
        RETURN src.id as source_id, tgt.id as target_id, type(r) as type, r as properties
        """
        
        params = {
            "point_in_time": point_in_time.isoformat()
        }
        
        # Execute entity query
        entity_result = self.graph_manager.execute_query(entity_query, params)
        
        entities = []
        for record in entity_result:
            if 'e' in record:
                entity_data = record['e']
                entities.append(dict(entity_data))
        
        # Execute relationship query
        rel_result = self.graph_manager.execute_query(rel_query, params)
        
        relationships = []
        for record in rel_result:
            rel = {
                "source_id": record.get("source_id"),
                "target_id": record.get("target_id"),
                "type": record.get("type"),
                "properties": dict(record.get("properties", {}))
            }
            relationships.append(rel)
        
        return {
            "timestamp": point_in_time.isoformat(),
            "entities": entities,
            "relationships": relationships
        }
    
    def compare_snapshots(self,
                        first_time: datetime,
                        second_time: datetime,
                        entity_types: Optional[List[str]] = None,
                        relationship_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare knowledge graph snapshots at two points in time.
        
        Args:
            first_time: First point in time
            second_time: Second point in time
            entity_types: Types of entities to include (or None for all)
            relationship_types: Types of relationships to include (or None for all)
            
        Returns:
            Dictionary with differences between the snapshots
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty comparison")
            return {"differences": {}}
        
        # Get snapshots at both points in time
        first_snapshot = self.get_knowledge_graph_snapshot(
            point_in_time=first_time,
            entity_types=entity_types,
            relationship_types=relationship_types
        )
        
        second_snapshot = self.get_knowledge_graph_snapshot(
            point_in_time=second_time,
            entity_types=entity_types,
            relationship_types=relationship_types
        )
        
        # Analyze entities
        first_entities = {e.get("id"): e for e in first_snapshot["entities"]}
        second_entities = {e.get("id"): e for e in second_snapshot["entities"]}
        
        # Find added, removed, and changed entities
        added_entities = []
        for entity_id, entity in second_entities.items():
            if entity_id not in first_entities:
                added_entities.append(entity)
        
        removed_entities = []
        for entity_id, entity in first_entities.items():
            if entity_id not in second_entities:
                removed_entities.append(entity)
        
        changed_entities = []
        for entity_id, entity in second_entities.items():
            if entity_id in first_entities:
                # Compare properties
                first_entity = first_entities[entity_id]
                changes = self._compare_properties(first_entity, entity)
                if changes["added"] or changes["removed"] or changes["changed"]:
                    changed_entities.append({
                        "entity_id": entity_id,
                        "changes": changes
                    })
        
        # Analyze relationships
        first_rels = {self._rel_key(r): r for r in first_snapshot["relationships"]}
        second_rels = {self._rel_key(r): r for r in second_snapshot["relationships"]}
        
        # Find added, removed, and changed relationships
        added_relationships = []
        for rel_key, rel in second_rels.items():
            if rel_key not in first_rels:
                added_relationships.append(rel)
        
        removed_relationships = []
        for rel_key, rel in first_rels.items():
            if rel_key not in second_rels:
                removed_relationships.append(rel)
        
        changed_relationships = []
        for rel_key, rel in second_rels.items():
            if rel_key in first_rels:
                # Compare properties
                first_rel = first_rels[rel_key]
                changes = self._compare_properties(
                    first_rel.get("properties", {}),
                    rel.get("properties", {})
                )
                if changes["added"] or changes["removed"] or changes["changed"]:
                    changed_relationships.append({
                        "source_id": rel.get("source_id"),
                        "target_id": rel.get("target_id"),
                        "type": rel.get("type"),
                        "changes": changes
                    })
        
        # Calculate statistics
        stats = {
            "entity_count_change": len(second_snapshot["entities"]) - len(first_snapshot["entities"]),
            "relationship_count_change": len(second_snapshot["relationships"]) - len(first_snapshot["relationships"]),
            "added_entities_count": len(added_entities),
            "removed_entities_count": len(removed_entities),
            "changed_entities_count": len(changed_entities),
            "added_relationships_count": len(added_relationships),
            "removed_relationships_count": len(removed_relationships),
            "changed_relationships_count": len(changed_relationships)
        }
        
        return {
            "first_time": first_time.isoformat(),
            "second_time": second_time.isoformat(),
            "statistics": stats,
            "differences": {
                "added_entities": added_entities,
                "removed_entities": removed_entities,
                "changed_entities": changed_entities,
                "added_relationships": added_relationships,
                "removed_relationships": removed_relationships,
                "changed_relationships": changed_relationships
            }
        }
    
    def _rel_key(self, rel: Dict[str, Any]) -> str:
        """
        Generate a unique key for a relationship.
        
        Args:
            rel: Relationship data
            
        Returns:
            Unique key for the relationship
        """
        return f"{rel.get('source_id')}|{rel.get('type')}|{rel.get('target_id')}"
    
    def _compare_properties(self, first: Dict[str, Any], second: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare properties between two dictionaries.
        
        Args:
            first: First dictionary
            second: Second dictionary
            
        Returns:
            Dictionary with added, removed, and changed properties
        """
        added = {}
        removed = {}
        changed = {}
        
        # Find added properties
        for key, value in second.items():
            if key not in first:
                added[key] = value
        
        # Find removed properties
        for key, value in first.items():
            if key not in second:
                removed[key] = value
        
        # Find changed properties
        for key, value in second.items():
            if key in first and first[key] != value:
                changed[key] = {
                    "old": first[key],
                    "new": value
                }
        
        return {
            "added": added,
            "removed": removed,
            "changed": changed
        }
    
    def find_temporal_path(self,
                          start_entity_id: str,
                          end_entity_id: str,
                          max_hops: int = 5,
                          include_indirect: bool = True) -> List[Dict[str, Any]]:
        """
        Find temporal paths between two entities, including evolution steps.
        
        Args:
            start_entity_id: ID of the start entity
            end_entity_id: ID of the end entity
            max_hops: Maximum number of hops in the path
            include_indirect: Whether to include indirect paths through version relationships
            
        Returns:
            List of paths between the entities
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty paths")
            return []
        
        # First, check if these are version IDs or entity IDs
        start_is_version = self._is_version_id(start_entity_id)
        end_is_version = self._is_version_id(end_entity_id)
        
        paths = []
        
        # Case 1: Direct path between specific versions
        if start_is_version and end_is_version:
            direct_paths = self._find_direct_paths(start_entity_id, end_entity_id, max_hops)
            paths.extend(direct_paths)
        
        # Case 2: Paths between any versions of the entities
        elif include_indirect:
            if start_is_version:
                # Get the stable entity ID for the start version
                start_stable_id = self._get_stable_entity_id(start_entity_id)
                if not start_stable_id:
                    logger.error(f"Could not find stable entity ID for version: {start_entity_id}")
                    return []
            else:
                start_stable_id = start_entity_id
            
            if end_is_version:
                # Get the stable entity ID for the end version
                end_stable_id = self._get_stable_entity_id(end_entity_id)
                if not end_stable_id:
                    logger.error(f"Could not find stable entity ID for version: {end_entity_id}")
                    return []
            else:
                end_stable_id = end_entity_id
            
            # Find paths between all versions of the entities
            version_paths = self._find_paths_between_entity_versions(
                start_stable_id, end_stable_id, max_hops
            )
            paths.extend(version_paths)
        
        # Case 3: Direct path from specific start version to any version of end entity
        elif start_is_version and not end_is_version:
            end_versions = self._get_entity_versions(end_entity_id)
            for end_version in end_versions:
                end_version_id = end_version.get("version_id")
                if end_version_id:
                    direct_paths = self._find_direct_paths(start_entity_id, end_version_id, max_hops)
                    paths.extend(direct_paths)
        
        # Case 4: Direct path from any version of start entity to specific end version
        elif not start_is_version and end_is_version:
            start_versions = self._get_entity_versions(start_entity_id)
            for start_version in start_versions:
                start_version_id = start_version.get("version_id")
                if start_version_id:
                    direct_paths = self._find_direct_paths(start_version_id, end_entity_id, max_hops)
                    paths.extend(direct_paths)
        
        return paths
    
    def _is_version_id(self, entity_id: str) -> bool:
        """
        Check if an ID is a version ID or a stable entity ID.
        
        Args:
            entity_id: ID to check
            
        Returns:
            True if the ID is a version ID, False otherwise
        """
        if not self.graph_manager:
            return False
        
        # Query if this is a version ID
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.version_id = $entity_id
        RETURN count(e) > 0 AS is_version
        """
        
        result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        if result and result[0] and 'is_version' in result[0]:
            return result[0]['is_version']
        
        return False
    
    def _get_stable_entity_id(self, version_id: str) -> Optional[str]:
        """
        Get the stable entity ID for a version ID.
        
        Args:
            version_id: Version ID
            
        Returns:
            Stable entity ID or None if not found
        """
        if not self.graph_manager:
            return None
        
        # Query the stable entity ID
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.version_id = $version_id
        RETURN e.entity_id AS entity_id
        """
        
        result = self.graph_manager.execute_query(query, {"version_id": version_id})
        
        if result and result[0] and 'entity_id' in result[0]:
            return result[0]['entity_id']
        
        return None
    
    def _get_entity_versions(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of an entity.
        
        Args:
            entity_id: Stable entity ID
            
        Returns:
            List of entity versions
        """
        if not self.graph_manager:
            return []
        
        # Query all versions of the entity
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.entity_id = $entity_id
        RETURN e
        """
        
        result = self.graph_manager.execute_query(query, {"entity_id": entity_id})
        
        versions = []
        for record in result:
            if 'e' in record:
                versions.append(dict(record['e']))
        
        return versions
    
    def _find_direct_paths(self, 
                          start_version_id: str, 
                          end_version_id: str,
                          max_hops: int) -> List[Dict[str, Any]]:
        """
        Find direct paths between two specific entity versions.
        
        Args:
            start_version_id: Version ID of the start entity
            end_version_id: Version ID of the end entity
            max_hops: Maximum number of hops in the path
            
        Returns:
            List of paths between the entities
        """
        if not self.graph_manager:
            return []
        
        # Query direct paths
        query = f"""
        MATCH path = (start:TemporalEntity)-[*1..{max_hops}]->(end:TemporalEntity)
        WHERE start.version_id = $start_version_id AND end.version_id = $end_version_id
        RETURN path
        LIMIT 10
        """
        
        params = {
            "start_version_id": start_version_id,
            "end_version_id": end_version_id
        }
        
        result = self.graph_manager.execute_query(query, params)
        
        paths = []
        for record in result:
            if 'path' in record and record['path']:
                path_data = self._extract_path_data(record['path'])
                paths.append({
                    "type": "direct",
                    "start_version_id": start_version_id,
                    "end_version_id": end_version_id,
                    "path": path_data
                })
        
        return paths
    
    def _find_paths_between_entity_versions(self,
                                          start_entity_id: str,
                                          end_entity_id: str,
                                          max_hops: int) -> List[Dict[str, Any]]:
        """
        Find paths between any versions of two entities.
        
        Args:
            start_entity_id: Stable ID of the start entity
            end_entity_id: Stable ID of the end entity
            max_hops: Maximum number of hops in the path
            
        Returns:
            List of paths between entity versions
        """
        if not self.graph_manager:
            return []
        
        # Query paths between versions
        query = f"""
        MATCH path = (start:TemporalEntity)-[*1..{max_hops}]->(end:TemporalEntity)
        WHERE start.entity_id = $start_entity_id AND end.entity_id = $end_entity_id
        RETURN path
        LIMIT 10
        """
        
        params = {
            "start_entity_id": start_entity_id,
            "end_entity_id": end_entity_id
        }
        
        result = self.graph_manager.execute_query(query, params)
        
        paths = []
        for record in result:
            if 'path' in record and record['path']:
                path_data = self._extract_path_data(record['path'])
                
                # Extract start and end version IDs from the path
                start_version_id = path_data[0].get("data", {}).get("version_id") if path_data else None
                end_version_id = path_data[-1].get("data", {}).get("version_id") if path_data else None
                
                paths.append({
                    "type": "version_path",
                    "start_entity_id": start_entity_id,
                    "end_entity_id": end_entity_id,
                    "start_version_id": start_version_id,
                    "end_version_id": end_version_id,
                    "path": path_data
                })
        
        return paths
    
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
    
    def trace_concept_evolution(self,
                               concept_name: str,
                               from_date: Optional[datetime] = None,
                               to_date: Optional[datetime] = None,
                               include_related_concepts: bool = False) -> Dict[str, Any]:
        """
        Trace the evolution of a concept over time.
        
        Args:
            concept_name: Name of the concept to trace
            from_date: Start date for the trace (defaults to earliest)
            to_date: End date for the trace (defaults to now)
            include_related_concepts: Whether to include related concepts
            
        Returns:
            Dictionary with evolution data for the concept
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty evolution data")
            return {"concept": concept_name, "evolution": []}
        
        # Set default dates if not provided
        if to_date is None:
            to_date = datetime.now()
        
        # Find entities matching the concept name
        query = """
        MATCH (e:TemporalEntity)
        WHERE e.name = $concept_name OR e.name CONTAINS $concept_name
        RETURN e.entity_id AS entity_id, e.label AS entity_type, e.name AS name
        """
        
        result = self.graph_manager.execute_query(query, {"concept_name": concept_name})
        
        entity_ids = []
        for record in result:
            if 'entity_id' in record:
                entity_ids.append(record['entity_id'])
        
        if not entity_ids:
            logger.warning(f"No entities found for concept: {concept_name}")
            return {"concept": concept_name, "evolution": []}
        
        # Get versions for each entity
        all_versions = []
        for entity_id in entity_ids:
            version_query = """
            MATCH (e:TemporalEntity)
            WHERE e.entity_id = $entity_id
            """
            
            if from_date:
                version_query += " AND e.valid_from >= $from_date"
            
            if to_date:
                version_query += " AND e.valid_from <= $to_date"
            
            version_query += """
            RETURN e
            ORDER BY e.valid_from
            """
            
            params = {
                "entity_id": entity_id
            }
            
            if from_date:
                params["from_date"] = from_date.isoformat()
            
            if to_date:
                params["to_date"] = to_date.isoformat()
            
            version_result = self.graph_manager.execute_query(version_query, params)
            
            for record in version_result:
                if 'e' in record:
                    all_versions.append(dict(record['e']))
        
        # Sort all versions by valid_from date
        all_versions.sort(key=lambda x: x.get("valid_from", ""))
        
        # Get evolution relationships between versions
        evolution_relationships = []
        if len(all_versions) > 0:
            rel_query = """
            MATCH (e1:TemporalEntity)-[r:EVOLVED_INTO|REPLACED_BY|INSPIRED|MERGED_WITH]->(e2:TemporalEntity)
            WHERE e1.entity_id IN $entity_ids AND e2.entity_id IN $entity_ids
            RETURN e1.version_id AS source_id, e2.version_id AS target_id, 
                   type(r) AS relationship_type, r AS properties
            """
            
            rel_result = self.graph_manager.execute_query(rel_query, {"entity_ids": entity_ids})
            
            for record in rel_result:
                evolution_relationships.append({
                    "source_id": record.get("source_id"),
                    "target_id": record.get("target_id"),
                    "type": record.get("relationship_type"),
                    "properties": dict(record.get("properties", {}))
                })
        
        # If requested, include related concepts
        related_concepts = []
        if include_related_concepts:
            related_query = """
            MATCH (e1:TemporalEntity)-[r]->(e2:TemporalEntity)
            WHERE e1.entity_id IN $entity_ids AND NOT e2.entity_id IN $entity_ids
            RETURN DISTINCT e2.entity_id AS related_id, e2.name AS related_name,
                   e2.label AS related_type, type(r) AS relationship_type
            UNION
            MATCH (e1:TemporalEntity)-[r]->(e2:TemporalEntity)
            WHERE NOT e1.entity_id IN $entity_ids AND e2.entity_id IN $entity_ids
            RETURN DISTINCT e1.entity_id AS related_id, e1.name AS related_name,
                   e1.label AS related_type, type(r) AS relationship_type
            """
            
            related_result = self.graph_manager.execute_query(related_query, {"entity_ids": entity_ids})
            
            for record in related_result:
                related_concepts.append({
                    "id": record.get("related_id"),
                    "name": record.get("related_name"),
                    "type": record.get("related_type"),
                    "relationship": record.get("relationship_type")
                })
        
        return {
            "concept": concept_name,
            "entity_ids": entity_ids,
            "versions": all_versions,
            "evolution_relationships": evolution_relationships,
            "related_concepts": related_concepts
        }
    
    def get_timeline_data(self,
                         entity_type: Optional[str] = None,
                         from_date: Optional[datetime] = None,
                         to_date: Optional[datetime] = None,
                         granularity: str = "month") -> Dict[str, Any]:
        """
        Get timeline data showing entity counts over time.
        
        Args:
            entity_type: Type of entities to include (or None for all)
            from_date: Start date for the timeline (defaults to earliest)
            to_date: End date for the timeline (defaults to now)
            granularity: Time granularity (day, week, month, year)
            
        Returns:
            Dictionary with timeline data
        """
        if not self.graph_manager:
            logger.warning("No graph manager available, returning empty timeline data")
            return {"timeline": []}
        
        # Set default dates if not provided
        if to_date is None:
            to_date = datetime.now()
        
        # Build the query based on granularity
        date_format = ""
        if granularity == "day":
            date_format = "%Y-%m-%d"
        elif granularity == "week":
            date_format = "%Y-W%W"
        elif granularity == "month":
            date_format = "%Y-%m"
        elif granularity == "year":
            date_format = "%Y"
        else:
            date_format = "%Y-%m"  # Default to month
        
        # Build the query
        query = """
        MATCH (e:TemporalEntity)
        """
        
        if entity_type:
            query += f" WHERE e:{entity_type}"
        
        if from_date:
            if "WHERE" in query:
                query += " AND"
            else:
                query += " WHERE"
            query += " e.valid_from >= $from_date"
        
        if to_date:
            if "WHERE" in query:
                query += " AND"
            else:
                query += " WHERE"
            query += " e.valid_from <= $to_date"
        
        query += f"""
        WITH datetime(e.valid_from) AS date, e.label AS type
        RETURN datetime.format(date, '{date_format}') AS period,
               type, count(e) AS count
        ORDER BY period
        """
        
        params = {}
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()
        
        result = self.graph_manager.execute_query(query, params)
        
        # Process the results
        timeline_data = {}
        entity_types = set()
        
        for record in result:
            period = record.get("period")
            entity_type = record.get("type")
            count = record.get("count")
            
            if period not in timeline_data:
                timeline_data[period] = {}
            
            timeline_data[period][entity_type] = count
            entity_types.add(entity_type)
        
        # Convert to list format
        timeline = []
        for period, counts in sorted(timeline_data.items()):
            entry = {"period": period}
            for entity_type in entity_types:
                entry[entity_type] = counts.get(entity_type, 0)
            timeline.append(entry)
        
        return {
            "timeline": timeline,
            "entity_types": list(entity_types),
            "granularity": granularity,
            "from_date": from_date.isoformat() if from_date else None,
            "to_date": to_date.isoformat() if to_date else None
        }