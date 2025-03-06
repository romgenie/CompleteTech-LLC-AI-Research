import { ResearchStats } from '../types/research';
import apiClient from './apiClient';
import { useFetchQuery } from '../hooks/useQueryFetch';

// Base URL for statistics endpoints
const STATS_BASE_URL = '/api/research/stats';

/**
 * Interface for date range parameters
 */
interface DateRangeParams {
  startDate?: string;
  endDate?: string;
}

/**
 * Service for research statistics
 */
const statsService = {
  /**
   * Get overall research statistics
   * @param params - Optional date range
   * @returns Research statistics
   */
  getStats: async (params?: DateRangeParams): Promise<ResearchStats> => {
    try {
      return await apiClient.get<ResearchStats>(STATS_BASE_URL, { params });
    } catch (error) {
      console.error('Error fetching research statistics:', error);
      // Return mock data if API fails
      return generateMockStats();
    }
  },

  /**
   * Get tag usage statistics
   * @returns Tag usage counts
   */
  getTagStats: async (): Promise<Record<string, number>> => {
    try {
      return await apiClient.get<Record<string, number>>(`${STATS_BASE_URL}/tags`);
    } catch (error) {
      console.error('Error fetching tag statistics:', error);
      // Return mock data if API fails
      return {
        'NLP': 24,
        'Machine Learning': 37,
        'Neural Networks': 18,
        'Transformers': 42,
        'Computer Vision': 15,
        'LLM': 35,
        'GPT': 22,
        'BERT': 12
      };
    }
  },

  /**
   * Get top search terms
   * @param limit - Maximum number of terms to return
   * @returns Most frequent search terms
   */
  getTopSearchTerms: async (limit: number = 10): Promise<Array<{term: string, count: number}>> => {
    try {
      return await apiClient.get<Array<{term: string, count: number}>>(`${STATS_BASE_URL}/terms`, { 
        params: { limit } 
      });
    } catch (error) {
      console.error('Error fetching top search terms:', error);
      // Return mock data if API fails
      return [
        { term: 'transformer architecture', count: 42 },
        { term: 'large language model comparison', count: 38 },
        { term: 'neural network training', count: 31 },
        { term: 'GPT-4 capabilities', count: 27 },
        { term: 'BERT vs RoBERTa', count: 24 },
        { term: 'attention mechanism explained', count: 22 },
        { term: 'image recognition advancements', count: 18 },
        { term: 'fine-tuning techniques', count: 16 },
        { term: 'reinforcement learning from human feedback', count: 15 },
        { term: 'text generation methods', count: 14 }
      ].slice(0, limit);
    }
  },

  /**
   * Get historical activity data
   * @param interval - Time interval ('day', 'week', 'month')
   * @param period - Number of intervals to return
   * @returns Historical activity data
   */
  getActivityHistory: async (
    interval: 'day' | 'week' | 'month' = 'day', 
    period: number = 14
  ): Promise<Array<{date: string, count: number}>> => {
    try {
      return await apiClient.get<Array<{date: string, count: number}>>(`${STATS_BASE_URL}/activity`, {
        params: { interval, period }
      });
    } catch (error) {
      console.error('Error fetching activity history:', error);
      // Return mock data if API fails
      return generateMockActivityData(interval, period);
    }
  },

  /**
   * Export statistics in various formats
   * @param format - Export format ('json', 'csv', 'xlsx')
   * @param params - Optional date range
   * @returns Export data or URL
   */
  exportStats: async (
    format: 'json' | 'csv' | 'xlsx' = 'json',
    params?: DateRangeParams
  ): Promise<string | Blob> => {
    try {
      const response = await apiClient.get<Blob>(`${STATS_BASE_URL}/export`, {
        params: { format, ...params },
        responseType: 'blob'
      });
      
      if (format === 'json') {
        // For JSON, return the parsed object
        const text = await new Response(response as any).text();
        return JSON.parse(text);
      }
      
      // For other formats, return the blob
      return response as unknown as Blob;
    } catch (error) {
      console.error(`Error exporting statistics as ${format}:`, error);
      throw error;
    }
  }
};

/**
 * Generate mock statistics data
 * @returns Mock statistics
 */
