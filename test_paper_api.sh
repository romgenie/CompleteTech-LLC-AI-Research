#!/bin/bash
# Test script for the Paper Processing Pipeline API

# Configuration
API_URL="http://localhost:8000"
MAX_ATTEMPTS=10
DELAY=5

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Paper Processing API Test ===${NC}"
echo "Testing API at $API_URL"

# Test health endpoint
echo -e "\n${YELLOW}Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Health endpoint responded:${NC} $HEALTH_RESPONSE"
else
    echo -e "${RED}Failed to connect to health endpoint${NC}"
    exit 1
fi

# Test routes endpoint (if available)
echo -e "\n${YELLOW}Testing routes endpoint...${NC}"
ROUTES_RESPONSE=$(curl -s "$API_URL/routes")
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Routes endpoint responded${NC}"
else
    echo -e "${YELLOW}Routes endpoint not available or unreachable${NC}"
fi

# Test papers endpoint
echo -e "\n${YELLOW}Testing paper status endpoint...${NC}"
RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
STATUS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/papers/$RANDOM_ID/status")

if [ "$STATUS_RESPONSE" == "404" ]; then
    echo -e "${GREEN}Paper status endpoint working correctly (returned 404 for invalid paper ID)${NC}"
else
    echo -e "${YELLOW}Paper status endpoint returned unexpected status: $STATUS_RESPONSE${NC}"
fi

# Test WebSocket connection
echo -e "\n${YELLOW}WebSocket endpoint should be available at:${NC}"
echo "ws://localhost:8000/ws"
echo "ws://localhost:8000/ws/{paper_id}"

echo -e "\n${GREEN}Basic API tests completed${NC}"
echo "To test paper processing, you would need to:"
echo "1. Upload a paper using POST to $API_URL/papers"
echo "2. Start processing using POST to $API_URL/papers/{paper_id}/process"
echo "3. Track status using GET to $API_URL/papers/{paper_id}/status"
echo "4. Connect to WebSocket for real-time updates"

echo -e "\n${YELLOW}For full testing, use the Python test script:${NC}"
echo "python test_api.py --paper-file path/to/paper.pdf --api-url $API_URL"