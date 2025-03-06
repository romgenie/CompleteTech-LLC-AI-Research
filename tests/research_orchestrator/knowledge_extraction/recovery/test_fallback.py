"""
Tests for the progressive fallback recovery system.

This module contains tests for the fallback strategies that enable graceful
degradation when services or dependencies fail.
"""

import unittest
from unittest.mock import Mock, patch

from src.research_orchestrator.knowledge_extraction.recovery.fallback import (
    FallbackResult, FallbackStrategy, ExtractionLevel, ProgressiveExtractor,
    with_fallback
)
from src.research_orchestrator.knowledge_extraction.recovery.circuit_breaker import (
    CircuitBreaker
)


class TestFallbackResult(unittest.TestCase):
    """Tests for the FallbackResult class."""
    
    def test_initialization(self):
        """Test basic initialization of FallbackResult."""
        result = FallbackResult(
            value="test_value",
            from_fallback=True,
            fallback_level=2,
            quality=0.7,
            error=ValueError("Test error"),
            metadata={"source": "test"}
        )
        
        self.assertEqual(result.value, "test_value")
        self.assertTrue(result.from_fallback)
        self.assertEqual(result.fallback_level, 2)
        self.assertEqual(result.quality, 0.7)
        self.assertIsInstance(result.error, ValueError)
        self.assertEqual(result.metadata, {"source": "test"})
        
    def test_default_values(self):
        """Test default values for FallbackResult."""
        result = FallbackResult("test_value")
        
        self.assertEqual(result.value, "test_value")
        self.assertFalse(result.from_fallback)
        self.assertEqual(result.fallback_level, 0)
        self.assertEqual(result.quality, 1.0)
        self.assertIsNone(result.error)
        self.assertEqual(result.metadata, {})
        
    def test_representation(self):
        """Test string representation of FallbackResult."""
        # Test primary result
        primary = FallbackResult("test_value")
        self.assertIn("primary", repr(primary))
        self.assertIn("level=0", repr(primary))
        self.assertIn("quality=1.00", repr(primary))
        
        # Test fallback result
        fallback = FallbackResult("fallback_value", from_fallback=True, fallback_level=1, quality=0.5)
        self.assertIn("fallback", repr(fallback))
        self.assertIn("level=1", repr(fallback))
        self.assertIn("quality=0.50", repr(fallback))
        
    def test_unwrap(self):
        """Test unwrapping the result value."""
        result = FallbackResult(["item1", "item2"])
        self.assertEqual(result.unwrap(), ["item1", "item2"])


