"""
Schema utilities for Knowledge Graph System.

This module provides utilities for managing and validating knowledge graph schemas,
including entity and relationship definitions.
"""

from typing import Dict, List, Optional, Any, Union, Set
import logging
import json
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchemaDefinition:
    """
    Class for defining and validating knowledge graph schemas.
    
    This class provides methods for loading schema definitions,
    validating entities and relationships against the schema,
    and generating schema visualizations.
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the schema definition.
        
        Args:
            schema_path: Path to the schema definition file (JSON)
        """
        self.entity_types = {}
        self.relationship_types = {}
        self.constraints = []
        self.indexes = []
        
        if schema_path:
            self.load_schema(schema_path)
    
    def load_schema(self, schema_path: str):
        """
        Load schema definition from a file.
        
        Args:
            schema_path: Path to the schema definition file (JSON)
            
        Raises:
            FileNotFoundError: If the schema file is not found
            ValueError: If the schema file is invalid
        """
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            # Load entity types
            self.entity_types = schema.get('entity_types', {})
            
            # Load relationship types
            self.relationship_types = schema.get('relationship_types', {})
            
            # Load constraints and indexes
            self.constraints = schema.get('constraints', [])
            self.indexes = schema.get('indexes', [])
            
            logger.info(f"Loaded schema with {len(self.entity_types)} entity types and "
                       f"{len(self.relationship_types)} relationship types")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading schema: {e}")
    
    def validate_entity(self, entity_data: Dict[str, Any]) -> List[str]:
        """
        Validate an entity against the schema.
        
        Args:
            entity_data: Dictionary containing entity data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check if the entity has a label
        if 'label' not in entity_data:
            errors.append("Entity missing required 'label' field")
            return errors
        
        label = entity_data['label']
        
        # Check if the label is defined in the schema
        if label not in self.entity_types:
            errors.append(f"Entity label '{label}' not defined in schema")
            return errors
        
        # Get the schema definition for this entity type
        schema_def = self.entity_types[label]
        
        # Check required properties
        for prop_name, prop_def in schema_def.get('properties', {}).items():
            if prop_def.get('required', False) and (
                'properties' not in entity_data or
                prop_name not in entity_data['properties']
            ):
                errors.append(f"Entity missing required property '{prop_name}'")
        
        # Check property types
        if 'properties' in entity_data:
            for prop_name, prop_value in entity_data['properties'].items():
                if prop_name in schema_def.get('properties', {}):
                    prop_def = schema_def['properties'][prop_name]
                    prop_type = prop_def.get('type')
                    
                    if prop_type and not self._check_type(prop_value, prop_type):
                        errors.append(f"Entity property '{prop_name}' has incorrect type. "
                                      f"Expected {prop_type}, got {type(prop_value).__name__}")
        
        return errors
    
    def validate_relationship(self, relationship_data: Dict[str, Any]) -> List[str]:
        """
        Validate a relationship against the schema.
        
        Args:
            relationship_data: Dictionary containing relationship data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check if the relationship has a type
        if 'type' not in relationship_data:
            errors.append("Relationship missing required 'type' field")
            return errors
        
        rel_type = relationship_data['type']
        
        # Check if the type is defined in the schema
        if rel_type not in self.relationship_types:
            errors.append(f"Relationship type '{rel_type}' not defined in schema")
            return errors
        
        # Get the schema definition for this relationship type
        schema_def = self.relationship_types[rel_type]
        
        # Check source and target entity types
        if 'source_id' not in relationship_data:
            errors.append("Relationship missing required 'source_id' field")
        
        if 'target_id' not in relationship_data:
            errors.append("Relationship missing required 'target_id' field")
        
        # Check required properties
        for prop_name, prop_def in schema_def.get('properties', {}).items():
            if prop_def.get('required', False) and (
                'properties' not in relationship_data or
                prop_name not in relationship_data['properties']
            ):
                errors.append(f"Relationship missing required property '{prop_name}'")
        
        # Check property types
        if 'properties' in relationship_data:
            for prop_name, prop_value in relationship_data['properties'].items():
                if prop_name in schema_def.get('properties', {}):
                    prop_def = schema_def['properties'][prop_name]
                    prop_type = prop_def.get('type')
                    
                    if prop_type and not self._check_type(prop_value, prop_type):
                        errors.append(f"Relationship property '{prop_name}' has incorrect type. "
                                      f"Expected {prop_type}, got {type(prop_value).__name__}")
        
        return errors
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if a value matches the expected type.
        
        Args:
            value: Value to check
            expected_type: Expected type name
            
        Returns:
            True if the value matches the expected type, False otherwise
        """
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'integer':
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == 'number':
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'null':
            return value is None
        elif expected_type.startswith('array['):
            item_type = expected_type[6:-1]  # Extract the type inside array[...]
            return isinstance(value, list) and all(self._check_type(item, item_type) for item in value)
        else:
            return True  # Unknown type, assume valid
    
    def generate_cypher_schema(self) -> str:
        """
        Generate Cypher statements for creating the schema constraints and indexes.
        
        Returns:
            String containing Cypher statements
        """
        cypher = "// Knowledge Graph Schema Definition\n\n"
        
        # Generate constraint statements
        cypher += "// Constraints\n"
        for constraint in self.constraints:
            name = constraint.get('name', '')
            label = constraint.get('label', '')
            property_name = constraint.get('property', '')
            
            cypher += f"CREATE CONSTRAINT {name} IF NOT EXISTS\n"
            cypher += f"FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE;\n\n"
        
        # Generate index statements
        cypher += "// Indexes\n"
        for index in self.indexes:
            name = index.get('name', '')
            label = index.get('label', '')
            properties = index.get('properties', [])
            
            properties_str = ', '.join([f"n.{prop}" for prop in properties])
            
            cypher += f"CREATE INDEX {name} IF NOT EXISTS\n"
            cypher += f"FOR (n:{label}) ON ({properties_str});\n\n"
        
        return cypher
    
    def generate_schema_visualization(self, output_path: str):
        """
        Generate a visualization of the schema.
        
        Args:
            output_path: Path to save the visualization
        """
        try:
            # Prepare graph data
            nodes = []
            for entity_type, entity_def in self.entity_types.items():
                properties = entity_def.get('properties', {})
                node = {
                    'id': entity_type,
                    'label': entity_type,
                    'properties': list(properties.keys())
                }
                nodes.append(node)
            
            edges = []
            for rel_type, rel_def in self.relationship_types.items():
                source_types = rel_def.get('source_types', [])
                target_types = rel_def.get('target_types', [])
                
                for source_type in source_types:
                    for target_type in target_types:
                        edge = {
                            'source': source_type,
                            'target': target_type,
                            'label': rel_type
                        }
                        edges.append(edge)
            
            # Create visualization data
            visualization_data = {
                'nodes': nodes,
                'edges': edges
            }
            
            # Save to file
            with open(output_path, 'w') as f:
                json.dump(visualization_data, f, indent=2)
            
            logger.info(f"Schema visualization saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate schema visualization: {e}")
    
    @classmethod
    def generate_default_schema(cls, output_path: str):
        """
        Generate a default schema definition.
        
        Args:
            output_path: Path to save the schema definition
        """
        schema = {
            "entity_types": {
                "Entity": {
                    "description": "Base entity type",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Unique identifier",
                            "required": True
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the entity",
                            "required": True
                        },
                        "created_at": {
                            "type": "string",
                            "description": "Creation timestamp",
                            "required": True
                        },
                        "updated_at": {
                            "type": "string",
                            "description": "Last update timestamp",
                            "required": True
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence score",
                            "required": True
                        },
                        "source": {
                            "type": "string",
                            "description": "Source of the entity information",
                            "required": False
                        },
                        "aliases": {
                            "type": "array[string]",
                            "description": "Alternative identifiers",
                            "required": False
                        }
                    }
                },
                "AIModel": {
                    "description": "AI model entity",
                    "inherits": "Entity",
                    "properties": {
                        "organization": {
                            "type": "string",
                            "description": "Organization that developed the model",
                            "required": False
                        },
                        "release_date": {
                            "type": "string",
                            "description": "Release date of the model",
                            "required": False
                        },
                        "model_type": {
                            "type": "string",
                            "description": "Type of model",
                            "required": False
                        },
                        "parameters": {
                            "type": "number",
                            "description": "Number of parameters",
                            "required": False
                        },
                        "architecture": {
                            "type": "string",
                            "description": "Model architecture",
                            "required": False
                        },
                        "training_data": {
                            "type": "string",
                            "description": "Description of training data",
                            "required": False
                        },
                        "capabilities": {
                            "type": "array[string]",
                            "description": "List of model capabilities",
                            "required": False
                        },
                        "limitations": {
                            "type": "array[string]",
                            "description": "List of model limitations",
                            "required": False
                        },
                        "repository": {
                            "type": "string",
                            "description": "URL to model repository",
                            "required": False
                        },
                        "paper": {
                            "type": "string",
                            "description": "URL to model paper",
                            "required": False
                        }
                    }
                },
                "Dataset": {
                    "description": "Dataset entity",
                    "inherits": "Entity",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of the dataset",
                            "required": False
                        },
                        "domain": {
                            "type": "string",
                            "description": "Domain of the dataset",
                            "required": False
                        },
                        "size": {
                            "type": "string",
                            "description": "Size of the dataset",
                            "required": False
                        },
                        "format": {
                            "type": "string",
                            "description": "Format of the dataset",
                            "required": False
                        },
                        "license": {
                            "type": "string",
                            "description": "License of the dataset",
                            "required": False
                        },
                        "url": {
                            "type": "string",
                            "description": "URL to the dataset",
                            "required": False
                        },
                        "citation": {
                            "type": "string",
                            "description": "Citation for the dataset",
                            "required": False
                        },
                        "features": {
                            "type": "array[string]",
                            "description": "List of features in the dataset",
                            "required": False
                        }
                    }
                }
            },
            "relationship_types": {
                "RELATED_TO": {
                    "description": "Generic relationship between entities",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Unique identifier",
                            "required": True
                        },
                        "created_at": {
                            "type": "string",
                            "description": "Creation timestamp",
                            "required": True
                        },
                        "updated_at": {
                            "type": "string",
                            "description": "Last update timestamp",
                            "required": True
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence score",
                            "required": True
                        },
                        "source": {
                            "type": "string",
                            "description": "Source of the relationship information",
                            "required": False
                        }
                    },
                    "source_types": ["Entity"],
                    "target_types": ["Entity"]
                },
                "TRAINED_ON": {
                    "description": "Relationship indicating a model was trained on a dataset",
                    "inherits": "RELATED_TO",
                    "properties": {},
                    "source_types": ["AIModel"],
                    "target_types": ["Dataset"]
                },
                "EVALUATED_ON": {
                    "description": "Relationship indicating a model was evaluated on a benchmark",
                    "inherits": "RELATED_TO",
                    "properties": {
                        "metrics": {
                            "type": "object",
                            "description": "Performance metrics",
                            "required": False
                        }
                    },
                    "source_types": ["AIModel"],
                    "target_types": ["Benchmark"]
                },
                "OUTPERFORMS": {
                    "description": "Relationship indicating one model outperforms another",
                    "inherits": "RELATED_TO",
                    "properties": {
                        "metrics": {
                            "type": "object",
                            "description": "Performance metrics",
                            "required": False
                        },
                        "margin": {
                            "type": "number",
                            "description": "Margin of improvement",
                            "required": False
                        }
                    },
                    "source_types": ["AIModel"],
                    "target_types": ["AIModel"]
                }
            },
            "constraints": [
                {
                    "name": "entity_id_unique",
                    "label": "Entity",
                    "property": "id"
                }
            ],
            "indexes": [
                {
                    "name": "entity_name_index",
                    "label": "Entity",
                    "properties": ["name"]
                },
                {
                    "name": "entity_label_index",
                    "label": "Entity",
                    "properties": ["label"]
                }
            ]
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(schema, f, indent=2)
            
            logger.info(f"Default schema definition saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate default schema definition: {e}")
    
    @classmethod
    def from_dict(cls, schema_dict: Dict[str, Any]) -> 'SchemaDefinition':
        """
        Create a schema definition from a dictionary.
        
        Args:
            schema_dict: Dictionary containing schema definition
            
        Returns:
            SchemaDefinition instance
        """
        schema = cls()
        
        schema.entity_types = schema_dict.get('entity_types', {})
        schema.relationship_types = schema_dict.get('relationship_types', {})
        schema.constraints = schema_dict.get('constraints', [])
        schema.indexes = schema_dict.get('indexes', [])
        
        return schema