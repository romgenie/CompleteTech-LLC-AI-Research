# AI Research Integration Frontend

This project is the frontend interface for the AI Research Integration system, providing a user interface for interacting with the research orchestration, knowledge graph, and paper implementation systems.

## Features

- **Research Interface**: Conduct research queries and generate comprehensive reports
- **Knowledge Graph Visualization**: Explore and visualize knowledge graphs of research entities and relationships
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

### Environment Setup

The application relies on a FastAPI backend running at `http://localhost:8000` but will gracefully fall back to mock data if the backend is unreachable.

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
- Phase 3: Advanced Features 🔄 (In Progress, TypeScript migration started)
- Technical debt management (Ongoing)
- Timeline and success metrics

### Current Focus

We are focusing on the following priorities:

1. **TypeScript Implementation**: Continuing the TypeScript migration with full interfaces and type safety
2. **Knowledge Graph Visualization Enhancements**: Optimizing visualization for large graphs
3. **Performance Optimization**: Implementing React Query and virtualization for better performance

See [CODING_PROMPT.md](./CODING_PROMPT.md) for detailed development guidelines and next steps.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Acknowledgments

- React team for the excellent framework
- Material-UI for the component library
- D3.js for visualization capabilities