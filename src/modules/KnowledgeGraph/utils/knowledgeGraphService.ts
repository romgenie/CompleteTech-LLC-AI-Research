/**
 * Knowledge Graph Service
 * Handles API interactions for the knowledge graph
 */
import { 
  Entity, 
  EntityFilter, 
  Relationship, 
  RelationshipFilter, 
  GraphData,
  PathQuery,
  Path,
  GraphStatistics
} from '../types/knowledgeGraph.types';

// Base API URL
const API_BASE_URL = '/api/knowledge-graph';

/**
 * Get entities with optional filtering
 */
export const getEntities = async (filter?: EntityFilter): Promise<Entity[]> => {
  try {
    const queryParams = new URLSearchParams();
    
    if (filter) {
      Object.entries(filter).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }
    
    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
    const response = await fetch(`${API_BASE_URL}/entities${queryString}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch entities: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching entities:', error);
    // Return mock data for development if API fails
    return getMockEntities();
  }
};

/**
 * Get a single entity by ID
 */
export const getEntity = async (id: string): Promise<Entity> => {
  try {
    const response = await fetch(`${API_BASE_URL}/entities/${id}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch entity: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching entity ${id}:`, error);
    // Return mock data for development if API fails
    return getMockEntities().find(e => e.id === id) || createMockEntity(id);
  }
};

/**
 * Create a new entity
 */
export const createEntity = async (entity: Omit<Entity, 'id' | 'createdAt' | 'updatedAt'>): Promise<Entity> => {
  try {
    const response = await fetch(`${API_BASE_URL}/entities`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(entity),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create entity: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating entity:', error);
    throw error;
  }
};

/**
 * Update an existing entity
 */
export const updateEntity = async (id: string, entity: Partial<Entity>): Promise<Entity> => {
  try {
    const response = await fetch(`${API_BASE_URL}/entities/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(entity),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update entity: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error updating entity ${id}:`, error);
    throw error;
  }
};

/**
 * Delete an entity
 */
export const deleteEntity = async (id: string): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/entities/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete entity: ${response.statusText}`);
    }
  } catch (error) {
    console.error(`Error deleting entity ${id}:`, error);
    throw error;
  }
};

/**
 * Get relationships with optional filtering
 */
export const getRelationships = async (filter?: RelationshipFilter): Promise<Relationship[]> => {
  try {
    const queryParams = new URLSearchParams();
    
    if (filter) {
      Object.entries(filter).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }
    
    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
    const response = await fetch(`${API_BASE_URL}/relationships${queryString}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch relationships: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching relationships:', error);
    // Return mock data for development if API fails
    return getMockRelationships();
  }
};

/**
 * Get a single relationship by ID
 */
export const getRelationship = async (id: string): Promise<Relationship> => {
  try {
    const response = await fetch(`${API_BASE_URL}/relationships/${id}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch relationship: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching relationship ${id}:`, error);
    // Return mock data for development if API fails
    return getMockRelationships().find(r => r.id === id) || createMockRelationship(id);
  }
};

/**
 * Create a new relationship
 */
export const createRelationship = async (relationship: Omit<Relationship, 'id' | 'createdAt' | 'updatedAt'>): Promise<Relationship> => {
  try {
    const response = await fetch(`${API_BASE_URL}/relationships`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(relationship),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create relationship: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating relationship:', error);
    throw error;
  }
};

/**
 * Update an existing relationship
 */
export const updateRelationship = async (id: string, relationship: Partial<Relationship>): Promise<Relationship> => {
  try {
    const response = await fetch(`${API_BASE_URL}/relationships/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(relationship),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update relationship: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error updating relationship ${id}:`, error);
    throw error;
  }
};

/**
 * Delete a relationship
 */
export const deleteRelationship = async (id: string): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/relationships/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete relationship: ${response.statusText}`);
    }
  } catch (error) {
    console.error(`Error deleting relationship ${id}:`, error);
    throw error;
  }
};

/**
 * Get all relationships for an entity
 */
export const getEntityRelationships = async (entityId: string): Promise<Relationship[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/entities/${entityId}/relationships`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch entity relationships: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching relationships for entity ${entityId}:`, error);
    // Return mock data for development if API fails
    return getMockRelationships().filter(r => r.sourceId === entityId || r.targetId === entityId);
  }
};

/**
 * Get graph data with a specified number of connections from a starting entity
 */
export const getGraphFromEntity = async (entityId: string, depth: number = 2): Promise<GraphData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/graph/from-entity/${entityId}?depth=${depth}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch graph data: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching graph from entity ${entityId}:`, error);
    // Return mock data for development if API fails
    return getMockGraphData();
  }
};

/**
 * Find paths between two entities
 */
export const findPaths = async (query: PathQuery): Promise<Path[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/graph/paths`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(query),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to find paths: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error finding paths:', error);
    // Return mock data for development if API fails
    return getMockPaths(query.sourceId, query.targetId);
  }
};

/**
 * Get graph statistics
 */
