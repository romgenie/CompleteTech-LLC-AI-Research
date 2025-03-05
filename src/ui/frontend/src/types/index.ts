// Core type definitions for the application
// These types are used across multiple components and contexts

// User and Authentication Types
export interface User {
  id: string | number;
  username: string;
  email?: string;
  full_name?: string;
  role?: string;
  permissions?: string[];
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'system';
  visualizationSettings?: VisualizationSettings;
}

export interface VisualizationSettings {
  nodeSize: number;
  forceStrength: number;
  showLabels: boolean;
  darkMode: boolean;
  highlightNeighbors: boolean;
  showRelationshipLabels: boolean;
  [key: string]: any;
}

export interface AuthState {
  currentUser: User | null;
  token: string | null;
  loading: boolean;
  error: Error | null;
  isAuthenticated: boolean;
}

export interface JWTPayload {
  sub: string;
  exp: number;
  iat: number;
  username: string;
  role?: string;
}

export interface AuthResponse {
  token: string;
  tokenType: string;
  expiresAt: string;
  user: User;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface NotificationMessage extends WebSocketMessage {
  type: 'notification';
  id: string;
  title: string;
  message: string;
  category: NotificationType;
  timestamp: string;
  entityId?: string;
  paperId?: string;
  isRead?: boolean;
  action?: {
    type: string;
    path?: string;
  };
}

export interface SubscriptionMessage extends WebSocketMessage {
  type: 'subscribe' | 'unsubscribe';
  channel: string;
}

export interface PaperStatusMessage extends WebSocketMessage {
  type: 'paper_status';
  paperId: string;
  status: PaperStatus;
  previousStatus?: PaperStatus;
  timestamp: string;
  progress?: number;
  message?: string;
}

export interface AuthMessage extends WebSocketMessage {
  type: 'auth';
  token: string;
}

// Paper Types
export interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract?: string;
  year?: number | string;
  url?: string;
  doi?: string;
  status: PaperStatus;
  uploaded_at: string;
  updated_at?: string;
  metadata?: Record<string, any>;
}

export type PaperStatus = 
  | 'uploaded' 
  | 'queued' 
  | 'processing' 
  | 'extracting_entities' 
  | 'extracting_relationships' 
  | 'building_knowledge_graph' 
  | 'analyzed' 
  | 'implementation_ready'
  | 'implemented'
  | 'failed'
  | 'error';

export type NotificationType = 
  | 'info' 
  | 'success' 
  | 'warning' 
  | 'error' 
  | 'paper_status'
  | 'system';

// Knowledge Graph Types
export interface Entity {
  id: string;
  name: string;
  type: EntityType;
  properties?: Record<string, any>;
  importance?: number;
  year?: number | string;
  color?: string;
  // D3 force simulation properties
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  index?: number;
}

export interface Relationship {
  id: string;
  source: string | Entity;
  target: string | Entity;
  type: RelationshipType;
  properties?: Record<string, any>;
  weight?: number;
  confidence?: number;
  index?: number;
}

export interface Graph {
  entities: Entity[];
  relationships: Relationship[];
}

export type EntityType = 
  | 'MODEL' 
  | 'DATASET' 
  | 'ALGORITHM'
  | 'PAPER' 
  | 'AUTHOR' 
  | 'CODE'
  | 'FRAMEWORK'
  | 'METRIC'
  | 'METHOD'
  | 'TASK';

export type RelationshipType =
  | 'TRAINED_ON'
  | 'CITES'
  | 'AUTHORED_BY'
  | 'IMPLEMENTS'
  | 'BASED_ON'
  | 'OUTPERFORMS'
  | 'USES'
  | 'EVALUATED_ON'
  | 'PART_OF'
  | 'DEVELOPED_BY'
  | 'IS_A'
  | 'BUILDS_ON';

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Error Types
export interface ApiError {
  statusCode: number;
  message: string;
  details?: any;
}

// WebSocket Context Types
export interface WebSocketState {
  socket: WebSocket | null;
  isConnected: boolean;
  reconnectAttempts: number;
  lastMessage: WebSocketMessage | null;
  error: Event | null;
  notifications: NotificationMessage[];
  paperStatusMap: Record<string, PaperStatus>;
}

export interface WebSocketOptions {
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (data: any, event?: MessageEvent) => void;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onError?: (event: Event) => void;
}

// Research Types
export interface ResearchQuery {
  query: string;
  sources?: string[];
  options?: Record<string, any>;
}

export interface ResearchResult {
  query: string;
  summary: string;
  sources: Array<Record<string, any>>;
  sections: Array<Record<string, any>>;
  relatedTopics: string[];
  entityGraph: Graph;
}

// Implementation Types
export interface Implementation {
  paper: Paper;
  language: string;
  framework: string;
  files: Array<Record<string, any>>;
  stats: Record<string, any>;
  sampleCode: string;
}