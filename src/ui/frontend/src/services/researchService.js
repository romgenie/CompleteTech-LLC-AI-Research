import axios from 'axios';

// Create axios instance for research orchestration API
const researchApi = axios.create({
  baseURL: '/api/research-orchestration',
});

// Add request interceptor to add authentication token
researchApi.interceptors.request.use(
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
 * Research service for interacting with the research orchestration API.
 */
const researchService = {
  /**
   * Submit a research query for processing.
   * 
   * @param {Object} queryData - Research query data
   * @returns {Promise<Object>} - Created research task
   */
  submitQuery: async (queryData) => {
    try {
      const response = await researchApi.post('/queries/', queryData);
      return response.data;
    } catch (error) {
      console.error('Error submitting research query:', error);
      throw error;
    }
  },

  /**
   * Get research tasks with optional filtering.
   * 
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} - List of research tasks
   */
  getTasks: async (params = {}) => {
    try {
      const response = await researchApi.get('/tasks/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching research tasks:', error);
      throw error;
    }
  },

  /**
   * Get a specific research task by ID.
   * 
   * @param {string} taskId - Task ID
   * @returns {Promise<Object>} - Research task details
   */
  getTaskById: async (taskId) => {
    try {
      const response = await researchApi.get(`/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching research task ${taskId}:`, error);
      throw error;
    }
  },

  /**
   * Cancel a research task.
   * 
   * @param {string} taskId - Task ID
   * @returns {Promise<void>}
   */
  cancelTask: async (taskId) => {
    try {
      await researchApi.delete(`/tasks/${taskId}`);
    } catch (error) {
      console.error(`Error canceling task ${taskId}:`, error);
      throw error;
    }
  },

  /**
   * Perform a quick search without creating a persistent task.
   * 
   * @param {string} query - Search query
   * @param {Array<string>} sources - Sources to search
   * @param {number} maxResults - Maximum results per source
   * @returns {Promise<Object>} - Search results
   */
  quickSearch: async (query, sources, maxResults = 5) => {
    try {
      const response = await researchApi.post('/search', null, {
        params: {
          query,
          sources: sources?.join(','),
          max_results: maxResults
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error performing quick search:', error);
      throw error;
    }
  }
};

export default researchService;