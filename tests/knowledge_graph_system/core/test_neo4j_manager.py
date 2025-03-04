"""
Tests for the Neo4j Manager module.
"""

import unittest
import os
from unittest.mock import MagicMock, patch

from knowledge_graph_system.core.db.neo4j_manager import Neo4jManager


class TestNeo4jManager(unittest.TestCase):
    """Tests for the Neo4jManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock for GraphDatabase
        self.mock_driver = MagicMock()
        self.mock_session = MagicMock()
        self.mock_transaction = MagicMock()
        
        # Configure mocks
        self.mock_driver.session.return_value = self.mock_session
        self.mock_session.__enter__.return_value = self.mock_session
        self.mock_session.__exit__.return_value = None
        self.mock_session.read_transaction.side_effect = self._mock_transaction
        self.mock_session.write_transaction.side_effect = self._mock_transaction
        
        # Create patch for GraphDatabase
        self.graph_db_patch = patch('knowledge_graph_system.core.db.neo4j_manager.GraphDatabase')
        self.mock_graph_db = self.graph_db_patch.start()
        self.mock_graph_db.driver.return_value = self.mock_driver
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.graph_db_patch.stop()
    
    def _mock_transaction(self, func, query, parameters=None):
        """Mock transaction execution."""
        return func(self.mock_transaction, query, parameters)
    
    def test_init(self):
        """Test initialization of Neo4jManager."""
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Check if driver was created correctly
        self.mock_graph_db.driver.assert_called_once_with(
            "bolt://localhost:7687",
            auth=("neo4j", "password"),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            encrypted=True
        )
        
        # Check if connection was verified
        self.mock_driver.verify_connectivity.assert_called_once()
    
    def test_close(self):
        """Test closing the Neo4jManager."""
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Close the manager
        manager.close()
        
        # Check if driver was closed
        self.mock_driver.close.assert_called_once()
    
    def test_get_session(self):
        """Test getting a session."""
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Get a session
        session = manager.get_session()
        
        # Check if session was created correctly
        self.mock_driver.session.assert_called_once_with(database="neo4j")
        self.assertEqual(session, self.mock_session)
    
    def test_run_query(self):
        """Test running a query."""
        # Configure mock
        mock_result = MagicMock()
        self.mock_session.run.return_value = mock_result
        
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Run a query
        query = "MATCH (n) RETURN n"
        parameters = {"param": "value"}
        result = manager.run_query(query, parameters)
        
        # Check if query was run correctly
        self.mock_session.run.assert_called_once_with(query, parameters)
        self.assertEqual(result, mock_result)
    
    def test_execute_read_query(self):
        """Test executing a read query."""
        # Configure mock
        mock_record = MagicMock()
        mock_record.data.return_value = {"key": "value"}
        mock_result = MagicMock()
        mock_result.__iter__.return_value = [mock_record]
        
        self.mock_transaction.run.return_value = mock_result
        
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Execute a read query
        query = "MATCH (n) RETURN n"
        parameters = {"param": "value"}
        result = manager.execute_read_query(query, parameters)
        
        # Check if query was executed correctly
        self.mock_session.read_transaction.assert_called_once()
        self.mock_transaction.run.assert_called_once_with(query, parameters)
        self.assertEqual(result, [{"key": "value"}])
    
    def test_execute_write_query(self):
        """Test executing a write query."""
        # Configure mock
        mock_record = MagicMock()
        mock_record.data.return_value = {"key": "value"}
        mock_result = MagicMock()
        mock_result.__iter__.return_value = [mock_record]
        
        self.mock_transaction.run.return_value = mock_result
        
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Execute a write query
        query = "CREATE (n) RETURN n"
        parameters = {"param": "value"}
        result = manager.execute_write_query(query, parameters)
        
        # Check if query was executed correctly
        self.mock_session.write_transaction.assert_called_once()
        self.mock_transaction.run.assert_called_once_with(query, parameters)
        self.assertEqual(result, [{"key": "value"}])
    
    def test_create_constraints(self):
        """Test creating constraints."""
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Create constraints
        constraints = [
            {"name": "test_constraint", "label": "Test", "property": "id"}
        ]
        manager.create_constraints(constraints)
        
        # Check if query was run correctly
        expected_query = (
            "CREATE CONSTRAINT test_constraint IF NOT EXISTS "
            "FOR (n:Test) REQUIRE n.id IS UNIQUE"
        )
        self.mock_session.run.assert_called_once_with(expected_query, {})
    
    def test_create_indexes(self):
        """Test creating indexes."""
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Create indexes
        indexes = [
            {"name": "test_index", "label": "Test", "properties": ["prop1", "prop2"]}
        ]
        manager.create_indexes(indexes)
        
        # Check if query was run correctly
        expected_query = (
            "CREATE INDEX test_index IF NOT EXISTS "
            "FOR (n:Test) ON (n.prop1, n.prop2)"
        )
        self.mock_session.run.assert_called_once_with(expected_query, {})
    
    def test_clear_database(self):
        """Test clearing the database."""
        # Create Neo4jManager instance
        manager = Neo4jManager(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        
        # Test without confirmation
        with self.assertRaises(ValueError):
            manager.clear_database()
        
        # Test with confirmation
        manager.clear_database(confirm=True)
        
        # Check if query was executed correctly
        expected_query = "MATCH (n) DETACH DELETE n"
        self.mock_session.write_transaction.assert_called_once()
    
    @patch('knowledge_graph_system.core.db.neo4j_manager.os')
    @patch('knowledge_graph_system.core.db.neo4j_manager.json')
    def test_from_config(self, mock_json, mock_os):
        """Test creating Neo4jManager from config file."""
        # Configure mocks
        mock_os.path.exists.return_value = True
        mock_json.load.return_value = {
            "uri": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password",
            "database": "test"
        }
        
        # Create Neo4jManager from config
        manager = Neo4jManager.from_config("config.json")
        
        # Check if manager was created correctly
        self.mock_graph_db.driver.assert_called_with(
            "bolt://localhost:7687",
            auth=("neo4j", "password"),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            encrypted=True
        )
        self.assertEqual(manager.database, "test")
    
    @patch('knowledge_graph_system.core.db.neo4j_manager.os')
    def test_from_env(self, mock_os):
        """Test creating Neo4jManager from environment variables."""
        # Configure mock
        mock_os.environ = {
            "NEO4J_URI": "bolt://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "password",
            "NEO4J_DATABASE": "test",
            "NEO4J_ENCRYPTED": "false"
        }
        
        # Create Neo4jManager from environment variables
        manager = Neo4jManager.from_env()
        
        # Check if manager was created correctly
        self.mock_graph_db.driver.assert_called_with(
            "bolt://localhost:7687",
            auth=("neo4j", "password"),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            encrypted=False
        )
        self.assertEqual(manager.database, "test")


if __name__ == '__main__':
    unittest.main()