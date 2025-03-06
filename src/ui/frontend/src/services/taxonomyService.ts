import { Taxonomy, Tag, SharedWith, TagVisibility } from '../types/research';
import apiClient from './apiClient';
import { useFetchQuery, useFetchMutation } from '../hooks/useQueryFetch';

// Base URL for taxonomy endpoints
const TAXONOMY_BASE_URL = '/api/taxonomies';

/**
 * Interface for taxonomy creation data
 */
interface CreateTaxonomyData {
  name: string;
  description?: string;
  visibility: TagVisibility;
  domain?: string;
  rootTagIds?: string[];
}

/**
 * Interface for taxonomy update data
 */
interface UpdateTaxonomyData {
  name?: string;
  description?: string;
  visibility?: TagVisibility;
  domain?: string;
  rootTagIds?: string[];
  version?: string;
}

/**
 * Interface for sharing taxonomy with users or groups
 */
interface ShareTaxonomyData {
  taxonomyId: string;
  sharedWith: SharedWith[];
}

/**
 * Interface for importing taxonomy data
 */
interface ImportTaxonomyData {
  name: string;
  description?: string;
  visibility: TagVisibility;
  data: any; // JSON structure of the taxonomy
  format: 'json' | 'csv' | 'xml' | 'skos';
  mergeStrategy?: 'replace' | 'merge' | 'keepBoth';
}

/**
 * Taxonomy service for managing tag taxonomies
 */
