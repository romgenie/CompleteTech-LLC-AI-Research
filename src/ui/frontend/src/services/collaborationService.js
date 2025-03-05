import axios from 'axios';
import { API_BASE_URL } from '../config';

/**
 * Service for interacting with collaboration APIs
 */
class CollaborationService {
  /**
   * Base URL for API requests
   */
  baseUrl = `${API_BASE_URL}/collaboration`;

  /**
   * Get a workspace by ID
   * 
   * @param {string} id - Workspace ID
   * @returns {Promise<Object>} - Workspace data
   */
  async getWorkspace(id) {
    const response = await axios.get(`${this.baseUrl}/workspaces/${id}`);
    return response.data;
  }

  /**
   * List all workspaces the current user has access to
   * 
   * @param {Object} filters - Optional filters
   * @returns {Promise<Array>} - List of workspaces
   */
  async listWorkspaces(filters = {}) {
    const response = await axios.get(`${this.baseUrl}/workspaces`, { params: filters });
    return response.data;
  }

  /**
   * Create a new workspace
   * 
   * @param {Object} workspaceData - Workspace data
   * @returns {Promise<Object>} - Created workspace
   */
  async createWorkspace(workspaceData) {
    const response = await axios.post(`${this.baseUrl}/workspaces`, workspaceData);
    return response.data;
  }

  /**
   * Update a workspace
   * 
   * @param {string} id - Workspace ID
   * @param {Object} workspaceData - Updated workspace data
   * @returns {Promise<Object>} - Updated workspace
   */
  async updateWorkspace(id, workspaceData) {
    const response = await axios.put(`${this.baseUrl}/workspaces/${id}`, workspaceData);
    return response.data;
  }

  /**
   * Delete a workspace
   * 
   * @param {string} id - Workspace ID
   * @returns {Promise<void>}
   */
  async deleteWorkspace(id) {
    await axios.delete(`${this.baseUrl}/workspaces/${id}`);
  }

  /**
   * Get members of a workspace
   * 
   * @param {string} workspaceId - Workspace ID
   * @returns {Promise<Array>} - List of members
   */
  async getWorkspaceMembers(workspaceId) {
    const response = await axios.get(`${this.baseUrl}/workspaces/${workspaceId}/members`);
    return response.data;
  }

  /**
   * Add a member to a workspace
   * 
   * @param {string} workspaceId - Workspace ID
   * @param {string} userId - User ID
   * @param {string} role - Role (member, admin, etc.)
   * @returns {Promise<Object>} - Added member
   */
  async addWorkspaceMember(workspaceId, userId, role) {
    const response = await axios.post(`${this.baseUrl}/workspaces/${workspaceId}/members`, {
      user_id: userId,
      role
    });
    return response.data;
  }

  /**
   * Update a workspace member
   * 
   * @param {string} workspaceId - Workspace ID
   * @param {string} userId - User ID
   * @param {string} role - New role
   * @returns {Promise<Object>} - Updated member
   */
  async updateWorkspaceMember(workspaceId, userId, role) {
    const response = await axios.put(`${this.baseUrl}/workspaces/${workspaceId}/members/${userId}`, { role });
    return response.data;
  }

  /**
   * Remove a member from a workspace
   * 
   * @param {string} workspaceId - Workspace ID
   * @param {string} userId - User ID
   * @returns {Promise<void>}
   */
  async removeWorkspaceMember(workspaceId, userId) {
    await axios.delete(`${this.baseUrl}/workspaces/${workspaceId}/members/${userId}`);
  }

  /**
   * Invite a member to a workspace by email
   * 
   * @param {string} workspaceId - Workspace ID
   * @param {string} email - Email address
   * @param {string} role - Role
   * @returns {Promise<Object>} - Created invitation
   */
  async inviteWorkspaceMember(workspaceId, email, role) {
    const response = await axios.post(`${this.baseUrl}/workspaces/${workspaceId}/invitations`, {
      email,
      role
    });
    return response.data;
  }

  /**
   * Get workspace projects
   * 
   * @param {string} workspaceId - Workspace ID
   * @returns {Promise<Array>} - List of projects
   */
  async getWorkspaceProjects(workspaceId) {
    const response = await axios.get(`${this.baseUrl}/workspaces/${workspaceId}/projects`);
    return response.data;
  }

  /**
   * Create a team
   * 
   * @param {Object} teamData - Team data
   * @returns {Promise<Object>} - Created team
   */
  async createTeam(teamData) {
    const response = await axios.post(`${this.baseUrl}/teams`, teamData);
    return response.data;
  }

  /**
   * Get user teams
   * 
   * @returns {Promise<Array>} - List of teams
   */
  async getUserTeams() {
    const response = await axios.get(`${this.baseUrl}/teams`);
    return response.data;
  }

  /**
   * Create a comment
   * 
   * @param {Object} commentData - Comment data
   * @returns {Promise<Object>} - Created comment
   */
  async createComment(commentData) {
    const response = await axios.post(`${this.baseUrl}/comments`, commentData);
    return response.data;
  }

  /**
   * Get comments for a target
   * 
   * @param {string} targetType - Target type (e.g., 'report', 'project')
   * @param {string} targetId - Target ID
   * @returns {Promise<Array>} - List of comments
   */
  async listComments(targetType, targetId) {
    const response = await axios.get(`${this.baseUrl}/comments`, {
      params: { target_type: targetType, target_id: targetId }
    });
    return response.data;
  }

