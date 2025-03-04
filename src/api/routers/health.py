"""
Health check router for the API.

This module provides endpoints for checking the health of the API
and its dependencies.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, Response

from src.api.dependencies.database import get_neo4j, get_mongo_client


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", summary="Health check")
async def health_check(
    response: Response,
    neo4j = Depends(get_neo4j),
    mongo = Depends(get_mongo_client)
) -> Dict[str, Any]:
    """
    Check the health of the API and its dependencies.
    
    Returns:
        Dict[str, Any]: Health status of the API and its dependencies
    """
    health_status = {
        "status": "ok",
        "dependencies": {
            "neo4j": "ok",
            "mongodb": "ok",
        }
    }
    
    # Check Neo4j connection
    try:
        neo4j.get_database_info()
    except Exception as e:
        logger.error(f"Neo4j health check failed: {str(e)}")
        health_status["dependencies"]["neo4j"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        response.status_code = 503
    
    # Check MongoDB connection
    try:
        mongo.server_info()
    except Exception as e:
        logger.error(f"MongoDB health check failed: {str(e)}")
        health_status["dependencies"]["mongodb"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        response.status_code = 503
    
    return health_status


@router.get("/ping", summary="Simple ping endpoint")
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint to check if the API is running.
    
    Returns:
        Dict[str, str]: Ping response
    """
    return {"message": "pong"}