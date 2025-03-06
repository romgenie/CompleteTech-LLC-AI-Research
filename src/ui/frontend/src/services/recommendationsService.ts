import { 
  ResearchRecommendation, 
  ResearchRecommendationGroup, 
  ResearchInsight,
  Tag 
} from '../types/research';
import apiClient from './apiClient';
import { useFetchQuery, useFetchMutation } from '../hooks/useQueryFetch';

// Base URL for recommendations endpoints
const RECS_BASE_URL = '/api/research/recommendations';
const INSIGHTS_BASE_URL = '/api/research/insights';

/**
 * Service for research recommendations and insights
 */
const recommendationsService = {
  /**
   * Get research recommendations
   * @returns Recommendation groups
   */
  getRecommendations: async (): Promise<ResearchRecommendationGroup[]> => {
    try {
      return await apiClient.get<ResearchRecommendationGroup[]>(RECS_BASE_URL);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      // Return mock data if API fails
      return generateMockRecommendations();
    }
  },

  /**
   * Save a recommendation for later reference
   * @param recommendationId - Recommendation ID
   * @returns Success status
   */
  saveRecommendation: async (recommendationId: string): Promise<boolean> => {
    try {
      await apiClient.post(`${RECS_BASE_URL}/save`, { recommendationId });
      return true;
    } catch (error) {
      console.error(`Error saving recommendation ${recommendationId}:`, error);
      return false;
    }
  },

  /**
   * Remove a saved recommendation
   * @param recommendationId - Recommendation ID
   * @returns Success status
   */
  removeSavedRecommendation: async (recommendationId: string): Promise<boolean> => {
    try {
      await apiClient.delete(`${RECS_BASE_URL}/save/${recommendationId}`);
      return true;
    } catch (error) {
      console.error(`Error removing saved recommendation ${recommendationId}:`, error);
      return false;
    }
  },

  /**
   * Get saved recommendations
   * @returns Saved recommendation IDs
   */
  getSavedRecommendations: async (): Promise<string[]> => {
    try {
      return await apiClient.get<string[]>(`${RECS_BASE_URL}/saved`);
    } catch (error) {
      console.error('Error fetching saved recommendations:', error);
      // Return empty array if API fails
      return [];
    }
  },

  /**
   * Get research insights
   * @returns Research insights
   */
  getInsights: async (): Promise<ResearchInsight[]> => {
    try {
      return await apiClient.get<ResearchInsight[]>(INSIGHTS_BASE_URL);
    } catch (error) {
      console.error('Error fetching insights:', error);
      // Return mock data if API fails
      return generateMockInsights();
    }
  },

  /**
   * Mark an insight as read
   * @param insightId - Insight ID
   * @returns Success status
   */
  markInsightAsRead: async (insightId: string): Promise<boolean> => {
    try {
      await apiClient.post(`${INSIGHTS_BASE_URL}/${insightId}/read`);
      return true;
    } catch (error) {
      console.error(`Error marking insight ${insightId} as read:`, error);
      return false;
    }
  },

  /**
   * Dismiss an insight
   * @param insightId - Insight ID
   * @returns Success status
   */
  dismissInsight: async (insightId: string): Promise<boolean> => {
    try {
      await apiClient.post(`${INSIGHTS_BASE_URL}/${insightId}/dismiss`);
      return true;
    } catch (error) {
      console.error(`Error dismissing insight ${insightId}:`, error);
      return false;
    }
  },

  /**
   * Generate custom recommendations based on input
   * @param query - Query or topic
   * @returns Recommendation group
   */
  generateCustomRecommendations: async (query: string): Promise<ResearchRecommendationGroup> => {
    try {
      return await apiClient.post<ResearchRecommendationGroup>(`${RECS_BASE_URL}/generate`, { query });
    } catch (error) {
      console.error('Error generating custom recommendations:', error);
      throw error;
    }
  }
};

/**
 * Generate mock recommendations
 * @returns Mock recommendation groups
 */