  /**
   * Get replies to a comment
   * 
   * @param {string} commentId - Parent comment ID
   * @returns {Promise<Array>} - List of replies
   */
  async getCommentReplies(commentId) {
    const response = await axios.get(`${this.baseUrl}/comments/${commentId}/replies`);
    return response.data;
  }

  /**
   * Resolve a comment
   * 
   * @param {string} commentId - Comment ID
   * @returns {Promise<Object>} - Updated comment
   */
  async resolveComment(commentId) {
    const response = await axios.post(`${this.baseUrl}/comments/${commentId}/resolve`);
    return response.data;
  }

  /**
   * Get reactions for a comment
   * 
   * @param {string} commentId - Comment ID
   * @returns {Promise<Array>} - List of reactions
   */
  async getCommentReactions(commentId) {
    const response = await axios.get(`${this.baseUrl}/comments/${commentId}/reactions`);
    return response.data;
  }

  /**
   * Add a reaction to a comment
   * 
   * @param {string} commentId - Comment ID
   * @param {string} reaction - Reaction type (like, etc.)
   * @returns {Promise<Object>} - Created reaction
   */
  async addReaction(commentId, reaction) {
    const response = await axios.post(`${this.baseUrl}/comments/${commentId}/reactions`, { reaction });
    return response.data;
  }

  /**
   * Remove a reaction from a comment
   * 
   * @param {string} commentId - Comment ID
   * @param {string} reaction - Reaction type
   * @returns {Promise<void>}
   */
  async removeReaction(commentId, reaction) {
    await axios.delete(`${this.baseUrl}/comments/${commentId}/reactions/${reaction}`);
  }

  /**
   * Get project versions
   * 
   * @param {string} projectId - Project ID
   * @returns {Promise<Array>} - List of versions
   */
  async getProjectVersions(projectId) {
    const response = await axios.get(`${this.baseUrl}/versions/${projectId}`);
    return response.data;
  }

  /**
   * Get a specific version
   * 
   * @param {string} versionId - Version ID
   * @returns {Promise<Object>} - Version data
   */
  async getVersion(versionId) {
    const response = await axios.get(`${this.baseUrl}/versions/detail/${versionId}`);
    return response.data;
  }

  /**
   * Create a new version
   * 
   * @param {string} projectId - Project ID
   * @param {Object} versionData - Version data
   * @returns {Promise<Object>} - Created version
   */
  async createVersion(projectId, versionData) {
    const response = await axios.post(`${this.baseUrl}/versions/${projectId}`, versionData);
    return response.data;
  }

  /**
   * Get project branches
   * 
   * @param {string} projectId - Project ID
   * @returns {Promise<Array>} - List of branches
   */
  async getProjectBranches(projectId) {
    const response = await axios.get(`${this.baseUrl}/branches/${projectId}`);
    return response.data;
  }

  /**
   * Create a branch
   * 
   * @param {string} projectId - Project ID
   * @param {Object} branchData - Branch data
   * @returns {Promise<Object>} - Created branch
   */
  async createBranch(projectId, branchData) {
    const response = await axios.post(`${this.baseUrl}/branches/${projectId}`, branchData);
    return response.data;
  }

  /**
   * Create a merge request
   * 
   * @param {string} projectId - Project ID
   * @param {Object} mergeRequestData - Merge request data
   * @returns {Promise<Object>} - Created merge request
   */
  async createMergeRequest(projectId, mergeRequestData) {
    const response = await axios.post(`${this.baseUrl}/merge-requests/${projectId}`, mergeRequestData);
    return response.data;
  }

  /**
   * Get project merge requests
   * 
   * @param {string} projectId - Project ID
   * @param {string} status - Optional status filter
   * @returns {Promise<Array>} - List of merge requests
   */
  async getProjectMergeRequests(projectId, status = null) {
    const params = status ? { status } : {};
    const response = await axios.get(`${this.baseUrl}/merge-requests/${projectId}`, { params });
    return response.data;
  }

  /**
   * Get merge request details
   * 
   * @param {string} mergeRequestId - Merge request ID
   * @returns {Promise<Object>} - Merge request data
   */
  async getMergeRequest(mergeRequestId) {
    const response = await axios.get(`${this.baseUrl}/merge-requests/detail/${mergeRequestId}`);
    return response.data;
  }

  /**
   * Approve a merge request
   * 
   * @param {string} mergeRequestId - Merge request ID
   * @returns {Promise<Object>} - Updated merge request
   */
  async approveMergeRequest(mergeRequestId) {
    const response = await axios.post(`${this.baseUrl}/merge-requests/${mergeRequestId}/approve`);
    return response.data;
  }

  /**
   * Merge a merge request
   * 
   * @param {string} mergeRequestId - Merge request ID
   * @returns {Promise<Object>} - Updated merge request
   */
  async mergeMergeRequest(mergeRequestId) {
    const response = await axios.post(`${this.baseUrl}/merge-requests/${mergeRequestId}/merge`);
    return response.data;
  }

  /**
   * Get version diff
   * 
   * @param {string} versionId - Version ID
   * @param {string} baseVersionId - Base version ID to compare against
   * @returns {Promise<Object>} - Diff data
   */
  async getVersionDiff(versionId, baseVersionId) {
    const response = await axios.get(`${this.baseUrl}/versions/diff/${versionId}`, {
      params: { base_version_id: baseVersionId }
    });
    return response.data;
  }
}

export default new CollaborationService();