# AI Research Integration Frontend - Docker Setup

This directory contains Docker configurations for running the AI Research Integration Frontend in various environments.

## Available Docker Configurations

### Production Build
- `Dockerfile`: Production build with Nginx server
- `nginx.conf`: Nginx configuration for the production build

### Development Environments
- `development.Dockerfile`: Development environment with hot reloading
- `docker-compose.dev.yml`: Docker Compose configuration for development

### Development with Mock API
- `docker-compose.mock.yml`: Docker Compose configuration with mock API server
- `development-mock/`: Mock API server for development without backend

## Getting Started

### Development Mode
To run the application in development mode with hot reloading:

```bash
cd /path/to/frontend
docker-compose -f docker/docker-compose.dev.yml up
```

The application will be available at http://localhost:3001

### Development Mode with Mock API
To run the application with a mock API server:

```bash
cd /path/to/frontend
docker-compose -f docker/docker-compose.mock.yml up
```

- Frontend will be available at http://localhost:3001
- Mock API will be available at http://localhost:8000
- Mock WebSocket will be available at ws://localhost:8000/ws

### Production Build
To build and run the production version:

```bash
cd /path/to/frontend
docker build -t ai-research-frontend -f docker/Dockerfile .
docker run -p 80:80 ai-research-frontend
```

The application will be available at http://localhost

## Full Stack Deployment
To run the full stack application with backend services:

```bash
cd /path/to/frontend
docker-compose up
```

This will start:
- Frontend (React)
- Backend API (FastAPI)
- MongoDB
- Neo4j
- Redis
- Celery workers

## Testing Credentials
For the mock API, use the following credentials:
- Username: `admin`
- Password: `password`

## Mock Features
The mock API server provides:
- Authentication with JWT tokens
- Paper management endpoints
- Knowledge graph endpoints
- Research query endpoints
- Implementation endpoints
- WebSocket server with mock notifications and status updates