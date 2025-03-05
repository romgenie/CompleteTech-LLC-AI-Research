"""
WebSocket connection management for the Paper Processing Pipeline.

This module handles WebSocket connections for real-time paper processing updates.
It provides connection managers and event handling for the Paper Processing Pipeline.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Set
import asyncio
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect

# Configure logging
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Connection manager for WebSocket connections.
    
    Manages active WebSocket connections and handles broadcasting messages.
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        # Active connections for general broadcasts
        self.active_connections: List[WebSocket] = []
        
        # Connections by paper ID for targeted updates
        self.paper_connections: Dict[str, Set[WebSocket]] = {}
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, paper_id: Optional[str] = None):
        """
        Connect a WebSocket client.
        
        Args:
            websocket: The WebSocket connection
            paper_id: Optional paper ID to subscribe to specific updates
        """
        # Accept the connection
        await websocket.accept()
        
        async with self._lock:
            # Add to general connections
            if websocket not in self.active_connections:
                self.active_connections.append(websocket)
            
            # Add to paper-specific connections if provided
            if paper_id:
                if paper_id not in self.paper_connections:
                    self.paper_connections[paper_id] = set()
                self.paper_connections[paper_id].add(websocket)
        
        logger.info(f"Client connected. Active connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """
        Disconnect a WebSocket client.
        
        Args:
            websocket: The WebSocket connection to disconnect
        """
        async with self._lock:
            # Remove from general connections
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # Remove from paper-specific connections
            for paper_id, connections in list(self.paper_connections.items()):
                if websocket in connections:
                    connections.remove(websocket)
                    # Clean up empty sets
                    if not connections:
                        del self.paper_connections[paper_id]
        
        logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")
    
    async def subscribe_to_paper(self, websocket: WebSocket, paper_id: str):
        """
        Subscribe a WebSocket client to updates for a specific paper.
        
        Args:
            websocket: The WebSocket connection
            paper_id: Paper ID to subscribe to
        """
        async with self._lock:
            if paper_id not in self.paper_connections:
                self.paper_connections[paper_id] = set()
            self.paper_connections[paper_id].add(websocket)
        
        logger.info(f"Client subscribed to paper {paper_id}")
    
    async def unsubscribe_from_paper(self, websocket: WebSocket, paper_id: str):
        """
        Unsubscribe a WebSocket client from updates for a specific paper.
        
        Args:
            websocket: The WebSocket connection
            paper_id: Paper ID to unsubscribe from
        """
        async with self._lock:
            if paper_id in self.paper_connections and websocket in self.paper_connections[paper_id]:
                self.paper_connections[paper_id].remove(websocket)
                # Clean up empty sets
                if not self.paper_connections[paper_id]:
                    del self.paper_connections[paper_id]
        
        logger.info(f"Client unsubscribed from paper {paper_id}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast
        """
        if not self.active_connections:
            return
            
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
            
        # Convert to JSON
        message_json = json.dumps(message)
        
        # Send to all active connections
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def broadcast_to_paper(self, paper_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to clients subscribed to a specific paper.
        
        Args:
            paper_id: The paper ID
            message: The message to broadcast
        """
        if paper_id not in self.paper_connections or not self.paper_connections[paper_id]:
            return
            
        # Add paper_id and timestamp if not present
        if "paper_id" not in message:
            message["paper_id"] = paper_id
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
            
        # Convert to JSON
        message_json = json.dumps(message)
        
        # Send to subscribed connections
        disconnected = []
        for connection in self.paper_connections.get(paper_id, set()):
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket client.
        
        Args:
            websocket: The WebSocket connection to send the message to
            message: The message to send
        """
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
            
        # Convert to JSON
        message_json = json.dumps(message)
        
        # Send to the specific client
        try:
            await websocket.send_text(message_json)
        except Exception as e:
            logger.error(f"Error sending personal message to client: {e}")
            # Disconnect client if an error occurs
            await self.disconnect(websocket)


# Global connection manager instance
connection_manager = ConnectionManager()