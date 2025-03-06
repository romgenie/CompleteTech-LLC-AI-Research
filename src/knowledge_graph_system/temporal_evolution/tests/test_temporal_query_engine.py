"""
Unit tests for the Temporal Query Engine module.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from src.knowledge_graph_system.temporal_evolution.query_engine.temporal_query_engine import (
    TemporalQueryEngine
)
from src.knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)


class TestTemporalQueryEngine(unittest.TestCase):
    """Tests for the TemporalQueryEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database connector
        self.mock_db = MagicMock()
        
        # Create the query engine
        self.query_engine = TemporalQueryEngine(self.mock_db)
        
        # Create some test entities
        now = datetime.now()
        self.entity1 = TemporalEntityBase(
            id="1",
            name="GPT-3",
            entity_type="AIModel",
            created_at=now - timedelta(days=500),
            updated_at=now - timedelta(days=100),
            version_id="1.0"
        )
        self.entity2 = TemporalEntityBase(
            id="2",
            name="GPT-4",
            entity_type="AIModel",
            created_at=now - timedelta(days=200),
            updated_at=now - timedelta(days=50),
            version_id="1.0"
        )
        self.entity3 = TemporalEntityBase(
            id="3",
            name="DALL-E",
            entity_type="AIModel",
            created_at=now - timedelta(days=300),
            updated_at=None,
            version_id="1.0"
        )
        
        # Create some test relationships
        self.rel1 = TemporalRelationshipBase(
            id="r1",
            source_id="1",
            target_id="2",
            type="EVOLVED_INTO",
            created_at=now - timedelta(days=200)
        )
        self.rel2 = TemporalRelationshipBase(
            id="r2",
            source_id="1",
            target_id="3",
            type="INSPIRED",
            created_at=now - timedelta(days=300)
        )
    
    def test_get_entity_by_id(self):
        """Test getting an entity by ID."""
        # Mock the database response
        self.mock_db.get_entity_by_id.return_value = self.entity1
        
        # Get the entity
        entity = self.query_engine.get_entity_by_id("1")
        
        # Check the result
        self.assertEqual(entity, self.entity1)
        self.mock_db.get_entity_by_id.assert_called_once_with("1")
    
    def test_query_entities_no_params(self):
        """Test querying entities with no parameters."""
        # Mock the database response
        self.mock_db.query_entities.return_value = [self.entity1, self.entity2, self.entity3]
        
        # Query entities
        entities = self.query_engine.query_entities()
        
        # Check the result
        self.assertEqual(len(entities), 3)
        self.mock_db.query_entities.assert_called_once()
    
    def test_query_entities_with_filters(self):
        """Test querying entities with filters."""
        # Mock the database response
        self.mock_db.query_entities.return_value = [self.entity1, self.entity2]
        
        # Query entities with filters
        entity_types = ["AIModel"]
        keywords = ["GPT"]
        time_window = (datetime.now() - timedelta(days=600), datetime.now())
        
        entities = self.query_engine.query_entities(
            entity_types=entity_types,
            keywords=keywords,
            time_window=time_window
        )
        
        # Check the result
        self.assertEqual(len(entities), 2)
        self.mock_db.query_entities.assert_called_once()
        
        # Check that filters were passed correctly
        call_args = self.mock_db.query_entities.call_args[1]
        self.assertEqual(call_args.get("entity_types"), entity_types)
        self.assertEqual(call_args.get("keywords"), keywords)
        self.assertEqual(call_args.get("time_window"), time_window)
    
    def test_query_relationships_no_params(self):
        """Test querying relationships with no parameters."""
        # Mock the database response
        self.mock_db.query_relationships.return_value = [self.rel1, self.rel2]
        
        # Query relationships
        relationships = self.query_engine.query_relationships()
        
        # Check the result
        self.assertEqual(len(relationships), 2)
        self.mock_db.query_relationships.assert_called_once()
    
    def test_query_relationships_with_filters(self):
        """Test querying relationships with filters."""
        # Mock the database response
        self.mock_db.query_relationships.return_value = [self.rel1]
        
        # Query relationships with filters
        relationship_types = ["EVOLVED_INTO"]
        source_ids = ["1"]
        target_ids = ["2"]
        time_window = (datetime.now() - timedelta(days=300), datetime.now())
        
        relationships = self.query_engine.query_relationships(
            relationship_types=relationship_types,
            source_ids=source_ids,
            target_ids=target_ids,
            time_window=time_window
        )
        
        # Check the result
        self.assertEqual(len(relationships), 1)
        self.mock_db.query_relationships.assert_called_once()
        
        # Check that filters were passed correctly
        call_args = self.mock_db.query_relationships.call_args[1]
        self.assertEqual(call_args.get("relationship_types"), relationship_types)
        self.assertEqual(call_args.get("source_ids"), source_ids)
        self.assertEqual(call_args.get("target_ids"), target_ids)
        self.assertEqual(call_args.get("time_window"), time_window)
    
    def test_trace_concept_evolution(self):
        """Test tracing concept evolution."""
        # Mock get_next_versions
        self.query_engine.get_next_versions = MagicMock()
        self.query_engine.get_next_versions.side_effect = [
            [self.entity2],  # For entity1
            [],              # For entity2
        ]
        
        # Trace concept evolution
        evolution_tree = self.query_engine.trace_concept_evolution("1", max_depth=2)
        
        # Check the result
        self.assertIn("1", evolution_tree)
        self.assertIn("2", evolution_tree.get("1", []))
        self.assertEqual(len(evolution_tree.get("2", [])), 0)
    
    def test_get_previous_versions(self):
        """Test getting previous versions of an entity."""
        # Mock the database response for querying relationships
        self.mock_db.query_relationships.return_value = [self.rel1]  # 1 EVOLVED_INTO 2
        
        # Mock get_entity_by_id to return the source entity
        self.query_engine.get_entity_by_id = MagicMock()
        self.query_engine.get_entity_by_id.return_value = self.entity1
        
        # Get previous versions of entity2
        previous_versions = self.query_engine.get_previous_versions("2")
        
        # Check the result
        self.assertEqual(len(previous_versions), 1)
        self.assertEqual(previous_versions[0], self.entity1)
    
    def test_get_next_versions(self):
        """Test getting next versions of an entity."""
        # Mock the database response for querying relationships
        self.mock_db.query_relationships.return_value = [self.rel1]  # 1 EVOLVED_INTO 2
        
        # Mock get_entity_by_id to return the target entity
        self.query_engine.get_entity_by_id = MagicMock()
        self.query_engine.get_entity_by_id.return_value = self.entity2
        
        # Get next versions of entity1
        next_versions = self.query_engine.get_next_versions("1")
        
        # Check the result
        self.assertEqual(len(next_versions), 1)
        self.assertEqual(next_versions[0], self.entity2)
    
    def test_get_snapshot(self):
        """Test getting a snapshot of the knowledge graph at a point in time."""
        # Mock the database responses
        self.mock_db.query_entities.return_value = [self.entity1, self.entity3]
        self.mock_db.query_relationships.return_value = [self.rel2]
        
        # Get a snapshot
        snapshot_date = datetime.now() - timedelta(days=250)
        snapshot = self.query_engine.get_snapshot(snapshot_date)
        
        # Check the result
        self.assertIn("entities", snapshot)
        self.assertIn("relationships", snapshot)
        self.assertEqual(len(snapshot["entities"]), 2)
        self.assertEqual(len(snapshot["relationships"]), 1)
    
    def test_find_temporal_paths(self):
        """Test finding temporal paths between entities."""
        # This is a more complex test that would require multiple relationships
        # Mock the graph building and path finding
        with patch('networkx.MultiDiGraph'), patch('networkx.all_simple_paths'):
            # Just test that the method runs without errors
            paths = self.query_engine.find_temporal_paths(
                start_id="1",
                end_id="3",
                max_hops=2
            )
            
            # Check that the result is a list
            self.assertIsInstance(paths, list)


if __name__ == '__main__':
    unittest.main()