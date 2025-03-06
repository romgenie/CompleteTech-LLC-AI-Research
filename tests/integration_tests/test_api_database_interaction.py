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
from datetime import datetime, timedelta

class TestApiDatabaseInteraction(unittest.TestCase):
    """Test interaction between API endpoints and databases."""

    def setUp(self):
        """Set up test environment with mocked databases."""
        # Patch Neo4j and MongoDB connections
        self.neo4j_patcher = patch('knowledge_graph_system.core.db.neo4j_manager.Neo4jManager')
        self.mongodb_patcher = patch('src.api.dependencies.database.MongoClient')
        self.auth_patcher = patch('src.api.dependencies.auth.get_current_user')
        
        # Start patchers
        self.mock_neo4j = self.neo4j_patcher.start()
        self.mock_mongodb = self.mongodb_patcher.start()
        self.mock_auth = self.auth_patcher.start()
        
        # Mock the auth to return a test user
        from src.api.dependencies.auth import User
        self.mock_auth.return_value = User(
            username="test_user",
            email="test@example.com",
            full_name="Test User",
            disabled=False
        )
        
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
            if query.get("id") == "research_1":
                return {
                    "id": "research_1", 
                    "query": "Vision Transformer Research",
                    "status": "completed",
                    "user": "test_user",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "sources": ["web", "academic"],
                    "max_results": 10,
                    "filters": {}
                }
            elif query.get("id") == "implementation_1":
                return {
                    "id": "implementation_1", 
                    "title": "ViT Implementation", 
                    "description": "Implementation of Vision Transformer",
                    "paper_id": "research_1",
                    "components": [
                        {
                            "name": "Transformer",
                            "description": "Core transformer component",
                            "dependencies": []
                        }
                    ],
                    "requirements": {
                        "frameworks": ["pytorch"],
                        "libraries": ["transformers"]
                    },
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "user": "test_user"
                }
            return None
            
        self.mock_collection.find_one.side_effect = mock_find_one
        
        # Mock find to return multiple documents
        self.mock_cursor = MagicMock()
        self.mock_cursor.limit.return_value = self.mock_cursor
        self.mock_cursor.skip.return_value = self.mock_cursor
        self.mock_cursor.sort.return_value = self.mock_cursor
        
        def mock_to_list():
            return [
                {
                    "id": "research_1", 
                    "query": "Vision Transformer Research",
                    "status": "completed",
                    "user": "test_user",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "sources": ["web", "academic"],
                    "max_results": 10,
                    "filters": {}
                },
                {
                    "id": "research_2", 
                    "query": "Diffusion Models Overview",
                    "status": "completed",
                    "user": "test_user",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "sources": ["web", "academic"],
                    "max_results": 10,
                    "filters": {}
                }
            ]
            
        self.mock_cursor.to_list.return_value = mock_to_list()
        self.mock_collection.find.return_value = self.mock_cursor
        
        # Mock insert_one to return created ID
        insert_result = MagicMock()
        insert_result.inserted_id = "new_id_123"
        self.mock_collection.insert_one.return_value = insert_result
        
        # Import and initialize FastAPI app (after patching)
        from src.api.main import app
        
        # Create a test token
        from src.api.dependencies.auth import create_access_token
        from datetime import timedelta
        
        test_token = create_access_token(
            data={"sub": "test_user"},
            expires_delta=timedelta(minutes=30)
        )
        
        # Create test client
        self.client = TestClient(app)
        
        # Set authorization header for all requests
        self.client.headers["Authorization"] = f"Bearer {test_token}"
        
    def tearDown(self):
        """Clean up test environment."""
        self.neo4j_patcher.stop()
        self.mongodb_patcher.stop()
        self.auth_patcher.stop()
        
    def add_query_params(self, url, params=None):
        """
        Helper function to add query parameters to API requests.
        
        Args:
            url (str): The base URL for the API endpoint
            params (dict, optional): Dictionary of query parameters to add. Defaults to None.
        
        Returns:
            str: URL with added query parameters
        """
        # Add default args and kwargs params if none provided
        if params is None:
            params = {}
        
        # Ensure required parameters are included
        if 'args' not in params:
            params['args'] = '[]'
        if 'kwargs' not in params:
            params['kwargs'] = '{}'
        
        # Construct query string
        query_parts = [f"{k}={v}" for k, v in params.items()]
        query_string = "&".join(query_parts)
        
        # Add query string to URL
        if "?" in url:
            return f"{url}&{query_string}"
        else:
            return f"{url}?{query_string}"
    
    def test_knowledge_graph_entity_endpoints(self):
        """Test knowledge graph entity API endpoints."""
        # Test GET /knowledge/entities/ with required query parameters
        url = self.add_query_params("/knowledge/entities/")
        response = self.client.get(url)
        print(f"GET /knowledge/entities/ response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains expected entities
        response_data = response.json()
        self.assertTrue("items" in response_data)
        entities = response_data["items"]
        self.assertEqual(len(entities), 3)
        self.assertEqual(entities[0]["name"], "Vision Transformer")
        
        # Test GET /knowledge/entities/{entity_id} with required query parameters
        url = self.add_query_params("/knowledge/entities/1")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Vision Transformer")
        
        # Test POST /knowledge/entities/ with required query parameters
        new_entity = {
            "name": "BERT",
            "label": "MODEL",
            "properties": {
                "year": 2018,
                "authors": ["Jacob Devlin", "Ming-Wei Chang"]
            },
            "confidence": 0.95,
            "source": "test"
        }
        url = self.add_query_params("/knowledge/entities/")
        response = self.client.post(url, json=new_entity)
        print(f"POST /knowledge/entities/ response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 201)
        
        # Verify Neo4j method was called correctly
        self.mock_neo4j_instance.add_entity.assert_called_once()
    
    def test_knowledge_graph_relationship_endpoints(self):
        """Test knowledge graph relationship API endpoints."""
        # Test GET /knowledge/relationships/ with required query parameters
        url = self.add_query_params("/knowledge/relationships/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains expected relationships
        response_data = response.json()
        self.assertTrue("items" in response_data)
        relationships = response_data["items"]
        self.assertEqual(len(relationships), 1)
        self.assertEqual(relationships[0]["source_entity"]["name"], "Vision Transformer")
        self.assertEqual(relationships[0]["target_entity"]["name"], "ImageNet")
        
        # Test POST /knowledge/relationships/ with required query parameters
        new_relationship = {
            "source_id": "1",
            "target_id": "2",
            "type": "COMPARED_TO",
            "properties": {
                "performance_difference": "+0.05"
            },
            "confidence": 0.9,
            "source": "test",
            "bidirectional": False
        }
        url = self.add_query_params("/knowledge/relationships/")
        response = self.client.post(url, json=new_relationship)
        self.assertEqual(response.status_code, 201)
        
        # Verify Neo4j method was called correctly
        self.mock_neo4j_instance.add_relationship.assert_called_once()
    
    def test_research_document_endpoints(self):
        """Test research document API endpoints with MongoDB."""
        # Test GET /research/tasks/{task_id} with required query parameters
        url = self.add_query_params("/research/tasks/research_1")
        response = self.client.get(url)
        print(f"GET /research/tasks/research_1 response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["query"], "Vision Transformer Research")
        
        # Test GET /research/tasks/ (list) with required query parameters
        url = self.add_query_params("/research/tasks/", {"limit": "10", "offset": "0"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify response contains expected documents
        tasks = response.json()
        self.assertEqual(len(tasks), 2)
        
        # Test POST /research/queries/ (create) with required query parameters
        new_research = {
            "query": "How do attention mechanisms work?",
            "sources": ["web", "academic"],
            "max_results": 10,
            "filters": {}
        }
        url = self.add_query_params("/research/queries/")
        response = self.client.post(url, json=new_research)
        print(f"POST /research/queries/ response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 201)
        
        # Verify MongoDB method was called correctly
        self.mock_collection.insert_one.assert_called_once()
    
    def test_implementation_endpoints(self):
        """Test implementation API endpoints with MongoDB."""
        # Test GET /implementation/{implementation_id}
        url = self.add_query_params("/implementation/implementation_1")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "ViT Implementation")
        
        # Test POST /implementation/ (create)
        new_implementation = {
            "title": "BERT Implementation",
            "description": "Implementation of BERT model",
            "paper_id": "research_1",
            "components": [],
            "requirements": {
                "frameworks": ["transformers"],
                "libraries": ["torch"]
            }
        }
        url = self.add_query_params("/implementation/")
        response = self.client.post(url, json=new_implementation)
        self.assertEqual(response.status_code, 201)
        
        # Verify MongoDB method was called correctly
        self.mock_collection.insert_one.assert_called_once()
    
    def test_api_database_end_to_end(self):
        """Test end-to-end flow from API to database and back."""
        # 1. Create a new research query via API
        new_research = {
            "query": "How does the transformer architecture work?",
            "sources": ["web", "academic"],
            "max_results": 10,
            "filters": {}
        }
        
        # Configure MongoDB to return a specific ID for the new research
        insert_result = MagicMock()
        insert_result.inserted_id = "research_transformer"
        self.mock_collection.insert_one.return_value = insert_result
        
        # Create research via API with required query parameters
        url = self.add_query_params("/research/queries/")
        response = self.client.post(url, json=new_research)
        self.assertEqual(response.status_code, 201)
        research_id = response.json()["id"]
        
        # 2. Set up mock to return this research when queried
        def updated_find_one(query):
            if query.get("id") == research_id:
                return {
                    "id": research_id, 
                    "query": "How does the transformer architecture work?",
                    "status": "completed",
                    "user": "test_user"
                }
            return None
            
        self.mock_collection.find_one.side_effect = updated_find_one
        
        # 3. Retrieve the research via API with required query parameters
        url = self.add_query_params(f"/research/tasks/{research_id}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["query"], "How does the transformer architecture work?")
        
        # 4. Create entities in knowledge graph extracted from research
        new_entity = {
            "name": "Transformer",
            "label": "ARCHITECTURE",
            "properties": {
                "year": 2017,
                "paper": "Attention Is All You Need"
            },
            "confidence": 0.95,
            "source": "test"
        }
        
        # Configure Neo4j mock for entity creation
        self.mock_neo4j_instance.add_entity.return_value = {"success": True, "entity_id": "entity_transformer"}
        
        # Create entity via API with required query parameters
        url = self.add_query_params("/knowledge/entities/")
        response = self.client.post(url, json=new_entity)
        self.assertEqual(response.status_code, 201)
        entity_id = response.json()["id"]
        
        # 5. Create implementation referencing the research and knowledge graph entity
        new_implementation = {
            "title": "Transformer Implementation",
            "description": "Implementation of the Transformer architecture",
            "paper_id": research_id,
            "components": [
                {
                    "name": "TransformerEncoder",
                    "description": "Encoder part of the transformer",
                    "dependencies": []
                },
                {
                    "name": "TransformerDecoder", 
                    "description": "Decoder part of the transformer",
                    "dependencies": ["TransformerEncoder"]
                }
            ],
            "requirements": {
                "frameworks": ["pytorch"],
                "libraries": ["transformers"]
            }
        }
        
        # Configure MongoDB for implementation creation
        insert_result.inserted_id = "implementation_transformer"
        
        # Create implementation via API with required query parameters
        url = self.add_query_params("/implementation/")
        response = self.client.post(url, json=new_implementation)
        self.assertEqual(response.status_code, 201)
        
        # Verify that MongoDB insert was called with research and implementation
        self.assertEqual(self.mock_collection.insert_one.call_count, 2)
        
        # Verify that Neo4j was used to add entity
        self.mock_neo4j_instance.add_entity.assert_called_once()
        implementation_id = response.json()["id"]

if __name__ == '__main__':
    unittest.main()