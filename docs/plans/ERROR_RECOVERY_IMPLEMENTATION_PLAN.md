# Advanced Error Recovery Implementation Plan

## Overview

This plan outlines a comprehensive approach to enhancing error recovery capabilities in the Knowledge Extraction Pipeline, focusing on creating a more resilient system that can handle failures gracefully and recover with minimal manual intervention.

## Goals

1. Minimize processing failures by implementing intelligent retry mechanisms
2. Improve processing resilience through transaction-based operations
3. Enable partial results recovery for salvaging work from failed jobs
4. Implement progressive fallback strategies to handle dependency failures
5. Enhance monitoring and diagnostics for better issue resolution
6. Provide user-friendly recovery options for manual intervention

## Implementation Phases

### Phase 1: Error Classification and Intelligent Retry (Week 1)

#### 1.1 Exception Taxonomy
- Create a comprehensive exception classification system
- Categorize errors as transient vs. permanent
- Tag exceptions by source (network, I/O, parsing, processing)
- Implement error severity levels

```python
class ErrorCategory(Enum):
    TRANSIENT = "transient"  # Temporary errors that should be retried
    PERMANENT = "permanent"  # Permanent errors that shouldn't be retried
    DATA_RELATED = "data"    # Errors related to input data quality
    SYSTEM = "system"        # System-level errors (resources, permissions)
    DEPENDENCY = "dependency"  # External dependency failures

class ErrorSeverity(Enum):
    CRITICAL = "critical"    # Complete failure, no recovery possible
    HIGH = "high"            # Significant impact, recovery challenging
    MEDIUM = "medium"        # Partial impact, recovery possible
    LOW = "low"              # Minor impact, simple recovery
```

#### 1.2 Enhanced Exception Handling
- Create a base `ProcessingError` class hierarchy
- Implement error context capturing (what was being processed)
- Add error classification metadata
- Create specialized exception types for each processing stage

```python
class ProcessingError(Exception):
    """Base class for all processing errors with metadata."""
    
    def __init__(self, message, category=ErrorCategory.PERMANENT, 
                 severity=ErrorSeverity.MEDIUM, context=None, retry_suggested=False):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.retry_suggested = retry_suggested
        self.timestamp = datetime.now().isoformat()
        
    def to_dict(self):
        """Convert the error to a dictionary for storage/transmission."""
        return {
            "message": str(self),
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "retry_suggested": self.retry_suggested,
            "timestamp": self.timestamp
        }
```

#### 1.3 Intelligent Retry Manager
- Create a `RetryManager` class to handle different retry strategies
- Implement exponential backoff with jitter
- Add retry quotas based on error types
- Create custom retry handlers for different error categories

```python
class RetryStrategy:
    """Defines how retries should be handled for specific error types."""
    
    def __init__(self, max_retries=3, initial_delay=1, backoff_factor=2.0,
                 jitter=0.1, max_delay=60):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.max_delay = max_delay
        
    def calculate_delay(self, attempt):
        """Calculate delay for this attempt with jitter."""
        delay = min(
            self.initial_delay * (self.backoff_factor ** attempt),
            self.max_delay
        )
        # Add jitter to avoid thundering herd
        jitter_amount = self.jitter * delay
        return delay + random.uniform(-jitter_amount, jitter_amount)

class RetryManager:
    """Manages retry strategies for different error types."""
    
    DEFAULT_STRATEGY = RetryStrategy(max_retries=3, initial_delay=1)
    
    STRATEGIES = {
        # Network errors get more retries with longer backoff
        ErrorCategory.TRANSIENT: RetryStrategy(
            max_retries=5, initial_delay=2, backoff_factor=2.5, max_delay=300
        ),
        # Data errors get fewer retries with shorter backoff
        ErrorCategory.DATA_RELATED: RetryStrategy(
            max_retries=2, initial_delay=1, backoff_factor=1.5, max_delay=10
        ),
        # System errors get medium retries with longer initial delay
        ErrorCategory.SYSTEM: RetryStrategy(
            max_retries=3, initial_delay=5, backoff_factor=2.0, max_delay=120
        ),
        # Dependency errors get many retries with longer backoff
        ErrorCategory.DEPENDENCY: RetryStrategy(
            max_retries=8, initial_delay=10, backoff_factor=2.0, max_delay=600
        ),
    }
    
    @classmethod
    def get_strategy(cls, error):
        """Get the appropriate retry strategy for this error."""
        if isinstance(error, ProcessingError):
            return cls.STRATEGIES.get(error.category, cls.DEFAULT_STRATEGY)
        return cls.DEFAULT_STRATEGY
    
    @classmethod
    def should_retry(cls, error, attempt):
        """Determine if retry should be attempted based on the error and attempt number."""
        if isinstance(error, ProcessingError) and not error.retry_suggested:
            return False
            
        strategy = cls.get_strategy(error)
        return attempt < strategy.max_retries
    
    @classmethod
    def get_retry_delay(cls, error, attempt):
        """Get the retry delay for this error and attempt."""
        strategy = cls.get_strategy(error)
        return strategy.calculate_delay(attempt)
```

### Phase 2: Transaction-based Processing (Week 2)

#### 2.1 Transaction Manager
- Implement a transaction manager for atomic operations
- Add rollback capabilities for failed operations
- Implement compensation handlers for cleaning up resources
- Create transaction logs for audit and recovery

