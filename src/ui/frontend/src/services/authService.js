import axios from 'axios';

// Create an axios instance for auth
const authApi = axios.create({
  baseURL: '/api/auth',
});

/**
 * Authentication service for handling API authentication.
 */
const authService = {
  /**
   * Log in a user with username and password.
   * 
   * @param {string} username - User's username
   * @param {string} password - User's password
   * @returns {Promise<Object>} - User and token information
   */
  login: async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await authApi.post('/token', formData);
      const { access_token, token_type, expires_at } = response.data;

      // Fetch user profile information
      const userInfo = await authService.getUserInfo(access_token);

      return {
        token: access_token,
        tokenType: token_type,
        expiresAt: expires_at,
        user: userInfo,
      };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Authentication failed';
      throw new Error(errorMessage);
    }
  },

  /**
   * Get the current user's information using their token.
   * 
   * @param {string} token - JWT token
   * @returns {Promise<Object>} - User information
   */
  getUserInfo: async (token) => {
    try {
      const response = await authApi.get('/users/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      return response.data;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to get user information';
      throw new Error(errorMessage);
    }
  },
};

export default authService;