function generateMockRecommendations(): ResearchRecommendationGroup[] {
  // Create simulated tags
  const mockTags: Tag[] = [
    { id: 'tag-1', name: 'Machine Learning', color: '#2196f3', count: 37 },
    { id: 'tag-2', name: 'NLP', color: '#f44336', count: 24 },
    { id: 'tag-3', name: 'Neural Networks', color: '#4caf50', count: 18 },
    { id: 'tag-4', name: 'Transformers', color: '#9c27b0', count: 42 }
  ];
  
  // Default recommendation groups
  return [
    {
      id: 'based-on-tags',
      title: 'Based on Your Research Interests',
      description: 'Recommendations derived from your most-used research tags',
      recommendations: [
        {
          id: 'tag-rec-1',
          title: 'Machine Learning Research Expansion',
          description: 'Explore the latest developments in Machine Learning based on your research interests.',
          confidence: 0.85,
          basedOn: [
            { type: 'tag', tagId: 'tag-1', tagName: 'Machine Learning' }
          ],
          tags: [mockTags[0]],
          suggestedQueryText: 'Latest research in Machine Learning'
        },
        {
          id: 'tag-rec-2',
          title: 'NLP Research Expansion',
          description: 'Explore the latest developments in NLP based on your research interests.',
          confidence: 0.78,
          basedOn: [
            { type: 'tag', tagId: 'tag-2', tagName: 'NLP' }
          ],
          tags: [mockTags[1]],
          suggestedQueryText: 'NLP advancements 2025'
        },
        {
          id: 'tag-pair-1',
          title: 'NLP + Transformers Intersection',
          description: 'Explore the intersection of NLP and Transformers for unique research insights.',
          confidence: 0.82,
          basedOn: [
            { type: 'tag', tagId: 'tag-2', tagName: 'NLP' },
            { type: 'tag', tagId: 'tag-4', tagName: 'Transformers' }
          ],
          tags: [mockTags[1], mockTags[3]],
          suggestedQueryText: 'NLP combined with Transformers applications'
        }
      ]
    },
    {
      id: 'based-on-queries',
      title: 'Continue Your Research',
      description: 'Suggestions to extend your previous research queries',
      recommendations: [
        {
          id: 'query-rec-1',
          title: 'Continue Research on "Transformer architecture"',
          description: 'Expand your existing research about Transformer architecture with the latest developments.',
          confidence: 0.79,
          basedOn: [
            { type: 'query', queryId: 'q1', queryText: 'Transformer architecture' }
          ],
          tags: [mockTags[3]],
          suggestedQueryText: 'Transformer architecture latest advancements'
        },
        {
          id: 'query-rec-2',
          title: 'Continue Research on "Large language models"',
          description: 'Expand your existing research about Large language models with the latest developments.',
          confidence: 0.75,
          basedOn: [
            { type: 'query', queryId: 'q2', queryText: 'Large language models' }
          ],
          suggestedQueryText: 'Large language models latest advancements'
        }
      ]
    },
    {
      id: 'trending-topics',
      title: 'Trending AI Research Topics',
      description: 'Hot topics in AI research you might want to explore',
      recommendations: [
        {
          id: 'trend-rec-1',
          title: 'Multi-Modal LLMs',
          description: 'Explore the latest in models that combine text, image, and audio understanding.',
          confidence: 0.85,
          basedOn: [
            { type: 'history', patternId: 'trending', patternDescription: 'Current trending AI topic' }
          ],
          suggestedQueryText: 'Multi-modal language models capabilities'
        },
        {
          id: 'trend-rec-2',
          title: 'Foundation Models for Specialized Domains',
          description: 'Research into domain-specific adaptations of large foundation models.',
          confidence: 0.82,
          basedOn: [
            { type: 'history', patternId: 'trending', patternDescription: 'Current trending AI topic' }
          ],
          suggestedQueryText: 'Domain-specific foundation models in AI'
        },
        {
          id: 'trend-rec-3',
          title: 'AI System Agents',
          description: 'Recent developments in autonomous AI systems and multi-agent frameworks.',
          confidence: 0.79,
          basedOn: [
            { type: 'history', patternId: 'trending', patternDescription: 'Current trending AI topic' }
          ],
          suggestedQueryText: 'Autonomous AI agent systems architecture'
        }
      ]
    }
  ];
}