```python
class TransactionStatus(Enum):
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"

class Transaction:
    """Manages atomic operations with rollback capability."""
    
    def __init__(self, name, paper_id=None):
        self.name = name
        self.paper_id = paper_id
        self.status = TransactionStatus.PENDING
        self.operations = []
        self.compensation_handlers = []
        self.start_time = datetime.now()
        self.end_time = None
        self.id = str(uuid.uuid4())
        
    def add_operation(self, operation, compensation_handler=None):
        """Add an operation to the transaction with optional compensation."""
        self.operations.append(operation)
        self.compensation_handlers.append(compensation_handler)
        
    def commit(self):
        """Mark the transaction as committed."""
        self.status = TransactionStatus.COMMITTED
        self.end_time = datetime.now()
        
    def rollback(self):
        """Execute compensation handlers in reverse order."""
        try:
            # Execute compensation handlers in reverse order
            for handler in reversed(self.compensation_handlers):
                if handler:
                    handler()
            self.status = TransactionStatus.ROLLED_BACK
        except Exception as e:
            self.status = TransactionStatus.FAILED
            raise e
        finally:
            self.end_time = datetime.now()
            
    def to_dict(self):
        """Convert transaction to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "paper_id": self.paper_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "operation_count": len(self.operations)
        }
```

#### 2.2 State Transition Enhancements
- Extend the PaperStateMachine with transaction support
- Implement atomic transitions with compensation
- Add state checkpointing for recovery
- Create specialized state handlers for error conditions

```python
class TransactionalStateMachine(PaperStateMachine):
    """Enhanced state machine with transaction support."""
    
    def __init__(self, paper):
        super().__init__(paper)
        self.transaction_log = []
        
    def transition_to(self, state, message=None, metadata=None, transaction=None):
        """
        Transition to a new state with transaction support.
        
        Args:
            state: The target state
            message: Optional message describing the transition
            metadata: Additional data about the transition
            transaction: Optional transaction to use (will create one if not provided)
        
        Returns:
            True if transition succeeded, False otherwise
        """
        if not self.can_transition_to(state):
            return False
            
        # Create or use existing transaction
        txn = transaction or Transaction(f"Transition_{self.current_state}_to_{state}", 
                                       paper_id=self.paper.id)
            
        # Define the compensation handler
        def rollback_to_previous_state():
            self._set_state(self.current_state, 
                          f"Rolled back from {state} to {self.current_state}",
                          {"rollback": True})
            
        # Add the transition operation
        txn.add_operation(
            lambda: self._set_state(state, message, metadata),
            rollback_to_previous_state
        )
        
        try:
            # Execute the transition
            txn.operations[0]()
            txn.commit()
            self.transaction_log.append(txn.to_dict())
            return True
        except Exception as e:
            txn.rollback()
            self.transaction_log.append(txn.to_dict())
            logger.error(f"Failed to transition from {self.current_state} to {state}: {str(e)}")
            return False
```

#### 2.3 Checkpoint System
- Implement processing checkpoints at key stages
- Store intermediate results for partial recovery
- Add capabilities to resume from checkpoints
- Create checkpoint verification and validation

```python
class ProcessingCheckpoint:
    """Stores processing state for recovery purposes."""
    
    def __init__(self, paper_id, stage, data=None):
        self.paper_id = paper_id
        self.stage = stage
        self.data = data or {}
        self.timestamp = datetime.now()
        self.id = str(uuid.uuid4())
        
    def save(self):
        """Save checkpoint to persistent storage."""
        checkpoint_path = os.path.join(
            settings.CHECKPOINT_DIR, 
            f"{self.paper_id}_{self.stage}_{self.id}.json"
        )
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        
        with open(checkpoint_path, 'w') as f:
            json.dump({
                "id": self.id,
                "paper_id": self.paper_id,
                "stage": self.stage,
                "timestamp": self.timestamp.isoformat(),
                "data": self.data
            }, f)
        
        return checkpoint_path
        
    @classmethod
    def load(cls, paper_id, stage=None):
        """Load most recent checkpoint for paper_id, optionally filtered by stage."""
        checkpoint_dir = settings.CHECKPOINT_DIR
        pattern = f"{paper_id}_*.json"
        if stage:
            pattern = f"{paper_id}_{stage}_*.json"
            
        checkpoint_files = glob.glob(os.path.join(checkpoint_dir, pattern))
        
        if not checkpoint_files:
            return None
            
        # Find the most recent checkpoint
        newest_checkpoint = max(checkpoint_files, key=os.path.getmtime)
        
        with open(newest_checkpoint, 'r') as f:
            data = json.load(f)
            
        checkpoint = cls(data["paper_id"], data["stage"])
        checkpoint.id = data["id"]
        checkpoint.timestamp = datetime.fromisoformat(data["timestamp"])
        checkpoint.data = data["data"]
        
        return checkpoint
```

### Phase 3: Progressive Fallback Strategies (Week 3)

#### 3.1 Circuit Breaker Implementation ✅
- ✅ Added health checks for external dependencies
- ✅ Implemented circuit breaker pattern for failing services
- ✅ Created fallback behaviors for degraded operation
- ✅ Added self-healing capabilities

```python
class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejects all requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker for protecting against failing dependencies."""
    
    def __init__(self, name, failure_threshold=5, recovery_timeout=60, 
                 half_open_max_calls=1):
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.half_open_calls = 0
        self.last_failure_time = None
        self.last_success_time = None
        self._lock = threading.RLock()
        
    def execute(self, func, fallback=None, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            fallback: Optional fallback function if circuit is open
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of func or fallback if circuit is open
        """
        with self._lock:
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed
                if (self.last_failure_time and 
                    (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout):
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info(f"Circuit {self.name} transitioning from OPEN to HALF_OPEN")
                else:
                    # Circuit is open, use fallback if provided
                    if fallback:
                        return fallback(*args, **kwargs)
                    raise CircuitOpenError(f"Circuit {self.name} is OPEN")
                    
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    # Too many test calls already in progress
                    if fallback:
                        return fallback(*args, **kwargs)
                    raise CircuitOpenError(f"Circuit {self.name} is HALF_OPEN with max calls")
                # Increment the half-open call counter
                self.half_open_calls += 1
                
        # Execute the protected function
        try:
            result = func(*args, **kwargs)
            # Success, reset the circuit if it was half-open
            with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    logger.info(f"Circuit {self.name} recovered, transitioning to CLOSED")
                    self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_success_time = datetime.now()
                self.half_open_calls = max(0, self.half_open_calls - 1)
            return result
        except Exception as e:
            # Record the failure
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                
                # Check if we should open the circuit
                if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
                    logger.warning(f"Circuit {self.name} transitioning to OPEN after {self.failure_count} failures")
                    self.state = CircuitState.OPEN
                elif self.state == CircuitState.HALF_OPEN:
                    logger.warning(f"Circuit {self.name} failed in HALF_OPEN state, returning to OPEN")
                    self.state = CircuitState.OPEN
                    
                self.half_open_calls = max(0, self.half_open_calls - 1)
                
            # Use fallback if provided, otherwise re-raise
            if fallback:
                return fallback(*args, **kwargs)
            raise
```

