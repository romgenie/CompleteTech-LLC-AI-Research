# AI Research Integration Frontend

This project is the frontend interface for the AI Research Integration system, providing a user interface for interacting with the research orchestration, knowledge graph, and paper implementation systems.

## Features

- **Research Interface**: Conduct research queries and generate comprehensive reports
- **Knowledge Graph Visualization**: Explore and visualize knowledge graphs of research entities and relationships with advanced filtering, analysis tools, and multiple export formats
- **Paper Implementation**: Generate code implementations from research papers
- **Authentication**: Secure login with JWT authentication
- **Responsive Design**: Works on devices of all sizes
- **Mock Data Fallbacks**: Graceful handling when backend services are unavailable

## Getting Started

### Prerequisites

- Node.js (v16+)
- npm or yarn
- Backend services (optional - the UI gracefully falls back to mock data)

### Installation

#### Using npm

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd src/ui/frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```
4. Start the development server:
   ```
   npm start
   ```
   The app will run on [http://localhost:3001](http://localhost:3001)

#### Using Docker

We provide multiple Docker setups for different development scenarios:

1. **Development Mode**:
   ```
   docker-compose -f docker/docker-compose.dev.yml up
   ```

2. **Development with Mock API** (recommended for frontend-only development):
   ```
   docker-compose -f docker/docker-compose.mock.yml up
   ```

3. **Full Stack Development**:
   ```
   docker-compose up
   ```

See [Docker Setup Documentation](./docker/README.md) for detailed information.

### Environment Setup

The application connects to a FastAPI backend running at `http://localhost:8000` and WebSocket server at `ws://localhost:8000/ws`. It will gracefully fall back to mock data if the backend is unreachable.

When using the mock API Docker setup, all backend features are simulated including real-time updates and notifications.

## Development

### Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   ├── contexts/           # React context providers
│   ├── hooks/              # Custom React hooks 
│   │   ├── useD3.js        # Hook for D3.js integration
│   │   ├── useFetch.js     # Hook for API requests with error handling
│   │   ├── useLocalStorage.js # Hook for localStorage state
│   │   ├── useWebSocket.js # Hook for WebSocket connections
│   │   └── useErrorBoundary.js # Error boundary hook
│   ├── pages/              # Main application pages
│   ├── services/           # API client services
│   └── utils/              # Utility functions
│   │   └── mockData.js     # Mock data for offline development
│   ├── App.js              # Main App component with routing
│   ├── index.js            # Entry point
│   └── theme.js            # Theme configuration
├── CODING_PROMPT.md        # Development guidelines
├── PROJECT_PLAN.md         # Project roadmap
└── package.json            # Dependencies and scripts
```

### Custom Hooks and Components

#### Hooks

The project uses several custom hooks to abstract common functionality:

- **useD3**: Integrates D3.js with React for knowledge graph visualization
- **useFetch**: Handles API requests with loading states, error handling, and mock data fallbacks
- **useLocalStorage**: Manages state that persists in localStorage
- **useWebSocket**: Manages WebSocket connections with reconnection capability
- **useErrorBoundary**: Provides error boundary components for graceful error handling

#### Reusable Components

Common UI components with standardized APIs:

- **ErrorBoundary**: Class component that catches and handles React errors
- **ErrorFallback**: Component for displaying error states with customizable UI
- **LoadingFallback**: Component for displaying loading indicators and states
- **StatusIndicator**: Component for displaying paper processing status with visual indicators
- **PaperStatusCard**: Card component for displaying paper information with real-time status updates
- **NotificationCenter**: Component for displaying and managing WebSocket notifications
- **KnowledgeGraphFilter**: Component for filtering knowledge graph entities and relationships
- **PaperUploadDialog**: Dialog for uploading papers with validation and metadata editing
- **PaperDashboard**: Comprehensive dashboard for paper management with filtering and sorting

### Available Scripts

- `npm start` - Start the development server on port 3001
- `npm build` - Build the project for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint to check code quality
- `npm run lint:fix` - Automatically fix ESLint issues

### Development Guidelines

See [CODING_PROMPT.md](./CODING_PROMPT.md) for detailed development guidelines, which cover:

- Component structure and best practices
- State management strategies
- API interaction patterns
- Error handling approaches
- Performance optimization techniques
- Accessibility requirements
- Testing strategies

### Testing Credentials

For testing purposes, you can use the following credentials:
- Username: `admin` 
- Password: `password`

## Integration with Backend

The frontend interfaces with the following backend services:

- **Authentication API**: `/auth/token` for JWT tokens
- **Research API**: `/api/research` for research queries
- **Knowledge Graph API**: `/api/knowledge-graph` for graph operations
- **Implementation API**: `/api/implementation` for paper implementation
- **WebSocket Server**: Real-time updates for paper processing

### WebSocket Integration

The application uses WebSockets for real-time updates:

- WebSocketContext provides a global WebSocket connection
- Status updates for paper processing are received in real-time
- NotificationCenter component for displaying system notifications
- PaperStatusCard components subscribe to individual paper updates
- Progress visualization with real-time status transitions
- Auto-reconnection with exponential backoff for connection stability
- Authentication integration with JWT tokens

```javascript
// Example WebSocket connection setup
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = process.env.REACT_APP_WEBSOCKET_HOST || window.location.host;
const wsUrl = `${protocol}//${host}/ws`;

