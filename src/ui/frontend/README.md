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

### Mock Data and Error Handling

When backend services are unavailable, the application falls back to mock data defined in `/src/utils/mockData.js`. This includes:

- Knowledge graph entities and relationships
- Research query results
- Paper implementation code
- Paper processing status

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

### Current Focus

We are focusing on the following priorities:

### Implementation Roadmap (Next 4 Weeks)

1. **Knowledge Graph Performance & Accessibility** (Weeks 1-2) 📈 🚀
   - 🔄 **Performance for Large Graphs**
     - **Week 1: D3 Force Optimization & Smart Filtering**
       ```javascript
       // Optimize simulation for stability with large node sets
       .alphaDecay(0.028)  // Slower cooling for better layout
       .velocityDecay(0.4) // Control movement friction
       
       // Implement importance-based filtering
       const filteredNodes = nodes.filter(node => 
         node.id === selectedNode.id || 
         isDirectlyConnected(node) ||
         hasHighImportance(node)
       );
       ```
       
     - **Week 2: Dynamic Level-of-Detail & Aggregation**
       ```javascript
       // Adjust detail based on zoom level
       function updateDetailLevel(zoomScale) {
         // Show labels only at higher zoom levels
         svg.selectAll(".node-label")
            .style("visibility", zoomScale > 1.2 ? "visible" : "hidden");
            
         // Create node clusters at low zoom levels
         if (zoomScale < 0.8 && nodes.length > 200) {
           showAggregatedView();
         } else {
           showDetailedView();
         }
       }
       ```
       
   - 🔄 **Accessibility Enhancements**
     - **Week 1: Keyboard Navigation & ARIA**
       ```javascript
       // Add keyboard controls for graph navigation
       node.attr("tabindex", 0)
          .attr("role", "button")
          .attr("aria-label", d => `${d.type}: ${d.name}`)
          .on("keydown", handleKeyNavigation);
          
       // Create screen reader announcements
       const announcer = d3.select("body").append("div")
         .attr("aria-live", "polite")
         .style("position", "absolute")
         .style("clip", "rect(0,0,0,0)");
       ```
       
     - **Week 2: Alternative Views & High Contrast**
       ```javascript
       // Create text-based view of graph data
       function createTextAlternative() {
         container.html(`
           <h3>Graph Summary</h3>
           <p>${nodes.length} entities, ${links.length} relationships</p>
           <p>Central entity: ${selectedEntity.name}</p>
           
           <div class="entity-list">...</div>
           <div class="relationship-list">...</div>
         `);
       }
       
       // Add high contrast color mode
       const highContrastColors = {
         MODEL: '#0000FF',   // Bold blue
         DATASET: '#008000', // Bold green
         ALGORITHM: '#FF0000', // Bold red
         // ...
       };
       ```

2. **TypeScript Migration** (Weeks 1-2) 🔐 📝
   - 🔄 **Core Context Migration**
     - **Week 1: AuthContext & WebSocketContext**
       ```typescript
       // AuthContext with proper JWT typing
       interface AuthState {
         isAuthenticated: boolean;
         token: string | null;
         user: User | null;
         error: Error | null;
         loading: boolean;
       }
       
       interface AuthContextType extends AuthState {
         login: (username: string, password: string) => Promise<void>;
         logout: () => void;
         checkAuthStatus: () => Promise<boolean>;
       }
       
       // WebSocket message types
       type WebSocketMessage = 
         | AuthMessage 
         | NotificationMessage 
         | SubscriptionMessage;
         
       interface NotificationMessage {
         type: 'notification';
         id: string;
         category: 'info' | 'success' | 'warning' | 'error' | 'paper_status';
         title: string;
         message: string;
         timestamp: string;
         action?: {
           type: string;
           path: string;
         };
       }
       ```
       
   - 🔄 **Custom Hook Migration**
     - **Week 2: useD3, useFetch & useWebSocket**
       ```typescript
       // useD3 with proper D3 selection typing
       function useD3<GElement extends d3.BaseType, PDatum, PGroup extends d3.BaseType>(
         renderFn: (selection: d3.Selection<GElement, PDatum, PGroup, unknown>) => void,
         dependencies: React.DependencyList = []
       ): React.RefObject<GElement> {
         const ref = useRef<GElement>(null);
         
         useEffect(() => {
           if (ref.current) {
             renderFn(d3.select(ref.current));
           }
           return () => {
             // Clean up code
           };
         }, dependencies);
         
         return ref;
       }
       
       // useFetch with request/response generics
       function useFetch<TData = any, TError = Error>() {
         const [data, setData] = useState<TData | null>(null);
         const [loading, setLoading] = useState<boolean>(false);
         const [error, setError] = useState<TError | null>(null);
         
         const fetchData = async <T = TData>(
           url: string, 
           options?: RequestInit
         ): Promise<T> => {
           // Implementation with proper type handling
         };
         
         return { data, loading, error, fetchData };
       }
       ```

3. **Research Enhancement** (Weeks 3-4) 📚 🔍
   - 🔄 **Citation Management**
     - **Week 3: Export & Reference Interface**
       ```javascript
       // Citation export in multiple formats
       const exportFormats = {
         bibtex: citation => `@article{${citation.id},
           title={${citation.title}},
           author={${citation.authors.join(' and ')}},
           journal={${citation.journal}},
           year={${citation.year}},
           doi={${citation.doi}}
         }`,
         
         apa: citation => `${citation.authors[0]} et al. (${citation.year}). 
           ${citation.title}. ${citation.journal}, ${citation.volume}(${citation.issue}), 
           ${citation.pages}. https://doi.org/${citation.doi}`,
           
         // Additional formats...
       };
       
       // Collapsible reference panel component
       const ReferencePanel = ({ citations, onEdit }) => (
         <Accordion>
           <AccordionSummary expandIcon={<ExpandMoreIcon />}>
             <Typography>References ({citations.length})</Typography>
           </AccordionSummary>
           <AccordionDetails>
             <List dense>
               {citations.map(citation => (
                 <ListItem key={citation.id}>
                   <ListItemText primary={citation.title} 
                                 secondary={`${citation.authors[0]} et al., ${citation.year}`} />
                   <ListItemSecondaryAction>
                     <IconButton onClick={() => onEdit(citation)}><EditIcon /></IconButton>
                   </ListItemSecondaryAction>
                 </ListItem>
               ))}
             </List>
           </AccordionDetails>
         </Accordion>
       );
       ```
       
   - 🔄 **Research Organization**
     - **Week 4: History & Favorites**
       ```javascript
       // Research history with local storage
       const useResearchHistory = () => {
         const [history, setHistory] = useState([]);
         
         // Load from localStorage on mount
         useEffect(() => {
           const savedHistory = localStorage.getItem('researchHistory');
           if (savedHistory) {
             setHistory(JSON.parse(savedHistory));
           }
         }, []);
         
         // Save query to history
         const saveToHistory = (query) => {
           const newHistory = [
             { query, timestamp: new Date().toISOString() },
             ...history
           ].slice(0, 50); // Keep last 50 queries
           
           setHistory(newHistory);
           localStorage.setItem('researchHistory', JSON.stringify(newHistory));
         };
         
         return { history, saveToHistory };
       };
       
       // Progressive disclosure UI for research filters
       const ResearchFilters = () => (
         <Accordion>
           <AccordionSummary expandIcon={<ExpandMoreIcon />}>
             <Typography>Advanced Filters</Typography>
           </AccordionSummary>
           <AccordionDetails>
             <Grid container spacing={2}>
               {/* Filter controls with tooltips */}
               <Grid item xs={6}>
                 <Tooltip title="Filter by publication year range">
                   <FormControl fullWidth>
                     <InputLabel>Year Range</InputLabel>
                     {/* Date range control */}
                   </FormControl>
                 </Tooltip>
               </Grid>
               {/* Additional filters... */}
             </Grid>
           </AccordionDetails>
         </Accordion>
       );
       ```

4. **Cross-Cutting Concerns** (Throughout Sprint) 🛠️ ♿
   - 🔄 **Accessibility Implementation**
     - Apply keyboard navigation across components
     - Ensure screen reader compatibility
     - Test with assistive technologies
     
   - 🔄 **Testing Foundation**
     - Set up Jest with React Testing Library
     - Create test utilities and helpers
     - Begin component test implementation

See the following documents for more details:
- [CODING_PROMPT.md](./CODING_PROMPT.md): Development guidelines and standards
- [PROJECT_PLAN.md](./PROJECT_PLAN.md): High-level project roadmap
- [DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md): Detailed implementation plan for Phase 3

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Acknowledgments

- React team for the excellent framework
- Material-UI for the component library
- D3.js for visualization capabilities