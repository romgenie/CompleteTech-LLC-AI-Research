# Frontend Development Guide

## Project Overview
The AI Research Integration frontend provides a UI for interacting with our knowledge graph, research, and paper implementation systems. It's built with React, MUI, and integrates with our FastAPI backend.

## Technology Stack
- React 18
- Material UI 5
- React Router 6
- Axios
- D3.js for visualizations
- JWT authentication

## Architecture
- `/components` - Reusable UI components
- `/contexts` - React context providers
- `/hooks` - Custom React hooks
- `/pages` - Main application pages
- `/services` - API client services
- `/utils` - Utility functions

## Development Standards
1. **Component Structure**
   - Use functional components with hooks
   - Follow atomic design principles
   - Extract complex logic to custom hooks
   - Implement proper prop validation
   - Use lazy loading for routes and heavy components

2. **State Management**
   - Use React Context for global state
   - React Query for server state (future implementation)
   - Local component state for UI-specific state
   - Keep state management consistent across components

3. **API Interaction**
   - All API calls through service modules
   - Include error handling and loading states
   - Implement graceful fallbacks to mock data
   - Use the useFetch hook for consistent API access

4. **Code Style**
   - Follow ESLint configuration
   - Document with JSDoc comments
   - Use descriptive variable/function names
   - Keep components focused and small (<200 lines)
   - Follow the principle of single responsibility

5. **Performance**
   - Memoize expensive calculations with useMemo
   - Use React.memo for pure components
   - Implement virtualization for lists with 100+ items
   - Optimize D3 rendering with useCallback and useD3 hook
   - Avoid unnecessary re-renders (React DevTools profiler)

## Testing Strategy
- Unit tests for utilities and hooks
- Component tests with React Testing Library
- Mock API responses for offline testing
- Focus on critical user flows
- Add E2E tests for main user journeys

## Error Handling
- Use the ErrorBoundary component for critical UI sections
- Provide user-friendly error messages with ErrorFallback
- Log errors to console in development mode only
- Use useFetch hook with built-in retry mechanism 
- Implement graceful degradation with mock data fallbacks
- Add descriptive error states for different error types
- Keep error messaging consistent across the application

## Accessibility
- Use semantic HTML elements
- Maintain proper heading hierarchy
- Ensure keyboard navigation works
- Add ARIA attributes where needed
- Maintain sufficient color contrast (WCAG 2.1 AA)
- Test with screen readers

## Paper Processing Integration
- Use WebSocketContext for real-time status updates
- Show processing stages with StatusIndicator component
- Implement useWebSocket hook for WebSocket connection management
- Handle reconnection automatically with exponential backoff
- Display paper status transitions with meaningful visual cues
- Cache paper status locally for quick loading and offline display
- Subscribe to specific paper updates using the WebSocket API
- Implement notification system for status changes

## Common Development Tasks
- **Adding a new page**:
  1. Create component in `/pages` directory
  2. Add route in App.js
  3. Update navigation in Layout component
  4. Implement lazy loading

- **Creating a new component**:
  1. Create component file in `/components` directory
  2. Export component in appropriate index file
  3. Implement prop validation
  4. Add JSDoc comments
  5. Consider memoization for expensive components

- **Adding an API service**:
  1. Create service file in `/services` directory
  2. Implement API methods with error handling
  3. Add mock data fallback
  4. Update relevant context providers
  5. Add appropriate retry mechanisms

## Backend Integration
- API base URL: http://localhost:8000
- Authentication: JWT tokens stored in localStorage
- Endpoints:
  - `/auth/login` - User authentication
  - `/api/research` - Research query endpoints
  - `/api/knowledge-graph` - Knowledge graph operations
  - `/api/implementation` - Paper implementation endpoints
- Error handling:
  - Network errors: Retry with exponential backoff
  - Authentication errors: Redirect to login
  - Server errors: Display appropriate UI message
  - Default to mock data when backend unavailable

## Knowledge Graph Visualization
- Use the useD3 hook for all D3 integrations
- Implement node and edge filtering
- Add zooming and panning controls
- Use color coding for entity and relationship types
- Optimize rendering for graphs with 100+ nodes
- Implement selection and focus mechanisms

## Research Query Interface
- Show loading indicators during queries
- Implement typeahead suggestions
- Add query history and favorites
- Support structured and natural language queries
- Format results with proper citations

## Implemented Features

1. **Enhanced Error Handling**
   - ErrorBoundary component for critical UI sections
   - ErrorFallback for consistent error display
   - LoadingFallback for standardized loading states
   - Retry mechanisms with exponential backoff

2. **WebSocket Integration**
   - useWebSocket hook for WebSocket connections
   - WebSocketContext for application-wide real-time updates
   - NotificationCenter for displaying system notifications
   - Paper status subscriptions and updates

3. **Paper Status Visualization**
   - StatusIndicator component for visual status display
   - PaperStatusCard component with real-time updates
   - Progress visualization for paper processing stages
   - Detailed status history view

4. **Knowledge Graph Enhancement**
   - KnowledgeGraphFilter component with comprehensive filtering
   - Entity and relationship type filtering
   - Search capabilities for graph nodes
   - Year and confidence filtering options

5. **Paper Management**
   - PaperUploadDialog with multi-file support
   - Paper metadata editing capabilities
   - Upload progress visualization
   - Status tracking and error handling

## Next Steps

1. **TypeScript Migration** (Priority: High)
   - Add TypeScript and configuration
   - Create shared interfaces for API models
   - Convert core contexts and hooks first
   - Convert components incrementally
   - Add comprehensive typing for all props

2. **Performance Optimization** (Priority: Medium)
   - Implement React Query for data fetching and caching
   - Add virtualization for lists with many items
   - Optimize D3 rendering for large knowledge graphs
   - Add proper memoization for expensive computations
   - Implement lazy loading for less critical components

3. **Knowledge Graph Enhancements** (Priority: Medium)
   - Implement dynamic rendering for large graphs
   - Create specialized visualization modes (hierarchical, radial)
   - Add node clustering for complex graphs
   - Implement export capabilities (PNG, SVG, JSON)
   - Add graph analysis tools

4. **Paper Dashboard** (Priority: High)
   - Create comprehensive paper management dashboard
   - Implement batch operations for multiple papers
   - Add advanced sorting and filtering capabilities
   - Create paper comparison view
   - Add analytics and statistics for papers

5. **Developer Experience** (Priority: Low)
   - Add Storybook for component documentation
   - Implement comprehensive Jest test suites
   - Set up GitHub Actions for CI/CD
   - Add accessibility testing with axe-core
   - Create comprehensive API documentation
   - Add JSDoc for all components and functions