class TestFallbackStrategy(unittest.TestCase):
    """Tests for the FallbackStrategy class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock functions
        self.primary_func = Mock(return_value="primary_result")
        self.fallback1 = Mock(return_value="fallback1_result")
        self.fallback2 = Mock(return_value="fallback2_result")
        self.error_handler = Mock(return_value="error_handler_result")
        
        # Create a circuit breaker
        self.circuit_breaker = CircuitBreaker("test_circuit")
        
        # Create a fallback strategy
        self.strategy = FallbackStrategy(
            name="test_strategy",
            primary_func=self.primary_func,
            fallback_funcs=[self.fallback1, self.fallback2],
            circuit_breaker=self.circuit_breaker,
            quality_estimates=[1.0, 0.8, 0.5],
            error_handler=self.error_handler
        )
        
    def test_initialization(self):
        """Test initialization of FallbackStrategy."""
        self.assertEqual(self.strategy.name, "test_strategy")
        self.assertEqual(self.strategy.primary_func, self.primary_func)
        self.assertEqual(self.strategy.fallback_funcs, [self.fallback1, self.fallback2])
        self.assertEqual(self.strategy.circuit_breaker, self.circuit_breaker)
        self.assertEqual(self.strategy.quality_estimates, [1.0, 0.8, 0.5])
        self.assertEqual(self.strategy.error_handler, self.error_handler)
        self.assertTrue(self.strategy.wrap_result)
        
    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        strategy = FallbackStrategy(
            name="simple_strategy",
            primary_func=self.primary_func
        )
        
        self.assertEqual(strategy.name, "simple_strategy")
        self.assertEqual(strategy.primary_func, self.primary_func)
        self.assertEqual(strategy.fallback_funcs, [])
        self.assertIsNotNone(strategy.circuit_breaker)
        self.assertEqual(strategy.quality_estimates, [1.0])
        self.assertIsNone(strategy.error_handler)
        self.assertTrue(strategy.wrap_result)
        
    def test_quality_estimates_validation(self):
        """Test validation of quality estimates."""
        # Test with incorrect number of quality estimates
        with self.assertRaises(ValueError):
            FallbackStrategy(
                name="invalid_strategy",
                primary_func=self.primary_func,
                fallback_funcs=[self.fallback1, self.fallback2],
                quality_estimates=[1.0, 0.8]  # Missing one estimate
            )
            
    def test_automatic_quality_estimates(self):
        """Test automatic generation of quality estimates."""
        strategy = FallbackStrategy(
            name="auto_quality",
            primary_func=self.primary_func,
            fallback_funcs=[self.fallback1, self.fallback2, self.fallback1]
        )
        
        # Verify primary is 1.0 and fallbacks degrade
        self.assertEqual(strategy.quality_estimates[0], 1.0)
        for i in range(1, len(strategy.quality_estimates)):
            # Each level should be lower than the previous
            self.assertLess(strategy.quality_estimates[i], strategy.quality_estimates[i-1])
            # But not less than 0.1
            self.assertGreaterEqual(strategy.quality_estimates[i], 0.1)
            
    def test_successful_primary_execution(self):
        """Test successful execution of primary function."""
        result = self.strategy.execute("arg1", kwarg1="value1")
        
        # Verify primary function was called
        self.primary_func.assert_called_once_with("arg1", kwarg1="value1")
        
        # Verify fallbacks were not called
        self.fallback1.assert_not_called()
        self.fallback2.assert_not_called()
        
        # Verify result is wrapped
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, "primary_result")
        self.assertFalse(result.from_fallback)
        self.assertEqual(result.fallback_level, 0)
        self.assertEqual(result.quality, 1.0)
        
    def test_fallback_execution(self):
        """Test fallback execution when primary fails."""
        # Make primary function fail
        self.primary_func.side_effect = ValueError("Primary failed")
        
        result = self.strategy.execute("arg1", kwarg1="value1")
        
        # Verify primary function was called
        self.primary_func.assert_called_once_with("arg1", kwarg1="value1")
        
        # Verify first fallback was called
        self.fallback1.assert_called_once_with("arg1", kwarg1="value1")
        
        # Verify second fallback was not called
        self.fallback2.assert_not_called()
        
        # Verify result is wrapped
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, "fallback1_result")
        self.assertTrue(result.from_fallback)
        self.assertEqual(result.fallback_level, 1)
        self.assertEqual(result.quality, 0.8)
        self.assertIsInstance(result.error, ValueError)
        
    def test_multiple_fallbacks(self):
        """Test multiple fallbacks when primary and first fallback fail."""
        # Make primary and first fallback fail
        self.primary_func.side_effect = ValueError("Primary failed")
        self.fallback1.side_effect = RuntimeError("Fallback1 failed")
        
        result = self.strategy.execute("arg1", kwarg1="value1")
        
        # Verify all functions were called in order
        self.primary_func.assert_called_once_with("arg1", kwarg1="value1")
        self.fallback1.assert_called_once_with("arg1", kwarg1="value1")
        self.fallback2.assert_called_once_with("arg1", kwarg1="value1")
        
        # Verify result is wrapped
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, "fallback2_result")
        self.assertTrue(result.from_fallback)
        self.assertEqual(result.fallback_level, 2)
        self.assertEqual(result.quality, 0.5)
        
    def test_error_handler(self):
        """Test error handler when all functions fail."""
        # Make all functions fail
        self.primary_func.side_effect = ValueError("Primary failed")
        self.fallback1.side_effect = RuntimeError("Fallback1 failed")
        self.fallback2.side_effect = AttributeError("Fallback2 failed")
        
        result = self.strategy.execute("arg1", kwarg1="value1")
        
        # Verify all functions were called
        self.primary_func.assert_called_once_with("arg1", kwarg1="value1")
        self.fallback1.assert_called_once_with("arg1", kwarg1="value1")
        self.fallback2.assert_called_once_with("arg1", kwarg1="value1")
        
        # Verify error handler was called
        self.error_handler.assert_called_once()
        
        # Verify result is wrapped
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, "error_handler_result")
        self.assertTrue(result.from_fallback)
        self.assertEqual(result.fallback_level, 3)
        self.assertLessEqual(result.quality, 0.1)
        
    def test_all_functions_fail(self):
        """Test case when all functions fail and no error handler."""
        # Create strategy without error handler
        strategy = FallbackStrategy(
            name="all_fail",
            primary_func=self.primary_func,
            fallback_funcs=[self.fallback1, self.fallback2],
            error_handler=None
        )
        
        # Make all functions fail
        self.primary_func.side_effect = ValueError("Primary failed")
        self.fallback1.side_effect = RuntimeError("Fallback1 failed")
        self.fallback2.side_effect = AttributeError("Fallback2 failed")
        
        # Execute should re-raise the last error
        with self.assertRaises(AttributeError):
            strategy.execute("arg1", kwarg1="value1")
            
        # Verify all functions were called
        self.primary_func.assert_called_once_with("arg1", kwarg1="value1")
        self.fallback1.assert_called_once_with("arg1", kwarg1="value1")
        self.fallback2.assert_called_once_with("arg1", kwarg1="value1")
        
    def test_unwrapped_results(self):
        """Test strategy with unwrapped results."""
        # Create strategy with wrap_result=False
        strategy = FallbackStrategy(
            name="unwrapped",
            primary_func=self.primary_func,
            fallback_funcs=[self.fallback1],
            wrap_result=False
        )
        
        # Test primary success
        result = strategy.execute()
        self.assertEqual(result, "primary_result")
        self.assertNotIsInstance(result, FallbackResult)
        
        # Test fallback
        self.primary_func.side_effect = ValueError("Primary failed")
        result = strategy.execute()
        self.assertEqual(result, "fallback1_result")
        self.assertNotIsInstance(result, FallbackResult)


class TestProgressiveExtractor(unittest.TestCase):
    """Tests for the ProgressiveExtractor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.extractor = ProgressiveExtractor(start_level=ExtractionLevel.FULL)
        
        # Create mock extractors for each level
        self.extractors = {
            ExtractionLevel.FULL: Mock(return_value={"entities": ["e1", "e2", "e3", "e4"]}),
            ExtractionLevel.STANDARD: Mock(return_value={"entities": ["e1", "e2", "e3"]}),
            ExtractionLevel.BASIC: Mock(return_value={"entities": ["e1", "e2"]}),
            ExtractionLevel.MINIMAL: Mock(return_value={"entities": ["e1"]})
        }
        
    def test_initialization(self):
        """Test initialization of ProgressiveExtractor."""
        self.assertEqual(self.extractor.current_level, ExtractionLevel.FULL)
        self.assertEqual(self.extractor.fallback_levels, [
            ExtractionLevel.STANDARD,
            ExtractionLevel.BASIC,
            ExtractionLevel.MINIMAL
        ])
        self.assertEqual(self.extractor.max_fallbacks, 3)
        self.assertEqual(self.extractor.fallback_count, 0)
        self.assertEqual(self.extractor.results, {})
        
    def test_initialization_with_custom_fallbacks(self):
        """Test initialization with custom fallback levels."""
        extractor = ProgressiveExtractor(
            start_level=ExtractionLevel.STANDARD,
            fallback_levels=[ExtractionLevel.MINIMAL]  # Skip BASIC
        )
        
        self.assertEqual(extractor.current_level, ExtractionLevel.STANDARD)
        self.assertEqual(extractor.fallback_levels, [ExtractionLevel.MINIMAL])
        self.assertEqual(extractor.max_fallbacks, 1)
        
    def test_successful_extraction(self):
        """Test successful extraction at the highest level."""
        result = self.extractor.process("test_content", self.extractors)
        
        # Verify only the FULL extractor was called
        self.extractors[ExtractionLevel.FULL].assert_called_once_with("test_content", {})
        self.extractors[ExtractionLevel.STANDARD].assert_not_called()
        self.extractors[ExtractionLevel.BASIC].assert_not_called()
        self.extractors[ExtractionLevel.MINIMAL].assert_not_called()
        
        # Verify result
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, {"entities": ["e1", "e2", "e3", "e4"]})
        self.assertFalse(result.from_fallback)
        self.assertEqual(result.fallback_level, 0)
        self.assertEqual(result.quality, 1.0)
        
        # Verify results were stored
        self.assertIn(ExtractionLevel.FULL, self.extractor.results)
        
    def test_fallback_to_standard(self):
        """Test fallback to STANDARD when FULL fails."""
        # Make FULL extractor fail
        self.extractors[ExtractionLevel.FULL].side_effect = ValueError("FULL failed")
        
        result = self.extractor.process("test_content", self.extractors)
        
        # Verify FULL and STANDARD extractors were called
        self.extractors[ExtractionLevel.FULL].assert_called_once_with("test_content", {})
        self.extractors[ExtractionLevel.STANDARD].assert_called_once_with("test_content", {})
        self.extractors[ExtractionLevel.BASIC].assert_not_called()
        self.extractors[ExtractionLevel.MINIMAL].assert_not_called()
        
        # Verify result
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, {"entities": ["e1", "e2", "e3"]})
        self.assertTrue(result.from_fallback)
        self.assertEqual(result.fallback_level, 1)
        self.assertEqual(result.quality, 0.8)
        self.assertIsInstance(result.error, ValueError)
        
        # Verify results were stored
        self.assertIn(ExtractionLevel.STANDARD, self.extractor.results)
        self.assertEqual(self.extractor.fallback_count, 1)
        
        # Verify current level was updated for next time
        self.assertEqual(self.extractor.current_level, ExtractionLevel.STANDARD)
        
    def test_fallback_to_minimal(self):
        """Test fallback to MINIMAL when all higher levels fail."""
        # Make all higher level extractors fail
        self.extractors[ExtractionLevel.FULL].side_effect = ValueError("FULL failed")
        self.extractors[ExtractionLevel.STANDARD].side_effect = ValueError("STANDARD failed")
        self.extractors[ExtractionLevel.BASIC].side_effect = ValueError("BASIC failed")
        
        result = self.extractor.process("test_content", self.extractors)
        
        # Verify all extractors were called
        self.extractors[ExtractionLevel.FULL].assert_called_once_with("test_content", {})
        self.extractors[ExtractionLevel.STANDARD].assert_called_once_with("test_content", {})
        self.extractors[ExtractionLevel.BASIC].assert_called_once_with("test_content", {})
        self.extractors[ExtractionLevel.MINIMAL].assert_called_once_with("test_content", {})
        
        # Verify result
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, {"entities": ["e1"]})
        self.assertTrue(result.from_fallback)
        self.assertEqual(result.fallback_level, 3)
        self.assertEqual(result.quality, 0.3)
        
        # Verify current level was updated
        self.assertEqual(self.extractor.current_level, ExtractionLevel.MINIMAL)
        
    def test_all_extractors_fail(self):
        """Test case when all extractors fail."""
        # Make all extractors fail
        for extractor in self.extractors.values():
            extractor.side_effect = ValueError("Extraction failed")
            
        # Process should raise an error
        with self.assertRaises(ValueError):
            self.extractor.process("test_content", self.extractors)
            
        # Verify all extractors were called
        for extractor in self.extractors.values():
            extractor.assert_called_once_with("test_content", {})
            
        # Verify current level was reset to original
        self.assertEqual(self.extractor.current_level, ExtractionLevel.FULL)
        
    def test_missing_extractor(self):
        """Test handling of missing extractors."""
        # Create extractor dict with missing levels
        incomplete_extractors = {
            ExtractionLevel.FULL: self.extractors[ExtractionLevel.FULL],
            # STANDARD is missing
            ExtractionLevel.BASIC: self.extractors[ExtractionLevel.BASIC]
            # MINIMAL is missing
        }
        
        # Make FULL fail so we try to fall back
        incomplete_extractors[ExtractionLevel.FULL].side_effect = ValueError("FULL failed")
        
        # Process should skip STANDARD and use BASIC
        result = self.extractor.process("test_content", incomplete_extractors)
        
        # Verify BASIC was used
        self.extractors[ExtractionLevel.BASIC].assert_called_once_with("test_content", {})
        self.assertEqual(result.value, {"entities": ["e1", "e2"]})
        self.assertEqual(result.fallback_level, 2)  # Skip STANDARD (1)
        
    def test_metadata_passing(self):
        """Test passing metadata to extractors."""
        metadata = {"source": "test", "options": {"key": "value"}}
        
        result = self.extractor.process("test_content", self.extractors, metadata)
        
        # Verify metadata was passed to extractor
        self.extractors[ExtractionLevel.FULL].assert_called_once_with("test_content", metadata)
        
    def test_reset(self):
        """Test resetting the extractor."""
        # Set some state
        self.extractor.fallback_count = 5
        self.extractor.results = {"test": "value"}
        
        # Reset
        self.extractor.reset()
        
        # Verify state was reset
        self.assertEqual(self.extractor.fallback_count, 0)
        self.assertEqual(self.extractor.results, {})


