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

2. **State Management**
   - Use React Context for global state
   - React Query for server state (future implementation)
   - Local component state for UI-specific state

3. **API Interaction**
   - All API calls through service modules
   - Include error handling and loading states
   - Implement graceful fallbacks to mock data

4. **Code Style**
   - Follow ESLint configuration
   - Document with JSDoc comments
   - Use descriptive variable/function names
   - Keep components focused and small

5. **Performance**
   - Memoize expensive calculations
   - Use React.memo for pure components
   - Implement virtualization for long lists
   - Optimize D3 rendering with useCallback

## Testing Strategy
- Unit tests for utilities and hooks
- Component tests with React Testing Library
- Mock API responses for offline testing
- Focus on critical user flows

## Common Development Tasks
- **Adding a new page**:
  1. Create component in `/pages` directory
  2. Add route in App.js
  3. Update navigation in Layout component

- **Creating a new component**:
  1. Create component file in `/components` directory
  2. Export component in appropriate index file
  3. Implement prop validation
  4. Add JSDoc comments

- **Adding an API service**:
  1. Create service file in `/services` directory
  2. Implement API methods with error handling
  3. Add mock data fallback
  4. Update relevant context providers

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

## Next Steps
1. **TypeScript Migration**
   - Add TypeScript and configuration
   - Convert files incrementally
   - Add interfaces for API models
   - Ensure comprehensive typing

2. **Performance Optimization**
   - Implement React Query for data fetching
   - Add virtualization for large data sets
   - Optimize D3 rendering for large graphs
   - Add code splitting for route-based bundles

3. **Enhanced Real-time Features**
   - Add WebSocket support for paper processing updates
   - Implement real-time knowledge graph updates
   - Add progress indicators for long-running operations

4. **Advanced UI Components**
   - Create comprehensive D3 visualization library
   - Implement advanced filtering for knowledge graph
   - Add exportable research reports
   - Create paper upload and tracking UI

5. **Developer Experience**
   - Add Storybook for component documentation
   - Implement automated testing with GitHub Actions
   - Add accessibility testing and improvements
   - Create comprehensive documentation