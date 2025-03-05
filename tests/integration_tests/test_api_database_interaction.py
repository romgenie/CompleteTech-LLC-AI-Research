"""
Integration test for the interaction between API endpoints and databases.

This test validates that API endpoints correctly interact with:
1. Neo4j database for knowledge graph operations
2. MongoDB for document storage

The test uses TestClient from FastAPI to simulate API requests and verifies
that data is correctly stored and retrieved from the databases.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

class TestApiDatabaseInteraction(unittest.TestCase):
    """Test interaction between API endpoints and databases."""

    def setUp(self):
        """Set up test environment with mocked databases."""
        # Patch Neo4j and MongoDB connections
        self.neo4j_patcher = patch('knowledge_graph_system.core.db.neo4j_manager.Neo4jManager')
        self.mongodb_patcher = patch('src.api.dependencies.database.MongoClient')
        
        # Start patchers
        self.mock_neo4j = self.neo4j_patcher.start()
        self.mock_mongodb = self.mongodb_patcher.start()
        
        # Configure Neo4j mock
        self.mock_neo4j_instance = self.mock_neo4j.return_value
        
        # Configure graph entities query mock to return test entities
        entity_query_result = MagicMock()
        entity_query_result.data.return_value = [
            {"entity": {"id": "1", "name": "Vision Transformer", "type": "MODEL"}},
            {"entity": {"id": "2", "name": "GPT-4", "type": "MODEL"}},
            {"entity": {"id": "3", "name": "ImageNet", "type": "DATASET"}}
        ]
        
        # Configure relationship query mock to return test relationships
        relationship_query_result = MagicMock()
        relationship_query_result.data.return_value = [
            {
                "source": {"id": "1", "name": "Vision Transformer"}, 
                "target": {"id": "3", "name": "ImageNet"},
                "relationship": {"type": "EVALUATED_ON", "properties": {"accuracy": 0.885}}
            }
        ]
        
        # Set up different query results based on query patterns
        def mock_run_query(query, **params):
            if "MATCH (entity:" in query:
                return entity_query_result
            elif "MATCH (source)-[r]->(target)" in query:
                return relationship_query_result
            return MagicMock()
            
        self.mock_neo4j_instance.run_query.side_effect = mock_run_query
        
        # Configure MongoDB mock
        self.mock_mongodb_instance = self.mock_mongodb.return_value
        
        # Mock MongoDB collection operations
        self.mock_collection = MagicMock()
        self.mock_mongodb_instance.get_collection.return_value = self.mock_collection
        
        # Mock find_one to return test documents
        def mock_find_one(query):
            if query.get("_id") == "research_1":
                return {"_id": "research_1", "title": "Vision Transformer Research", "content": "Research content..."}
            elif query.get("_id") == "implementation_1":
                return {"_id": "implementation_1", "title": "ViT Implementation", "code": "import torch..."}
            return None
            
        self.mock_collection.find_one.side_effect = mock_find_one
        
        # Mock find to return multiple documents
        self.mock_cursor = MagicMock()
        self.mock_cursor.limit.return_value = self.mock_cursor
        self.mock_cursor.skip.return_value = self.mock_cursor
        self.mock_cursor.sort.return_value = self.mock_cursor
        
        def mock_to_list():
            return [
                {"_id": "research_1", "title": "Vision Transformer Research"},
                {"_id": "research_2", "title": "Diffusion Models Overview"}
            ]
            
        self.mock_cursor.to_list.return_value = mock_to_list()
        self.mock_collection.find.return_value = self.mock_cursor
        
        # Mock insert_one to return created ID
        insert_result = MagicMock()
        insert_result.inserted_id = "new_id_123"
        self.mock_collection.insert_one.return_value = insert_result
        
        # Import and initialize FastAPI app (after patching)
        from src.ui.api.app import app
        
        # Create test client
        self.client = TestClient(app)
        
    def tearDown(self):
        """Clean up test environment."""
        self.neo4j_patcher.stop()
        self.mongodb_patcher.stop()
    
    def test_knowledge_graph_entity_endpoints(self):
        """Test knowledge graph entity API endpoints."""
        # Test GET /api/knowledge-graph/entities
        response = self.client.get("/api/knowledge-graph/entities")
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains expected entities
        entities = response.json()
        self.assertEqual(len(entities), 3)
        self.assertEqual(entities[0]["name"], "Vision Transformer")
        
        # Test GET /api/knowledge-graph/entities/{entity_id}
        response = self.client.get("/api/knowledge-graph/entities/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Vision Transformer")
        
        # Test POST /api/knowledge-graph/entities
        new_entity = {
            "name": "BERT",
            "type": "MODEL",
            "properties": {
                "year": 2018,
                "authors": ["Jacob Devlin", "Ming-Wei Chang"]
            }
        }
        response = self.client.post("/api/knowledge-graph/entities", json=new_entity)
        self.assertEqual(response.status_code, 201)
        
        # Verify Neo4j method was called correctly
        self.mock_neo4j_instance.add_entity.assert_called_once()
    
    def test_knowledge_graph_relationship_endpoints(self):
        """Test knowledge graph relationship API endpoints."""
        # Test GET /api/knowledge-graph/relationships
        response = self.client.get("/api/knowledge-graph/relationships")
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains expected relationships
        relationships = response.json()
        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0]["source"]["name"], "Vision Transformer")
        self.assertEqual(relationships[0]["target"]["name"], "ImageNet")
        
        # Test POST /api/knowledge-graph/relationships
        new_relationship = {
            "source_id": "1",
            "target_id": "2",
            "type": "COMPARED_TO",
            "properties": {
                "performance_difference": "+0.05"
            }
        }
        response = self.client.post("/api/knowledge-graph/relationships", json=new_relationship)
        self.assertEqual(response.status_code, 201)
        
        # Verify Neo4j method was called correctly
        self.mock_neo4j_instance.add_relationship.assert_called_once()
    
    def test_research_document_endpoints(self):
        """Test research document API endpoints with MongoDB."""
        # Test GET /api/research/{research_id}
        response = self.client.get("/api/research/research_1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Vision Transformer Research")
        
        # Test GET /api/research (list)
        response = self.client.get("/api/research?limit=10&page=1")
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains expected documents
        documents = response.json()["items"]
        self.assertEqual(len(documents), 2)
        
        # Test POST /api/research (create)
        new_research = {
            "title": "Attention Mechanisms in Deep Learning",
            "query": "How do attention mechanisms work?",
            "content": "Attention mechanisms allow models to focus on specific parts of the input..."
        }
        response = self.client.post("/api/research", json=new_research)
        self.assertEqual(response.status_code, 201)
        
        # Verify MongoDB method was called correctly
        self.mock_collection.insert_one.assert_called_once()
    
    def test_implementation_endpoints(self):
        """Test implementation API endpoints with MongoDB."""
        # Test GET /api/implementation/{implementation_id}
        response = self.client.get("/api/implementation/implementation_1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "ViT Implementation")
        
        # Test POST /api/implementation (create)
        new_implementation = {
            "title": "BERT Implementation",
            "model_id": "2",
            "code": "import transformers...",
            "description": "Implementation of BERT model"
        }
        response = self.client.post("/api/implementation", json=new_implementation)
        self.assertEqual(response.status_code, 201)
        
        # Verify MongoDB method was called correctly
        self.mock_collection.insert_one.assert_called_once()
    
    def test_api_database_end_to_end(self):
        """Test end-to-end flow from API to database and back."""
        # 1. Create a new research document via API
        new_research = {
            "title": "Transformer Architecture",
            "query": "How does the transformer architecture work?",
            "content": "The transformer architecture relies on attention mechanisms..."
        }
        
        # Configure MongoDB to return a specific ID for the new research
        insert_result = MagicMock()
        insert_result.inserted_id = "research_transformer"
        self.mock_collection.insert_one.return_value = insert_result
        
        # Create research via API
        response = self.client.post("/api/research", json=new_research)
        self.assertEqual(response.status_code, 201)
        research_id = response.json()["id"]
        
        # 2. Set up mock to return this research when queried
        def updated_find_one(query):
            if query.get("_id") == "research_transformer":
                return {"_id": "research_transformer", "title": "Transformer Architecture", **new_research}
            return None
            
        self.mock_collection.find_one.side_effect = updated_find_one
        
        # 3. Retrieve the research via API
        response = self.client.get(f"/api/research/{research_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Transformer Architecture")
        
        # 4. Create entities in knowledge graph extracted from research
        new_entity = {
            "name": "Transformer",
            "type": "ARCHITECTURE",
            "properties": {
                "year": 2017,
                "paper": "Attention Is All You Need"
            }
        }
        
        # Configure Neo4j mock for entity creation
        self.mock_neo4j_instance.add_entity.return_value = "entity_transformer"
        
        # Create entity via API
        response = self.client.post("/api/knowledge-graph/entities", json=new_entity)
        self.assertEqual(response.status_code, 201)
        entity_id = response.json()["id"]
        
        # 5. Create implementation referencing the research and knowledge graph entity
        new_implementation = {
            "title": "Transformer Implementation",
            "research_id": research_id,
            "entity_id": entity_id,
            "code": "import torch\nclass TransformerModel(nn.Module):\n    def __init__(self):\n        super().__init__()\n        # Implementation details..."
        }
        
        # Configure MongoDB for implementation creation
        insert_result.inserted_id = "implementation_transformer"
        
        # Create implementation via API
        response = self.client.post("/api/implementation", json=new_implementation)
        self.assertEqual(response.status_code, 201)
        implementation_id = response.json()["id"]
        
        # Verify correct interaction between components
        self.mock_collection.insert_one.assert_called()
        self.mock_neo4j_instance.add_entity.assert_called_once()

if __name__ == '__main__':
    unittest.main()