"""
Knowledge Extractor module for the Knowledge Extraction Pipeline.

This module provides a coordinator that manages the entire knowledge extraction process,
including document processing, entity recognition, and relationship extraction.
"""

from typing import Dict, List, Optional, Set, Any, Tuple, Union
import logging
import os
import json
from pathlib import Path

from research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from research_orchestrator.knowledge_extraction.entity_recognition.entity import Entity
from research_orchestrator.knowledge_extraction.entity_recognition.base_recognizer import EntityRecognizer
from research_orchestrator.knowledge_extraction.entity_recognition.factory import EntityRecognizerFactory
from research_orchestrator.knowledge_extraction.relationship_extraction.relationship import Relationship
from research_orchestrator.knowledge_extraction.relationship_extraction.base_extractor import RelationshipExtractor
from research_orchestrator.knowledge_extraction.relationship_extraction.factory import RelationshipExtractorFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeExtractor:
    """
    Coordinator for the knowledge extraction process, managing document processing,
    entity recognition, and relationship extraction.
    """
    
    def __init__(self, 
                 document_processor: Optional[DocumentProcessor] = None,
                 entity_recognizer: Optional[EntityRecognizer] = None,
                 relationship_extractor: Optional[RelationshipExtractor] = None,
                 config_path: Optional[str] = None):
        """
        Initialize the knowledge extractor.
        
        Args:
            document_processor: Document processor to use
            entity_recognizer: Entity recognizer to use
            relationship_extractor: Relationship extractor to use
            config_path: Path to configuration file
        """
        self.document_processor = document_processor
        self.entity_recognizer = entity_recognizer
        self.relationship_extractor = relationship_extractor
        self.config = self._load_config(config_path) if config_path else {}
        
        # Data storage
        self.documents = {}
        self.entities = {}
        self.relationships = {}
        self.knowledge_graph = {}
        
        # Initialize components if not provided
        self._initialize_components()
        
        logger.info("Initialized Knowledge Extractor")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration
        """
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}
    
    def _initialize_components(self):
        """Initialize document processor, entity recognizer, and relationship extractor if not provided."""
        if not self.document_processor:
            # Initialize document processor
            from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
            self.document_processor = DocumentProcessor()
        
        if not self.entity_recognizer:
            # Initialize entity recognizer from config or create a default one
            entity_recognizer_config = self.config.get("entity_recognizer", {})
            if entity_recognizer_config:
                self.entity_recognizer = EntityRecognizerFactory.create_from_config(entity_recognizer_config)
            else:
                # Create a combined entity recognizer by default
                self.entity_recognizer = EntityRecognizerFactory.create_extractor("combined")
        
        if not self.relationship_extractor:
            # Initialize relationship extractor from config or create a default one
            relationship_extractor_config = self.config.get("relationship_extractor", {})
            if relationship_extractor_config:
                self.relationship_extractor = RelationshipExtractorFactory.create_from_config(relationship_extractor_config)
            else:
                # Create a combined relationship extractor by default
                self.relationship_extractor = RelationshipExtractorFactory.create_extractor("combined")
    
    def extract_knowledge(self, input_path: str, 
                         output_dir: Optional[str] = None,
                         **kwargs) -> Dict[str, Any]:
        """
        Extract knowledge from a document.
        
        Args:
            input_path: Path to the input document
            output_dir: Directory to save output files (if None, don't save)
            **kwargs: Additional arguments to pass to the extractors
            
        Returns:
            Dictionary containing extracted entities and relationships
        """
        try:
            # Process the document
            document_content = self.process_document(input_path)
            
            # Extract entities
            entities = self.extract_entities(document_content, **kwargs)
            
            # Extract relationships
            relationships = self.extract_relationships(document_content, entities, **kwargs)
            
            # Create knowledge graph
            knowledge_graph = self.create_knowledge_graph(entities, relationships)
            
            # Save results if output directory is provided
            if output_dir:
                self.save_results(entities, relationships, knowledge_graph, output_dir, os.path.basename(input_path))
            
            # Return results
            return {
                "entities": [e.to_dict() for e in entities],
                "relationships": [r.to_dict() for r in relationships],
                "knowledge_graph": knowledge_graph
            }
            
        except Exception as e:
            logger.error(f"Error extracting knowledge from {input_path}: {e}")
            return {"error": str(e)}
            
    def extract_from_document(self, doc_path: str, **kwargs) -> Dict[str, Any]:
        """
        Extract knowledge from a document file.
        
        Args:
            doc_path: Path to the document file
            **kwargs: Additional arguments to pass to the extractors
            
        Returns:
            Dictionary containing extraction results
        """
        import datetime
        
        try:
            # Process the document
            document = self.document_processor.process_document(doc_path)
            
            # Store the document
            self.documents[doc_path] = document
            
            # Extract entities - handle both Document objects and dictionary returns
            if hasattr(document, 'content'):
                document_content = document.content
            elif isinstance(document, dict) and 'content' in document:
                document_content = document['content']
            else:
                raise ValueError(f"Document does not have content attribute or key: {type(document)}")
                
            entities = self.entity_recognizer.recognize(document_content)
            self.entities[doc_path] = entities
            
            # Extract relationships
            relationships = self.relationship_extractor.extract_relationships(
                document_content, entities
            )
            self.relationships[doc_path] = relationships
            
            # Create knowledge graph
            graph = self._create_knowledge_graph(entities, relationships, doc_path)
            self.knowledge_graph[doc_path] = graph
            
            # Build result
            result = {
                "document_id": doc_path,
                "document_type": document.document_type,
                "extraction_time": datetime.datetime.now().isoformat(),
                "entity_count": len(entities),
                "relationship_count": len(relationships)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from document {doc_path}: {e}")
            raise
            
    def extract_from_text(self, text: str, doc_id: str = "text_content", **kwargs) -> Dict[str, Any]:
        """
        Extract knowledge from text content.
        
        Args:
            text: Text content to process
            doc_id: Identifier for the document
            **kwargs: Additional arguments to pass to the extractors
            
        Returns:
            Dictionary containing extraction results
        """
        import datetime
        
        try:
            # Process the text
            document = self.document_processor.process_text(text)
            
            # Store the document
            self.documents[doc_id] = document
            
            # Extract entities - handle both Document objects and dictionary returns
            if hasattr(document, 'content'):
                document_content = document.content
            elif isinstance(document, dict) and 'content' in document:
                document_content = document['content']
            else:
                document_content = text  # Fallback to original text
                
            entities = self.entity_recognizer.recognize(document_content)
            self.entities[doc_id] = entities
            
            # Extract relationships
            relationships = self.relationship_extractor.extract_relationships(
                document_content, entities
            )
            self.relationships[doc_id] = relationships
            
            # Create knowledge graph
            graph = self._create_knowledge_graph(entities, relationships, doc_id)
            self.knowledge_graph[doc_id] = graph
            
            # Build result
            result = {
                "document_id": doc_id,
                "document_type": "text",
                "extraction_time": datetime.datetime.now().isoformat(),
                "entity_count": len(entities),
                "relationship_count": len(relationships)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting from text: {e}")
            raise
    
    def process_document(self, input_path: str) -> str:
        """
        Process a document and extract its content.
        
        Args:
            input_path: Path to the input document
            
        Returns:
            Extracted document content
        """
        try:
            # Process the document
            processed_doc = self.document_processor.process(input_path)
            
            # Get the content
            content = processed_doc.get("content", "")
            
            logger.info(f"Processed document {input_path}, extracted {len(content)} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"Error processing document {input_path}: {e}")
            raise
    
    def extract_entities(self, text: str, **kwargs) -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: The text to analyze
            **kwargs: Additional arguments to pass to the entity recognizer
            
        Returns:
            List of extracted entities
        """
        try:
            # Extract entities
            entities = self.entity_recognizer.recognize_entities(text)
            
            # Filter entities if needed
            min_confidence = kwargs.get("min_entity_confidence", 0.0)
            entity_types = kwargs.get("entity_types")
            
            if min_confidence > 0 or entity_types:
                entities = self.entity_recognizer.filter_entities(
                    entities, min_confidence, entity_types
                )
            
            logger.info(f"Extracted {len(entities)} entities from text")
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            raise
    
    def extract_relationships(self, text: str, entities: List[Entity], **kwargs) -> List[Relationship]:
        """
        Extract relationships from text and entities.
        
        Args:
            text: The text to analyze
            entities: List of entities to find relationships between
            **kwargs: Additional arguments to pass to the relationship extractor
            
        Returns:
            List of extracted relationships
        """
        try:
            # Extract relationships
            relationships = self.relationship_extractor.extract_relationships(text, entities)
            
            # Filter relationships if needed
            min_confidence = kwargs.get("min_relationship_confidence", 0.0)
            relation_types = kwargs.get("relation_types")
            
            if min_confidence > 0 or relation_types:
                relationships = self.relationship_extractor.filter_relationships(
                    relationships, min_confidence, relation_types
                )
            
            logger.info(f"Extracted {len(relationships)} relationships from text")
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error extracting relationships: {e}")
            raise
    
    def create_knowledge_graph(self, entities: List[Entity], 
                              relationships: List[Relationship]) -> Dict[str, Any]:
        """
        Create a knowledge graph from entities and relationships.
        
        Args:
            entities: List of entities
            relationships: List of relationships
            
        Returns:
            Dictionary representing the knowledge graph
        """
        # Create nodes
        nodes = []
        for entity in entities:
            node = {
                "id": entity.id,
                "label": entity.text,
                "type": entity.type,
                "confidence": entity.confidence,
                "properties": entity.metadata
            }
            nodes.append(node)
        
        # Create edges
        edges = []
        for relationship in relationships:
            edge = {
                "id": relationship.id,
                "source": relationship.source.id if hasattr(relationship, 'source') else relationship.source_entity.id,
                "target": relationship.target.id if hasattr(relationship, 'target') else relationship.target_entity.id,
                "label": relationship.relation_type,
                "confidence": relationship.confidence,
                "properties": relationship.metadata
            }
            edges.append(edge)
        
        # Create knowledge graph
        knowledge_graph = {
            "nodes": nodes,
            "edges": edges
        }
        
        logger.info(f"Created knowledge graph with {len(nodes)} nodes and {len(edges)} edges")
        
        return knowledge_graph
        
    def _create_knowledge_graph(self, entities: List[Entity], 
                              relationships: List[Relationship],
                              doc_id: str) -> Dict[str, Any]:
        """
        Create a knowledge graph from entities and relationships with document ID.
        
        Args:
            entities: List of entities
            relationships: List of relationships
            doc_id: Document ID
            
        Returns:
            Dictionary representing the knowledge graph
        """
        import datetime
        
        # Create nodes dictionary
        nodes = {}
        for entity in entities:
            nodes[entity.id] = {
                "id": entity.id,
                "text": entity.text,
                "type": entity.type.value,
                "confidence": entity.confidence,
                "metadata": entity.metadata
            }
        
        # Create edges dictionary
        edges = {}
        for relationship in relationships:
            source_id = relationship.source.id if hasattr(relationship, 'source') else relationship.source_entity.id
            target_id = relationship.target.id if hasattr(relationship, 'target') else relationship.target_entity.id
            
            edges[relationship.id] = {
                "id": relationship.id,
                "source": source_id,
                "target": target_id,
                "type": relationship.relation_type.value,
                "confidence": relationship.confidence,
                "metadata": relationship.metadata
            }
        
        # Create knowledge graph
        knowledge_graph = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "document_id": doc_id,
                "created_at": datetime.datetime.now().isoformat()
            }
        }
        
        logger.info(f"Created knowledge graph with {len(nodes)} nodes and {len(edges)} edges")
        
        return knowledge_graph
    
    def save_results(self, entities: List[Entity], relationships: List[Relationship],
                    knowledge_graph: Dict[str, Any], output_dir: str, doc_name: str):
        """
        Save results to output directory.
        
        Args:
            entities: List of entities
            relationships: List of relationships
            knowledge_graph: Knowledge graph dictionary
            output_dir: Output directory
            doc_name: Document name
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Create document directory
            doc_dir = os.path.join(output_dir, os.path.splitext(doc_name)[0])
            os.makedirs(doc_dir, exist_ok=True)
            
            # Save entities
            entity_path = os.path.join(doc_dir, "entities.json")
            with open(entity_path, 'w') as f:
                json.dump([e.to_dict() for e in entities], f, indent=2)
            
            # Save relationships
            relationship_path = os.path.join(doc_dir, "relationships.json")
            with open(relationship_path, 'w') as f:
                json.dump([r.to_dict() for r in relationships], f, indent=2)
            
            # Save knowledge graph
            graph_path = os.path.join(doc_dir, "knowledge_graph.json")
            with open(graph_path, 'w') as f:
                json.dump(knowledge_graph, f, indent=2)
            
            logger.info(f"Saved results to {doc_dir}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def analyze_results(self, entities: List[Entity], 
                       relationships: List[Relationship]) -> Dict[str, Any]:
        """
        Analyze the extraction results.
        
        Args:
            entities: List of entities
            relationships: List of relationships
            
        Returns:
            Dictionary containing analysis results
        """
        # Entity analysis
        entity_count_by_type = {}
        for entity in entities:
            if entity.type not in entity_count_by_type:
                entity_count_by_type[entity.type] = 0
            entity_count_by_type[entity.type] += 1
        
        # Relationship analysis
        relationship_count_by_type = {}
        for relationship in relationships:
            if relationship.relation_type not in relationship_count_by_type:
                relationship_count_by_type[relationship.relation_type] = 0
            relationship_count_by_type[relationship.relation_type] += 1
        
        # Entity pairs analysis
        entity_pair_counts = {}
        for relationship in relationships:
            source_type = relationship.source_entity.type
            target_type = relationship.target_entity.type
            pair_key = f"{source_type}_{target_type}"
            
            if pair_key not in entity_pair_counts:
                entity_pair_counts[pair_key] = 0
            entity_pair_counts[pair_key] += 1
        
        # Confidence analysis
        entity_confidence = [entity.confidence for entity in entities]
        relationship_confidence = [relationship.confidence for relationship in relationships]
        
        avg_entity_confidence = sum(entity_confidence) / len(entity_confidence) if entity_confidence else 0
        avg_relationship_confidence = sum(relationship_confidence) / len(relationship_confidence) if relationship_confidence else 0
        
        # Create analysis results
        analysis = {
            "entity_count": len(entities),
            "relationship_count": len(relationships),
            "entity_count_by_type": entity_count_by_type,
            "relationship_count_by_type": relationship_count_by_type,
            "entity_pair_counts": entity_pair_counts,
            "avg_entity_confidence": avg_entity_confidence,
            "avg_relationship_confidence": avg_relationship_confidence
        }
        
        return analysis
    
    def batch_process(self, input_dir: str, output_dir: str,
                     file_pattern: str = "*",
                     **kwargs) -> List[Dict[str, Any]]:
        """
        Process a batch of documents.
        
        Args:
            input_dir: Input directory containing documents
            output_dir: Output directory to save results
            file_pattern: File pattern to match documents
            **kwargs: Additional arguments to pass to the extractors
            
        Returns:
            List of dictionaries containing results for each document
        """
        import glob
        
        # Get all files matching the pattern
        files = glob.glob(os.path.join(input_dir, file_pattern))
        
        results = []
        
        for file_path in files:
            try:
                # Extract knowledge from the document
                result = self.extract_knowledge(file_path, output_dir, **kwargs)
                
                # Add document path to the result
                result["document_path"] = file_path
                
                results.append(result)
                
                logger.info(f"Processed document {file_path}")
                
            except Exception as e:
                logger.error(f"Error processing document {file_path}: {e}")
                results.append({
                    "document_path": file_path,
                    "error": str(e)
                })
        
        logger.info(f"Processed {len(results)} documents")
        
        return results
        
    def save_extraction_results(self, temp_dir, doc_id):
        """
        Save extraction results to files.
        
        Args:
            temp_dir: Directory to save results
            doc_id: Document ID
            
        Returns:
            Path to the output directory
        """
        output_dir = os.path.join(temp_dir, f"{doc_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save entities
        entity_file = os.path.join(output_dir, "entities.json")
        with open(entity_file, 'w') as f:
            json.dump([e.to_dict() for e in self.entities[doc_id]], f, indent=2)
        
        # Save relationships
        relationship_file = os.path.join(output_dir, "relationships.json")
        with open(relationship_file, 'w') as f:
            json.dump([r.to_dict() for r in self.relationships[doc_id]], f, indent=2)
        
        # Save knowledge graph
        graph_file = os.path.join(output_dir, "knowledge_graph.json")
        with open(graph_file, 'w') as f:
            json.dump(self.knowledge_graph[doc_id], f, indent=2)
        
        # Save stats
        stats_file = os.path.join(temp_dir, "extraction_statistics.json")
        with open(stats_file, 'w') as f:
            json.dump(self.get_extraction_statistics(), f, indent=2)
        
        return output_dir
        
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about extracted entities and relationships.
        
        Returns:
            Dictionary containing statistics
        """
        # Document statistics
        document_count = len(self.documents)
        
        # Entity statistics
        all_entities = []
        for doc_entities in self.entities.values():
            all_entities.extend(doc_entities)
        
        entity_count = len(all_entities)
        entity_by_type = self._get_entity_type_statistics(all_entities)
        
        # Calculate average confidence
        if entity_count > 0:
            avg_entity_confidence = sum(e.confidence for e in all_entities) / entity_count
        else:
            avg_entity_confidence = 0.0
        
        # Relationship statistics
        all_relationships = []
        for doc_relationships in self.relationships.values():
            all_relationships.extend(doc_relationships)
        
        relationship_count = len(all_relationships)
        relationship_by_type = self._get_relationship_type_statistics(all_relationships)
        
        # Calculate average confidence
        if relationship_count > 0:
            avg_relationship_confidence = sum(r.confidence for r in all_relationships) / relationship_count
        else:
            avg_relationship_confidence = 0.0
        
        # Knowledge graph statistics
        total_nodes = sum(len(g["nodes"]) for g in self.knowledge_graph.values())
        total_edges = sum(len(g["edges"]) for g in self.knowledge_graph.values())
        
        # Build the statistics dictionary
        statistics = {
            "documents": {
                "count": document_count
            },
            "entities": {
                "count": entity_count,
                "by_type": entity_by_type,
                "avg_confidence": avg_entity_confidence
            },
            "relationships": {
                "count": relationship_count,
                "by_type": relationship_by_type,
                "avg_confidence": avg_relationship_confidence
            },
            "knowledge_graph": {
                "total_nodes": total_nodes,
                "total_edges": total_edges
            }
        }
        
        return statistics
        
    def _get_entity_type_statistics(self, entities: List[Entity]) -> Dict[str, int]:
        """
        Calculate entity counts by type.
        
        Args:
            entities: List of entities
            
        Returns:
            Dictionary mapping entity types to counts
        """
        type_counts = {}
        
        for entity in entities:
            type_value = entity.type.value
            if type_value not in type_counts:
                type_counts[type_value] = 0
            type_counts[type_value] += 1
        
        return type_counts
        
    def _get_relationship_type_statistics(self, relationships: List[Relationship]) -> Dict[str, int]:
        """
        Calculate relationship counts by type.
        
        Args:
            relationships: List of relationships
            
        Returns:
            Dictionary mapping relationship types to counts
        """
        type_counts = {}
        
        for relationship in relationships:
            type_value = relationship.relation_type.value
            if type_value not in type_counts:
                type_counts[type_value] = 0
            type_counts[type_value] += 1
        
        return type_counts