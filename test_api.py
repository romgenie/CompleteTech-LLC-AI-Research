#!/usr/bin/env python3
"""
Test script for the Paper Processing Pipeline API.

This script tests the paper processing pipeline by uploading a test paper
and tracking its processing through the various stages.
"""

import argparse
import json
import time
import requests
import os
from datetime import datetime
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("paper_api_test")

# Default API URL
DEFAULT_API_URL = "http://localhost:8000"

def upload_paper(api_url, paper_file):
    """
    Upload a paper to the API.
    
    Args:
        api_url: Base URL of the API
        paper_file: Path to the paper file
        
    Returns:
        Paper ID if successful, None otherwise
    """
    if not os.path.exists(paper_file):
        logger.error(f"Paper file not found: {paper_file}")
        return None
        
    try:
        # Extract filename and title from path
        filename = os.path.basename(paper_file)
        title = os.path.splitext(filename)[0].replace("_", " ").title()
        
        # Prepare the form data
        files = {
            'file': (filename, open(paper_file, 'rb'), 'application/pdf')
        }
        data = {
            'title': title,
            'authors': json.dumps([{"name": "Test Author"}]),
            'year': 2023,
            'metadata': json.dumps({
                "source": "test_script",
                "uploaded_at": datetime.now().isoformat()
            })
        }
        
        # Make the upload request
        logger.info(f"Uploading paper '{title}' from {paper_file}")
        response = requests.post(
            f"{api_url}/papers",
            files=files,
            data=data
        )
        
        # Check the response
        if response.status_code == 201:
            paper = response.json()
            logger.info(f"Paper uploaded successfully: {paper['paper_id']}")
            return paper['paper_id']
        else:
            logger.error(f"Failed to upload paper: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error uploading paper: {e}")
        return None

def start_processing(api_url, paper_id):
    """
    Start processing the paper.
    
    Args:
        api_url: Base URL of the API
        paper_id: ID of the paper to process
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Make the process request
        logger.info(f"Starting processing for paper {paper_id}")
        response = requests.post(
            f"{api_url}/papers/{paper_id}/process"
        )
        
        # Check the response
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Processing started: {result['message']}")
            return True
        else:
            logger.error(f"Failed to start processing: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error starting processing: {e}")
        return False

def poll_status(api_url, paper_id, max_polls=60, interval=5):
    """
    Poll the paper status until complete or max_polls is reached.
    
    Args:
        api_url: Base URL of the API
        paper_id: ID of the paper to track
        max_polls: Maximum number of status polls
        interval: Interval between polls in seconds
        
    Returns:
        Final paper status
    """
    logger.info(f"Polling status for paper {paper_id}")
    polls = 0
    terminal_states = [
        "ANALYZED", "IMPLEMENTATION_READY", "FAILED"
    ]
    
    while polls < max_polls:
        try:
            # Get the paper status
            response = requests.get(
                f"{api_url}/papers/{paper_id}/status"
            )
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status", "unknown")
                progress = status_data.get("progress", 0)
                
                logger.info(f"Status poll {polls+1}/{max_polls}: {status} ({progress}%)")
                
                # Show entity and relationship counts
                entity_count = status_data.get("entity_count", 0)
                relationship_count = status_data.get("relationship_count", 0)
                logger.info(f"Entities: {entity_count}, Relationships: {relationship_count}")
                
                if status.upper() in terminal_states:
                    logger.info(f"Processing complete with status: {status}")
                    return status_data
                    
            else:
                logger.error(f"Failed to get status: {response.status_code} - {response.text}")
            
            # Wait for the next poll
            time.sleep(interval)
            polls += 1
            
        except Exception as e:
            logger.error(f"Error polling status: {e}")
            time.sleep(interval)
            polls += 1
    
    logger.warning(f"Max polls ({max_polls}) reached without completion")
    return None

def test_paper_processing_api(api_url=DEFAULT_API_URL):
    """
    Test the basic API endpoints.
    
    Args:
        api_url: Base URL of the API
    """
    logger.info("Testing basic API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            logger.info(f"Health check passed: {response.json()}")
        else:
            logger.error(f"Health check failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error testing health endpoint: {e}")
    
    # Test routes endpoint
    try:
        response = requests.get(f"{api_url}/routes")
        if response.status_code == 200:
            routes = response.json()
            logger.info(f"Found {routes['count']} routes")
        else:
            logger.error(f"Routes check failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error testing routes endpoint: {e}")

def main():
    """Main entry point for the test script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Paper Processing Pipeline API")
    parser.add_argument("--paper-file", help="Path to the paper file to upload")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Base URL of the API")
    parser.add_argument("--max-polls", type=int, default=60, help="Maximum number of status polls")
    parser.add_argument("--interval", type=int, default=5, help="Interval between polls in seconds")
    parser.add_argument("--basic-test", action="store_true", help="Run basic API tests only")
    args = parser.parse_args()
    
    # Run basic API tests
    test_paper_processing_api(args.api_url)
    
    # If no paper file provided or basic-test flag is set, exit
    if args.basic_test or not args.paper_file:
        logger.info("Basic API tests completed")
        return 0
    
    # Upload the paper
    paper_id = upload_paper(args.api_url, args.paper_file)
    if not paper_id:
        logger.error("Failed to upload paper, aborting test")
        return 1
    
    # Start processing
    if not start_processing(args.api_url, paper_id):
        logger.error("Failed to start processing, aborting test")
        return 1
    
    # Use polling for status updates
    final_status = poll_status(args.api_url, paper_id, args.max_polls, args.interval)
    
    if final_status:
        logger.info(f"Final status: {final_status['status']}")
        if final_status['status'].upper() == "FAILED":
            logger.error("Paper processing failed")
            return 1
        else:
            logger.info("Test successful")
            return 0
    else:
        logger.warning("Test incomplete: processing did not finish within timeout")
        return 2

if __name__ == "__main__":
    sys.exit(main())