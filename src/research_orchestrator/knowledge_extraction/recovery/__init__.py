"""
Recovery and error handling system for the Knowledge Extraction Pipeline.

This package provides advanced error recovery mechanisms including error classification,
intelligent retry strategies, transactional processing, checkpointing, circuit breakers,
and progressive fallback strategies.
"""

from .errors import (
    # Error categories
    ErrorCategory,
    ErrorSeverity,
    
    # Error classes
    ProcessingError,
    DocumentProcessingError,
    DocumentReadError,
    DocumentParseError,
    DocumentEncodingError,
    UrlProcessingError,
    EntityRecognitionError,
    NoEntitiesFoundError,
    EntityExtractionError,
    RelationshipExtractionError,
    NoRelationshipsFoundError,
    KnowledgeGraphError,
    GraphDatabaseError,
    SchemaValidationError,
    
    # Helper functions
    classify_exception,
    handle_processing_error,
    create_fallback_result
)

from .retry import (
    RetryStrategy,
    RetryResult,
    RetryManager,
    retry,
    RetryContext
)

from .transaction import (
    TransactionStatus,
    OperationStatus,
    Operation,
    Transaction,
    TransactionContext,
    TransactionManager,
    transaction_manager
)

from .checkpoint import (
    Checkpoint,
    CheckpointError,
    CheckpointManager,
    checkpoint_manager,
    CheckpointedTask
)

from .circuit_breaker import (
    CircuitState, 
    CircuitOpenError,
    CircuitBreaker,
    get_circuit_breaker,
    circuit_protected,
    circuit_breaker_registry
)

from .fallback import (
    FallbackResult,
    ExtractionLevel,
    FallbackStrategy,
    ProgressiveExtractor,
    with_fallback
)

# Version information
__version__ = "0.2.0"

# All exported symbols
__all__ = [
    # Error system
    "ErrorCategory", "ErrorSeverity", "ProcessingError",
    "DocumentProcessingError", "DocumentReadError", "DocumentParseError",
    "DocumentEncodingError", "UrlProcessingError", "EntityRecognitionError",
    "NoEntitiesFoundError", "EntityExtractionError", "RelationshipExtractionError",
    "NoRelationshipsFoundError", "KnowledgeGraphError", "GraphDatabaseError",
    "SchemaValidationError", "classify_exception", "handle_processing_error",
    "create_fallback_result",
    
    # Retry system
    "RetryStrategy", "RetryResult", "RetryManager", "retry", "RetryContext",
    
    # Transaction system
    "TransactionStatus", "OperationStatus", "Operation", "Transaction",
    "TransactionContext", "TransactionManager", "transaction_manager",
    
    # Checkpoint system
    "Checkpoint", "CheckpointError", "CheckpointManager", "checkpoint_manager",
    "CheckpointedTask",
    
    # Circuit breaker system
    "CircuitState", "CircuitOpenError", "CircuitBreaker", "get_circuit_breaker",
    "circuit_protected", "circuit_breaker_registry",
    
    # Progressive fallback system
    "FallbackResult", "ExtractionLevel", "FallbackStrategy", "ProgressiveExtractor",
    "with_fallback"
]