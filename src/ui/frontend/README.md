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

**Mon-Tue: Force Simulation Parameter Optimization**
```javascript
// Optimize D3 force simulation for large graph performance
const simulation = d3.forceSimulation(graphData.nodes)
  // Reduce alpha decay for more stable layout with 1000+ nodes
  .alphaDecay(0.028)  // default is 0.0228
  .velocityDecay(0.4) // Controls movement friction
  
  // Configure link forces with dynamic distance and strength
  .force("link", d3.forceLink(graphData.links)
    .id(d => d.id)
    .distance(d => visualizationSettings.nodeSize * 10)
    .strength(d => 1 / Math.min(countConnections(d.source), countConnections(d.target))))
  
  // Scale charge force based on node count for better layouts
  .force("charge", d3.forceManyBody()
    .strength(d => -visualizationSettings.forceStrength / Math.sqrt(graphData.nodes.length))
    .distanceMax(300))  // Limit effect distance for performance
  
  // Prevent node overlap in dense graphs
  .force("collision", d3.forceCollide().radius(d => visualizationSettings.nodeSize * 1.5));
```

**Wed-Thu: Smart Node Filtering Based on Importance**
```javascript
// Intelligently filter nodes for large graphs
function getVisibleNodes() {
  return graphData.nodes.filter(node => {
    // Always show selected node
    if (node.id === selectedEntity.id) return true;
    
    // Always show direct connections to selected node
    if (graphData.links.some(link => 
      (link.source.id === selectedEntity.id && link.target.id === node.id) ||
      (link.target.id === selectedEntity.id && link.source.id === node.id))) {
      return true;
    }
    
    // For other nodes, filter based on connection count
    const connectionCount = graphData.links.filter(link => 
      link.source.id === node.id || link.target.id === node.id
    ).length;
    
    // Show only significant nodes when graph is large
    return graphData.nodes.length < 100 || 
           connectionCount > Math.log(graphData.nodes.length);
  });
}
```

**Fri: Dynamic Node Sizing Based on Connectivity**
```javascript
// Scale node sizes based on connectivity and importance
const nodeSizeScale = d3.scaleLinear()
  .domain([0, d3.max(graphData.nodes, d => countConnections(d))])
  .range([visualizationSettings.nodeSize, visualizationSettings.nodeSize * 2.5]);

// Apply dynamic sizing to nodes
node.attr("r", d => {
  // Selected node is always prominent
  if (d.id === selectedEntity.id) {
    return visualizationSettings.nodeSize * 1.5;
  }
  
  // Size based on connection count
  return nodeSizeScale(countConnections(d));
});
```

### TypeScript Migration (Week 1) 🔐

**Mon-Tue: Convert AuthContext to TypeScript**
```typescript
// Core authentication types
interface User {
  id: string;
  username: string;
  roles: string[];
  email?: string;
}

interface AuthState {
  currentUser: User | null;
  token: string | null;
  loading: boolean;
  error: Error | null;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<User>;
  logout: () => void;
}
```

**Wed-Fri: Convert WebSocketContext to TypeScript**
```typescript
// WebSocket message types
interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface NotificationMessage extends WebSocketMessage {
  type: 'notification';
  id: string;
  title: string;
  message: string;
  category: 'info' | 'success' | 'warning' | 'error' | 'paper_status';
  timestamp: string;
}

interface WebSocketContextType {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (data: WebSocketMessage) => boolean;
  lastMessage: WebSocketMessage | null;
  error: Event | null;
  notifications: NotificationMessage[];
  clearNotifications: () => void;
  subscribeToPaperUpdates: (paperId: string) => boolean;
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