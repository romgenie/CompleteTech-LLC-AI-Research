"""
Tests for the KnowledgeGraphAdapter in the Knowledge Integration module.

This module contains tests for the KnowledgeGraphAdapter, which integrates
the Knowledge Extraction Pipeline with the Knowledge Graph System.
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from research_orchestrator.knowledge_integration.knowledge_graph_adapter import KnowledgeGraphAdapter
from research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType


class TestKnowledgeGraphAdapter:
    """Tests for the KnowledgeGraphAdapter class."""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for local storage tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_entities(self):
        """Create a list of mock entities for testing."""
        return [
            Entity(
                id="entity1",
                text="GPT-4",
                type=EntityType.AI_MODEL,
                confidence=0.95,
                metadata={
                    "organization": "OpenAI",
                    "model_type": "language",
                    "architecture": "Transformer",
                    "parameters": "1.8 trillion"
                }
            ),
            Entity(
                id="entity2",
                text="ImageNet",
                type=EntityType.DATASET,
                confidence=0.9,
                metadata={
                    "domain": "computer vision",
                    "size": "14 million images"
                }
            )
        ]
    
    @pytest.fixture
    def mock_relationships(self, mock_entities):
        """Create a list of mock relationships for testing."""
        return [
            Relationship(
                id="rel1",
                source_entity=mock_entities[0],
                target_entity=mock_entities[1],
                relation_type=RelationType.TRAINED_ON,
                confidence=0.85,
                metadata={
                    "version": "v1",
                    "date": "2022-01-01"
                }
            )
        ]
    
    def test_init_local_storage(self, temp_storage_dir):
        """Test initialization with local storage."""
        with patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', False):
            adapter = KnowledgeGraphAdapter(local_storage_path=temp_storage_dir)
            
            assert adapter.using_local_storage is True
            assert os.path.exists(os.path.join(temp_storage_dir, "entities"))
            assert os.path.exists(os.path.join(temp_storage_dir, "relationships"))
            assert os.path.exists(os.path.join(temp_storage_dir, "connections"))
    
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', True)
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.Neo4jManager')
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KnowledgeGraphManager')
    def test_init_knowledge_graph_system(self, mock_kg_manager, mock_neo4j_manager, temp_storage_dir):
        """Test initialization with Knowledge Graph System."""
        # Mock Neo4jManager.from_env to return a MagicMock
        mock_neo4j_manager.from_env.return_value = MagicMock()
        
        # Create a mock KnowledgeGraphManager instance
        mock_kg_manager_instance = MagicMock()
        mock_kg_manager.return_value = mock_kg_manager_instance
        
        adapter = KnowledgeGraphAdapter()
        
        assert adapter.using_local_storage is False
        assert adapter.kg_manager == mock_kg_manager_instance
        mock_neo4j_manager.from_env.assert_called_once()
    
    def test_integrate_extracted_knowledge_local_storage(self, temp_storage_dir, mock_entities, mock_relationships):
        """Test integrating extracted knowledge with local storage."""
        with patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', False):
            adapter = KnowledgeGraphAdapter(local_storage_path=temp_storage_dir)
            
            result = adapter.integrate_extracted_knowledge(mock_entities, mock_relationships)
            
            assert result["integrated_entities"] == len(mock_entities)
            assert result["integrated_relationships"] == len(mock_relationships)
            assert len(result["failed_entities"]) == 0
            assert len(result["failed_relationships"]) == 0
            
            # Check that files were created
            entities_dir = os.path.join(temp_storage_dir, "entities")
            relationships_dir = os.path.join(temp_storage_dir, "relationships")
            
            assert len(os.listdir(entities_dir)) == len(mock_entities)
            assert len(os.listdir(relationships_dir)) == len(mock_relationships)
    
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', True)
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.Neo4jManager')
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KnowledgeGraphManager')
    def test_integrate_extracted_knowledge_kg_system(self, mock_kg_manager, mock_neo4j_manager, mock_entities, mock_relationships):
        """Test integrating extracted knowledge with Knowledge Graph System."""
        # Mock Neo4jManager.from_env to return a MagicMock
        mock_neo4j_manager.from_env.return_value = MagicMock()
        
        # Create a mock KnowledgeGraphManager instance
        mock_kg_manager_instance = MagicMock()
        mock_kg_manager_instance.add_entity.return_value = {"success": True}
        mock_kg_manager_instance.add_relationship.return_value = {"success": True}
        mock_kg_manager.return_value = mock_kg_manager_instance
        
        adapter = KnowledgeGraphAdapter()
        
        result = adapter.integrate_extracted_knowledge(mock_entities, mock_relationships)
        
        assert result["integrated_entities"] == len(mock_entities)
        assert result["integrated_relationships"] == len(mock_relationships)
        assert len(result["failed_entities"]) == 0
        assert len(result["failed_relationships"]) == 0
    
    def test_query_knowledge_graph_local_storage(self, temp_storage_dir, mock_entities, mock_relationships):
        """Test querying knowledge graph with local storage."""
        with patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', False):
            adapter = KnowledgeGraphAdapter(local_storage_path=temp_storage_dir)
            
            # First, integrate some knowledge
            adapter.integrate_extracted_knowledge(mock_entities, mock_relationships)
            
            # Then query for entities
            entity_query = {
                "query_type": "entity",
                "filters": {},
                "limit": 10
            }
            
            entity_results = adapter.query_knowledge_graph(entity_query)
            
            assert "results" in entity_results
            assert len(entity_results["results"]) == len(mock_entities)
            
            # Query for relationships
            relationship_query = {
                "query_type": "relationship",
                "filters": {},
                "limit": 10
            }
            
            relationship_results = adapter.query_knowledge_graph(relationship_query)
            
            assert "results" in relationship_results
            assert len(relationship_results["results"]) == len(mock_relationships)
    
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', True)
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.Neo4jManager')
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KnowledgeGraphManager')
    def test_query_knowledge_graph_kg_system(self, mock_kg_manager, mock_neo4j_manager):
        """Test querying knowledge graph with Knowledge Graph System."""
        # Mock Neo4jManager.from_env to return a MagicMock
        mock_neo4j_manager.from_env.return_value = MagicMock()
        
        # Create a mock KnowledgeGraphManager instance
        mock_kg_manager_instance = MagicMock()
        mock_kg_manager_instance.find_entities.return_value = {"results": [{"id": "entity1"}, {"id": "entity2"}]}
        mock_kg_manager_instance.find_relationships.return_value = {"results": [{"id": "rel1"}]}
        mock_kg_manager.return_value = mock_kg_manager_instance
        
        adapter = KnowledgeGraphAdapter()
        
        # Query for entities
        entity_query = {
            "query_type": "entity",
            "filters": {},
            "limit": 10
        }
        
        entity_results = adapter.query_knowledge_graph(entity_query)
        
        assert entity_results == {"results": [{"id": "entity1"}, {"id": "entity2"}]}
        mock_kg_manager_instance.find_entities.assert_called_once_with({}, 10)
        
        # Query for relationships
        relationship_query = {
            "query_type": "relationship",
            "filters": {},
            "limit": 10
        }
        
        relationship_results = adapter.query_knowledge_graph(relationship_query)
        
        assert relationship_results == {"results": [{"id": "rel1"}]}
        mock_kg_manager_instance.find_relationships.assert_called_once_with({}, 10)
    
    def test_get_statistics_local_storage(self, temp_storage_dir, mock_entities, mock_relationships):
        """Test getting statistics with local storage."""
        with patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', False):
            adapter = KnowledgeGraphAdapter(local_storage_path=temp_storage_dir)
            
            # First, integrate some knowledge
            adapter.integrate_extracted_knowledge(mock_entities, mock_relationships)
            
            # Then get statistics
            stats = adapter.get_statistics()
            
            assert stats["entity_count"] == len(mock_entities)
            assert stats["relationship_count"] == len(mock_relationships)
            assert stats["storage_type"] == "local"
    
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', True)
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.Neo4jManager')
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KnowledgeGraphManager')
    def test_get_statistics_kg_system(self, mock_kg_manager, mock_neo4j_manager):
        """Test getting statistics with Knowledge Graph System."""
        # Mock Neo4jManager.from_env to return a MagicMock
        mock_neo4j_manager.from_env.return_value = MagicMock()
        
        # Create a mock KnowledgeGraphManager instance
        mock_kg_manager_instance = MagicMock()
        mock_kg_manager_instance.get_statistics.return_value = {
            "entity_count": 2,
            "relationship_count": 1,
            "storage_type": "neo4j"
        }
        mock_kg_manager.return_value = mock_kg_manager_instance
        
        adapter = KnowledgeGraphAdapter()
        
        # Get statistics
        stats = adapter.get_statistics()
        
        assert stats == {
            "entity_count": 2,
            "relationship_count": 1,
            "storage_type": "neo4j"
        }
        mock_kg_manager_instance.get_statistics.assert_called_once()
    
    def test_clear_knowledge_store_local_storage(self, temp_storage_dir, mock_entities, mock_relationships):
        """Test clearing knowledge store with local storage."""
        with patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', False):
            adapter = KnowledgeGraphAdapter(local_storage_path=temp_storage_dir)
            
            # First, integrate some knowledge
            adapter.integrate_extracted_knowledge(mock_entities, mock_relationships)
            
            # Then clear the store
            result = adapter.clear_knowledge_store(confirm=True)
            
            assert result["success"] is True
            
            # Check that files were removed
            entities_dir = os.path.join(temp_storage_dir, "entities")
            relationships_dir = os.path.join(temp_storage_dir, "relationships")
            
            assert len(os.listdir(entities_dir)) == 0
            assert len(os.listdir(relationships_dir)) == 0
    
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', True)
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.Neo4jManager')
    @patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KnowledgeGraphManager')
    def test_clear_knowledge_store_kg_system(self, mock_kg_manager, mock_neo4j_manager):
        """Test clearing knowledge store with Knowledge Graph System."""
        # Mock Neo4jManager.from_env to return a MagicMock
        mock_neo4j_manager.from_env.return_value = MagicMock()
        
        # Create a mock KnowledgeGraphManager instance
        mock_kg_manager_instance = MagicMock()
        mock_kg_manager_instance.clear.return_value = {"success": True, "message": "Knowledge graph cleared"}
        mock_kg_manager.return_value = mock_kg_manager_instance
        
        adapter = KnowledgeGraphAdapter()
        
        # Clear the store
        result = adapter.clear_knowledge_store(confirm=True)
        
        assert result == {"success": True, "message": "Knowledge graph cleared"}
        mock_kg_manager_instance.clear.assert_called_once()
    
    def test_clear_knowledge_store_without_confirmation(self, temp_storage_dir):
        """Test that clearing knowledge store requires confirmation."""
        with patch('research_orchestrator.knowledge_integration.knowledge_graph_adapter.KNOWLEDGE_GRAPH_AVAILABLE', False):
            adapter = KnowledgeGraphAdapter(local_storage_path=temp_storage_dir)
            
            # Try to clear without confirmation
            result = adapter.clear_knowledge_store(confirm=False)
            
            assert result["success"] is False
            assert "Confirmation required" in result["error"]