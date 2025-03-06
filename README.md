# AI Research Integration Platform

A comprehensive platform that streamlines the process from research paper to working implementation.

## Project Overview

The AI Research Integration Platform helps researchers and developers discover, analyze, and implement AI research findings. The platform provides tools for knowledge graph exploration, research orchestration, and implementation planning.

## Key Features

1. **Knowledge Graph System**: Build and explore a comprehensive knowledge graph of AI research entities including models, datasets, papers, and their relationships.

2. **Research Orchestration**: Conduct research queries, gather information from multiple sources, extract knowledge, and generate comprehensive research reports.

3. **Implementation Planning**: Bridge the gap between research and implementation by automatically planning, generating, and testing code based on research papers.

4. **Temporal Evolution**: Track how AI concepts, models, and architectures evolve over time with temporal analysis and prediction tools.

5. **Team Collaboration**: Work together with your team using workspaces, comments, and version control features designed for research collaboration.

6. **Paper Processing**: Automatically process, analyze, and extract structured information from research papers with our specialized pipeline.

## Architecture

The platform is built with a modern architecture:

1. **API Layer**: FastAPI-based RESTful API providing access to all platform features
2. **Knowledge Graph System**: Neo4j-based graph database for storing and querying research entities and relationships
3. **Research Orchestration Engine**: Coordinates the research process from query to report generation
4. **Implementation Planning System**: Manages the process of converting research papers to code implementations
5. **Frontend Layer**: Modern React-based UI for interacting with the platform

## Getting Started

### Running with Docker

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-research-integration.git
cd ai-research-integration

# Start all services
docker-compose up -d
```

This will start:
- The landing page at http://localhost:3000
- The API at http://localhost:8000
- Neo4j database at bolt://localhost:7687 (Web UI: http://localhost:7474)
- MongoDB at mongodb://localhost:27017

### API Documentation

Once the services are running, you can access the API documentation at:
- http://localhost:3000/api/docs (Swagger UI)
- http://localhost:3000/api/redoc (ReDoc)

## Theme and Design System

The platform follows a consistent design system documented in [THEME.md](THEME.md). The design system includes:

- Color palette with primary, secondary, and accent colors
- Typography guidelines
- UI component styling
- Accessibility considerations

All new components and pages should adhere to this design system for a consistent user experience.

## Development

### API Development

The API is built with FastAPI. To run the API in development mode:

```bash
# Install dependencies
pip install -r requirements.txt -r requirements-api.txt

# Run the API with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

The landing page is built with Express.js:

```bash
# Navigate to the landing page directory
cd src/ui/landing

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms of the MIT license.