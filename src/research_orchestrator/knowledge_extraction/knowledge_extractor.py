"""
Knowledge Extractor module for the Research Orchestration Framework.

This module provides the coordinator for the Knowledge Extraction Pipeline,
integrating document processing, entity recognition, and relationship extraction
into a cohesive workflow that produces structured knowledge from research documents.
"""

from typing import List, Dict, Any, Optional, Set, Union, Tuple
import logging
import os
import json
import time
from pathlib import Path

# Import document processing components
from .document_processing import DocumentProcessor, PDFProcessor, HTMLProcessor, TextProcessor

# Import entity recognition components
from .entity_recognition import (
    EntityRecognizerFactory, Entity, EntityType, EntityRecognizer
)

# Import relationship extraction components
from .relationship_extraction import (
    RelationshipExtractorFactory, Relationship, RelationType, RelationshipExtractor
)

logger = logging.getLogger(__name__)


class KnowledgeExtractor:
    """Coordinator for the Knowledge Extraction Pipeline.
    
    This class orchestrates the extraction of structured knowledge from
    research documents, coordinating document processing, entity recognition,
    and relationship extraction components.
    """
    
    def __init__(
        self, 
        config: Optional[Dict[str, Any]] = None,
        document_processor: Optional[DocumentProcessor] = None,
        entity_recognizer: Optional[EntityRecognizer] = None,
        relationship_extractor: Optional[RelationshipExtractor] = None
    ):
        """Initialize the Knowledge Extractor.
        
        Args:
            config: Configuration dictionary for the extractor
            document_processor: Optional pre-configured DocumentProcessor
            entity_recognizer: Optional pre-configured EntityRecognizer
            relationship_extractor: Optional pre-configured RelationshipExtractor
        """
        self.config = config or {}
        
        # Initialize components based on configuration or use provided instances
        self.document_processor = document_processor or self._create_document_processor()
        self.entity_recognizer = entity_recognizer or self._create_entity_recognizer()
        self.relationship_extractor = relationship_extractor or self._create_relationship_extractor()
        
        # Initialize extraction results storage
        self.documents = {}
        self.entities = {}
        self.relationships = {}
        self.knowledge_graph = {}
        
        # Extraction configuration
        self.entity_confidence_threshold = self.config.get("entity_confidence_threshold", 0.5)
        self.relationship_confidence_threshold = self.config.get("relationship_confidence_threshold", 0.6)
        self.extraction_batch_size = self.config.get("extraction_batch_size", 5)
        self.parallel_processing = self.config.get("parallel_processing", False)
    
    def _create_document_processor(self) -> DocumentProcessor:
        """Create a document processor based on configuration.
        
        Returns:
            Configured DocumentProcessor instance
        """
        processor_config = self.config.get("document_processor", {})
        return DocumentProcessor(config=processor_config)
    
    def _create_entity_recognizer(self) -> EntityRecognizer:
        """Create an entity recognizer based on configuration.
        
        Returns:
            Configured EntityRecognizer instance
        """
        recognizer_type = self.config.get("entity_recognizer_type", "combined")
        recognizer_config = self.config.get("entity_recognizer", {})
        
        return EntityRecognizerFactory.create_recognizer(
            recognizer_type, config=recognizer_config
        )
    
    def _create_relationship_extractor(self) -> RelationshipExtractor:
        """Create a relationship extractor based on configuration.
        
        Returns:
            Configured RelationshipExtractor instance
        """
        extractor_type = self.config.get("relationship_extractor_type", "combined")
        extractor_config = self.config.get("relationship_extractor", {})
        
        return RelationshipExtractorFactory.create_extractor(
            extractor_type, config=extractor_config
        )
    
    def extract_from_document(
        self, 
        document_path: str,
        document_id: Optional[str] = None,
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract knowledge from a single document.
        
        Args:
            document_path: Path to the document file
            document_id: Optional identifier for the document
            document_metadata: Optional metadata for the document
            
        Returns:
            Dictionary with extraction results
        """
        # Process the document
        doc_id = document_id or os.path.basename(document_path)
        metadata = document_metadata or {}
        
        logger.info(f"Processing document: {doc_id}")
        start_time = time.time()
        
        try:
            # Process the document to extract content
            processed_doc = self.document_processor.process_document(document_path)
            self.documents[doc_id] = processed_doc
            
            # Extract text content for analysis
            document_text = processed_doc.get_text()
            
            # Extract entities from the document
            entities = self.entity_recognizer.recognize(document_text)
            filtered_entities = self.entity_recognizer.filter_entities(
                entities, min_confidence=self.entity_confidence_threshold
            )
            self.entities[doc_id] = filtered_entities
            
            # Extract relationships between entities
            relationships = self.relationship_extractor.extract_relationships(
                document_text, filtered_entities
            )
            filtered_relationships = self.relationship_extractor.filter_relationships(
                relationships, min_confidence=self.relationship_confidence_threshold
            )
            self.relationships[doc_id] = filtered_relationships
            
            # Create knowledge graph from extracted information
            document_graph = self._create_knowledge_graph(
                filtered_entities, filtered_relationships, doc_id
            )
            self.knowledge_graph[doc_id] = document_graph
            
            processing_time = time.time() - start_time
            
            # Compile extraction results
            extraction_results = {
                "document_id": doc_id,
                "document_metadata": metadata,
                "document_type": processed_doc.document_type,
                "extraction_time": processing_time,
                "entity_count": len(filtered_entities),
                "relationship_count": len(filtered_relationships),
                "entity_types": self._count_by_type(filtered_entities, "type"),
                "relationship_types": self._count_by_type(filtered_relationships, "relation_type"),
                "confidence": {
                    "entity_avg": self._average_confidence(filtered_entities),
                    "relationship_avg": self._average_confidence(filtered_relationships)
                }
            }
            
            logger.info(f"Extraction complete for {doc_id}. Found {len(filtered_entities)} entities and {len(filtered_relationships)} relationships in {processing_time:.2f} seconds")
            
            return extraction_results
            
        except Exception as e:
            logger.error(f"Error extracting knowledge from {doc_id}: {e}")
            raise
    
    def extract_from_directory(
        self, 
        directory_path: str,
        file_extensions: Optional[List[str]] = None,
        recursive: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """Extract knowledge from all documents in a directory.
        
        Args:
            directory_path: Path to the directory containing documents
            file_extensions: List of file extensions to process (e.g., [".pdf", ".html"])
            recursive: Whether to process subdirectories recursively
            
        Returns:
            Dictionary mapping document IDs to extraction results
        """
        extensions = file_extensions or [".pdf", ".html", ".txt", ".md"]
        
        # Find all document files
        if recursive:
            file_paths = []
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_paths.append(os.path.join(root, file))
        else:
            file_paths = [
                os.path.join(directory_path, f) for f in os.listdir(directory_path)
                if os.path.isfile(os.path.join(directory_path, f)) and
                any(f.endswith(ext) for ext in extensions)
            ]
        
        # Extract knowledge from each document
        results = {}
        for file_path in file_paths:
            doc_id = os.path.basename(file_path)
            try:
                results[doc_id] = self.extract_from_document(file_path, doc_id)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results[doc_id] = {"error": str(e)}
        
        return results
    
    def extract_from_text(
        self,
        text: str,
        document_id: str = "text_content",
        document_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract knowledge directly from text content.
        
        Args:
            text: Text content to analyze
            document_id: Identifier for the text content
            document_metadata: Optional metadata for the content
            
        Returns:
            Dictionary with extraction results
        """
        metadata = document_metadata or {}
        logger.info(f"Processing text content with ID: {document_id}")
        start_time = time.time()
        
        try:
            # Create a document object for the text
            from .document_processing.document_processor import Document
            text_document = Document(
                content=text,
                document_type="text",
                metadata=metadata,
                path=None
            )
            self.documents[document_id] = text_document
            
            # Extract entities from the text
            entities = self.entity_recognizer.recognize(text)
            filtered_entities = self.entity_recognizer.filter_entities(
                entities, min_confidence=self.entity_confidence_threshold
            )
            self.entities[document_id] = filtered_entities
            
            # Extract relationships between entities
            relationships = self.relationship_extractor.extract_relationships(
                text, filtered_entities
            )
            filtered_relationships = self.relationship_extractor.filter_relationships(
                relationships, min_confidence=self.relationship_confidence_threshold
            )
            self.relationships[document_id] = filtered_relationships
            
            # Create knowledge graph from extracted information
            document_graph = self._create_knowledge_graph(
                filtered_entities, filtered_relationships, document_id
            )
            self.knowledge_graph[document_id] = document_graph
            
            processing_time = time.time() - start_time
            
            # Compile extraction results
            extraction_results = {
                "document_id": document_id,
                "document_metadata": metadata,
                "document_type": "text",
                "extraction_time": processing_time,
                "entity_count": len(filtered_entities),
                "relationship_count": len(filtered_relationships),
                "entity_types": self._count_by_type(filtered_entities, "type"),
                "relationship_types": self._count_by_type(filtered_relationships, "relation_type"),
                "confidence": {
                    "entity_avg": self._average_confidence(filtered_entities),
                    "relationship_avg": self._average_confidence(filtered_relationships)
                }
            }
            
            logger.info(f"Extraction complete for {document_id}. Found {len(filtered_entities)} entities and {len(filtered_relationships)} relationships in {processing_time:.2f} seconds")
            
            return extraction_results
            
        except Exception as e:
            logger.error(f"Error extracting knowledge from text {document_id}: {e}")
            raise
    
    def _create_knowledge_graph(
        self,
        entities: List[Entity],
        relationships: List[Relationship],
        graph_id: str
    ) -> Dict[str, Any]:
        """Create a knowledge graph from extracted entities and relationships.
        
        Args:
            entities: List of extracted entities
            relationships: List of extracted relationships
            graph_id: Identifier for the graph
            
        Returns:
            Dictionary representation of the knowledge graph
        """
        # Create nodes from entities
        nodes = {
            entity.id: {
                "id": entity.id,
                "label": entity.text,
                "type": str(entity.type),
                "confidence": entity.confidence,
                "metadata": entity.metadata
            }
            for entity in entities
        }
        
        # Create edges from relationships
        edges = {
            relationship.id: {
                "id": relationship.id,
                "source": relationship.source.id,
                "target": relationship.target.id,
                "type": str(relationship.relation_type),
                "confidence": relationship.confidence,
                "bidirectional": relationship.bidirectional,
                "metadata": relationship.metadata
            }
            for relationship in relationships
            if relationship.source is not None and relationship.target is not None
        }
        
        # Create the graph structure
        graph = {
            "id": graph_id,
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "creation_timestamp": time.time()
            }
        }
        
        return graph
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about all extractions.
        
        Returns:
            Dictionary with extraction statistics
        """
        # Ensure we have extraction results
        if not self.documents:
            return {"status": "No extractions performed yet"}
        
        # Collect all entities and relationships
        all_entities = []
        all_relationships = []
        for doc_id in self.documents:
            all_entities.extend(self.entities.get(doc_id, []))
            all_relationships.extend(self.relationships.get(doc_id, []))
        
        # Compute statistics
        stats = {
            "documents": {
                "count": len(self.documents),
                "types": self._count_document_types()
            },
            "entities": {
                "count": len(all_entities),
                "by_type": self._count_by_type(all_entities, "type"),
                "avg_confidence": self._average_confidence(all_entities)
            },
            "relationships": {
                "count": len(all_relationships),
                "by_type": self._count_by_type(all_relationships, "relation_type"),
                "avg_confidence": self._average_confidence(all_relationships)
            },
            "knowledge_graph": {
                "count": len(self.knowledge_graph),
                "total_nodes": sum(graph.get("metadata", {}).get("node_count", 0) 
                                 for graph in self.knowledge_graph.values()),
                "total_edges": sum(graph.get("metadata", {}).get("edge_count", 0) 
                                 for graph in self.knowledge_graph.values())
            }
        }
        
        return stats
    
    def _count_document_types(self) -> Dict[str, int]:
        """Count the number of documents by type.
        
        Returns:
            Dictionary mapping document types to counts
        """
        type_counts = {}
        for doc_id, doc in self.documents.items():
            doc_type = getattr(doc, "document_type", "unknown")
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        return type_counts
    
    def _count_by_type(self, items: List[Any], type_attr: str) -> Dict[str, int]:
        """Count items by their type attribute.
        
        Args:
            items: List of items to count
            type_attr: Name of the type attribute
            
        Returns:
            Dictionary mapping types to counts
        """
        type_counts = {}
        for item in items:
            item_type = getattr(item, type_attr, None)
            if item_type:
                type_str = str(item_type)
                type_counts[type_str] = type_counts.get(type_str, 0) + 1
        return type_counts
    
    def _average_confidence(self, items: List[Any]) -> float:
        """Calculate the average confidence score for a list of items.
        
        Args:
            items: List of items with confidence scores
            
        Returns:
            Average confidence score (0.0 if list is empty)
        """
        if not items:
            return 0.0
        return sum(getattr(item, "confidence", 0.0) for item in items) / len(items)
    
    def save_extraction_results(
        self,
        output_directory: str,
        document_id: Optional[str] = None
    ) -> str:
        """Save extraction results to files.
        
        Args:
            output_directory: Directory to save results
            document_id: Optional document ID to save (all if None)
            
        Returns:
            Path to the saved results
        """
        # Create the output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Determine which documents to save
        doc_ids = [document_id] if document_id else list(self.documents.keys())
        
        for doc_id in doc_ids:
            # Skip if document doesn't exist
            if doc_id not in self.documents:
                logger.warning(f"Document {doc_id} not found in extraction results")
                continue
            
            # Create document-specific directory
            doc_dir = os.path.join(output_directory, doc_id)
            os.makedirs(doc_dir, exist_ok=True)
            
            # Save entities
            if doc_id in self.entities:
                entity_path = os.path.join(doc_dir, "entities.json")
                with open(entity_path, 'w', encoding='utf-8') as f:
                    json.dump([e.to_dict() for e in self.entities[doc_id]], f, indent=2)
            
            # Save relationships
            if doc_id in self.relationships:
                rel_path = os.path.join(doc_dir, "relationships.json")
                with open(rel_path, 'w', encoding='utf-8') as f:
                    json.dump([r.to_dict() for r in self.relationships[doc_id]], f, indent=2)
            
            # Save knowledge graph
            if doc_id in self.knowledge_graph:
                graph_path = os.path.join(doc_dir, "knowledge_graph.json")
                with open(graph_path, 'w', encoding='utf-8') as f:
                    json.dump(self.knowledge_graph[doc_id], f, indent=2)
            
            logger.info(f"Saved extraction results for {doc_id} to {doc_dir}")
        
        # Save overall statistics
        stats_path = os.path.join(output_directory, "extraction_statistics.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.get_extraction_statistics(), f, indent=2)
        
        return output_directory
    
    def load_extraction_results(
        self,
        input_directory: str,
        document_id: Optional[str] = None
    ) -> None:
        """Load extraction results from files.
        
        Args:
            input_directory: Directory containing saved results
            document_id: Optional document ID to load (all if None)
        """
        # Determine which documents to load
        if document_id:
            doc_dirs = [os.path.join(input_directory, document_id)]
        else:
            doc_dirs = [
                os.path.join(input_directory, d) for d in os.listdir(input_directory)
                if os.path.isdir(os.path.join(input_directory, d))
            ]
        
        for doc_dir in doc_dirs:
            doc_id = os.path.basename(doc_dir)
            
            # Load entities
            entity_path = os.path.join(doc_dir, "entities.json")
            if os.path.exists(entity_path):
                with open(entity_path, 'r', encoding='utf-8') as f:
                    entity_dicts = json.load(f)
                    self.entities[doc_id] = [Entity.from_dict(e_dict) for e_dict in entity_dicts]
            
            # Load relationships
            rel_path = os.path.join(doc_dir, "relationships.json")
            if os.path.exists(rel_path):
                with open(rel_path, 'r', encoding='utf-8') as f:
                    rel_dicts = json.load(f)
                    self.relationships[doc_id] = [Relationship.from_dict(r_dict) for r_dict in rel_dicts]
            
            # Load knowledge graph
            graph_path = os.path.join(doc_dir, "knowledge_graph.json")
            if os.path.exists(graph_path):
                with open(graph_path, 'r', encoding='utf-8') as f:
                    self.knowledge_graph[doc_id] = json.load(f)
            
            logger.info(f"Loaded extraction results for {doc_id} from {doc_dir}")
    
    def query_knowledge_graph(
        self,
        query: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query the knowledge graph for specific patterns.
        
        Args:
            query: Query specification
            document_id: Optional document ID to query (all if None)
            
        Returns:
            List of matching results
        """
        # Determine which documents to query
        graph_ids = [document_id] if document_id else list(self.knowledge_graph.keys())
        
        # Filter to only existing graphs
        graph_ids = [gid for gid in graph_ids if gid in self.knowledge_graph]
        
        if not graph_ids:
            return []
        
        results = []
        
        # Process query based on type
        query_type = query.get("type", "entity")
        
        if query_type == "entity":
            # Query for entities
            entity_type = query.get("entity_type")
            min_confidence = query.get("min_confidence", 0.0)
            keywords = query.get("keywords", [])
            
            for graph_id in graph_ids:
                graph = self.knowledge_graph[graph_id]
                
                for node_id, node in graph.get("nodes", {}).items():
                    # Check entity type if specified
                    if entity_type and node.get("type") != entity_type:
                        continue
                    
                    # Check confidence
                    if node.get("confidence", 0.0) < min_confidence:
                        continue
                    
                    # Check keywords
                    if keywords and not any(kw.lower() in node.get("label", "").lower() for kw in keywords):
                        continue
                    
                    # Add to results
                    result = {
                        "type": "entity",
                        "document_id": graph_id,
                        "entity": node
                    }
                    results.append(result)
        
        elif query_type == "relationship":
            # Query for relationships
            relation_type = query.get("relation_type")
            min_confidence = query.get("min_confidence", 0.0)
            source_type = query.get("source_type")
            target_type = query.get("target_type")
            
            for graph_id in graph_ids:
                graph = self.knowledge_graph[graph_id]
                nodes = graph.get("nodes", {})
                
                for edge_id, edge in graph.get("edges", {}).items():
                    # Check relationship type if specified
                    if relation_type and edge.get("type") != relation_type:
                        continue
                    
                    # Check confidence
                    if edge.get("confidence", 0.0) < min_confidence:
                        continue
                    
                    # Get source and target nodes
                    source_id = edge.get("source")
                    target_id = edge.get("target")
                    
                    if source_id not in nodes or target_id not in nodes:
                        continue
                    
                    source_node = nodes[source_id]
                    target_node = nodes[target_id]
                    
                    # Check source type if specified
                    if source_type and source_node.get("type") != source_type:
                        continue
                    
                    # Check target type if specified
                    if target_type and target_node.get("type") != target_type:
                        continue
                    
                    # Add to results
                    result = {
                        "type": "relationship",
                        "document_id": graph_id,
                        "relationship": edge,
                        "source": source_node,
                        "target": target_node
                    }
                    results.append(result)
        
        elif query_type == "path":
            # Query for paths between entities
            start_entity = query.get("start_entity")
            end_entity = query.get("end_entity")
            max_length = query.get("max_length", 3)
            
            if not start_entity or not end_entity:
                return []
            
            for graph_id in graph_ids:
                paths = self._find_paths(graph_id, start_entity, end_entity, max_length)
                for path in paths:
                    result = {
                        "type": "path",
                        "document_id": graph_id,
                        "path": path
                    }
                    results.append(result)
        
        return results
    
    def _find_paths(
        self,
        graph_id: str,
        start_entity: str,
        end_entity: str,
        max_length: int = 3
    ) -> List[List[Dict[str, Any]]]:
        """Find paths between two entities in the knowledge graph.
        
        Args:
            graph_id: ID of the graph to search
            start_entity: Starting entity text or ID
            end_entity: Ending entity text or ID
            max_length: Maximum path length
            
        Returns:
            List of paths, where each path is a list of edges
        """
        if graph_id not in self.knowledge_graph:
            return []
        
        graph = self.knowledge_graph[graph_id]
        nodes = graph.get("nodes", {})
        edges = graph.get("edges", {})
        
        # Find node IDs for start and end entities
        start_ids = []
        end_ids = []
        
        for node_id, node in nodes.items():
            if node.get("id") == start_entity or node.get("label") == start_entity:
                start_ids.append(node_id)
            if node.get("id") == end_entity or node.get("label") == end_entity:
                end_ids.append(node_id)
        
        if not start_ids or not end_ids:
            return []
        
        # Build an adjacency list for the graph
        adjacency_list = {}
        for edge_id, edge in edges.items():
            source_id = edge.get("source")
            target_id = edge.get("target")
            
            if source_id and target_id:
                if source_id not in adjacency_list:
                    adjacency_list[source_id] = []
                adjacency_list[source_id].append((target_id, edge_id))
                
                # Add reverse direction for bidirectional edges
                if edge.get("bidirectional"):
                    if target_id not in adjacency_list:
                        adjacency_list[target_id] = []
                    adjacency_list[target_id].append((source_id, edge_id))
        
        # Find paths using BFS
        all_paths = []
        
        for start_id in start_ids:
            for end_id in end_ids:
                paths = self._bfs_paths(adjacency_list, start_id, end_id, max_length, edges, nodes)
                all_paths.extend(paths)
        
        return all_paths
    
    def _bfs_paths(
        self,
        adjacency_list: Dict[str, List[Tuple[str, str]]],
        start_id: str,
        end_id: str,
        max_length: int,
        edges: Dict[str, Dict[str, Any]],
        nodes: Dict[str, Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Find paths between two nodes using BFS.
        
        Args:
            adjacency_list: Adjacency list representation of the graph
            start_id: Starting node ID
            end_id: Ending node ID
            max_length: Maximum path length
            edges: Dictionary of edge data
            nodes: Dictionary of node data
            
        Returns:
            List of paths between start and end nodes
        """
        # Queue of paths, where each path is a list of (node_id, edge_id) tuples
        queue = [[(start_id, None)]]
        paths = []
        
        while queue:
            path = queue.pop(0)
            current_id, _ = path[-1]
            
            # Stop if we've reached the maximum path length
            if len(path) > max_length + 1:
                continue
            
            # Check if we've reached the end node
            if current_id == end_id and len(path) > 1:
                # Convert path to a list of edges
                edge_path = []
                for i in range(1, len(path)):
                    _, edge_id = path[i]
                    source_id, _ = path[i-1]
                    target_id, _ = path[i]
                    
                    edge_data = edges.get(edge_id, {}).copy()
                    edge_data.update({
                        "source_node": nodes.get(source_id, {}),
                        "target_node": nodes.get(target_id, {})
                    })
                    edge_path.append(edge_data)
                
                paths.append(edge_path)
                continue
            
            # Expand the path with adjacent nodes
            if current_id in adjacency_list:
                for neighbor_id, edge_id in adjacency_list[current_id]:
                    # Avoid cycles
                    if any(node_id == neighbor_id for node_id, _ in path):
                        continue
                    
                    new_path = path + [(neighbor_id, edge_id)]
                    queue.append(new_path)
        
        return paths