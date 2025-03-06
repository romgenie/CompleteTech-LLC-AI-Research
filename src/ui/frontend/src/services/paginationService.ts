import { PaginatedResponse } from '../types';
import { usePaginatedQuery } from '../hooks/useQueryFetch';
import { AxiosRequestConfig } from 'axios';

/**
 * Configuration options for paginated API endpoints
 */
export interface PaginationOptions {
  /** Initial page to load */
  initialPage?: number;
  /** Number of items per page */
  initialPageSize?: number;
  /** Default sort field */
  sortField?: string;
  /** Default sort direction */
  sortDirection?: 'asc' | 'desc';
  /** Additional API request configuration */
  requestConfig?: AxiosRequestConfig;
}

/**
 * Service for handling paginated data from API endpoints
 */
export const paginationService = {
  /**
   * Generate pagination params for API requests
   * 
   * @param page - Current page number
   * @param pageSize - Number of items per page
   * @param sortField - Field to sort by
   * @param sortDirection - Sort direction
   * @returns Object with pagination parameters
   */
  getPaginationParams(
    page: number = 1, 
    pageSize: number = 10,
    sortField?: string,
    sortDirection?: 'asc' | 'desc'
  ): Record<string, any> {
    const params: Record<string, any> = {
      page,
      pageSize,
    };

    // Add sorting parameters if provided
    if (sortField) {
      params.sortField = sortField;
      params.sortDirection = sortDirection || 'asc';
    }

    return params;
  },

  /**
   * Get paginated research data
   */
  useResearchData(options: PaginationOptions = {}) {
    const { 
      initialPage = 1,
      initialPageSize = 10,
      sortField,
      sortDirection = 'asc',
      requestConfig
    } = options;

    // Build config with pagination params
    const config: AxiosRequestConfig = {
      ...requestConfig,
      params: {
        ...requestConfig?.params,
        ...this.getPaginationParams(initialPage, initialPageSize, sortField, sortDirection)
      }
    };

    return usePaginatedQuery<PaginatedResponse<any>>({
      url: '/research/history',
      config,
      initialPage,
      initialPageSize,
      // Mock data for development or when API fails
      mockData: () => ({
        items: Array.from({ length: initialPageSize }, (_, i) => ({
          id: `mock-${i + (initialPage - 1) * initialPageSize}`,
          query: `Mock research query ${i + (initialPage - 1) * initialPageSize}`,
          timestamp: new Date().toISOString(),
          tags: []
        })),
        total: 100,
        page: initialPage,
        pageSize: initialPageSize,
        totalPages: Math.ceil(100 / initialPageSize)
      })
    });
  },

  /**
   * Get paginated knowledge graph entities
   */
  useKnowledgeGraphEntities(options: PaginationOptions = {}) {
    const { 
      initialPage = 1,
      initialPageSize = 20,
      sortField = 'importance',
      sortDirection = 'desc',
      requestConfig
    } = options;

    const config: AxiosRequestConfig = {
      ...requestConfig,
      params: {
        ...requestConfig?.params,
        ...this.getPaginationParams(initialPage, initialPageSize, sortField, sortDirection)
      }
    };

    return usePaginatedQuery<PaginatedResponse<any>>({
      url: '/knowledge-graph/entities',
      config,
      initialPage,
      initialPageSize,
      mockData: () => ({
        items: Array.from({ length: initialPageSize }, (_, i) => ({
          id: `entity-${i + (initialPage - 1) * initialPageSize}`,
          name: `Entity ${i + (initialPage - 1) * initialPageSize}`,
          type: ['MODEL', 'DATASET', 'ALGORITHM', 'PAPER'][Math.floor(Math.random() * 4)],
          importance: Math.random() * 10,
          properties: {}
        })),
        total: 500,
        page: initialPage,
        pageSize: initialPageSize,
        totalPages: Math.ceil(500 / initialPageSize)
      })
    });
  },

  /**
   * Get paginated tags
   */
  useTags(options: PaginationOptions = {}) {
    const { 
      initialPage = 1,
      initialPageSize = 50,
      sortField = 'name',
      sortDirection = 'asc',
      requestConfig
    } = options;

    const config: AxiosRequestConfig = {
      ...requestConfig,
      params: {
        ...requestConfig?.params,
        ...this.getPaginationParams(initialPage, initialPageSize, sortField, sortDirection)
      }
    };

    return usePaginatedQuery<PaginatedResponse<any>>({
      url: '/tags',
      config,
      initialPage,
      initialPageSize,
      mockData: () => ({
        items: Array.from({ length: initialPageSize }, (_, i) => ({
          id: `tag-${i + (initialPage - 1) * initialPageSize}`,
          name: `Tag ${i + (initialPage - 1) * initialPageSize}`,
          color: '#' + Math.floor(Math.random()*16777215).toString(16),
          count: Math.floor(Math.random() * 50)
        })),
        total: 200,
        page: initialPage,
        pageSize: initialPageSize,
        totalPages: Math.ceil(200 / initialPageSize)
      })
    });
  },

  /**
   * Get paginated research recommendations
   */
  useRecommendations(options: PaginationOptions = {}) {
    const { 
      initialPage = 1,
      initialPageSize = 10,
      sortField = 'confidence',
      sortDirection = 'desc',
      requestConfig
    } = options;

    const config: AxiosRequestConfig = {
      ...requestConfig,
      params: {
        ...requestConfig?.params,
        ...this.getPaginationParams(initialPage, initialPageSize, sortField, sortDirection)
      }
    };

    return usePaginatedQuery<PaginatedResponse<any>>({
      url: '/recommendations',
      config,
      initialPage,
      initialPageSize,
      mockData: () => ({
        items: Array.from({ length: initialPageSize }, (_, i) => ({
          id: `rec-${i + (initialPage - 1) * initialPageSize}`,
          title: `Recommendation ${i + (initialPage - 1) * initialPageSize}`,
          description: `This is a mock recommendation ${i + (initialPage - 1) * initialPageSize}`,
          confidence: Math.random(),
          basedOn: []
        })),
        total: 50,
        page: initialPage,
        pageSize: initialPageSize,
        totalPages: Math.ceil(50 / initialPageSize)
      })
    });
  },

  /**
   * Create a custom paginated query
   */
  createPaginatedQuery<TData = any>(
    url: string,
    options: PaginationOptions = {},
    mockDataGenerator?: (page: number, pageSize: number) => PaginatedResponse<TData>
  ) {
    const { 
      initialPage = 1,
      initialPageSize = 10,
      sortField,
      sortDirection,
      requestConfig
    } = options;

    const config: AxiosRequestConfig = {
      ...requestConfig,
      params: {
        ...requestConfig?.params,
        ...this.getPaginationParams(initialPage, initialPageSize, sortField, sortDirection)
      }
    };

    return usePaginatedQuery<PaginatedResponse<TData>>({
      url,
      config,
      initialPage,
      initialPageSize,
      mockData: mockDataGenerator ? 
        () => mockDataGenerator(initialPage, initialPageSize) :
        undefined
    });
  }
};

export default paginationService;