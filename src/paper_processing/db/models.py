"""
Database models for the Paper Processing Pipeline.

This module defines the database models for storing papers and their processing
status in MongoDB. These models provide the persistence layer for the Paper
Processing Pipeline and integrate with the Pydantic models for API interactions.

Current Implementation Status:
- Core paper model defined ✓
- Document schema defined ✓
- State persistence functionality ✓

Upcoming Development:
- Index creation for query optimization
- Schema migration utilities
- Advanced query methods
- Batch operations
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
from pymongo import MongoClient, UpdateOne, InsertOne
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from ..models.paper import Paper, PaperStatus, ProcessingEvent


logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Exception raised for database errors."""
    pass


class PaperModel:
    """
    Database model for papers.
    
    This class provides methods for storing and retrieving papers in MongoDB.
    It converts between the Pydantic Paper model and MongoDB documents.
    """
    
    def __init__(self, collection: Collection):
        """
        Initialize the paper model.
        
        Args:
            collection: MongoDB collection for papers
        """
        self.collection = collection
    
    def to_document(self, paper: Paper) -> Dict[str, Any]:
        """
        Convert a Paper model to a MongoDB document.
        
        Args:
            paper: The paper model to convert
            
        Returns:
            Dict representing the MongoDB document
        """
        # Convert the Pydantic model to a dict
        doc = paper.dict()
        
        # Ensure enums are stored as strings
        doc['status'] = paper.status.value
        
        # Convert processing history
        if 'processing_history' in doc and doc['processing_history']:
            for event in doc['processing_history']:
                if isinstance(event.get('status'), PaperStatus):
                    event['status'] = event['status'].value
        
        return doc
    
    def from_document(self, doc: Dict[str, Any]) -> Paper:
        """
        Convert a MongoDB document to a Paper model.
        
        Args:
            doc: The MongoDB document to convert
            
        Returns:
            Paper model
        """
        # Convert status string to enum
        if 'status' in doc and isinstance(doc['status'], str):
            doc['status'] = PaperStatus(doc['status'])
        
        # Convert processing history
        if 'processing_history' in doc and doc['processing_history']:
            for event in doc['processing_history']:
                if isinstance(event.get('status'), str):
                    event['status'] = PaperStatus(event['status'])
        
        # Create Paper model
        return Paper(**doc)
    
    async def find_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Find a paper by ID.
        
        Args:
            paper_id: The ID of the paper to find
            
        Returns:
            Paper if found, None otherwise
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            doc = await self.collection.find_one({'id': paper_id})
            if doc:
                return self.from_document(doc)
            return None
        except PyMongoError as e:
            logger.error(f"Database error finding paper {paper_id}: {e}")
            raise DatabaseError(f"Error finding paper: {e}")
    
    async def save(self, paper: Paper) -> Paper:
        """
        Save a paper to the database.
        
        Args:
            paper: The paper to save
            
        Returns:
            The saved paper
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            doc = self.to_document(paper)
            result = await self.collection.replace_one(
                {'id': paper.id},
                doc,
                upsert=True
            )
            logger.debug(f"Saved paper {paper.id}, upserted: {result.upserted_id is not None}")
            return paper
        except PyMongoError as e:
            logger.error(f"Database error saving paper {paper.id}: {e}")
            raise DatabaseError(f"Error saving paper: {e}")
    
    async def update_status(
        self,
        paper_id: str,
        status: PaperStatus,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[Paper]:
        """
        Update a paper's status and add a processing event.
        
        Args:
            paper_id: The ID of the paper to update
            status: The new status
            message: Status change message
            details: Optional status details
            
        Returns:
            Updated paper if found, None otherwise
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            # Create processing event
            event = {
                'timestamp': datetime.utcnow(),
                'status': status.value,
                'message': message
            }
            if details:
                event['details'] = details
            
            # Update the document
            result = await self.collection.update_one(
                {'id': paper_id},
                {
                    '$set': {'status': status.value, 'last_updated': datetime.utcnow()},
                    '$push': {'processing_history': event}
                }
            )
            
            if result.matched_count == 0:
                logger.warning(f"Paper {paper_id} not found for status update")
                return None
            
            # Fetch the updated paper
            return await self.find_by_id(paper_id)
        except PyMongoError as e:
            logger.error(f"Database error updating paper {paper_id} status: {e}")
            raise DatabaseError(f"Error updating paper status: {e}")
    
    async def find_by_status(
        self,
        status: PaperStatus,
        limit: int = 100,
        offset: int = 0
    ) -> List[Paper]:
        """
        Find papers by status.
        
        Args:
            status: The status to filter by
            limit: Maximum number of papers to return
            offset: Number of papers to skip
            
        Returns:
            List of papers with the given status
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            cursor = self.collection.find({'status': status.value}) \
                .skip(offset) \
                .limit(limit) \
                .sort('uploaded_at', -1)
            
            papers = []
            async for doc in cursor:
                papers.append(self.from_document(doc))
            
            return papers
        except PyMongoError as e:
            logger.error(f"Database error finding papers by status {status}: {e}")
            raise DatabaseError(f"Error finding papers by status: {e}")
    
    async def search(
        self,
        query: Optional[str] = None,
        status: Optional[PaperStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = 'uploaded_at',
        sort_order: int = -1
    ) -> Dict[str, Any]:
        """
        Search for papers matching criteria.
        
        Args:
            query: Optional search query
            status: Optional status filter
            from_date: Optional from date filter
            to_date: Optional to date filter
            limit: Maximum number of papers to return
            offset: Number of papers to skip
            sort_by: Field to sort by
            sort_order: Sort order (1 for ascending, -1 for descending)
            
        Returns:
            Dict with search results and metadata
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            # Build filter
            filter_query = {}
            
            if query:
                filter_query['$or'] = [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'abstract': {'$regex': query, '$options': 'i'}},
                    {'authors.name': {'$regex': query, '$options': 'i'}}
                ]
            
            if status:
                filter_query['status'] = status.value
            
            date_filter = {}
            if from_date:
                date_filter['$gte'] = from_date
            if to_date:
                date_filter['$lte'] = to_date
            
            if date_filter:
                filter_query['uploaded_at'] = date_filter
            
            # Count total matches
            total = await self.collection.count_documents(filter_query)
            
            # Execute search
            cursor = self.collection.find(filter_query) \
                .skip(offset) \
                .limit(limit) \
                .sort(sort_by, sort_order)
            
            # Collect results
            papers = []
            async for doc in cursor:
                papers.append(self.from_document(doc))
            
            return {
                'count': len(papers),
                'total': total,
                'limit': limit,
                'offset': offset,
                'papers': papers
            }
        except PyMongoError as e:
            logger.error(f"Database error searching papers: {e}")
            raise DatabaseError(f"Error searching papers: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get paper processing statistics.
        
        Returns:
            Dict with statistics
            
        Raises:
            DatabaseError: If a database error occurs
        """
        try:
            # Count papers by status
            pipeline = [
                {
                    '$group': {
                        '_id': '$status',
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            status_counts = {}
            cursor = self.collection.aggregate(pipeline)
            async for doc in cursor:
                status_counts[doc['_id']] = doc['count']
            
            # Calculate total papers
            total_papers = sum(status_counts.values())
            
            # This is a placeholder for the rest of the statistics
            # The full implementation would calculate average processing times,
            # entity counts, etc.
            
            return {
                'total_papers': total_papers,
                'papers_by_status': status_counts,
                'avg_processing_time': 0.0,  # Placeholder
                'avg_entity_count': 0.0,     # Placeholder
                'avg_relationship_count': 0.0  # Placeholder
            }
        except PyMongoError as e:
            logger.error(f"Database error getting statistics: {e}")
            raise DatabaseError(f"Error getting statistics: {e}")


# This will be initialized by the application at startup
paper_model = None