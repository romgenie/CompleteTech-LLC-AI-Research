# Frontend Development Guide

## Recent Achievements & Current Focus
- ✅ Enhanced Knowledge Graph Explorer with advanced visualization settings
- ✅ Implemented comprehensive UX improvements for better information hierarchy
- ✅ Added research-focused analysis tools for AI scientists
- ✅ Created intuitive onboarding experience with step-by-step guidance
- ✅ Improved export capabilities with multiple format options

## Implementation Priorities (Next 4 Weeks)
1. **Knowledge Graph Performance & Accessibility** (Weeks 1-2)
   - Optimize rendering for large graphs (1000+ nodes)
   - Implement keyboard navigation for visualization
   - Add screen reader support for data visualization

2. **TypeScript Migration** (Weeks 1-2)
   - Convert core contexts and hooks to TypeScript
   - Create comprehensive interface definitions
   - Implement type validation for API interactions

3. **Research Enhancement** (Weeks 3-4)
   - Complete citation and reference management
   - Implement research history and favorites
   - Apply Knowledge Graph UX standards to research interface

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
   - Implement proper prop validation with TypeScript or PropTypes
   - Use lazy loading for routes and heavy components
   - Follow established UX patterns from Knowledge Graph Explorer

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
   - Add proper TypeScript interfaces for request/response types
   - Include retry logic for transient failures

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
   - Implement progressive loading for large datasets
   - Use level-of-detail techniques for complex visualizations
   - Add client-side caching where appropriate

## Testing Strategy
- Unit tests for utilities and hooks (minimum 80% coverage)
- Component tests with React Testing Library
- Mock API responses using Mock Service Worker
- Visual regression tests for UI components
- Focus on critical user flows
- Add E2E tests for main user journeys
- Include accessibility testing in component tests
- Test keyboard navigation for all interactive elements
- Verify screen reader compatibility for critical components

## Docker Development
- Use Docker for consistent development environments
- Development mode: `docker-compose -f docker/docker-compose.dev.yml up`
- Mock API mode: `docker-compose -f docker/docker-compose.mock.yml up`
- Production build: Build with `docker/Dockerfile`
- Full stack: Use root `docker-compose.yml`

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
- Use tooltips to explain visualization features
- Provide progressive disclosure of advanced features
- Ensure visualization controls have clear visual feedback
- Implement keyboard navigation for accessibility
- Follow consistent visual hierarchy for visualization options
- Include contextual help for complex features
- Always provide empty states with clear user guidance
- Consider visual information density for different screen sizes

## Research Query Interface
- Show loading indicators during queries
- Implement typeahead suggestions
- Add query history and favorites
- Support structured and natural language queries
- Format results with proper citations

## Implemented Features (Phases 1 & 2)

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

## New UX Standards

Following our Knowledge Graph Explorer redesign, all components should follow these standards:

1. **Empty States**
   - Every component should have a meaningful empty state
   - Include step-by-step guidance for first-time users
   - Provide examples and suggested actions
   - Use visual elements to increase clarity

2. **Progressive Disclosure**
   - Start with simplified interface, reveal complexity progressively
   - Use accordions for grouping related settings
   - Organize options from most common to most advanced
   - Employ visual hierarchy to guide users

3. **Contextual Help**
   - Add tooltips to explain functionality
   - Include help icons for advanced features
   - Provide meaningful labels for all controls
   - Use inline illustrations for complex concepts

4. **Visual Feedback**
   - Every user action should receive immediate visual feedback
   - Highlight active states and selections
   - Show progress indicators for asynchronous operations
   - Use animations sparingly to guide attention

5. **Information Architecture**
   - Group related information in cards or panels
   - Use consistent layouts across similar components
   - Employ typography to create clear hierarchies
   - Balance information density with readability

6. **Accessibility**
   - Ensure keyboard navigation for all interactive elements
   - Include ARIA labels and roles for screen readers
   - Maintain sufficient color contrast ratios (WCAG AA compliance)
   - Provide alternative text for visualizations
   - Create text-based alternatives for graphical information
   - Support different viewport sizes with responsive design

## Current Development Priorities

1. **TypeScript Migration** (Priority: High)
   - Create JSDoc type definitions as preparation (✅ Completed with typeDefs.js)
   - Add TypeScript and tsconfig.json configuration
   - Convert core contexts and hooks first
   - Convert components incrementally
   - Add comprehensive typing for all props
   - Ensure all API models have proper interfaces

2. **Performance Optimization** (Priority: Medium)
   - Implement React Query for data fetching and caching
   - Add virtualization for lists with many items
   - Optimize D3 rendering for large knowledge graphs
   - Add proper memoization for expensive computations
   - Implement lazy loading for less critical components

3. **Knowledge Graph Enhancements** (Priority: High) ✅ Phase 1 Completed ✅ Phase 2 Started
   - ✅ Implement dynamic rendering options and visualization settings
   - ✅ Create specialized visualization modes (clustering, relationship focus)
   - ✅ Add node clustering for complex graphs
   - ✅ Implement export capabilities (JSON, CSV, Neo4j, SVG, PNG)
   - ✅ Add research-focused analysis tools (metrics, frontiers)
   - ✅ Enhance user experience with tooltips and contextual guidance
   - ✅ Improve information hierarchy with collapsible sections
   - ✅ Add intuitive empty state with step-by-step guidance
   
   **Phase 2 (In Progress):**
   - Optimize performance for graphs with 1000+ nodes (Priority: High)
   - Add WebGL rendering for very large graphs (Priority: Medium)
   - Implement URL state encoding for sharing specific views (Priority: Medium)
   - Add keyboard navigation and accessibility features (Priority: High)
   - Create additional layout options (hierarchical and radial) (Priority: Low)

4. **Paper Dashboard** (Priority: High) ✅ Completed
   - Create comprehensive paper management dashboard with PaperDashboard component
   - Implement advanced sorting options by date, title, status, and year
   - Add filtering capabilities by status, year and search term
   - Provide paper statistics and analytics
   - Create tabs for different paper status groups

5. **Developer Experience** (Priority: Medium)
   - Add Storybook for component documentation
   - Implement comprehensive Jest test suites
   - Set up GitHub Actions for CI/CD
   - Create component templates to ensure consistency
   - Add detailed JSDoc comments for all components
   - Implement Prettier for consistent code formatting
   - Create visual regression testing for UI components
   - Add accessibility testing with axe-core
   - Create comprehensive API documentation
   - Add JSDoc for all components and functions