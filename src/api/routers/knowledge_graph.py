"""
Knowledge Graph router for the API.

This module provides endpoints for interacting with the knowledge graph system.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path

from src.knowledge_graph_system.core.knowledge_graph_manager import KnowledgeGraphManager

# Mock models for testing
class GraphEntity:
    def __init__(self, id, name, label, aliases=None, properties=None, source=None, confidence=1.0, 
                 created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.label = label
        self.aliases = aliases or []
        self.properties = properties or {}
        self.source = source
        self.confidence = confidence
        self.created_at = created_at
        self.updated_at = updated_at

class GraphRelationship:
    def __init__(self, id, type, source_id, target_id, properties=None, confidence=1.0, 
                 source=None, bidirectional=False, created_at=None, updated_at=None):
        self.id = id
        self.type = type
        self.source_id = source_id
        self.target_id = target_id
        self.properties = properties or {}
        self.confidence = confidence
        self.source = source
        self.bidirectional = bidirectional
        self.created_at = created_at
        self.updated_at = updated_at

from src.api.dependencies.auth import User, get_current_user
from src.api.dependencies.database import get_knowledge_graph_manager
from src.api.models.entity import (
    Entity, 
    EntityCreate, 
    EntityUpdate, 
    EntityList, 
    EntitySearch
)
from src.api.models.relationship import (
    Relationship, 
    RelationshipCreate, 
    RelationshipUpdate, 
    RelationshipList,
    RelationshipSearch,
    RelationshipWithEntities
)


logger = logging.getLogger(__name__)
router = APIRouter()


# Entity endpoints
@router.post(
    "/entities/", 
    response_model=Entity, 
    status_code=201,
    summary="Create entity"
)
async def create_entity(
    entity: EntityCreate,
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> Entity:
    """
    Create a new entity in the knowledge graph.
    
    Args:
        entity: Entity data to create
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        Entity: Created entity
        
    Raises:
        HTTPException: If entity creation fails
    """
    # Create GraphEntity from EntityCreate
    graph_entity = GraphEntity(
        id=str(uuid.uuid4()),
        name=entity.name,
        label=entity.label,
        aliases=entity.aliases or [],
        properties=entity.properties or {},
        source=entity.source,
        confidence=entity.confidence,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    # Add entity to knowledge graph
    result = kg_manager.add_entity(graph_entity)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400, 
            detail=result.get("error", "Failed to create entity")
        )
    
    # Convert GraphEntity to Entity response model
    return Entity(
        id=graph_entity.id,
        name=graph_entity.name,
        label=graph_entity.label,
        aliases=graph_entity.aliases,
        properties=graph_entity.properties,
        source=graph_entity.source,
        confidence=graph_entity.confidence,
        created_at=datetime.fromisoformat(graph_entity.created_at) if graph_entity.created_at else None,
        updated_at=datetime.fromisoformat(graph_entity.updated_at) if graph_entity.updated_at else None
    )


@router.get(
    "/entities/{entity_id}", 
    response_model=Entity,
    summary="Get entity"
)
async def get_entity(
    entity_id: str = Path(..., description="The ID of the entity to retrieve"),
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> Entity:
    """
    Get an entity by ID.
    
    Args:
        entity_id: ID of the entity to retrieve
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        Entity: Retrieved entity
        
    Raises:
        HTTPException: If entity is not found
    """
    entity = kg_manager.get_entity_by_id(entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Convert GraphEntity to Entity response model
    return Entity(
        id=entity.id,
        name=entity.name,
        label=entity.label,
        aliases=entity.aliases,
        properties=entity.properties,
        source=entity.source,
        confidence=entity.confidence,
        created_at=datetime.fromisoformat(entity.created_at) if entity.created_at else None,
        updated_at=datetime.fromisoformat(entity.updated_at) if entity.updated_at else None
    )


@router.get(
    "/entities/", 
    response_model=EntityList,
    summary="List entities"
)
async def list_entities(
    label: Optional[str] = Query(None, description="Filter by entity label"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> EntityList:
    """
    List entities, optionally filtered by label.
    
    Args:
        label: Optional entity label filter
        limit: Maximum number of results
        offset: Number of results to skip
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        EntityList: List of entities with pagination metadata
    """
    # Get entities
    if label:
        entities = kg_manager.get_entities_by_label(label, limit, offset)
        total = kg_manager.count_entities_by_label(label)
    else:
        entities = kg_manager.get_all_entities(limit, offset)
        total = kg_manager.count_entities()
    
    # Convert entities to response format
    items = [
        Entity(
            id=entity.id,
            name=entity.name,
            label=entity.label,
            aliases=entity.aliases,
            properties=entity.properties,
            source=entity.source,
            confidence=entity.confidence,
            created_at=datetime.fromisoformat(entity.created_at) if entity.created_at else None,
            updated_at=datetime.fromisoformat(entity.updated_at) if entity.updated_at else None
        ) 
        for entity in entities
    ]
    
    # Calculate pagination
    pages = (total + limit - 1) // limit if limit > 0 else 1
    page = (offset // limit) + 1 if limit > 0 else 1
    
    return EntityList(
        items=items,
        total=total,
        pages=pages,
        page=page,
        limit=limit
    )


@router.put(
    "/entities/{entity_id}", 
    response_model=Entity,
    summary="Update entity"
)
async def update_entity(
    entity_update: EntityUpdate,
    entity_id: str = Path(..., description="The ID of the entity to update"),
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> Entity:
    """
    Update an existing entity.
    
    Args:
        entity_update: Updated entity data
        entity_id: ID of the entity to update
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        Entity: Updated entity
        
    Raises:
        HTTPException: If entity is not found or update fails
    """
    # Check if entity exists
    existing_entity = kg_manager.get_entity_by_id(entity_id)
    
    if not existing_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Prepare update data
    update_data = {}
    
    if entity_update.name is not None:
        update_data["name"] = entity_update.name
    
    if entity_update.label is not None:
        update_data["label"] = entity_update.label
    
    if entity_update.aliases is not None:
        update_data["aliases"] = entity_update.aliases
    
    if entity_update.properties is not None:
        update_data["properties"] = entity_update.properties
    
    if entity_update.source is not None:
        update_data["source"] = entity_update.source
    
    if entity_update.confidence is not None:
        update_data["confidence"] = entity_update.confidence
    
    # Add timestamp
    update_data["updated_at"] = datetime.now().isoformat()
    
    # Update entity
    result = kg_manager.update_entity(entity_id, update_data)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400, 
            detail=result.get("error", "Failed to update entity")
        )
    
    # Get updated entity
    updated_entity = kg_manager.get_entity_by_id(entity_id)
    
    # Convert to response model
    return Entity(
        id=updated_entity.id,
        name=updated_entity.name,
        label=updated_entity.label,
        aliases=updated_entity.aliases,
        properties=updated_entity.properties,
        source=updated_entity.source,
        confidence=updated_entity.confidence,
        created_at=datetime.fromisoformat(updated_entity.created_at) if updated_entity.created_at else None,
        updated_at=datetime.fromisoformat(updated_entity.updated_at) if updated_entity.updated_at else None
    )


@router.delete(
    "/entities/{entity_id}", 
    status_code=204,
    summary="Delete entity"
)
async def delete_entity(
    entity_id: str = Path(..., description="The ID of the entity to delete"),
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete an entity by ID.
    
    Args:
        entity_id: ID of the entity to delete
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If entity is not found or deletion fails
    """
    # Check if entity exists
    existing_entity = kg_manager.get_entity_by_id(entity_id)
    
    if not existing_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Delete entity
    result = kg_manager.delete_entity(entity_id)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400, 
            detail=result.get("error", "Failed to delete entity")
        )
    
    # 204 No Content response handled by FastAPI