// WebSocket wrapper hook with auto-reconnect
const { isConnected, sendMessage } = useWebSocket(wsUrl, {
  onMessage: handleWebSocketMessage,
  reconnectInterval: 2000,
  maxReconnectAttempts: 5
});

// Subscribe to paper status updates
const subscribeToPaper = (paperId) => {
  if (isConnected) {
    sendMessage({ 
      type: 'subscribe', 
      channel: `paper_status_${paperId}` 
    });
  }
};
```

### Mock Data and Error Handling

When backend services are unavailable, the application falls back to mock data defined in `/src/utils/mockData.js`. This includes:

- Knowledge graph entities and relationships
- Research query results
- Paper implementation code
- Paper processing status

```javascript
// Example API call with mock data fallback
const fetchEntityData = async (entityId) => {
  try {
    // Try to fetch from API
    const response = await knowledgeGraphService.getEntityDetails(entityId);
    return response;
  } catch (err) {
    console.error('Error fetching from API, using mock data');
    
    // Fallback to mock data
    const mockGraph = knowledgeGraphService.getMockGraph();
    const entity = mockGraph.nodes.find(node => node.id === entityId);
    
    if (entity) {
      return {
        ...entity,
        description: `Mock description for ${entity.name}`,
        properties: {
          // Mock properties...
        }
      };
    }
    throw new Error('Entity not found in mock data');
  }
};
```

The application implements comprehensive error handling:

- Global ErrorBoundary at the application root
- Component-level error boundaries for isolated failures
- Consistent error UI with ErrorFallback component
- Standardized loading states with LoadingFallback
- Automatic retry with exponential backoff for API requests

## Project Roadmap

See [PROJECT_PLAN.md](./PROJECT_PLAN.md) for the detailed project roadmap, which outlines:

- Current implementation status
- Phase 1: Optimization & Developer Experience ✅ (Completed)
- Phase 2: Real-time Features & Paper Processing ✅ (Completed)
- Phase 3: Advanced Features 🔄 (In Progress)
- Technical debt management (Ongoing)
- Timeline and success metrics

### Next Steps & Implementation Plan

We are currently focused on the following priorities for the next 4 weeks:

## Week 1-2: Knowledge Graph Performance & Accessibility + TypeScript Migration

### Knowledge Graph Performance Optimization (Week 1) 📈

**Comprehensive Force Simulation Optimization**
```javascript
/**
 * Optimizes D3 force simulation for large graphs (1000+ nodes)
 * - Adjusts parameters based on graph size automatically
 * - Scales forces for better stability and performance
 * - Implements early stabilization for very large graphs
 */
