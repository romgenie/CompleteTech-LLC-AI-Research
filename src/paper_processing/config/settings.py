"""
Configuration settings for the Paper Processing Pipeline.

This module defines the configuration settings for the Paper Processing Pipeline,
using Pydantic for validation and loading from environment variables.

Current Implementation Status:
- Settings models defined ✓
- Environment variable loading ✓
- Default configuration values ✓
- Validation rules ✓

Upcoming Development:
- Configuration file loading
- Dynamic configuration reloading
- Secrets management
- Environment-specific configurations
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from pydantic import Field, validator, PostgresDsn, AnyHttpUrl, BaseModel
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    """Database connection settings."""
    
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI"
    )
    database_name: str = Field(
        default="paper_processing",
        description="Database name"
    )
    max_pool_size: int = Field(
        default=10,
        description="Maximum connection pool size",
        ge=1
    )
    min_pool_size: int = Field(
        default=1,
        description="Minimum connection pool size",
        ge=1
    )
    max_idle_time_ms: int = Field(
        default=30000,
        description="Maximum connection idle time in milliseconds",
        ge=1000
    )
    connect_timeout_ms: int = Field(
        default=5000,
        description="Connection timeout in milliseconds",
        ge=1000
    )
    socket_timeout_ms: int = Field(
        default=30000,
        description="Socket timeout in milliseconds",
        ge=1000
    )
    server_selection_timeout_ms: int = Field(
        default=5000,
        description="Server selection timeout in milliseconds",
        ge=1000
    )
    wait_queue_timeout_ms: int = Field(
        default=10000,
        description="Wait queue timeout in milliseconds",
        ge=1000
    )


class CelerySettings(BaseModel):
    """Celery task queue settings."""
    
    broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL"
    )
    task_serializer: str = Field(
        default="json",
        description="Task serialization format"
    )
    result_serializer: str = Field(
        default="json",
        description="Result serialization format"
    )
    accept_content: List[str] = Field(
        default=["json"],
        description="Accepted content types"
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for Celery"
    )
    worker_concurrency: Optional[int] = Field(
        default=None,
        description="Worker concurrency (None for auto)"
    )
    task_acks_late: bool = Field(
        default=True,
        description="Acknowledge tasks after execution"
    )
    task_reject_on_worker_lost: bool = Field(
        default=True,
        description="Reject tasks if worker is lost"
    )
    worker_prefetch_multiplier: int = Field(
        default=1,
        description="Worker prefetch multiplier",
        ge=1
    )
    task_default_retry_delay: int = Field(
        default=60,
        description="Default retry delay in seconds",
        ge=1
    )
    task_max_retries: int = Field(
        default=3,
        description="Maximum number of retries",
        ge=0
    )
    result_expires: int = Field(
        default=86400,
        description="Result expiration time in seconds",
        ge=1
    )


class FilesSettings(BaseModel):
    """File storage settings."""
    
    upload_dir: str = Field(
        default="/tmp/paper_processing/uploads",
        description="Directory for uploaded files"
    )
    max_upload_size_mb: int = Field(
        default=50,
        description="Maximum upload size in megabytes",
        ge=1
    )
    allowed_extensions: List[str] = Field(
        default=["pdf", "txt", "html", "htm", "xml"],
        description="Allowed file extensions"
    )
    allowed_mime_types: List[str] = Field(
        default=[
            "application/pdf",
            "text/plain",
            "text/html",
            "application/xhtml+xml",
            "text/xml",
            "application/xml"
        ],
        description="Allowed MIME types"
    )
    

class LoggingSettings(BaseModel):
    """Logging configuration."""
    
    level: str = Field(
        default="INFO",
        description="Logging level"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Log file path (None for stdout)"
    )
    
    @validator('level')
    def validate_level(cls, v):
        """Validate logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in valid_levels:
            raise ValueError(f"Invalid logging level. Must be one of {valid_levels}")
        return v


