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

# Mock implementation for testing
class Neo4jManager:
    @staticmethod
    def from_config(config_path):
        return Neo4jManager()
    
    def close(self):
        pass
    
    def get_database_info(self):
        return {"name": "test", "version": "1.0"}
    
    def execute_read_query(self, query, params=None):
        return []

class KnowledgeGraphManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def add_entity(self, entity):
        return {"success": True, "entity_id": entity.id}
    
    def get_entity_by_id(self, entity_id):
        return None
    
    def get_entities_by_label(self, label, limit=10, offset=0):
        return []
    
    def get_all_entities(self, limit=10, offset=0):
        return []
    
    def count_entities(self):
        return 0
    
    def count_entities_by_label(self, label):
        return 0
    
    def update_entity(self, entity_id, properties):
        return {"success": True}
    
    def delete_entity(self, entity_id):
        return {"success": True}
    
    def add_relationship(self, relationship):
        return {"success": True, "relationship_id": relationship.id}
    
    def get_relationships_by_type(self, rel_type, limit=10, offset=0):
        return []
    
    def get_relationships_for_entity(self, entity_id, direction="both", limit=10, offset=0):
        return []
    
    def get_all_relationships(self, limit=10, offset=0):
        return []
    
    def count_relationships(self):
        return 0
    
    def count_relationships_by_type(self, rel_type):
        return 0
    
    def compute_graph_statistics(self):
        return {"entities": 0, "relationships": 0, "labels": [], "types": []}


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