function createOptimizedForceSimulation(nodes, links, settings) {
  // Automatically adjust parameters based on graph size
  const nodeCount = nodes.length;
  const isLargeGraph = nodeCount > 500;
  const isVeryLargeGraph = nodeCount > 1000;
  
  // Scale parameters progressively with graph size
  const alphaDecay = isVeryLargeGraph ? 0.035 : (isLargeGraph ? 0.028 : 0.0228);
  const baseStrength = isVeryLargeGraph ? settings.forceStrength * 1.5 : settings.forceStrength;
  
  // Create optimized simulation
  const simulation = d3.forceSimulation(nodes)
    .alphaDecay(alphaDecay)
    .velocityDecay(0.4)
    .force("link", d3.forceLink(links)
      .id(d => d.id)
      .distance(d => {
        // Increase distance for large graphs
        const baseDistance = settings.nodeSize * 10;
        return isVeryLargeGraph ? baseDistance * 1.5 : baseDistance;
      })
      .strength(d => {
        // Optimize link strength based on connection count
        const sourceConnections = countConnections(d.source.id, links);
        const targetConnections = countConnections(d.target.id, links);
        return 1 / Math.min(Math.sqrt(sourceConnections), Math.sqrt(targetConnections));
      }))
    .force("charge", d3.forceManyBody()
      .strength(d => -baseStrength / Math.sqrt(nodeCount))
      .distanceMax(isVeryLargeGraph ? 200 : 300)
      .theta(0.8))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide()
      .radius(d => settings.nodeSize * (d.isSelected ? 1.75 : 1.5)));
    
  // Partial pre-computation for very large graphs
  if (isVeryLargeGraph) {
    simulation.stop();
    for (let i = 0; i < 100; ++i) simulation.tick();
  }
  
  return simulation;
}
```

**Smart Node Filtering With Fast Lookups**
```javascript
/**
 * Filters nodes in large graphs with optimized performance
 * - Uses Set data structures for O(1) lookups
 * - Implements logarithmic scaling for better visibility
 * - Prioritizes connected and important nodes
 */
function getFilteredNodes(nodes, links, selected, settings) {
  // Fast path for smaller graphs
  if (nodes.length < settings.filterThreshold) {
    return nodes;
  }
  
  // Pre-compute direct connections using Sets for O(1) lookup
  const selectedId = selected?.id;
  const directConnectionIds = new Set();
  const connectionCounts = {};
  
  // Build connection index in single pass (more efficient)
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    // Count connections for each node
    connectionCounts[sourceId] = (connectionCounts[sourceId] || 0) + 1;
    connectionCounts[targetId] = (connectionCounts[targetId] || 0) + 1;
    
    // Track direct connections to selected node
    if (sourceId === selectedId) directConnectionIds.add(targetId);
    if (targetId === selectedId) directConnectionIds.add(sourceId);
  });
  
  // Compute importance threshold using logarithmic scaling
  const importanceThreshold = Math.max(2, Math.log(nodes.length) / 2);
  
  // Filter nodes with optimized criteria
  return nodes.filter(node => {
    // Always include selected node and direct connections
    if (node.id === selectedId || directConnectionIds.has(node.id)) return true;
    
    // Include nodes with significant user-defined importance
    if (node.importance && node.importance > settings.importanceThreshold) return true;
    
    // Filter based on connection count (logarithmic scaling)
    const connectionCount = connectionCounts[node.id] || 0;
    return connectionCount >= importanceThreshold;
  });
}
```

**Dynamic Node Sizing and Visual Hierarchy**
```javascript
/**
 * Dynamic node sizing with visual hierarchy optimization
 * - Uses logarithmic scaling for better visual distribution
 * - Implements distinct visual states for selected and related nodes
 * - Adjusts sizing based on zoom level for consistent appearance
 */
