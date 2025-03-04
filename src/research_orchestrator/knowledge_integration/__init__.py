"""
Knowledge Integration module for the Research Orchestration Framework.

This module provides components for integrating the Knowledge Extraction Pipeline
with the Knowledge Graph System, enabling storage, querying, and analysis of
extracted knowledge.
"""

from .knowledge_graph_adapter import KnowledgeGraphAdapter
from .entity_converter import EntityConverter
from .relationship_converter import RelationshipConverter
from .conflict_resolver import ConflictResolver
from .connection_discovery import ConnectionDiscoveryEngine

__version__ = "0.1.0"