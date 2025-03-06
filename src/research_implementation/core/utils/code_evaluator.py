"""
Code Evaluator for Research Implementation System.

This module provides utilities for evaluating code implementations of research papers,
including functionality for checking correctness, performance, and adherence to
research paper specifications.
"""

from typing import Dict, List, Optional, Any, Union
import logging
import json
import os
import subprocess
import tempfile
import time
import platform
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeEvaluator:
    """
    Evaluator for code implementations of research papers.
    
    This class provides methods for evaluating code implementations, including
    checking for correctness, performance, and adherence to research paper specifications.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the code evaluator.
        
        Args:
            config: Configuration for the code evaluator
        """
        self.config = config or {}
        
        # Detect system environment
        self.system_info = {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "platform": platform.platform()
        }
        
        logger.info(f"Initialized CodeEvaluator with system info: {self.system_info}")
    
    def evaluate_code(self, code_files: List[Dict[str, Any]], 
                     expected_outputs: Dict[str, Any],
                     entry_point: str,
                     dependencies: Optional[List[Dict[str, Any]]] = None,
                     timeout: int = 300) -> Dict[str, Any]:
        """
        Evaluate code files to check if they produce the expected outputs.
        
        Args:
            code_files: List of code files to evaluate
            expected_outputs: Dictionary of expected outputs for different scenarios
            entry_point: Entry point for running the code (file path or command)
            dependencies: List of dependencies needed to run the code
            timeout: Timeout for running the code in seconds
            
        Returns:
            Dictionary containing evaluation results
        """
        # Create a temporary directory for evaluation
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Write code files to the temporary directory
                for code_file in code_files:
                    file_path = os.path.join(temp_dir, code_file["filename"])
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(code_file["content"])
                
                # Install dependencies if provided
                if dependencies:
                    self._install_dependencies(dependencies, temp_dir)
                
                # Run the code
                results = self._run_code(entry_point, temp_dir, expected_outputs, timeout)
                
                return results
            except Exception as e:
                logger.error(f"Error evaluating code: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "comparison": {},
                    "performance": {
                        "memory_usage": None,
                        "execution_time": None
                    }
                }
    
    def evaluate_algorithm_implementation(self, code_files: List[Dict[str, Any]],
                                        algorithm_spec: Dict[str, Any],
                                        test_cases: List[Dict[str, Any]],
                                        entry_point: str,
                                        dependencies: Optional[List[Dict[str, Any]]] = None,
                                        timeout: int = 300) -> Dict[str, Any]:
        """
        Evaluate an algorithm implementation against its specification and test cases.
        
        Args:
            code_files: List of code files to evaluate
            algorithm_spec: Specification of the algorithm (inputs, outputs, etc.)
            test_cases: List of test cases for the algorithm
            entry_point: Entry point for running the code (file path or command)
            dependencies: List of dependencies needed to run the code
            timeout: Timeout for running the code in seconds
            
        Returns:
            Dictionary containing evaluation results
        """
        # Create expected outputs from test cases
        expected_outputs = {}
        for i, test_case in enumerate(test_cases):
            expected_outputs[f"test_case_{i}"] = {
                "input": test_case["input"],
                "expected_output": test_case["expected_output"]
            }
        
        # Evaluate the code
        results = self.evaluate_code(
            code_files=code_files,
            expected_outputs=expected_outputs,
            entry_point=entry_point,
            dependencies=dependencies,
            timeout=timeout
        )
        
        # Analyze results in terms of the algorithm specification
        algorithm_analysis = self._analyze_algorithm_implementation(
            results=results,
            algorithm_spec=algorithm_spec,
            test_cases=test_cases
        )
        
        # Combine results
        combined_results = {
            **results,
            "algorithm_analysis": algorithm_analysis
        }
        
        return combined_results
    
    def verify_implementation_matches_paper(self, implementation: Dict[str, Any],
                                          paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that an implementation matches the specifications in a research paper.
        
        Args:
            implementation: Dictionary containing implementation details
            paper: Dictionary containing paper details
            
        Returns:
            Dictionary containing verification results
        """
        verification_results = {
            "success": True,
            "matches": [],
            "discrepancies": [],
            "score": 0.0
        }
        
        try:
            # Check algorithm implementation
            algorithm_verification = self._verify_algorithms(implementation, paper)
            verification_results["algorithm_verification"] = algorithm_verification
            
            # Check architecture implementation
            architecture_verification = self._verify_architecture(implementation, paper)
            verification_results["architecture_verification"] = architecture_verification
            
            # Check evaluation methodology
            evaluation_verification = self._verify_evaluation(implementation, paper)
            verification_results["evaluation_verification"] = evaluation_verification
            
            # Check results
            results_verification = self._verify_results(implementation, paper)
            verification_results["results_verification"] = results_verification
            
            # Combine results
            matches = (
                algorithm_verification.get("matches", []) +
                architecture_verification.get("matches", []) +
                evaluation_verification.get("matches", []) +
                results_verification.get("matches", [])
            )
            
            discrepancies = (
                algorithm_verification.get("discrepancies", []) +
                architecture_verification.get("discrepancies", []) +
                evaluation_verification.get("discrepancies", []) +
                results_verification.get("discrepancies", [])
            )
            
            verification_results["matches"] = matches
            verification_results["discrepancies"] = discrepancies
            
            # Calculate overall score
            total_points = len(matches) + len(discrepancies)
            if total_points > 0:
                verification_results["score"] = len(matches) / total_points
            else:
                verification_results["score"] = 0.0
            
            return verification_results
        except Exception as e:
            logger.error(f"Error verifying implementation against paper: {e}")
            return {
                "success": False,
                "error": str(e),
                "matches": [],
                "discrepancies": [],
                "score": 0.0
            }
    
    def _install_dependencies(self, dependencies: List[Dict[str, Any]], 
                            working_dir: str) -> bool:
        """
        Install dependencies for code evaluation.
        
        Args:
            dependencies: List of dependencies to install
            working_dir: Working directory for installation
            
        Returns:
            True if installation succeeded, False otherwise
        """
        logger.info(f"Installing {len(dependencies)} dependencies in {working_dir}")
        
        for dependency in dependencies:
            name = dependency.get("name", "")
            version = dependency.get("version", "")
            installation_command = dependency.get("installation_command")
            
            if installation_command:
                command = installation_command
            else:
                if version:
                    command = f"pip install {name}=={version}"
                else:
                    command = f"pip install {name}"
            
            try:
                logger.info(f"Running: {command}")
                
                process = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_dir,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                logger.info(f"Installed {name}: {process.stdout}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error installing {name}: {e.stderr}")
                return False
        
        return True
    
    def _run_code(self, entry_point: str, working_dir: str,
                expected_outputs: Dict[str, Any],
                timeout: int) -> Dict[str, Any]:
        """
        Run code and compare outputs to expected values.
        
        Args:
            entry_point: Entry point for running the code (file path or command)
            working_dir: Working directory for running the code
            expected_outputs: Dictionary of expected outputs for different scenarios
            timeout: Timeout for running the code in seconds
            
        Returns:
            Dictionary containing run results
        """
        results = {
            "success": True,
            "error": None,
            "comparison": {},
            "performance": {
                "memory_usage": None,
                "execution_time": None
            }
        }
        
        # Determine the command to run
        if entry_point.endswith(".py"):
            command = f"python {entry_point}"
        else:
            command = entry_point
        
        # Record start time
        start_time = time.time()
        
        try:
            # Run the command
            process = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                universal_newlines=True
            )
            
            # Record end time
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Parse output
            output = process.stdout
            
            # Compare to expected outputs
            comparison = self._compare_outputs(output, expected_outputs)
            
            # Update results
            results["comparison"] = comparison
            results["performance"]["execution_time"] = execution_time
            
            # Determine success based on comparison
            if comparison.get("match_percentage", 0) < 0.8:
                results["success"] = False
                results["error"] = "Output does not match expected output"
            
            return results
        except subprocess.TimeoutExpired as e:
            logger.error(f"Timeout running code: {e}")
            results["success"] = False
            results["error"] = f"Execution timed out after {timeout} seconds"
            return results
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running code: {e.stderr}")
            results["success"] = False
            results["error"] = f"Execution failed: {e.stderr}"
            return results
        except Exception as e:
            logger.error(f"Unexpected error running code: {e}")
            results["success"] = False
            results["error"] = f"Unexpected error: {str(e)}"
            return results
    
    def _compare_outputs(self, output: str, 
                       expected_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare actual output to expected outputs.
        
        Args:
            output: Actual output from running the code
            expected_outputs: Dictionary of expected outputs for different scenarios
            
        Returns:
            Dictionary containing comparison results
        """
        comparison = {
            "matches": [],
            "mismatches": [],
            "match_percentage": 0.0
        }
        
        # Check each expected output
        for scenario, expected in expected_outputs.items():
            expected_output = expected.get("expected_output", "")
            
            # Compare output with expected output
            if isinstance(expected_output, str):
                # String comparison
                if expected_output in output:
                    comparison["matches"].append(scenario)
                else:
                    comparison["mismatches"].append({
                        "scenario": scenario,
                        "expected": expected_output,
                        "actual": output
                    })
            elif isinstance(expected_output, dict):
                # JSON comparison
                try:
                    # Try to extract JSON from output
                    json_output = self._extract_json_from_output(output)
                    
                    if json_output:
                        # Compare JSON objects
                        matches, mismatches = self._compare_json_objects(json_output, expected_output)
                        
                        if not mismatches:
                            comparison["matches"].append(scenario)
                        else:
                            comparison["mismatches"].append({
                                "scenario": scenario,
                                "expected": expected_output,
                                "actual": json_output,
                                "specific_mismatches": mismatches
                            })
                    else:
                        comparison["mismatches"].append({
                            "scenario": scenario,
                            "expected": expected_output,
                            "actual": output,
                            "error": "Could not extract JSON from output"
                        })
                except Exception as e:
                    comparison["mismatches"].append({
                        "scenario": scenario,
                        "expected": expected_output,
                        "actual": output,
                        "error": str(e)
                    })
            else:
                # Other types of comparison - implement as needed
                comparison["mismatches"].append({
                    "scenario": scenario,
                    "expected": expected_output,
                    "actual": output,
                    "error": "Unsupported output type for comparison"
                })
        
        # Calculate match percentage
        total_scenarios = len(expected_outputs)
        if total_scenarios > 0:
            comparison["match_percentage"] = len(comparison["matches"]) / total_scenarios
        
        return comparison
    
    def _extract_json_from_output(self, output: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON object from output string.
        
        Args:
            output: Output string potentially containing JSON
            
        Returns:
            Extracted JSON object, or None if not found
        """
        # Try to find JSON object in the output
        json_pattern = r'\{(?:[^{}]|(?R))*\}'
        match = re.search(json_pattern, output)
        
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        
        return None
    
    def _compare_json_objects(self, actual: Dict[str, Any], 
                            expected: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Compare actual and expected JSON objects.
        
        Args:
            actual: Actual JSON object
            expected: Expected JSON object
            
        Returns:
            Tuple of (matches, mismatches)
        """
        matches = []
        mismatches = []
        
        # Check each key in expected
        for key, expected_value in expected.items():
            if key in actual:
                actual_value = actual[key]
                
                if isinstance(expected_value, dict) and isinstance(actual_value, dict):
                    # Recursive comparison for nested objects
                    nested_matches, nested_mismatches = self._compare_json_objects(actual_value, expected_value)
                    
                    if not nested_mismatches:
                        matches.append(key)
                    else:
                        mismatches.append({
                            "key": key,
                            "expected": expected_value,
                            "actual": actual_value,
                            "nested_mismatches": nested_mismatches
                        })
                elif isinstance(expected_value, list) and isinstance(actual_value, list):
                    # List comparison - simplified
                    if len(expected_value) == len(actual_value):
                        list_match = True
                        for i, (expected_item, actual_item) in enumerate(zip(expected_value, actual_value)):
                            if expected_item != actual_item:
                                list_match = False
                                mismatches.append({
                                    "key": f"{key}[{i}]",
                                    "expected": expected_item,
                                    "actual": actual_item
                                })
                        
                        if list_match:
                            matches.append(key)
                    else:
                        mismatches.append({
                            "key": key,
                            "expected": f"List of length {len(expected_value)}",
                            "actual": f"List of length {len(actual_value)}"
                        })
                elif expected_value == actual_value:
                    # Direct comparison for simple types
                    matches.append(key)
                else:
                    mismatches.append({
                        "key": key,
                        "expected": expected_value,
                        "actual": actual_value
                    })
            else:
                mismatches.append({
                    "key": key,
                    "expected": expected_value,
                    "actual": "Key not found"
                })
        
        return matches, mismatches
    
    def _analyze_algorithm_implementation(self, results: Dict[str, Any],
                                        algorithm_spec: Dict[str, Any],
                                        test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze an algorithm implementation against its specification and test cases.
        
        Args:
            results: Results from running the code
            algorithm_spec: Specification of the algorithm
            test_cases: List of test cases for the algorithm
            
        Returns:
            Dictionary containing analysis results
        """
        analysis = {
            "correctness": results.get("success", False),
            "efficiency": None,
            "adherence_to_spec": True,
            "notes": []
        }
        
        # Check efficiency if execution time is available
        execution_time = results.get("performance", {}).get("execution_time")
        if execution_time is not None:
            # Compare to expected complexity
            expected_complexity = algorithm_spec.get("complexity", "").lower()
            
            # Simple heuristic for efficiency - can be improved
            if "o(1)" in expected_complexity and execution_time > 1.0:
                analysis["efficiency"] = "poor"
                analysis["notes"].append("Execution time higher than expected for O(1) algorithm")
            elif "o(n)" in expected_complexity and execution_time > 10.0:
                analysis["efficiency"] = "poor"
                analysis["notes"].append("Execution time higher than expected for O(n) algorithm")
            elif "o(n^2)" in expected_complexity and execution_time > 100.0:
                analysis["efficiency"] = "poor"
                analysis["notes"].append("Execution time higher than expected for O(n^2) algorithm")
            elif execution_time < 1.0:
                analysis["efficiency"] = "excellent"
            elif execution_time < 5.0:
                analysis["efficiency"] = "good"
            else:
                analysis["efficiency"] = "acceptable"
        
        # Check adherence to specification
        expected_inputs = set(algorithm_spec.get("inputs", []))
        expected_outputs = set(algorithm_spec.get("outputs", []))
        
        for test_case in test_cases:
            # Check if test case uses all expected inputs
            test_inputs = set(test_case.get("input", {}).keys())
            if not expected_inputs.issubset(test_inputs):
                missing_inputs = expected_inputs - test_inputs
                analysis["adherence_to_spec"] = False
                analysis["notes"].append(f"Test case missing expected inputs: {missing_inputs}")
        
        # Check if there were comparison errors
        comparison = results.get("comparison", {})
        mismatches = comparison.get("mismatches", [])
        
        if mismatches:
            analysis["notes"].append(f"Found {len(mismatches)} mismatches in output comparison")
            
            for mismatch in mismatches:
                analysis["notes"].append(f"Mismatch in scenario {mismatch.get('scenario', '')}")
        
        return analysis
    
    def _verify_algorithms(self, implementation: Dict[str, Any],
                         paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that implementation algorithms match paper algorithms.
        
        Args:
            implementation: Implementation details
            paper: Paper details
            
        Returns:
            Dictionary containing verification results
        """
        # TODO: Implement algorithm verification
        return {
            "matches": [],
            "discrepancies": [],
            "score": 0.0,
            "notes": ["Algorithm verification not yet implemented"]
        }
    
    def _verify_architecture(self, implementation: Dict[str, Any],
                           paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that implementation architecture matches paper architecture.
        
        Args:
            implementation: Implementation details
            paper: Paper details
            
        Returns:
            Dictionary containing verification results
        """
        # TODO: Implement architecture verification
        return {
            "matches": [],
            "discrepancies": [],
            "score": 0.0,
            "notes": ["Architecture verification not yet implemented"]
        }
    
    def _verify_evaluation(self, implementation: Dict[str, Any],
                         paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that implementation evaluation matches paper evaluation.
        
        Args:
            implementation: Implementation details
            paper: Paper details
            
        Returns:
            Dictionary containing verification results
        """
        # TODO: Implement evaluation verification
        return {
            "matches": [],
            "discrepancies": [],
            "score": 0.0,
            "notes": ["Evaluation verification not yet implemented"]
        }
    
    def _verify_results(self, implementation: Dict[str, Any],
                      paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that implementation results match paper results.
        
        Args:
            implementation: Implementation details
            paper: Paper details
            
        Returns:
            Dictionary containing verification results
        """
        # TODO: Implement results verification
        return {
            "matches": [],
            "discrepancies": [],
            "score": 0.0,
            "notes": ["Results verification not yet implemented"]
        }