function applyDynamicNodeSizing(nodeSelection, nodes, links, selected, settings, scale = 1) {
  // Build connection index for O(1) lookup
  const connectionCounts = {};
  const connectedToSelected = new Set();
  
  links.forEach(link => {
    const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
    const targetId = typeof link.target === 'object' ? link.target.id : link.target;
    
    // Count connections
    connectionCounts[sourceId] = (connectionCounts[sourceId] || 0) + 1;
    connectionCounts[targetId] = (connectionCounts[targetId] || 0) + 1;
    
    // Track connections to selected node
    if (selected?.id) {
      if (sourceId === selected.id) connectedToSelected.add(targetId);
      if (targetId === selected.id) connectedToSelected.add(sourceId);
    }
  });
  
  // Create logarithmic scale for better size distribution with many nodes
  const maxConnections = Math.max(1, d3.max(Object.values(connectionCounts)));
  const nodeSizeScale = d3.scaleLog()
    .domain([1, maxConnections])
    .range([settings.nodeSize, settings.nodeSize * 2.5])
    .clamp(true);
  
  // Apply optimized sizing to all nodes in a single pass
  nodeSelection.attr("r", d => {
    // Calculate base size using logarithmic scale
    let nodeSize = nodeSizeScale(connectionCounts[d.id] || 1);
    
    // Apply different sizing based on selection state
    if (d.id === selected?.id) {
      nodeSize = settings.nodeSize * 2;
    } else if (connectedToSelected.has(d.id)) {
      nodeSize = settings.nodeSize * 1.5;
    }
    
    // Factor in user-defined importance if available
    if (d.importance) {
      nodeSize *= 0.8 + (d.importance * 0.4);
    }
    
    // Adjust for zoom level to maintain consistent visual size
    return nodeSize / Math.sqrt(scale);
  });
  
  // Update visual styling for selection state
  nodeSelection
    .attr("stroke", d => {
      if (d.id === selected?.id) return "#000";
      if (connectedToSelected.has(d.id)) return "#555";
      return "#999";
    })
    .attr("stroke-width", d => {
      if (d.id === selected?.id) return 2.5 / Math.sqrt(scale);
      if (connectedToSelected.has(d.id)) return 1.5 / Math.sqrt(scale);
      return 1 / Math.sqrt(scale);
    });
}
```

### TypeScript Migration Implementation Plan 🔐

**Week 1: Core Context Migration**

```typescript
/**
 * TypeScript Migration Strategy
 * 
 * Our approach follows these principles:
 * 1. Incremental conversion starting with core infrastructure
 * 2. Shared type definitions in central location
 * 3. Complete context typing before component conversion
 * 4. Comprehensive interface definitions with documentation
 */

// Day 1-2: AuthContext with JWT token handling
interface User {
  id: string;
  username: string;
  roles: string[];
  email?: string;
  displayName?: string;
  preferences?: UserPreferences;
}

interface UserPreferences {
  theme?: 'light' | 'dark' | 'system';
  visualizationSettings?: {
    nodeSize: number;
    forceStrength: number;
    showLabels: boolean;
    [key: string]: any;
  };
}

// JWT token handling with type safety
interface JWTPayload {
  sub: string;
  username: string;
  roles: string[];
  exp: number;
  iat: number;
}

function parseJWT(token: string): JWTPayload | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(window.atob(base64));
    return payload as JWTPayload;
  } catch (e) {
    console.error('Error parsing JWT:', e);
    return null;
  }
}

// Complete AuthContext interface
interface AuthContextType {
  currentUser: User | null;
  token: string | null;
  loading: boolean;
  error: Error | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<User>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateUserPreferences: (preferences: Partial<UserPreferences>) => Promise<void>;
}

// Day 3-4: WebSocketContext with real-time messaging
interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface NotificationMessage extends WebSocketMessage {
  type: 'notification';
  id: string;
  title: string;
  message: string;
  category: 'info' | 'success' | 'warning' | 'error' | 'paper_status' | 'system';
  timestamp: string;
  entityId?: string;
  paperId?: string;
  isRead?: boolean;
}

interface PaperStatusMessage extends WebSocketMessage {
  type: 'paper_status';
  paperId: string;
  status: PaperStatus;
  previousStatus?: PaperStatus;
  timestamp: string;
  progress?: number;
  message?: string;
}

