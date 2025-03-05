# AI Research Integration Platform UI

Frontend React application for the AI Research Integration Platform, providing interfaces for knowledge graph visualization, research queries, and paper implementation.

## Features

- **Knowledge Graph Visualization**: Interactive D3.js-based visualization with advanced filtering, navigation, and accessibility features
- **Research Interface**: Submit research queries and browse results with citation management
- **Implementation Tracking**: Monitor and manage AI paper implementations
- **Authentication**: Secure JWT-based authentication system
- **WebSocket Integration**: Real-time updates and notifications
- **Responsive Design**: Mobile-friendly UI that adapts to different screen sizes

## Getting Started

### Prerequisites

- Node.js 14+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server (runs on port 3001)
npm start

# Run linting
npm run lint

# Run linting with automatic fixes
npm run lint:fix

# Run tests
npm test
```

### Building for Production

```bash
# Create production build
npm run build
```

## Architecture

The frontend is built using:

- React 18
- Material UI for components
- React Router for navigation
- D3.js for knowledge graph visualization
- TypeScript for type safety
- Axios for API requests
- JWT for authentication

## Project Structure

```
/src
├── components/       # Reusable UI components
├── contexts/         # React context providers
├── docs/             # Documentation files
├── hooks/            # Custom React hooks
├── pages/            # Main application pages
├── services/         # API client services
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
```

## Documentation

See the `/docs` directory for detailed documentation:

- [Accessibility Implementation](./docs/Accessibility_Implementation.md)
- [TypeScript JavaScript Compatibility](./docs/TypeScript_JavaScript_Compatibility.md)
- [Optimization Results](./docs/Optimization_Results.md)

## Backend Integration

The frontend integrates with:

- FastAPI backend for API requests
- Neo4j for knowledge graph data
- MongoDB for paper and implementation data
- WebSockets for real-time updates

By default, the frontend connects to the backend at `http://localhost:8000`. You can modify this in the proxy settings in `package.json`.

## Mock Data

When the backend is unavailable, the frontend falls back to mock data for development and testing purposes. Mock data is available in `src/utils/mockData.js`.

## License

This project is proprietary and confidential.