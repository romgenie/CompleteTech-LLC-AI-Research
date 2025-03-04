"""
Database dependency providers for the API.

This module provides dependency injection functions for database connections,
including Neo4j for the knowledge graph and MongoDB for document storage.
"""

import os
import json
from typing import Generator, Dict, Any

from fastapi import Depends
from pymongo import MongoClient
from pymongo.database import Database

from knowledge_graph_system.core.db.neo4j_manager import Neo4jManager
from knowledge_graph_system.core.knowledge_graph_manager import KnowledgeGraphManager


def get_neo4j() -> Generator[Neo4jManager, None, None]:
    """
    Get a Neo4j database manager instance.
    
    Returns:
        Generator[Neo4jManager, None, None]: Neo4j database manager
    """
    config_path = os.environ.get(
        "NEO4J_CONFIG_PATH", 
        "/Users/completetech/open-computer-use/claude_workspace/knowledge_graph_system/config/db_config.json"
    )
    
    try:
        manager = Neo4jManager.from_config(config_path)
        yield manager
    finally:
        if manager:
            manager.close()


def get_knowledge_graph_manager(neo4j: Neo4jManager = Depends(get_neo4j)) -> KnowledgeGraphManager:
    """
    Get a Knowledge Graph manager instance.
    
    Args:
        neo4j (Neo4jManager): Neo4j database manager
        
    Returns:
        KnowledgeGraphManager: The knowledge graph manager
    """
    manager = KnowledgeGraphManager(neo4j)
    return manager


def get_mongo_client() -> Generator[MongoClient, None, None]:
    """
    Get a MongoDB client.
    
    Returns:
        Generator[MongoClient, None, None]: MongoDB client
    """
    mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    
    try:
        yield client
    finally:
        client.close()


def get_db(mongo_client: MongoClient = Depends(get_mongo_client)) -> Database:
    """
    Get a MongoDB database.
    
    Args:
        mongo_client (MongoClient): MongoDB client
        
    Returns:
        Database: MongoDB database
    """
    db_name = os.environ.get("MONGODB_DB", "ai_research")
    return mongo_client[db_name]