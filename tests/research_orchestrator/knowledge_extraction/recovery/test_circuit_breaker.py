"""
Tests for the circuit breaker recovery system.

This module contains tests for the CircuitBreaker class and related utilities
used for protecting against failing dependencies.
"""

import time
import unittest
from unittest.mock import Mock, patch

from src.research_orchestrator.knowledge_extraction.recovery.circuit_breaker import (
    CircuitBreaker, CircuitOpenError, CircuitState,
    get_circuit_breaker, circuit_protected, circuit_breaker_registry
)


class TestCircuitBreaker(unittest.TestCase):
    """Tests for the CircuitBreaker class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a circuit breaker with a small recovery timeout for faster testing
        self.cb = CircuitBreaker(
            name="test_circuit",
            failure_threshold=3,
            recovery_timeout=0.1,  # 100ms for faster testing
            half_open_max_calls=1
        )
        
    def test_initialization(self):
        """Test circuit breaker initialization."""
        self.assertEqual(self.cb.name, "test_circuit")
        self.assertEqual(self.cb.state, CircuitState.CLOSED)
        self.assertEqual(self.cb.failure_count, 0)
        self.assertEqual(self.cb.failure_threshold, 3)
        self.assertEqual(self.cb.recovery_timeout, 0.1)
        self.assertEqual(self.cb.half_open_max_calls, 1)
        
    def test_successful_execution(self):
        """Test successful function execution."""
        test_func = Mock(return_value="success")
        
        # Execute function through circuit breaker
        result = self.cb.execute(test_func, None, "arg1", "arg2", kwarg1="value1")
        
        # Verify function was called with correct arguments
        test_func.assert_called_once_with("arg1", "arg2", kwarg1="value1")
        self.assertEqual(result, "success")
        
        # Verify circuit state
        self.assertEqual(self.cb.state, CircuitState.CLOSED)
        self.assertEqual(self.cb.success_count, 1)
        self.assertEqual(self.cb.failure_count, 0)
        
    def test_failed_execution(self):
        """Test failed function execution."""
        # Create a function that raises an exception
        test_func = Mock(side_effect=ValueError("Test error"))
        
        # Execute function through circuit breaker (no fallback)
        with self.assertRaises(ValueError):
            self.cb.execute(test_func, None)
            
        # Verify circuit state
        self.assertEqual(self.cb.state, CircuitState.CLOSED)
        self.assertEqual(self.cb.failure_count, 1)
        
    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after failure threshold is reached."""
        # Create a function that raises an exception
        test_func = Mock(side_effect=RuntimeError("Test failure"))
        
        # Execute function until we hit the threshold
        for i in range(self.cb.failure_threshold):
            with self.assertRaises(RuntimeError):
                self.cb.execute(test_func, None)
                
            # Check circuit state after each call
            if i < self.cb.failure_threshold - 1:
                # Still below threshold
                self.assertEqual(self.cb.state, CircuitState.CLOSED)
            else:
                # Hit threshold, circuit should be open
                self.assertEqual(self.cb.state, CircuitState.OPEN)
                
        # Verify circuit state at the end
        self.assertEqual(self.cb.state, CircuitState.OPEN)
        self.assertEqual(self.cb.failure_count, self.cb.failure_threshold)
        
    def test_open_circuit_rejects_calls(self):
        """Test that open circuit rejects calls."""
        # Force circuit to open
        self.cb.state = CircuitState.OPEN
        self.cb.last_failure_time = time.time()
        
        # Try to execute a function
        test_func = Mock(return_value="success")
        
        with self.assertRaises(CircuitOpenError):
            self.cb.execute(test_func, None)
            
        # Verify function was not called
        test_func.assert_not_called()
        
    def test_open_circuit_uses_fallback(self):
        """Test that open circuit uses fallback if provided."""
        # Force circuit to open
        self.cb.state = CircuitState.OPEN
        self.cb.last_failure_time = time.time()
        
        # Define main function and fallback
        test_func = Mock(return_value="success")
        fallback_func = Mock(return_value="fallback_result")
        
        # Execute with fallback
        result = self.cb.execute(test_func, fallback_func, "arg1", kwarg1="value1")
        
        # Verify fallback was called, but not main function
        test_func.assert_not_called()
        fallback_func.assert_called_once_with("arg1", kwarg1="value1")
        self.assertEqual(result, "fallback_result")
        
    def test_circuit_transitions_to_half_open_after_timeout(self):
        """Test circuit transitions to half-open after recovery timeout."""
        # Force circuit to open
        self.cb.state = CircuitState.OPEN
        self.cb.last_failure_time = time.time() - (self.cb.recovery_timeout * 2)  # Past timeout
        
        # Try to execute a function
        test_func = Mock(return_value="success")
        
        # Execute
        result = self.cb.execute(test_func, None)
        
        # Verify function was called
        test_func.assert_called_once()
        self.assertEqual(result, "success")
        
        # Verify circuit state
        self.assertEqual(self.cb.state, CircuitState.CLOSED)  # Success in half-open closes circuit
        
    def test_half_open_circuit_limits_calls(self):
        """Test half-open circuit limits concurrent calls."""
        # Force circuit to half-open
        self.cb.state = CircuitState.HALF_OPEN
        self.cb.half_open_calls = self.cb.half_open_max_calls
        
        # Try to execute a function
        test_func = Mock(return_value="success")
        
        with self.assertRaises(CircuitOpenError):
            self.cb.execute(test_func, None)
            
        # Verify function was not called
        test_func.assert_not_called()
        
    def test_half_open_failure_reopens_circuit(self):
        """Test failure in half-open state reopens the circuit."""
        # Force circuit to half-open
        self.cb.state = CircuitState.HALF_OPEN
        self.cb.half_open_calls = 0
        
        # Define function that fails
        test_func = Mock(side_effect=ValueError("Test error"))
        
        # Execute
        with self.assertRaises(ValueError):
            self.cb.execute(test_func, None)
            
        # Verify circuit state
        self.assertEqual(self.cb.state, CircuitState.OPEN)
        
    def test_allowed_exceptions_not_counted(self):
        """Test that allowed exceptions don't count as failures."""
        # Create circuit with allowed exceptions
        cb = CircuitBreaker(
            name="allowed_exceptions_test",
            failure_threshold=2,
            allowed_exceptions=[ValueError]
        )
        
        # Create a function that raises an allowed exception
        allowed_func = Mock(side_effect=ValueError("Allowed error"))
        
        # Execute multiple times - should raise but not count as failure
        for _ in range(cb.failure_threshold + 1):
            with self.assertRaises(ValueError):
                cb.execute(allowed_func, None)
                
        # Circuit should still be closed
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertEqual(cb.failure_count, 0)
        
        # Now try with a non-allowed exception
        not_allowed_func = Mock(side_effect=RuntimeError("Not allowed error"))
        
        # Execute until threshold
        for i in range(cb.failure_threshold):
            with self.assertRaises(RuntimeError):
                cb.execute(not_allowed_func, None)
                
        # Circuit should be open now
        self.assertEqual(cb.state, CircuitState.OPEN)
        
    def test_reset(self):
        """Test resetting the circuit breaker."""
        # Force circuit to open state with some metrics
        self.cb.state = CircuitState.OPEN
        self.cb.failure_count = 5
        self.cb.success_count = 10
        self.cb.last_failure_time = time.time()
        
        # Reset the circuit
        self.cb.reset()
        
        # Verify circuit state
        self.assertEqual(self.cb.state, CircuitState.CLOSED)
        self.assertEqual(self.cb.failure_count, 0)
        self.assertEqual(self.cb.success_count, 0)
        self.assertIsNone(self.cb.last_failure_time)
        
    def test_get_state_dict(self):
        """Test getting circuit state as dictionary."""
        # Set some circuit state
        self.cb.failure_count = 2
        self.cb.success_count = 5
        current_time = time.time()
        self.cb.last_failure_time = current_time - 10
        self.cb.last_success_time = current_time - 5
        
        # Get state dictionary
        state_dict = self.cb.get_state_dict()
        
        # Verify dictionary contains expected keys
        expected_keys = [
            "name", "state", "failure_count", "success_count", 
            "failure_threshold", "recovery_timeout", "half_open_calls",
            "half_open_max_calls", "last_failure_time", "last_success_time",
            "state_change_time", "uptime", "recovery_remaining"
        ]
        
        for key in expected_keys:
            self.assertIn(key, state_dict)
            
        # Verify values
        self.assertEqual(state_dict["name"], "test_circuit")
        self.assertEqual(state_dict["state"], "closed")
        self.assertEqual(state_dict["failure_count"], 2)
        self.assertEqual(state_dict["success_count"], 5)


