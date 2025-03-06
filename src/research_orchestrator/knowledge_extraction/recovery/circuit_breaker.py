"""
Circuit Breaker implementation for the Knowledge Extraction Pipeline.

This module provides a circuit breaker pattern implementation to protect
against failing dependencies and services, allowing for graceful degradation
and self-healing capabilities.
"""

import time
import logging
import threading
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast
from functools import wraps

logger = logging.getLogger(__name__)

# Type variables for generic function signatures
T = TypeVar('T')
R = TypeVar('R')


class CircuitState(Enum):
    """Possible states for a circuit breaker."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejects all requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitOpenError(Exception):
    """Exception raised when a circuit is open and a request is made."""

    def __init__(self, circuit_name: str, recovery_time: float = 0.0):
        self.circuit_name = circuit_name
        self.recovery_time = recovery_time
        message = (f"Circuit '{circuit_name}' is OPEN" +
                  (f", recovery in {recovery_time:.1f}s" if recovery_time > 0 else ""))
        super().__init__(message)


class CircuitBreaker:
    """
    Circuit breaker for protecting against failing dependencies.
    
    Implements the circuit breaker pattern to prevent cascading failures
    when a dependency is failing. When failures exceed a threshold, the
    circuit opens and rejects requests until a recovery timeout has elapsed.
    """
    
    def __init__(self, 
                name: str,
                failure_threshold: int = 5,
                recovery_timeout: float = 60.0,
                half_open_max_calls: int = 1,
                allowed_exceptions: Optional[List[type]] = None):
        """
        Initialize a circuit breaker.
        
        Args:
            name: Unique name for this circuit breaker
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Seconds to wait before trying to recover
            half_open_max_calls: Max calls allowed while in HALF_OPEN state
            allowed_exceptions: Exception types that don't count as failures
        """
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.half_open_calls = 0
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None
        self.state_change_time: float = time.time()
        self.allowed_exceptions = allowed_exceptions or []
        self._lock = threading.RLock()
        
        logger.info(f"Circuit Breaker '{name}' initialized with threshold={failure_threshold}, " +
                   f"timeout={recovery_timeout}s")
        
    def execute(self, 
               func: Callable[..., T],
               fallback: Optional[Callable[..., T]] = None,
               *args: Any,
               **kwargs: Any) -> T:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            fallback: Optional fallback function if circuit is open
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of func or fallback if circuit is open
            
        Raises:
            CircuitOpenError: If circuit is open and no fallback is provided
            Exception: Any exceptions raised by the function
        """
        with self._lock:
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed
                if (self.last_failure_time and 
                    (time.time() - self.last_failure_time) >= self.recovery_timeout):
                    logger.info(f"Circuit '{self.name}' transitioning from OPEN to HALF_OPEN " +
                               f"after {self.recovery_timeout}s timeout")
                    self._transition_to_half_open()
                else:
                    # Calculate recovery time
                    recovery_time = 0.0
                    if self.last_failure_time:
                        elapsed = time.time() - self.last_failure_time
                        recovery_time = max(0.0, self.recovery_timeout - elapsed)
                    
                    # Circuit is open, use fallback if provided
                    if fallback:
                        logger.debug(f"Circuit '{self.name}' is OPEN, using fallback function")
                        return fallback(*args, **kwargs)
                    
                    logger.warning(f"Circuit '{self.name}' is OPEN, rejecting request. " +
                                 f"Recovery in {recovery_time:.1f}s")
                    raise CircuitOpenError(self.name, recovery_time)
                    
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    # Too many test calls already in progress
                    if fallback:
                        logger.debug(f"Circuit '{self.name}' is HALF_OPEN with max calls, " +
                                   f"using fallback function")
                        return fallback(*args, **kwargs)
                    
                    logger.warning(f"Circuit '{self.name}' is HALF_OPEN with max calls, " +
                                 f"rejecting request")
                    raise CircuitOpenError(self.name)
                    
                # Increment the half-open call counter
                self.half_open_calls += 1
                logger.debug(f"Circuit '{self.name}' is HALF_OPEN, allowing test call " +
                           f"({self.half_open_calls}/{self.half_open_max_calls})")
                
        # Execute the protected function
        try:
            result = func(*args, **kwargs)
            
            # Success, handle state transitions
            with self._lock:
                self._on_success()
                
            return result
        except Exception as e:
            # Check if this exception type should not count as a failure
            if any(isinstance(e, ex_type) for ex_type in self.allowed_exceptions):
                # Allowed exception, don't count as failure
                logger.debug(f"Circuit '{self.name}' ignored allowed exception: {type(e).__name__}")
                raise
                
            # Record the failure
            with self._lock:
                self._on_failure()
                
            # Use fallback if provided, otherwise re-raise
            if fallback:
                logger.debug(f"Circuit '{self.name}' using fallback after {type(e).__name__}")
                return fallback(*args, **kwargs)
                
            logger.debug(f"Circuit '{self.name}' propagating exception: {type(e).__name__}")
            raise
            
    def _on_success(self) -> None:
        """Handle a successful execution."""
        self.success_count += 1
        self.last_success_time = time.time()
        
        # Reset failure count in closed state
        if self.state == CircuitState.CLOSED:
            if self.failure_count > 0:
                logger.debug(f"Circuit '{self.name}' reset failure count after success")
                self.failure_count = 0
        
        # If we're half-open, a success means we can close the circuit
        elif self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit '{self.name}' recovered, transitioning to CLOSED " +
                       f"after {self.success_count} success(es)")
            self._transition_to_closed()
            
        # Decrement half-open calls
        self.half_open_calls = max(0, self.half_open_calls - 1)
        
    def _on_failure(self) -> None:
        """Handle a failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # Check if we should open the circuit
        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit '{self.name}' transitioning to OPEN after " +
                         f"{self.failure_count} failures")
            self._transition_to_open()
        elif self.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit '{self.name}' failed in HALF_OPEN state, " +
                         f"returning to OPEN")
            self._transition_to_open()
            
        # Decrement half-open calls
        self.half_open_calls = max(0, self.half_open_calls - 1)
        
    def _transition_to_open(self) -> None:
        """Transition to the OPEN state."""
        self.state = CircuitState.OPEN
        self.state_change_time = time.time()
        self.half_open_calls = 0
        
    def _transition_to_half_open(self) -> None:
        """Transition to the HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.state_change_time = time.time()
        self.half_open_calls = 0
        
    def _transition_to_closed(self) -> None:
        """Transition to the CLOSED state."""
        self.state = CircuitState.CLOSED
        self.state_change_time = time.time()
        self.failure_count = 0
        self.half_open_calls = 0
        
    def get_state_dict(self) -> Dict[str, Any]:
        """
        Get the current state as a dictionary.
        
        Returns:
            Dictionary with circuit breaker state information
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "half_open_calls": self.half_open_calls,
            "half_open_max_calls": self.half_open_max_calls,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "state_change_time": self.state_change_time,
            "uptime": time.time() - self.state_change_time if self.state == CircuitState.CLOSED else 0,
            "recovery_remaining": (
                max(0, self.recovery_timeout - (time.time() - self.last_failure_time))
                if self.state == CircuitState.OPEN and self.last_failure_time
                else 0
            )
        }
        
    def reset(self) -> None:
        """Reset the circuit breaker to its initial closed state."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.state_change_time = time.time()
            self.half_open_calls = 0
            self.last_failure_time = None
            self.last_success_time = None
            
        logger.info(f"Circuit '{self.name}' manually reset to CLOSED state")
        
    def __str__(self) -> str:
        """String representation of the circuit breaker."""
        return (f"CircuitBreaker(name='{self.name}', state={self.state.value}, " +
               f"failures={self.failure_count}/{self.failure_threshold})")