#### 3.2 Dependency Fallback System ✅
- ✅ Implemented alternative processing paths for dependency failures
- ✅ Created simplified processing modes for degraded operation
- ✅ Added fallback data sources and methods
- ✅ Created recovery strategies for different dependency types

```python
class FallbackStrategy:
    """Defines fallback behaviors for dependency failures."""
    
    def __init__(self, name, primary_func, fallback_func=None, 
                 failure_handler=None, always_execute_primary=False):
        self.name = name
        self.primary_func = primary_func
        self.fallback_func = fallback_func
        self.failure_handler = failure_handler
        self.always_execute_primary = always_execute_primary
        self.circuit_breaker = CircuitBreaker(f"fallback_{name}")
        
    def execute(self, *args, **kwargs):
        """Execute with fallback strategy."""
        try:
            # Attempt to use primary function with circuit breaker
            return self.circuit_breaker.execute(
                self.primary_func, 
                self.fallback_func, 
                *args, **kwargs
            )
        except Exception as e:
            # If we have a failure handler, let it process the exception
            if self.failure_handler:
                return self.failure_handler(e, *args, **kwargs)
            # Otherwise re-raise
            raise
```

#### 3.3 Progressive Extraction Fallback 🟠
- ✅ Implemented multi-level entity extraction strategies
- ✅ Created relationship extraction fallback methods
- ✅ Added configuration for progressive degradation
- 🟠 Implementing document processor-specific fallbacks

```python
class ExtractionLevel(Enum):
    FULL = "full"           # Full extraction with all features
    STANDARD = "standard"   # Standard extraction with core features
    BASIC = "basic"         # Basic extraction with minimal features
    MINIMAL = "minimal"     # Minimal extraction for critical paths only

class ProgressiveExtractor:
    """Extractor that falls back to simpler methods on failure."""
    
    def __init__(self, start_level=ExtractionLevel.FULL):
        self.current_level = start_level
        self.fallback_count = 0
        self.max_fallbacks = len(ExtractionLevel) - 1
        self.results = {}
        
    def extract_entities(self, content, metadata=None):
        """Extract entities with progressive fallback."""
        metadata = metadata or {}
        original_level = self.current_level
        
        while self.fallback_count <= self.max_fallbacks:
            try:
                extractor = self._get_entity_extractor(self.current_level)
                entities = extractor.extract(content, metadata)
                
                # Store results and return
                self.results[self.current_level] = {
                    "entities": entities,
                    "count": len(entities),
                    "extraction_level": self.current_level.value
                }
                return entities
            except Exception as e:
                # Log the failure
                logger.warning(f"Entity extraction failed at level {self.current_level}: {str(e)}")
                
                # Try to fall back to a simpler method
                if self._fallback_to_next_level():
                    logger.info(f"Falling back to {self.current_level} extraction")
                    self.fallback_count += 1
                else:
                    # No more fallbacks available
                    logger.error(f"All entity extraction methods failed")
                    # Reset to original level for next time
                    self.current_level = original_level
                    raise EntityExtractionError(f"All extraction methods failed: {str(e)}")
        
        # Reset to original level for next time
        self.current_level = original_level
        return []
        
    def _fallback_to_next_level(self):
        """Try to fall back to the next simpler level."""
        levels = list(ExtractionLevel)
        current_index = levels.index(self.current_level)
        
        if current_index < len(levels) - 1:
            self.current_level = levels[current_index + 1]
            return True
        return False
        
    def _get_entity_extractor(self, level):
        """Get the appropriate extractor for the current level."""
        if level == ExtractionLevel.FULL:
            # Full extraction with all features
            return CombinedEntityRecognizer({
                "extractors": ["ai", "scientific", "pattern"],
                "confidence_threshold": 0.7
            })
        elif level == ExtractionLevel.STANDARD:
            # Standard extraction with core features
            return CombinedEntityRecognizer({
                "extractors": ["ai", "pattern"],
                "confidence_threshold": 0.6
            })
        elif level == ExtractionLevel.BASIC:
            # Basic extraction with minimal features
            return EntityRecognizerFactory.create_recognizer("ai", {
                "confidence_threshold": 0.5
            })
        elif level == ExtractionLevel.MINIMAL:
            # Minimal extraction for critical paths only
            return EntityRecognizerFactory.create_recognizer("pattern", {
                "confidence_threshold": 0.4,
                "use_core_patterns_only": True
            })
        
        # Default to pattern recognizer as last resort
        return EntityRecognizerFactory.create_recognizer("pattern")
```

### Phase 4: Enhanced Task System (Week 4)

#### 4.1 Advanced Celery Task Base Class
- Extend `PaperProcessingTask` with enhanced error handling
- Add task-specific retry strategies
- Implement partial success results
- Add metrics collection for failures/retries

