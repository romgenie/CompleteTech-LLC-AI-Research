import { Tag, TagVisibility, SharedWith, TagSuggestion, TagUsageStats, TagConflict } from '../types/research';
import apiClient from './apiClient';
import { useFetchQuery, useFetchMutation } from '../hooks/useQueryFetch';
import { mockTags, mockTagStats, mockTagConflicts } from './mockData/mockTags';

// Base URL for tag endpoints
const TAG_BASE_URL = '/api/tags';

/**
 * Interface for tag creation data
 */
interface CreateTagData {
  name: string;
  color?: string;
  description?: string;
  parentId?: string | null;
  visibility?: TagVisibility;
  taxonomyId?: string;
}

/**
 * Interface for tag update data
 */
interface UpdateTagData {
  name?: string;
  color?: string;
  description?: string;
  parentId?: string | null;
  visibility?: TagVisibility;
  taxonomyId?: string;
}

/**
 * Interface for tag merge data
 */
interface MergeTagsData {
  sourceTagId: string;
  targetTagId: string;
}

/**
 * Interface for moving a tag in the hierarchy
 */
interface MoveTagData {
  tagId: string;
  newParentId: string | null;
}

/**
 * Interface for tag inheritance rule
 */
interface TagInheritanceRule {
  tagId: string;
  inheritedProperties: ('color' | 'description' | 'filters')[];
  applyToChildren: boolean;
}

/**
 * Interface for sharing tag data
 */
interface ShareTagData {
  tagId: string;
  sharedWith: SharedWith[];
}

/**
 * Interface for tag suggestion data
 */
interface CreateTagSuggestionData {
  name: string;
  parentId?: string;
  tagId?: string;
  taxonomyId?: string;
  reason: 'similarity' | 'popularity' | 'cooccurrence' | 'system' | 'user';
  confidence: number;
}

/**
 * Interface for tag conflict resolution data
 */
interface ResolveTagConflictData {
  conflictId: string;
  selectedOptionId: string;
}

/**
 * Tag service for managing research tags
 */
