#!/usr/bin/env python3
"""
Test script for the AI Research Integration API.

This script starts a FastAPI test client and makes a request to the API.
"""

import sys
import os
import asyncio
from fastapi.testclient import TestClient
import uvicorn
import threading
import time

# Make sure the code directory is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the app
from src.api.main import app

# Create a test client
client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_endpoint():
    """Test the health endpoint."""
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
def test_docs_endpoint():
    """Test the docs endpoint."""
    response = client.get("/docs")
    print(f"Status Code: {response.status_code}")
    print(f"Response Length: {len(response.text)} characters")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()

def main():
    """Run the tests."""
    print("Testing API endpoints...")
    print("\n=== Root Endpoint ===")
    test_root_endpoint()
    print("\n=== Health Endpoint ===")
    test_health_endpoint()
    print("\n=== Docs Endpoint ===")
    test_docs_endpoint()
    print("\nAll tests passed!")

if __name__ == "__main__":
    main()