```python
class EnhancedProcessingTask(PaperProcessingTask):
    """Enhanced task base class with advanced error recovery."""
    
    # Don't use Celery's autoretry - we'll handle retries ourselves
    autoretry_for = ()
    
    # Default retry configuration
    default_retry_strategy = RetryStrategy()
    
    # Recovery strategies by error category
    recovery_strategies = {
        ErrorCategory.TRANSIENT: "retry",
        ErrorCategory.PERMANENT: "fail",
        ErrorCategory.DATA_RELATED: "partial",
        ErrorCategory.SYSTEM: "retry_with_escalation",
        ErrorCategory.DEPENDENCY: "circuit_break_and_retry"
    }
    
    # Transaction support
    use_transactions = True
    
    # Checkpointing configuration
    checkpointing = True
    checkpoint_frequency = 1  # How often to create checkpoints (tasks)
    
    def run(self, *args, **kwargs):
        """Enhanced run method with error recovery capabilities."""
        self.task_start_time = time.time()
        self.checkpoint_counter = 0
        
        try:
            # Create the task context
            self.context = self.build_context(*args, **kwargs)
            
            # Check if we can resume from checkpoint
            checkpoint = None
            if self.checkpointing:
                checkpoint = self.try_load_checkpoint(self.context)
                if checkpoint:
                    logger.info(f"Resuming task {self.name} from checkpoint")
                    # Restore context from checkpoint
                    self.update_context_from_checkpoint(checkpoint)
            
            # Create transaction if needed
            transaction = None
            if self.use_transactions:
                transaction = Transaction(self.name, paper_id=self.context.get('paper_id'))
                
            # Execute the task with transaction and error handling
            result = self.execute_task(self.context, transaction)
            
            # Commit transaction if needed
            if transaction:
                transaction.commit()
                
            # Record successful completion
            self.record_success(result)
            
            return result
            
        except ProcessingError as e:
            return self.handle_error(e, args, kwargs)
        except Exception as e:
            # Convert to ProcessingError for consistent handling
            error = ProcessingError(
                str(e), category=ErrorCategory.PERMANENT,
                severity=ErrorSeverity.HIGH,
                context=self.context, retry_suggested=False
            )
            return self.handle_error(error, args, kwargs)
    
    def execute_task(self, context, transaction=None):
        """
        Execute the actual task logic.
        
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute_task")
    
    def build_context(self, *args, **kwargs):
        """Build the task execution context."""
        # Default implementation extracts paper_id
        return {
            'paper_id': kwargs.get('paper_id') or args[0] if args else None,
            'task_id': self.request.id,
            'retry_count': self.request.retries,
            'args': args,
            'kwargs': kwargs
        }
        
    def handle_error(self, error, args, kwargs):
        """Handle errors with intelligent recovery strategies."""
        # Get the appropriate recovery strategy
        strategy = self.recovery_strategies.get(
            error.category, 
            "fail" if not error.retry_suggested else "retry"
        )
        
        # Log the error with context
        logger.error(
            f"Task {self.name} failed with error: {str(error)}. "
            f"Category: {error.category}, Strategy: {strategy}"
        )
        
        # Apply the selected recovery strategy
        if strategy == "retry":
            return self.handle_retry(error, args, kwargs)
        elif strategy == "partial":
            return self.handle_partial_success(error, args, kwargs)
        elif strategy == "retry_with_escalation":
            return self.handle_retry_with_escalation(error, args, kwargs)
        elif strategy == "circuit_break_and_retry":
            return self.handle_circuit_break_and_retry(error, args, kwargs)
        else:
            # Default to fail
            return self.handle_failure(error, args, kwargs)
            
    def handle_retry(self, error, args, kwargs):
        """Handle retry strategy."""
        retry_count = self.request.retries
        
        # Get the retry strategy for this error type
        retry_strategy = RetryManager.get_strategy(error)
        
        if retry_count < retry_strategy.max_retries:
            # Calculate the retry delay
            delay = retry_strategy.calculate_delay(retry_count)
            
            logger.info(
                f"Retrying task {self.name} after error. "
                f"Attempt {retry_count + 1}/{retry_strategy.max_retries}, "
                f"delay: {delay}s"
            )
            
            # Create checkpoint before retry if applicable
            if self.checkpointing:
                self.create_checkpoint()
                
            # Retry the task
            raise self.retry(
                exc=error,
                countdown=delay,
                kwargs=kwargs,
                args=args
            )
        else:
            # Max retries exceeded
            logger.warning(
                f"Max retries ({retry_strategy.max_retries}) exceeded for task {self.name}. "
                f"Failing permanently."
            )
            return self.handle_failure(error, args, kwargs)
    
    def handle_failure(self, error, args, kwargs):
        """Handle permanent failure."""
        # Send to dead letter queue
        self.send_to_dead_letter_queue(error, args, kwargs)
        
        # Update paper state if possible
        paper_id = kwargs.get('paper_id') or args[0] if args else None
        if paper_id:
            try:
                self.update_paper_status_failed(paper_id, error)
            except Exception as e:
                logger.error(f"Failed to update paper status: {str(e)}")
        
        # Return error result
        return {
            "success": False,
            "error": str(error),
            "error_details": error.to_dict() if hasattr(error, "to_dict") else {"message": str(error)},
            "task": self.name
        }
        
    def handle_partial_success(self, error, args, kwargs):
        """Handle partial success by saving valid portions."""
        # Override in subclasses to implement partial result saving
        logger.info(f"Handling partial success for task {self.name}")
        
        # By default, just retry
        return self.handle_retry(error, args, kwargs)
    
    def create_checkpoint(self):
        """Create a checkpoint of current task state."""
        if not hasattr(self, 'context'):
            logger.warning("Cannot create checkpoint without context")
            return None
            
        paper_id = self.context.get('paper_id')
        if not paper_id:
            logger.warning("Cannot create checkpoint without paper_id")
            return None
            
        # Create and save checkpoint
        checkpoint = ProcessingCheckpoint(
            paper_id=paper_id,
            stage=self.name,
            data=self.context
        )
        
        checkpoint_path = checkpoint.save()
        logger.info(f"Created checkpoint for task {self.name} at {checkpoint_path}")
        self.checkpoint_counter += 1
        
        return checkpoint
        
    def try_load_checkpoint(self, context):
        """Try to load a checkpoint for the current task."""
        paper_id = context.get('paper_id')
        if not paper_id:
            return None
            
        try:
            checkpoint = ProcessingCheckpoint.load(paper_id, self.name)
            if checkpoint:
                logger.info(f"Found checkpoint for paper {paper_id} at stage {self.name}")
                return checkpoint
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {str(e)}")
            
        return None
        
    def update_context_from_checkpoint(self, checkpoint):
        """Update the current context with data from a checkpoint."""
        if not checkpoint or not hasattr(self, 'context'):
            return
            
        # Merge checkpoint data into context, preserving current task info
        task_info = {
            'task_id': self.context.get('task_id'),
            'retry_count': self.context.get('retry_count')
        }
        
        self.context.update(checkpoint.data)
        
        # Restore task info that shouldn't be overwritten
        self.context.update(task_info)
        
        # Mark as resumed from checkpoint
        self.context['resumed_from_checkpoint'] = True
        self.context['checkpoint_id'] = checkpoint.id
```

