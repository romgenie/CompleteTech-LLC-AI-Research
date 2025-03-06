"""
Extraction integration for the Paper Processing Pipeline.

This module provides an adapter for integrating the Paper Processing Pipeline
with the Knowledge Extraction Pipeline. It handles document processing, entity
recognition, and relationship extraction to extract knowledge from papers.

Current Implementation Status:
- Adapter interface defined ✓
- Document processing methods defined ✓
- Entity and relationship extraction defined ✓

Upcoming Development:
- Complete integration with extraction pipeline
- Advanced extraction configuration
- Quality assessment and validation
- Extraction performance optimization
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, BinaryIO
import uuid
import os
import tempfile

# Import the Knowledge Extraction Pipeline interfaces
from src.research_orchestrator.knowledge_extraction.document_processing.document_processor import DocumentProcessor
from src.research_orchestrator.knowledge_extraction.entity_recognition.base_recognizer import EntityRecognizer
from src.research_orchestrator.knowledge_extraction.relationship_extraction.base_extractor import RelationshipExtractor
from src.research_orchestrator.knowledge_extraction.knowledge_extractor import KnowledgeExtractor

# Import the Paper Processing models
from ..models.paper import Paper, Entity, Relationship, PaperStatus


logger = logging.getLogger(__name__)


class ExtractionAdapter:
    """
    Adapter for Knowledge Extraction integration.
    
    This class provides methods for integrating papers with the Knowledge
    Extraction Pipeline, processing documents, and extracting entities and
    relationships.
    """
    
    def __init__(
        self,
        document_processor: DocumentProcessor,
        entity_recognizer: EntityRecognizer,
        relationship_extractor: RelationshipExtractor,
        knowledge_extractor: KnowledgeExtractor
    ):
        """
        Initialize the Extraction adapter.
        
        Args:
            document_processor: Document processor for parsing documents
            entity_recognizer: Entity recognizer for identifying entities
            relationship_extractor: Relationship extractor for identifying relationships
            knowledge_extractor: Knowledge extractor for coordinating extraction
        """
        self.document_processor = document_processor
        self.entity_recognizer = entity_recognizer
        self.relationship_extractor = relationship_extractor
        self.knowledge_extractor = knowledge_extractor
    
    async def process_document(self, paper: Paper, file_path: str) -> Dict[str, Any]:
        """
        Process a document file to extract text content.
        
        Args:
            paper: The paper metadata
            file_path: Path to the document file
            
        Returns:
            Dict with the processed document result
            
        Raises:
            Exception: If document processing fails
        """
        try:
            # Determine document type from content_type
            document_type = None
            if paper.content_type == 'application/pdf':
                document_type = 'pdf'
            elif paper.content_type in ['text/html', 'application/xhtml+xml']:
                document_type = 'html'
            elif paper.content_type == 'text/plain':
                document_type = 'text'
            else:
                document_type = 'text'  # Default to text
            
            # Process the document
            processed_document = await self.document_processor.process(
                file_path, document_type=document_type
            )
            
            # Extract metadata if not available in paper
            metadata = processed_document.metadata
            
            # Update paper metadata if not already set
            updates = {}
            if not paper.title and metadata.get('title'):
                updates['title'] = metadata['title']
            
            if not paper.abstract and metadata.get('abstract'):
                updates['abstract'] = metadata['abstract']
            
            if not paper.authors and metadata.get('authors'):
                updates['authors'] = metadata['authors']
            
            if not paper.year and metadata.get('year'):
                updates['year'] = metadata['year']
            
            logger.info(f"Processed document for paper {paper.id}")
            
            return {
                'status': 'success',
                'document_id': processed_document.id,
                'content_length': len(processed_document.content),
                'metadata': metadata,
                'updates': updates
            }
        except Exception as e:
            logger.error(f"Failed to process document for paper {paper.id}: {e}")
            raise
    
    async def extract_entities(self, paper: Paper, document_id: str) -> Dict[str, Any]:
        """
        Extract entities from a processed document.
        
        Args:
            paper: The paper metadata
            document_id: ID of the processed document
            
        Returns:
            Dict with the extracted entities result
            
        Raises:
            Exception: If entity extraction fails
        """
        try:
            # Get the processed document
            document = await self.document_processor.get_document(document_id)
            
            # Extract entities
            entities = await self.entity_recognizer.extract_entities(document.content)
            
            # Convert to Paper.Entity format
            paper_entities = []
            for entity in entities:
                paper_entity = Entity(
                    id=str(uuid.uuid4()),
                    type=entity.type,
                    name=entity.name,
                    confidence=entity.confidence,
                    context=entity.context,
                    metadata=entity.metadata
                )
                paper_entities.append(paper_entity)
            
            logger.info(f"Extracted {len(paper_entities)} entities for paper {paper.id}")
            
            return {
                'status': 'success',
                'entity_count': len(paper_entities),
                'entities': paper_entities
            }
        except Exception as e:
            logger.error(f"Failed to extract entities for paper {paper.id}: {e}")
            raise
    
    async def extract_relationships(
        self,
        paper: Paper,
        document_id: str,
        entities: List[Entity]
    ) -> Dict[str, Any]:
        """
        Extract relationships from a processed document.
        
        Args:
            paper: The paper metadata
            document_id: ID of the processed document
            entities: List of extracted entities
            
        Returns:
            Dict with the extracted relationships result
            
        Raises:
            Exception: If relationship extraction fails
        """
        try:
            # Get the processed document
            document = await self.document_processor.get_document(document_id)
            
            # Extract relationships
            relationships = await self.relationship_extractor.extract_relationships(
                document.content, 
                [entity.name for entity in entities]
            )
            
            # Create entity name to ID mapping
            entity_map = {entity.name: entity.id for entity in entities}
            
            # Convert to Paper.Relationship format
            paper_relationships = []
            for rel in relationships:
                # Skip if source or target not found
                if rel.source not in entity_map or rel.target not in entity_map:
                    continue
                
                paper_rel = Relationship(
                    id=str(uuid.uuid4()),
                    type=rel.type,
                    source_id=entity_map[rel.source],
                    target_id=entity_map[rel.target],
                    confidence=rel.confidence,
                    context=rel.context,
                    metadata=rel.metadata
                )
                paper_relationships.append(paper_rel)
            
            logger.info(f"Extracted {len(paper_relationships)} relationships for paper {paper.id}")
            
            return {
                'status': 'success',
                'relationship_count': len(paper_relationships),
                'relationships': paper_relationships
            }
        except Exception as e:
            logger.error(f"Failed to extract relationships for paper {paper.id}: {e}")
            raise
    
    async def process_paper(self, paper: Paper) -> Dict[str, Any]:
        """
        Process a paper through the entire extraction pipeline.
        
        Args:
            paper: The paper to process
            
        Returns:
            Dict with the processing result
            
        Raises:
            Exception: If processing fails
        """
        try:
            # Process the document
            doc_result = await self.process_document(paper, paper.file_path)
            document_id = doc_result['document_id']
            
            # Extract entities
            entity_result = await self.extract_entities(paper, document_id)
            entities = entity_result['entities']
            
            # Extract relationships
            relationship_result = await self.extract_relationships(paper, document_id, entities)
            relationships = relationship_result['relationships']
            
            # Consolidate results
            result = {
                'status': 'success',
                'document_id': document_id,
                'entity_count': len(entities),
                'relationship_count': len(relationships),
                'entities': entities,
                'relationships': relationships,
                'metadata_updates': doc_result.get('updates', {})
            }
            
            logger.info(f"Completed extraction pipeline for paper {paper.id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to process paper {paper.id} through extraction pipeline: {e}")
            raise


# Note: This is a placeholder for the actual implementation
# The adapter will be initialized with the actual extraction components
extraction_adapter = None