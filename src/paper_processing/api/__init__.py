"""
Paper Processing API Package.

This package contains the API endpoints for the Paper Processing Pipeline,
providing interfaces for paper processing, status updates, and manual control.
It includes both RESTful API routes and WebSocket endpoints for real-time updates.
"""

from .routes import router, ws_router

__all__ = ["router", "ws_router"]