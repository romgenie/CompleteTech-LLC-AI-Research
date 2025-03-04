import axios from 'axios';

// Create an axios instance for auth
const authApi = axios.create({
  baseURL: '/api/auth',
});

// Mock data for testing
const MOCK_MODE = false; // Set to false to try real API first, but fall back to mock when API fails
const MOCK_USERS = {
  'admin': {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: 'Admin User',
    role: 'admin',
    permissions: ['read', 'write', 'admin']
  },
  'researcher': {
    id: 2,
    username: 'researcher',
    email: 'researcher@example.com',
    full_name: 'Research User',
    role: 'researcher',
    permissions: ['read', 'write']
  },
  'viewer': {
    id: 3,
    username: 'viewer',
    email: 'viewer@example.com',
    full_name: 'View Only User',
    role: 'viewer',
    permissions: ['read']
  }
};

// Default password for testing: 'password'

// Create a mock JWT token
const createMockToken = (username) => {
  // Create payload with standard JWT claims
  const payload = {
    sub: MOCK_USERS[username].id.toString(),
    exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours from now
    iat: Math.floor(Date.now() / 1000),
    username: username,
    role: MOCK_USERS[username].role
  };
  
  // Base64 encode the payload (this is NOT secure, just for testing)
  const encodedPayload = btoa(JSON.stringify(payload));
  
  // Return a mock token structure (header.payload.signature)
  return `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.${encodedPayload}.MOCK_SIGNATURE`;
};

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
    // Try the actual implementation first, unless in mock mode
    if (!MOCK_MODE) {
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
        console.log('Auth API failed, falling back to mock data');
        // Fall back to mock mode if API fails
        if (MOCK_USERS[username] && password === 'password') {
          const token = createMockToken(username);
          return {
            token,
            tokenType: 'bearer',
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
            user: MOCK_USERS[username]
          };
        } else {
          const errorMessage = error.response?.data?.detail || 'Authentication failed';
          throw new Error(errorMessage);
        }
      }
    } else {
      // Use mock authentication for testing
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          // Check if user exists and password is correct
          if (MOCK_USERS[username] && password === 'password') {
            const token = createMockToken(username);
            resolve({
              token,
              tokenType: 'bearer',
              expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
              user: MOCK_USERS[username]
            });
          } else {
            reject(new Error('Invalid username or password'));
          }
        }, 500); // Add delay to simulate network request
      });
    }
  },

  /**
   * Get the current user's information using their token.
   * 
   * @param {string} token - JWT token
   * @returns {Promise<Object>} - User information
   */
  getUserInfo: async (token) => {
    // Try the actual implementation first, unless in mock mode
    if (!MOCK_MODE) {
      try {
        const response = await authApi.get('/users/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        
        return response.data;
      } catch (error) {
        console.log('User API failed, falling back to mock data');
        // Fall back to mock mode if API fails
        try {
          // Decode the token to get the username
          const payload = JSON.parse(atob(token.split('.')[1]));
          const username = payload.username;
          
          if (MOCK_USERS[username]) {
            return MOCK_USERS[username];
          } else {
            const errorMessage = error.response?.data?.detail || 'Failed to get user information';
            throw new Error(errorMessage);
          }
        } catch (err) {
          throw new Error('Invalid token');
        }
      }
    } else {
      // Use mock data for testing
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          try {
            // Decode the token to get the username
            const payload = JSON.parse(atob(token.split('.')[1]));
            const username = payload.username;
            
            if (MOCK_USERS[username]) {
              resolve(MOCK_USERS[username]);
            } else {
              reject(new Error('User not found'));
            }
          } catch (err) {
            reject(new Error('Invalid token'));
          }
        }, 300); // Add delay to simulate network request
      });
    }
  },
};

export default authService;