const tagsService = {
  /**
   * Get all tags
   * @returns List of tags
   */
  getTags: async (): Promise<Tag[]> => {
    try {
      return await apiClient.get<Tag[]>(TAG_BASE_URL);
    } catch (error) {
      console.error('Error fetching tags:', error);
      // Return a default empty array if API fails
      return [];
    }
  },

  /**
   * Get a tag by ID
   * @param id - Tag ID
   * @returns Tag details
   */
  getTagById: async (id: string): Promise<Tag> => {
    try {
      return await apiClient.get<Tag>(`${TAG_BASE_URL}/${id}`);
    } catch (error) {
      console.error(`Error fetching tag ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new tag
   * @param tagData - Tag data
   * @returns Created tag
   */
  createTag: async (tagData: CreateTagData): Promise<Tag> => {
    try {
      return await apiClient.post<Tag>(TAG_BASE_URL, tagData);
    } catch (error) {
      console.error('Error creating tag:', error);
      throw error;
    }
  },

  /**
   * Update a tag
   * @param id - Tag ID
   * @param tagData - Tag data to update
   * @returns Updated tag
   */
  updateTag: async (id: string, tagData: UpdateTagData): Promise<Tag> => {
    try {
      return await apiClient.patch<Tag>(`${TAG_BASE_URL}/${id}`, tagData);
    } catch (error) {
      console.error(`Error updating tag ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a tag
   * @param id - Tag ID
   * @returns Success status
   */
  deleteTag: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`${TAG_BASE_URL}/${id}`);
    } catch (error) {
      console.error(`Error deleting tag ${id}:`, error);
      throw error;
    }
  },

  /**
   * Merge two tags
   * @param mergeData - Merge data
   * @returns Updated target tag
   */
  mergeTags: async (mergeData: MergeTagsData): Promise<Tag> => {
    try {
      return await apiClient.post<Tag>(`${TAG_BASE_URL}/merge`, mergeData);
    } catch (error) {
      console.error('Error merging tags:', error);
      throw error;
    }
  },

  /**
   * Get items tagged with a specific tag
   * @param id - Tag ID
   * @returns Tagged items
   */
  getTaggedItems: async (id: string): Promise<any[]> => {
    try {
      return await apiClient.get<any[]>(`${TAG_BASE_URL}/${id}/items`);
    } catch (error) {
      console.error(`Error fetching items with tag ${id}:`, error);
      return [];
    }
  },

  /**
   * Add a tag to an item
   * @param tagId - Tag ID
   * @param itemId - Item ID
   * @param itemType - Type of item (e.g., 'query', 'result')
   * @returns Success status
   */
  addTagToItem: async (tagId: string, itemId: string, itemType: string): Promise<void> => {
    try {
      await apiClient.post(`${TAG_BASE_URL}/${tagId}/items`, {
        itemId,
        itemType
      });
    } catch (error) {
      console.error(`Error adding tag ${tagId} to item ${itemId}:`, error);
      throw error;
    }
  },

  /**
   * Remove a tag from an item
   * @param tagId - Tag ID
   * @param itemId - Item ID
   * @returns Success status
   */
  removeTagFromItem: async (tagId: string, itemId: string): Promise<void> => {
    try {
      await apiClient.delete(`${TAG_BASE_URL}/${tagId}/items/${itemId}`);
    } catch (error) {
      console.error(`Error removing tag ${tagId} from item ${itemId}:`, error);
      throw error;
    }
  },

  /**
   * Get the tag hierarchy
   * @returns Hierarchical structure of tags
   */
  getTagHierarchy: async (): Promise<Tag[]> => {
    try {
      return await apiClient.get<Tag[]>(`${TAG_BASE_URL}/hierarchy`);
    } catch (error) {
      console.error('Error fetching tag hierarchy:', error);
      return [];
    }
  },

  /**
   * Move a tag in the hierarchy
   * @param moveData - Move data with tag ID and new parent ID
   * @returns Updated tag
   */
  moveTag: async (moveData: MoveTagData): Promise<Tag> => {
    try {
      return await apiClient.post<Tag>(`${TAG_BASE_URL}/${moveData.tagId}/move`, {
        newParentId: moveData.newParentId
      });
    } catch (error) {
      console.error(`Error moving tag ${moveData.tagId}:`, error);
      throw error;
    }
  },

  /**
   * Get child tags of a parent tag
   * @param parentId - Parent tag ID
   * @returns List of child tags
   */
  getChildTags: async (parentId: string): Promise<Tag[]> => {
    try {
      return await apiClient.get<Tag[]>(`${TAG_BASE_URL}/${parentId}/children`);
    } catch (error) {
      console.error(`Error fetching children of tag ${parentId}:`, error);
      return [];
    }
  },

  /**
   * Set tag inheritance rules
   * @param tagId - Tag ID
   * @param inheritanceRule - Inheritance rule configuration
   * @returns Updated tag
   */
  setTagInheritance: async (tagId: string, inheritanceRule: TagInheritanceRule): Promise<Tag> => {
    try {
      return await apiClient.post<Tag>(`${TAG_BASE_URL}/${tagId}/inheritance`, inheritanceRule);
    } catch (error) {
      console.error(`Error setting inheritance for tag ${tagId}:`, error);
      throw error;
    }
  },

  /**
   * Bulk update tags (for hierarchy reorganization)
   * @param tags - Array of tags to update
   * @returns Updated tags
   */
  bulkUpdateTags: async (tags: Partial<Tag>[]): Promise<Tag[]> => {
    try {
      return await apiClient.patch<Tag[]>(`${TAG_BASE_URL}/bulk`, { tags });
    } catch (error) {
      console.error('Error bulk updating tags:', error);
      throw error;
    }
  },

  /**
   * Share a tag with users or groups
   * @param shareData - Share data with tag ID and recipients
   * @returns Updated tag
   */
  shareTag: async (shareData: ShareTagData): Promise<Tag> => {
    try {
      return await apiClient.post<Tag>(`${TAG_BASE_URL}/${shareData.tagId}/share`, {
        sharedWith: shareData.sharedWith
      });
    } catch (error) {
      console.error(`Error sharing tag ${shareData.tagId}:`, error);
      throw error;
    }
  },

  /**
   * Get suggested tags based on user history and context
   * @param query - Optional search term to filter suggestions
   * @param context - Optional context (item ID, content snippet) for targeted suggestions
   * @returns List of tag suggestions
   */
  getTagSuggestions: async (query?: string, context?: string): Promise<TagSuggestion[]> => {
    try {
      return await apiClient.get<TagSuggestion[]>(`${TAG_BASE_URL}/suggestions`, {
        params: { query, context }
      });
    } catch (error) {
      console.error('Error fetching tag suggestions:', error);
      return [];
    }
  },

  /**
   * Create a new tag suggestion
   * @param data - Suggestion data
   * @returns Created suggestion
   */
  createTagSuggestion: async (data: CreateTagSuggestionData): Promise<TagSuggestion> => {
    try {
      return await apiClient.post<TagSuggestion>(`${TAG_BASE_URL}/suggestions`, data);
    } catch (error) {
      console.error('Error creating tag suggestion:', error);
      throw error;
    }
  },

  /**
   * Accept a tag suggestion
   * @param id - Suggestion ID
   * @returns Created or updated tag
   */
  acceptTagSuggestion: async (id: string): Promise<Tag> => {
    try {
      return await apiClient.post<Tag>(`${TAG_BASE_URL}/suggestions/${id}/accept`);
    } catch (error) {
      console.error(`Error accepting tag suggestion ${id}:`, error);
      throw error;
    }
  },

  /**
   * Reject a tag suggestion
   * @param id - Suggestion ID
   * @returns Success status
   */
  rejectTagSuggestion: async (id: string): Promise<void> => {
    try {
      await apiClient.post(`${TAG_BASE_URL}/suggestions/${id}/reject`);
    } catch (error) {
      console.error(`Error rejecting tag suggestion ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get community usage statistics for a tag
   * @param id - Tag ID
   * @returns Usage statistics
   */
  getTagUsageStats: async (id: string): Promise<TagUsageStats> => {
    try {
      return await apiClient.get<TagUsageStats>(`${TAG_BASE_URL}/${id}/stats`);
    } catch (error) {
      console.error(`Error fetching stats for tag ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get popular tags across all users
   * @param limit - Maximum number of tags to return
   * @returns List of popular tags with usage statistics
   */
  getPopularTags: async (limit: number = 20): Promise<Tag[]> => {
    try {
      return await apiClient.get<Tag[]>(`${TAG_BASE_URL}/popular`, {
        params: { limit }
      });
    } catch (error) {
      console.error('Error fetching popular tags:', error);
      return [];
    }
  },

  /**
   * Get tag conflicts that need resolution
   * @returns List of unresolved tag conflicts
   */
  getTagConflicts: async (): Promise<TagConflict[]> => {
    try {
      return await apiClient.get<TagConflict[]>(`${TAG_BASE_URL}/conflicts`);
    } catch (error) {
      console.error('Error fetching tag conflicts:', error);
      return [];
    }
  },

  /**
   * Resolve a tag conflict
   * @param data - Resolution data with conflict ID and selected option
   * @returns Updated tag(s) after conflict resolution
   */
  resolveTagConflict: async (data: ResolveTagConflictData): Promise<Tag[]> => {
    try {
      return await apiClient.post<Tag[]>(`${TAG_BASE_URL}/conflicts/${data.conflictId}/resolve`, {
        selectedOptionId: data.selectedOptionId
      });
    } catch (error) {
      console.error(`Error resolving tag conflict ${data.conflictId}:`, error);
      throw error;
    }
  },

  /**
   * Get tags shared with the current user
   * @returns List of shared tags
   */
  getSharedTags: async (): Promise<Tag[]> => {
    try {
      return await apiClient.get<Tag[]>(`${TAG_BASE_URL}/shared`);
    } catch (error) {
      console.error('Error fetching shared tags:', error);
      return [];
    }
  },

  /**
   * Get global/public tags
   * @returns List of global tags
   */
  getGlobalTags: async (): Promise<Tag[]> => {
    try {
      return await apiClient.get<Tag[]>(`${TAG_BASE_URL}/global`);
    } catch (error) {
      console.error('Error fetching global tags:', error);
      return [];
    }
  }
};

/**
 * Hook for fetching all tags with React Query
 * @returns Query result with tags
 */
export function useTags() {
  return useFetchQuery<Tag[]>({
    url: TAG_BASE_URL,
    queryOptions: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
    },
    mockData: () => {
      // Generate mock tags if API fails
      return [
        { id: 'tag-1', name: 'Machine Learning', color: '#2196f3', count: 37, parentId: null, level: 0 },
        { id: 'tag-2', name: 'NLP', color: '#f44336', count: 24, parentId: 'tag-1', level: 1, path: 'Machine Learning/NLP' },
        { id: 'tag-3', name: 'Neural Networks', color: '#4caf50', count: 18, parentId: 'tag-1', level: 1, path: 'Machine Learning/Neural Networks' },
        { id: 'tag-4', name: 'Transformers', color: '#9c27b0', count: 42, parentId: 'tag-2', level: 2, path: 'Machine Learning/NLP/Transformers' },
        { id: 'tag-5', name: 'Computer Vision', color: '#ff9800', count: 15, parentId: null, level: 0 },
        { id: 'tag-6', name: 'LLM', color: '#607d8b', count: 35, parentId: 'tag-2', level: 2, path: 'Machine Learning/NLP/LLM' },
        { id: 'tag-7', name: 'GPT', color: '#e91e63', count: 22, parentId: 'tag-6', level: 3, path: 'Machine Learning/NLP/LLM/GPT' },
        { id: 'tag-8', name: 'BERT', color: '#cddc39', count: 12, parentId: 'tag-4', level: 3, path: 'Machine Learning/NLP/Transformers/BERT' },
      ];
    }
  });
}

/**
 * Hook for fetching hierarchical tag structure
 * @returns Query result with hierarchical tags
 */
export function useTagHierarchy() {
  return useFetchQuery<Tag[]>({
    url: `${TAG_BASE_URL}/hierarchy`,
    queryOptions: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
    },
    mockData: () => {
      // Generate mock hierarchical tags if API fails
      return [
        { 
          id: 'tag-1', 
          name: 'Machine Learning', 
          color: '#2196f3', 
          count: 37, 
          parentId: null, 
          level: 0,
          children: ['tag-2', 'tag-3'] 
        },
        { 
          id: 'tag-5', 
          name: 'Computer Vision', 
          color: '#ff9800', 
          count: 15, 
          parentId: null, 
          level: 0,
          children: [] 
        },
      ];
    }
  });
}

/**
 * Hook for creating a new tag with React Query
 * @returns Mutation function and result
 */
export function useCreateTag() {
  return useFetchMutation<Tag, CreateTagData>({
    url: TAG_BASE_URL,
    method: 'POST',
    // Optimistic update to immediately show the new tag
    optimisticUpdate: {
      queryKey: [TAG_BASE_URL],
      updateFn: (oldData: Tag[] = [], newTag: CreateTagData) => {
        // Generate a temporary ID until the real one comes back
        const tempId = `temp-${Date.now()}`;
        const tempTag: Tag = {
          id: tempId,
          name: newTag.name,
          color: newTag.color || '#2196f3',
          description: newTag.description,
          count: 0
        };
        return [...oldData, tempTag];
      }
    }
  });
}

/**
 * Hook for updating a tag with React Query
 * @returns Mutation function and result
 */
export function useUpdateTag() {
  return useFetchMutation<Tag, { id: string, data: UpdateTagData }>({
    url: `${TAG_BASE_URL}/:id`,
    method: 'PATCH',
    // Dynamically set the URL based on the tag ID
    config: {
      transformRequest: [(data: { id: string, data: UpdateTagData }) => {
        // Extract the actual data to send
        return JSON.stringify(data.data);
      }]
    },
    // Optimistic update to immediately show the updated tag
    optimisticUpdate: {
      queryKey: [TAG_BASE_URL],
      updateFn: (oldData: Tag[] = [], params: { id: string, data: UpdateTagData }) => {
        return oldData.map(tag => 
          tag.id === params.id 
            ? { ...tag, ...params.data } 
            : tag
        );
      }
    }
  });
}

/**
 * Hook for deleting a tag with React Query
 * @returns Mutation function and result
 */
export function useDeleteTag() {
  return useFetchMutation<void, string>({
    url: `${TAG_BASE_URL}/:id`,
    method: 'DELETE',
    // Dynamically set the URL based on the tag ID
    config: {
      transformRequest: [(id: string) => {
        // No body needed for DELETE
        return undefined;
      }]
    },
    // Optimistic update to immediately remove the tag
    optimisticUpdate: {
      queryKey: [TAG_BASE_URL],
      updateFn: (oldData: Tag[] = [], id: string) => {
        return oldData.filter(tag => tag.id !== id);
      }
    }
  });
}

/**
 * Hook for merging tags with React Query
 * @returns Mutation function and result
 */
export function useMergeTags() {
  return useFetchMutation<Tag, MergeTagsData>({
    url: `${TAG_BASE_URL}/merge`,
    method: 'POST',
    // Optimistic update to show the merged tags
    optimisticUpdate: {
      queryKey: [TAG_BASE_URL],
      updateFn: (oldData: Tag[] = [], mergeData: MergeTagsData) => {
        const sourceTag = oldData.find(tag => tag.id === mergeData.sourceTagId);
        const targetTag = oldData.find(tag => tag.id === mergeData.targetTagId);
        
        if (!sourceTag || !targetTag) return oldData;
        
        // Create a new array without the source tag
        const filteredTags = oldData.filter(tag => tag.id !== mergeData.sourceTagId);
        
        // Update the target tag count
        const updatedTargetTag = {
          ...targetTag,
          count: (targetTag.count || 0) + (sourceTag.count || 0)
        };
        
        // Return updated array
        return filteredTags.map(tag => 
          tag.id === mergeData.targetTagId ? updatedTargetTag : tag
        );
      }
    }
  });
}

/**
 * Hook for moving a tag in the hierarchy
 * @returns Mutation function and result
 */
export function useMoveTag() {
  return useFetchMutation<Tag, MoveTagData>({
    url: `${TAG_BASE_URL}/:tagId/move`,
    method: 'POST',
    config: {
      transformRequest: [(data: MoveTagData) => {
        return JSON.stringify({ newParentId: data.newParentId });
      }]
    },
    optimisticUpdate: {
      queryKey: [TAG_BASE_URL],
      updateFn: (oldData: Tag[] = [], moveData: MoveTagData) => {
        return oldData.map(tag => {
          if (tag.id === moveData.tagId) {
            // Update the moved tag
            const oldParentId = tag.parentId;
            const newLevel = moveData.newParentId === null 
              ? 0 
              : (oldData.find(t => t.id === moveData.newParentId)?.level || 0) + 1;
            
            // If there was a previous parent, remove this tag from its children
            if (oldParentId) {
              const oldParent = oldData.find(t => t.id === oldParentId);
              if (oldParent && oldParent.children) {
                const updatedChildren = oldParent.children.filter(id => id !== tag.id);
                const updatedOldParent = { ...oldParent, children: updatedChildren };
                oldData = oldData.map(t => t.id === oldParentId ? updatedOldParent : t);
              }
            }
            
            // If there's a new parent, add this tag to its children
            if (moveData.newParentId) {
              const newParent = oldData.find(t => t.id === moveData.newParentId);
              if (newParent) {
                const updatedChildren = [...(newParent.children || []), tag.id];
                const updatedNewParent = { ...newParent, children: updatedChildren };
                oldData = oldData.map(t => t.id === moveData.newParentId ? updatedNewParent : t);
              }
            }
            
            // Update tag path based on new parent
            let newPath = tag.name;
            if (moveData.newParentId) {
              const parentTag = oldData.find(t => t.id === moveData.newParentId);
              if (parentTag && parentTag.path) {
                newPath = `${parentTag.path}/${tag.name}`;
              }
            }
            
            return {
              ...tag,
              parentId: moveData.newParentId,
              level: newLevel,
              path: newPath
            };
          }
          return tag;
        });
      }
    }
  });
}

/**
 * Hook for setting tag inheritance rules
 * @returns Mutation function and result
 */
export function useSetTagInheritance() {
  return useFetchMutation<Tag, { tagId: string, rule: TagInheritanceRule }>({
    url: `${TAG_BASE_URL}/:tagId/inheritance`,
    method: 'POST',
    config: {
      transformRequest: [(data: { tagId: string, rule: TagInheritanceRule }) => {
        return JSON.stringify(data.rule);
      }]
    }
  });
}

/**
 * Hook for bulk updating tags
 * @returns Mutation function and result
 */
export function useBulkUpdateTags() {
  return useFetchMutation<Tag[], Partial<Tag>[]>({
    url: `${TAG_BASE_URL}/bulk`,
    method: 'PATCH',
    config: {
      transformRequest: [(data: Partial<Tag>[]) => {
        return JSON.stringify({ tags: data });
      }]
    },
    optimisticUpdate: {
      queryKey: [TAG_BASE_URL],
      updateFn: (oldData: Tag[] = [], updatedTags: Partial<Tag>[]) => {
        const tagMap = new Map<string, Partial<Tag>>();
        updatedTags.forEach(tag => {
          if (tag.id) {
            tagMap.set(tag.id, tag);
          }
        });
        
        return oldData.map(tag => {
          const updates = tagMap.get(tag.id);
          return updates ? { ...tag, ...updates } : tag;
        });
      }
    }
  });
}

/**
 * Hook for sharing a tag with React Query
 * @returns Mutation function and result
 */
export function useShareTag() {
  return useFetchMutation<Tag, ShareTagData>({
    url: `${TAG_BASE_URL}/:tagId/share`,
    method: 'POST',
    // Dynamically set the URL based on the tag ID
    config: {
      transformRequest: [(data: ShareTagData) => {
        // Extract the actual data to send
        return JSON.stringify({ sharedWith: data.sharedWith });
      }]
    }
  });
}

/**
 * Hook for fetching tag suggestions with React Query
 * @param query Optional search term
 * @param context Optional context for suggestions
 * @returns Query result with tag suggestions
 */
export function useTagSuggestions(query?: string, context?: string) {
  return useFetchQuery<TagSuggestion[]>({
    url: `${TAG_BASE_URL}/suggestions`,
    queryParams: { query, context },
    queryOptions: {
      staleTime: 1000 * 60, // 1 minute
      cacheTime: 1000 * 60 * 5, // 5 minutes
      enabled: !!(query || context) // Only run if query or context is provided
    },
    mockData: () => {
      // Generate mock suggestions if API fails
      return [
        { id: 'sug-1', name: 'Transformer Architecture', confidence: 0.95, reason: 'popularity', tagId: 'tag-4' },
        { id: 'sug-2', name: 'Attention Mechanism', confidence: 0.85, reason: 'similarity' },
        { id: 'sug-3', name: 'Language Model', confidence: 0.75, reason: 'cooccurrence', parentId: 'tag-6' }
      ];
    }
  });
}

/**
 * Hook for creating a tag suggestion with React Query
 * @returns Mutation function and result
 */
export function useCreateTagSuggestion() {
  return useFetchMutation<TagSuggestion, CreateTagSuggestionData>({
    url: `${TAG_BASE_URL}/suggestions`,
    method: 'POST'
  });
}

/**
 * Hook for accepting a tag suggestion with React Query
 * @returns Mutation function and result
 */
export function useAcceptTagSuggestion() {
  return useFetchMutation<Tag, string>({
    url: `${TAG_BASE_URL}/suggestions/:id/accept`,
    method: 'POST',
    // No body needed for accepting a suggestion
    config: {
      transformRequest: [(id: string) => undefined]
    }
  });
}

/**
 * Hook for fetching tag usage statistics with React Query
 * @param id Tag ID
 * @returns Query result with tag usage statistics
 */
export function useTagStats(id: string) {
  return useQuery({
    queryKey: ['tagStats', id],
    queryFn: async () => {
      if (!id) return null;
      try {
        const response = await apiClient.get<TagUsageStats>(`${TAG_BASE_URL}/${id}/stats`);
        return response.data;
      } catch (error) {
        console.warn('Falling back to mock data for tag stats');
        return {
          ...mockTagStats,
          tagId: id
        };
      }
    },
    enabled: !!id
  });
}

/**
 * Hook for fetching popular tags with React Query
 * @param limit Maximum number of tags to fetch
 * @returns Query result with popular tags
 */
export function usePopularTags(limit: number = 20) {
  return useQuery({
    queryKey: ['popularTags', limit],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Tag[]>(`${TAG_BASE_URL}/popular?limit=${limit}`);
        return response.data;
      } catch (error) {
        console.warn('Falling back to mock data for popular tags');
        return mockTags;
      }
    }
  });
}

