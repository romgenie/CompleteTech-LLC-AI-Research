# Deployment Guide for AI Research Integration Project

This guide provides detailed instructions for deploying the AI Research Integration Project in various environments. It covers local development, Docker-based deployment, and production setup.

## Prerequisites

- Python 3.9+ for core components
- Node.js 14+ for frontend
- Docker and Docker Compose for containerized deployment
- Neo4j 4.4+ for knowledge graph storage
- MongoDB 5.0+ for document storage

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-research-integration.git
cd ai-research-integration
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
# Especially the database connection details
nano .env
```

#### Start Database Services (Docker)

```bash
# Start Neo4j and MongoDB containers
docker-compose up -d neo4j mongodb

# Wait for services to initialize
sleep 10
```

#### Start the Backend API

```bash
# Start the FastAPI application
uvicorn src.ui.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd src/ui/frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## Docker Deployment

The project includes a complete Docker setup for easy deployment.

### 1. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Modify environment variables as needed
nano .env
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check the status of the containers
docker-compose ps
```

### 3. Access the Application

- Web UI: http://localhost:3001
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## Production Deployment

For production environments, additional steps are recommended:

### 1. Security Considerations

- Use proper SSL/TLS certificates for all endpoints
- Configure proper authentication for Neo4j and MongoDB
- Use secrets management for sensitive information
- Set up proper network isolation for database services

### 2. High Availability Setup

#### Database Configuration

- Configure Neo4j in a cluster mode for high availability
- Set up MongoDB replica set for redundancy
- Use persistent volumes for data storage

```yaml
# Example docker-compose-prod.yml snippet for Neo4j cluster
services:
  neo4j-core:
    image: neo4j:4.4-enterprise
    environment:
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_dbms_mode=CORE
      - NEO4J_causal__clustering_minimum__core__cluster__size__at__formation=3
      - NEO4J_causal__clustering_minimum__core__cluster__size__at__runtime=3
      - NEO4J_causal__clustering_initial__discovery__members=neo4j-core-1:5000,neo4j-core-2:5000,neo4j-core-3:5000
    volumes:
      - neo4j-core-data:/data
      - neo4j-core-logs:/logs
```

#### API Service Scaling

```bash
# Scale the API service to multiple instances
docker-compose -f docker-compose-prod.yml up -d --scale api=3
```

### 3. Monitoring and Logging

Set up comprehensive monitoring and logging:

- Configure Prometheus for metrics collection
- Set up Grafana for visualization
- Use logging aggregation services (ELK stack or similar)

```yaml
# Example Prometheus configuration snippet
scrape_configs:
  - job_name: 'api'
    scrape_interval: 15s
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
```

### 4. Backup Strategy

Implement regular backups for all data:

```bash
# Neo4j backup
docker exec neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j-$(date +%Y%m%d).dump

# MongoDB backup
docker exec mongodb mongodump --out=/backups/mongodb-$(date +%Y%m%d)
```

## Troubleshooting

### Common Issues

#### API Connection Issues

If the API cannot connect to the database services:

1. Verify database services are running:
   ```bash
   docker-compose ps
   ```

2. Check database logs:
   ```bash
   docker-compose logs neo4j
   docker-compose logs mongodb
   ```

3. Verify connection strings in `.env` file

#### Frontend Can't Reach API

If the frontend can't communicate with the API:

1. Check API is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verify API URL in frontend configuration:
   ```bash
   cat src/ui/frontend/src/services/config.js
   ```

3. Check for CORS issues in browser console

### Health Checks

The system provides health check endpoints to verify service status:

```bash
# Check API health
curl http://localhost:8000/health

# Check database connectivity
curl http://localhost:8000/health/database
```

## Upgrade Procedures

When upgrading to a new version:

1. Backup all data
   ```bash
   docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j-pre-upgrade.dump
   docker-compose exec mongodb mongodump --out=/backups/mongodb-pre-upgrade
   ```

2. Pull the latest code
   ```bash
   git pull origin main
   ```

3. Build new containers
   ```bash
   docker-compose build
   ```

4. Apply database migrations if needed
   ```bash
   docker-compose run --rm api python -m alembic upgrade head
   ```

5. Restart services
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Performance Tuning

### Neo4j Optimization

For large knowledge graphs:

1. Increase memory allocation
   ```bash
   # Edit .env file
   NEO4J_dbms_memory_heap_initial__size=4G
   NEO4J_dbms_memory_heap_max__size=8G
   ```

2. Add database indexes for frequently queried properties
   ```cypher
   CREATE INDEX ON :Paper(title);
   CREATE INDEX ON :AIModel(name);
   CREATE INDEX ON :Dataset(name);
   ```

### API Performance

For high-traffic deployments:

1. Enable API result caching
   ```python
   # In src/ui/api/config.py
   CACHE_ENABLED = True
   CACHE_TTL = 300  # seconds
   ```

2. Increase worker count for ASGI server
   ```bash
   uvicorn src.ui.api.app:app --workers 4 --host 0.0.0.0
   ```

## Appendix

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `NEO4J_URI` | Neo4j connection URI | `bolt://neo4j:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |
| `MONGODB_URI` | MongoDB connection URI | `mongodb://mongodb:27017` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | `secret` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Container Resource Requirements

| Container | CPU | Memory | Disk |
|-----------|-----|--------|------|
| api | 1-2 cores | 1-2 GB | 500 MB |
| neo4j | 2-4 cores | 4-8 GB | 20+ GB |
| mongodb | 1-2 cores | 2-4 GB | 10+ GB |
| frontend | 0.5 cores | 512 MB | 200 MB |