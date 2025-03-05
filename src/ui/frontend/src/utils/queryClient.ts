import { QueryClient } from '@tanstack/react-query';

/**
 * Configuration for the React Query client
 * This includes caching and retry behavior settings
 */
const queryClientConfig = {
  defaultOptions: {
    queries: {
      // How long data will be considered fresh (in milliseconds)
      staleTime: 1000 * 60 * 5, // 5 minutes
      
      // Whether to retry failed queries
      retry: 1,
      
      // Time to keep data in cache (in milliseconds)
      cacheTime: 1000 * 60 * 30, // 30 minutes
      
      // Refetch when window refocuses?
      refetchOnWindowFocus: false,
      
      // Show cached data while fetching new data
      keepPreviousData: true,
      
      // Get stale data from cache while fetching
      useErrorBoundary: false,
    },
    mutations: {
      // Whether to retry failed mutations
      retry: 0,
      
      // Use error boundary for mutations
      useErrorBoundary: false,
    },
  },
};

/**
 * Create and export the query client with configuration
 */
export const queryClient = new QueryClient(queryClientConfig);