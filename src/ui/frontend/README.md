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
│   ├── hooks/              # Custom React hooks (planned)
│   ├── pages/              # Main application pages
│   ├── services/           # API client services
│   └── utils/              # Utility functions
│   ├── App.js              # Main App component with routing
│   ├── index.js            # Entry point
│   └── theme.js            # Theme configuration
├── CODING_PROMPT.md        # Development guidelines
├── PROJECT_PLAN.md         # Project roadmap
└── package.json            # Dependencies and scripts
```

### Available Scripts

- `npm start` - Start the development server on port 3001
- `npm build` - Build the project for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint to check code quality
- `npm run lint:fix` - Automatically fix ESLint issues

### Development Guidelines

See [CODING_PROMPT.md](./CODING_PROMPT.md) for detailed development guidelines.

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
- **WebSocket Server**: Real-time updates (planned)

## Project Roadmap

See [PROJECT_PLAN.md](./PROJECT_PLAN.md) for the detailed project roadmap.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Acknowledgments

- React team for the excellent framework
- Material-UI for the component library
- D3.js for visualization capabilities