/**
 * Hook for fetching tag conflicts with React Query
 * @returns Query result with tag conflicts
 */
export function useTagConflicts() {
  return useQuery({
    queryKey: ['tagConflicts'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<TagConflict[]>(`${TAG_BASE_URL}/conflicts`);
        return response.data;
      } catch (error) {
        console.warn('Falling back to mock data for tag conflicts');
        return mockTagConflicts;
      }
    }
  });
}

/**
 * Hook for resolving a tag conflict with React Query
 * @returns Mutation function and result
 */
export function useResolveTagConflict() {
  return useFetchMutation<Tag[], ResolveTagConflictData>({
    url: `${TAG_BASE_URL}/conflicts/:conflictId/resolve`,
    method: 'POST',
    config: {
      transformRequest: [(data: ResolveTagConflictData) => {
        return JSON.stringify({ selectedOptionId: data.selectedOptionId });
      }]
    }
  });
}

/**
 * Hook for fetching shared tags with React Query
 * @returns Query result with shared tags
 */
export function useSharedTags() {
  return useFetchQuery<Tag[]>({
    url: `${TAG_BASE_URL}/shared`,
    queryOptions: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
    },
    mockData: () => {
      // Generate mock shared tags if API fails
      return [
        { id: 'tag-10', name: 'Reinforcement Learning', color: '#ff5722', visibility: 'shared', owner: '2' },
        { id: 'tag-11', name: 'Research Methodologies', color: '#3f51b5', visibility: 'shared', owner: '2' }
      ];
    }
  });
}

/**
 * Hook for fetching global tags with React Query
 * @returns Query result with global tags
 */
export function useGlobalTags() {
  return useFetchQuery<Tag[]>({
    url: `${TAG_BASE_URL}/global`,
    queryOptions: {
      staleTime: 1000 * 60 * 10, // 10 minutes
      cacheTime: 1000 * 60 * 60, // 60 minutes
    },
    mockData: () => {
      // Generate mock global tags if API fails
      return [
        { id: 'tag-20', name: 'AI Ethics', color: '#795548', visibility: 'public', isGlobal: true },
        { id: 'tag-21', name: 'Benchmark Datasets', color: '#9e9e9e', visibility: 'public', isGlobal: true },
        { id: 'tag-22', name: 'Open Source', color: '#8bc34a', visibility: 'public', isGlobal: true }
      ];
    }
  });
}

export default tagsService;