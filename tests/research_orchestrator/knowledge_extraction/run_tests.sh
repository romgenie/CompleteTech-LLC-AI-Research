#!/bin/bash
# Script to run knowledge extraction tests with different options

# Get directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
VERBOSITY="-v"
MARKERS=""
REPORT=false

# Help text
show_help() {
    echo -e "${BLUE}Knowledge Extraction Test Runner${NC}"
    echo "Usage: ./run_tests.sh [options]"
    echo ""
    echo "Options:"
    echo "  -t, --test-type TYPE    Run specific test types: unit, integration, e2e, property, benchmark, edge, all (default: all)"
    echo "  -m, --markers MARKERS   Specify pytest markers (e.g. 'document or entity')"
    echo "  -r, --report            Generate an HTML report"
    echo "  -v, --verbose           Increase verbosity"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh                    # Run all tests"
    echo "  ./run_tests.sh -t unit            # Run only unit tests"
    echo "  ./run_tests.sh -m entity          # Run only entity-related tests"
    echo "  ./run_tests.sh -t edge -r         # Run edge case tests and generate a report"
    echo "  ./run_tests.sh -m \"fast and unit\" # Run fast unit tests"
}

# Parse command line options
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--test-type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -m|--markers)
            MARKERS="-m \"$2\""
            shift 2
            ;;
        -r|--report)
            REPORT=true
            shift
            ;;
        -v|--verbose)
            VERBOSITY="-vv"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate test type
if [[ ! "$TEST_TYPE" =~ ^(unit|integration|e2e|property|benchmark|edge|all)$ ]]; then
    echo -e "${RED}Error: Invalid test type. Choose from: unit, integration, e2e, property, benchmark, edge, all${NC}"
    exit 1
fi

# Define report options
REPORT_OPTS=""
if [ "$REPORT" = true ]; then
    echo -e "${BLUE}Generating HTML report...${NC}"
    REPORT_OPTS="--html=test-report.html --self-contained-html"
fi

# Function to run tests
run_tests() {
    local test_path=$1
    local test_name=$2
    
    echo -e "${YELLOW}Running $test_name tests...${NC}"
    
    # Construct the command
    cmd="python -m pytest $test_path $VERBOSITY $MARKERS $REPORT_OPTS"
    
    # Echo command for visibility
    echo -e "${BLUE}$cmd${NC}"
    
    # Run command
    eval $cmd
    
    # Check result
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}$test_name tests passed!${NC}"
        return 0
    else
        echo -e "${RED}$test_name tests failed!${NC}"
        return 1
    fi
}

# Track overall success
OVERALL_SUCCESS=0

# Run tests based on type
case $TEST_TYPE in
    unit)
        run_tests "unit/" "Unit"
        OVERALL_SUCCESS=$?
        ;;
    integration)
        run_tests "integration/" "Integration"
        OVERALL_SUCCESS=$?
        ;;
    e2e)
        run_tests "e2e/" "End-to-end"
        OVERALL_SUCCESS=$?
        ;;
    property)
        run_tests "property/" "Property-based"
        OVERALL_SUCCESS=$?
        ;;
    benchmark)
        run_tests "benchmark/" "Benchmark"
        OVERALL_SUCCESS=$?
        ;;
    edge)
        run_tests "edge_cases/" "Edge Case"
        OVERALL_SUCCESS=$?
        ;;
    all)
        # Run all test types
        run_tests "unit/" "Unit"
        UNIT_SUCCESS=$?
        
        run_tests "integration/" "Integration"
        INTEGRATION_SUCCESS=$?
        
        run_tests "e2e/" "End-to-end"
        E2E_SUCCESS=$?
        
        run_tests "property/" "Property-based"
        PROPERTY_SUCCESS=$?
        
        run_tests "benchmark/" "Benchmark"
        BENCHMARK_SUCCESS=$?
        
        run_tests "edge_cases/" "Edge Case"
        EDGE_SUCCESS=$?
        
        # Check if any test type failed
        if [ $UNIT_SUCCESS -ne 0 ] || [ $INTEGRATION_SUCCESS -ne 0 ] || [ $E2E_SUCCESS -ne 0 ] || 
           [ $PROPERTY_SUCCESS -ne 0 ] || [ $BENCHMARK_SUCCESS -ne 0 ] || [ $EDGE_SUCCESS -ne 0 ]; then
            OVERALL_SUCCESS=1
        fi
        ;;
esac

# Check if report was generated
if [ "$REPORT" = true ]; then
    if [ -f "test-report.html" ]; then
        echo -e "${GREEN}Report generated: $(realpath test-report.html)${NC}"
    else
        echo -e "${RED}Failed to generate report${NC}"
    fi
fi

# Exit with success/failure code
exit $OVERALL_SUCCESS