import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Service for handling workspace collaboration operations
 */
class CollaborationService {
  /**
   * Get all workspaces
   */
  async getWorkspaces() {
    try {
      const response = await axios.get(`${API_BASE_URL}/workspaces`);
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get a single workspace by ID
   */
  async getWorkspace(workspaceId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/workspaces/${workspaceId}`);
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Create a new workspace
   */
  async createWorkspace(workspaceData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/workspaces`, workspaceData);
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Update a workspace
   */
  async updateWorkspace(workspaceId, workspaceData) {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/workspaces/${workspaceId}`, 
        workspaceData
      );
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Delete a workspace
   */
  async deleteWorkspace(workspaceId) {
    try {
      await axios.delete(`${API_BASE_URL}/workspaces/${workspaceId}`);
      return true;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get workspace members
   */
  async getWorkspaceMembers(workspaceId) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/workspaces/${workspaceId}/members`
      );
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Get workspace projects
   */
  async getProjects(workspaceId) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/workspaces/${workspaceId}/projects`
      );
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Add member to workspace
   */
  async addMember(workspaceId, memberData) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/workspaces/${workspaceId}/members`,
        memberData
      );
      return response.data;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Remove member from workspace
   */
  async removeMember(workspaceId, memberId) {
    try {
      await axios.delete(
        `${API_BASE_URL}/workspaces/${workspaceId}/members/${memberId}`
      );
      return true;
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * Handle API errors
   */
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data.message || 'An error occurred';
      throw new Error(message);
    } else if (error.request) {
      // Request made but no response received
      throw new Error('No response received from server');
    } else {
      // Error in request setup
      throw new Error('Error setting up request');
    }
  }
}

// Create singleton instance
const collaborationService = new CollaborationService();

export default collaborationService;