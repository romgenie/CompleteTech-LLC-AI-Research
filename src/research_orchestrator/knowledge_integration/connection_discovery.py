"""
Connection Discovery Engine for the Knowledge Graph Integration.

This module provides the ConnectionDiscoveryEngine class that discovers non-obvious
connections between entities in the knowledge graph.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
import json

logger = logging.getLogger(__name__)


class ConnectionDiscoveryEngine:
    """Discovers non-obvious connections between entities in the knowledge graph.
    
    This class implements algorithms to find potential connections between entities
    that are not directly linked in the knowledge graph, helping to identify 
    hidden patterns and relationships.
    """
    
    # Default connection types to discover
    DEFAULT_CONNECTION_TYPES = [
        "common_intermediaries",
        "similar_relationships",
        "shared_properties",
        "temporal_connections",
        "transitive_relations"
    ]
    
    # Default relationship types to consider for transitive connections
    DEFAULT_TRANSITIVE_RELATIONSHIPS = [
        "BUILDS_ON", "IS_A", "PART_OF", "USES", "BASED_ON", "EXTENDS"
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the connection discovery engine.
        
        Args:
            config: Configuration dictionary for connection discovery
        """
        self.config = config or {}
        
        # Configure which connection types to discover
        self.connection_types = self.config.get("connection_types", self.DEFAULT_CONNECTION_TYPES)
        
        # Configure discovery parameters
        self.max_path_length = self.config.get("max_path_length", 3)
        self.min_confidence = self.config.get("min_confidence", 0.5)
        self.max_connections = self.config.get("max_connections", 100)
        self.transitive_relationship_types = self.config.get(
            "transitive_relationship_types",
            self.DEFAULT_TRANSITIVE_RELATIONSHIPS
        )
        
        # Store discovered connections
        self.discovered_connections = []
    
    def discover_connections(
        self,
        nodes: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Discover connections between entities in the knowledge graph.
        
        Args:
            nodes: List of nodes in the knowledge graph
            relationships: List of relationships in the knowledge graph
            
        Returns:
            List of discovered connections
        """
        discovered = []
        
        # Create lookup dictionaries for faster access
        node_by_id = {node["id"]: node for node in nodes}
        
        # Build adjacency list for graph algorithms
        adjacency_list = self._build_adjacency_list(relationships)
        
        # Discover each type of connection based on configuration
        if "common_intermediaries" in self.connection_types:
            connections = self._discover_common_intermediaries(nodes, adjacency_list, node_by_id)
            discovered.extend(connections)
        
        if "similar_relationships" in self.connection_types:
            connections = self._discover_similar_relationships(nodes, relationships, node_by_id)
            discovered.extend(connections)
        
        if "shared_properties" in self.connection_types:
            connections = self._discover_shared_properties(nodes)
            discovered.extend(connections)
        
        if "transitive_relations" in self.connection_types:
            connections = self._discover_transitive_relations(relationships, adjacency_list, node_by_id)
            discovered.extend(connections)
        
        # Limit the number of connections returned
        if len(discovered) > self.max_connections:
            # Sort by confidence and take the top ones
            discovered.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            discovered = discovered[:self.max_connections]
        
        # Store the discovered connections
        self.discovered_connections = discovered
        
        return discovered
    
    def _build_adjacency_list(
        self, 
        relationships: List[Dict[str, Any]]
    ) -> Dict[str, List[Tuple[str, str, Dict[str, Any]]]]:
        """Build an adjacency list representation of the graph for path finding.
        
        Args:
            relationships: List of relationships in the knowledge graph
            
        Returns:
            Dictionary mapping node IDs to lists of (target_id, relationship_type, properties)
        """
        adjacency_list = {}
        
        for rel in relationships:
            source_id = rel.get("source_id")
            target_id = rel.get("target_id")
            rel_type = rel.get("type")
            properties = rel.get("properties", {})
            
            if source_id and target_id:
                # Add outgoing edge
                if source_id not in adjacency_list:
                    adjacency_list[source_id] = []
                adjacency_list[source_id].append((target_id, rel_type, properties))
                
                # Add incoming edge if relationship is bidirectional
                if properties.get("bidirectional", False):
                    if target_id not in adjacency_list:
                        adjacency_list[target_id] = []
                    adjacency_list[target_id].append((source_id, rel_type, properties))
        
        return adjacency_list
    
    def _discover_common_intermediaries(
        self,
        nodes: List[Dict[str, Any]],
        adjacency_list: Dict[str, List[Tuple[str, str, Dict[str, Any]]]],
        node_by_id: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Discover entities that connect to the same intermediary nodes.
        
        Args:
            nodes: List of nodes in the knowledge graph
            adjacency_list: Adjacency list representation of the graph
            node_by_id: Dictionary mapping node IDs to node data
            
        Returns:
            List of discovered connections
        """
        connections = []
        
        # For each pair of nodes
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                # Skip if same node or already directly connected
                if node1["id"] == node2["id"] or self._are_directly_connected(node1["id"], node2["id"], adjacency_list):
                    continue
                
                # Find common neighbors
                common_intermediaries = self._find_common_neighbors(node1["id"], node2["id"], adjacency_list)
                
                if common_intermediaries:
                    # Create a connection for each common intermediary
                    for intermediary_id, rel_types in common_intermediaries.items():
                        if intermediary_id in node_by_id:
                            intermediary_name = node_by_id[intermediary_id]["properties"].get("name", "Unknown")
                            
                            connection = {
                                "type": "common_intermediary",
                                "entity1_id": node1["id"],
                                "entity1_name": node1["properties"].get("name", "Unknown"),
                                "entity2_id": node2["id"],
                                "entity2_name": node2["properties"].get("name", "Unknown"),
                                "intermediary_id": intermediary_id,
                                "intermediary_name": intermediary_name,
                                "relationship_types": rel_types,
                                "confidence": 0.7,  # Base confidence for this type of connection
                                "description": f"{node1['properties'].get('name', 'Entity 1')} and {node2['properties'].get('name', 'Entity 2')} are both connected to {intermediary_name}"
                            }
                            
                            connections.append(connection)
        
        return connections
    
    def _discover_similar_relationships(
        self,
        nodes: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        node_by_id: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Discover entities with similar relationships to other entities.
        
        Args:
            nodes: List of nodes in the knowledge graph
            relationships: List of relationships in the knowledge graph
            node_by_id: Dictionary mapping node IDs to node data
            
        Returns:
            List of discovered connections
        """
        connections = []
        
        # Group relationships by type
        relationships_by_type = {}
        for rel in relationships:
            rel_type = rel.get("type")
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append(rel)
        
        # For each relationship type
        for rel_type, type_relationships in relationships_by_type.items():
            # Group by target entity
            by_target = {}
            for rel in type_relationships:
                target_id = rel.get("target_id")
                if target_id not in by_target:
                    by_target[target_id] = []
                by_target[target_id].append(rel)
            
            # Find entities with relationships to the same targets
            for target_id, target_relationships in by_target.items():
                if len(target_relationships) < 2:
                    continue
                
                # Get unique source entities
                source_ids = [rel.get("source_id") for rel in target_relationships]
                
                # Create connections between sources with the same target and relationship type
                for i, source1_id in enumerate(source_ids):
                    for source2_id in source_ids[i+1:]:
                        if source1_id == source2_id:
                            continue
                        
                        if source1_id in node_by_id and source2_id in node_by_id and target_id in node_by_id:
                            source1_name = node_by_id[source1_id]["properties"].get("name", "Unknown")
                            source2_name = node_by_id[source2_id]["properties"].get("name", "Unknown")
                            target_name = node_by_id[target_id]["properties"].get("name", "Unknown")
                            
                            connection = {
                                "type": "similar_relationship",
                                "entity1_id": source1_id,
                                "entity1_name": source1_name,
                                "entity2_id": source2_id,
                                "entity2_name": source2_name,
                                "relationship_type": rel_type,
                                "target_id": target_id,
                                "target_name": target_name,
                                "confidence": 0.65,  # Base confidence for this type of connection
                                "description": f"{source1_name} and {source2_name} both have a {rel_type} relationship with {target_name}"
                            }
                            
                            connections.append(connection)
        
        return connections
    
    def _discover_shared_properties(
        self,
        nodes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Discover entities with significant shared properties.
        
        Args:
            nodes: List of nodes in the knowledge graph
            
        Returns:
            List of discovered connections
        """
        connections = []
        
        # Create dictionary of entities by their properties
        entities_by_property = {}
        
        # Collect properties we're interested in (excluding common ones like id, name, confidence)
        excluded_properties = {"id", "name", "confidence", "provenance"}
        
        for node in nodes:
            for prop, value in node.get("properties", {}).items():
                if prop not in excluded_properties and value:
                    # For simplicity, convert value to string for comparison
                    # More sophisticated implementations might handle different types differently
                    if isinstance(value, (dict, list)):
                        # Skip complex properties for now
                        continue
                    
                    key = f"{prop}:{value}"
                    if key not in entities_by_property:
                        entities_by_property[key] = []
                    entities_by_property[key].append(node)
        
        # Find entities sharing the same property values
        for prop_key, prop_entities in entities_by_property.items():
            if len(prop_entities) < 2:
                continue
            
            prop_name, prop_value = prop_key.split(":", 1)
            
            # Create connections between entities with shared properties
            for i, entity1 in enumerate(prop_entities):
                for entity2 in prop_entities[i+1:]:
                    # Don't create connections for entities of same type with common properties
                    if set(entity1.get("labels", [])) == set(entity2.get("labels", [])):
                        continue
                    
                    entity1_name = entity1["properties"].get("name", "Unknown")
                    entity2_name = entity2["properties"].get("name", "Unknown")
                    
                    connection = {
                        "type": "shared_property",
                        "entity1_id": entity1["id"],
                        "entity1_name": entity1_name,
                        "entity2_id": entity2["id"],
                        "entity2_name": entity2_name,
                        "property_name": prop_name,
                        "property_value": prop_value,
                        "confidence": 0.6,  # Base confidence for this type of connection
                        "description": f"{entity1_name} and {entity2_name} share the same value for {prop_name}: {prop_value}"
                    }
                    
                    connections.append(connection)
        
        return connections
    
    def _discover_transitive_relations(
        self,
        relationships: List[Dict[str, Any]],
        adjacency_list: Dict[str, List[Tuple[str, str, Dict[str, Any]]]],
        node_by_id: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Discover transitive relationships between entities.
        
        For example, if A BUILDS_ON B and B BUILDS_ON C, then A indirectly BUILDS_ON C.
        
        Args:
            relationships: List of relationships in the knowledge graph
            adjacency_list: Adjacency list representation of the graph
            node_by_id: Dictionary mapping node IDs to node data
            
        Returns:
            List of discovered connections
        """
        connections = []
        
        # Focus on relationship types that are likely to be transitive
        for rel_type in self.transitive_relationship_types:
            # Filter relationships of this type
            type_relationships = [r for r in relationships if r.get("type") == rel_type]
            
            # Build a direct lookup of source->targets for this relationship type
            direct_connections = {}
            for rel in type_relationships:
                source_id = rel.get("source_id")
                target_id = rel.get("target_id")
                
                if source_id not in direct_connections:
                    direct_connections[source_id] = set()
                direct_connections[source_id].add(target_id)
            
            # For each entity that has this relationship
            for source_id, direct_targets in direct_connections.items():
                # For each direct target
                for target_id in direct_targets:
                    # Find targets of the target (2-step connections)
                    if target_id in direct_connections:
                        indirect_targets = direct_connections[target_id]
                        
                        # Create transitive connections
                        for indirect_target in indirect_targets:
                            # Skip if there's already a direct connection
                            if indirect_target in direct_targets or indirect_target == source_id:
                                continue
                            
                            if source_id in node_by_id and target_id in node_by_id and indirect_target in node_by_id:
                                source_name = node_by_id[source_id]["properties"].get("name", "Unknown")
                                intermediate_name = node_by_id[target_id]["properties"].get("name", "Unknown")
                                target_name = node_by_id[indirect_target]["properties"].get("name", "Unknown")
                                
                                connection = {
                                    "type": "transitive_relation",
                                    "entity1_id": source_id,
                                    "entity1_name": source_name,
                                    "entity2_id": indirect_target,
                                    "entity2_name": target_name,
                                    "intermediate_id": target_id,
                                    "intermediate_name": intermediate_name,
                                    "relationship_type": rel_type,
                                    "confidence": 0.55,  # Lower confidence for transitive relationships
                                    "description": f"{source_name} has an indirect {rel_type} relationship with {target_name} via {intermediate_name}"
                                }
                                
                                connections.append(connection)
        
        return connections
    
    def _are_directly_connected(
        self,
        node1_id: str,
        node2_id: str,
        adjacency_list: Dict[str, List[Tuple[str, str, Dict[str, Any]]]]
    ) -> bool:
        """Check if two nodes are directly connected.
        
        Args:
            node1_id: ID of the first node
            node2_id: ID of the second node
            adjacency_list: Adjacency list representation of the graph
            
        Returns:
            True if the nodes are directly connected, False otherwise
        """
        # Check outgoing edges from node1
        if node1_id in adjacency_list:
            for target_id, _, _ in adjacency_list[node1_id]:
                if target_id == node2_id:
                    return True
        
        # Check outgoing edges from node2
        if node2_id in adjacency_list:
            for target_id, _, _ in adjacency_list[node2_id]:
                if target_id == node1_id:
                    return True
        
        return False
    
    def _find_common_neighbors(
        self,
        node1_id: str,
        node2_id: str,
        adjacency_list: Dict[str, List[Tuple[str, str, Dict[str, Any]]]]
    ) -> Dict[str, List[str]]:
        """Find common neighbors between two nodes.
        
        Args:
            node1_id: ID of the first node
            node2_id: ID of the second node
            adjacency_list: Adjacency list representation of the graph
            
        Returns:
            Dictionary mapping neighbor IDs to lists of relationship types
        """
        neighbors1 = {}
        neighbors2 = {}
        
        # Get neighbors of node1
        if node1_id in adjacency_list:
            for target_id, rel_type, _ in adjacency_list[node1_id]:
                if target_id not in neighbors1:
                    neighbors1[target_id] = []
                neighbors1[target_id].append(rel_type)
        
        # Get neighbors of node2
        if node2_id in adjacency_list:
            for target_id, rel_type, _ in adjacency_list[node2_id]:
                if target_id not in neighbors2:
                    neighbors2[target_id] = []
                neighbors2[target_id].append(rel_type)
        
        # Find common neighbors
        common_neighbors = {}
        for neighbor_id, rel_types1 in neighbors1.items():
            if neighbor_id in neighbors2:
                rel_types2 = neighbors2[neighbor_id]
                common_neighbors[neighbor_id] = {
                    "from_node1": rel_types1,
                    "from_node2": rel_types2
                }
        
        return common_neighbors
    
    def get_discovered_connections(self) -> List[Dict[str, Any]]:
        """Get all discovered connections.
        
        Returns:
            List of all connections discovered
        """
        return self.discovered_connections
    
    def clear_discovered_connections(self) -> None:
        """Clear the list of discovered connections."""
        self.discovered_connections = []