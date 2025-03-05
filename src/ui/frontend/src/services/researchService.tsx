import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { 
  ApiResponse, 
  PaginatedResponse, 
  ResearchQuery, 
  ResearchResult 
} from '../types';
import { useFetchQuery, useFetchMutation } from '../hooks';
import { mockData } from '../utils/mockData';

// Create axios instance for research orchestration API
const researchApi: AxiosInstance = axios.create({
  baseURL: '/research',
});

// Add request interceptor to add authentication token
researchApi.interceptors.request.use(
  (config: AxiosRequestConfig): AxiosRequestConfig => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  }
);

/**
 * Interface for a research task
 */
export interface ResearchTask {
  id: string;
  query: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  result?: ResearchResult;
  error?: string;
}

/**
 * Interface for a saved query
 */
export interface SavedQuery {
  id: string;
  query: string;
  createdAt: string;
  updatedAt?: string;
  notes?: string;
  tags?: string[];
}

/**
 * Interface for query history item
 */
export interface QueryHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  status: string;
  resultCount?: number;
}

/**
 * Interface for mock search result
 */
export interface MockSearchResult {
  id: string;
  title: string;
  source: string;
  relevance: number;
  content: string;
  pdfUrl: string;
}

/**
 * Interface for quick search options
 */
export interface QuickSearchOptions {
  sources?: string[];
  maxResults?: number;
}

/**
 * Hook to fetch saved queries with React Query
 */
export function useSavedQueries() {
  return useFetchQuery<SavedQuery[]>({
    url: '/research/saved-queries',
    queryOptions: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
    },
    mockData: () => {
      // Return mock saved queries
      return [
        { id: '1', query: 'Recent advances in transformer architecture', createdAt: new Date().toISOString() },
        { id: '2', query: 'Comparison of large language models', createdAt: new Date().toISOString() },
        { id: '3', query: 'Neural network evolution', createdAt: new Date().toISOString() }
      ];
    }
  });
}

/**
 * Hook to fetch query history with React Query
 */
export function useQueryHistory() {
  return useFetchQuery<QueryHistoryItem[]>({
    url: '/research/query-history',
    queryOptions: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
    },
    mockData: () => {
      // Return mock query history
      return [
        { id: '1', query: 'Recent advances in transformer architecture', timestamp: new Date().toISOString(), status: 'completed', resultCount: 5 },
        { id: '2', query: 'Comparison of large language models', timestamp: new Date(Date.now() - 86400000).toISOString(), status: 'completed', resultCount: 3 },
        { id: '3', query: 'Neural network evolution', timestamp: new Date(Date.now() - 172800000).toISOString(), status: 'completed', resultCount: 7 }
      ];
    }
  });
}

/**
 * Hook to conduct research with React Query
 */
export function useResearch() {
  return useFetchMutation<ResearchResult, { query: string }>({
    url: '/research/research',
    method: 'POST',
    mockData: () => {
      // Return mock research results
      return mockData.researchResults;
    }
  });
}

/**
 * Hook to save a query with React Query
 */
export function useSaveQuery() {
  return useFetchMutation<SavedQuery, { query: string }>({
    url: '/research/saved-queries',
    method: 'POST',
    mockData: (variables) => {
      // Return mock saved query
      return {
        id: `saved-${Date.now()}`,
        query: variables.query,
        createdAt: new Date().toISOString()
      };
    }
  });
}

/**
 * Hook to fetch research tasks with React Query
 */
export function useResearchTasks(params: Record<string, any> = {}) {
  return useFetchQuery<PaginatedResponse<ResearchTask>>({
    url: '/research/tasks',
    config: { params },
    queryOptions: {
      staleTime: 1000 * 60 * 1, // 1 minute - tasks change frequently
      cacheTime: 1000 * 60 * 10, // 10 minutes
    },
    mockData: () => {
      // Return mock paginated research tasks
      return {
        items: [
          {
            id: '1',
            query: 'Recent advances in transformer architecture',
            status: 'completed',
            createdAt: new Date(Date.now() - 36000000).toISOString(),
            updatedAt: new Date(Date.now() - 35000000).toISOString(),
            completedAt: new Date(Date.now() - 35000000).toISOString(),
          },
          {
            id: '2',
            query: 'Comparison of large language models',
            status: 'running',
            createdAt: new Date(Date.now() - 1800000).toISOString(),
            updatedAt: new Date(Date.now() - 1700000).toISOString(),
          }
        ],
        total: 2,
        page: 1,
        pageSize: 10,
        totalPages: 1
      };
    }
  });
}

