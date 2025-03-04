"""
Error handler middleware for the API.

This middleware catches exceptions and converts them to appropriate HTTP responses.
"""

import logging
import traceback
from typing import Callable, Dict, Any, Union

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from neo4j.exceptions import Neo4jError, ServiceUnavailable
from pymongo.errors import PyMongoError


logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions and converting them to HTTP responses."""
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process the request and handle any exceptions.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            Response: The response or an error response if an exception occurs
        """
        try:
            return await call_next(request)
        except Exception as e:
            return self._handle_exception(e, request)
            
    def _handle_exception(self, exc: Exception, request: Request) -> JSONResponse:
        """
        Handle an exception and return an appropriate HTTP response.
        
        Args:
            exc: The exception that occurred
            request: The incoming request
            
        Returns:
            JSONResponse: An error response with details about the exception
        """
        # Common error response format
        error_response: Dict[str, Any] = {
            "error": True,
            "message": str(exc),
            "path": request.url.path,
            "method": request.method,
        }
        
        # Log the exception
        logger.error(
            f"Error handling request: {request.method} {request.url.path}\n"
            f"Exception: {exc.__class__.__name__}: {str(exc)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # Handle specific exception types
        if isinstance(exc, Neo4jError):
            # Neo4j database errors
            error_response["type"] = "database_error"
            error_response["code"] = getattr(exc, "code", "unknown")
            status_code = 500
            
        elif isinstance(exc, ServiceUnavailable):
            # Neo4j connection errors
            error_response["type"] = "service_unavailable"
            status_code = 503
            
        elif isinstance(exc, PyMongoError):
            # MongoDB errors
            error_response["type"] = "database_error"
            error_response["code"] = exc.__class__.__name__
            status_code = 500
            
        elif hasattr(exc, "status_code"):
            # FastAPI HTTPException or similar with status_code attribute
            status_code = getattr(exc, "status_code", 500)
            error_response["type"] = "api_error"
            
            # Include additional details if available
            if hasattr(exc, "detail"):
                error_response["detail"] = getattr(exc, "detail")
            
        else:
            # Generic server error for unhandled exceptions
            status_code = 500
            error_response["type"] = "server_error"
        
        # Include traceback in development mode
        if "dev" in request.headers.get("x-environment", "").lower():
            error_response["traceback"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )