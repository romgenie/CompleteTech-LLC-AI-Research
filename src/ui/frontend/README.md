# AI Research Integration Frontend

This project is the frontend interface for the AI Research Integration system, providing a user interface for interacting with the research orchestration, knowledge graph, and paper implementation systems.

## Features

- **Research Interface**: Conduct research queries with citation management and organization tools
- **Knowledge Graph Visualization**: Explore large knowledge graphs (1000+ nodes) with accessible, high-performance visualization 
- **TypeScript Support**: Type-safe implementation with comprehensive interface definitions
- **Paper Implementation**: Generate code implementations from research papers with traceability
- **Authentication**: Secure JWT authentication with token refresh capabilities
- **Accessibility**: Full WCAG 2.1 AA compliance including keyboard navigation and screen reader support
- **Responsive Design**: Optimized interface across all device sizes
- **Graceful Degradation**: Mock data fallbacks for offline or disconnected operation

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

The frontend follows a structured organization:

- **public/** - Static assets
- **src/** - Source code
  - **components/** - Reusable UI components
  - **contexts/** - React context providers
  - **hooks/** - Custom React hooks
  - **pages/** - Main application pages
  - **services/** - API client services
  - **utils/** - Utility functions

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

### 4-Week Development Roadmap

Our comprehensive implementation plan is organized into focused weekly sprints with detailed daily tasks:

## Week 1: Knowledge Graph Performance & TypeScript Foundations
| Focus | Monday | Tuesday | Wednesday | Thursday | Friday |
|-------|--------|---------|-----------|----------|--------|
| **Knowledge Graph** | Optimize force simulation | Node connection calculation | Smart filtering | Dynamic sizing | Performance testing |
| **TypeScript** | AuthContext interfaces | Token validation | WebSocket message types | Subscription typing | Core type definitions |

## Week 2: Accessibility & TypeScript Hooks
| Focus | Monday | Tuesday | Wednesday | Thursday | Friday |
|-------|--------|---------|-----------|----------|--------|
| **Accessibility** | Keyboard navigation | ARIA attributes | Screen reader support | Text alternatives | High contrast mode |
| **TypeScript** | D3.js type definitions | useD3 hook | useFetch with errors | Request/response generics | useWebSocket hooks |

## Week 3: Citation Management & Performance
| Focus | Monday | Tuesday | Wednesday | Thursday | Friday |
|-------|--------|---------|-----------|----------|--------|
| **Citations** | BibTeX & APA formats | MLA & Chicago formats | Export UI with preview | Reference management | DOI lookup |
| **Performance** | React Query research | API caching setup | Background fetching | Virtualization | Memoization |

## Week 4: Research Organization & UX
| Focus | Monday | Tuesday | Wednesday | Thursday | Friday |
|-------|--------|---------|-----------|----------|--------|
| **Research** | History with localStorage | Favorites system | Tagging system | Advanced filtering | Statistics & export |
| **UX** | Component library | Step-by-step workflows | Progressive disclosure | Error handling | Help documentation |

### Implementation Approach

Our approach to executing this plan emphasizes:

1. **Parallel Development Tracks**: Performance and TypeScript work progress concurrently
2. **Clear Task Dependencies**: Daily tasks build on previous day's work
3. **Measurable Deliverables**: Each day has concrete implementation goals
4. **Priority-Based Implementation**: Focus on P0 (must-have) features first
5. **Comprehensive Documentation**: All code includes detailed JSDoc comments

We'll track progress daily with GitHub PRs that include thorough testing instructions.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Acknowledgments

- React team for the excellent framework
- Material-UI for the component library
- D3.js for visualization capabilities