class APISettings(BaseModel):
    """API settings."""
    
    host: str = Field(
        default="0.0.0.0",
        description="API host"
    )
    port: int = Field(
        default=8000,
        description="API port",
        ge=1,
        le=65535
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    workers: int = Field(
        default=1,
        description="Number of worker processes",
        ge=1
    )
    allow_origins: List[str] = Field(
        default=["*"],
        description="Allowed origins for CORS"
    )
    auth_required: bool = Field(
        default=True,
        description="Whether authentication is required"
    )
    token_expiration_minutes: int = Field(
        default=60,
        description="Token expiration time in minutes",
        ge=1
    )


class ExtractionSettings(BaseModel):
    """Extraction settings."""
    
    entity_confidence_threshold: float = Field(
        default=0.5,
        description="Minimum confidence threshold for entities",
        ge=0.0,
        le=1.0
    )
    relationship_confidence_threshold: float = Field(
        default=0.5,
        description="Minimum confidence threshold for relationships",
        ge=0.0,
        le=1.0
    )
    max_entities_per_paper: int = Field(
        default=1000,
        description="Maximum number of entities per paper",
        ge=1
    )
    max_relationships_per_paper: int = Field(
        default=5000,
        description="Maximum number of relationships per paper",
        ge=1
    )
    

class KnowledgeGraphSettings(BaseModel):
    """Knowledge Graph connection settings."""
    
    host: str = Field(
        default="localhost",
        description="Neo4j host for Knowledge Graph"
    )
    port: int = Field(
        default=7687,
        description="Neo4j port for Knowledge Graph",
        ge=1,
        le=65535
    )
    user: str = Field(
        default="neo4j",
        description="Neo4j username for Knowledge Graph"
    )
    password: str = Field(
        default="password",
        description="Neo4j password for Knowledge Graph"
    )
    database: str = Field(
        default="neo4j",
        description="Neo4j database name for Knowledge Graph"
    )
    encryption: bool = Field(
        default=False,
        description="Whether to use encryption for Neo4j connection"
    )
    max_connection_pool_size: int = Field(
        default=50,
        description="Maximum connection pool size for Neo4j",
        ge=1
    )
    connection_timeout: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=1
    )


class TemporalEvolutionSettings(BaseModel):
    """Temporal Evolution Layer settings."""
    
    enabled: bool = Field(
        default=True,
        description="Whether to enable Temporal Evolution Layer integration"
    )
    host: str = Field(
        default="localhost",
        description="Neo4j host for Temporal Evolution Layer"
    )
    port: int = Field(
        default=7687,
        description="Neo4j port for Temporal Evolution Layer",
        ge=1,
        le=65535
    )
    user: str = Field(
        default="neo4j",
        description="Neo4j username for Temporal Evolution Layer"
    )
    password: str = Field(
        default="password",
        description="Neo4j password for Temporal Evolution Layer"
    )
    database: str = Field(
        default="neo4j",
        description="Neo4j database name for Temporal Evolution Layer"
    )
    encryption: bool = Field(
        default=False,
        description="Whether to use encryption for Neo4j connection"
    )
    use_same_connection: bool = Field(
        default=True,
        description="Whether to use the same Neo4j connection as Knowledge Graph"
    )
    

class IntegrationSettings(BaseModel):
    """Integration settings."""
    
    knowledge_graph_api_url: str = Field(
        default="http://localhost:8000/knowledge-graph",
        description="Knowledge Graph API URL"
    )
    research_impl_api_url: str = Field(
        default="http://localhost:8000/research-implementation",
        description="Research Implementation API URL"
    )
    research_orch_api_url: str = Field(
        default="http://localhost:8000/research-orchestration",
        description="Research Orchestration API URL"
    )
    knowledge_extraction_api_url: str = Field(
        default="http://localhost:8000/knowledge-extraction",
        description="Knowledge Extraction API URL"
    )
    connect_timeout: int = Field(
        default=5,
        description="Connection timeout in seconds",
        ge=1
    )
    read_timeout: int = Field(
        default=30,
        description="Read timeout in seconds",
        ge=1
    )
    use_mocks: bool = Field(
        default=False,
        description="Use mock data instead of actual integration"
    )


