"""
Property-based tests for the knowledge graph creation and manipulation.

This module contains property-based tests using hypothesis to validate
that the knowledge graph creation and manipulation functions maintain
invariants and properties across a wide range of inputs.
"""

import pytest
from hypothesis import given, strategies as st
import json

# Mark all tests in this module as property tests and knowledge graph related tests
pytestmark = [
    pytest.mark.property,
    pytest.mark.knowledge_graph,
    pytest.mark.medium
]

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity, EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship, RelationType
from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor


# Helper strategy for generating entities
def entity_strategy():
    """Generate a random entity."""
    return st.builds(
        Entity,
        text=st.text(min_size=1, max_size=50),
        type=st.sampled_from(list(EntityType)),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        start_pos=st.integers(min_value=0, max_value=100),
        end_pos=st.integers(min_value=101, max_value=200),  # Ensure end_pos > start_pos
        metadata=st.fixed_dictionaries({}),
        id=st.text(min_size=1, max_size=20)
    )


# Strategy for generating a list of entities with unique IDs
def unique_entities_strategy():
    """Generate a list of entities with unique IDs."""
    return st.lists(
        entity_strategy(),
        min_size=1,
        max_size=10,
        unique_by=lambda e: e.id
    )


# Strategy for generating a list of relationships
def relationships_strategy(entities):
    """Generate a list of relationships from the given entities."""
    if len(entities) < 2:
        return st.just([])  # Can't create relationships with less than 2 entities
    
    return st.lists(
        st.builds(
            Relationship,
            source=st.sampled_from(entities),
            target=st.sampled_from(entities),
            relation_type=st.sampled_from(list(RelationType)),
            confidence=st.floats(min_value=0.0, max_value=1.0),
            context=st.text(min_size=0, max_size=200),
            metadata=st.fixed_dictionaries({}),
            id=st.text(min_size=1, max_size=20).filter(lambda id_: id_ not in [e.id for e in entities])
        ).filter(lambda r: r.source.id != r.target.id),  # Ensure source and target are different
        min_size=0,
        max_size=min(20, len(entities) * (len(entities) - 1)),  # Upper bound on number of relationships
        unique_by=lambda r: r.id
    )


