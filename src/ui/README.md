# UI for AI Research Integration Project

This module contains the web-based user interface for the AI Research Integration Project.

## Overview

The UI provides a user-friendly interface for:

1. **Research Querying**: Submit research queries and view results
2. **Knowledge Graph Visualization**: Explore and visualize AI research knowledge
3. **Research Report Generation**: Create and customize research reports
4. **Implementation Management**: Request and track paper implementations

## Architecture

The UI consists of:

- **Frontend**: React-based single-page application
- **Backend Integration**: API clients for connecting to the FastAPI backend
- **Visualization Components**: D3.js for knowledge graph visualization

## Technology Stack

- React for UI components
- D3.js for data visualization
- Axios for API communication
- JWT for authentication
- Material-UI for component library

## Directory Structure

```
ui/
├── frontend/              # React application
│   ├── public/            # Static assets
│   ├── src/               # Source code
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── utils/         # Utility functions
│   │   └── contexts/      # React contexts
├── api_client/            # API client for backend communication
└── visualization/         # Visualization components
```

## Setup and Running

### Development

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

3. Access the UI at http://localhost:3000

### Production

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Serve the static files from a web server or the backend API

## Authentication

The UI uses JWT authentication to communicate with the API:

1. Login page collects user credentials
2. Auth service exchanges credentials for JWT token
3. Token is stored in localStorage/sessionStorage
4. Subsequent API calls include the token in Authorization header
5. Protected routes check for valid token

## Key Features

### Research Interface
- Query input with natural language support
- Source selection for academic, web, and code repositories
- Results display with relevance scoring

### Knowledge Graph Explorer
- Interactive graph visualization
- Entity and relationship filtering
- Search and exploration tools
- Path discovery between concepts

### Report Generator
- Template selection
- Section customization
- Citation management
- Export to multiple formats (PDF, HTML, Markdown)

### User Management
- Authentication and authorization
- Profile management
- Research history and favorites

## Implementation Status

- 🔄 **In Progress**: Initial setup and structure
- ⬜ Research querying interface
- ⬜ Knowledge graph visualization
- ⬜ Report generation interface
- ⬜ User authentication