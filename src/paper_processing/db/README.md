# Database Models for Paper Processing Pipeline

## Overview

This directory contains the database models and connection management for the Paper Processing Pipeline. It provides the persistence layer for storing and retrieving papers and their processing status.

## Components

### Connection Management

The `connection.py` file handles MongoDB connection setup and management:

- **Connection Pool**: Manages a pool of connections for efficient database access
- **Configuration**: Supports configuration via environment variables or parameters
- **Collection Management**: Provides access to MongoDB collections
- **Index Creation**: Creates indexes for efficient queries

### Paper Model

The `models.py` file defines the database models for papers:

- **Document Conversion**: Converts between Pydantic models and MongoDB documents
- **CRUD Operations**: Provides methods for creating, reading, updating, and deleting papers
- **Status Updates**: Manages paper status changes and processing history
- **Search and Filtering**: Supports searching and filtering papers

## Database Schema

The Paper Processing Pipeline uses MongoDB as its primary database. The schema includes the following collections:

### Papers Collection

Stores papers and their processing status:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Attention Is All You Need",
  "authors": [
    {"name": "Ashish Vaswani", "affiliation": "Google Brain"}
  ],
  "abstract": "The dominant sequence transduction models...",
  "year": 2017,
  "doi": "10.48550/arXiv.1706.03762",
  "url": "https://arxiv.org/abs/1706.03762",
  "filename": "123e4567-e89b-12d3-a456-426614174000.pdf",
  "file_path": "/app/uploads/123e4567-e89b-12d3-a456-426614174000.pdf",
  "content_type": "application/pdf",
  "original_filename": "attention_is_all_you_need.pdf",
  "uploaded_by": "researcher",
  "uploaded_at": "2025-03-01T10:30:00Z",
  "status": "uploaded",
  "processing_history": [
    {
      "timestamp": "2025-03-01T10:30:00Z",
      "status": "uploaded",
      "message": "Paper uploaded successfully"
    }
  ],
  "entities": [],
  "relationships": [],
  "statistics": null,
  "knowledge_graph_id": null,
  "implementation_ready": false,
  "metadata": {
    "keywords": ["transformer", "attention", "neural machine translation"]
  }
}
```

### Batches Collection

Stores batch processing information:

```json
{
  "id": "batch-123e4567-e89b-12d3-a456-426614174000",
  "paper_ids": ["123e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174001"],
  "status": "in_progress",
  "created_at": "2025-03-01T10:30:00Z",
  "created_by": "researcher",
  "completed_at": null,
  "paper_statuses": {
    "123e4567-e89b-12d3-a456-426614174000": "completed",
    "123e4567-e89b-12d3-a456-426614174001": "in_progress"
  },
  "options": {
    "extract_citations": true,
    "build_knowledge_graph": true
  }
}
```

### Tasks Collection

Stores Celery task information:

```json
{
  "task_id": "4f8ed542-a2ea-4a47-92b3-5fe0ae7740f2",
  "paper_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "in_progress",
  "created_at": "2025-03-01T10:35:00Z",
  "started_at": "2025-03-01T10:35:05Z",
  "completed_at": null,
  "task_type": "process_paper",
  "task_args": {"paper_id": "123e4567-e89b-12d3-a456-426614174000"},
  "task_kwargs": {"priority": 5},
  "result": null,
  "error": null
}
```

## Usage

The database models are used by the Celery tasks and API endpoints to store and retrieve paper information:

```python
# Initialize the database connection
await db_connection.connect()

# Get collections
papers_collection = await db_connection.get_collection('papers')

# Initialize the paper model
paper_model = PaperModel(papers_collection)

# Find a paper by ID
paper = await paper_model.find_by_id(paper_id)

# Update paper status
updated_paper = await paper_model.update_status(
    paper_id,
    PaperStatus.PROCESSING,
    "Processing started"
)

# Save a paper
await paper_model.save(paper)

# Search papers
results = await paper_model.search(
    query="transformer",
    status=PaperStatus.ANALYZED,
    limit=10
)
```

## Future Work

- **Schema Migration**: Add support for schema migrations
- **Caching**: Implement caching for frequently accessed papers
- **Sharding**: Prepare for sharded collections for horizontal scaling
- **Backup and Recovery**: Implement backup and recovery procedures
- **Performance Optimization**: Add more indexes and query optimizations