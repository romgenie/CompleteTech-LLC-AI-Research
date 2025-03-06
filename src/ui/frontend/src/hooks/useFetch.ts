import { useState, useEffect, useCallback } from 'react';
import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse } from '../types';

interface UseFetchOptions<TRequestData = any> extends Omit<AxiosRequestConfig, 'url'> {
  data?: TRequestData;
  retries?: number;
  retryDelay?: number;
  useCache?: boolean;
  cacheTime?: number; // In milliseconds
}

interface UseFetchResult<TData, TError> {
  data: TData | null;
  loading: boolean;
  error: TError | null;
  refetch: (options?: Partial<UseFetchOptions>) => Promise<TData>;
  clearData: () => void;
}

// Cache for storing responses
const responseCache: Record<string, { data: any; timestamp: number }> = {};

/**
 * Custom hook for handling API requests with loading, error states, and retry capability
 * 
 * @template TData - Type of the response data
 * @template TError - Type of the error
 * @template TRequestData - Type of the request data
 * 
 * @param url - The API endpoint URL
 * @param options - Request options like method, headers, data
 * @param immediate - Whether to fetch immediately when component mounts
 * @param mockDataFn - Function to generate mock data if API fails
 * @returns Object containing data, loading state, error, and refetch function
 */
function useFetch<
  TData = any,
  TError = Error | AxiosError,
  TRequestData = any
>(
  url: string,
  options: UseFetchOptions<TRequestData> = {},
  immediate: boolean = true,
  mockDataFn?: () => TData
): UseFetchResult<TData, TError> {
  const [data, setData] = useState<TData | null>(null);
  const [loading, setLoading] = useState<boolean>(immediate);
  const [error, setError] = useState<TError | null>(null);
  const [retryCount, setRetryCount] = useState<number>(0);
  
  // Default options
  const defaultOptions: Partial<UseFetchOptions> = {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    retries: 3,
    retryDelay: 1000,
    useCache: true,
    cacheTime: 5 * 60 * 1000, // 5 minutes
  };
  
  // Merge default options with provided options
  const mergedOptions: UseFetchOptions = { ...defaultOptions, ...options };
  
  // Create cache key from URL and request data
  const getCacheKey = useCallback((): string => {
    const dataString = mergedOptions.data ? JSON.stringify(mergedOptions.data) : '';
    return `${mergedOptions.method}-${url}-${dataString}`;
  }, [url, mergedOptions.method, mergedOptions.data]);
  
  // Check if cached data is valid
  const isValidCache = useCallback((cacheKey: string): boolean => {
    if (!responseCache[cacheKey]) return false;
    
    const now = Date.now();
    const { timestamp } = responseCache[cacheKey];
    
    return now - timestamp < (mergedOptions.cacheTime || 0);
  }, [mergedOptions.cacheTime]);
  
  const fetchData = useCallback(async (customOptions: Partial<UseFetchOptions> = {}): Promise<TData> => {
    // Merge original options with custom options for this call
    const currentOptions = { ...mergedOptions, ...customOptions };
    const cacheKey = getCacheKey();
    
    setLoading(true);
    setError(null);
    
    // Check cache first if enabled
    if (currentOptions.useCache && isValidCache(cacheKey)) {
      const cachedData = responseCache[cacheKey].data;
      setData(cachedData);
      setLoading(false);
      return cachedData;
    }
    
    try {
      const response: AxiosResponse = await axios({
        url,
        ...currentOptions,
        headers: {
          ...currentOptions.headers,
          'Authorization': localStorage.getItem('token') 
            ? `Bearer ${localStorage.getItem('token')}` 
            : undefined
        }
      });
      
      let responseData: TData;
      
      // Handle API wrapper format if it exists
      if (response.data && typeof response.data === 'object' && 'data' in response.data) {
        responseData = (response.data as ApiResponse<TData>).data as TData;
      } else {
        responseData = response.data as TData;
      }
      
      // Cache successful response if caching is enabled
      if (currentOptions.useCache) {
        responseCache[cacheKey] = {
          data: responseData,
          timestamp: Date.now(),
        };
      }
      
      setData(responseData);
      setLoading(false);
      return responseData;
    } catch (err) {
      console.error(`Error fetching from ${url}:`, err);
      
      // Exponential backoff for retries
      if (retryCount < (currentOptions.retries || 0)) {
        const delay = Math.pow(2, retryCount) * (currentOptions.retryDelay || 1000);
        console.log(`Retrying in ${delay}ms...`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        setRetryCount(prev => prev + 1);
        return fetchData(customOptions);
      } else {
        // Handle error
        const typedError = err as TError;
        setError(typedError);
        setLoading(false);
        
        // Fall back to mock data if provided and API failed
        if (mockDataFn) {
          console.log('Falling back to mock data');
          const mockData = mockDataFn();
          setData(mockData);
          return mockData;
        }
        
        throw typedError;
      }
    }
  }, [url, mergedOptions, retryCount, mockDataFn, getCacheKey, isValidCache]);
  
  // Clear data function
  const clearData = useCallback((): void => {
    setData(null);
  }, []);
  
  // Fetch on mount if immediate is true
  useEffect(() => {
    if (immediate) {
      fetchData().catch(() => {}); // Catch error since it's already handled in state
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate]);
  
  // Reset retry count when URL or options change
  useEffect(() => {
    setRetryCount(0);
  }, [url, options.method, options.data]);
  
  const refetch = useCallback((customOptions: Partial<UseFetchOptions> = {}): Promise<TData> => {
    setRetryCount(0); // Reset retry count
    return fetchData(customOptions);
  }, [fetchData]);
  
  return { data, loading, error, refetch, clearData };
}

export default useFetch;