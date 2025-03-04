import axios from 'axios';

// Create axios instance for knowledge graph API
const knowledgeGraphApi = axios.create({
  baseURL: '/api/knowledge-graph',
});

// Add request interceptor to add authentication token
knowledgeGraphApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Knowledge Graph service for interacting with the knowledge graph API.
 */
const knowledgeGraphService = {
  /**
   * Get entities with optional filtering.
   * 
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} - List of entities with pagination info
   */
  getEntities: async (params = {}) => {
    try {
      const response = await knowledgeGraphApi.get('/entities/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching entities:', error);
      throw error;
    }
  },

  /**
   * Get a specific entity by ID.
   * 
   * @param {string} id - Entity ID
   * @returns {Promise<Object>} - Entity details
   */
  getEntityById: async (id) => {
    try {
      const response = await knowledgeGraphApi.get(`/entities/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching entity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new entity.
   * 
   * @param {Object} entityData - Entity data to create
   * @returns {Promise<Object>} - Created entity
   */
  createEntity: async (entityData) => {
    try {
      const response = await knowledgeGraphApi.post('/entities/', entityData);
      return response.data;
    } catch (error) {
      console.error('Error creating entity:', error);
      throw error;
    }
  },

  /**
   * Update an existing entity.
   * 
   * @param {string} id - Entity ID
   * @param {Object} entityData - Updated entity data
   * @returns {Promise<Object>} - Updated entity
   */
  updateEntity: async (id, entityData) => {
    try {
      const response = await knowledgeGraphApi.put(`/entities/${id}`, entityData);
      return response.data;
    } catch (error) {
      console.error(`Error updating entity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete an entity.
   * 
   * @param {string} id - Entity ID
   * @returns {Promise<void>}
   */
  deleteEntity: async (id) => {
    try {
      await knowledgeGraphApi.delete(`/entities/${id}`);
    } catch (error) {
      console.error(`Error deleting entity ${id}:`, error);
      throw error;
    }
  },

  /**
   * Search for entities.
   * 
   * @param {Object} searchParams - Search parameters
   * @returns {Promise<Object>} - Search results
   */
  searchEntities: async (searchParams) => {
    try {
      const response = await knowledgeGraphApi.post('/search/entities', searchParams);
      return response.data;
    } catch (error) {
      console.error('Error searching entities:', error);
      throw error;
    }
  },

  /**
   * Get relationships with optional filtering.
   * 
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} - List of relationships with pagination info
   */
  getRelationships: async (params = {}) => {
    try {
      const response = await knowledgeGraphApi.get('/relationships/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching relationships:', error);
      throw error;
    }
  },

  /**
   * Create a new relationship.
   * 
   * @param {Object} relationshipData - Relationship data to create
   * @returns {Promise<Object>} - Created relationship
   */
  createRelationship: async (relationshipData) => {
    try {
      const response = await knowledgeGraphApi.post('/relationships/', relationshipData);
      return response.data;
    } catch (error) {
      console.error('Error creating relationship:', error);
      throw error;
    }
  },

  /**
   * Get graph statistics.
   * 
   * @returns {Promise<Object>} - Knowledge graph statistics
   */
  getGraphStats: async () => {
    try {
      const response = await knowledgeGraphApi.get('/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching graph statistics:', error);
      throw error;
    }
  },

  /**
   * Find paths between two entities.
   * 
   * @param {string} sourceId - Source entity ID
   * @param {string} targetId - Target entity ID
   * @param {number} maxDepth - Maximum path depth
   * @returns {Promise<Array>} - Paths between entities
   */
  findPaths: async (sourceId, targetId, maxDepth = 3) => {
    try {
      const response = await knowledgeGraphApi.get('/paths', {
        params: { source_id: sourceId, target_id: targetId, max_depth: maxDepth }
      });
      return response.data;
    } catch (error) {
      console.error('Error finding paths:', error);
      throw error;
    }
  }
};

export default knowledgeGraphService;