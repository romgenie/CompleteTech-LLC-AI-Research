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
  parentId?: string | null; // ID of parent tag if this is a child tag
  children?: string[]; // IDs of child tags
  level?: number; // Hierarchy level (0 for root tags)
  path?: string; // Full path of the tag (e.g., "AI/Machine Learning/NLP")
  inheritedFrom?: string[]; // IDs of tags from which properties are inherited
  
  // Collaboration properties
  owner?: string; // User ID of tag owner
  visibility: TagVisibility; // Public, private, or shared
  sharedWith?: SharedWith[]; // Users or groups this tag is shared with
  isGlobal?: boolean; // Whether this tag is available to all users
  taxonomyId?: string; // ID of the taxonomy this tag belongs to
  usageCount?: number; // How many users have used this tag
  popularity?: number; // Calculated score based on usage
  suggestedBy?: string; // System or user ID that suggested this tag
  lastUsed?: string; // Timestamp when the tag was last used
}

// Visibility options for tags
export type TagVisibility = 'private' | 'public' | 'shared';

// Sharing permissions
export interface SharedWith {
  id: string; // User or group ID
  type: 'user' | 'group' | 'team'; // Type of entity
  permission: 'view' | 'use' | 'edit' | 'admin'; // Permission level
}

// Taxonomy for organizing tags
export interface Taxonomy {
  id: string;
  name: string;
  description?: string;
  owner: string; // User ID
  visibility: TagVisibility;
  sharedWith?: SharedWith[];
  rootTags: string[]; // IDs of top-level tags
  isOfficial?: boolean; // Whether this is an official/curated taxonomy
  domain?: string; // Domain this taxonomy is related to (e.g. "machine learning")
  createdAt: string;
  updatedAt?: string;
  version?: string;
}

// Tag suggestion model
export interface TagSuggestion {
  id: string;
  tagId?: string; // ID of existing tag if suggestion is for an existing tag
  name: string;
  parentId?: string; // Suggested parent tag
  taxonomy?: string; // Suggested taxonomy
  reason: 'similarity' | 'popularity' | 'cooccurrence' | 'system' | 'user';
  confidence: number; // 0-1 score
  source?: string; // ID of user or system that generated the suggestion
  expiresAt?: string; // When this suggestion expires
}

// Community tag usage statistics
export interface TagUsageStats {
  tagId: string;
  userCount: number; // Number of users using this tag
  itemCount: number; // Number of items tagged
  dailyUse?: {date: string, count: number}[]; // Usage trend
  relatedTags: {tagId: string, cooccurrence: number}[]; // Tags often used together
  trend: 'rising' | 'stable' | 'falling'; // Popularity trend
}

// Tag conflict resolution for competing hierarchies
export interface TagConflict {
  id: string;
  tagId: string;
  conflictType: 'hierarchy' | 'name' | 'classification' | 'duplicate';
  description: string;
  options: TagConflictOption[];
  resolved: boolean;
  selectedOption?: string;
  createdAt: string;
  updatedAt?: string;
}

// Resolution options for tag conflicts
export interface TagConflictOption {
  id: string;
  description: string;
  action: 'merge' | 'move' | 'rename' | 'split' | 'keep';
  tagIds: string[]; // Tags affected by this option
  newParentId?: string; // For move action
  newName?: string; // For rename action
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