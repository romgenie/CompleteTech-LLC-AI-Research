"""
Unit tests for the paper processing tasks.

This module tests the Celery tasks for paper processing.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime

from paper_processing.models.paper import Paper, PaperStatus
from paper_processing.tasks.processing_tasks import (
    process_paper,
    process_document,
    extract_entities,
    extract_relationships,
    build_knowledge_graph
)


@pytest.fixture
def sample_paper():
    """Create a sample paper for testing."""
    paper_id = str(uuid.uuid4())
    return Paper(
        id=paper_id,
        title="Test Paper",
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        content_type="application/pdf",
        original_filename="original_test.pdf",
        uploaded_by="test_user",
        uploaded_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_paper_model(sample_paper):
    """Create a mock PaperModel for testing."""
    mock_model = MagicMock()
    mock_model.to_domain.return_value = sample_paper
    
    # Mock the get_by_id class method
    with patch('paper_processing.db.models.PaperModel.get_by_id') as mock_get:
        mock_get.return_value = mock_model
        yield mock_model


def test_process_paper(mock_paper_model, sample_paper):
    """Test the process_paper task."""
    # Mock the chain
    with patch('paper_processing.tasks.processing_tasks.chain') as mock_chain:
        mock_chain_instance = MagicMock()
        mock_chain.return_value = mock_chain_instance
        
        # Call the task
        result = process_paper(sample_paper.id)
        
        # Check that the paper was retrieved
        assert mock_paper_model.to_domain.called
        
        # Check that the chain was created with the correct tasks
        mock_chain.assert_called_once()
        
        # Check chain delay was called
        assert mock_chain_instance.delay.called
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_process_document(mock_paper_model, sample_paper):
    """Test the process_document task."""
    # Mock the document processor
    document_processor_mock = MagicMock()
    processed_document = MagicMock()
    processed_document.content = "Processed content"
    processed_document.metadata = {
        "page_count": 5,
        "word_count": 1000,
        "char_count": 5000,
        "document_info": {
            "Title": "Updated Title",
            "Author": "Test Author",
            "Keywords": "test, paper",
            "CreationDate": "2023-01-01",
            "Subject": "Test Subject"
        }
    }
    processed_document.segments = [{"id": "page1", "content": "Page 1 content"}]
    processed_document.document_type = "pdf"
    processed_document.processed_at = datetime.utcnow().isoformat()
    
    document_processor_mock.process_document.return_value = processed_document
    
    # Mock the websocket manager
    manager_mock = MagicMock()
    
    with patch('research_orchestrator.knowledge_extraction.document_processing.document_processor.DocumentProcessor', 
               return_value=document_processor_mock) as mock_dp_class, \
         patch('paper_processing.websocket.connection.manager', manager_mock), \
         patch('paper_processing.websocket.events.create_paper_status_event') as mock_event_creator, \
         patch('asyncio.run') as mock_asyncio_run:
        
        # Configure event creator
        mock_event = MagicMock()
        mock_event_creator.return_value = mock_event
        
        # Call the task
        result = process_document(sample_paper.id)
        
        # Check that the document processor was created and called
        assert mock_dp_class.called
        assert document_processor_mock.process_document.called
        document_processor_mock.process_document.assert_called_with(sample_paper.file_path)
        
        # Check that the paper was updated with the document content
        assert mock_paper_model.update_from_domain.called
        updated_paper = mock_paper_model.update_from_domain.call_args[0][0]
        assert updated_paper.content == "Processed content"
        assert "document" in updated_paper.metadata
        assert updated_paper.metadata["document"]["document_type"] == "pdf"
        
        # Check that the paper was saved
        assert mock_paper_model.save.called
        
        # Check that a WebSocket event was created and broadcast
        assert mock_event_creator.called
        mock_event_creator.assert_called_with(
            paper_id=sample_paper.id,
            status=ANY,
            message="Document processed successfully",
            progress=30,
            metadata=ANY
        )
        
        # Check that asyncio.run was called to broadcast the event
        assert mock_asyncio_run.called
        mock_asyncio_run.assert_called_with(manager_mock.broadcast_to_paper(sample_paper.id, mock_event))
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_extract_entities(mock_paper_model, sample_paper):
    """Test the extract_entities task."""
    # Add content to the paper
    sample_paper.content = "This is a test paper about TestAlgorithm and TestDataset."
    mock_paper_model.to_domain.return_value = sample_paper
    
    # Mock the entity recognizer
    entity_recognizer_mock = MagicMock()
    extracted_entities = [
        MagicMock(entity_type="ALGORITHM", name="TestAlgorithm", confidence=0.9, context="context"),
        MagicMock(entity_type="DATASET", name="TestDataset", confidence=0.85, context="context")
    ]
    entity_recognizer_mock.extract_entities.return_value = extracted_entities
    
    # Mock the entity recognizer factory
    factory_mock = MagicMock()
    factory_mock.create_combined_recognizer.return_value = entity_recognizer_mock
    
    # Mock the websocket manager
    manager_mock = MagicMock()
    
    with patch('paper_processing.models.state_machine.PaperStateMachine') as mock_state_machine_cls, \
         patch('research_orchestrator.knowledge_extraction.entity_recognition.factory.EntityRecognizerFactory',
               return_value=factory_mock), \
         patch('paper_processing.websocket.connection.manager', manager_mock), \
         patch('paper_processing.websocket.events.create_paper_status_event') as mock_event_creator, \
         patch('asyncio.run') as mock_asyncio_run:
        
        # Configure state machine
        mock_state_machine = MagicMock()
        mock_state_machine_cls.return_value = mock_state_machine
        mock_state_machine.transition_to.return_value = sample_paper
        
        # Configure event creator
        mock_event = MagicMock()
        mock_event_creator.return_value = mock_event
        
        # Call the task
        result = extract_entities(sample_paper.id)
        
        # Check that the state machine transitions to EXTRACTING_ENTITIES
        mock_state_machine.transition_to.assert_called_with(
            PaperStatus.EXTRACTING_ENTITIES,
            "Starting entity extraction"
        )
        
        # Check that the entity recognizer was created and called
        assert factory_mock.create_combined_recognizer.called
        assert entity_recognizer_mock.extract_entities.called
        entity_recognizer_mock.extract_entities.assert_called_with(sample_paper.content)
        
        # Check that the paper was updated with the extracted entities
        assert mock_paper_model.update_from_domain.called
        updated_paper = mock_paper_model.update_from_domain.call_args[0][0]
        assert len(updated_paper.entities) == 2
        assert updated_paper.entities[0]["type"] == "algorithm"
        assert updated_paper.entities[1]["type"] == "dataset"
        
        # Check that the paper was saved
        assert mock_paper_model.save.called
        
        # Check that a WebSocket event was created and broadcast
        assert mock_event_creator.called
        mock_event_creator.assert_called_with(
            paper_id=sample_paper.id,
            status=ANY,
            message="Extracted 2 entities",
            progress=50,
            metadata=ANY
        )
        
        # Check that asyncio.run was called to broadcast the event
        assert mock_asyncio_run.called
        mock_asyncio_run.assert_called_with(manager_mock.broadcast_to_paper(sample_paper.id, mock_event))
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_extract_relationships(mock_paper_model, sample_paper):
    """Test the extract_relationships task."""
    # Add content and entities to the paper
    sample_paper.content = "This is a test paper about TestAlgorithm using TestDataset."
    sample_paper.entities = [
        {
            "id": "entity1",
            "type": "algorithm",
            "name": "TestAlgorithm",
            "confidence": 0.9,
            "context": "context"
        },
        {
            "id": "entity2",
            "type": "dataset",
            "name": "TestDataset",
            "confidence": 0.85,
            "context": "context"
        }
    ]
    mock_paper_model.to_domain.return_value = sample_paper
    
    # Mock the relationship extractor
    relationship_extractor_mock = MagicMock()
    
    # Mock extracted relationships
    source_entity_mock = MagicMock()
    target_entity_mock = MagicMock()
    extracted_relationship = MagicMock(
        source=source_entity_mock,
        target=target_entity_mock,
        relationship_type="USES",
        confidence=0.8,
        context="TestAlgorithm uses TestDataset"
    )
    relationship_extractor_mock.extract_relationships.return_value = [extracted_relationship]
    
    # Mock the relationship extractor factory
    factory_mock = MagicMock()
    factory_mock.create_combined_extractor.return_value = relationship_extractor_mock
    
    # Mock the websocket manager
    manager_mock = MagicMock()
    
    with patch('paper_processing.models.state_machine.PaperStateMachine') as mock_state_machine_cls, \
         patch('research_orchestrator.knowledge_extraction.relationship_extraction.factory.RelationshipExtractorFactory',
               return_value=factory_mock), \
         patch('research_orchestrator.knowledge_extraction.entity_recognition.entity.Entity') as mock_entity_cls, \
         patch('paper_processing.websocket.connection.manager', manager_mock), \
         patch('paper_processing.websocket.events.create_paper_status_event') as mock_event_creator, \
         patch('asyncio.run') as mock_asyncio_run:
        
        # Configure state machine
        mock_state_machine = MagicMock()
        mock_state_machine_cls.return_value = mock_state_machine
        mock_state_machine.transition_to.return_value = sample_paper
        
        # Configure entity mock to handle entity creation
        def create_entity(name, entity_type, confidence, context):
            mock_entity = MagicMock()
            # Store the values to allow checking
            mock_entity.name = name
            mock_entity.entity_type = entity_type
            mock_entity.confidence = confidence
            mock_entity.context = context
            return mock_entity
            
        mock_entity_cls.side_effect = create_entity
        
        # Configure event creator
        mock_event = MagicMock()
        mock_event_creator.return_value = mock_event
        
        # Call the task
        result = extract_relationships(sample_paper.id)
        
        # Check that the state machine transitions to EXTRACTING_RELATIONSHIPS
        mock_state_machine.transition_to.assert_called_with(
            PaperStatus.EXTRACTING_RELATIONSHIPS,
            "Starting relationship extraction"
        )
        
        # Check that the relationship extractor was created and called
        assert factory_mock.create_combined_extractor.called
        assert relationship_extractor_mock.extract_relationships.called
        
        # Check that the paper was updated with extracted relationships
        assert mock_paper_model.update_from_domain.called
        updated_paper = mock_paper_model.update_from_domain.call_args[0][0]
        
        # Check that the paper was saved
        assert mock_paper_model.save.called
        
        # Check that a WebSocket event was created and broadcast
        assert mock_event_creator.called
        
        # Check that asyncio.run was called to broadcast the event
        assert mock_asyncio_run.called
        
        # Check that the paper ID was returned
        assert result == sample_paper.id


def test_build_knowledge_graph(mock_paper_model, sample_paper):
    """Test the build_knowledge_graph task."""
    # Add entities and relationships to the paper
    sample_paper.entities = [
        {
            "id": "entity1",
            "type": "algorithm",
            "name": "TestAlgorithm",
            "confidence": 0.9,
            "context": "context"
        },
        {
            "id": "entity2",
            "type": "dataset",
            "name": "TestDataset",
            "confidence": 0.85,
            "context": "context"
        }
    ]
    sample_paper.relationships = [
        {
            "id": "rel1",
            "type": "uses",
            "source_id": "entity1",
            "target_id": "entity2",
            "confidence": 0.8,
            "context": "TestAlgorithm uses TestDataset"
        }
    ]
    mock_paper_model.to_domain.return_value = sample_paper
    
    # Mock the knowledge graph adapter
    kg_adapter_mock = MagicMock()
    kg_adapter_mock.add_paper_to_knowledge_graph.return_value = {
        "paper_id": "kg-123",
        "entity_count": 2,
        "relationship_count": 1,
        "status": "success"
    }
    kg_adapter_mock.add_paper_to_temporal_knowledge_graph.return_value = {
        "temporal_paper_id": "temporal-123",
        "entity_count": 2,
        "relationship_count": 1,
        "status": "success"
    }
    
    # Mock the Neo4j manager and Knowledge Graph manager
    neo4j_manager_mock = MagicMock()
    kg_manager_mock = MagicMock()
    
    # Mock the websocket manager
    manager_mock = MagicMock()
    
    with patch('paper_processing.models.state_machine.PaperStateMachine') as mock_state_machine_cls, \
         patch('paper_processing.integrations.knowledge_graph.KnowledgeGraphAdapter',
               return_value=kg_adapter_mock) as mock_adapter_cls, \
         patch('knowledge_graph_system.core.db.neo4j_manager.Neo4jManager',
               return_value=neo4j_manager_mock), \
         patch('knowledge_graph_system.core.knowledge_graph_manager.KnowledgeGraphManager',
               return_value=kg_manager_mock), \
         patch('paper_processing.config.settings.TEMPORAL_EVOLUTION_ENABLED', True), \
         patch('paper_processing.websocket.connection.manager', manager_mock), \
         patch('paper_processing.websocket.events.create_paper_status_event') as mock_event_creator, \
         patch('asyncio.run') as mock_asyncio_run:
        
        # Configure state machine
        mock_state_machine = MagicMock()
        mock_state_machine_cls.return_value = mock_state_machine
        # Mock transition_to to handle both transitions (to BUILDING_KNOWLEDGE_GRAPH and then to ANALYZED)
        mock_state_machine.transition_to.side_effect = [sample_paper, sample_paper]
        
        # Configure event creator
        mock_event = MagicMock()
        mock_event_creator.return_value = mock_event
        
        # Call the task
        result = build_knowledge_graph(sample_paper.id)
        
        # Check that the state machine transitions to BUILDING_KNOWLEDGE_GRAPH
        mock_state_machine.transition_to.assert_any_call(
            PaperStatus.BUILDING_KNOWLEDGE_GRAPH,
            "Starting knowledge graph integration"
        )
        
        # Check that the knowledge graph adapter was created
        assert mock_adapter_cls.called
        
        # Check that add_paper_to_knowledge_graph was called
        assert kg_adapter_mock.add_paper_to_knowledge_graph.called
        kg_adapter_mock.add_paper_to_knowledge_graph.assert_called_with(sample_paper)
        
        # Check that add_paper_to_temporal_knowledge_graph was called
        assert kg_adapter_mock.add_paper_to_temporal_knowledge_graph.called
        kg_adapter_mock.add_paper_to_temporal_knowledge_graph.assert_called_with(sample_paper)
        
        # Check that the paper was updated with knowledge graph ID
        assert mock_paper_model.update_from_domain.called
        updated_paper = mock_paper_model.update_from_domain.call_args[0][0]
        assert updated_paper.knowledge_graph_id == "kg-123"
        assert updated_paper.metadata.get("temporal_graph_id") == "temporal-123"
        
        # Check that the state machine transitions to ANALYZED
        mock_state_machine.transition_to.assert_any_call(
            PaperStatus.ANALYZED,
            "Paper analysis complete"
        )
        
        # Check that the paper was saved
        assert mock_paper_model.save.called
        
        # Check that a WebSocket event was created and broadcast
        assert mock_event_creator.called
        mock_event_creator.assert_called_with(
            paper_id=sample_paper.id,
            status=ANY,
            message="Knowledge graph integration complete",
            progress=90,
            metadata=ANY
        )
        
        # Check that asyncio.run was called to broadcast the event
        assert mock_asyncio_run.called
        mock_asyncio_run.assert_called_with(manager_mock.broadcast_to_paper(sample_paper.id, mock_event))
        
        # Check that the paper ID was returned
        assert result == sample_paper.id