/**
 * Research service for interacting with the research orchestration API.
 * This version includes both traditional methods and React Query hooks.
 */
const researchService = {
  /**
   * Conduct a research query
   * 
   * @param query - The research query
   * @returns Search results
   */
  conductResearch: async (query: string): Promise<ResearchResult> => {
    try {
      const response = await researchApi.post<ApiResponse<ResearchResult>>('/research', { query });
      return response.data.data as ResearchResult;
    } catch (error) {
      console.error('Error conducting research:', error);
      throw error;
    }
  },

  /**
   * Save a query for later use
   * 
   * @param query - The query to save
   * @returns Saved query
   */
  saveQuery: async (query: string): Promise<SavedQuery> => {
    try {
      const response = await researchApi.post<ApiResponse<SavedQuery>>('/saved-queries', { query });
      return response.data.data as SavedQuery;
    } catch (error) {
      console.error('Error saving query:', error);
      throw error;
    }
  },

  /**
   * Get saved queries
   * 
   * @returns List of saved queries
   */
  getSavedQueries: async (): Promise<SavedQuery[]> => {
    try {
      const response = await researchApi.get<ApiResponse<SavedQuery[]>>('/saved-queries');
      return response.data.data as SavedQuery[] || [];
    } catch (error) {
      console.error('Error fetching saved queries:', error);
      return [];
    }
  },

  /**
   * Get query history
   * 
   * @returns List of previous queries
   */
  getQueryHistory: async (): Promise<QueryHistoryItem[]> => {
    try {
      const response = await researchApi.get<ApiResponse<QueryHistoryItem[]>>('/query-history');
      return response.data.data as QueryHistoryItem[] || [];
    } catch (error) {
      console.error('Error fetching query history:', error);
      return [];
    }
  },

  /**
   * Generate mock data for testing
   */
  getMockResults: (): { results: MockSearchResult[] } => {
    return {
      results: [
        {
          id: "r1",
          title: "Recent Advances in Transformer Models",
          source: "ArXiv",
          relevance: 9.8,
          content: `<h2>Recent Advances in Transformer Models</h2>
          <p>Transformer models have revolutionized natural language processing since their introduction in 2017. This report examines recent developments in transformer architecture improvements, including:</p>
          <ul>
            <li><strong>Efficient Attention Mechanisms</strong>: Linear and sub-quadratic attention alternatives</li>
            <li><strong>Parameter Efficiency</strong>: Adapters, LoRA, and other parameter-efficient tuning methods</li>
            <li><strong>Multimodal Extensions</strong>: Vision transformers and text-to-image models</li>
          </ul>
          <p>The performance improvements have been substantial, with state-of-the-art models achieving unprecedented results on benchmark tasks while requiring fewer computational resources for fine-tuning.</p>
          <h3>Key Findings</h3>
          <p>Our analysis reveals that efficient attention mechanisms can reduce computational complexity from O(n²) to O(n log n) or even O(n), making transformers viable for much longer sequences. Parameter-efficient tuning methods have made it possible to adapt large pre-trained models to specific tasks with as little as 0.1% of the original parameter count.</p>`,
          pdfUrl: "#"
        },
        {
          id: "r2",
          title: "Comparative Analysis of Large Language Models",
          source: "Research Report",
          relevance: 9.5,
          content: `<h2>Comparative Analysis of Large Language Models</h2>
          <p>This report presents a comprehensive comparison of recent large language models, evaluating their performance across multiple dimensions:</p>
          <ul>
            <li><strong>Benchmark Performance</strong>: MMLU, HumanEval, GSM8K, TruthfulQA</li>
            <li><strong>Computational Efficiency</strong>: Parameters, FLOPs, inference speed</li>
            <li><strong>Reasoning Capabilities</strong>: Logic, mathematics, planning</li>
            <li><strong>Specialized Knowledge</strong>: Domain-specific expertise</li>
          </ul>
          <p>Our findings indicate that while parameter count correlates with performance, model architecture and training methodology are equally important factors. Models fine-tuned with RLHF generally demonstrate better alignment with human preferences.</p>
          <h3>Performance Comparison</h3>
          <table border="1">
            <tr><th>Model</th><th>MMLU</th><th>HumanEval</th><th>GSM8K</th><th>TruthfulQA</th></tr>
            <tr><td>GPT-4</td><td>86.4%</td><td>67.0%</td><td>92.0%</td><td>59.0%</td></tr>
            <tr><td>Claude 2</td><td>78.5%</td><td>63.2%</td><td>88.0%</td><td>70.0%</td></tr>
            <tr><td>LLaMA 2</td><td>68.9%</td><td>29.9%</td><td>56.8%</td><td>41.7%</td></tr>
          </table>`,
          pdfUrl: "#"
        },
        {
          id: "r3",
          title: "The Evolution of Neural Network Architectures",
          source: "Journal of Machine Learning",
          relevance: 8.7,
          content: `<h2>The Evolution of Neural Network Architectures</h2>
          <p>Neural network architectures have undergone significant evolution over the past decade. This report traces this development from early feed-forward networks to modern architectures:</p>
          <ol>
            <li><strong>Convolutional Neural Networks (CNNs)</strong>: LeNet, AlexNet, VGG, ResNet</li>
            <li><strong>Recurrent Neural Networks (RNNs)</strong>: LSTM, GRU</li>
            <li><strong>Attention Mechanisms</strong>: Self-attention, multi-head attention</li>
            <li><strong>Transformers</strong>: Encoder-decoder, encoder-only, decoder-only</li>
            <li><strong>Mixture of Experts (MoE)</strong>: Conditional computation, sparse activation</li>
          </ol>
          <p>Each architectural innovation has addressed specific limitations of previous approaches, leading to improvements in performance, efficiency, or both.</p>
          <h3>Key Milestones</h3>
          <p>The introduction of residual connections in ResNet (2015) solved the vanishing gradient problem for deep networks. The attention mechanism in the Transformer architecture (2017) enabled parallel processing of sequences, overcoming the sequential nature of RNNs. More recently, mixture-of-experts architectures have shown how conditional computation can dramatically increase model capacity without proportional increases in computation.</p>`,
          pdfUrl: "#"
        }
      ]
    };
  },

  /**
   * Submit a research query for processing.
   * 
   * @param queryData - Research query data
   * @returns Created research task
   */
  submitQuery: async (queryData: ResearchQuery): Promise<ResearchTask> => {
    try {
      const response = await researchApi.post<ApiResponse<ResearchTask>>('/queries/', queryData);
      return response.data.data as ResearchTask;
    } catch (error) {
      console.error('Error submitting research query:', error);
      throw error;
    }
  },

  /**
   * Get research tasks with optional filtering.
   * 
   * @param params - Query parameters
   * @returns List of research tasks
   */
  getTasks: async (params: Record<string, any> = {}): Promise<PaginatedResponse<ResearchTask>> => {
    try {
      const response = await researchApi.get<ApiResponse<PaginatedResponse<ResearchTask>>>('/tasks/', { params });
      return response.data.data as PaginatedResponse<ResearchTask>;
    } catch (error) {
      console.error('Error fetching research tasks:', error);
      throw error;
    }
  },

  /**
   * Get a specific research task by ID.
   * 
   * @param taskId - Task ID
   * @returns Research task details
   */
  getTaskById: async (taskId: string): Promise<ResearchTask> => {
    try {
      const response = await researchApi.get<ApiResponse<ResearchTask>>(`/tasks/${taskId}`);
      return response.data.data as ResearchTask;
    } catch (error) {
      console.error(`Error fetching research task ${taskId}:`, error);
      throw error;
    }
  },

  /**
   * Cancel a research task.
   * 
   * @param taskId - Task ID
   */
  cancelTask: async (taskId: string): Promise<void> => {
    try {
      await researchApi.delete(`/tasks/${taskId}`);
    } catch (error) {
      console.error(`Error canceling task ${taskId}:`, error);
      throw error;
    }
  },

  /**
   * Perform a quick search without creating a persistent task.
   * 
   * @param query - Search query
   * @param sources - Sources to search
   * @param maxResults - Maximum results per source
   * @returns Search results
   */
  quickSearch: async (
    query: string, 
    options: QuickSearchOptions = {}
  ): Promise<ResearchResult> => {
    try {
      const response = await researchApi.post<ApiResponse<ResearchResult>>('/search', null, {
        params: {
          query,
          sources: options.sources?.join(','),
          max_results: options.maxResults || 5
        }
      });
      return response.data.data as ResearchResult;
    } catch (error) {
      console.error('Error performing quick search:', error);
      throw error;
    }
  }
};

export default researchService;