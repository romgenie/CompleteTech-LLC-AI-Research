"""
Relationship Converter for integrating Knowledge Extraction with the Knowledge Graph System.

This module provides the RelationshipConverter class that converts extracted relationships
from the Knowledge Extraction Pipeline format to the Knowledge Graph System format.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple, Union
import json
import os

from ..knowledge_extraction.relationship_extraction import Relationship, RelationType

logger = logging.getLogger(__name__)


class RelationshipConverter:
    """Converts extracted relationships to knowledge graph format.
    
    This class is responsible for transforming Relationship objects from the 
    Knowledge Extraction Pipeline into the format required by the Knowledge
    Graph System.
    """
    
    # Default relationship type mapping from Extraction to Knowledge Graph
    DEFAULT_RELATIONSHIP_TYPE_MAPPING = {
        "is_a": "IS_A",
        "part_of": "PART_OF",
        "used_for": "USED_FOR",
        "based_on": "BUILDS_ON",
        "developed_by": "DEVELOPED_BY",
        "evaluated_on": "EVALUATED_ON",
        "outperforms": "OUTPERFORMS",
        "implements": "IMPLEMENTS",
        "extends": "EXTENDS",
        "related_to": "RELATED_TO",
        "trained_on": "TRAINED_ON",
        "achieves": "ACHIEVES",
        "uses": "USES",
        "compared_to": "COMPARED_TO",
        "feature_of": "FEATURE_OF",
        "parameter_of": "PARAMETER_OF",
        "applied_to": "APPLIED_TO",
        "optimized_for": "OPTIMIZED_FOR",
        "belongs_to": "BELONGS_TO",
        "supported_by": "SUPPORTED_BY",
        "implemented_in": "IMPLEMENTED_IN",
        "composed_of": "COMPOSED_OF",
        "compatible_with": "COMPATIBLE_WITH",
        "hypothesizes": "HYPOTHESIZES",
        "proves": "PROVES",
        "disproves": "DISPROVES",
        "cites": "CITES",
        "contradicts": "CONTRADICTS",
        "confirms": "CONFIRMS",
        "studies": "STUDIES",
        "analyzes": "ANALYZES",
        "introduces": "INTRODUCES",
        "improves_upon": "IMPROVES_UPON"
    }
    
    # Default property mappings from Relationship attributes to graph relationship properties
    DEFAULT_PROPERTY_MAPPING = {
        "confidence": "confidence",
        "bidirectional": "bidirectional",
        "context": "context",
        "metadata": None  # Handle metadata specially
    }
    
    def __init__(
        self, 
        relationship_type_mapping: Optional[Dict[str, str]] = None,
        property_mapping: Optional[Dict[str, str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the relationship converter.
        
        Args:
            relationship_type_mapping: Optional mapping from extraction types to graph relationship types
            property_mapping: Optional mapping from relationship attributes to graph relationship properties
            config: Additional configuration options
        """
        self.config = config or {}
        
        # Use provided mappings or defaults
        self.relationship_type_mapping = relationship_type_mapping or self.DEFAULT_RELATIONSHIP_TYPE_MAPPING.copy()
        self.property_mapping = property_mapping or self.DEFAULT_PROPERTY_MAPPING.copy()
        
        # Additional configuration options
        self.include_provenance = self.config.get('include_provenance', True)
        self.include_extraction_metadata = self.config.get('include_extraction_metadata', True)
        self.min_confidence_threshold = self.config.get('min_confidence_threshold', 0.0)
        self.include_context = self.config.get('include_context', True)
        self.generate_inverse_relationships = self.config.get('generate_inverse_relationships', False)
        
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
            if 'relationship_type_mapping' in mappings:
                self.relationship_type_mapping.update(mappings['relationship_type_mapping'])
            
            if 'property_mapping' in mappings:
                self.property_mapping.update(mappings['property_mapping'])
                
            logger.info(f"Loaded relationship mappings from {mapping_file}")
        except Exception as e:
            logger.error(f"Error loading mappings from {mapping_file}: {e}")
    
    def convert_relationship(
        self, 
        relationship: Relationship, 
        document_id: Optional[str] = None,
        source_info: Optional[Dict[str, Any]] = None,
        entity_id_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Convert a single relationship to knowledge graph format.
        
        Args:
            relationship: The relationship to convert
            document_id: Optional ID of the source document
            source_info: Optional information about the source
            entity_id_mapping: Optional mapping from extraction entity IDs to graph entity IDs
            
        Returns:
            Dictionary representation for the knowledge graph
        """
        # Skip relationships below confidence threshold
        if relationship.confidence < self.min_confidence_threshold:
            return None
        
        # Skip relationships without source or target entities
        if not relationship.source or not relationship.target:
            return None
        
        # Map relationship type to graph relationship type
        rel_type_str = str(relationship.relation_type).lower()
        graph_type = self.relationship_type_mapping.get(rel_type_str, "RELATED_TO")
        
        # Get source and target entity IDs, applying mapping if provided
        source_id = relationship.source.id
        target_id = relationship.target.id
        
        if entity_id_mapping:
            source_id = entity_id_mapping.get(source_id, source_id)
            target_id = entity_id_mapping.get(target_id, target_id)
        
        # Create basic relationship properties
        graph_relationship = {
            "id": relationship.id,
            "type": graph_type,
            "source_id": source_id,
            "target_id": target_id,
            "properties": {
                "id": relationship.id,
                "confidence": relationship.confidence
            }
        }
        
        # Include bidirectional flag if set
        if relationship.bidirectional:
            graph_relationship["properties"]["bidirectional"] = True
        
        # Include context if available and configured
        if relationship.context and self.include_context:
            graph_relationship["properties"]["context"] = relationship.context[:500]  # Limit context length
        
        # Map additional properties according to mapping
        for rel_attr, graph_prop in self.property_mapping.items():
            if graph_prop and hasattr(relationship, rel_attr) and rel_attr not in ["confidence", "bidirectional", "context"]:
                value = getattr(relationship, rel_attr)
                if value is not None:
                    graph_relationship["properties"][graph_prop] = value
        
        # Include relationship metadata if available
        if relationship.metadata and self.include_extraction_metadata:
            for key, value in relationship.metadata.items():
                # Skip special metadata that might conflict with core properties
                if key not in ["id", "type", "source_id", "target_id"]:
                    graph_relationship["properties"][f"metadata_{key}"] = value
        
        # Add provenance information
        if self.include_provenance and (document_id or source_info):
            graph_relationship["properties"]["provenance"] = {}
            if document_id:
                graph_relationship["properties"]["provenance"]["document_id"] = document_id
            if source_info:
                graph_relationship["properties"]["provenance"].update(source_info)
            
            # Convert to string for Neo4j compatibility if needed
            graph_relationship["properties"]["provenance"] = json.dumps(graph_relationship["properties"]["provenance"])
        
        return graph_relationship
    
    def convert_relationships(
        self, 
        relationships: List[Relationship],
        document_id: Optional[str] = None,
        source_info: Optional[Dict[str, Any]] = None,
        entity_id_mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Convert multiple relationships to knowledge graph format.
        
        Args:
            relationships: List of relationships to convert
            document_id: Optional ID of the source document
            source_info: Optional information about the source
            entity_id_mapping: Optional mapping from extraction entity IDs to graph entity IDs
            
        Returns:
            List of dictionary representations for the knowledge graph
        """
        graph_relationships = []
        
        for relationship in relationships:
            rel = self.convert_relationship(relationship, document_id, source_info, entity_id_mapping)
            if rel:  # Only include relationships that were successfully converted
                graph_relationships.append(rel)
                
                # Generate inverse relationship if configured
                if self.generate_inverse_relationships and relationship.bidirectional:
                    inverse_rel = self._generate_inverse(rel)
                    if inverse_rel:
                        graph_relationships.append(inverse_rel)
        
        return graph_relationships
    
    def _generate_inverse(self, relationship: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate an inverse relationship for bidirectional relationships.
        
        Args:
            relationship: The original relationship in graph format
            
        Returns:
            Inverse relationship in graph format, or None if not applicable
        """
        # Skip if not bidirectional
        if not relationship.get("properties", {}).get("bidirectional", False):
            return None
        
        # Create a copy of the original relationship
        inverse = relationship.copy()
        inverse["properties"] = relationship["properties"].copy()
        
        # Generate a new ID for the inverse relationship
        inverse["id"] = f"{relationship['id']}_inverse"
        inverse["properties"]["id"] = inverse["id"]
        
        # Swap source and target
        inverse["source_id"], inverse["target_id"] = relationship["target_id"], relationship["source_id"]
        
        # Add metadata about being an inverse relationship
        inverse["properties"]["inverse_of"] = relationship["id"]
        
        return inverse
    
    def add_relationship_type_mapping(self, rel_type: str, graph_type: str) -> None:
        """Add a new relationship type mapping.
        
        Args:
            rel_type: Relationship type from the extraction pipeline
            graph_type: Corresponding relationship type in the knowledge graph
        """
        self.relationship_type_mapping[rel_type.lower()] = graph_type
    
    def add_property_mapping(self, rel_attr: str, graph_prop: str) -> None:
        """Add a new property mapping.
        
        Args:
            rel_attr: Relationship attribute from the extraction pipeline
            graph_prop: Corresponding property name in the knowledge graph
        """
        self.property_mapping[rel_attr] = graph_prop