class Settings(BaseSettings):
    """
    Main configuration settings for the Paper Processing Pipeline.
    
    This class provides all configuration settings, loaded from environment
    variables with fallback to default values.
    """
    
    # Environment name
    environment: str = Field(
        default="development",
        description="Environment name"
    )
    
    # Project information
    project_name: str = Field(
        default="Paper Processing Pipeline",
        description="Project name"
    )
    version: str = Field(
        default="0.1.0",
        description="Project version"
    )
    
    # Component settings
    database: DatabaseSettings = Field(
        default_factory=DatabaseSettings,
        description="Database settings"
    )
    celery: CelerySettings = Field(
        default_factory=CelerySettings,
        description="Celery settings"
    )
    files: FilesSettings = Field(
        default_factory=FilesSettings,
        description="File storage settings"
    )
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging settings"
    )
    api: APISettings = Field(
        default_factory=APISettings,
        description="API settings"
    )
    extraction: ExtractionSettings = Field(
        default_factory=ExtractionSettings,
        description="Extraction settings"
    )
    knowledge_graph: KnowledgeGraphSettings = Field(
        default_factory=KnowledgeGraphSettings,
        description="Knowledge Graph settings"
    )
    temporal_evolution: TemporalEvolutionSettings = Field(
        default_factory=TemporalEvolutionSettings,
        description="Temporal Evolution Layer settings"
    )
    integration: IntegrationSettings = Field(
        default_factory=IntegrationSettings,
        description="Integration settings"
    )
    
    class Config:
        """Pydantic configuration."""
        env_nested_delimiter = '__'
        env_prefix = 'PAPER_PROCESSING_'
        case_sensitive = False
        env_file = '.env'


# Create settings instance
settings = Settings()


def configure_logging():
    """
    Configure logging based on settings.
    
    This function sets up logging with the configured level and format.
    """
    log_level = getattr(logging, settings.logging.level)
    log_format = settings.logging.format
    
    if settings.logging.file_path:
        logging.basicConfig(
            level=log_level,
            format=log_format,
            filename=settings.logging.file_path
        )
    else:
        logging.basicConfig(
            level=log_level,
            format=log_format
        )
    
    # Reduce verbosity of some loggers
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at level {settings.logging.level}")


def get_settings() -> Settings:
    """
    Get the current settings.
    
    This function is used to provide dependency injection for settings.
    
    Returns:
        The current settings instance
    """
    return settings


# Convenience constants for common settings

# Knowledge Graph
KNOWLEDGE_GRAPH_HOST = settings.knowledge_graph.host
KNOWLEDGE_GRAPH_PORT = settings.knowledge_graph.port
KNOWLEDGE_GRAPH_USER = settings.knowledge_graph.user
KNOWLEDGE_GRAPH_PASSWORD = settings.knowledge_graph.password
KNOWLEDGE_GRAPH_DATABASE = settings.knowledge_graph.database

# Temporal Evolution Layer
TEMPORAL_EVOLUTION_ENABLED = settings.temporal_evolution.enabled
TEMPORAL_EVOLUTION_HOST = settings.temporal_evolution.host if not settings.temporal_evolution.use_same_connection else KNOWLEDGE_GRAPH_HOST
TEMPORAL_EVOLUTION_PORT = settings.temporal_evolution.port if not settings.temporal_evolution.use_same_connection else KNOWLEDGE_GRAPH_PORT
TEMPORAL_EVOLUTION_USER = settings.temporal_evolution.user if not settings.temporal_evolution.use_same_connection else KNOWLEDGE_GRAPH_USER
TEMPORAL_EVOLUTION_PASSWORD = settings.temporal_evolution.password if not settings.temporal_evolution.use_same_connection else KNOWLEDGE_GRAPH_PASSWORD
TEMPORAL_EVOLUTION_DATABASE = settings.temporal_evolution.database if not settings.temporal_evolution.use_same_connection else KNOWLEDGE_GRAPH_DATABASE

# Extraction settings
ENTITY_CONFIDENCE_THRESHOLD = settings.extraction.entity_confidence_threshold
RELATIONSHIP_CONFIDENCE_THRESHOLD = settings.extraction.relationship_confidence_threshold
MAX_ENTITIES = settings.extraction.max_entities_per_paper
MAX_RELATIONSHIPS = settings.extraction.max_relationships_per_paper