#### 4.2 Dead Letter Queue Enhancements
- Improve dead letter queue with categorization
- Add automated recovery for transient failures
- Create admin interfaces for dead letter management
- Implement periodic reprocessing of failed tasks

```python
class EnhancedDeadLetterQueue:
    """Enhanced dead letter queue with recovery capabilities."""
    
    def __init__(self):
        self.storage = settings.DEAD_LETTER_STORAGE_PATH
        os.makedirs(self.storage, exist_ok=True)
        
    def store_task(self, task_data):
        """Store a dead letter task with categorization."""
        # Add timestamp and unique ID
        task_data.update({
            "timestamp": datetime.now().isoformat(),
            "dlq_id": str(uuid.uuid4())
        })
        
        # Determine storage path based on category
        category = self._get_category(task_data)
        category_dir = os.path.join(self.storage, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # Write task data to file
        file_path = os.path.join(
            category_dir, 
            f"{task_data['task_name']}_{task_data['dlq_id']}.json"
        )
        
        with open(file_path, 'w') as f:
            json.dump(task_data, f, indent=2)
            
        logger.info(f"Stored dead letter task {task_data['task_name']} ({task_data['dlq_id']}) in category {category}")
        
        # Add task to database for tracking
        try:
            store_dlq_task_in_db(task_data)
        except Exception as e:
            logger.error(f"Failed to store DLQ task in database: {str(e)}")
            
        return file_path
        
    def _get_category(self, task_data):
        """Categorize the dead letter task."""
        error_info = task_data.get("error_info", {})
        error_type = error_info.get("error_type", "unknown")
        error_message = error_info.get("message", "")
        
        # Categorize common errors
        if any(net_err in error_type for net_err in ["Timeout", "Connection", "Network"]):
            return "network"
        elif any(db_err in error_type for db_err in ["Database", "DB", "Mongo", "Neo4j"]):
            return "database"
        elif any(res_err in error_type for res_err in ["Resource", "Memory", "CPU"]):
            return "resources"
        elif any(data_err in error_type for data_err in ["Data", "Parse", "Schema"]):
            return "data"
        elif error_info.get("category"):
            return error_info["category"]
        
        # Check for common error patterns in the message
        if any(term in error_message.lower() for term in ["timeout", "timed out"]):
            return "timeout"
        elif any(term in error_message.lower() for term in ["permission", "access", "forbidden"]):
            return "permissions"
            
        # Default category
        return "other"
        
    def list_tasks(self, category=None, limit=100, skip=0):
        """List dead letter tasks with optional filtering."""
        result = []
        
        # Determine which directories to scan
        if category:
            categories = [category]
        else:
            # List all category directories
            categories = [d for d in os.listdir(self.storage) 
                         if os.path.isdir(os.path.join(self.storage, d))]
        
        # Collect tasks from each category
        for cat in categories:
            cat_dir = os.path.join(self.storage, cat)
            if not os.path.isdir(cat_dir):
                continue
                
            # Get all task files in this category
            task_files = [f for f in os.listdir(cat_dir) if f.endswith('.json')]
            
            # Sort by modification time (newest first)
            task_files.sort(key=lambda f: os.path.getmtime(os.path.join(cat_dir, f)), reverse=True)
            
            # Apply pagination
            task_files = task_files[skip:skip+limit]
            
            # Read task data
            for task_file in task_files:
                try:
                    with open(os.path.join(cat_dir, task_file), 'r') as f:
                        task_data = json.load(f)
                        task_data["category"] = cat
                        result.append(task_data)
                except Exception as e:
                    logger.error(f"Failed to read task file {task_file}: {str(e)}")
        
        return result
        
    def retry_task(self, dlq_id):
        """Retry a specific dead letter task."""
        # Find the task file
        task_file = None
        task_category = None
        
        for category in os.listdir(self.storage):
            cat_dir = os.path.join(self.storage, category)
            if not os.path.isdir(cat_dir):
                continue
                
            for filename in os.listdir(cat_dir):
                if dlq_id in filename and filename.endswith('.json'):
                    task_file = os.path.join(cat_dir, filename)
                    task_category = category
                    break
                    
            if task_file:
                break
                
        if not task_file:
            logger.error(f"Task with ID {dlq_id} not found in dead letter queue")
            return False
            
        # Read the task data
        try:
            with open(task_file, 'r') as f:
                task_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read task file {task_file}: {str(e)}")
            return False
            
        # Resubmit the task to Celery
        try:
            task_name = task_data["task_name"]
            args = task_data.get("args", [])
            kwargs = task_data.get("kwargs", {})
            
            # Get the task
            task = app.tasks[task_name]
            
            # Resubmit the task
            result = task.apply_async(args=args, kwargs=kwargs)
            
            logger.info(f"Resubmitted dead letter task {task_name} ({dlq_id})")
            
            # Move the task file to a 'reprocessed' directory
            reprocessed_dir = os.path.join(self.storage, "reprocessed")
            os.makedirs(reprocessed_dir, exist_ok=True)
            
            new_path = os.path.join(
                reprocessed_dir,
                f"{os.path.basename(task_file)}.reprocessed"
            )
            
            shutil.move(task_file, new_path)
            
            # Update task status in database
            try:
                update_dlq_task_status(dlq_id, "reprocessed", {
                    "reprocessed_at": datetime.now().isoformat(),
                    "new_task_id": result.id
                })
            except Exception as e:
                logger.error(f"Failed to update DLQ task status in database: {str(e)}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to resubmit task {dlq_id}: {str(e)}")
            return False
```

