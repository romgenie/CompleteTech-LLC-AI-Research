import axios from 'axios';

// Create axios instance for research implementation API
const implementationApi = axios.create({
  baseURL: '/api/research-implementation',
});

// Add request interceptor to add authentication token
implementationApi.interceptors.request.use(
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
 * Implementation service for interacting with the research implementation API.
 */
const implementationService = {
  /**
   * Upload a research paper.
   * 
   * @param {File} file - The paper file
   * @param {Object} metadata - Paper metadata
   * @returns {Promise<Object>} - Uploaded paper information
   */
  uploadPaper: async (file, metadata = {}) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Add metadata fields to form data
      Object.entries(metadata).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, value);
        }
      });
      
      const response = await implementationApi.post('/papers/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Error uploading paper:', error);
      throw error;
    }
  },

  /**
   * Get uploaded papers.
   * 
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} - List of papers
   */
  getPapers: async (params = {}) => {
    try {
      const response = await implementationApi.get('/papers/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching papers:', error);
      throw error;
    }
  },

  /**
   * Get a specific paper by ID.
   * 
   * @param {string} paperId - Paper ID
   * @returns {Promise<Object>} - Paper details
   */
  getPaperById: async (paperId) => {
    try {
      const response = await implementationApi.get(`/papers/${paperId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching paper ${paperId}:`, error);
      throw error;
    }
  },

  /**
   * Request an implementation for a research paper.
   * 
   * @param {Object} requestData - Implementation request data
   * @returns {Promise<Object>} - Created implementation
   */
  requestImplementation: async (requestData) => {
    try {
      const response = await implementationApi.post('/implementations/', requestData);
      return response.data;
    } catch (error) {
      console.error('Error requesting implementation:', error);
      throw error;
    }
  },

  /**
   * Get implementations.
   * 
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} - List of implementations
   */
  getImplementations: async (params = {}) => {
    try {
      const response = await implementationApi.get('/implementations/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching implementations:', error);
      throw error;
    }
  },

  /**
   * Get a specific implementation by ID.
   * 
   * @param {string} implementationId - Implementation ID
   * @returns {Promise<Object>} - Implementation details
   */
  getImplementationById: async (implementationId) => {
    try {
      const response = await implementationApi.get(`/implementations/${implementationId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching implementation ${implementationId}:`, error);
      throw error;
    }
  },

  /**
   * Cancel an implementation.
   * 
   * @param {string} implementationId - Implementation ID
   * @returns {Promise<void>}
   */
  cancelImplementation: async (implementationId) => {
    try {
      await implementationApi.delete(`/implementations/${implementationId}`);
    } catch (error) {
      console.error(`Error canceling implementation ${implementationId}:`, error);
      throw error;
    }
  }
};

export default implementationService;