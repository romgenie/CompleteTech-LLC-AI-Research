import { QueryClient, DefaultOptions } from '@tanstack/react-query';

/**
 * Configuration for the React Query client
 * This includes caching and retry behavior settings
 */
const queryClientConfig: { defaultOptions: DefaultOptions } = {
  defaultOptions: {
    queries: {
      // How long data will be considered fresh (in milliseconds)
      staleTime: 1000 * 60 * 5, // 5 minutes
      
      // Whether to retry failed queries
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error.response?.status && error.response.status >= 400 && error.response.status < 500) {
          return false;
        }
        
        // Retry up to 3 times on other errors
        return failureCount < 3;
      },
      
      // Time to keep data in cache (in milliseconds)
      gcTime: 1000 * 60 * 30, // 30 minutes
      
      // Refetch when window refocuses
      refetchOnWindowFocus: true,
      
      // Show cached data while fetching new data
      keepPreviousData: true,
      
      // Refetch on mount when stale
      refetchOnMount: 'always',
      
      // Refetch on reconnect when stale
      refetchOnReconnect: true,
      
      // Use error boundary for queries
      throwOnError: false,
    },
    mutations: {
      // Don't retry mutations
      retry: false,
      
      // Use error boundary for mutations
      throwOnError: false,
    },
  },
};

/**
 * Create and export the query client with configuration
 */
export const queryClient = new QueryClient(queryClientConfig);

export default queryClient;