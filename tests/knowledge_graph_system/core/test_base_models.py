"""
Tests for the base models module.
"""

import unittest
from datetime import datetime
import json

from knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship


class TestGraphEntity(unittest.TestCase):
    """Tests for the GraphEntity class."""
    
    def test_init(self):
        """Test initialization of GraphEntity."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity",
            properties={"name": "Test Entity", "description": "A test entity"},
            confidence=0.9,
            source="test"
        )
        
        # Check if attributes were set correctly
        self.assertEqual(entity.id, "test-entity")
        self.assertEqual(entity.label, "TestEntity")
        self.assertEqual(entity.properties, {"name": "Test Entity", "description": "A test entity"})
        self.assertEqual(entity.confidence, 0.9)
        self.assertEqual(entity.source, "test")
        self.assertIsInstance(entity.created_at, datetime)
        self.assertIsInstance(entity.updated_at, datetime)
        self.assertEqual(entity.labels, {"TestEntity"})
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity",
            properties={"name": "Test Entity", "description": "A test entity"},
            confidence=0.9,
            source="test"
        )
        
        # Convert to dictionary
        entity_dict = entity.to_dict()
        
        # Check if dictionary contains the correct values
        self.assertEqual(entity_dict["id"], "test-entity")
        self.assertEqual(entity_dict["label"], "TestEntity")
        self.assertEqual(entity_dict["properties"], {"name": "Test Entity", "description": "A test entity"})
        self.assertEqual(entity_dict["confidence"], 0.9)
        self.assertEqual(entity_dict["source"], "test")
        self.assertIsInstance(entity_dict["created_at"], str)
        self.assertIsInstance(entity_dict["updated_at"], str)
        self.assertEqual(entity_dict["labels"], ["TestEntity"])
    
    def test_to_json(self):
        """Test conversion to JSON."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity",
            properties={"name": "Test Entity", "description": "A test entity"},
            confidence=0.9,
            source="test"
        )
        
        # Convert to JSON
        entity_json = entity.to_json()
        
        # Check if JSON can be parsed back to dictionary
        entity_dict = json.loads(entity_json)
        self.assertEqual(entity_dict["id"], "test-entity")
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        # Create dictionary
        entity_dict = {
            "id": "test-entity",
            "label": "TestEntity",
            "properties": {"name": "Test Entity", "description": "A test entity"},
            "confidence": 0.9,
            "source": "test",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "labels": ["TestEntity"]
        }
        
        # Create GraphEntity from dictionary
        entity = GraphEntity.from_dict(entity_dict)
        
        # Check if attributes were set correctly
        self.assertEqual(entity.id, "test-entity")
        self.assertEqual(entity.label, "TestEntity")
        self.assertEqual(entity.properties, {"name": "Test Entity", "description": "A test entity"})
        self.assertEqual(entity.confidence, 0.9)
        self.assertEqual(entity.source, "test")
        self.assertIsInstance(entity.created_at, datetime)
        self.assertIsInstance(entity.updated_at, datetime)
        self.assertEqual(entity.labels, {"TestEntity"})
    
    def test_update(self):
        """Test updating entity properties."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity",
            properties={"name": "Test Entity"},
            confidence=0.9
        )
        
        # Initial values
        initial_created_at = entity.created_at
        initial_updated_at = entity.updated_at
        
        # Wait a moment to ensure updated_at will be different
        import time
        time.sleep(0.001)
        
        # Update properties
        entity.update({
            "label": "UpdatedEntity",
            "properties": {"description": "An updated entity"},
            "confidence": 0.95,
            "source": "updated",
            "labels": ["UpdatedEntity", "AnotherLabel"]
        })
        
        # Check if attributes were updated correctly
        self.assertEqual(entity.id, "test-entity")  # ID should not change
        self.assertEqual(entity.label, "UpdatedEntity")
        self.assertEqual(entity.properties, {"name": "Test Entity", "description": "An updated entity"})
        self.assertEqual(entity.confidence, 0.95)
        self.assertEqual(entity.source, "updated")
        self.assertEqual(entity.created_at, initial_created_at)  # created_at should not change
        self.assertNotEqual(entity.updated_at, initial_updated_at)  # updated_at should change
        self.assertEqual(entity.labels, {"UpdatedEntity", "AnotherLabel"})
    
    def test_add_alias(self):
        """Test adding an alias."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity"
        )
        
        # Initial values
        initial_updated_at = entity.updated_at
        
        # Wait a moment to ensure updated_at will be different
        import time
        time.sleep(0.001)
        
        # Add alias
        entity.add_alias("test-alias")
        
        # Check if alias was added
        self.assertIn("test-alias", entity.aliases)
        self.assertNotEqual(entity.updated_at, initial_updated_at)  # updated_at should change
    
    def test_add_label(self):
        """Test adding a label."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity"
        )
        
        # Initial values
        initial_updated_at = entity.updated_at
        
        # Wait a moment to ensure updated_at will be different
        import time
        time.sleep(0.001)
        
        # Add label
        entity.add_label("AnotherLabel")
        
        # Check if label was added
        self.assertIn("AnotherLabel", entity.labels)
        self.assertNotEqual(entity.updated_at, initial_updated_at)  # updated_at should change
    
    def test_to_cypher_params(self):
        """Test conversion to Cypher parameters."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity",
            properties={"name": "Test Entity", "description": "A test entity"},
            confidence=0.9,
            source="test",
            aliases=["alias1", "alias2"]
        )
        
        # Convert to Cypher parameters
        params = entity.to_cypher_params()
        
        # Check if parameters contain the correct values
        self.assertEqual(params["id"], "test-entity")
        self.assertEqual(params["name"], "Test Entity")
        self.assertEqual(params["description"], "A test entity")
        self.assertEqual(params["confidence"], 0.9)
        self.assertEqual(params["source"], "test")
        self.assertEqual(params["aliases"], ["alias1", "alias2"])
        self.assertIsInstance(params["created_at"], str)
        self.assertIsInstance(params["updated_at"], str)
    
    def test_get_cypher_create(self):
        """Test generating Cypher query for entity creation."""
        # Create GraphEntity instance
        entity = GraphEntity(
            id="test-entity",
            label="TestEntity",
            properties={"name": "Test Entity", "description": "A test entity"},
            confidence=0.9,
            source="test",
            aliases=["alias1", "alias2"]
        )
        
        # Generate Cypher query
        query, params = entity.get_cypher_create()
        
        # Check if query and parameters are correct
        self.assertIn("CREATE (e:TestEntity", query)
        self.assertIn("id: $id", query)
        self.assertIn("created_at: $created_at", query)
        self.assertIn("updated_at: $updated_at", query)
        self.assertIn("confidence: $confidence", query)
        self.assertIn("aliases: $aliases", query)
        self.assertIn("source: $source", query)
        self.assertIn("name: $name", query)
        self.assertIn("description: $description", query)
        self.assertEqual(params["id"], "test-entity")
        self.assertEqual(params["name"], "Test Entity")
        self.assertEqual(params["description"], "A test entity")
        self.assertEqual(params["confidence"], 0.9)
        self.assertEqual(params["source"], "test")
        self.assertEqual(params["aliases"], ["alias1", "alias2"])