class TestKnowledgeGraphProperties:
    """Property-based tests for knowledge graph creation and manipulation."""

    @given(
        entities=unique_entities_strategy(),
        doc_id=st.text(min_size=1, max_size=20)
    )
    def test_create_knowledge_graph_nodes(self, entities, doc_id):
        """Test that _create_knowledge_graph correctly creates nodes from entities."""
        # Create a KnowledgeExtractor
        extractor = KnowledgeExtractor(
            document_processor=None,
            entity_recognizer=None,
            relationship_extractor=None
        )
        
        # Create a knowledge graph with only entities (no relationships)
        graph = extractor._create_knowledge_graph(entities, [], doc_id)
        
        # Check that the graph has the correct structure
        assert "nodes" in graph
        assert "edges" in graph
        assert "metadata" in graph
        
        # Check that metadata contains the document ID
        assert "document_id" in graph["metadata"]
        assert graph["metadata"]["document_id"] == doc_id
        
        # Check that there's a node for each entity
        assert len(graph["nodes"]) == len(entities)
        
        # Check that each node has the correct properties
        for entity in entities:
            assert entity.id in graph["nodes"]
            node = graph["nodes"][entity.id]
            assert node["id"] == entity.id
            assert node["text"] == entity.text
            assert node["type"] == entity.type.value
            assert node["confidence"] == entity.confidence
    
    @given(
        entities=unique_entities_strategy()
    )
    def test_create_knowledge_graph_with_relationships(self, entities):
        """Test that _create_knowledge_graph correctly creates nodes and edges."""
        if len(entities) < 2:
            pytest.skip("Need at least 2 entities to create relationships")
            
        # Create a list of relationships between entities
        relationships = relationships_strategy(entities).example()
        
        # Create a KnowledgeExtractor
        extractor = KnowledgeExtractor(
            document_processor=None,
            entity_recognizer=None,
            relationship_extractor=None
        )
        
        # Create a knowledge graph
        doc_id = "test_doc"
        graph = extractor._create_knowledge_graph(entities, relationships, doc_id)
        
        # Check that the graph has the correct structure
        assert "nodes" in graph
        assert "edges" in graph
        assert "metadata" in graph
        
        # Check that there's a node for each entity
        assert len(graph["nodes"]) == len(entities)
        
        # Check that there's an edge for each relationship
        assert len(graph["edges"]) == len(relationships)
        
        # Check that each edge has the correct properties
        for relationship in relationships:
            assert relationship.id in graph["edges"]
            edge = graph["edges"][relationship.id]
            assert edge["id"] == relationship.id
            assert edge["source"] == relationship.source.id
            assert edge["target"] == relationship.target.id
            assert edge["type"] == relationship.relation_type.value
            assert edge["confidence"] == relationship.confidence
    
    @given(
        entities=unique_entities_strategy(),
        doc_id=st.text(min_size=1, max_size=20)
    )
    def test_knowledge_graph_json_serialization(self, entities, doc_id):
        """Test that knowledge graphs can be serialized to JSON and back."""
        if len(entities) < 2:
            pytest.skip("Need at least 2 entities to create relationships")
            
        # Create a list of relationships between entities
        relationships = relationships_strategy(entities).example()
        
        # Create a KnowledgeExtractor
        extractor = KnowledgeExtractor(
            document_processor=None,
            entity_recognizer=None,
            relationship_extractor=None
        )
        
        # Create a knowledge graph
        graph = extractor._create_knowledge_graph(entities, relationships, doc_id)
        
        # Convert to JSON
        graph_json = json.dumps(graph)
        
        # Convert back from JSON
        graph2 = json.loads(graph_json)
        
        # Check that the graph has the same structure after JSON round trip
        assert graph2["nodes"] == graph["nodes"]
        assert graph2["edges"] == graph["edges"]
        assert graph2["metadata"] == graph["metadata"]
    
    @given(
        entities=unique_entities_strategy()
    )
    def test_get_extraction_statistics(self, entities):
        """Test that get_extraction_statistics correctly computes statistics."""
        if len(entities) < 2:
            pytest.skip("Need at least 2 entities to create relationships")
            
        # Create a list of relationships between entities
        relationships = relationships_strategy(entities).example()
        
        # Create a KnowledgeExtractor
        extractor = KnowledgeExtractor(
            document_processor=None,
            entity_recognizer=None,
            relationship_extractor=None
        )
        
        # Add data to the extractor
        doc_id = "test_doc"
        extractor.entities[doc_id] = entities
        extractor.relationships[doc_id] = relationships
        extractor.knowledge_graph[doc_id] = extractor._create_knowledge_graph(entities, relationships, doc_id)
        
        # Mock document
        from unittest.mock import Mock
        mock_doc = Mock()
        mock_doc.document_type = "text"
        extractor.documents[doc_id] = mock_doc
        
        # Get statistics
        stats = extractor.get_extraction_statistics()
        
        # Check that statistics has the correct structure
        assert "documents" in stats
        assert "count" in stats["documents"]
        assert stats["documents"]["count"] == 1
        
        assert "entities" in stats
        assert "count" in stats["entities"]
        assert stats["entities"]["count"] == len(entities)
        assert "by_type" in stats["entities"]
        
        assert "relationships" in stats
        assert "count" in stats["relationships"]
        assert stats["relationships"]["count"] == len(relationships)
        assert "by_type" in stats["relationships"]
        
        assert "knowledge_graph" in stats
        assert "total_nodes" in stats["knowledge_graph"]
        assert stats["knowledge_graph"]["total_nodes"] == len(entities)
        assert "total_edges" in stats["knowledge_graph"]
        assert stats["knowledge_graph"]["total_edges"] == len(relationships)
        
        # Check entity type statistics
        entity_type_counts = {}
        for entity in entities:
            entity_type = entity.type.value
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        for entity_type, count in entity_type_counts.items():
            assert entity_type in stats["entities"]["by_type"]
            assert stats["entities"]["by_type"][entity_type] == count
        
        # Check relationship type statistics
        relationship_type_counts = {}
        for relationship in relationships:
            relationship_type = relationship.relation_type.value
            relationship_type_counts[relationship_type] = relationship_type_counts.get(relationship_type, 0) + 1
        
        for relationship_type, count in relationship_type_counts.items():
            assert relationship_type in stats["relationships"]["by_type"]
            assert stats["relationships"]["by_type"][relationship_type] == count