// Comprehensive WebSocket context interface
interface WebSocketContextType {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
  sendMessage: <T extends WebSocketMessage>(data: T) => boolean;
  lastMessage: WebSocketMessage | null;
  error: Event | null;
  notifications: NotificationMessage[];
  clearNotifications: () => void;
  removeNotification: (id: string) => void;
  markNotificationAsRead: (id: string) => void;
  subscribeToPaperUpdates: (paperId: string) => boolean;
  unsubscribeFromPaperUpdates: (paperId: string) => boolean;
  paperStatusMap: Record<string, PaperStatus>;
}

// Day 5: Central type definitions
// Create shared types in src/types/index.ts
namespace Types {
  // Knowledge Graph Types
  export interface GraphNode {
    id: string;
    name: string;
    type: EntityType;
    properties?: Record<string, any>;
    importance?: number;
    year?: number;
    color?: string;
  }

  export interface GraphLink {
    source: string | GraphNode;
    target: string | GraphNode;
    type: RelationshipType;
    properties?: Record<string, any>;
    weight?: number;
    confidence?: number;
  }

  export interface GraphData {
    nodes: GraphNode[];
    links: GraphLink[];
  }

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
}
```

**Week 2: Custom Hooks Migration**

```typescript
// Day 1-2: useD3 Hook with D3.js typing
import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

/**
 * Hook to integrate D3 visualizations with React
 * - Generic typing for different element types
 * - Proper cleanup to prevent memory leaks
 * - Support for dependencies for controlled updates
 */
function useD3<GElement extends d3.BaseType>(
  renderFn: (selection: d3.Selection<GElement, unknown, null, undefined>) => void,
  dependencies: React.DependencyList = []
): React.RefObject<GElement> {
  const ref = useRef<GElement>(null);
  
  useEffect(() => {
    if (ref.current) {
      // Create D3 selection and call the render function
      const selection = d3.select(ref.current) as d3.Selection<GElement, unknown, null, undefined>;
      renderFn(selection);
    }
    
    // Cleanup function to prevent memory leaks
    return () => {
      if (ref.current) {
        // Stop any running transitions or timers
        const selection = d3.select(ref.current);
        selection.selectAll('*').interrupt();
      }
    };
  }, dependencies);
  
  return ref;
}

// Day 3-5: useFetch Hook with advanced features
interface UseFetchOptions<TRequestData = any> {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  data?: TRequestData;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  useCache?: boolean;
  cacheTime?: number;
}

/**
 * Enhanced data fetching hook with comprehensive features:
 * - Type-safe request and response handling
 * - Automatic retries with exponential backoff
 * - Request cancellation support
 * - Caching with configurable TTL
 * - Mock data fallback for development
 */
function useFetch<TData = any, TError = ApiError, TRequestData = any>(
  url: string,
  options?: UseFetchOptions<TRequestData>,
  immediate: boolean = true,
  mockDataFn?: () => TData
): {
  data: TData | null;
  loading: boolean;
  error: TError | null;
  timestamp: number | null;
  refetch: (customOptions?: Partial<UseFetchOptions>) => Promise<TData>;
  cancel: () => void;
} {
  // Implementation with comprehensive error handling,
  // caching, and retry logic...
}
```

### Knowledge Graph Accessibility (Week 2) ♿ 

**Mon-Tue: Keyboard Navigation**
```javascript
// Add keyboard navigation to graph visualization
svg.attr("tabindex", 0)
  .attr("role", "application")
  .attr("aria-label", "Knowledge Graph Visualization")
  .on("keydown", e => {
    // Navigation shortcuts
    switch(e.key) {
      case "ArrowRight": navigateToNextNode(); break;
      case "ArrowLeft": navigateToPrevNode(); break;
      case "+": zoomIn(); break;
      case "-": zoomOut(); break;
      case "0": resetZoom(); break;
    }
  });

