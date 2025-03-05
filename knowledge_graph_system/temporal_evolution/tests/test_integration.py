"""
Unit tests for the Knowledge Graph Integration module.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import os
import tempfile

from knowledge_graph_system.temporal_evolution.integration.knowledge_graph_integration import (
    TemporalKnowledgeGraphIntegrator
)
from knowledge_graph_system.core.models.base_models import GraphEntity, GraphRelationship
from knowledge_graph_system.temporal_evolution.models.temporal_base_models import (
    TemporalEntityBase, TemporalRelationshipBase
)


class TestTemporalKnowledgeGraphIntegrator(unittest.TestCase):
    """Tests for the TemporalKnowledgeGraphIntegrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects
        self.mock_kg_manager = MagicMock()
        self.mock_temporal_entity_manager = MagicMock()
        self.mock_temporal_query_engine = MagicMock()
        
        # Create the integrator
        self.integrator = TemporalKnowledgeGraphIntegrator(
            self.mock_kg_manager,
            self.mock_temporal_entity_manager,
            self.mock_temporal_query_engine
        )
        
        # Create sample entities and relationships
        now = datetime.now()
        
        # Core entities
        self.core_entity1 = GraphEntity(
            id="c1",
            name="GPT-3",
            entity_type="AIModel"
        )
        self.core_entity1.created_at = now - timedelta(days=500)
        
        self.core_entity2 = GraphEntity(
            id="c2",
            name="GPT-4",
            entity_type="AIModel"
        )
        self.core_entity2.created_at = now - timedelta(days=200)
        
        # Core relationship
        self.core_relationship = GraphRelationship(
            id="cr1",
            source_id="c1",
            target_id="c2",
            type="EVOLVED_INTO"
        )
        self.core_relationship.created_at = now - timedelta(days=200)
        
        # Temporal entities
        self.temporal_entity1 = TemporalEntityBase(
            id="t1",
            name="GPT-3",
            entity_type="AIModel",
            created_at=now - timedelta(days=500),
            updated_at=None,
            version_id="1.0",
            source_id="c1"  # Reference to core entity
        )
        
        self.temporal_entity2 = TemporalEntityBase(
            id="t2",
            name="GPT-4",
            entity_type="AIModel",
            created_at=now - timedelta(days=200),
            updated_at=None,
            version_id="1.0",
            source_id="c2"  # Reference to core entity
        )
        
        # Temporal relationship
        self.temporal_relationship = TemporalRelationshipBase(
            id="tr1",
            source_id="t1",
            target_id="t2",
            type="EVOLVED_INTO",
            created_at=now - timedelta(days=200),
            valid_from=now - timedelta(days=200),
            valid_to=None
        )
        
        # Set up entity ID mapping
        self.integrator.entity_id_mapping = {
            "c1": "t1", "t1": "c1",
            "c2": "t2", "t2": "c2"
        }
    
    def test_convert_to_temporal_entity(self):
        """Test converting a core entity to a temporal entity."""
        # Call the method
        temporal_entity = self.integrator._convert_to_temporal_entity(self.core_entity1)
        
        # Check the result
        self.assertIsInstance(temporal_entity, TemporalEntityBase)
        self.assertEqual(temporal_entity.name, "GPT-3")
        self.assertEqual(temporal_entity.entity_type, "AIModel")
        self.assertEqual(temporal_entity.source_id, "c1")
        self.assertEqual(temporal_entity.version_id, "1.0")
    
    def test_convert_to_temporal_relationship(self):
        """Test converting a core relationship to a temporal relationship."""
        # Call the method
        temporal_relationship = self.integrator._convert_to_temporal_relationship(self.core_relationship)
        
        # Check the result
        self.assertIsInstance(temporal_relationship, TemporalRelationshipBase)
        self.assertEqual(temporal_relationship.source_id, "t1")
        self.assertEqual(temporal_relationship.target_id, "t2")
        self.assertEqual(temporal_relationship.type, "EVOLVED_INTO")
    
    def test_convert_to_core_entity(self):
        """Test converting a temporal entity to a core entity."""
        # Call the method
        core_entity = self.integrator._convert_to_core_entity(self.temporal_entity1)
        
        # Check the result
        self.assertIsInstance(core_entity, GraphEntity)
        self.assertEqual(core_entity.name, "GPT-3")
        self.assertEqual(core_entity.entity_type, "AIModel")
        self.assertEqual(getattr(core_entity, "_temp_id", None), "t1")
    
    def test_convert_to_core_relationship(self):
        """Test converting a temporal relationship to a core relationship."""
        # Call the method
        core_relationship = self.integrator._convert_to_core_relationship(self.temporal_relationship)
        
        # Check the result
        self.assertIsInstance(core_relationship, GraphRelationship)
        self.assertEqual(core_relationship.source_id, "c1")
        self.assertEqual(core_relationship.target_id, "c2")
        self.assertEqual(core_relationship.type, "EVOLVED_INTO")
    
    def test_import_from_knowledge_graph(self):
        """Test importing entities and relationships from the core knowledge graph."""
        # Mock query_entities and query_relationships
        self.mock_kg_manager.query_entities.return_value = [self.core_entity1, self.core_entity2]
        self.mock_kg_manager.query_relationships.return_value = [self.core_relationship]
        
        # Mock create_temporal_entity and create_temporal_relationship
        self.mock_temporal_entity_manager.create_temporal_entity.return_value = "t1"
        self.mock_temporal_entity_manager.create_temporal_relationship.return_value = "tr1"
        
        # Call import_from_knowledge_graph
        entity_count, relationship_count = self.integrator.import_from_knowledge_graph(
            entity_types=["AIModel"]
        )
        
        # Check the result
        self.assertEqual(entity_count, 2)  # Should import 2 entities
        self.assertEqual(relationship_count, 1)  # Should import 1 relationship
    
    def test_export_to_knowledge_graph(self):
        """Test exporting entities and relationships to the core knowledge graph."""
        # Mock query_entities and query_relationships
        self.mock_temporal_query_engine.query_entities.return_value = [self.temporal_entity1, self.temporal_entity2]
        self.mock_temporal_query_engine.query_relationships.return_value = [self.temporal_relationship]
        
        # Mock add_entity and add_relationship
        self.mock_kg_manager.add_entity.return_value = "c1"
        self.mock_kg_manager.add_relationship.return_value = "cr1"
        
        # Call export_to_knowledge_graph
        entity_count, relationship_count = self.integrator.export_to_knowledge_graph()
        
        # Check the result
        self.assertEqual(entity_count, 2)  # Should export 2 entities
        self.assertEqual(relationship_count, 1)  # Should export 1 relationship
    
    def test_create_evolution_relationship(self):
        """Test creating an evolution relationship."""
        # Mock get_entity_by_id to return entities
        self.mock_temporal_query_engine.get_entity_by_id.side_effect = lambda id: {
            "t1": self.temporal_entity1,
            "t2": self.temporal_entity2
        }.get(id)
        
        # Mock create_temporal_relationship and add_relationship
        self.mock_temporal_entity_manager.create_temporal_relationship.return_value = "tr1"
        self.mock_kg_manager.add_relationship.return_value = "cr1"
        
        # Call create_evolution_relationship
        rel_id = self.integrator.create_evolution_relationship(
            source_id="t1",
            target_id="t2",
            relationship_type="EVOLVED_INTO"
        )
        
        # Check the result
        self.assertEqual(rel_id, "tr1")
        self.mock_temporal_entity_manager.create_temporal_relationship.assert_called_once()
        self.mock_kg_manager.add_relationship.assert_called_once()
    
    def test_save_and_load_entity_id_mapping(self):
        """Test saving and loading entity ID mapping."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Save the mapping
            self.integrator.save_entity_id_mapping(temp_path)
            
            # Create a new integrator with empty mapping
            new_integrator = TemporalKnowledgeGraphIntegrator(
                self.mock_kg_manager,
                self.mock_temporal_entity_manager,
                self.mock_temporal_query_engine
            )
            
            # Load the mapping
            new_integrator.load_entity_id_mapping(temp_path)
            
            # Check that the mapping was loaded correctly
            self.assertEqual(new_integrator.entity_id_mapping, self.integrator.entity_id_mapping)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_synchronize(self):
        """Test synchronizing data between core and temporal layers."""
        # Mock import_from_knowledge_graph and export_to_knowledge_graph
        self.integrator.import_from_knowledge_graph = MagicMock(return_value=(2, 1))
        self.integrator.export_to_knowledge_graph = MagicMock(return_value=(2, 1))
        
        # Call synchronize
        stats = self.integrator.synchronize(entity_types=["AIModel"], bidirectional=True)
        
        # Check the result
        self.assertEqual(stats["imported_entities"], 2)
        self.assertEqual(stats["imported_relationships"], 1)
        self.assertEqual(stats["exported_entities"], 2)
        self.assertEqual(stats["exported_relationships"], 1)
        
        # Check that both methods were called
        self.integrator.import_from_knowledge_graph.assert_called_once()
        self.integrator.export_to_knowledge_graph.assert_called_once()


if __name__ == '__main__':
    unittest.main()