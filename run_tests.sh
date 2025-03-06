#!/bin/bash

# Define colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Print usage
function usage {
    echo -e "${YELLOW}Usage: $0 [OPTIONS]${NC}"
    echo ""
    echo "Options:"
    echo "  -h, --help             Show this help message and exit"
    echo "  -v, --verbose          Run tests with verbose output"
    echo "  -c, --coverage         Run tests with coverage report"
    echo "  -s, --skip-slow        Skip slow tests"
    echo "  -k EXPRESSION          Only run tests matching expression"
    echo "  -m MARKERS             Only run tests with these markers"
    echo "  -p PATH                Path to tests to run (default: tests/)"
    echo "  -f FILE                Run specific test file"
    echo ""
    echo "Examples:"
    echo "  $0 -v                  Run all tests with verbose output"
    echo "  $0 -c -s               Run tests with coverage, skipping slow tests"
    echo "  $0 -k 'entity'         Run tests containing 'entity' in their name"
    echo "  $0 -m 'unit'           Run tests marked as 'unit' tests"
    echo "  $0 -f tests/test_file.py  Run tests in specific file"
    echo "  $0 -p tests/integration_tests/websocket/  Run WebSocket integration tests"
    echo "  $0 -p tests/integration_tests/celery/     Run Celery task tests"
    echo ""
}

# Default values
VERBOSE=0
COVERAGE=0
SKIP_SLOW=0
EXPRESSION=""
MARKERS=""
TEST_PATH="tests/"
TEST_FILE=""

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=1
            ;;
        -c|--coverage)
            COVERAGE=1
            ;;
        -s|--skip-slow)
            SKIP_SLOW=1
            ;;
        -k)
            shift
            EXPRESSION="$1"
            ;;
        -m)
            shift
            MARKERS="$1"
            ;;
        -p)
            shift
            TEST_PATH="$1"
            ;;
        -f)
            shift
            TEST_FILE="$1"
            ;;
        *)
            echo -e "${RED}Unknown parameter: $1${NC}"
            usage
            exit 1
            ;;
    esac
    shift
done

# Build the command
CMD="python -m pytest"

# Add options based on provided arguments
if [ $VERBOSE -eq 1 ]; then
    CMD="$CMD -v"
fi

if [ $COVERAGE -eq 1 ]; then
    CMD="$CMD --cov=src --cov-report=term"
fi

if [ $SKIP_SLOW -eq 1 ]; then
    CMD="$CMD -m 'not slow'"
elif [ ! -z "$MARKERS" ]; then
    CMD="$CMD -m '$MARKERS'"
fi

if [ ! -z "$EXPRESSION" ]; then
    CMD="$CMD -k '$EXPRESSION'"
fi

# Add the test path/file
if [ ! -z "$TEST_FILE" ]; then
    CMD="$CMD $TEST_FILE"
else
    CMD="$CMD $TEST_PATH"
fi

# Run the command
echo -e "${GREEN}Running: $CMD${NC}"
eval $CMD

# Check the exit status
EXIT_STATUS=$?
if [ $EXIT_STATUS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Tests failed with exit status $EXIT_STATUS${NC}"
fi

exit $EXIT_STATUS