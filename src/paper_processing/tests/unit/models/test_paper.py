"""
Unit tests for the Paper model.

This module tests the Paper model and related functionality.
"""

import pytest
import uuid
from datetime import datetime
from pydantic import ValidationError

from paper_processing.models.paper import (
    Paper, 
    PaperStatus, 
    Author, 
    Entity, 
    Relationship, 
    ProcessingEvent,
    add_processing_event
)


def test_paper_create():
    """Test creating a Paper instance."""
    # Create a paper with minimal fields
    paper_id = str(uuid.uuid4())
    paper = Paper(
        id=paper_id,
        title="Test Paper",
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        content_type="application/pdf",
        original_filename="original_test.pdf",
        uploaded_by="test_user",
        uploaded_at=datetime.utcnow(),
    )
    
    # Check default values
    assert paper.id == paper_id
    assert paper.title == "Test Paper"
    assert paper.status == PaperStatus.UPLOADED
    assert len(paper.processing_history) == 0
    assert len(paper.entities) == 0
    assert len(paper.relationships) == 0
    assert paper.statistics is None
    assert paper.knowledge_graph_id is None
    assert paper.implementation_ready is False


def test_paper_create_with_all_fields():
    """Test creating a Paper instance with all fields."""
    # Create authors
    authors = [
        Author(name="Author 1", email="author1@example.com", affiliation="University 1"),
        Author(name="Author 2", affiliation="University 2")
    ]
    
    # Create entities
    entities = [
        Entity(
            id="entity1",
            type="MODEL",
            name="Test Model",
            confidence=0.9,
            context="Test context"
        ),
        Entity(
            id="entity2",
            type="DATASET",
            name="Test Dataset",
            confidence=0.8,
            context="Test context"
        )
    ]
    
    # Create relationships
    relationships = [
        Relationship(
            id="rel1",
            type="TRAINED_ON",
            source_id="entity1",
            target_id="entity2",
            confidence=0.85,
            context="Test context"
        )
    ]
    
    # Create processing history
    history = [
        ProcessingEvent(
            timestamp=datetime.utcnow(),
            status=PaperStatus.UPLOADED,
            message="Paper uploaded"
        )
    ]
    
    # Create paper
    paper_id = str(uuid.uuid4())
    paper = Paper(
        id=paper_id,
        title="Test Paper",
        authors=authors,
        abstract="This is a test paper",
        year=2025,
        doi="10.1234/test",
        url="https://example.com/test",
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        content_type="application/pdf",
        original_filename="original_test.pdf",
        uploaded_by="test_user",
        uploaded_at=datetime.utcnow(),
        status=PaperStatus.ANALYZED,
        processing_history=history,
        entities=entities,
        relationships=relationships,
        knowledge_graph_id="kg-123",
        implementation_ready=True,
        metadata={"keywords": ["test", "paper"]}
    )
    
    # Check values
    assert paper.id == paper_id
    assert paper.title == "Test Paper"
    assert len(paper.authors) == 2
    assert paper.authors[0].name == "Author 1"
    assert paper.authors[1].name == "Author 2"
    assert paper.abstract == "This is a test paper"
    assert paper.year == 2025
    assert paper.doi == "10.1234/test"
    assert paper.url == "https://example.com/test"
    assert paper.status == PaperStatus.ANALYZED
    assert len(paper.processing_history) == 1
    assert paper.processing_history[0].status == PaperStatus.UPLOADED
    assert len(paper.entities) == 2
    assert paper.entities[0].type == "MODEL"
    assert paper.entities[1].type == "DATASET"
    assert len(paper.relationships) == 1
    assert paper.relationships[0].type == "TRAINED_ON"
    assert paper.knowledge_graph_id == "kg-123"
    assert paper.implementation_ready is True
    assert paper.metadata == {"keywords": ["test", "paper"]}


def test_add_processing_event():
    """Test adding a processing event to a paper."""
    # Create a paper
    paper_id = str(uuid.uuid4())
    paper = Paper(
        id=paper_id,
        title="Test Paper",
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        content_type="application/pdf",
        original_filename="original_test.pdf",
        uploaded_by="test_user",
        uploaded_at=datetime.utcnow(),
    )
    
    # Add a processing event
    updated_paper = add_processing_event(
        paper,
        PaperStatus.QUEUED,
        "Paper queued for processing"
    )
    
    # Check that the event was added and status updated
    assert updated_paper.status == PaperStatus.QUEUED
    assert len(updated_paper.processing_history) == 1
    assert updated_paper.processing_history[0].status == PaperStatus.QUEUED
    assert updated_paper.processing_history[0].message == "Paper queued for processing"
    
    # Add another event with details
    details = {"task_id": "123", "worker": "worker1"}
    updated_paper = add_processing_event(
        updated_paper,
        PaperStatus.PROCESSING,
        "Paper processing started",
        details
    )
    
    # Check that the event was added and status updated
    assert updated_paper.status == PaperStatus.PROCESSING
    assert len(updated_paper.processing_history) == 2
    assert updated_paper.processing_history[1].status == PaperStatus.PROCESSING
    assert updated_paper.processing_history[1].message == "Paper processing started"
    assert updated_paper.processing_history[1].details == details


def test_paper_validation():
    """Test paper validation."""
    # Missing required fields
    with pytest.raises(ValidationError):
        Paper(title="Test")
    
    # Invalid status
    with pytest.raises(ValidationError):
        Paper(
            id=str(uuid.uuid4()),
            title="Test Paper",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            original_filename="original_test.pdf",
            uploaded_by="test_user",
            uploaded_at=datetime.utcnow(),
            status="INVALID_STATUS"  # Invalid status
        )
    
    # Invalid year
    with pytest.raises(ValidationError):
        Paper(
            id=str(uuid.uuid4()),
            title="Test Paper",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            original_filename="original_test.pdf",
            uploaded_by="test_user",
            uploaded_at=datetime.utcnow(),
            year=1800  # Year too old
        )


def test_entity_validation():
    """Test entity validation."""
    # Valid entity
    entity = Entity(
        id="entity1",
        type="MODEL",
        name="Test Model",
        confidence=0.9
    )
    assert entity.id == "entity1"
    assert entity.type == "MODEL"
    assert entity.name == "Test Model"
    assert entity.confidence == 0.9
    
    # Invalid confidence (< 0)
    with pytest.raises(ValidationError):
        Entity(
            id="entity1",
            type="MODEL",
            name="Test Model",
            confidence=-0.1  # Invalid confidence
        )
    
    # Invalid confidence (> 1)
    with pytest.raises(ValidationError):
        Entity(
            id="entity1",
            type="MODEL",
            name="Test Model",
            confidence=1.1  # Invalid confidence
        )


def test_relationship_validation():
    """Test relationship validation."""
    # Valid relationship
    relationship = Relationship(
        id="rel1",
        type="TRAINED_ON",
        source_id="entity1",
        target_id="entity2",
        confidence=0.85
    )
    assert relationship.id == "rel1"
    assert relationship.type == "TRAINED_ON"
    assert relationship.source_id == "entity1"
    assert relationship.target_id == "entity2"
    assert relationship.confidence == 0.85
    
    # Missing required fields
    with pytest.raises(ValidationError):
        Relationship(
            id="rel1",
            type="TRAINED_ON",
            source_id="entity1",
            # Missing target_id
            confidence=0.85
        )
    
    # Invalid confidence
    with pytest.raises(ValidationError):
        Relationship(
            id="rel1",
            type="TRAINED_ON",
            source_id="entity1",
            target_id="entity2",
            confidence=1.1  # Invalid confidence
        )