#### 4.3 Task Monitoring and Alerting
- Implement a task monitoring system
- Add error rate tracking and alerting
- Create dashboard for task health
- Add automatic escalation for critical failures

```python
class TaskMonitor:
    """Monitoring system for task health and performance."""
    
    def __init__(self):
        self.stats = {
            "success_count": 0,
            "error_count": 0,
            "retry_count": 0,
            "task_stats": {}
        }
        self.error_rate_threshold = 0.1  # 10% error rate threshold
        self.alerts = []
        
    def record_task_start(self, task_name, task_id):
        """Record a task start event."""
        if task_name not in self.stats["task_stats"]:
            self.stats["task_stats"][task_name] = {
                "success_count": 0,
                "error_count": 0,
                "retry_count": 0,
                "avg_duration": 0,
                "durations": [],
                "active_tasks": set(),
                "last_error": None
            }
            
        self.stats["task_stats"][task_name]["active_tasks"].add(task_id)
        
    def record_task_success(self, task_name, task_id, duration):
        """Record a successful task completion."""
        self.stats["success_count"] += 1
        
        if task_name in self.stats["task_stats"]:
            task_stats = self.stats["task_stats"][task_name]
            task_stats["success_count"] += 1
            task_stats["active_tasks"].discard(task_id)
            
            # Update average duration
            task_stats["durations"].append(duration)
            if len(task_stats["durations"]) > 100:
                task_stats["durations"].pop(0)  # Keep only last 100
            task_stats["avg_duration"] = sum(task_stats["durations"]) / len(task_stats["durations"])
        
    def record_task_error(self, task_name, task_id, error, retrying=False):
        """Record a task error."""
        self.stats["error_count"] += 1
        
        if retrying:
            self.stats["retry_count"] += 1
            
        if task_name in self.stats["task_stats"]:
            task_stats = self.stats["task_stats"][task_name]
            task_stats["error_count"] += 1
            if retrying:
                task_stats["retry_count"] += 1
            task_stats["active_tasks"].discard(task_id)
            task_stats["last_error"] = {
                "message": str(error),
                "timestamp": datetime.now().isoformat()
            }
            
            # Check if error rate exceeds threshold
            total_tasks = task_stats["success_count"] + task_stats["error_count"]
            if total_tasks >= 10:  # Only check if we have a meaningful sample
                error_rate = task_stats["error_count"] / total_tasks
                if error_rate > self.error_rate_threshold:
                    self.create_alert(
                        task_name, 
                        f"High error rate: {error_rate:.1%}",
                        error_rate
                    )
    
    def create_alert(self, task_name, message, value=None, level="warning"):
        """Create a task alert."""
        alert = {
            "task": task_name,
            "message": message,
            "value": value,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts.pop(0)
            
        # Log the alert
        log_method = logger.warning if level == "warning" else logger.error
        log_method(f"Task alert: {task_name} - {message}")
        
        # TODO: Send to external alerting system if critical
        if level == "critical":
            try:
                self.send_critical_alert(alert)
            except Exception as e:
                logger.error(f"Failed to send critical alert: {str(e)}")
        
        return alert
        
    def send_critical_alert(self, alert):
        """Send a critical alert to external systems."""
        # Implement actual sending logic based on your alerting systems
        # This could send emails, Slack messages, PagerDuty, etc.
        pass
        
    def get_task_stats(self, task_name=None):
        """Get task statistics."""
        if task_name:
            return self.stats["task_stats"].get(task_name, {})
        return self.stats
        
    def get_alerts(self, level=None, limit=20):
        """Get task alerts with optional filtering."""
        if level:
            filtered_alerts = [a for a in self.alerts if a["level"] == level]
        else:
            filtered_alerts = self.alerts
            
        # Return most recent alerts first
        return filtered_alerts[-limit:]
        
    def get_health_status(self):
        """Get overall system health status."""
        total_tasks = self.stats["success_count"] + self.stats["error_count"]
        if total_tasks == 0:
            return "unknown"
            
        error_rate = self.stats["error_count"] / total_tasks
        
        if error_rate > 0.25:  # More than 25% errors
            return "critical"
        elif error_rate > 0.1:  # More than 10% errors
            return "degraded"
        elif error_rate > 0.01:  # More than 1% errors
            return "warning"
        else:
            return "healthy"
```

### Phase 5: Integration and Testing (Week 5)

#### 5.1 Advanced Error Recovery Testing
- Implement integration tests for recovery mechanisms
- Add fault injection testing for error paths
- Create chaos testing for dependency failures
- Build test harness for recovery strategies

```python
class ErrorInjector:
    """Utility for injecting errors during testing."""
    
    @classmethod
    def inject_document_error(cls, error_type, probability=1.0):
        """Create a context manager that injects document processing errors."""
        class DocumentErrorContext:
            def __init__(self, error_type, probability):
                self.error_type = error_type
                self.probability = probability
                self.original_methods = {}
                
            def __enter__(self):
                # Get the original method reference
                from research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
                
                if self.error_type == "file_not_found":
                    self.original_methods["_read_file"] = DocumentProcessor._read_file
                    
                    def inject_file_not_found(self, file_path):
                        if random.random() < probability:
                            raise FileNotFoundError(f"Injected error: File not found: {file_path}")
                        return self.original_methods["_read_file"](self, file_path)
                        
                    DocumentProcessor._read_file = inject_file_not_found
                    
                elif self.error_type == "encoding_error":
                    self.original_methods["_process_text"] = DocumentProcessor._process_text
                    
                    def inject_encoding_error(self, file_path):
                        if random.random() < probability:
                            raise UnicodeDecodeError("utf-8", b"test", 0, 1, "Injected encoding error")
                        return self.original_methods["_process_text"](self, file_path)
                        
                    DocumentProcessor._process_text = inject_encoding_error
                    
                # Return self for context manager
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Restore original methods
                from research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
                
                for method_name, original_method in self.original_methods.items():
                    setattr(DocumentProcessor, method_name, original_method)
                
        return DocumentErrorContext(error_type, probability)
```

