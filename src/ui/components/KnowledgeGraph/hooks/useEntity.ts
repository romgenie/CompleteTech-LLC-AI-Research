/**
 * Hook for working with individual entities
 */
import { useState, useCallback, useEffect } from 'react';
import { Entity, EntityFilter, Relationship } from '../types/knowledgeGraph.types';
import * as knowledgeGraphService from '../utils/knowledgeGraphService';

interface EntityState {
  entity: Entity | null;
  relationships: Relationship[];
  loading: boolean;
  error: Error | null;
}

interface EntityActions {
  fetchEntity: (id: string) => Promise<Entity>;
  fetchEntityRelationships: (entityId: string) => Promise<Relationship[]>;
  updateEntity: (entity: Partial<Entity>) => Promise<Entity>;
  deleteEntity: () => Promise<void>;
  createRelationship: (relationship: Omit<Relationship, 'id' | 'createdAt' | 'updatedAt'>) => Promise<Relationship>;
  deleteRelationship: (relationshipId: string) => Promise<void>;
}

export const useEntity = (entityId?: string) => {
  const [state, setState] = useState<EntityState>({
    entity: null,
    relationships: [],
    loading: false,
    error: null,
  });

  const fetchEntity = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const entity = await knowledgeGraphService.getEntity(id);
      setState(prev => ({ ...prev, entity, loading: false }));
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

  const fetchEntityRelationships = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const relationships = await knowledgeGraphService.getEntityRelationships(id);
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

  const updateEntity = useCallback(async (entityUpdate: Partial<Entity>) => {
    if (!state.entity) {
      throw new Error('No entity selected');
    }

    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const updatedEntity = await knowledgeGraphService.updateEntity(state.entity.id, entityUpdate);
      setState(prev => ({ ...prev, entity: updatedEntity, loading: false }));
      return updatedEntity;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, [state.entity]);

  const deleteEntity = useCallback(async () => {
    if (!state.entity) {
      throw new Error('No entity selected');
    }

    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      await knowledgeGraphService.deleteEntity(state.entity.id);
      setState({ entity: null, relationships: [], loading: false, error: null });
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error : new Error(String(error)),
        loading: false 
      }));
      throw error;
    }
  }, [state.entity]);

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

  const deleteRelationship = useCallback(async (relationshipId: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      await knowledgeGraphService.deleteRelationship(relationshipId);
      setState(prev => ({ 
        ...prev, 
        relationships: prev.relationships.filter(r => r.id !== relationshipId),
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

  useEffect(() => {
    if (entityId) {
      fetchEntity(entityId).then(entity => {
        fetchEntityRelationships(entityId);
      });
    }
  }, [entityId, fetchEntity, fetchEntityRelationships]);

  const actions: EntityActions = {
    fetchEntity,
    fetchEntityRelationships,
    updateEntity,
    deleteEntity,
    createRelationship,
    deleteRelationship,
  };

  return {
    ...state,
    actions,
  };
};