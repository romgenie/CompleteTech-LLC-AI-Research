"""
Unit tests for configuration settings.

This module tests the configuration settings functionality.
"""

import pytest
import os
from unittest.mock import patch
import logging

from paper_processing.config.settings import (
    DatabaseSettings,
    CelerySettings,
    FilesSettings,
    LoggingSettings,
    APISettings,
    ExtractionSettings,
    IntegrationSettings,
    Settings,
    configure_logging,
    get_settings
)


def test_database_settings():
    """Test database settings."""
    # Default settings
    settings = DatabaseSettings()
    assert settings.mongodb_uri == "mongodb://localhost:27017"
    assert settings.database_name == "paper_processing"
    assert settings.max_pool_size == 10
    assert settings.min_pool_size == 1
    
    # Custom settings
    settings = DatabaseSettings(
        mongodb_uri="mongodb://user:pass@host:27017",
        database_name="custom_db",
        max_pool_size=20,
        min_pool_size=5
    )
    assert settings.mongodb_uri == "mongodb://user:pass@host:27017"
    assert settings.database_name == "custom_db"
    assert settings.max_pool_size == 20
    assert settings.min_pool_size == 5


def test_celery_settings():
    """Test Celery settings."""
    # Default settings
    settings = CelerySettings()
    assert settings.broker_url == "redis://localhost:6379/0"
    assert settings.result_backend == "redis://localhost:6379/0"
    assert settings.task_serializer == "json"
    assert settings.result_serializer == "json"
    assert settings.accept_content == ["json"]
    assert settings.timezone == "UTC"
    
    # Custom settings
    settings = CelerySettings(
        broker_url="redis://custom-host:6379/1",
        result_backend="redis://custom-host:6379/1",
        worker_concurrency=4,
        task_max_retries=5
    )
    assert settings.broker_url == "redis://custom-host:6379/1"
    assert settings.result_backend == "redis://custom-host:6379/1"
    assert settings.worker_concurrency == 4
    assert settings.task_max_retries == 5


def test_files_settings():
    """Test files settings."""
    # Default settings
    settings = FilesSettings()
    assert settings.upload_dir == "/tmp/paper_processing/uploads"
    assert settings.max_upload_size_mb == 50
    assert "pdf" in settings.allowed_extensions
    assert "application/pdf" in settings.allowed_mime_types
    
    # Custom settings
    settings = FilesSettings(
        upload_dir="/custom/upload/dir",
        max_upload_size_mb=100,
        allowed_extensions=["pdf", "docx"]
    )
    assert settings.upload_dir == "/custom/upload/dir"
    assert settings.max_upload_size_mb == 100
    assert settings.allowed_extensions == ["pdf", "docx"]


def test_logging_settings():
    """Test logging settings."""
    # Default settings
    settings = LoggingSettings()
    assert settings.level == "INFO"
    assert "%(asctime)s" in settings.format
    assert settings.file_path is None
    
    # Custom settings
    settings = LoggingSettings(
        level="DEBUG",
        file_path="/var/log/paper_processing.log"
    )
    assert settings.level == "DEBUG"
    assert settings.file_path == "/var/log/paper_processing.log"
    
    # Invalid level
    with pytest.raises(ValueError):
        LoggingSettings(level="INVALID")


def test_api_settings():
    """Test API settings."""
    # Default settings
    settings = APISettings()
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.debug is False
    assert settings.workers == 1
    assert settings.allow_origins == ["*"]
    assert settings.auth_required is True
    
    # Custom settings
    settings = APISettings(
        host="127.0.0.1",
        port=9000,
        debug=True,
        workers=4,
        allow_origins=["http://localhost:3000"],
        auth_required=False
    )
    assert settings.host == "127.0.0.1"
    assert settings.port == 9000
    assert settings.debug is True
    assert settings.workers == 4
    assert settings.allow_origins == ["http://localhost:3000"]
    assert settings.auth_required is False