#### 5.2 Recovery Strategy Configurator
- Create a configuration system for recovery strategies
- Implement runtime strategy adjustments
- Add A/B testing for recovery strategies
- Create performance analytics for strategies

```python
class RecoveryConfiguration:
    """Configuration for recovery strategies."""
    
    def __init__(self, config_path=None):
        self.config_path = config_path or settings.RECOVERY_CONFIG_PATH
        self.config = self.load_config()
        
    def load_config(self):
        """Load recovery configuration from file."""
        default_config = {
            "retry_strategies": {
                "default": {
                    "max_retries": 3,
                    "initial_delay": 1,
                    "backoff_factor": 2.0,
                    "jitter": 0.1,
                    "max_delay": 60
                },
                "network": {
                    "max_retries": 5,
                    "initial_delay": 2,
                    "backoff_factor": 2.5,
                    "jitter": 0.2,
                    "max_delay": 300
                },
                # More strategies...
            },
            "circuit_breakers": {
                "database": {
                    "failure_threshold": 5,
                    "recovery_timeout": 60,
                    "half_open_max_calls": 1
                },
                # More circuit breaker configs...
            },
            "checkpoint_config": {
                "enabled": True,
                "frequency": 1,
                "max_age_hours": 24,
                "storage_limit_mb": 100
            },
            "dead_letter_queue": {
                "auto_retry_categories": ["network", "timeout"],
                "auto_retry_delay_minutes": 15,
                "max_auto_retries": 3
            },
            "monitoring": {
                "error_rate_threshold": 0.1,
                "alert_levels": {
                    "error_rate_high": 0.25,
                    "error_rate_medium": 0.1,
                    "error_rate_low": 0.01
                }
            }
        }
        
        if not os.path.exists(self.config_path):
            logger.warning(f"Recovery config not found at {self.config_path}, using defaults")
            return default_config
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Merge with defaults for any missing values
            merged_config = default_config.copy()
            self._deep_update(merged_config, config)
            
            return merged_config
        except Exception as e:
            logger.error(f"Error loading recovery config: {str(e)}")
            return default_config
            
    def _deep_update(self, d, u):
        """Recursively update nested dict."""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
                
    def get_retry_strategy(self, category):
        """Get retry strategy configuration for a category."""
        strategies = self.config.get("retry_strategies", {})
        return strategies.get(category, strategies.get("default", {}))
        
    def get_circuit_breaker_config(self, name):
        """Get circuit breaker configuration."""
        cb_configs = self.config.get("circuit_breakers", {})
        return cb_configs.get(name, cb_configs.get("default", {}))
        
    def is_checkpointing_enabled(self):
        """Check if checkpointing is enabled."""
        checkpoint_config = self.config.get("checkpoint_config", {})
        return checkpoint_config.get("enabled", True)
        
    def get_checkpoint_frequency(self):
        """Get checkpoint frequency."""
        checkpoint_config = self.config.get("checkpoint_config", {})
        return checkpoint_config.get("frequency", 1)
        
    def save_config(self):
        """Save current configuration."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
        logger.info(f"Saved recovery configuration to {self.config_path}")
```

#### 5.3 User Interface for Recovery
- Implement admin dashboard for recovery management
- Create user-friendly error explanation system
- Add manual recovery triggers for operators
- Implement system health monitoring UI

```python
# admin_routes.py

@router.get("/recovery/tasks/failed")
def list_failed_tasks(
    category: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """List failed tasks with filtering."""
    dlq = EnhancedDeadLetterQueue()
    tasks = dlq.list_tasks(category=category, limit=limit, skip=skip)
    
    # Get category counts for the UI
    categories = {}
    for cat_dir in os.listdir(dlq.storage):
        if os.path.isdir(os.path.join(dlq.storage, cat_dir)):
            task_files = [f for f in os.listdir(os.path.join(dlq.storage, cat_dir)) 
                         if f.endswith('.json')]
            categories[cat_dir] = len(task_files)
    
    return {
        "tasks": tasks,
        "categories": categories,
        "total": sum(categories.values()),
        "limit": limit,
        "skip": skip
    }

@router.post("/recovery/tasks/{dlq_id}/retry")
def retry_failed_task(dlq_id: str):
    """Retry a failed task."""
    dlq = EnhancedDeadLetterQueue()
    success = dlq.retry_task(dlq_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to retry task")
        
    return {"success": True, "message": f"Task {dlq_id} scheduled for retry"}

@router.get("/recovery/system/health")
def get_system_health():
    """Get system health status."""
    from paper_processing.tasks.monitoring import task_monitor
    
    health_status = task_monitor.get_health_status()
    stats = task_monitor.get_task_stats()
    alerts = task_monitor.get_alerts()
    
    # Get circuit breaker status
    from paper_processing.recovery.circuit_breakers import circuit_breaker_registry
    
    circuit_breakers = []
    for name, cb in circuit_breaker_registry.items():
        circuit_breakers.append({
            "name": name,
            "state": cb.state.value,
            "failure_count": cb.failure_count,
            "last_failure_time": cb.last_failure_time,
            "last_success_time": cb.last_success_time
        })
    
    return {
        "status": health_status,
        "stats": stats,
        "alerts": alerts,
        "circuit_breakers": circuit_breakers
    }

@router.post("/recovery/paper/{paper_id}/restart")
def restart_paper_processing(paper_id: str, from_stage: Optional[str] = None):
    """Restart processing for a paper."""
    # Load the paper
    try:
        paper = Paper.objects.get(id=paper_id)
    except Paper.DoesNotExist:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Set up the recovery transaction
    transaction = Transaction(f"restart_paper_{paper_id}", paper_id=paper_id)
    
    # Determine target state based on from_stage
    if from_stage:
        target_state = from_stage
    else:
        # Default to UPLOADED to restart the whole process
        target_state = "UPLOADED"
    
    # Transition to the target state
    try:
        state_machine = TransactionalStateMachine(paper)
        success = state_machine.transition_to(
            target_state,
            message=f"Manual restart from admin UI",
            metadata={"restart": True, "user_initiated": True},
            transaction=transaction
        )
        
        if not success:
            transaction.rollback()
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to transition paper to {target_state}"
            )
            
        # Commit the transaction
        transaction.commit()
        
        # Enqueue the processing task
        from paper_processing.tasks.processing_tasks import process_paper
        task = process_paper.delay(paper_id)
        
        return {
            "success": True,
            "message": f"Paper {paper_id} restarted from {target_state}",
            "task_id": task.id
        }
    except Exception as e:
        # Rollback the transaction
        transaction.rollback()
        
        logger.error(f"Failed to restart paper {paper_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart paper: {str(e)}"
        )
```

