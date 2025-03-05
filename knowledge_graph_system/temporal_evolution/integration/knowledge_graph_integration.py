"""
Knowledge Graph Integration for the Temporal Evolution Layer.

This module provides integration between the Temporal Evolution Layer and the
existing Knowledge Graph System, allowing temporal capabilities to be used
with the core graph database.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import json
import logging
import os

from knowledge_graph_system.core.knowledge_graph_manager import KnowledgeGraphManager
from knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship
from knowledge_graph_system.core.models.ai_models import AIModel, Dataset, Algorithm, Paper

from knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)
from knowledge_graph_system.temporal_evolution.models.temporal_ai_models import (
    TemporalAIModel, TemporalDataset, TemporalAlgorithm
)
from knowledge_graph_system.temporal_evolution.core.temporal_entity_manager import (
    TemporalEntityManager
)
from knowledge_graph_system.temporal_evolution.query_engine.temporal_query_engine import (
    TemporalQueryEngine
)


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TemporalKnowledgeGraphIntegrator:
    """
    Integrator for connecting the Temporal Evolution Layer with the Knowledge Graph System.
    Provides bi-directional conversion between standard and temporal entities/relationships.
    """
    
    def __init__(self, 
                knowledge_graph_manager: KnowledgeGraphManager,
                temporal_entity_manager: TemporalEntityManager,
                temporal_query_engine: TemporalQueryEngine):
        """
        Initialize the Temporal Knowledge Graph Integrator.
        
        Args:
            knowledge_graph_manager: The core knowledge graph manager
            temporal_entity_manager: The temporal entity manager
            temporal_query_engine: The temporal query engine
        """
        self.kg_manager = knowledge_graph_manager
        self.temporal_entity_manager = temporal_entity_manager
        self.temporal_query_engine = temporal_query_engine
        
        # Map entity types from core to temporal
        self.entity_type_mapping = {
            'AIModel': TemporalAIModel,
            'Dataset': TemporalDataset,
            'Algorithm': TemporalAlgorithm,
            # Add other mappings as needed
        }
        
        # Map relationship types and create reverse mapping
        self.relationship_type_mapping = {
            'TRAINED_ON': 'TRAINED_ON',
            'EVALUATED_ON': 'EVALUATED_ON',
            'OUTPERFORMS': 'OUTPERFORMS',
            'CITES': 'CITES',
            'IMPLEMENTED_IN': 'IMPLEMENTED_IN',
            'BUILDS_ON': 'BUILDS_ON',
            'PART_OF': 'PART_OF',
            'USED_IN': 'USED_IN',
            # Add other mappings as needed
        }
        
        # Evolution relationship mappings
        self.evolution_relationship_types = {
            'EVOLVED_INTO': 'EVOLVED_INTO',
            'REPLACED_BY': 'REPLACED_BY',
            'INSPIRED': 'INSPIRED',
            'MERGED_WITH': 'MERGED_WITH'
        }
        
        # Initialize cache for entity mapping
        self.entity_id_mapping = {}  # Maps core IDs to temporal IDs and vice versa
    
    def import_from_knowledge_graph(self, 
                                  entity_types: Optional[List[str]] = None,
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None,
                                  limit: int = 1000) -> Tuple[int, int]:
        """
        Import entities and relationships from the core knowledge graph into the temporal layer.
        
        Args:
            entity_types: Optional list of entity types to import
            start_date: Optional start date for filtering entities
            end_date: Optional end date for filtering entities
            limit: Maximum number of entities to import in one call
            
        Returns:
            Tuple of (number of entities imported, number of relationships imported)
        """
        # Query entities from core knowledge graph
        entities_query = {}
        if entity_types:
            entities_query['entity_type'] = {'$in': entity_types}
        
        # Add date filters if provided
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter['$gte'] = start_date
            if end_date:
                date_filter['$lte'] = end_date
                
            if date_filter:
                entities_query['created_at'] = date_filter
        
        try:
            # Execute query on core knowledge graph
            entities = self.kg_manager.query_entities(entities_query, limit=limit)
            logger.info(f"Retrieved {len(entities)} entities from knowledge graph")
            
            # Convert and import entities
            temporal_entities = []
            for entity in entities:
                temporal_entity = self._convert_to_temporal_entity(entity)
                if temporal_entity:
                    temporal_entities.append(temporal_entity)
            
            # Import entities into temporal layer
            imported_entity_count = 0
            for entity in temporal_entities:
                try:
                    self.temporal_entity_manager.create_temporal_entity(entity)
                    # Map core ID to temporal ID
                    self.entity_id_mapping[entity.source_id] = entity.id
                    self.entity_id_mapping[entity.id] = entity.source_id
                    imported_entity_count += 1
                except Exception as e:
                    logger.warning(f"Failed to import entity {entity.name}: {str(e)}")
            
            logger.info(f"Imported {imported_entity_count} entities into temporal layer")
            
            # Import relationships between these entities
            imported_relationship_count = self._import_relationships(entities)
            logger.info(f"Imported {imported_relationship_count} relationships into temporal layer")
            
            return imported_entity_count, imported_relationship_count
            
        except Exception as e:
            logger.error(f"Failed to import from knowledge graph: {str(e)}")
            return 0, 0
    
    def _import_relationships(self, entities: List[GraphEntity]) -> int:
        """
        Import relationships between the given entities.
        
        Args:
            entities: List of core knowledge graph entities
            
        Returns:
            Number of relationships imported
        """
        # Get entity IDs
        entity_ids = [entity.id for entity in entities]
        
        # Query relationships where both source and target are in our entity list
        relationships_query = {
            '$or': [
                {'source_id': {'$in': entity_ids}},
                {'target_id': {'$in': entity_ids}}
            ]
        }
        
        try:
            # Execute query on core knowledge graph
            relationships = self.kg_manager.query_relationships(relationships_query)
            logger.info(f"Retrieved {len(relationships)} relationships from knowledge graph")
            
            # Convert and import relationships
            temporal_relationships = []
            for rel in relationships:
                # Only import if both source and target are in our imported entities
                if rel.source_id in self.entity_id_mapping and rel.target_id in self.entity_id_mapping:
                    temporal_rel = self._convert_to_temporal_relationship(rel)
                    if temporal_rel:
                        temporal_relationships.append(temporal_rel)
            
            # Import relationships into temporal layer
            imported_count = 0
            for rel in temporal_relationships:
                try:
                    self.temporal_entity_manager.create_temporal_relationship(rel)
                    imported_count += 1
                except Exception as e:
                    logger.warning(f"Failed to import relationship {rel.type}: {str(e)}")
            
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import relationships: {str(e)}")
            return 0
    
    def export_to_knowledge_graph(self, 
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                include_evolution: bool = True) -> Tuple[int, int]:
        """
        Export entities and relationships from the temporal layer to the core knowledge graph.
        
        Args:
            start_date: Optional start date for filtering entities
            end_date: Optional end date for filtering entities
            include_evolution: Whether to include evolution relationships
            
        Returns:
            Tuple of (number of entities exported, number of relationships exported)
        """
        try:
            # Query temporal entities
            temporal_entities = self.temporal_query_engine.query_entities(
                time_window=(start_date, end_date)
            )
            logger.info(f"Retrieved {len(temporal_entities)} entities from temporal layer")
            
            # Convert and export entities
            core_entities = []
            for entity in temporal_entities:
                # Skip if already in core KG (by checking source_id)
                if hasattr(entity, 'source_id') and entity.source_id:
                    # Update existing entity instead of creating new one
                    core_entity = self._update_core_entity(entity)
                else:
                    # Convert to core entity
                    core_entity = self._convert_to_core_entity(entity)
                
                if core_entity:
                    core_entities.append(core_entity)
            
            # Export entities to core knowledge graph
            exported_entity_count = 0
            for entity in core_entities:
                try:
                    entity_id = self.kg_manager.add_entity(entity)
                    if entity_id:
                        # Map temporal ID to core ID
                        entity_temp_id = getattr(entity, '_temp_id', None)
                        if entity_temp_id:
                            self.entity_id_mapping[entity_temp_id] = entity_id
                            self.entity_id_mapping[entity_id] = entity_temp_id
                        exported_entity_count += 1
                except Exception as e:
                    logger.warning(f"Failed to export entity {entity.name}: {str(e)}")
            
            logger.info(f"Exported {exported_entity_count} entities to knowledge graph")
            
            # Export relationships
            exported_relationship_count = self._export_relationships(
                temporal_entities, include_evolution
            )
            logger.info(f"Exported {exported_relationship_count} relationships to knowledge graph")
            
            return exported_entity_count, exported_relationship_count
            
        except Exception as e:
            logger.error(f"Failed to export to knowledge graph: {str(e)}")
            return 0, 0
    
    def _export_relationships(self, 
                            temporal_entities: List[TemporalEntityBase],
                            include_evolution: bool) -> int:
        """
        Export relationships between temporal entities to the core knowledge graph.
        
        Args:
            temporal_entities: List of temporal entities
            include_evolution: Whether to include evolution relationships
            
        Returns:
            Number of relationships exported
        """
        # Get entity IDs
        entity_ids = [entity.id for entity in temporal_entities]
        
        # Query temporal relationships
        temporal_relationships = self.temporal_query_engine.query_relationships(
            source_ids=entity_ids,
            target_ids=entity_ids
        )
        logger.info(f"Retrieved {len(temporal_relationships)} relationships from temporal layer")
        
        # Filter evolution relationships if needed
        if not include_evolution:
            temporal_relationships = [
                rel for rel in temporal_relationships
                if rel.type not in self.evolution_relationship_types.values()
            ]
        
        # Convert and export relationships
        core_relationships = []
        for rel in temporal_relationships:
            core_rel = self._convert_to_core_relationship(rel)
            if core_rel:
                core_relationships.append(core_rel)
        
        # Export relationships to core knowledge graph
        exported_count = 0
        for rel in core_relationships:
            try:
                rel_id = self.kg_manager.add_relationship(rel)
                if rel_id:
                    exported_count += 1
            except Exception as e:
                logger.warning(f"Failed to export relationship {rel.type}: {str(e)}")
        
        return exported_count
    
    def _convert_to_temporal_entity(self, entity: GraphEntity) -> Optional[TemporalEntityBase]:
        """
        Convert a core knowledge graph entity to a temporal entity.
        
        Args:
            entity: Core knowledge graph entity
            
        Returns:
            Converted temporal entity, or None if conversion failed
        """
        try:
            # Determine the appropriate temporal entity class
            entity_type = entity.__class__.__name__
            temporal_class = self.entity_type_mapping.get(entity_type)
            
            if not temporal_class:
                # Use generic TemporalEntityBase for unknown types
                temporal_class = TemporalEntityBase
            
            # Extract common attributes
            attributes = {}
            for attr, value in entity.__dict__.items():
                if attr not in ['id', 'name', 'entity_type', 'created_at', 'updated_at']:
                    attributes[attr] = value
            
            # Create temporal entity
            temporal_entity = temporal_class(
                name=entity.name,
                source_id=entity.id,  # Store original ID
                entity_type=entity.entity_type,
                created_at=entity.created_at if hasattr(entity, 'created_at') else datetime.now(),
                updated_at=entity.updated_at if hasattr(entity, 'updated_at') else None,
                version_id="1.0",  # Initial version
                attributes=attributes
            )
            
            return temporal_entity
            
        except Exception as e:
            logger.warning(f"Failed to convert entity {entity.name} to temporal: {str(e)}")
            return None
    
    def _convert_to_temporal_relationship(self, 
                                        relationship: GraphRelationship) -> Optional[TemporalRelationshipBase]:
        """
        Convert a core knowledge graph relationship to a temporal relationship.
        
        Args:
            relationship: Core knowledge graph relationship
            
        Returns:
            Converted temporal relationship, or None if conversion failed
        """
        try:
            # Map source and target IDs to temporal IDs
            source_id = self.entity_id_mapping.get(relationship.source_id)
            target_id = self.entity_id_mapping.get(relationship.target_id)
            
            if not source_id or not target_id:
                logger.warning(f"Could not map relationship IDs: {relationship.source_id} -> {relationship.target_id}")
                return None
            
            # Extract attributes
            attributes = {}
            for attr, value in relationship.__dict__.items():
                if attr not in ['id', 'source_id', 'target_id', 'type', 'created_at']:
                    attributes[attr] = value
            
            # Map relationship type
            rel_type = self.relationship_type_mapping.get(
                relationship.type, relationship.type
            )
            
            # Create temporal relationship
            temporal_relationship = TemporalRelationshipBase(
                source_id=source_id,
                target_id=target_id,
                type=rel_type,
                created_at=relationship.created_at if hasattr(relationship, 'created_at') else datetime.now(),
                valid_from=relationship.created_at if hasattr(relationship, 'created_at') else datetime.now(),
                valid_to=None,  # No end date initially
                strength=1.0,  # Default strength
                attributes=attributes
            )
            
            return temporal_relationship
            
        except Exception as e:
            logger.warning(f"Failed to convert relationship to temporal: {str(e)}")
            return None
    
    def _convert_to_core_entity(self, entity: TemporalEntityBase) -> Optional[GraphEntity]:
        """
        Convert a temporal entity to a core knowledge graph entity.
        
        Args:
            entity: Temporal entity
            
        Returns:
            Converted core entity, or None if conversion failed
        """
        try:
            # Determine entity type and create appropriate class
            entity_type = entity.entity_type
            
            # Create a generic entity if specific type not found
            core_entity = GraphEntity(
                name=entity.name,
                entity_type=entity_type
            )
            
            # Store temporal ID for reference
            core_entity._temp_id = entity.id
            
            # Copy attributes
            if hasattr(entity, 'attributes') and entity.attributes:
                for key, value in entity.attributes.items():
                    setattr(core_entity, key, value)
            
            # Add version info
            if hasattr(entity, 'version_id'):
                core_entity.version = entity.version_id
            
            # Add dates
            if hasattr(entity, 'created_at'):
                core_entity.created_at = entity.created_at
            if hasattr(entity, 'updated_at') and entity.updated_at:
                core_entity.updated_at = entity.updated_at
            
            return core_entity
            
        except Exception as e:
            logger.warning(f"Failed to convert temporal entity {entity.name} to core: {str(e)}")
            return None
    
    def _update_core_entity(self, entity: TemporalEntityBase) -> Optional[GraphEntity]:
        """
        Update an existing core entity with temporal entity data.
        
        Args:
            entity: Temporal entity with source_id
            
        Returns:
            Updated core entity, or None if update failed
        """
        if not hasattr(entity, 'source_id') or not entity.source_id:
            return self._convert_to_core_entity(entity)
            
        try:
            # Get existing entity
            core_entity = self.kg_manager.get_entity_by_id(entity.source_id)
            if not core_entity:
                return self._convert_to_core_entity(entity)
            
            # Update attributes
            if hasattr(entity, 'attributes') and entity.attributes:
                for key, value in entity.attributes.items():
                    setattr(core_entity, key, value)
            
            # Update version info
            if hasattr(entity, 'version_id'):
                core_entity.version = entity.version_id
            
            # Update dates
            if hasattr(entity, 'updated_at') and entity.updated_at:
                core_entity.updated_at = entity.updated_at
            
            return core_entity
            
        except Exception as e:
            logger.warning(f"Failed to update core entity from temporal {entity.name}: {str(e)}")
            return None
    
    def _convert_to_core_relationship(self, 
                                    relationship: TemporalRelationshipBase) -> Optional[GraphRelationship]:
        """
        Convert a temporal relationship to a core knowledge graph relationship.
        
        Args:
            relationship: Temporal relationship
            
        Returns:
            Converted core relationship, or None if conversion failed
        """
        try:
            # Map source and target IDs to core IDs
            source_id = self.entity_id_mapping.get(relationship.source_id)
            target_id = self.entity_id_mapping.get(relationship.target_id)
            
            if not source_id or not target_id:
                logger.warning(f"Could not map temporal relationship IDs: {relationship.source_id} -> {relationship.target_id}")
                return None
            
            # Map relationship type (reverse mapping)
            for core_type, temp_type in self.relationship_type_mapping.items():
                if temp_type == relationship.type:
                    rel_type = core_type
                    break
            else:
                rel_type = relationship.type
            
            # Create core relationship
            core_relationship = GraphRelationship(
                source_id=source_id,
                target_id=target_id,
                type=rel_type
            )
            
            # Copy attributes
            if hasattr(relationship, 'attributes') and relationship.attributes:
                for key, value in relationship.attributes.items():
                    setattr(core_relationship, key, value)
            
            # Add strength as confidence
            if hasattr(relationship, 'strength'):
                core_relationship.confidence = relationship.strength
            
            # Add validity period if supported
            if hasattr(relationship, 'valid_from'):
                core_relationship.valid_from = relationship.valid_from
            if hasattr(relationship, 'valid_to') and relationship.valid_to:
                core_relationship.valid_to = relationship.valid_to
            
            # Add creation date
            if hasattr(relationship, 'created_at'):
                core_relationship.created_at = relationship.created_at
            
            return core_relationship
            
        except Exception as e:
            logger.warning(f"Failed to convert temporal relationship to core: {str(e)}")
            return None
    
    def synchronize(self, 
                  entity_types: Optional[List[str]] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  bidirectional: bool = True) -> Dict[str, int]:
        """
        Synchronize data between core knowledge graph and temporal layer.
        
        Args:
            entity_types: Optional list of entity types to synchronize
            start_date: Optional start date for filtering entities
            end_date: Optional end date for filtering entities
            bidirectional: Whether to sync in both directions
            
        Returns:
            Dictionary with synchronization statistics
        """
        stats = {
            'imported_entities': 0,
            'imported_relationships': 0,
            'exported_entities': 0,
            'exported_relationships': 0
        }
        
        try:
            # First import from core to temporal
            imported_entities, imported_relationships = self.import_from_knowledge_graph(
                entity_types=entity_types,
                start_date=start_date,
                end_date=end_date
            )
            
            stats['imported_entities'] = imported_entities
            stats['imported_relationships'] = imported_relationships
            
            # Then export from temporal to core if bidirectional
            if bidirectional:
                exported_entities, exported_relationships = self.export_to_knowledge_graph(
                    start_date=start_date,
                    end_date=end_date
                )
                
                stats['exported_entities'] = exported_entities
                stats['exported_relationships'] = exported_relationships
            
            logger.info(f"Synchronization completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Synchronization failed: {str(e)}")
            return stats
    
    def create_evolution_relationship(self, 
                                    source_id: str,
                                    target_id: str,
                                    relationship_type: str = 'EVOLVED_INTO',
                                    attributes: Dict[str, Any] = None) -> Optional[str]:
        """
        Create an evolution relationship between two entities.
        
        Args:
            source_id: ID of the source entity (original version)
            target_id: ID of the target entity (new version)
            relationship_type: Type of evolution relationship
            attributes: Optional attributes for the relationship
            
        Returns:
            ID of the created relationship, or None if creation failed
        """
        if relationship_type not in self.evolution_relationship_types.values():
            relationship_type = self.evolution_relationship_types.get(
                relationship_type, 'EVOLVED_INTO'
            )
            
        try:
            # First check if entities exist in temporal layer
            source_entity = self.temporal_query_engine.get_entity_by_id(source_id)
            target_entity = self.temporal_query_engine.get_entity_by_id(target_id)
            
            if not source_entity or not target_entity:
                logger.warning(f"Cannot create evolution relationship: entities not found")
                return None
            
            # Create the relationship
            relationship = TemporalRelationshipBase(
                source_id=source_id,
                target_id=target_id,
                type=relationship_type,
                created_at=datetime.now(),
                valid_from=datetime.now(),
                valid_to=None,
                strength=1.0,
                attributes=attributes or {}
            )
            
            # Add to temporal layer
            rel_id = self.temporal_entity_manager.create_temporal_relationship(relationship)
            
            # Also add to core knowledge graph if needed
            if self.kg_manager:
                # Convert IDs if needed
                core_source_id = self.entity_id_mapping.get(source_id, source_id)
                core_target_id = self.entity_id_mapping.get(target_id, target_id)
                
                # Map relationship type
                core_rel_type = relationship_type
                for core_type, temp_type in self.evolution_relationship_types.items():
                    if temp_type == relationship_type:
                        core_rel_type = core_type
                        break
                
                # Create core relationship
                core_relationship = GraphRelationship(
                    source_id=core_source_id,
                    target_id=core_target_id,
                    type=core_rel_type
                )
                
                # Add attributes
                if attributes:
                    for key, value in attributes.items():
                        setattr(core_relationship, key, value)
                
                # Add to core knowledge graph
                self.kg_manager.add_relationship(core_relationship)
            
            return rel_id
            
        except Exception as e:
            logger.error(f"Failed to create evolution relationship: {str(e)}")
            return None
    
    def save_entity_id_mapping(self, filepath: str) -> bool:
        """
        Save the entity ID mapping to a file for persistence.
        
        Args:
            filepath: Path to save the mapping
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.entity_id_mapping, f)
            return True
        except Exception as e:
            logger.error(f"Failed to save entity ID mapping: {str(e)}")
            return False
    
    def load_entity_id_mapping(self, filepath: str) -> bool:
        """
        Load the entity ID mapping from a file.
        
        Args:
            filepath: Path to load the mapping from
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(filepath):
            return False
            
        try:
            with open(filepath, 'r') as f:
                self.entity_id_mapping = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Failed to load entity ID mapping: {str(e)}")
            return False