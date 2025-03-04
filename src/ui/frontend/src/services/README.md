# Services

This directory contains API client services for interacting with the backend.

## Services Structure

Each service module follows a consistent pattern:

1. Create an Axios instance with appropriate configuration
2. Implement API methods with proper error handling
3. Add fallback to mock data when the API is unavailable
4. Export a service object with methods

## Available Services

- `authService.js`: Authentication-related functionality (login, token management)
- `implementationService.js`: Paper implementation features
- `knowledgeGraphService.js`: Knowledge graph operations
- `researchService.js`: Research and query functionality

## Using Services

Import the service and use its methods:

```javascript
import authService from '../services/authService';

// Example usage
async function login(username, password) {
  try {
    const result = await authService.login(username, password);
    return result;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}
```

## Error Handling

All services include built-in error handling with:

1. Automatic retry for transient failures
2. Fallback to mock data when configured
3. Standardized error responses

## Mock Mode

Services can operate in mock mode for development without a backend:

- Set `MOCK_MODE` to `true` in the service file for permanent mock mode
- Services will automatically fall back to mock data if the API fails

## WebSocket Integration

For real-time updates, the WebSocket connection is managed through the WebSocketContext. Services provide methods that integrate with this context when needed.