// Make nodes focusable
node.attr("tabindex", 0)
  .attr("role", "button")
  .attr("aria-label", d => `${d.type} node: ${d.name}`)
  .on("focus", handleNodeFocus)
  .on("keydown", e => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      selectNode(d);
    }
  });
```

**Wed-Thu: Screen Reader Support**
```javascript
// Create live region for screen reader announcements
const announcer = d3.select("body")
  .append("div")
  .attr("id", "graph-announcer")
  .attr("role", "status")
  .attr("aria-live", "polite")
  .style("position", "absolute")
  .style("clip", "rect(0,0,0,0)");

// Announce graph changes to screen readers
function announceToScreenReader(message) {
  announcer.text(message);
}

// Add proper ARIA attributes to visualization controls
d3.selectAll(".visualization-control")
  .attr("aria-controls", "knowledge-graph-visualization");
```

**Fri: Text-Based Alternative View & High Contrast Mode**
```javascript
// Create text representation of graph data
function createTextAlternative() {
  const container = d3.select("#graph-text-alternative");
  
  // Add graph summary
  container.html(`
    <h3>Knowledge Graph Summary</h3>
    <p>This graph contains ${graphData.nodes.length} entities and 
       ${graphData.links.length} relationships.</p>
    <p>The central entity is ${selectedEntity.type}: 
       <strong>${selectedEntity.name}</strong></p>
  `);
  
  // Add entity list grouped by type
  const entityTypes = [...new Set(graphData.nodes.map(n => n.type))];
  entityTypes.forEach(type => {
    const typeNodes = graphData.nodes.filter(n => n.type === type);
    // Add entity listings with interaction buttons...
  });
}

// Add high contrast mode
function applyHighContrastMode(enabled) {
  if (enabled) {
    const highContrastColors = {
      MODEL: '#0000FF',    // Blue
      DATASET: '#008000',  // Green
      ALGORITHM: '#FF0000' // Red
      // ...other entity types
    };
    
    // Apply high contrast colors with strong borders
    node.attr("fill", d => highContrastColors[d.type] || '#000000')
      .attr("stroke", "#FFFFFF")
      .attr("stroke-width", 2);
      
    // Increase contrast for links
    link.attr("stroke", "#000000")
      .attr("stroke-width", 2);
  }
}
```

### TypeScript Migration (Week 2) 📝

**Mon-Wed: Convert useD3 Hook to TypeScript**
```typescript
// Add proper typing to D3 integration hook
function useD3<GElement extends d3.BaseType>(
  renderFn: (selection: d3.Selection<GElement, unknown, null, undefined>) => void, 
  dependencies: React.DependencyList = []
): React.RefObject<GElement> {
  const ref = useRef<GElement>(null);
  
  useEffect(() => {
    if (ref.current) {
      renderFn(d3.select(ref.current));
    }
    return () => {
      if (ref.current) {
        d3.select(ref.current).selectAll('*').interrupt();
      }
    };
  }, dependencies);
  
  return ref;
}
```

**Thu-Fri: Convert useFetch & useLocalStorage to TypeScript**
```typescript
// Type-safe data fetching hook
function useFetch<TData = any, TError = Error>(
  url: string,
  options?: RequestInit,
  immediate: boolean = true
): {
  data: TData | null;
  loading: boolean;
  error: TError | null;
  refetch: () => Promise<void>;
} {
  // Implementation...
}

// Type-safe localStorage hook
function useLocalStorage<T>(
  key: string, 
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void] {
  // Implementation...
}
```

## Week 3-4: Research Enhancement & Knowledge Graph Improvements

### Citation Management (Week 3) 📚

**Mon-Tue: Citation Export in Multiple Formats**
```javascript
// Support multiple citation format exports
const exportFormats = {
  bibtex: citation => `@article{${citation.id},
    title={${citation.title}},
    author={${citation.authors.join(' and ')}},
    journal={${citation.journal}},
    year={${citation.year}}
  }`,
  
  apa: citation => `${citation.authors[0]} et al. (${citation.year}). 
    ${citation.title}. ${citation.journal}, ${citation.volume}(${citation.issue}), 
    ${citation.pages}.`
};

