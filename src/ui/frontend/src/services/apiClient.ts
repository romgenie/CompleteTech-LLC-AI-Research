import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse } from '../types';

/**
 * Configuration options for the API client
 */
export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  useAuth?: boolean;
  defaultHeaders?: Record<string, string>;
}

/**
 * Unified API client for handling all backend requests
 */
class ApiClient {
  private instance: AxiosInstance;
  private websocket: WebSocket | null = null;
  private websocketSubscribers: Map<string, Array<(data: any) => void>> = new Map();
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000;
  private websocketURL: string | null = null;

  /**
   * Create a new API client instance
   * 
   * @param config - Configuration options
   */
  constructor(config: ApiClientConfig) {
    this.instance = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
        ...config.defaultHeaders,
      },
    });

    // Add auth interceptor if requested
    if (config.useAuth) {
      this.instance.interceptors.request.use(
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
    }

    // Add response interceptor for error handling
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        // Handle auth errors (401)
        if (error.response?.status === 401) {
          console.error('Authentication error - redirecting to login');
          // Clear auth token
          localStorage.removeItem('token');
          // Redirect to login page
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Make a GET request
   * 
   * @param url - Endpoint URL
   * @param config - Axios request config
   * @returns Response data
   */
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.instance.get<ApiResponse<T>>(url, config);
      return this.extractResponseData(response);
    } catch (error) {
      this.handleError(error as AxiosError, url);
      throw error;
    }
  }

  /**
   * Make a POST request
   * 
   * @param url - Endpoint URL
   * @param data - Request payload
   * @param config - Axios request config
   * @returns Response data
   */
  async post<T, D = any>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.instance.post<ApiResponse<T>>(url, data, config);
      return this.extractResponseData(response);
    } catch (error) {
      this.handleError(error as AxiosError, url);
      throw error;
    }
  }

  /**
   * Make a PUT request
   * 
   * @param url - Endpoint URL
   * @param data - Request payload
   * @param config - Axios request config
   * @returns Response data
   */
  async put<T, D = any>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.instance.put<ApiResponse<T>>(url, data, config);
      return this.extractResponseData(response);
    } catch (error) {
      this.handleError(error as AxiosError, url);
      throw error;
    }
  }

  /**
   * Make a PATCH request
   * 
   * @param url - Endpoint URL
   * @param data - Request payload
   * @param config - Axios request config
   * @returns Response data
   */
  async patch<T, D = any>(url: string, data?: D, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.instance.patch<ApiResponse<T>>(url, data, config);
      return this.extractResponseData(response);
    } catch (error) {
      this.handleError(error as AxiosError, url);
      throw error;
    }
  }

  /**
   * Make a DELETE request
   * 
   * @param url - Endpoint URL
   * @param config - Axios request config
   * @returns Response data
   */
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.instance.delete<ApiResponse<T>>(url, config);
      return this.extractResponseData(response);
    } catch (error) {
      this.handleError(error as AxiosError, url);
      throw error;
    }
  }

  /**
   * Initialize WebSocket connection
   * 
   * @param url - WebSocket URL
   */
  connectWebSocket(url: string): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.websocketURL = url;
    this.websocket = new WebSocket(url);

    this.websocket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        // Handle different message types
        if (message.type && typeof message.data !== 'undefined') {
          // Notify subscribers for this message type
          const subscribers = this.websocketSubscribers.get(message.type) || [];
          subscribers.forEach(callback => callback(message.data));
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.websocket.onclose = () => {
      console.log('WebSocket connection closed');
      
      // Attempt to reconnect if needed
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
        console.log(`Attempting to reconnect in ${delay}ms...`);
        
        setTimeout(() => {
          this.reconnectAttempts++;
          if (this.websocketURL) {
            this.connectWebSocket(this.websocketURL);
          }
        }, delay);
      } else {
        console.error('Max reconnect attempts reached. WebSocket connection lost.');
      }
    };
  }

  /**
   * Subscribe to WebSocket messages of a specific type
   * 
   * @param messageType - Type of message to subscribe to
   * @param callback - Function to call when message received
   * @returns Unsubscribe function
   */
  subscribeToWebSocket<T = any>(messageType: string, callback: (data: T) => void): () => void {
    if (!this.websocketSubscribers.has(messageType)) {
      this.websocketSubscribers.set(messageType, []);
    }
    
    const subscribers = this.websocketSubscribers.get(messageType)!;
    subscribers.push(callback as any);
    
    // Return unsubscribe function
    return () => {
      const index = subscribers.indexOf(callback as any);
      if (index !== -1) {
        subscribers.splice(index, 1);
      }
    };
  }

  /**
   * Send a message through the WebSocket connection
   * 
   * @param type - Message type
   * @param data - Message payload
   * @returns Success status
   */
  sendWebSocketMessage<T = any>(type: string, data: T): boolean {
    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return false;
    }
    
    try {
      this.websocket.send(JSON.stringify({
        type,
        data
      }));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  /**
   * Close the WebSocket connection
   */
  disconnectWebSocket(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
      this.websocketURL = null;
    }
  }

  /**
   * Extract data from API response
   * 
   * @param response - Axios response
   * @returns Extracted data
   */
  private extractResponseData<T>(response: AxiosResponse<ApiResponse<T>>): T {
    if (response.data && 'data' in response.data) {
      return response.data.data as T;
    }
    return response.data as unknown as T;
  }

  /**
   * Centralized error handling
   * 
   * @param error - Axios error
   * @param url - Request URL
   */
  private handleError(error: AxiosError, url: string): void {
    if (error.response) {
      // Server responded with error status
      console.error(`API error for ${url}:`, {
        status: error.response.status,
        data: error.response.data
      });
    } else if (error.request) {
      // Request made but no response received
      console.error(`No response for request to ${url}:`, error.request);
    } else {
      // Error setting up request
      console.error(`Error setting up request to ${url}:`, error.message);
    }
  }
}

// Create and export the default API client instance
const defaultClient = new ApiClient({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  useAuth: true
});

export default defaultClient;