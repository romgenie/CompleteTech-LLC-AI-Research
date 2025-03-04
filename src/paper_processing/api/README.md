# API Endpoints for Paper Processing Pipeline

## Overview

This directory contains the FastAPI routes for the Paper Processing Pipeline, providing endpoints for controlling paper processing and retrieving status information. These endpoints are the primary interface for interacting with the Paper Processing Pipeline.

## Endpoints

### Paper Processing

- **POST `/papers/{paper_id}/process`**: Initiate processing for a specific paper
- **POST `/papers/batch/process`**: Process multiple papers in batch
- **GET `/papers/{paper_id}/status`**: Get the processing status of a paper
- **GET `/papers/{paper_id}/progress`**: Get detailed progress information
- **POST `/papers/{paper_id}/cancel`**: Cancel ongoing processing

### Statistics and Search

- **GET `/papers/stats`**: Get processing statistics
- **GET `/papers/search`**: Search for papers with filtering options

## Implementation Status

The API endpoints structure has been implemented as part of the Paper Processing Pipeline foundation (Phase 3.5). The current implementation includes:

- ✅ API route structure and documentation
- ✅ Request and response validation schemas
- ✅ Status reporting endpoints
- ✅ Error handling framework
- 🔄 Full task execution (coming in next sprints)
- 🔄 WebSocket integration (coming in next sprints)

## Example Usage

### Processing a Paper

```bash
curl -X POST "http://localhost:8000/papers/123e4567-e89b-12d3-a456-426614174000/process" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "options": {
      "extract_citations": true,
      "build_knowledge_graph": true,
      "check_implementation_readiness": true
    },
    "priority": 5
  }'
```

### Getting Paper Status

```bash
curl -X GET "http://localhost:8000/papers/123e4567-e89b-12d3-a456-426614174000/status" \
  -H "Authorization: Bearer {token}"
```

### Searching Papers

```bash
curl -X GET "http://localhost:8000/papers/search?query=transformer&status=analyzed&limit=10" \
  -H "Authorization: Bearer {token}"
```

## Authentication and Authorization

All API endpoints require authentication using JWT tokens. The token should be included in the `Authorization` header with the `Bearer` scheme.

```
Authorization: Bearer {token}
```

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success",
  "data": {
    // Response data specific to the endpoint
  },
  "meta": {
    // Metadata about the response (pagination, etc.)
  }
}
```

For error responses:

```json
{
  "status": "error",
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

## WebSocket Integration

In addition to the REST endpoints, the API will provide WebSocket endpoints for real-time updates:

- **WebSocket `/ws/papers/{paper_id}/status`**: Real-time status updates for a paper
- **WebSocket `/ws/papers/all/status`**: Updates for all papers (with filtering)

These endpoints are currently being implemented and will be available in future sprints.

## Future Enhancements

- **Batch Processing Improvements**: Enhanced batch operations with progress tracking
- **Advanced Search**: More sophisticated search and filtering options
- **Streaming Responses**: Support for streaming large responses
- **Rate Limiting**: Protection against excessive API usage
- **API Versioning**: Support for versioned endpoints