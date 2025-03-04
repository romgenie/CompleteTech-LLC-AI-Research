"""
Entity Converter for integrating Knowledge Extraction with the Knowledge Graph System.

This module provides the EntityConverter class that converts extracted entities from
the Knowledge Extraction Pipeline format to the Knowledge Graph System format.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
import json
import os

from ..knowledge_extraction.entity_recognition import Entity, EntityType

logger = logging.getLogger(__name__)


class EntityConverter:
    """Converts extracted entities to knowledge graph format.
    
    This class is responsible for transforming Entity objects from the 
    Knowledge Extraction Pipeline into the format required by the Knowledge
    Graph System.
    """
    
    # Default entity type mapping from Entity Recognition to Knowledge Graph
    DEFAULT_ENTITY_TYPE_MAPPING = {
        "model": "Model",
        "algorithm": "Algorithm",
        "architecture": "Architecture",
        "dataset": "Dataset",
        "metric": "Metric",
        "parameter": "Parameter",
        "hyperparameter": "Parameter",
        "framework": "Framework",
        "library": "Framework",
        "technique": "Technique",
        "task": "Task",
        "benchmark": "Dataset",
        "concept": "Concept",
        "theory": "Theory",
        "methodology": "Methodology",
        "finding": "Finding",
        "hypothesis": "Hypothesis",
        "experiment": "Experiment",
        "artifact": "Artifact",
        "tool": "Tool",
        "property": "Property",
        "constraint": "Constraint",
        "limitation": "Limitation",
        "field": "Field",
        "author": "Author",
        "institution": "Institution"
    }
    
    # Default property mappings from Entity attributes to graph properties
    DEFAULT_PROPERTY_MAPPING = {
        "text": "name",
        "confidence": "confidence",
        "metadata": None  # Handle metadata specially
    }
    
    def __init__(
        self, 
        entity_type_mapping: Optional[Dict[str, str]] = None,
        property_mapping: Optional[Dict[str, str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the entity converter.
        
        Args:
            entity_type_mapping: Optional mapping from entity recognition types to graph node labels
            property_mapping: Optional mapping from entity attributes to graph node properties
            config: Additional configuration options
        """
        self.config = config or {}
        
        # Use provided mappings or defaults
        self.entity_type_mapping = entity_type_mapping or self.DEFAULT_ENTITY_TYPE_MAPPING.copy()
        self.property_mapping = property_mapping or self.DEFAULT_PROPERTY_MAPPING.copy()
        
        # Additional configuration options
        self.include_provenance = self.config.get('include_provenance', True)
        self.include_extraction_metadata = self.config.get('include_extraction_metadata', True)
        self.min_confidence_threshold = self.config.get('min_confidence_threshold', 0.0)
        
        # Load any custom mappings from files
        mapping_file = self.config.get('mapping_file')
        if mapping_file and os.path.exists(mapping_file):
            self._load_mappings_from_file(mapping_file)
    
    def _load_mappings_from_file(self, mapping_file: str) -> None:
        """Load type and property mappings from a JSON file.
        
        Args:
            mapping_file: Path to the mapping configuration JSON file
        """
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
            
            # Update mappings from file
            if 'entity_type_mapping' in mappings:
                self.entity_type_mapping.update(mappings['entity_type_mapping'])
            
            if 'property_mapping' in mappings:
                self.property_mapping.update(mappings['property_mapping'])
                
            logger.info(f"Loaded entity mappings from {mapping_file}")
        except Exception as e:
            logger.error(f"Error loading mappings from {mapping_file}: {e}")
    
    def convert_entity(
        self, 
        entity: Entity, 
        document_id: Optional[str] = None,
        source_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert a single entity to knowledge graph format.
        
        Args:
            entity: The entity to convert
            document_id: Optional ID of the source document
            source_info: Optional information about the source
            
        Returns:
            Dictionary representation for the knowledge graph
        """
        # Skip entities below confidence threshold
        if entity.confidence < self.min_confidence_threshold:
            return None
        
        # Map entity type to graph label
        entity_type_str = str(entity.type).lower()
        graph_label = self.entity_type_mapping.get(entity_type_str, "UnknownType")
        
        # Create basic node properties
        node = {
            "id": entity.id,
            "labels": [graph_label],
            "properties": {
                "id": entity.id,
                "name": entity.text,
                "confidence": entity.confidence
            }
        }
        
        # Map additional properties according to mapping
        for entity_attr, graph_prop in self.property_mapping.items():
            if graph_prop and hasattr(entity, entity_attr) and entity_attr != "text":
                value = getattr(entity, entity_attr)
                if value is not None:
                    node["properties"][graph_prop] = value
        
        # Include entity metadata if available
        if entity.metadata and self.include_extraction_metadata:
            for key, value in entity.metadata.items():
                # Skip special metadata that might conflict with core properties
                if key not in ["id", "name", "labels"]:
                    node["properties"][f"metadata_{key}"] = value
        
        # Add provenance information
        if self.include_provenance and (document_id or source_info):
            node["properties"]["provenance"] = {}
            if document_id:
                node["properties"]["provenance"]["document_id"] = document_id
            if source_info:
                node["properties"]["provenance"].update(source_info)
            
            # Convert to string for Neo4j compatibility if needed
            node["properties"]["provenance"] = json.dumps(node["properties"]["provenance"])
        
        return node
    
    def convert_entities(
        self, 
        entities: List[Entity],
        document_id: Optional[str] = None,
        source_info: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Convert multiple entities to knowledge graph format.
        
        Args:
            entities: List of entities to convert
            document_id: Optional ID of the source document
            source_info: Optional information about the source
            
        Returns:
            List of dictionary representations for the knowledge graph
        """
        graph_nodes = []
        
        for entity in entities:
            node = self.convert_entity(entity, document_id, source_info)
            if node:  # Only include nodes that were successfully converted
                graph_nodes.append(node)
        
        return graph_nodes
    
    def add_entity_type_mapping(self, entity_type: str, graph_label: str) -> None:
        """Add a new entity type mapping.
        
        Args:
            entity_type: Entity type from the extraction pipeline
            graph_label: Corresponding node label in the knowledge graph
        """
        self.entity_type_mapping[entity_type.lower()] = graph_label
    
    def add_property_mapping(self, entity_attr: str, graph_prop: str) -> None:
        """Add a new property mapping.
        
        Args:
            entity_attr: Entity attribute from the extraction pipeline
            graph_prop: Corresponding property name in the knowledge graph
        """
        self.property_mapping[entity_attr] = graph_prop