const taxonomyService = {
  /**
   * Get all accessible taxonomies
   * @returns List of taxonomies
   */
  getTaxonomies: async (): Promise<Taxonomy[]> => {
    try {
      return await apiClient.get<Taxonomy[]>(TAXONOMY_BASE_URL);
    } catch (error) {
      console.error('Error fetching taxonomies:', error);
      // Return a default empty array if API fails
      return [];
    }
  },

  /**
   * Get a taxonomy by ID
   * @param id - Taxonomy ID
   * @returns Taxonomy details
   */
  getTaxonomyById: async (id: string): Promise<Taxonomy> => {
    try {
      return await apiClient.get<Taxonomy>(`${TAXONOMY_BASE_URL}/${id}`);
    } catch (error) {
      console.error(`Error fetching taxonomy ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new taxonomy
   * @param data - Taxonomy data
   * @returns Created taxonomy
   */
  createTaxonomy: async (data: CreateTaxonomyData): Promise<Taxonomy> => {
    try {
      return await apiClient.post<Taxonomy>(TAXONOMY_BASE_URL, data);
    } catch (error) {
      console.error('Error creating taxonomy:', error);
      throw error;
    }
  },

  /**
   * Update a taxonomy
   * @param id - Taxonomy ID
   * @param data - Taxonomy data to update
   * @returns Updated taxonomy
   */
  updateTaxonomy: async (id: string, data: UpdateTaxonomyData): Promise<Taxonomy> => {
    try {
      return await apiClient.patch<Taxonomy>(`${TAXONOMY_BASE_URL}/${id}`, data);
    } catch (error) {
      console.error(`Error updating taxonomy ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a taxonomy
   * @param id - Taxonomy ID
   * @returns Success status
   */
  deleteTaxonomy: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`${TAXONOMY_BASE_URL}/${id}`);
    } catch (error) {
      console.error(`Error deleting taxonomy ${id}:`, error);
      throw error;
    }
  },

  /**
   * Share a taxonomy with users or groups
   * @param data - Share data
   * @returns Updated taxonomy
   */
  shareTaxonomy: async (data: ShareTaxonomyData): Promise<Taxonomy> => {
    try {
      return await apiClient.post<Taxonomy>(`${TAXONOMY_BASE_URL}/${data.taxonomyId}/share`, {
        sharedWith: data.sharedWith
      });
    } catch (error) {
      console.error(`Error sharing taxonomy ${data.taxonomyId}:`, error);
      throw error;
    }
  },

  /**
   * Get the tags in a taxonomy
   * @param id - Taxonomy ID
   * @returns List of tags
   */
  getTaxonomyTags: async (id: string): Promise<Tag[]> => {
    try {
      return await apiClient.get<Tag[]>(`${TAXONOMY_BASE_URL}/${id}/tags`);
    } catch (error) {
      console.error(`Error fetching tags for taxonomy ${id}:`, error);
      return [];
    }
  },

  /**
   * Add a tag to a taxonomy
   * @param taxonomyId - Taxonomy ID
   * @param tagId - Tag ID
   * @returns Updated taxonomy
   */
  addTagToTaxonomy: async (taxonomyId: string, tagId: string): Promise<Taxonomy> => {
    try {
      return await apiClient.post<Taxonomy>(`${TAXONOMY_BASE_URL}/${taxonomyId}/tags`, {
        tagId
      });
    } catch (error) {
      console.error(`Error adding tag ${tagId} to taxonomy ${taxonomyId}:`, error);
      throw error;
    }
  },

  /**
   * Remove a tag from a taxonomy
   * @param taxonomyId - Taxonomy ID
   * @param tagId - Tag ID
   * @returns Updated taxonomy
   */
  removeTagFromTaxonomy: async (taxonomyId: string, tagId: string): Promise<Taxonomy> => {
    try {
      return await apiClient.delete<Taxonomy>(`${TAXONOMY_BASE_URL}/${taxonomyId}/tags/${tagId}`);
    } catch (error) {
      console.error(`Error removing tag ${tagId} from taxonomy ${taxonomyId}:`, error);
      throw error;
    }
  },

  /**
   * Import a taxonomy from external data
   * @param data - Import data
   * @returns Created taxonomy
   */
  importTaxonomy: async (data: ImportTaxonomyData): Promise<Taxonomy> => {
    try {
      return await apiClient.post<Taxonomy>(`${TAXONOMY_BASE_URL}/import`, data);
    } catch (error) {
      console.error('Error importing taxonomy:', error);
      throw error;
    }
  },

  /**
   * Export a taxonomy to a specific format
   * @param id - Taxonomy ID
   * @param format - Export format
   * @returns Taxonomy data in specified format
   */
  exportTaxonomy: async (id: string, format: 'json' | 'csv' | 'xml' | 'skos'): Promise<any> => {
    try {
      return await apiClient.get<any>(`${TAXONOMY_BASE_URL}/${id}/export`, {
        params: { format }
      });
    } catch (error) {
      console.error(`Error exporting taxonomy ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get popular/community taxonomies
   * @returns List of popular taxonomies
   */
  getPopularTaxonomies: async (): Promise<Taxonomy[]> => {
    try {
      return await apiClient.get<Taxonomy[]>(`${TAXONOMY_BASE_URL}/popular`);
    } catch (error) {
      console.error('Error fetching popular taxonomies:', error);
      return [];
    }
  },

  /**
   * Get official/system taxonomies
   * @returns List of official taxonomies
   */
  getOfficialTaxonomies: async (): Promise<Taxonomy[]> => {
    try {
      return await apiClient.get<Taxonomy[]>(`${TAXONOMY_BASE_URL}/official`);
    } catch (error) {
      console.error('Error fetching official taxonomies:', error);
      return [];
    }
  }
};

/**
 * Hook for fetching all taxonomies with React Query
 * @returns Query result with taxonomies
 */
export function useTaxonomies() {
  return useFetchQuery<Taxonomy[]>({
    url: TAXONOMY_BASE_URL,
    queryOptions: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes
    },
    mockData: () => {
      // Generate mock taxonomies if API fails
      return [
        {
          id: 'tax-1',
          name: 'Research Topics',
          description: 'Standard taxonomy for organizing research topics',
          owner: '1', // Admin user
          visibility: 'public',
          rootTags: ['tag-1', 'tag-5'],
          isOfficial: true,
          domain: 'research',
          createdAt: '2023-01-01T00:00:00Z',
          version: '1.0'
        },
        {
          id: 'tax-2',
          name: 'AI Research Framework',
          description: 'Specialized taxonomy for AI research topics',
          owner: '2', // Researcher user
          visibility: 'shared',
          rootTags: ['tag-1'],
          isOfficial: false,
          domain: 'artificial intelligence',
          createdAt: '2023-02-15T00:00:00Z',
          version: '0.5'
        }
      ];
    }
  });
}

/**
 * Hook for fetching taxonomy by ID with React Query
 * @param id Taxonomy ID
 * @returns Query result with taxonomy
 */
export function useTaxonomy(id: string) {
  return useFetchQuery<Taxonomy>({
    url: `${TAXONOMY_BASE_URL}/${id}`,
    queryOptions: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes
      enabled: !!id // Only run query if ID is provided
    }
  });
}

/**
 * Hook for creating a new taxonomy with React Query
 * @returns Mutation function and result
 */
export function useCreateTaxonomy() {
  return useFetchMutation<Taxonomy, CreateTaxonomyData>({
    url: TAXONOMY_BASE_URL,
    method: 'POST'
  });
}

/**
 * Hook for updating a taxonomy with React Query
 * @returns Mutation function and result
 */
export function useUpdateTaxonomy() {
  return useFetchMutation<Taxonomy, { id: string, data: UpdateTaxonomyData }>({
    url: `${TAXONOMY_BASE_URL}/:id`,
    method: 'PATCH',
    // Dynamically set the URL based on the taxonomy ID
    config: {
      transformRequest: [(data: { id: string, data: UpdateTaxonomyData }) => {
        // Extract the actual data to send
        return JSON.stringify(data.data);
      }]
    }
  });
}

/**
 * Hook for deleting a taxonomy with React Query
 * @returns Mutation function and result
 */
export function useDeleteTaxonomy() {
  return useFetchMutation<void, string>({
    url: `${TAXONOMY_BASE_URL}/:id`,
    method: 'DELETE',
    // Dynamically set the URL based on the taxonomy ID
    config: {
      transformRequest: [(id: string) => {
        // No body needed for DELETE
        return undefined;
      }]
    }
  });
}

/**
 * Hook for sharing a taxonomy with React Query
 * @returns Mutation function and result
 */
export function useShareTaxonomy() {
  return useFetchMutation<Taxonomy, ShareTaxonomyData>({
    url: `${TAXONOMY_BASE_URL}/:taxonomyId/share`,
    method: 'POST',
    // Dynamically set the URL based on the taxonomy ID
    config: {
      transformRequest: [(data: ShareTaxonomyData) => {
        // Extract the actual data to send
        return JSON.stringify({ sharedWith: data.sharedWith });
      }]
    }
  });
}

export default taxonomyService;