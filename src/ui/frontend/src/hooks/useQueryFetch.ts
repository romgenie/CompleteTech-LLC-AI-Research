import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import { ApiResponse } from '../types';

/**
 * Type for query options
 */
type QueryFetchOptions<TData> = {
  url: string;
  config?: AxiosRequestConfig;
  queryOptions?: Omit<UseQueryOptions<TData, AxiosError>, 'queryKey' | 'queryFn'>;
  mockData?: () => TData;
  onSuccess?: (data: TData) => void;
  onError?: (error: AxiosError) => void;
};

/**
 * Type for mutation options
 */
type MutationFetchOptions<TData, TVariables> = {
  url: string;
  method?: 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  config?: Omit<AxiosRequestConfig, 'method' | 'data'>;
  mutationOptions?: Omit<UseMutationOptions<TData, AxiosError, TVariables>, 'mutationFn'>;
  mockData?: (variables: TVariables) => TData;
};

/**
 * Hook for making GET requests with React Query
 * @param options - Options for the query
 * @returns Query result
 */
export function useFetchQuery<TData = unknown>(
  options: QueryFetchOptions<TData>
) {
  const { url, config, queryOptions, mockData, onSuccess, onError } = options;

  return useQuery<TData, AxiosError>(
    [url, config], // Query key
    async () => {
      try {
        const response = await axios({
          url,
          method: 'GET',
          ...config,
          headers: {
            ...config?.headers,
            'Authorization': localStorage.getItem('token') 
              ? `Bearer ${localStorage.getItem('token')}` 
              : undefined
          }
        });

        // Handle API wrapper format if it exists
        if (response.data && typeof response.data === 'object' && 'data' in response.data) {
          return (response.data as ApiResponse<TData>).data as TData;
        }

        return response.data as TData;
      } catch (error) {
        console.error(`Error fetching from ${url}:`, error);
        
        // Use mock data if provided and API failed
        if (mockData) {
          console.log('Falling back to mock data');
          return mockData();
        }
        
        throw error;
      }
    },
    {
      onSuccess,
      onError,
      ...queryOptions
    }
  );
}

/**
 * Hook for making mutation requests (POST, PUT, PATCH, DELETE) with React Query
 * @param options - Options for the mutation
 * @returns Mutation result
 */
export function useFetchMutation<TData = unknown, TVariables = unknown>(
  options: MutationFetchOptions<TData, TVariables>
) {
  const { url, method = 'POST', config, mutationOptions, mockData } = options;

  return useMutation<TData, AxiosError, TVariables>(
    async (variables) => {
      try {
        const response = await axios({
          url,
          method,
          data: variables,
          ...config,
          headers: {
            ...config?.headers,
            'Authorization': localStorage.getItem('token') 
              ? `Bearer ${localStorage.getItem('token')}` 
              : undefined
          }
        });

        // Handle API wrapper format if it exists
        if (response.data && typeof response.data === 'object' && 'data' in response.data) {
          return (response.data as ApiResponse<TData>).data as TData;
        }

        return response.data as TData;
      } catch (error) {
        console.error(`Error in ${method} request to ${url}:`, error);
        
        // Use mock data if provided and API failed
        if (mockData) {
          console.log('Falling back to mock data');
          return mockData(variables);
        }
        
        throw error;
      }
    },
    mutationOptions
  );
}

/**
 * Hook for making prefetch queries
 * @param queryClient - The React Query client
 * @param options - Options for the prefetch
 */
export function usePrefetch<TData = unknown>(
  options: QueryFetchOptions<TData>
) {
  const { url, config, queryOptions, mockData } = options;

  const queryKey = [url, config];
  const queryFn = async () => {
    try {
      const response = await axios({
        url,
        method: 'GET',
        ...config,
        headers: {
          ...config?.headers,
          'Authorization': localStorage.getItem('token') 
            ? `Bearer ${localStorage.getItem('token')}` 
            : undefined
        }
      });

      // Handle API wrapper format if it exists
      if (response.data && typeof response.data === 'object' && 'data' in response.data) {
        return (response.data as ApiResponse<TData>).data as TData;
      }

      return response.data as TData;
    } catch (error) {
      console.error(`Error prefetching from ${url}:`, error);
      
      // Use mock data if provided and API failed
      if (mockData) {
        console.log('Falling back to mock data for prefetch');
        return mockData();
      }
      
      throw error;
    }
  };

  return { queryKey, queryFn, options: queryOptions };
}