export const getGraphStatistics = async (): Promise<GraphStatistics> => {
  try {
    const response = await fetch(`${API_BASE_URL}/graph/statistics`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch graph statistics: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching graph statistics:', error);
    // Return mock data for development if API fails
    return getMockGraphStatistics();
  }
};

// Mock data generators for development
const getMockEntities = (): Entity[] => {
  return [
    {
      id: 'e1',
      name: 'GPT-4',
      type: 'MODEL',
      description: 'Large language model by OpenAI',
      properties: { parameters: '1.76T', architecture: 'Transformer' },
      confidence: 0.95,
      createdAt: '2023-01-01T00:00:00Z',
      updatedAt: '2023-01-01T00:00:00Z',
    },
    {
      id: 'e2',
      name: 'BERT',
      type: 'MODEL',
      description: 'Bidirectional Encoder Representations from Transformers',
      properties: { parameters: '340M', architecture: 'Transformer' },
      confidence: 0.98,
      createdAt: '2023-01-02T00:00:00Z',
      updatedAt: '2023-01-02T00:00:00Z',
    },
    {
      id: 'e3',
      name: 'Attention Is All You Need',
      type: 'PAPER',
      description: 'Original transformer paper',
      properties: { year: 2017, authors: 'Vaswani et al.' },
      confidence: 0.99,
      createdAt: '2023-01-03T00:00:00Z',
      updatedAt: '2023-01-03T00:00:00Z',
    },
    {
      id: 'e4',
      name: 'Transformer',
      type: 'ALGORITHM',
      description: 'Self-attention based neural network architecture',
      properties: { complexity: 'O(n²)' },
      confidence: 0.97,
      createdAt: '2023-01-04T00:00:00Z',
      updatedAt: '2023-01-04T00:00:00Z',
    },
    {
      id: 'e5',
      name: 'ImageNet',
      type: 'DATASET',
      description: 'Large image dataset',
      properties: { size: '14M images', classes: 21843 },
      confidence: 0.96,
      createdAt: '2023-01-05T00:00:00Z',
      updatedAt: '2023-01-05T00:00:00Z',
    },
  ];
};

const createMockEntity = (id: string): Entity => {
  return {
    id,
    name: `Entity ${id}`,
    type: 'CONCEPT',
    description: 'Auto-generated mock entity',
    properties: {},
    confidence: 0.7,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
};

const getMockRelationships = (): Relationship[] => {
  return [
    {
      id: 'r1',
      type: 'IMPLEMENTS',
      sourceId: 'e1',
      targetId: 'e4',
      properties: { year: 2020 },
      confidence: 0.92,
      createdAt: '2023-02-01T00:00:00Z',
      updatedAt: '2023-02-01T00:00:00Z',
    },
    {
      id: 'r2',
      type: 'IMPLEMENTS',
      sourceId: 'e2',
      targetId: 'e4',
      properties: { year: 2018 },
      confidence: 0.95,
      createdAt: '2023-02-02T00:00:00Z',
      updatedAt: '2023-02-02T00:00:00Z',
    },
    {
      id: 'r3',
      type: 'CITES',
      sourceId: 'e1',
      targetId: 'e3',
      properties: {},
      confidence: 0.99,
      createdAt: '2023-02-03T00:00:00Z',
      updatedAt: '2023-02-03T00:00:00Z',
    },
    {
      id: 'r4',
      type: 'CITES',
      sourceId: 'e2',
      targetId: 'e3',
      properties: {},
      confidence: 0.99,
      createdAt: '2023-02-04T00:00:00Z',
      updatedAt: '2023-02-04T00:00:00Z',
    },
    {
      id: 'r5',
      type: 'TRAINED_ON',
      sourceId: 'e1',
      targetId: 'e5',
      properties: { subset: 'partial' },
      confidence: 0.85,
      createdAt: '2023-02-05T00:00:00Z',
      updatedAt: '2023-02-05T00:00:00Z',
    },
  ];
};

const createMockRelationship = (id: string): Relationship => {
  return {
    id,
    type: 'RELATED_TO',
    sourceId: 'e1',
    targetId: 'e2',
    properties: {},
    confidence: 0.7,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
};

const getMockGraphData = (): GraphData => {
  return {
    entities: getMockEntities(),
    relationships: getMockRelationships(),
  };
};

const getMockPaths = (sourceId: string, targetId: string): Path[] => {
  const entities = getMockEntities();
  const relationships = getMockRelationships();
  
  // Find entities and relationships that could form a path
  const path: Path = {
    entities: entities.filter(e => e.id === sourceId || e.id === targetId || e.id === 'e4'),
    relationships: relationships.filter(r => 
      (r.sourceId === sourceId && r.targetId === 'e4') || 
      (r.sourceId === 'e4' && r.targetId === targetId)
    ),
    length: 2,
    score: 0.9,
  };
  
  return [path];
};

const getMockGraphStatistics = (): GraphStatistics => {
  return {
    entityCount: 5,
    relationshipCount: 5,
    entityTypeCounts: {
      MODEL: 2,
      ALGORITHM: 1,
      DATASET: 1,
      PAPER: 1,
      AUTHOR: 0,
      METHOD: 0,
      FINDING: 0,
      METRIC: 0,
      CODE: 0,
      CONCEPT: 0,
      FRAMEWORK: 0,
    },
    relationshipTypeCounts: {
      CREATED_BY: 0,
      USES: 0,
      IMPLEMENTS: 2,
      TRAINED_ON: 1,
      EVALUATED_ON: 0,
      CITES: 2,
      OUTPERFORMS: 0,
      PART_OF: 0,
      RELATED_TO: 0,
      EXTENDS: 0,
    },
    density: 0.25,
    averageDegree: 2.0,
    maxDegree: 3,
    diameter: 3,
    clusteringCoefficient: 0.5,
  };
};