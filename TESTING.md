# Testing the Paper Processing Pipeline

This document provides instructions for testing the Paper Processing Pipeline implementation.

## Getting Started

The Paper Processing Pipeline is designed to extract knowledge from academic papers and integrate it into our knowledge graph system. The implementation includes:

- Document processing with PDF, HTML, and text support
- Entity recognition and relationship extraction
- Knowledge Graph integration with Temporal Evolution support
- Real-time updates via WebSocket connections

## Prerequisites

To test the Paper Processing Pipeline, ensure you have the following:

1. Running MongoDB instance
2. Running Neo4j instance
3. Running Redis server (for Celery)
4. Python requirements installed:
   ```
   pip install -r requirements.txt
   ```

## Running the API Services

1. Start the backend services:
   ```bash
   docker-compose up -d
   ```

2. Start the Celery worker:
   ```bash
   cd src/paper_processing
   celery -A paper_processing.tasks.celery_app worker --loglevel=INFO
   ```

3. Start the FastAPI application:
   ```bash
   cd src/paper_processing
   uvicorn api.main:app --reload --port 8000
   ```

## Testing the API

### Basic Testing

You can perform basic API testing using the provided shell script:

```bash
./test_paper_api.sh
```

This script tests the basic endpoints and WebSocket availability.

### Full Testing

For complete testing of the paper processing pipeline, use the Python test script:

```bash
python test_api.py --paper-file path/to/paper.pdf --api-url http://localhost:8000
```

Replace `path/to/paper.pdf` with a path to a valid PDF file.

### API Endpoints

The main endpoints for testing are:

- `POST /papers`: Upload a paper
- `POST /papers/{paper_id}/process`: Start processing a paper
- `GET /papers/{paper_id}/status`: Get paper processing status
- `GET /papers/{paper_id}/progress`: Get detailed progress information
- `GET /papers/stats`: Get overall statistics

### WebSocket Endpoints

Real-time updates are available via WebSocket:

- `ws://localhost:8000/ws`: Global updates
- `ws://localhost:8000/ws/{paper_id}`: Paper-specific updates

## Testing WebSocket Connection

You can test the WebSocket connection using any WebSocket client. For example, using `websocat`:

```bash
websocat ws://localhost:8000/ws/{paper_id}
```

## Expected Results

When processing a paper, you should observe:

1. The paper progresses through the states: UPLOADED → QUEUED → PROCESSING → EXTRACTING_ENTITIES → EXTRACTING_RELATIONSHIPS → BUILDING_KNOWLEDGE_GRAPH → ANALYZED → IMPLEMENTATION_READY
2. Entity and relationship counts increase as the processing progresses
3. The knowledge graph is updated with new entities and relationships
4. Real-time status updates are sent through WebSocket

## Troubleshooting

If you encounter issues:

- Check MongoDB connection in `src/paper_processing/config/settings.py`
- Check Neo4j connection in `src/paper_processing/config/settings.py`
- Check Redis connection in `src/paper_processing/tasks/celery_app.py`
- Ensure all services are running properly
- Check logs for detailed error messages