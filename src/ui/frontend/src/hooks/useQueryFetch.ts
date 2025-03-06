import React from 'react';
import { useQuery, useMutation, UseQueryOptions, UseMutationOptions, useQueryClient } from '@tanstack/react-query';
import { AxiosError, AxiosRequestConfig } from 'axios';
import { ApiResponse } from '../types';
import apiClient from '../services/apiClient';

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
  enableWebSocket?: boolean;
  wsMessageType?: string;
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
  optimisticUpdate?: {
    queryKey: unknown[];
    updateFn: (oldData: any, variables: TVariables) => any;
  };
};

/**
 * Hook for making GET requests with React Query
 * Uses the ApiClient and supports real-time updates via WebSockets
 * 
 * @param options - Options for the query
 * @returns Query result
 */
export function useFetchQuery<TData = unknown>(
  options: QueryFetchOptions<TData>
) {
  const { 
    url, 
    config, 
    queryOptions, 
    mockData, 
    onSuccess, 
    onError,
    enableWebSocket = false,
    wsMessageType
  } = options;

  const queryClient = useQueryClient();
  const queryKey = [url, config]; // Query key based on URL and config

  const query = useQuery<TData, AxiosError>({
    queryKey,
    queryFn: async () => {
      try {
        const data = await apiClient.get<TData>(url, config);
        return data;
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
    ...queryOptions,
    ...(onSuccess ? { onSuccess } : {}),
    ...(onError ? { onError } : {})
  });

  // Set up WebSocket subscription if enabled
  React.useEffect(() => {
    if (enableWebSocket && wsMessageType) {
      // Get WebSocket URL from environment or use default
      const wsUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';
      
      // Initialize WebSocket if not already connected
      apiClient.connectWebSocket(wsUrl);
      
      // Subscribe to real-time updates for this query
      const unsubscribe = apiClient.subscribeToWebSocket<TData>(wsMessageType, (wsData) => {
        // Update query data when we receive WebSocket message
        queryClient.setQueryData(queryKey, wsData);
      });
      
      // Clean up subscription when component unmounts
      return () => {
        unsubscribe();
      };
    }
  }, [enableWebSocket, wsMessageType, queryClient, queryKey]);

  return query;
}

/**
 * Hook for making mutating requests (POST, PUT, PATCH, DELETE) with React Query
 * 
 * @param options - Options for the mutation
 * @returns Mutation result
 */
export function useFetchMutation<TData = unknown, TVariables = unknown>(
  options: MutationFetchOptions<TData, TVariables>
) {
  const { 
    url, 
    method = 'POST', 
    config, 
    mutationOptions, 
    mockData,
    optimisticUpdate
  } = options;

  const queryClient = useQueryClient();

  return useMutation<TData, AxiosError, TVariables>({
    mutationFn: async (variables) => {
      try {
        let response: TData;
        
        // Choose appropriate method based on the HTTP verb
        switch (method) {
          case 'POST':
            response = await apiClient.post<TData, TVariables>(url, variables, config);
            break;
          case 'PUT':
            response = await apiClient.put<TData, TVariables>(url, variables, config);
            break;
          case 'PATCH':
            response = await apiClient.patch<TData, TVariables>(url, variables, config);
            break;
          case 'DELETE':
            response = await apiClient.delete<TData>(url, config);
            break;
          default:
            throw new Error(`Unsupported HTTP method: ${method}`);
        }
        
        return response;
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
    onMutate: async (variables) => {
      if (optimisticUpdate) {
        // Cancel any outgoing refetches to avoid overwriting optimistic update
        await queryClient.cancelQueries({ queryKey: optimisticUpdate.queryKey });
        
        // Snapshot the previous value
        const previousData = queryClient.getQueryData(optimisticUpdate.queryKey);
        
        // Optimistically update to the new value
        queryClient.setQueryData(optimisticUpdate.queryKey, (old) => 
          optimisticUpdate.updateFn(old, variables)
        );
        
        // Return a context object with the snapshotted value
        return { previousData };
      }
    },
    onError: (err, variables, context: any) => {
      if (optimisticUpdate && context && context.previousData) {
        queryClient.setQueryData(optimisticUpdate.queryKey, context.previousData);
      }
    },
    onSettled: () => {
      if (optimisticUpdate) {
        queryClient.invalidateQueries({ queryKey: optimisticUpdate.queryKey });
      }
    },
    ...(mutationOptions || {})
  });
}

/**
 * Hook for prefetching query data
 * @param options - Options for the prefetch
 * @returns Prefetch functions and metadata
 */
export function usePrefetch<TData = unknown>(
  options: QueryFetchOptions<TData>
) {
  const { url, config, queryOptions, mockData } = options;
  const queryClient = useQueryClient();
  
  const queryKey = [url, config];
  
  // Define query function for prefetching
  const queryFn = async () => {
    try {
      return await apiClient.get<TData>(url, config);
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
  
  // Return functions and data
  return { 
    queryKey, 
    queryFn, 
    options: queryOptions,
    prefetch: () => queryClient.prefetchQuery({ 
      queryKey,
      queryFn,
      ...queryOptions 
    })
  };
}

/**
 * Hook for infinite query (pagination, load more, etc.)
 * @param options - Options for the infinite query
 * @returns Infinite query result
 */
export function useInfiniteQuery<TData = unknown>(
  options: QueryFetchOptions<TData> & {
    getNextPageParam: (lastPage: any, allPages: any[]) => any | undefined;
  }
) {
  const { 
    url, 
    config, 
    queryOptions, 
    mockData, 
    onSuccess, 
    onError,
    getNextPageParam
  } = options;
  
  const queryClient = useQueryClient();

  // Note: For TanStack Query v5, useInfiniteQuery should be used directly
  // This is a simplified implementation for compatibility
  return useQuery<TData, AxiosError>({
    queryKey: [url, config],
    queryFn: async ({ pageParam = 1 }) => {
      try {
        // Add page parameter to request config
        const paginatedConfig = {
          ...config,
          params: {
            ...config?.params,
            page: pageParam
          }
        };
        
        const data = await apiClient.get<TData>(url, paginatedConfig);
        return data;
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
    ...queryOptions,
    ...(onSuccess ? { onSuccess } : {})
    // Note: getNextPageParam should be used with useInfiniteQuery, not useQuery
  });
}

/**
 * Hook for paginated queries with proper server-side pagination support
 * @param options - Options for the paginated query
 * @returns Paginated query result with pagination controls
 */
export function usePaginatedQuery<TData = unknown>(
  options: QueryFetchOptions<TData> & {
    initialPage?: number;
    initialPageSize?: number;
  }
) {
  const { 
    url, 
    config, 
    queryOptions, 
    mockData, 
    onSuccess, 
    onError,
    initialPage = 1,
    initialPageSize = 10
  } = options;

  const [page, setPage] = React.useState(initialPage);
  const [pageSize, setPageSize] = React.useState(initialPageSize);
  const queryClient = useQueryClient();

  // Build query key that includes pagination parameters
  const queryKey = [url, { ...config, page, pageSize }];

  // The main query
  const query = useQuery<TData, AxiosError>({
    queryKey,
    queryFn: async () => {
      try {
        // Add pagination parameters to request config
        const paginatedConfig = {
          ...config,
          params: {
            ...config?.params,
            page,
            pageSize,
            limit: pageSize
          }
        };
        
        const data = await apiClient.get<TData>(url, paginatedConfig);
        return data;
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
    ...queryOptions,
    ...(onSuccess ? { onSuccess } : {}),
    ...(onError ? { onError } : {})
  });

  // Prefetch next page when current page is successfully loaded
  React.useEffect(() => {
    if (query.data) {
      const nextPage = page + 1;
      
      queryClient.prefetchQuery({
        queryKey: [url, { ...config, page: nextPage, pageSize }],
        queryFn: async () => {
          try {
            const paginatedConfig = {
              ...config,
              params: {
                ...config?.params,
                page: nextPage,
                pageSize,
                limit: pageSize
              }
            };
            
            return await apiClient.get<TData>(url, paginatedConfig);
          } catch (error) {
            console.error(`Error prefetching next page from ${url}:`, error);
            
            if (mockData) {
              return mockData();
            }
            
            throw error;
          }
        },
        ...queryOptions
      });
    }
  }, [query.data, page, pageSize, url, config, queryClient, queryOptions, mockData]);

  // Pagination control functions
  const goToPage = React.useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  const nextPage = React.useCallback(() => {
    setPage(old => old + 1);
  }, []);

  const previousPage = React.useCallback(() => {
    setPage(old => Math.max(old - 1, 1));
  }, []);

  const setPageSizeAndReset = React.useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1); // Reset to first page when changing page size
  }, []);

  // Return query result with pagination controls
  return {
    ...query,
    pagination: {
      page,
      pageSize,
      goToPage,
      nextPage,
      previousPage,
      setPageSize: setPageSizeAndReset
    }
  };
}