# Dictionary to store circuit breakers by name
circuit_breaker_registry: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str,
                        failure_threshold: int = 5,
                        recovery_timeout: float = 60.0,
                        half_open_max_calls: int = 1,
                        allowed_exceptions: Optional[List[type]] = None) -> CircuitBreaker:
    """
    Get or create a circuit breaker by name.
    
    This ensures we reuse circuit breakers across different parts of the system.
    
    Args:
        name: Unique name for the circuit breaker
        failure_threshold: Number of failures before opening the circuit
        recovery_timeout: Seconds to wait before trying to recover
        half_open_max_calls: Max calls allowed while in HALF_OPEN state
        allowed_exceptions: Exception types that don't count as failures
        
    Returns:
        The circuit breaker instance
    """
    if name not in circuit_breaker_registry:
        circuit_breaker_registry[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            half_open_max_calls=half_open_max_calls,
            allowed_exceptions=allowed_exceptions
        )
        
    return circuit_breaker_registry[name]


def circuit_protected(circuit_name: str,
                     failure_threshold: int = 5,
                     recovery_timeout: float = 60.0,
                     half_open_max_calls: int = 1,
                     allowed_exceptions: Optional[List[type]] = None,
                     fallback_function: Optional[Callable[..., Any]] = None):
    """
    Decorator for functions that should be protected by a circuit breaker.
    
    Args:
        circuit_name: Name for the circuit breaker
        failure_threshold: Number of failures before opening the circuit
        recovery_timeout: Seconds to wait before trying to recover
        half_open_max_calls: Max calls allowed while in HALF_OPEN state
        allowed_exceptions: Exception types that don't count as failures
        fallback_function: Optional fallback function to call when circuit is open
        
    Returns:
        Decorated function
        
    Example:
        @circuit_protected("database_operations", recovery_timeout=30)
        def save_to_database(data):
            # Function will be protected by circuit breaker
            ...
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        # Get or create the circuit breaker
        circuit = get_circuit_breaker(
            name=circuit_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            half_open_max_calls=half_open_max_calls,
            allowed_exceptions=allowed_exceptions
        )
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            # Find fallback if provided
            fallback = fallback_function
            
            # If fallback is provided as keyword argument, use that instead
            if '_fallback' in kwargs:
                fallback = kwargs.pop('_fallback')
                
            # Execute with circuit breaker protection
            return cast(R, circuit.execute(func, fallback, *args, **kwargs))
            
        # Add reference to the circuit breaker
        wrapper.circuit_breaker = circuit  # type: ignore
        
        return wrapper
        
    return decorator