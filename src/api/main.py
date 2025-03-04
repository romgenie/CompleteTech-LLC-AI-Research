"""
AI Research Integration Project - Main API

This module initializes the FastAPI application and configures routers,
middleware, and dependencies for the AI Research Integration Project.
"""

import logging
import os
from typing import Dict, List

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.database import get_db, get_neo4j, get_mongo_client
from src.api.middlewares.logging import LoggingMiddleware
from src.api.middlewares.error_handler import ErrorHandlerMiddleware
from src.api.routers import (
    knowledge_graph,
    research_orchestration,
    research_implementation,
    auth,
    health,
)

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
    docs_url=None,  # We'll serve custom docs
    redoc_url=None,  # We'll serve custom redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=eval(os.environ.get("CORS_ORIGINS", '["*"]')),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(
    knowledge_graph.router,
    prefix="/api/knowledge-graph",
    tags=["knowledge-graph"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    research_orchestration.router,
    prefix="/api/research-orchestration",
    tags=["research-orchestration"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    research_implementation.router,
    prefix="/api/research-implementation",
    tags=["research-implementation"],
    dependencies=[Depends(get_current_user)],
)

# Mount static files if available
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    logger.warning("Static files directory not found, skipping...")


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Apply security to all operations
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            # Skip health endpoint and auth endpoints
            if "/health" in path or "/auth" in path:
                continue
            
            if openapi_schema["paths"][path][method].get("security") is None:
                openapi_schema["paths"][path][method]["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Documentation",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="API Documentation",
        redoc_js_url="/static/redoc.standalone.js",
    )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "AI Research Integration API",
        "version": app.version,
        "documentation": "/docs",
        "redoc": "/redoc",
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