class TestWithFallbackDecorator(unittest.TestCase):
    """Tests for the with_fallback decorator."""
    
    def test_decorator_basic(self):
        """Test basic usage of the decorator."""
        # Define test functions
        def primary_func(arg1, kwarg1=None):
            return f"primary_{arg1}_{kwarg1}"
            
        def fallback_func(arg1, kwarg1=None):
            return f"fallback_{arg1}_{kwarg1}"
            
        # Create decorated function
        decorated = with_fallback("test_fallback", [fallback_func])(primary_func)
        
        # Call the function
        result = decorated("test", kwarg1="value")
        
        # Verify result
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, "primary_test_value")
        self.assertFalse(result.from_fallback)
        
    def test_decorator_fallback(self):
        """Test decorator with fallback."""
        # Define test functions
        def primary_func(arg1, kwarg1=None):
            raise ValueError("Primary failed")
            
        def fallback_func(arg1, kwarg1=None):
            return f"fallback_{arg1}_{kwarg1}"
            
        # Create decorated function
        decorated = with_fallback("test_fallback", [fallback_func])(primary_func)
        
        # Call the function
        result = decorated("test", kwarg1="value")
        
        # Verify result
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, "fallback_test_value")
        self.assertTrue(result.from_fallback)
        self.assertEqual(result.fallback_level, 1)
        
    def test_decorator_unwrapped(self):
        """Test decorator with unwrapped results."""
        # Define test functions
        def primary_func(arg1, kwarg1=None):
            return f"primary_{arg1}_{kwarg1}"
            
        # Create decorated function with unwrapped results
        decorated = with_fallback("test_unwrapped", wrap_result=False)(primary_func)
        
        # Call the function
        result = decorated("test", kwarg1="value")
        
        # Verify result is not wrapped
        self.assertEqual(result, "primary_test_value")
        self.assertNotIsInstance(result, FallbackResult)
        
    def test_decorator_circuit_breaker_options(self):
        """Test decorator with circuit breaker options."""
        # Define test function
        def primary_func():
            return "primary_result"
            
        # Create decorated function with circuit breaker options
        circuit_options = {
            "name": "custom_circuit",
            "failure_threshold": 2,
            "recovery_timeout": 0.1
        }
        
        decorated = with_fallback(
            "test_circuit",
            circuit_breaker_options=circuit_options
        )(primary_func)
        
        # Verify circuit breaker was created with correct options
        circuit = decorated.fallback_strategy.circuit_breaker
        self.assertEqual(circuit.name, "custom_circuit")
        self.assertEqual(circuit.failure_threshold, 2)
        self.assertEqual(circuit.recovery_timeout, 0.1)
        
    def test_decorator_error_handler(self):
        """Test decorator with error handler."""
        # Define test functions
        def primary_func():
            raise ValueError("Primary failed")
            
        def error_handler(error, context):
            return f"handled_{type(error).__name__}"
            
        # Create decorated function with error handler
        decorated = with_fallback(
            "test_handler",
            error_handler=error_handler
        )(primary_func)
        
        # Call the function
        result = decorated()
        
        # Verify result
        self.assertIsInstance(result, FallbackResult)
        self.assertEqual(result.value, "handled_ValueError")
        self.assertTrue(result.from_fallback)
        self.assertLessEqual(result.quality, 0.1)
        

if __name__ == '__main__':
    unittest.main()