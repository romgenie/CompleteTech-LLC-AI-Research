"""
Progressive fallback strategies for the Knowledge Extraction Pipeline.

This module provides fallback mechanisms that degrade gracefully when
dependencies or services fail, ensuring the system can continue to operate
with reduced functionality rather than failing completely.
"""

import logging
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union, cast
from functools import wraps

from src.research_orchestrator.knowledge_extraction.recovery.circuit_breaker import (
    CircuitBreaker, get_circuit_breaker
)

logger = logging.getLogger(__name__)

# Type variables for generic function signatures
T = TypeVar('T')
R = TypeVar('R')


class FallbackResult(Generic[T]):
    """
    Result of a fallback operation, including metadata about how it was produced.
    
    This class wraps the actual result, including information on whether
    the result was produced by the primary function or a fallback, and
    other metadata that helps in understanding the quality and source of the result.
    """
    
    def __init__(self, 
                value: T,
                from_fallback: bool = False,
                fallback_level: int = 0,
                quality: float = 1.0,
                error: Optional[Exception] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a fallback result.
        
        Args:
            value: The actual result
            from_fallback: Whether this was produced by a fallback function
            fallback_level: Which fallback level was used (0 = primary)
            quality: Quality estimate of the result (0.0-1.0)
            error: Original error that triggered the fallback (if any)
            metadata: Additional metadata about the result
        """
        self.value = value
        self.from_fallback = from_fallback
        self.fallback_level = fallback_level
        self.quality = quality
        self.error = error
        self.metadata = metadata or {}
        
    def __repr__(self) -> str:
        """String representation of the result."""
        status = "fallback" if self.from_fallback else "primary"
        return f"FallbackResult({status}, level={self.fallback_level}, " + \
               f"quality={self.quality:.2f}, value={self.value!r})"
        
    def unwrap(self) -> T:
        """
        Get the raw value without the wrapper.
        
        Returns:
            The wrapped value
        """
        return self.value


class ExtractionLevel(Enum):
    """
    Levels of extraction capability, from most to least comprehensive.
    
    These levels represent different capabilities that can be used when
    degrading gracefully in response to failures or resource constraints.
    """
    FULL = "full"           # Full extraction with all features
    STANDARD = "standard"   # Standard extraction with core features
    BASIC = "basic"         # Basic extraction with minimal features
    MINIMAL = "minimal"     # Minimal extraction for critical paths only


class FallbackStrategy:
    """
    Defines how fallbacks should be handled for different services and operations.
    
    A fallback strategy maps a sequence of functions that should be tried
    in order when the primary function fails, with optional quality estimates
    and circuit breaker protection.
    """
    
    def __init__(self, 
                name: str,
                primary_func: Callable[..., R],
                fallback_funcs: Optional[List[Callable[..., R]]] = None,
                circuit_breaker: Optional[CircuitBreaker] = None,
                quality_estimates: Optional[List[float]] = None,
                error_handler: Optional[Callable[[Exception, Dict[str, Any]], R]] = None,
                wrap_result: bool = True):
        """
        Initialize a fallback strategy.
        
        Args:
            name: Name for this fallback strategy
            primary_func: Primary function to execute
            fallback_funcs: Ordered list of fallback functions to try
            circuit_breaker: Optional circuit breaker to protect calls
            quality_estimates: Quality estimate for each function (0.0-1.0)
            error_handler: Optional handler for errors from all functions
            wrap_result: Whether to wrap results in FallbackResult
        """
        self.name = name
        self.primary_func = primary_func
        self.fallback_funcs = fallback_funcs or []
        
        # Create or use provided circuit breaker
        self.circuit_breaker = circuit_breaker or get_circuit_breaker(f"fallback_{name}")
        
        # Quality estimates (default to degrading quality)
        if quality_estimates:
            if len(quality_estimates) != len(self.fallback_funcs) + 1:
                raise ValueError(
                    f"Quality estimates must match number of functions " +
                    f"(expected {len(self.fallback_funcs) + 1}, got {len(quality_estimates)})"
                )
            self.quality_estimates = quality_estimates
        else:
            # Generate degrading quality estimates if not provided
            primary_quality = 1.0
            fallback_qualities = [
                max(0.1, primary_quality * (0.7 ** (i + 1)))
                for i in range(len(self.fallback_funcs))
            ]
            self.quality_estimates = [primary_quality] + fallback_qualities
            
        self.error_handler = error_handler
        self.wrap_result = wrap_result
        
        logger.debug(f"Created fallback strategy '{name}' with " +
                    f"{len(self.fallback_funcs)} fallback functions")
        
    def execute(self, *args: Any, **kwargs: Any) -> Union[R, FallbackResult[R]]:
        """
        Execute with fallback strategy.
        
        This tries the primary function first, then falls back through the
        fallback functions in order if failures occur.
        
        Args:
            *args, **kwargs: Arguments to pass to the functions
            
        Returns:
            Result from the first successful function, or FallbackResult if wrap_result=True
            
        Raises:
            Exception: If all functions fail and no error_handler is provided
        """
        # Try the primary function first
        primary_error = None
        try:
            # Use circuit breaker to protect the primary function
            result = self.circuit_breaker.execute(self.primary_func, None, *args, **kwargs)
            
            # Primary function succeeded
            if self.wrap_result:
                return FallbackResult(
                    value=result,
                    from_fallback=False,
                    fallback_level=0,
                    quality=self.quality_estimates[0]
                )
            return result
        except Exception as e:
            # Primary function failed
            logger.debug(f"Primary function in '{self.name}' failed: {type(e).__name__}")
            primary_error = e
            
        # Try fallback functions in order
        last_error = primary_error
        for i, fallback_func in enumerate(self.fallback_funcs):
            fallback_level = i + 1
            try:
                # Execute fallback function (no circuit breaker for fallbacks)
                result = fallback_func(*args, **kwargs)
                
                # Fallback succeeded
                logger.info(f"Fallback {fallback_level} succeeded for '{self.name}'")
                
                if self.wrap_result:
                    return FallbackResult(
                        value=result,
                        from_fallback=True,
                        fallback_level=fallback_level,
                        quality=self.quality_estimates[fallback_level],
                        error=primary_error
                    )
                return result
            except Exception as e:
                # Fallback failed, continue to next
                logger.debug(f"Fallback {fallback_level} in '{self.name}' failed: {type(e).__name__}")
                last_error = e
                
        # All functions failed
        logger.warning(f"All functions in '{self.name}' failed, " +
                      f"including {len(self.fallback_funcs)} fallbacks")
                
        # If we have an error handler, use it
        if self.error_handler:
            try:
                result = self.error_handler(last_error, {
                    "args": args,
                    "kwargs": kwargs,
                    "primary_error": primary_error
                })
                
                logger.info(f"Error handler for '{self.name}' provided a result")
                
                if self.wrap_result:
                    return FallbackResult(
                        value=result,
                        from_fallback=True, 
                        fallback_level=len(self.fallback_funcs) + 1,
                        quality=0.1,  # Very low quality for error handler
                        error=last_error
                    )
                return result
            except Exception as e:
                # Error handler failed
                logger.error(f"Error handler for '{self.name}' failed: {str(e)}")
                # Fall through to re-raise the last error
                
        # Re-raise the last error
        raise last_error


class ProgressiveExtractor:
    """
    Extractor that falls back to simpler methods on failure.
    
    This class implements a progressive fallback approach specifically for
    extraction tasks, where more complex extraction methods can be replaced
    with simpler ones that are more likely to succeed but may extract less
    information or lower quality information.
    """
    
    def __init__(self, 
                start_level: ExtractionLevel = ExtractionLevel.FULL,
                fallback_levels: Optional[List[ExtractionLevel]] = None):
        """
        Initialize a progressive extractor.
        
        Args:
            start_level: Initial extraction level to try
            fallback_levels: Extraction levels to try in order (defaults to all remaining levels)
        """
        self.current_level = start_level
        
        # If fallback levels aren't specified, use all levels below the start level
        if fallback_levels is None:
            # Get all levels in order
            all_levels = list(ExtractionLevel)
            
            # Find the start level index
            start_index = all_levels.index(start_level)
            
            # Use all remaining levels
            self.fallback_levels = all_levels[start_index + 1:]
        else:
            self.fallback_levels = fallback_levels
            
        self.max_fallbacks = len(self.fallback_levels)
        self.fallback_count = 0
        self.results: Dict[ExtractionLevel, Dict[str, Any]] = {}
        
        logger.debug(f"Created ProgressiveExtractor starting at {start_level.value} " +
                    f"with {self.max_fallbacks} fallback levels")
        
    def process(self, 
               content: Any,
               extractors: Dict[ExtractionLevel, Callable[[Any, Dict[str, Any]], T]],
               metadata: Optional[Dict[str, Any]] = None) -> FallbackResult[T]:
        """
        Process content with progressive fallback.
        
        This attempts extraction starting from the current level and falls
        back to simpler methods if failures occur.
        
        Args:
            content: Content to process
            extractors: Mapping of extraction levels to extractor functions
            metadata: Additional metadata to pass to extractors
            
        Returns:
            FallbackResult containing the extraction results and metadata
            
        Raises:
            ValueError: If no extractors were successful
        """
        metadata = metadata or {}
        original_level = self.current_level
        tried_levels = []
        last_error = None
        
        # First, try the current level
        try:
            extractor = extractors.get(self.current_level)
            if not extractor:
                raise ValueError(f"No extractor defined for level {self.current_level.value}")
                
            result = extractor(content, metadata)
            
            # Store the result
            self.results[self.current_level] = {
                "result": result,
                "extraction_level": self.current_level.value,
                "fallback": False
            }
            
            # Create FallbackResult with quality based on level
            quality = self._get_quality_for_level(self.current_level)
            return FallbackResult(
                value=result,
                from_fallback=False,
                fallback_level=0,
                quality=quality
            )
        except Exception as e:
            # Log the failure
            logger.warning(f"Extraction failed at level {self.current_level.value}: {str(e)}")
            tried_levels.append(self.current_level)
            last_error = e
            
            # Fall through to fallback processing
            
        # Try fallback levels in order
        current_fallback = 0
        for level in self.fallback_levels:
            # Skip already tried levels
            if level in tried_levels:
                continue
                
            # Try this fallback level
            current_fallback += 1
            try:
                extractor = extractors.get(level)
                if not extractor:
                    logger.warning(f"No extractor defined for fallback level {level.value}, skipping")
                    continue
                    
                logger.info(f"Trying fallback extraction at level {level.value}")
                result = extractor(content, metadata)
                
                # Store the result
                self.results[level] = {
                    "result": result,
                    "extraction_level": level.value,
                    "fallback": True,
                    "fallback_level": current_fallback
                }
                
                # Update current level for next time
                self.current_level = level
                self.fallback_count += 1
                
                # Create FallbackResult
                quality = self._get_quality_for_level(level)
                return FallbackResult(
                    value=result,
                    from_fallback=True,
                    fallback_level=current_fallback,
                    quality=quality,
                    error=last_error
                )
            except Exception as e:
                # Log the failure
                logger.warning(f"Fallback extraction failed at level {level.value}: {str(e)}")
                tried_levels.append(level)
                last_error = e
                
        # All extractors failed
        error_msg = f"All extraction methods failed, including {len(tried_levels)} fallbacks"
        logger.error(error_msg)
        
        # Reset to original level for next time
        self.current_level = original_level
        
        # Re-raise the last error
        if last_error:
            raise last_error
        else:
            raise ValueError(error_msg)
            
    def _get_quality_for_level(self, level: ExtractionLevel) -> float:
        """
        Get the quality estimate for an extraction level.
        
        Args:
            level: The extraction level
            
        Returns:
            Quality estimate (0.0-1.0)
        """
        # Quality degrades as we move to simpler levels
        if level == ExtractionLevel.FULL:
            return 1.0
        elif level == ExtractionLevel.STANDARD:
            return 0.8
        elif level == ExtractionLevel.BASIC:
            return 0.5
        elif level == ExtractionLevel.MINIMAL:
            return 0.3
        return 0.1  # Unknown level
        
    def reset(self) -> None:
        """Reset the extractor to its initial state."""
        self.fallback_count = 0
        self.results = {}


def with_fallback(name: str,
                fallback_funcs: Optional[List[Callable[..., Any]]] = None,
                circuit_breaker_options: Optional[Dict[str, Any]] = None,
                quality_estimates: Optional[List[float]] = None,
                error_handler: Optional[Callable[[Exception, Dict[str, Any]], Any]] = None,
                wrap_result: bool = True):
    """
    Decorator for functions that should have fallback options.
    
    Args:
        name: Name for the fallback strategy
        fallback_funcs: Ordered list of fallback functions to try
        circuit_breaker_options: Options for the circuit breaker
        quality_estimates: Quality estimate for each function (0.0-1.0)
        error_handler: Optional handler for errors from all functions
        wrap_result: Whether to wrap results in FallbackResult
        
    Returns:
        Decorated function
        
    Example:
        @with_fallback("entity_extraction", 
                     [simple_entity_extraction, pattern_based_extraction])
        def extract_entities(document):
            # Primary extraction logic that might fail
            ...
    """
    def decorator(func: Callable[..., R]) -> Callable[..., Union[R, FallbackResult[R]]]:
        # Create circuit breaker if options provided
        circuit_breaker = None
        if circuit_breaker_options:
            circuit_name = circuit_breaker_options.pop("name", f"fallback_{name}")
            circuit_breaker = get_circuit_breaker(circuit_name, **circuit_breaker_options)
            
        # Create the fallback strategy
        strategy = FallbackStrategy(
            name=name,
            primary_func=func,
            fallback_funcs=fallback_funcs,
            circuit_breaker=circuit_breaker,
            quality_estimates=quality_estimates,
            error_handler=error_handler,
            wrap_result=wrap_result
        )
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[R, FallbackResult[R]]:
            return strategy.execute(*args, **kwargs)
            
        # Add reference to the strategy
        wrapper.fallback_strategy = strategy  # type: ignore
        
        return wrapper
        
    return decorator