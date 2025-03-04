"""
AI Research Integration Project - Main API

This module initializes the FastAPI application and configures routers,
middleware, and dependencies for the AI Research Integration Project.
"""

import logging
import os
import datetime
from typing import Dict, List

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(
    level=os.environ.get("API_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="AI Research Integration API",
    description="API for AI Research Integration Project",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from src.api.routers import (
    auth,
    health,
    knowledge_graph,
    research_orchestration,
    research_implementation,
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(knowledge_graph.router, prefix="/knowledge", tags=["Knowledge Graph"])
app.include_router(research_orchestration.router, prefix="/research", tags=["Research"])
app.include_router(research_implementation.router, prefix="/implementation", tags=["Implementation"])

# Create a simple test endpoint
@app.get("/")
async def root():
    """Root endpoint for testing."""
    return {
        "message": "AI Research Integration API is running",
        "version": app.version,
        "documentation": "/docs",
        "redoc": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": str(datetime.datetime.now()),
        "service": "AI Research Integration API"
    }


# Main entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.environ.get("ENVIRONMENT", "development") == "development",
        workers=int(os.environ.get("API_WORKERS", 1)),
    )