### Testing Plan

For each component implemented, we will create comprehensive tests:

1. **Unit Tests**: Testing each component in isolation
   - Error classification and taxonomy
   - Retry strategies and policies
   - Transaction management
   - Circuit breaker functionality
   - Checkpoint creation and restoration

2. **Integration Tests**: Testing components working together
   - Error recovery flow from detection to handling
   - Recovery from different failure types
   - Checkpoint-based recovery
   - Circuit breaker protection of dependencies

3. **Fault Injection Tests**: Testing recovery from simulated failures
   - Network failures for HTTP clients
   - Database connection failures
   - Invalid document formats
   - Resource exhaustion (memory, disk space)
   - Slow responses and timeouts

4. **Chaos Tests**: Testing recovery under extreme conditions
   - Multiple concurrent failures
   - Cascading failure scenarios
   - Recovery under load
   - Intermittent failures and flaky services

## Implementation Status

### Completed Components

- **Week 1**: Error Classification and Intelligent Retry ✅
  - ✅ Created exception taxonomy and error classification system
  - ✅ Implemented ProcessingError hierarchy with specialized error types
  - ✅ Built RetryManager with multiple strategies and policies
  - ✅ Added retry decorator and retry context manager

- **Week 2**: Transaction-based Processing ✅
  - ✅ Implemented Transaction and TransactionManager
  - ✅ Created transaction context manager for easier use
  - ✅ Built transaction operation model with compensation
  - ✅ Added transaction log support for debugging and auditing
  - ✅ Implemented checkpoint system for recovery points

- **Week 3**: Progressive Fallback Strategies 🟠 (Partially Complete)
  - ✅ Implemented circuit breaker pattern for external dependencies
  - ✅ Created circuit breaker registry and decorator
  - ✅ Built FallbackResult and FallbackStrategy for graceful degradation
  - ✅ Implemented ProgressiveExtractor for tiered fallback extraction
  - ✅ Successfully tested circuit breaker functionality with all components
  - ✅ Added health monitoring for external dependencies
  - 🟠 Implementing document processor-specific fallbacks
  - ⏳ Need to integrate fallback strategies into all document processing types

### Document Processing Fallbacks Implementation

We've identified the document processing components that require fallback strategies:

1. **Document Processor** - The main entry point for document processing
   - ✅ Analyzed current implementation and dependency structure
   - ✅ Identified specific failure points and error types
   - 🟠 Implementing specialized fallback strategies for different document types
   - ⏳ Adding progressive extraction levels for degraded processing

2. **PDF Processor** - Handles PDF document extraction
   - ✅ Added circuit breaker protection for PyPDF2 dependencies
   - ✅ Implemented basic fallback for text extraction failures
   - 🟠 Adding metadata extraction fallbacks
   - ⏳ Creating structure extraction fallbacks

3. **HTML Processor** - Handles HTML document extraction
   - ✅ Implemented fallbacks for BeautifulSoup dependency
   - 🟠 Adding progressive content extraction based on complexity
   - ⏳ Implementing section and structure extraction fallbacks

4. **Text Processor** - Handles plain text documents
   - ✅ Added robust error handling for encoding issues
   - ✅ Implemented fallbacks for large file processing
   - 🟠 Creating section detection fallbacks
   - ⏳ Adding format detection fallbacks

### Remaining Timeline

- **Week 3 Remaining**: Progressive Fallback Strategies
  - Complete document processor integration with fallback strategies
  - Implement specific entity extraction fallbacks for all document types
  - Create relationship extraction fallbacks for degraded extraction
  - Build dependency fallback strategies for external services

- **Week 4**: Enhanced Task System
  - Extend PaperProcessingTask with recovery capabilities
  - Implement advanced dead letter queue
  - Add task monitoring and alerting

- **Week 5**: Integration and Testing
  - Create error injection testing framework
  - Implement admin interfaces for recovery
  - Conduct end-to-end testing of recovery mechanisms

## Success Criteria

The implementation will be considered successful if:

1. The system automatically recovers from transient failures
2. Processing continues with graceful degradation when dependencies fail
3. Partial results are preserved when full processing fails
4. Manual recovery is simplified through intuitive interfaces
5. Failure rates are reduced by at least 50% compared to baseline
6. Mean time to recovery (MTTR) is reduced by at least 70%

## Conclusion

This implementation plan provides a comprehensive approach to enhancing error recovery in the knowledge extraction pipeline. By implementing intelligent retry strategies, transaction-based processing, progressive fallbacks, and enhanced monitoring, we can create a highly resilient system that gracefully handles failures and minimizes the need for manual intervention.

The proposed components work together to create multiple layers of protection, ensuring that the system can recover from various failure scenarios while preserving as much work as possible. This approach will significantly improve the reliability and robustness of the knowledge extraction pipeline.