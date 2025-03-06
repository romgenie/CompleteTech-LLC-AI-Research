/**
 * Tests for the API client service
 */
import { getWithAuth, postWithAuth, deleteWithAuth } from '../../../src/ui/frontend/src/services/apiClient';

// Mock fetch response
const mockResponse = (status: number, data: any, headers = {}) => {
  return new Response(JSON.stringify(data), {
    status,
    headers: new Headers(headers),
  });
};

describe('API Client', () => {
  // Set up mocks before each test
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem('token', 'mock-token-123');
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // Test GET with authentication
  test('getWithAuth sends request with auth header', async () => {
    // Mock successful response
    (global.fetch as jest.Mock).mockResolvedValueOnce(
      mockResponse(200, { data: { id: '123', name: 'Test Item' } })
    );

    // Make API request
    const result = await getWithAuth('/api/items/123');

    // Check fetch was called with correct parameters
    expect(global.fetch).toHaveBeenCalledWith('/api/items/123', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock-token-123',
      },
    });

    // Check result
    expect(result).toEqual({ id: '123', name: 'Test Item' });
  });

  // Test POST with authentication
  test('postWithAuth sends request with auth header and body', async () => {
    // Mock successful response
    (global.fetch as jest.Mock).mockResolvedValueOnce(
      mockResponse(201, { data: { id: '123', name: 'New Item' } })
    );

    // Data to send
    const data = { name: 'New Item' };

    // Make API request
    const result = await postWithAuth('/api/items', data);

    // Check fetch was called with correct parameters
    expect(global.fetch).toHaveBeenCalledWith('/api/items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock-token-123',
      },
      body: JSON.stringify(data),
    });

    // Check result
    expect(result).toEqual({ id: '123', name: 'New Item' });
  });

  // Test DELETE with authentication
  test('deleteWithAuth sends request with auth header', async () => {
    // Mock successful response
    (global.fetch as jest.Mock).mockResolvedValueOnce(
      mockResponse(204, null)
    );

    // Make API request
    await deleteWithAuth('/api/items/123');

    // Check fetch was called with correct parameters
    expect(global.fetch).toHaveBeenCalledWith('/api/items/123', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock-token-123',
      },
    });
  });

  // Test error handling
  test('handles API errors correctly', async () => {
    // Mock error response
    (global.fetch as jest.Mock).mockResolvedValueOnce(
      mockResponse(404, { error: 'Item not found' })
    );

    // Make API request and expect it to throw
    await expect(getWithAuth('/api/items/invalid')).rejects.toThrow();

    // Check fetch was called
    expect(global.fetch).toHaveBeenCalled();
  });

  // Test handling missing authentication token
  test('handles missing auth token', async () => {
    // Remove token
    localStorage.removeItem('token');

    // Mock response 
    (global.fetch as jest.Mock).mockResolvedValueOnce(
      mockResponse(200, { data: { id: '123', name: 'Test Item' } })
    );

    // Make API request
    const result = await getWithAuth('/api/items/123');

    // Check fetch was called without Authorization header
    expect(global.fetch).toHaveBeenCalledWith('/api/items/123', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  // Test network error handling
  test('handles network errors', async () => {
    // Mock network error
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    // Make API request and expect it to throw
    await expect(getWithAuth('/api/items/123')).rejects.toThrow('Network error');

    // Check fetch was called
    expect(global.fetch).toHaveBeenCalled();
  });
});