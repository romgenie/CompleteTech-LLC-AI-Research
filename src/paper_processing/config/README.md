# Configuration for Paper Processing Pipeline

## Overview

This directory contains the configuration management for the Paper Processing Pipeline. It provides a structured way to configure the pipeline through environment variables, configuration files, and default values.

## Components

### Settings

The `settings.py` file defines the configuration settings using Pydantic models:

- **Database Settings**: MongoDB connection parameters
- **Celery Settings**: Task queue configuration
- **Files Settings**: File storage and upload settings
- **Logging Settings**: Logging configuration
- **API Settings**: API server settings
- **Extraction Settings**: Knowledge extraction parameters
- **Integration Settings**: External system integration configuration

## Environment Variables

All settings can be configured through environment variables with the prefix `PAPER_PROCESSING_`. Nested settings use double underscores (`__`) as delimiters.

Examples:

```
PAPER_PROCESSING_ENVIRONMENT=production
PAPER_PROCESSING_DATABASE__MONGODB_URI=mongodb://user:password@mongo:27017
PAPER_PROCESSING_CELERY__BROKER_URL=redis://redis:6379/0
PAPER_PROCESSING_LOGGING__LEVEL=INFO
```

## Configuration Files

The settings can also be loaded from a `.env` file in the project root:

```
PAPER_PROCESSING_ENVIRONMENT=development
PAPER_PROCESSING_DATABASE__MONGODB_URI=mongodb://localhost:27017
PAPER_PROCESSING_CELERY__BROKER_URL=redis://localhost:6379/0
PAPER_PROCESSING_LOGGING__LEVEL=DEBUG
```

## Default Values

All settings have sensible defaults that allow the system to run in a development environment without additional configuration.

## Usage

```python
from paper_processing.config.settings import settings, get_settings

# Access settings directly
mongodb_uri = settings.database.mongodb_uri
broker_url = settings.celery.broker_url

# Use dependency injection
def get_db(settings = Depends(get_settings)):
    return connect_to_db(settings.database.mongodb_uri)

# Configure logging
from paper_processing.config.settings import configure_logging
configure_logging()
```

## Environment-Specific Configuration

The settings support different environments through the `environment` setting:

- **development**: Local development with debug options
- **testing**: Used for running tests
- **staging**: Pre-production environment
- **production**: Production settings

## Validation

All settings are validated using Pydantic, which ensures:

- Type safety
- Value constraints
- Format validation
- Required fields

## Future Work

- **Configuration Files**: Support for YAML and JSON configuration files
- **Dynamic Reloading**: Runtime configuration updates
- **Secrets Management**: Better handling of sensitive information
- **Environment Detection**: Automatic environment detection
- **Configuration UI**: Admin interface for managing configuration