function generateMockStats(): ResearchStats {
  return {
    totalQueries: 248,
    savedQueries: 52,
    favorites: 18,
    tagCounts: {
      'NLP': 24,
      'Machine Learning': 37,
      'Neural Networks': 18,
      'Transformers': 42,
      'Computer Vision': 15,
      'LLM': 35,
      'GPT': 22,
      'BERT': 12,
      'Fine-tuning': 9,
      'Embeddings': 14,
      'Reinforcement Learning': 7,
      'Deep Learning': 28,
      'Text Generation': 16,
      'Image Recognition': 11
    },
    topSearchTerms: [
      { term: 'transformer architecture', count: 42 },
      { term: 'large language model comparison', count: 38 },
      { term: 'neural network training', count: 31 },
      { term: 'GPT-4 capabilities', count: 27 },
      { term: 'BERT vs RoBERTa', count: 24 },
      { term: 'attention mechanism explained', count: 22 },
      { term: 'image recognition advancements', count: 18 },
      { term: 'fine-tuning techniques', count: 16 },
      { term: 'reinforcement learning from human feedback', count: 15 },
      { term: 'text generation methods', count: 14 }
    ],
    queriesByDate: generateMockActivityData(),
    averageResultsPerQuery: 7.2
  };
}

/**
 * Generate mock activity data
 * @param interval - Time interval
 * @param period - Number of intervals
 * @returns Mock activity data
 */
function generateMockActivityData(
  interval: 'day' | 'week' | 'month' = 'day',
  period: number = 14
): Array<{date: string, count: number}> {
  const result: Array<{date: string, count: number}> = [];
  const today = new Date();
  
  // Set milliseconds per interval
  const intervalMs = {
    day: 24 * 60 * 60 * 1000,
    week: 7 * 24 * 60 * 60 * 1000,
    month: 30 * 24 * 60 * 60 * 1000
  };
  
  // Generate data for each interval
  for (let i = period - 1; i >= 0; i--) {
    const date = new Date(today.getTime() - (i * intervalMs[interval]));
    const formattedDate = date.toISOString().split('T')[0]; // YYYY-MM-DD
    
    // Generate a count between 5 and 40, with some trend
    const baseCount = 20; // Average
    const trend = Math.sin(i / period * Math.PI) * 10; // Sinusoidal trend
    const random = Math.random() * 10 - 5; // Random variation between -5 and 5
    const count = Math.round(Math.max(5, Math.min(40, baseCount + trend + random)));
    
    result.push({ date: formattedDate, count });
  }
  
  return result;
}

/**
 * Hook for fetching research statistics with React Query
 * @param dateRange - Optional date range
 * @returns Query result with statistics
 */
export function useResearchStats(dateRange?: DateRangeParams) {
  return useFetchQuery<ResearchStats>({
    url: STATS_BASE_URL,
    config: { params: dateRange },
    queryOptions: {
      staleTime: 1000 * 60 * 15, // 15 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: generateMockStats
  });
}

/**
 * Hook for fetching historical activity with React Query
 * @param interval - Time interval
 * @param period - Number of intervals
 * @returns Query result with activity data
 */
export function useActivityHistory(
  interval: 'day' | 'week' | 'month' = 'day',
  period: number = 14
) {
  return useFetchQuery<Array<{date: string, count: number}>>({
    url: `${STATS_BASE_URL}/activity`,
    config: { params: { interval, period } },
    queryOptions: {
      staleTime: 1000 * 60 * 15, // 15 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: () => generateMockActivityData(interval, period)
  });
}

/**
 * Hook for fetching tag statistics with React Query
 * @returns Query result with tag statistics
 */
export function useTagStats() {
  return useFetchQuery<Record<string, number>>({
    url: `${STATS_BASE_URL}/tags`,
    queryOptions: {
      staleTime: 1000 * 60 * 15, // 15 minutes
      cacheTime: 1000 * 60 * 60, // 1 hour
    },
    mockData: () => ({
      'NLP': 24,
      'Machine Learning': 37,
      'Neural Networks': 18,
      'Transformers': 42,
      'Computer Vision': 15,
      'LLM': 35,
      'GPT': 22,
      'BERT': 12
    })
  });
}

export default statsService;