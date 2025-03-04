"""
Neo4j Manager for Knowledge Graph System.

This module provides functionality for connecting to and managing Neo4j databases
for the Knowledge Graph System.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import json
import os
from neo4j import GraphDatabase, Session, Transaction, Result, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError, DriverError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jManager:
    """
    Manager for Neo4j database connections and operations.
    
    This class provides methods for connecting to Neo4j, executing queries,
    and managing graph data.
    """
    
    def __init__(self, uri: str, username: str, password: str, 
                 database: str = "neo4j", max_connection_lifetime: int = 3600,
                 max_connection_pool_size: int = 50, encrypted: bool = True):
        """
        Initialize the Neo4j manager.
        
        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
            database: Neo4j database name
            max_connection_lifetime: Maximum lifetime of connections in seconds
            max_connection_pool_size: Maximum size of the connection pool
            encrypted: Whether to use encryption for the connection
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.driver = None
        self.max_connection_lifetime = max_connection_lifetime
        self.max_connection_pool_size = max_connection_pool_size
        self.encrypted = encrypted
        
        # Initialize connection
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password),
                max_connection_lifetime=self.max_connection_lifetime,
                max_connection_pool_size=self.max_connection_pool_size,
                encrypted=self.encrypted
            )
            # Verify connection
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j database at {self.uri}")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close the connection to Neo4j."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def get_session(self) -> Session:
        """
        Get a new session for interacting with Neo4j.
        
        Returns:
            Neo4j session
            
        Raises:
            DriverError: If there's an issue with the driver
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            raise DriverError("Neo4j driver not initialized")
        
        return self.driver.session(database=self.database)
    
    def run_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Result:
        """
        Run a Cypher query against Neo4j.
        
        Args:
            query: Cypher query string
            parameters: Parameters for the query
            
        Returns:
            Neo4j result object
            
        Raises:
            Exception: If the query fails
        """
        if not parameters:
            parameters = {}
        
        with self.get_session() as session:
            try:
                result = session.run(query, parameters)
                return result
            except Exception as e:
                logger.error(f"Query failed: {e}\nQuery: {query}\nParameters: {parameters}")
                raise
    
    def execute_read_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a read query and return the results as a list of dictionaries.
        
        Args:
            query: Cypher query string
            parameters: Parameters for the query
            
        Returns:
            List of dictionaries containing query results
        """
        with self.get_session() as session:
            result = session.read_transaction(self._execute_query, query, parameters)
            return result
    
    def execute_write_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a write query and return the results as a list of dictionaries.
        
        Args:
            query: Cypher query string
            parameters: Parameters for the query
            
        Returns:
            List of dictionaries containing query results
        """
        with self.get_session() as session:
            result = session.write_transaction(self._execute_query, query, parameters)
            return result
    
    @staticmethod
    def _execute_query(tx: Transaction, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query in a transaction and convert the result to a list of dictionaries.
        
        Args:
            tx: Neo4j transaction
            query: Cypher query string
            parameters: Parameters for the query
            
        Returns:
            List of dictionaries containing query results
        """
        if not parameters:
            parameters = {}
        
        result = tx.run(query, parameters)
        records = [record.data() for record in result]
        return records
    
    def create_constraints(self, constraints: List[Dict[str, str]]):
        """
        Create constraints in the Neo4j database.
        
        Args:
            constraints: List of constraint definitions, each with 'name', 'label', and 'property'
        """
        for constraint in constraints:
            name = constraint.get('name')
            label = constraint.get('label')
            property_name = constraint.get('property')
            
            if not all([name, label, property_name]):
                logger.warning(f"Incomplete constraint definition: {constraint}")
                continue
            
            # For Neo4j 4.x+
            query = (
                f"CREATE CONSTRAINT {name} IF NOT EXISTS "
                f"FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE"
            )
            
            try:
                self.run_query(query)
                logger.info(f"Created constraint {name} for {label}.{property_name}")
            except Exception as e:
                logger.error(f"Failed to create constraint {name}: {e}")
    
    def create_indexes(self, indexes: List[Dict[str, str]]):
        """
        Create indexes in the Neo4j database.
        
        Args:
            indexes: List of index definitions, each with 'name', 'label', and 'properties' (list)
        """
        for index in indexes:
            name = index.get('name')
            label = index.get('label')
            properties = index.get('properties', [])
            
            if not all([name, label, properties]):
                logger.warning(f"Incomplete index definition: {index}")
                continue
            
            # For Neo4j 4.x+
            properties_str = ', '.join([f"n.{prop}" for prop in properties])
            query = (
                f"CREATE INDEX {name} IF NOT EXISTS "
                f"FOR (n:{label}) ON ({properties_str})"
            )
            
            try:
                self.run_query(query)
                logger.info(f"Created index {name} for {label} on {properties}")
            except Exception as e:
                logger.error(f"Failed to create index {name}: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the Neo4j database.
        
        Returns:
            Dictionary containing database information
        """
        query = """
        CALL dbms.components()
        YIELD name, versions, edition
        RETURN name, versions, edition
        """
        
        try:
            result = self.execute_read_query(query)
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}
    
    def get_database_size(self) -> Dict[str, Any]:
        """
        Get information about the size of the database.
        
        Returns:
            Dictionary containing node and relationship counts
        """
        query = """
        MATCH (n)
        RETURN count(n) as nodeCount
        """
        
        try:
            node_result = self.execute_read_query(query)
            node_count = node_result[0].get('nodeCount', 0) if node_result else 0
            
            query = """
            MATCH ()-[r]->()
            RETURN count(r) as relCount
            """
            
            rel_result = self.execute_read_query(query)
            rel_count = rel_result[0].get('relCount', 0) if rel_result else 0
            
            return {
                'node_count': node_count,
                'relationship_count': rel_count,
                'total_elements': node_count + rel_count
            }
        except Exception as e:
            logger.error(f"Failed to get database size: {e}")
            return {
                'node_count': 0,
                'relationship_count': 0,
                'total_elements': 0
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema of the database (labels, relationship types, properties).
        
        Returns:
            Dictionary containing schema information
        """
        # Get node labels
        labels_query = """
        CALL db.labels() YIELD label
        RETURN collect(label) as labels
        """
        
        # Get relationship types
        rel_types_query = """
        CALL db.relationshipTypes() YIELD relationshipType
        RETURN collect(relationshipType) as relationshipTypes
        """
        
        # Get property keys
        property_keys_query = """
        CALL db.propertyKeys() YIELD propertyKey
        RETURN collect(propertyKey) as propertyKeys
        """
        
        try:
            labels_result = self.execute_read_query(labels_query)
            labels = labels_result[0].get('labels', []) if labels_result else []
            
            rel_types_result = self.execute_read_query(rel_types_query)
            rel_types = rel_types_result[0].get('relationshipTypes', []) if rel_types_result else []
            
            property_keys_result = self.execute_read_query(property_keys_query)
            property_keys = property_keys_result[0].get('propertyKeys', []) if property_keys_result else []
            
            return {
                'labels': labels,
                'relationship_types': rel_types,
                'property_keys': property_keys
            }
        except Exception as e:
            logger.error(f"Failed to get schema information: {e}")
            return {
                'labels': [],
                'relationship_types': [],
                'property_keys': []
            }
    
    def clear_database(self, confirm: bool = False):
        """
        Clear all data from the database.
        
        Args:
            confirm: Confirmation flag to prevent accidental clearing
            
        Raises:
            ValueError: If confirmation is not provided
        """
        if not confirm:
            raise ValueError("Database clearing requires confirmation. Set confirm=True to proceed.")
        
        query = "MATCH (n) DETACH DELETE n"
        
        try:
            self.execute_write_query(query)
            logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            raise
    
    @classmethod
    def from_config(cls, config_path: str) -> 'Neo4jManager':
        """
        Create a Neo4jManager instance from a configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Neo4jManager instance
            
        Raises:
            FileNotFoundError: If the configuration file is not found
            ValueError: If the configuration is invalid
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            required_fields = ['uri', 'username', 'password']
            if not all(field in config for field in required_fields):
                missing = [field for field in required_fields if field not in config]
                raise ValueError(f"Missing required fields in configuration: {missing}")
            
            return cls(
                uri=config['uri'],
                username=config['username'],
                password=config['password'],
                database=config.get('database', 'neo4j'),
                max_connection_lifetime=config.get('max_connection_lifetime', 3600),
                max_connection_pool_size=config.get('max_connection_pool_size', 50),
                encrypted=config.get('encrypted', True)
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    @classmethod
    def from_env(cls) -> 'Neo4jManager':
        """
        Create a Neo4jManager instance from environment variables.
        
        Required environment variables:
            NEO4J_URI: Neo4j connection URI
            NEO4J_USERNAME: Neo4j username
            NEO4J_PASSWORD: Neo4j password
        
        Optional environment variables:
            NEO4J_DATABASE: Neo4j database name (default: 'neo4j')
            NEO4J_MAX_CONNECTION_LIFETIME: Maximum lifetime of connections in seconds (default: 3600)
            NEO4J_MAX_CONNECTION_POOL_SIZE: Maximum size of the connection pool (default: 50)
            NEO4J_ENCRYPTED: Whether to use encryption for the connection (default: 'true')
        
        Returns:
            Neo4jManager instance
            
        Raises:
            ValueError: If required environment variables are not set
        """
        required_env_vars = ['NEO4J_URI', 'NEO4J_USERNAME', 'NEO4J_PASSWORD']
        for var in required_env_vars:
            if not os.environ.get(var):
                raise ValueError(f"Missing required environment variable: {var}")
        
        encrypted = os.environ.get('NEO4J_ENCRYPTED', 'true').lower() == 'true'
        
        return cls(
            uri=os.environ['NEO4J_URI'],
            username=os.environ['NEO4J_USERNAME'],
            password=os.environ['NEO4J_PASSWORD'],
            database=os.environ.get('NEO4J_DATABASE', 'neo4j'),
            max_connection_lifetime=int(os.environ.get('NEO4J_MAX_CONNECTION_LIFETIME', 3600)),
            max_connection_pool_size=int(os.environ.get('NEO4J_MAX_CONNECTION_POOL_SIZE', 50)),
            encrypted=encrypted
        )