/**
 * Generate mock insights
 * @returns Mock insights
 */
function generateMockInsights(): ResearchInsight[] {
  // Create simulated tags
  const mockTags: Tag[] = [
    { id: 'tag-1', name: 'Machine Learning', color: '#2196f3', count: 37 },
    { id: 'tag-4', name: 'Transformers', color: '#9c27b0', count: 42 }
  ];
  
  return [
    {
      id: 'insight-top-tag',
      type: 'pattern',
      title: 'Transformers is Your Main Research Focus',
      description: "You've used the \"Transformers\" tag most frequently, indicating a strong research interest in this area.",
      importance: 'medium',
      relatedTags: [mockTags[1]],
      iconType: 'analytics'
    },
    {
      id: 'insight-gap-machine-learning',
      type: 'gap',
      title: 'Potential Research Gap in MACHINE LEARNING',
      description: 'Your research in machine learning might benefit from exploring neural networks, deep learning.',
      importance: 'medium',
      relatedTags: [mockTags[0]],
      iconType: 'explore'
    },
    {
      id: 'insight-recurring-terms',
      type: 'trend',
      title: 'Recurring Research Themes',
      description: 'Terms like "transformer", "model", "architecture" appear frequently in your queries, showing consistent research interests.',
      importance: 'high',
      iconType: 'trending_up'
    },
    {
      id: 'insight-suggestion-export',
      type: 'suggestion',
      title: 'Create a Research Portfolio',
      description: 'You have a substantial collection of research. Consider exporting your findings into a structured document to share with others.',
      importance: 'high',
      iconType: 'assignment'
    }
  ];
}

/**
 * Hook for fetching recommendations with React Query
 * @returns Query result with recommendations
 */
export function useRecommendations() {
  return useFetchQuery<ResearchRecommendationGroup[]>({
    url: RECS_BASE_URL,
    queryOptions: {
      staleTime: 1000 * 60 * 15, // 15 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: generateMockRecommendations,
    // Enable real-time updates via WebSocket
    enableWebSocket: true,
    wsMessageType: 'recommendations_update'
  });
}

/**
 * Hook for fetching research insights with React Query
 * @returns Query result with insights
 */
export function useResearchInsights() {
  return useFetchQuery<ResearchInsight[]>({
    url: INSIGHTS_BASE_URL,
    queryOptions: {
      staleTime: 1000 * 60 * 30, // 30 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: generateMockInsights,
    // Enable real-time updates via WebSocket
    enableWebSocket: true,
    wsMessageType: 'insights_update'
  });
}

/**
 * Hook for saving/unsaving recommendations with React Query
 * @returns Mutation function and result
 */
export function useSaveRecommendation() {
  return useFetchMutation<{ success: boolean }, { recommendationId: string; action: 'save' | 'unsave' }>({
    url: `${RECS_BASE_URL}/save`,
    method: 'POST',
    // Optimistic update is not needed as we directly update UI state
    mockData: () => ({ success: true })
  });
}

/**
 * Hook for dismissing insights with React Query
 * @returns Mutation function and result
 */
export function useDismissInsight() {
  return useFetchMutation<{ success: boolean }, string>({
    url: `${INSIGHTS_BASE_URL}/:id/dismiss`,
    method: 'POST',
    // Dynamically set the URL based on the insight ID
    config: {
      transformRequest: [(id: string) => {
        // No body needed for this request
        return undefined;
      }]
    },
    // Optimistic update to immediately remove the insight
    optimisticUpdate: {
      queryKey: [INSIGHTS_BASE_URL],
      updateFn: (oldData: ResearchInsight[] = [], id: string) => {
        return oldData.filter(insight => insight.id !== id);
      }
    }
  });
}

export default recommendationsService;