@router.post(
    "/search/entities", 
    response_model=EntityList,
    summary="Search entities"
)
async def search_entities(
    search: EntitySearch,
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> EntityList:
    """
    Search for entities based on query and filters.
    
    Args:
        search: Search parameters
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        EntityList: List of matching entities with pagination metadata
    """
    # Search entities
    search_results = kg_manager.search_entities(
        search.query,
        search.labels,
        search.min_confidence,
        search.limit
    )
    
    # Convert to response model
    items = [
        Entity(
            id=entity.id,
            name=entity.name,
            label=entity.label,
            aliases=entity.aliases,
            properties=entity.properties,
            source=entity.source,
            confidence=entity.confidence,
            created_at=datetime.fromisoformat(entity.created_at) if entity.created_at else None,
            updated_at=datetime.fromisoformat(entity.updated_at) if entity.updated_at else None
        ) 
        for entity in search_results
    ]
    
    return EntityList(
        items=items,
        total=len(items),
        pages=1,
        page=1,
        limit=search.limit
    )


# Relationship endpoints
@router.post(
    "/relationships/", 
    response_model=Relationship, 
    status_code=201,
    summary="Create relationship"
)
async def create_relationship(
    relationship: RelationshipCreate,
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> Relationship:
    """
    Create a new relationship in the knowledge graph.
    
    Args:
        relationship: Relationship data to create
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        Relationship: Created relationship
        
    Raises:
        HTTPException: If relationship creation fails
    """
    # Check if source and target entities exist
    source_entity = kg_manager.get_entity_by_id(relationship.source_id)
    target_entity = kg_manager.get_entity_by_id(relationship.target_id)
    
    if not source_entity:
        raise HTTPException(
            status_code=404, 
            detail=f"Source entity {relationship.source_id} not found"
        )
    
    if not target_entity:
        raise HTTPException(
            status_code=404, 
            detail=f"Target entity {relationship.target_id} not found"
        )
    
    # Create GraphRelationship from RelationshipCreate
    graph_relationship = GraphRelationship(
        id=str(uuid.uuid4()),
        type=relationship.type,
        source_id=relationship.source_id,
        target_id=relationship.target_id,
        properties=relationship.properties or {},
        confidence=relationship.confidence,
        source=relationship.source,
        bidirectional=relationship.bidirectional,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    
    # Add relationship to knowledge graph
    result = kg_manager.add_relationship(graph_relationship)
    
    if not result.get("success", False):
        raise HTTPException(
            status_code=400, 
            detail=result.get("error", "Failed to create relationship")
        )
    
    # Convert GraphRelationship to Relationship response model
    return Relationship(
        id=graph_relationship.id,
        type=graph_relationship.type,
        source_id=graph_relationship.source_id,
        target_id=graph_relationship.target_id,
        properties=graph_relationship.properties,
        confidence=graph_relationship.confidence,
        source=graph_relationship.source,
        bidirectional=graph_relationship.bidirectional,
        created_at=datetime.fromisoformat(graph_relationship.created_at) if graph_relationship.created_at else None,
        updated_at=datetime.fromisoformat(graph_relationship.updated_at) if graph_relationship.updated_at else None
    )


@router.get(
    "/relationships/", 
    response_model=RelationshipList,
    summary="List relationships"
)
async def list_relationships(
    type: Optional[str] = Query(None, description="Filter by relationship type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID (either source or target)"),
    direction: str = Query("both", description="Direction of relationships: 'outgoing', 'incoming', or 'both'"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> RelationshipList:
    """
    List relationships, optionally filtered by type or entity.
    
    Args:
        type: Optional relationship type filter
        entity_id: Optional entity ID filter
        direction: Relationship direction filter
        limit: Maximum number of results
        offset: Number of results to skip
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        RelationshipList: List of relationships with pagination metadata
    """
    # Get relationships
    if type and entity_id:
        relationships = kg_manager.get_relationships_by_type_and_entity(
            entity_id, type, direction, limit, offset
        )
        total = kg_manager.count_relationships_by_type_and_entity(entity_id, type, direction)
    elif type:
        relationships = kg_manager.get_relationships_by_type(type, limit, offset)
        total = kg_manager.count_relationships_by_type(type)
    elif entity_id:
        relationships = kg_manager.get_relationships_for_entity(entity_id, direction, limit, offset)
        total = kg_manager.count_relationships_for_entity(entity_id, direction)
    else:
        relationships = kg_manager.get_all_relationships(limit, offset)
        total = kg_manager.count_relationships()
    
    # Convert relationships to response format
    items = []
    for rel in relationships:
        source_entity = kg_manager.get_entity_by_id(rel.source_id)
        target_entity = kg_manager.get_entity_by_id(rel.target_id)
        
        if source_entity and target_entity:
            items.append(
                RelationshipWithEntities(
                    id=rel.id,
                    type=rel.type,
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    properties=rel.properties,
                    confidence=rel.confidence,
                    source=rel.source,
                    bidirectional=rel.bidirectional,
                    created_at=datetime.fromisoformat(rel.created_at) if rel.created_at else None,
                    updated_at=datetime.fromisoformat(rel.updated_at) if rel.updated_at else None,
                    source_entity={
                        "id": source_entity.id,
                        "name": source_entity.name,
                        "label": source_entity.label,
                    },
                    target_entity={
                        "id": target_entity.id,
                        "name": target_entity.name,
                        "label": target_entity.label,
                    }
                )
            )
    
    # Calculate pagination
    pages = (total + limit - 1) // limit if limit > 0 else 1
    page = (offset // limit) + 1 if limit > 0 else 1
    
    return RelationshipList(
        items=items,
        total=total,
        pages=pages,
        page=page,
        limit=limit
    )


@router.get(
    "/stats", 
    response_model=Dict[str, Any],
    summary="Get graph statistics"
)
async def get_graph_statistics(
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get statistics about the knowledge graph.
    
    Args:
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Knowledge graph statistics
    """
    return kg_manager.compute_graph_statistics()


@router.get(
    "/paths", 
    response_model=List[List[Dict[str, Any]]],
    summary="Find paths between entities"
)
async def find_paths(
    source_id: str = Query(..., description="Source entity ID"),
    target_id: str = Query(..., description="Target entity ID"),
    max_depth: int = Query(3, ge=1, le=5, description="Maximum path depth"),
    kg_manager: KnowledgeGraphManager = Depends(get_knowledge_graph_manager),
    current_user: User = Depends(get_current_user)
) -> List[List[Dict[str, Any]]]:
    """
    Find paths between two entities in the knowledge graph.
    
    Args:
        source_id: Source entity ID
        target_id: Target entity ID
        max_depth: Maximum path depth
        kg_manager: Knowledge graph manager
        current_user: Current authenticated user
        
    Returns:
        List[List[Dict[str, Any]]]: List of paths between the entities
        
    Raises:
        HTTPException: If entities are not found
    """
    # Check if entities exist
    source_entity = kg_manager.get_entity_by_id(source_id)
    target_entity = kg_manager.get_entity_by_id(target_id)
    
    if not source_entity:
        raise HTTPException(status_code=404, detail=f"Source entity {source_id} not found")
    
    if not target_entity:
        raise HTTPException(status_code=404, detail=f"Target entity {target_id} not found")
    
    # Find paths
    paths = kg_manager.find_paths(source_id, target_id, max_depth)
    
    return paths