"""
Database connection management for the Paper Processing Pipeline.

This module handles MongoDB connection setup and management for the Paper
Processing Pipeline. It provides a connection pool for efficient database
access and configuration options for different environments.

Current Implementation Status:
- Connection management structure defined ✓
- Configuration options defined ✓
- Connection pooling defined ✓

Upcoming Development:
- Robust connection retry mechanisms
- Advanced connection pool management
- Read preference configuration
- Replica set support
"""

import os
import logging
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ConfigurationError

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    MongoDB connection manager.
    
    This class manages MongoDB connections for the Paper Processing Pipeline,
    providing a connection pool and configuration options.
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        self.client = None
        self.db = None
        self.collections = {}
        self.is_connected = False
    
    async def connect(
        self,
        connection_string: Optional[str] = None,
        db_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Connect to MongoDB.
        
        Args:
            connection_string: MongoDB connection string
            db_name: Database name
            **kwargs: Additional connection options
            
        Raises:
            ConnectionFailure: If connection fails
            ConfigurationError: If connection parameters are invalid
        """
        try:
            # Get connection parameters from environment or arguments
            conn_str = connection_string or os.environ.get(
                'MONGODB_URI',
                'mongodb://localhost:27017'
            )
            
            database = db_name or os.environ.get(
                'MONGODB_DB',
                'paper_processing'
            )
            
            # Create the client
            self.client = AsyncIOMotorClient(
                conn_str,
                maxPoolSize=kwargs.get('max_pool_size', 10),
                minPoolSize=kwargs.get('min_pool_size', 1),
                maxIdleTimeMS=kwargs.get('max_idle_time_ms', 30000),
                connectTimeoutMS=kwargs.get('connect_timeout_ms', 5000),
                socketTimeoutMS=kwargs.get('socket_timeout_ms', 30000),
                serverSelectionTimeoutMS=kwargs.get('server_selection_timeout_ms', 5000),
                waitQueueTimeoutMS=kwargs.get('wait_queue_timeout_ms', 10000)
            )
            
            # Get the database
            self.db = self.client[database]
            
            # Initialize collections
            self.collections = {
                'papers': self.db.papers,
                'batches': self.db.batches,
                'tasks': self.db.tasks,
                'statistics': self.db.statistics
            }
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.is_connected = True
            logger.info(f"Connected to MongoDB database {database}")
        except (ConnectionFailure, ConfigurationError) as e:
            self.is_connected = False
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Disconnect from MongoDB.
        
        This method cleanly closes the connection to MongoDB.
        """
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.collections = {}
            self.is_connected = False
            logger.info("Disconnected from MongoDB")
    
    async def get_collection(self, collection_name: str):
        """
        Get a MongoDB collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            The collection
            
        Raises:
            ValueError: If not connected or collection not found
        """
        if not self.is_connected:
            raise ValueError("Not connected to MongoDB")
        
        if collection_name not in self.collections:
            raise ValueError(f"Collection {collection_name} not found")
        
        return self.collections[collection_name]
    
    async def create_indexes(self) -> None:
        """
        Create indexes for collections.
        
        This method creates the necessary indexes for efficient queries.
        
        Raises:
            ConnectionFailure: If not connected
        """
        if not self.is_connected:
            raise ConnectionFailure("Not connected to MongoDB")
        
        # Papers collection indexes
        await self.collections['papers'].create_index([('id', 1)], unique=True)
        await self.collections['papers'].create_index([('status', 1)])
        await self.collections['papers'].create_index([('uploaded_at', -1)])
        await self.collections['papers'].create_index([('title', 'text'), ('abstract', 'text')])
        
        # Batches collection indexes
        await self.collections['batches'].create_index([('id', 1)], unique=True)
        await self.collections['batches'].create_index([('status', 1)])
        await self.collections['batches'].create_index([('created_at', -1)])
        
        # Tasks collection indexes
        await self.collections['tasks'].create_index([('task_id', 1)], unique=True)
        await self.collections['tasks'].create_index([('paper_id', 1)])
        await self.collections['tasks'].create_index([('status', 1)])
        await self.collections['tasks'].create_index([('created_at', -1)])
        
        logger.info("Created MongoDB indexes")


# Global database connection instance
# This will be initialized by the application at startup
db_connection = DatabaseConnection()