class TestCircuitBreakerRegistry(unittest.TestCase):
    """Tests for the circuit breaker registry and utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear registry before each test
        circuit_breaker_registry.clear()
        
    def test_get_circuit_breaker(self):
        """Test getting a circuit breaker by name."""
        # Get a new circuit breaker
        cb1 = get_circuit_breaker("test_cb")
        
        # Verify it was created
        self.assertIn("test_cb", circuit_breaker_registry)
        self.assertEqual(cb1.name, "test_cb")
        
        # Get the same circuit breaker again
        cb2 = get_circuit_breaker("test_cb")
        
        # Verify we got the same instance
        self.assertIs(cb1, cb2)
        
        # Get a different circuit breaker
        cb3 = get_circuit_breaker("other_cb")
        
        # Verify we got a different instance
        self.assertIsNot(cb1, cb3)
        self.assertEqual(len(circuit_breaker_registry), 2)
        
    def test_circuit_protected_decorator(self):
        """Test the circuit_protected decorator."""
        # Define test functions
        @circuit_protected("decorated_function")
        def test_func(arg1, kwarg1=None):
            return f"{arg1}_{kwarg1}"
            
        @circuit_protected("decorated_function_with_fallback",
                         fallback_function=lambda arg1, kwarg1=None: "fallback")
        def test_func_with_fallback(arg1, kwarg1=None):
            return f"{arg1}_{kwarg1}"
            
        # Verify circuit breakers were created
        self.assertIn("decorated_function", circuit_breaker_registry)
        self.assertIn("decorated_function_with_fallback", circuit_breaker_registry)
        
        # Call the decorated function
        result = test_func("test", kwarg1="value")
        self.assertEqual(result, "test_value")
        
        # Verify access to circuit breaker
        self.assertTrue(hasattr(test_func, "circuit_breaker"))
        cb = test_func.circuit_breaker
        self.assertEqual(cb.name, "decorated_function")
        self.assertEqual(cb.success_count, 1)
        
        # Force circuit to open
        cb.state = CircuitState.OPEN
        cb.last_failure_time = time.time()
        
        # Try to call the function again
        with self.assertRaises(CircuitOpenError):
            test_func("test", kwarg1="value")
            
        # Try the function with fallback
        cb_fallback = test_func_with_fallback.circuit_breaker
        cb_fallback.state = CircuitState.OPEN
        cb_fallback.last_failure_time = time.time()
        
        result = test_func_with_fallback("test", kwarg1="value")
        self.assertEqual(result, "fallback")
        
    def test_circuit_protected_with_dynamic_fallback(self):
        """Test providing fallback at call time."""
        @circuit_protected("dynamic_fallback")
        def test_func(arg1):
            return arg1.upper()
            
        # Normal call
        result = test_func("test")
        self.assertEqual(result, "TEST")
        
        # Force circuit to open
        cb = test_func.circuit_breaker
        cb.state = CircuitState.OPEN
        cb.last_failure_time = time.time()
        
        # Call with dynamic fallback
        result = test_func("test", _fallback=lambda arg1: f"fallback_{arg1}")
        self.assertEqual(result, "fallback_test")


if __name__ == '__main__':
    unittest.main()