class TestGraphRelationship(unittest.TestCase):
    """Tests for the GraphRelationship class."""
    
    def test_init(self):
        """Test initialization of GraphRelationship."""
        # Create GraphRelationship instance
        relationship = GraphRelationship(
            id="test-rel",
            type="TEST_RELATION",
            source_id="source-entity",
            target_id="target-entity",
            properties={"weight": 0.8, "label": "Test Relation"},
            confidence=0.9,
            source="test",
            bidirectional=True
        )
        
        # Check if attributes were set correctly
        self.assertEqual(relationship.id, "test-rel")
        self.assertEqual(relationship.type, "TEST_RELATION")
        self.assertEqual(relationship.source_id, "source-entity")
        self.assertEqual(relationship.target_id, "target-entity")
        self.assertEqual(relationship.properties, {"weight": 0.8, "label": "Test Relation"})
        self.assertEqual(relationship.confidence, 0.9)
        self.assertEqual(relationship.source, "test")
        self.assertTrue(relationship.bidirectional)
        self.assertIsInstance(relationship.created_at, datetime)
        self.assertIsInstance(relationship.updated_at, datetime)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        # Create GraphRelationship instance
        relationship = GraphRelationship(
            id="test-rel",
            type="TEST_RELATION",
            source_id="source-entity",
            target_id="target-entity",
            properties={"weight": 0.8, "label": "Test Relation"},
            confidence=0.9,
            source="test",
            bidirectional=True
        )
        
        # Convert to dictionary
        relationship_dict = relationship.to_dict()
        
        # Check if dictionary contains the correct values
        self.assertEqual(relationship_dict["id"], "test-rel")
        self.assertEqual(relationship_dict["type"], "TEST_RELATION")
        self.assertEqual(relationship_dict["source_id"], "source-entity")
        self.assertEqual(relationship_dict["target_id"], "target-entity")
        self.assertEqual(relationship_dict["properties"], {"weight": 0.8, "label": "Test Relation"})
        self.assertEqual(relationship_dict["confidence"], 0.9)
        self.assertEqual(relationship_dict["source"], "test")
        self.assertTrue(relationship_dict["bidirectional"])
        self.assertIsInstance(relationship_dict["created_at"], str)
        self.assertIsInstance(relationship_dict["updated_at"], str)
    
    def test_to_json(self):
        """Test conversion to JSON."""
        # Create GraphRelationship instance
        relationship = GraphRelationship(
            id="test-rel",
            type="TEST_RELATION",
            source_id="source-entity",
            target_id="target-entity",
            properties={"weight": 0.8, "label": "Test Relation"},
            confidence=0.9,
            source="test"
        )
        
        # Convert to JSON
        relationship_json = relationship.to_json()
        
        # Check if JSON can be parsed back to dictionary
        relationship_dict = json.loads(relationship_json)
        self.assertEqual(relationship_dict["id"], "test-rel")
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        # Create dictionary
        relationship_dict = {
            "id": "test-rel",
            "type": "TEST_RELATION",
            "source_id": "source-entity",
            "target_id": "target-entity",
            "properties": {"weight": 0.8, "label": "Test Relation"},
            "confidence": 0.9,
            "source": "test",
            "bidirectional": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Create GraphRelationship from dictionary
        relationship = GraphRelationship.from_dict(relationship_dict)
        
        # Check if attributes were set correctly
        self.assertEqual(relationship.id, "test-rel")
        self.assertEqual(relationship.type, "TEST_RELATION")
        self.assertEqual(relationship.source_id, "source-entity")
        self.assertEqual(relationship.target_id, "target-entity")
        self.assertEqual(relationship.properties, {"weight": 0.8, "label": "Test Relation"})
        self.assertEqual(relationship.confidence, 0.9)
        self.assertEqual(relationship.source, "test")
        self.assertTrue(relationship.bidirectional)
        self.assertIsInstance(relationship.created_at, datetime)
        self.assertIsInstance(relationship.updated_at, datetime)
    
    def test_update(self):
        """Test updating relationship properties."""
        # Create GraphRelationship instance
        relationship = GraphRelationship(
            id="test-rel",
            type="TEST_RELATION",
            source_id="source-entity",
            target_id="target-entity",
            properties={"weight": 0.8},
            confidence=0.9
        )
        
        # Initial values
        initial_created_at = relationship.created_at
        initial_updated_at = relationship.updated_at
        
        # Wait a moment to ensure updated_at will be different
        import time
        time.sleep(0.001)
        
        # Update properties
        relationship.update({
            "type": "UPDATED_RELATION",
            "properties": {"label": "Updated Relation"},
            "confidence": 0.95,
            "source": "updated",
            "bidirectional": True
        })
        
        # Check if attributes were updated correctly
        self.assertEqual(relationship.id, "test-rel")  # ID should not change
        self.assertEqual(relationship.type, "UPDATED_RELATION")
        self.assertEqual(relationship.properties, {"weight": 0.8, "label": "Updated Relation"})
        self.assertEqual(relationship.confidence, 0.95)
        self.assertEqual(relationship.source, "updated")
        self.assertTrue(relationship.bidirectional)
        self.assertEqual(relationship.created_at, initial_created_at)  # created_at should not change
        self.assertNotEqual(relationship.updated_at, initial_updated_at)  # updated_at should change
    
    def test_to_cypher_params(self):
        """Test conversion to Cypher parameters."""
        # Create GraphRelationship instance
        relationship = GraphRelationship(
            id="test-rel",
            type="TEST_RELATION",
            source_id="source-entity",
            target_id="target-entity",
            properties={"weight": 0.8, "label": "Test Relation"},
            confidence=0.9,
            source="test",
            bidirectional=True
        )
        
        # Convert to Cypher parameters
        params = relationship.to_cypher_params()
        
        # Check if parameters contain the correct values
        self.assertEqual(params["id"], "test-rel")
        self.assertEqual(params["source_id"], "source-entity")
        self.assertEqual(params["target_id"], "target-entity")
        self.assertEqual(params["weight"], 0.8)
        self.assertEqual(params["label"], "Test Relation")
        self.assertEqual(params["confidence"], 0.9)
        self.assertEqual(params["source"], "test")
        self.assertTrue(params["bidirectional"])
        self.assertIsInstance(params["created_at"], str)
        self.assertIsInstance(params["updated_at"], str)
    
    def test_get_cypher_create(self):
        """Test generating Cypher query for relationship creation."""
        # Create GraphRelationship instance
        relationship = GraphRelationship(
            id="test-rel",
            type="TEST_RELATION",
            source_id="source-entity",
            target_id="target-entity",
            properties={"weight": 0.8, "label": "Test Relation"},
            confidence=0.9,
            source="test"
        )
        
        # Generate Cypher query
        query, params = relationship.get_cypher_create()
        
        # Check if query and parameters are correct
        self.assertIn("MATCH (source), (target)", query)
        self.assertIn("WHERE source.id = $source_id AND target.id = $target_id", query)
        self.assertIn("CREATE (source)-[r:TEST_RELATION", query)
        self.assertIn("id: $id", query)
        self.assertIn("created_at: $created_at", query)
        self.assertIn("updated_at: $updated_at", query)
        self.assertIn("confidence: $confidence", query)
        self.assertIn("source: $source", query)
        self.assertIn("weight: $weight", query)
        self.assertIn("label: $label", query)
        self.assertEqual(params["id"], "test-rel")
        self.assertEqual(params["source_id"], "source-entity")
        self.assertEqual(params["target_id"], "target-entity")
        self.assertEqual(params["weight"], 0.8)
        self.assertEqual(params["label"], "Test Relation")
        self.assertEqual(params["confidence"], 0.9)
        self.assertEqual(params["source"], "test")


if __name__ == '__main__':
    unittest.main()