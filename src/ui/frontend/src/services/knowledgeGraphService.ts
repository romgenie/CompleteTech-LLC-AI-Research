import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { 
  Entity, 
  Relationship, 
  EntityType, 
  ApiResponse, 
  Graph
} from '../types';

// Create axios instance for knowledge graph API
const knowledgeGraphApi: AxiosInstance = axios.create({
  baseURL: '/knowledge',
});

// Add request interceptor to add authentication token
knowledgeGraphApi.interceptors.request.use(
  (config: AxiosRequestConfig): AxiosRequestConfig => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

// Add a response timeout for improved UX
knowledgeGraphApi.defaults.timeout = 15000;

/**
 * Type definition for graph stats
 */
interface GraphStats {
  nodeCount: number;
  edgeCount: number;
  nodeTypeCounts: Record<string, number>;
  relationshipTypeCounts: Record<string, number>;
  averageConnectivity: number;
  densityScore: number;
  lastUpdated: string;
  topEntities: Entity[];
}

/**
 * Interface for path between entities
 */
interface Path {
  path: {
    nodes: Entity[];
    relationships: Relationship[];
  }
  length: number;
  score: number;
}

/**
 * Type for search parameters
 */
interface SearchParams {
  term: string;
  type?: EntityType | 'all';
  limit?: number;
  offset?: number;
}

/**
 * Type for entity query parameters
 */
interface EntityParams {
  type?: EntityType | EntityType[];
  limit?: number;
  offset?: number;
  sortBy?: string;
  order?: 'asc' | 'desc';
  [key: string]: any;
}

/**
 * Type for related entities response
 */
interface RelatedEntitiesResponse {
  entities: Entity[];
  relationships: Relationship[];
  centrality?: number;
  clusters?: any[];
}

/**
 * Knowledge Graph service for interacting with the knowledge graph API.
 */
const knowledgeGraphService = {
  /**
   * Get entity details
   * 
   * @param entityId - Entity ID
   * @returns Entity details
   */
  getEntityDetails: async (entityId: string): Promise<Entity> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<Entity>>(`/entities/${entityId}`);
      return response.data.data as Entity;
    } catch (error) {
      console.error(`Error fetching entity details for ${entityId}:`, error);
      throw error;
    }
  },

  /**
   * Get related entities
   * 
   * @param entityId - Entity ID
   * @returns Related entities and relationships
   */
  getRelatedEntities: async (entityId: string): Promise<RelatedEntitiesResponse> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<RelatedEntitiesResponse>>(`/entities/${entityId}/related`);
      return response.data.data as RelatedEntitiesResponse;
    } catch (error) {
      console.error(`Error fetching related entities for ${entityId}:`, error);
      throw error;
    }
  },

  /**
   * Search entities by term and type
   * 
   * @param term - Search term
   * @param type - Entity type, defaults to 'all'
   * @returns Search results
   */
  searchEntities: async (term: string, type: EntityType | 'all' = 'all'): Promise<Entity[]> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<Entity[]>>('/search', { 
        params: { term, type } 
      });
      return response.data.data as Entity[];
    } catch (error) {
      console.error('Error searching entities:', error);
      throw error;
    }
  },

  /**
   * Get entities with optional filtering.
   * 
   * @param params - Query parameters
   * @returns List of entities with pagination info
   */
  getEntities: async (params: EntityParams = {}): Promise<Entity[]> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<Entity[]>>('/entities/', { params });
      return response.data.data as Entity[];
    } catch (error) {
      console.error('Error fetching entities:', error);
      throw error;
    }
  },

  /**
   * Get a specific entity by ID.
   * 
   * @param id - Entity ID
   * @returns Entity details
   */
  getEntityById: async (id: string): Promise<Entity> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<Entity>>(`/entities/${id}`);
      return response.data.data as Entity;
    } catch (error) {
      console.error(`Error fetching entity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new entity.
   * 
   * @param entityData - Entity data to create
   * @returns Created entity
   */
  createEntity: async (entityData: Partial<Entity>): Promise<Entity> => {
    try {
      const response = await knowledgeGraphApi.post<ApiResponse<Entity>>('/entities/', entityData);
      return response.data.data as Entity;
    } catch (error) {
      console.error('Error creating entity:', error);
      throw error;
    }
  },

  /**
   * Update an existing entity.
   * 
   * @param id - Entity ID
   * @param entityData - Updated entity data
   * @returns Updated entity
   */
  updateEntity: async (id: string, entityData: Partial<Entity>): Promise<Entity> => {
    try {
      const response = await knowledgeGraphApi.put<ApiResponse<Entity>>(`/entities/${id}`, entityData);
      return response.data.data as Entity;
    } catch (error) {
      console.error(`Error updating entity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete an entity.
   * 
   * @param id - Entity ID
   */
  deleteEntity: async (id: string): Promise<void> => {
    try {
      await knowledgeGraphApi.delete(`/entities/${id}`);
    } catch (error) {
      console.error(`Error deleting entity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get relationships with optional filtering.
   * 
   * @param params - Query parameters
   * @returns List of relationships with pagination info
   */
  getRelationships: async (params: Record<string, any> = {}): Promise<Relationship[]> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<Relationship[]>>('/relationships/', { params });
      return response.data.data as Relationship[];
    } catch (error) {
      console.error('Error fetching relationships:', error);
      throw error;
    }
  },

  /**
   * Create a new relationship.
   * 
   * @param relationshipData - Relationship data to create
   * @returns Created relationship
   */
  createRelationship: async (relationshipData: Partial<Relationship>): Promise<Relationship> => {
    try {
      const response = await knowledgeGraphApi.post<ApiResponse<Relationship>>('/relationships/', relationshipData);
      return response.data.data as Relationship;
    } catch (error) {
      console.error('Error creating relationship:', error);
      throw error;
    }
  },

  /**
   * Get graph statistics.
   * 
   * @returns Knowledge graph statistics
   */
  getGraphStats: async (): Promise<GraphStats> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<GraphStats>>('/stats');
      return response.data.data as GraphStats;
    } catch (error) {
      console.error('Error fetching graph statistics:', error);
      throw error;
    }
  },

  /**
   * Find paths between two entities.
   * 
   * @param sourceId - Source entity ID
   * @param targetId - Target entity ID
   * @param maxDepth - Maximum path depth
   * @returns Paths between entities
   */
  findPaths: async (sourceId: string, targetId: string, maxDepth: number = 3): Promise<Path[]> => {
    try {
      const response = await knowledgeGraphApi.get<ApiResponse<Path[]>>('/paths', {
        params: { source_id: sourceId, target_id: targetId, max_depth: maxDepth }
      });
      return response.data.data as Path[];
    } catch (error) {
      console.error('Error finding paths:', error);
      throw error;
    }
  },

  /**
   * Generate a mock graph with sample data
   * Used for testing when there's no backend
   * 
   * @returns Sample graph data
   */
  getMockGraph: (): Graph => {
    return {
      nodes: [
        { id: "1", name: "BERT", type: "MODEL" },
        { id: "2", name: "GPT-3", type: "MODEL" },
        { id: "3", name: "Attention Is All You Need", type: "PAPER" },
        { id: "4", name: "ImageNet", type: "DATASET" },
        { id: "5", name: "Transformer", type: "ALGORITHM" },
        { id: "6", name: "GLUE Benchmark", type: "DATASET" },
        { id: "7", name: "Ashish Vaswani", type: "AUTHOR" }
      ],
      relationships: [
        { id: "r1", source: "1", target: "5", type: "USES" },
        { id: "r2", source: "2", target: "5", type: "USES" },
        { id: "r3", source: "3", target: "5", type: "INTRODUCES" },
        { id: "r4", source: "1", target: "6", type: "EVALUATED_ON" },
        { id: "r5", source: "2", target: "6", type: "EVALUATED_ON" },
        { id: "r6", source: "7", target: "3", type: "AUTHORED_BY" },
        { id: "r7", source: "3", target: "1", type: "INSPIRED" }
      ]
    };
  },
  
  /**
   * Get a larger mock graph for performance testing
   * 
   * @param size - Size of the mock graph (small, medium, large)
   * @returns Large graph data for performance testing
   */
  getLargeTestGraph: async (size: 'small' | 'medium' | 'large' | 'veryLarge' | 'extreme' = 'medium'): Promise<Graph> => {
    try {
      // Import utils dynamically to avoid circular dependencies
      const { generateTestData } = await import('../utils/graphUtils');
      
      const nodeCounts = {
        'small': 100,
        'medium': 500,
        'large': 1000,
        'veryLarge': 2000,
        'extreme': 5000
      };
      
      const nodeCount = nodeCounts[size] || nodeCounts.medium;
      return generateTestData(nodeCount);
    } catch (error) {
      console.error('Error generating test graph:', error);
      return { nodes: [], relationships: [] };
    }
  },
  
  /**
   * Get real-world graph data with focus on AI research topics
   * 
   * @returns Real-world graph data
   */
  getRealWorldGraph: async (): Promise<Graph> => {
    try {
      // Try to get data from API
      const response = await knowledgeGraphApi.get<ApiResponse<Graph>>('/graph/research/ai');
      return response.data.data as Graph;
    } catch (error) {
      console.error('Error fetching real-world graph:', error);
      // If API fails, use the mock data with additional nodes
      const { generateTestData } = await import('../utils/graphUtils');
      return generateTestData(1000);
    }
  }
};

export default knowledgeGraphService;