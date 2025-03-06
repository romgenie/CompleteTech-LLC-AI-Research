/**
 * Main hook for Knowledge Graph module
 */
import { useState, useCallback, useEffect } from 'react';
import { 
  Entity, 
  EntityFilter, 
  Relationship, 
  RelationshipFilter, 
  GraphData,
  GraphStatistics,
  Path,
  PathQuery,
} from '../types/knowledgeGraph.types';
import * as knowledgeGraphService from '../utils/knowledgeGraphService';

interface KnowledgeGraphState {
  loading: boolean;
  error: Error | null;
  entities: Entity[];
  relationships: Relationship[];
  selectedEntity: Entity | null;
  graphData: GraphData | null;
  graphStatistics: GraphStatistics | null;
  paths: Path[];
}

interface KnowledgeGraphActions {
  fetchEntities: (filter?: EntityFilter) => Promise<Entity[]>;
  fetchEntity: (id: string) => Promise<Entity>;
  createEntity: (entity: Omit<Entity, 'id' | 'createdAt' | 'updatedAt'>) => Promise<Entity>;
  updateEntity: (id: string, entity: Partial<Entity>) => Promise<Entity>;
  deleteEntity: (id: string) => Promise<void>;
  fetchRelationships: (filter?: RelationshipFilter) => Promise<Relationship[]>;
  fetchEntityRelationships: (entityId: string) => Promise<Relationship[]>;
  createRelationship: (relationship: Omit<Relationship, 'id' | 'createdAt' | 'updatedAt'>) => Promise<Relationship>;
  updateRelationship: (id: string, relationship: Partial<Relationship>) => Promise<Relationship>;
  deleteRelationship: (id: string) => Promise<void>;
  fetchGraphFromEntity: (entityId: string, depth?: number) => Promise<GraphData>;
  findPaths: (query: PathQuery) => Promise<Path[]>;
  fetchGraphStatistics: () => Promise<GraphStatistics>;
  selectEntity: (entity: Entity | null) => void;
}

export const useKnowledgeGraph = (initialEntityFilter?: EntityFilter, initialRelationshipFilter?: RelationshipFilter) => {
  // State
  const [state, setState] = useState<KnowledgeGraphState>({
    loading: false,
    error: null,
    entities: [],
    relationships: [],
    selectedEntity: null,
    graphData: null,
    graphStatistics: null,
    paths: [],
  });

  // Fetch entities
  const fetchEntities = useCallback(async (filter?: EntityFilter) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const entities = await knowledgeGraphService.getEntities(filter);
      setState(prev => ({ ...prev, entities, loading: false }));
      return entities;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      return [];
    }
  }, []);

  // Fetch a single entity
  const fetchEntity = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const entity = await knowledgeGraphService.getEntity(id);
      setState(prev => ({ 
        ...prev, 
        selectedEntity: entity, 
        loading: false 
      }));
      return entity;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Create a new entity
  const createEntity = useCallback(async (entity: Omit<Entity, 'id' | 'createdAt' | 'updatedAt'>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const newEntity = await knowledgeGraphService.createEntity(entity);
      setState(prev => ({ 
        ...prev, 
        entities: [...prev.entities, newEntity],
        loading: false 
      }));
      return newEntity;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Update an entity
  const updateEntity = useCallback(async (id: string, entity: Partial<Entity>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const updatedEntity = await knowledgeGraphService.updateEntity(id, entity);
      setState(prev => ({ 
        ...prev, 
        entities: prev.entities.map(e => e.id === id ? updatedEntity : e),
        selectedEntity: prev.selectedEntity?.id === id ? updatedEntity : prev.selectedEntity,
        loading: false 
      }));
      return updatedEntity;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Delete an entity
  const deleteEntity = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      await knowledgeGraphService.deleteEntity(id);
      setState(prev => ({ 
        ...prev, 
        entities: prev.entities.filter(e => e.id !== id),
        selectedEntity: prev.selectedEntity?.id === id ? null : prev.selectedEntity,
        loading: false 
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Fetch relationships
  const fetchRelationships = useCallback(async (filter?: RelationshipFilter) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const relationships = await knowledgeGraphService.getRelationships(filter);
      setState(prev => ({ ...prev, relationships, loading: false }));
      return relationships;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      return [];
    }
  }, []);

  // Fetch entity relationships
  const fetchEntityRelationships = useCallback(async (entityId: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const relationships = await knowledgeGraphService.getEntityRelationships(entityId);
      setState(prev => ({ ...prev, relationships, loading: false }));
      return relationships;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      return [];
    }
  }, []);

  // Create a new relationship
  const createRelationship = useCallback(async (relationship: Omit<Relationship, 'id' | 'createdAt' | 'updatedAt'>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const newRelationship = await knowledgeGraphService.createRelationship(relationship);
      setState(prev => ({ 
        ...prev, 
        relationships: [...prev.relationships, newRelationship],
        loading: false 
      }));
      return newRelationship;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Update a relationship
  const updateRelationship = useCallback(async (id: string, relationship: Partial<Relationship>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const updatedRelationship = await knowledgeGraphService.updateRelationship(id, relationship);
      setState(prev => ({ 
        ...prev, 
        relationships: prev.relationships.map(r => r.id === id ? updatedRelationship : r),
        loading: false 
      }));
      return updatedRelationship;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Delete a relationship
  const deleteRelationship = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      await knowledgeGraphService.deleteRelationship(id);
      setState(prev => ({ 
        ...prev, 
        relationships: prev.relationships.filter(r => r.id !== id),
        loading: false 
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Fetch graph data from entity
  const fetchGraphFromEntity = useCallback(async (entityId: string, depth: number = 2) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const graphData = await knowledgeGraphService.getGraphFromEntity(entityId, depth);
      setState(prev => ({ ...prev, graphData, loading: false }));
      return graphData;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Find paths between entities
  const findPaths = useCallback(async (query: PathQuery) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const paths = await knowledgeGraphService.findPaths(query);
      setState(prev => ({ ...prev, paths, loading: false }));
      return paths;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      return [];
    }
  }, []);

  // Fetch graph statistics
  const fetchGraphStatistics = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const statistics = await knowledgeGraphService.getGraphStatistics();
      setState(prev => ({ ...prev, graphStatistics: statistics, loading: false }));
      return statistics;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, []);

  // Select an entity
  const selectEntity = useCallback((entity: Entity | null) => {
    setState(prev => ({ ...prev, selectedEntity: entity }));
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchEntities(initialEntityFilter);
    fetchRelationships(initialRelationshipFilter);
    fetchGraphStatistics();
  }, [fetchEntities, fetchRelationships, fetchGraphStatistics, initialEntityFilter, initialRelationshipFilter]);

  // Actions object
  const actions: KnowledgeGraphActions = {
    fetchEntities,
    fetchEntity,
    createEntity,
    updateEntity,
    deleteEntity,
    fetchRelationships,
    fetchEntityRelationships,
    createRelationship,
    updateRelationship,
    deleteRelationship,
    fetchGraphFromEntity,
    findPaths,
    fetchGraphStatistics,
    selectEntity,
  };

  return {
    ...state,
    actions,
  };
};