"""
FastAPI application for Paper Processing Pipeline.

This module defines the FastAPI application for the Paper Processing Pipeline,
integrating the routes and configuration.
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI, APIRouter, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..config.settings import settings, configure_logging
from . import routes

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    description="API for processing and analyzing research papers",
    version=settings.version,
    debug=settings.api.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log API requests.
    
    Args:
        request: The incoming request
        call_next: The next middleware function
        
    Returns:
        The response from the next middleware
    """
    path = request.url.path
    method = request.method
    client = request.client.host if request.client else "unknown"
    
    logger.info(f"{method} {path} from {client}")
    
    try:
        response = await call_next(request)
        logger.info(f"{method} {path} returned {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing {method} {path}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )

# Add error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    
    Args:
        request: The incoming request
        exc: The exception
        
    Returns:
        JSON response with error information
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )

# Include paper processing routes
app.include_router(routes.router)

# Include WebSocket routes
app.include_router(routes.ws_router)

# Health check endpoint at the API root
@app.get("/", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns basic information about the API status.
    
    Returns:
        Dict containing API information
    """
    return {
        "name": settings.project_name,
        "version": settings.version,
        "environment": settings.environment,
        "status": "up"
    }

# Get list of available routes for debugging
@app.get("/routes", tags=["Debug"])
async def list_routes() -> Dict[str, Any]:
    """
    List available routes.
    
    Returns a list of available routes for debugging purposes.
    This endpoint is only available in development mode.
    
    Returns:
        Dict containing route information
    """
    if settings.environment != "development":
        return JSONResponse(
            status_code=403,
            content={
                "status": "error",
                "message": "This endpoint is only available in development mode"
            }
        )
    
    routes_list = []
    for route in app.routes:
        route_info = {
            "path": getattr(route, "path", None),
            "name": getattr(route, "name", None),
            "methods": getattr(route, "methods", None),
        }
        routes_list.append(route_info)
    
    return {
        "count": len(routes_list),
        "routes": routes_list
    }