// UI for export format selection
const CitationExport = ({ citation }) => (
  <FormControl fullWidth variant="outlined" size="small">
    <InputLabel>Export Format</InputLabel>
    <Select value={format} onChange={handleFormatChange}>
      <MenuItem value="bibtex">BibTeX</MenuItem>
      <MenuItem value="apa">APA</MenuItem>
      <MenuItem value="mla">MLA</MenuItem>
      <MenuItem value="chicago">Chicago</MenuItem>
    </Select>
    <TextField
      multiline
      value={formatCitation(citation, format)}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <IconButton onClick={handleCopy}><ContentCopyIcon /></IconButton>
          </InputAdornment>
        )
      }}
    />
  </FormControl>
);
```

**Wed-Fri: Reference Management Interface**
```javascript
// Reference management panel component
const ReferencePanel = ({ citations, onEdit }) => (
  <Card variant="outlined">
    <CardHeader 
      title="References" 
      subheader={`${citations.length} citations`}
      action={
        <IconButton aria-label="export all">
          <FileDownloadIcon />
        </IconButton>
      }
    />
    <Divider />
    <List sx={{ maxHeight: '400px', overflow: 'auto' }}>
      {citations.map(citation => (
        <ListItem 
          key={citation.id}
          secondaryAction={
            <IconButton edge="end" onClick={() => onEdit(citation)}>
              <EditIcon fontSize="small" />
            </IconButton>
          }
        >
          <ListItemText
            primary={citation.title}
            secondary={`${citation.authors[0]} et al., ${citation.year}`}
          />
        </ListItem>
      ))}
    </List>
  </Card>
);
```

### Research Organization (Week 4) 🔍

**Mon-Tue: Research History with Local Storage**
```javascript
// Research history management hook
const useResearchHistory = () => {
  const [history, setHistory] = useLocalStorage('researchHistory', []);
  
  const saveToHistory = (query) => {
    const newHistory = [
      { 
        query, 
        timestamp: new Date().toISOString(),
        id: `query-${Date.now()}`
      },
      ...history
    ].slice(0, 50); // Keep last 50 queries
    
    setHistory(newHistory);
  };
  
  const removeFromHistory = (id) => {
    setHistory(history.filter(item => item.id !== id));
  };
  
  const clearHistory = () => setHistory([]);
  
  return { 
    history, 
    saveToHistory, 
    removeFromHistory,
    clearHistory
  };
};
```

**Wed-Fri: Research UI Improvements**
```javascript
// Progressive disclosure UI for research options
const ResearchOptions = () => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Paper variant="outlined" sx={{ mt: 2, p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="subtitle1">Search Options</Typography>
        <Button 
          size="small"
          endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Hide Options" : "Show Options"}
        </Button>
      </Box>
      
      <Collapse in={expanded}>
        <Box mt={2}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Result Type</InputLabel>
                <Select value={resultType} onChange={handleResultTypeChange}>
                  <MenuItem value="all">All Results</MenuItem>
                  <MenuItem value="papers">Research Papers</MenuItem>
                  <MenuItem value="implementation">Implementations</MenuItem>
                  <MenuItem value="datasets">Datasets</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Time Period</InputLabel>
                <Select value={timePeriod} onChange={handleTimePeriodChange}>
                  <MenuItem value="all">All Time</MenuItem>
                  <MenuItem value="year">Last Year</MenuItem>
                  <MenuItem value="month">Last Month</MenuItem>
                  <MenuItem value="custom">Custom Range</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
      </Collapse>
    </Paper>
  );
};
```

See the following documents for detailed implementation plans:
- [CODING_PROMPT.md](./CODING_PROMPT.md): Complete implementation code samples
- [PROJECT_PLAN.md](./PROJECT_PLAN.md): High-level project roadmap
- [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md): Day-by-day implementation schedule

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Acknowledgments

- React team for the excellent framework
- Material-UI for the component library
- D3.js for visualization capabilities