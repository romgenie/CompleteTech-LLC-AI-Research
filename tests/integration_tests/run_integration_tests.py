#!/usr/bin/env python3
"""
Integration Test Runner for the AI Research Integration Project.

This script runs all integration tests that validate the interactions between
the major systems of the project:
1. Research Orchestration Framework
2. Dynamic Knowledge Graph System
3. AI Research Implementation System

Usage:
    python run_integration_tests.py [options]

Options:
    --verbose     Show detailed test output
    --coverage    Generate test coverage report
    --backend     Run only backend integration tests
    --frontend    Run only frontend integration tests
"""

import os
import sys
import unittest
import argparse
import subprocess
from pathlib import Path
import coverage

def get_backend_test_suite():
    """Return a TestSuite with all backend integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add research_to_implementation_flow tests
    from tests.integration_tests.test_research_to_implementation_flow import TestResearchToImplementationFlow
    suite.addTest(loader.loadTestsFromTestCase(TestResearchToImplementationFlow))
    
    # Add api_database_interaction tests
    from tests.integration_tests.test_api_database_interaction import TestApiDatabaseInteraction
    suite.addTest(loader.loadTestsFromTestCase(TestApiDatabaseInteraction))
    
    return suite

def run_backend_tests(verbose=False, with_coverage=False):
    """Run backend integration tests."""
    print("Running backend integration tests...")
    
    if with_coverage:
        cov = coverage.Coverage(
            source=['research_orchestrator', 'knowledge_graph_system', 'research_implementation', 'src/ui/api'],
            omit=['*/__pycache__/*', '*/tests/*', '*/test_*.py']
        )
        cov.start()
    
    suite = get_backend_test_suite()
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = test_runner.run(suite)
    
    if with_coverage:
        cov.stop()
        cov.save()
        print("\nCoverage report:")
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print("HTML coverage report generated in 'htmlcov' directory")
    
    return result.wasSuccessful()

def run_frontend_tests(verbose=False, with_coverage=False):
    """Run frontend integration tests using Jest."""
    print("Running frontend integration tests...")
    
    # Navigate to frontend directory
    frontend_dir = Path(__file__).parents[3] / 'src' / 'ui' / 'frontend'
    
    # Build Jest command
    cmd = ['npm', 'test', '--', 'tests/integration_tests/test_frontend_api_integration.py']
    
    if verbose:
        cmd.append('--verbose')
    
    if with_coverage:
        cmd.append('--coverage')
    
    # Run tests
    try:
        completed_process = subprocess.run(
            cmd,
            cwd=frontend_dir,
            check=True,
            capture_output=not verbose
        )
        return completed_process.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Frontend tests failed with error code {e.returncode}")
        if not verbose and e.output:
            print(e.output.decode())
        return False
    except Exception as e:
        print(f"Error running frontend tests: {e}")
        return False

def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run integration tests for the AI Research Integration Project")
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed test output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Generate test coverage report')
    parser.add_argument('--backend', '-b', action='store_true', help='Run only backend integration tests')
    parser.add_argument('--frontend', '-f', action='store_true', help='Run only frontend integration tests')
    
    args = parser.parse_args()
    
    # If no specific test type is specified, run all
    run_all = not (args.backend or args.frontend)
    
    results = []
    
    # Run backend tests if specified or running all
    if args.backend or run_all:
        backend_success = run_backend_tests(
            verbose=args.verbose,
            with_coverage=args.coverage
        )
        results.append(('Backend', backend_success))
    
    # Run frontend tests if specified or running all
    if args.frontend or run_all:
        frontend_success = run_frontend_tests(
            verbose=args.verbose,
            with_coverage=args.coverage
        )
        results.append(('Frontend', frontend_success))
    
    # Print summary
    print("\n=== Integration Test Results ===")
    all_passed = True
    for test_type, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test_type} tests: {status}")
        all_passed = all_passed and success
    
    # Return appropriate exit code
    return 0 if all_passed else 1

if __name__ == "__main__":
    # Change to the integration_tests directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())