def test_extraction_settings():
    """Test extraction settings."""
    # Default settings
    settings = ExtractionSettings()
    assert settings.entity_confidence_threshold == 0.5
    assert settings.relationship_confidence_threshold == 0.5
    assert settings.max_entities_per_paper == 1000
    assert settings.max_relationships_per_paper == 5000
    
    # Custom settings
    settings = ExtractionSettings(
        entity_confidence_threshold=0.7,
        relationship_confidence_threshold=0.8,
        max_entities_per_paper=500
    )
    assert settings.entity_confidence_threshold == 0.7
    assert settings.relationship_confidence_threshold == 0.8
    assert settings.max_entities_per_paper == 500
    
    # Invalid confidence threshold
    with pytest.raises(ValueError):
        ExtractionSettings(entity_confidence_threshold=1.5)
    
    with pytest.raises(ValueError):
        ExtractionSettings(relationship_confidence_threshold=-0.1)


def test_integration_settings():
    """Test integration settings."""
    # Default settings
    settings = IntegrationSettings()
    assert settings.knowledge_graph_api_url == "http://localhost:8000/knowledge-graph"
    assert settings.research_impl_api_url == "http://localhost:8000/research-implementation"
    assert settings.research_orch_api_url == "http://localhost:8000/research-orchestration"
    assert settings.knowledge_extraction_api_url == "http://localhost:8000/knowledge-extraction"
    assert settings.connect_timeout == 5
    assert settings.read_timeout == 30
    assert settings.use_mocks is False
    
    # Custom settings
    settings = IntegrationSettings(
        knowledge_graph_api_url="http://custom-host:8000/knowledge-graph",
        connect_timeout=10,
        use_mocks=True
    )
    assert settings.knowledge_graph_api_url == "http://custom-host:8000/knowledge-graph"
    assert settings.connect_timeout == 10
    assert settings.use_mocks is True


def test_main_settings():
    """Test main settings."""
    # Default settings might be set to 'testing' in the test environment
    # We'll patch the environment variable to ensure the correct value
    with patch.dict(os.environ, {'PAPER_PROCESSING_ENVIRONMENT': 'development'}):
        settings = Settings()
        assert settings.environment == "development"
        assert settings.project_name == "Paper Processing Pipeline"
        assert settings.version == "0.1.0"
        assert isinstance(settings.database, DatabaseSettings)
        assert isinstance(settings.celery, CelerySettings)
        assert isinstance(settings.files, FilesSettings)
        assert isinstance(settings.logging, LoggingSettings)
        assert isinstance(settings.api, APISettings)
        assert isinstance(settings.extraction, ExtractionSettings)
        assert isinstance(settings.integration, IntegrationSettings)
    
    # Custom settings
    settings = Settings(
        environment="production",
        version="1.0.0",
        database={"mongodb_uri": "mongodb://prod-host:27017"},
        api={"port": 9000}
    )
    assert settings.environment == "production"
    assert settings.version == "1.0.0"
    assert settings.database.mongodb_uri == "mongodb://prod-host:27017"
    assert settings.api.port == 9000


def test_settings_env_vars():
    """Test loading settings from environment variables."""
    with patch.dict(os.environ, {
        "PAPER_PROCESSING_ENVIRONMENT": "production",
        "PAPER_PROCESSING_DATABASE__MONGODB_URI": "mongodb://env-host:27017",
        "PAPER_PROCESSING_CELERY__BROKER_URL": "redis://env-host:6379/0",
        "PAPER_PROCESSING_API__PORT": "9000"
    }):
        settings = Settings()
        assert settings.environment == "production"
        assert settings.database.mongodb_uri == "mongodb://env-host:27017"
        assert settings.celery.broker_url == "redis://env-host:6379/0"
        assert settings.api.port == 9000


def test_configure_logging():
    """Test configuring logging."""
    # Test with default settings
    with patch.object(logging, 'basicConfig') as mock_basic_config:
        with patch.object(logging, 'getLogger') as mock_get_logger:
            mock_logger = logging.getLogger('test')
            mock_get_logger.return_value = mock_logger
            
            # Configure logging
            configure_logging()
            
            # Check that basicConfig was called
            mock_basic_config.assert_called_once()
            assert mock_basic_config.call_args[1]['level'] == logging.INFO


def test_get_settings():
    """Test getting settings."""
    # Instead of checking the environment value (which may be set to 'testing' in tests),
    # let's just check that get_settings() returns the global settings instance
    with patch('paper_processing.config.settings.settings', Settings(environment="development")):
        # Call get_settings
        settings = get_settings()
        
        # Check that it returns the global settings
        assert isinstance(settings, Settings)
        assert settings.environment == "development"