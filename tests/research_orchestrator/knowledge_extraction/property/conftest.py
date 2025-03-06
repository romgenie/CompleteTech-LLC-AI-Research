"""
Fixtures for property-based testing with hypothesis.

This module provides pytest fixtures specifically for property-based tests
using the hypothesis library to generate test data for the knowledge extraction
components.
"""

import pytest
import string
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

from src.research_orchestrator.knowledge_extraction.entity_recognition.entity import EntityType
from src.research_orchestrator.knowledge_extraction.relationship_extraction.relationship import RelationType


@pytest.fixture
def entity_text_strategy() -> SearchStrategy:
    """Strategy for generating entity text strings."""
    return st.text(
        alphabet=string.ascii_letters + string.digits + ' ',
        min_size=1,
        max_size=50
    ).filter(lambda s: s.strip() != '')  # Filter out whitespace-only strings


@pytest.fixture
def entity_type_strategy() -> SearchStrategy:
    """Strategy for generating entity types."""
    return st.sampled_from(list(EntityType))


@pytest.fixture
def relation_type_strategy() -> SearchStrategy:
    """Strategy for generating relationship types."""
    return st.sampled_from(list(RelationType))


@pytest.fixture
def confidence_strategy() -> SearchStrategy:
    """Strategy for generating confidence scores."""
    return st.floats(min_value=0.0, max_value=1.0)


@pytest.fixture
def position_strategy() -> SearchStrategy:
    """Strategy for generating position indices."""
    return st.integers(min_value=0, max_value=1000)


@pytest.fixture
def metadata_strategy() -> SearchStrategy:
    """Strategy for generating metadata dictionaries."""
    return st.dictionaries(
        keys=st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=10),
        values=st.one_of(
            st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=20),
            st.integers(min_value=0, max_value=1000),
            st.floats(min_value=0.0, max_value=100.0)
        ),
        max_size=5
    )


@pytest.fixture
def entity_id_strategy() -> SearchStrategy:
    """Strategy for generating entity IDs."""
    return st.text(
        alphabet=string.ascii_letters + string.digits + '_',
        min_size=1,
        max_size=20
    )


@pytest.fixture
def document_text_strategy() -> SearchStrategy:
    """Strategy for generating document text."""
    # Generate paragraphs of text
    paragraph = st.text(
        alphabet=string.ascii_letters + string.digits + string.punctuation + ' ' + '\n',
        min_size=50,
        max_size=500
    )
    return st.lists(paragraph, min_size=1, max_size=10).map(lambda ps: '\n\n'.join(ps))


@pytest.fixture
def document_type_strategy() -> SearchStrategy:
    """Strategy for generating document types."""
    return st.sampled_from(['text', 'html', 'pdf', 'markdown', 'docx'])


@pytest.fixture
def file_path_strategy() -> SearchStrategy:
    """Strategy for generating file paths."""
    # Generate directory path components
    dir_component = st.text(
        alphabet=string.ascii_lowercase + string.digits + '_',
        min_size=1,
        max_size=10
    )
    
    # Generate filename and extension
    filename = st.text(
        alphabet=string.ascii_lowercase + string.digits + '_',
        min_size=1,
        max_size=20
    )
    extension = st.sampled_from(['.txt', '.html', '.pdf', '.md', '.docx'])
    
    # Combine to create a path
    return st.builds(
        lambda dirs, name, ext: '/' + '/'.join(dirs) + '/' + name + ext,
        st.lists(dir_component, min_size=1, max_size=3),
        filename,
        extension
    )