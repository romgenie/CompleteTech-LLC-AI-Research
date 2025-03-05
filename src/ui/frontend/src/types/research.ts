import { Graph } from './index';

// Basic research query type
export interface ResearchQuery {
  id?: string;
  query: string;
  sources?: string[];
  options?: Record<string, any>;
  timestamp?: string;
  tags?: Tag[];
  isFavorite?: boolean;
  userId?: string;
}

// Research result type
export interface ResearchResult {
  id?: string;
  query: string;
  summary: string;
  sources: Array<ResearchSource>;
  sections: Array<ResearchSection>;
  relatedTopics: string[];
  entityGraph: Graph;
  timestamp?: string;
  tags?: Tag[];
  isFavorite?: boolean;
}

// Research source type
export interface ResearchSource {
  id?: string;
  title: string;
  authors?: string[];
  url?: string;
  publishedDate?: string;
  source?: string;
  journal?: string;
  confidence?: string | number;
  relevance?: number;
  snippet?: string;
  cited?: boolean;
}

// Research section type
export interface ResearchSection {
  id?: string;
  title: string;
  content: string;
  sourceIds?: string[];
  order?: number;
}

// Tag type for organizing research
export interface Tag {
  id: string;
  name: string;
  color?: string;
  description?: string;
  count?: number; // Number of items with this tag
}

// Research history item
export interface ResearchHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  resultCount?: number;
  sections?: string[];
  tags?: Tag[];
  isFavorite?: boolean;
}

// Saved research query
export interface SavedQuery {
  id: string;
  query: string;
  description?: string;
  createdAt: string;
  updatedAt?: string;
  lastRun?: string;
  tags?: Tag[];
  isFavorite?: boolean;
  userId: string;
  notes?: string;
}

// Research filter options
export interface ResearchFilterOptions {
  dateRange?: {
    from?: Date | null;
    to?: Date | null;
  };
  tags?: string[];
  favorites?: boolean;
  sources?: string[];
  sortBy?: 'date' | 'relevance' | 'alphabetical';
  sortOrder?: 'asc' | 'desc';
}

// Research organization statistics
export interface ResearchStats {
  totalQueries: number;
  savedQueries: number;
  favorites: number;
  tagCounts: Record<string, number>;
  topSearchTerms: Array<{term: string, count: number}>;
  queriesByDate: Array<{date: string, count: number}>;
  averageResultsPerQuery: number;
}

// Research task for long-running research operations
export interface ResearchTask {
  id: string;
  query: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  progress?: number;
  result?: ResearchResult;
  error?: string;
  userId: string;
}

// Export format options
export type ExportFormat = 'pdf' | 'markdown' | 'html' | 'docx' | 'text';

// Export options
export interface ExportOptions {
  format: ExportFormat;
  includeSources: boolean;
  includeGraphVisual: boolean;
  includeTags: boolean;
  includeMetadata: boolean;
  template?: string;
  citations?: {
    style: string;
    includeReferences: boolean;
  };
}

// Research recommendation types
export interface ResearchRecommendation {
  id: string;
  title: string;
  description: string;
  confidence: number; // 0-1 relevance score
  basedOn: RecommendationSource[];
  tags?: Tag[];
  suggestedQueryText?: string;
}

export type RecommendationSource = 
  | { type: 'tag'; tagId: string; tagName: string } 
  | { type: 'query'; queryId: string; queryText: string }
  | { type: 'history'; patternId: string; patternDescription: string };

export interface ResearchRecommendationGroup {
  id: string;
  title: string;
  description: string;
  recommendations: ResearchRecommendation[];
}

// Analysis of user's research behavior
export interface ResearchInsight {
  id: string;
  type: 'trend' | 'gap' | 'pattern' | 'suggestion';
  title: string;
  description: string;
  importance: 'low' | 'medium' | 'high';
  relatedTags?: Tag[];
  iconType?: string;
}