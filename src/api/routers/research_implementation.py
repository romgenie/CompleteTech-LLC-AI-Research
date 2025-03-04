"""
Research Implementation router for the API.

This module provides endpoints for managing research implementations.

Note: The paper processing pipeline is currently not implemented.
Papers can be uploaded but will remain in "uploaded" status.
Future implementation will include automatic background processing
and manual processing endpoints to analyze papers and generate
implementations.
"""

import logging
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Query, 
    Path, 
    File, 
    UploadFile, 
    Form
)

from src.api.dependencies.auth import User, get_current_user
from src.api.dependencies.database import get_db
from src.api.models.research import (
    Implementation, 
    ImplementationRequestCreate, 
    ImplementationStatus,
    Author,
    PaperInfo
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/papers/", 
    status_code=201,
    summary="Upload research paper"
)
async def upload_paper(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    authors: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    abstract: Optional[str] = Form(None),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Upload a research paper for processing.
    
    Args:
        file: The paper file (PDF, arXiv ID, etc.)
        title: Optional paper title
        authors: Optional comma-separated author names
        year: Optional publication year
        abstract: Optional paper abstract
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Upload result
    """
    # Generate a unique ID for the paper
    paper_id = str(uuid.uuid4())
    
    # Get file extension
    filename = file.filename
    file_extension = filename.split(".")[-1].lower()
    
    # Check file extension
    allowed_extensions = ["pdf", "txt", "html", "md"]
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create a unique filename
    unique_filename = f"{paper_id}.{file_extension}"
    upload_dir = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
    
    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        # Read the file content
        content = await file.read()
        
        # Write to disk
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Parse author names
    author_list = []
    if authors:
        author_names = [name.strip() for name in authors.split(",")]
        author_list = [{"name": name} for name in author_names]
    
    # Create paper metadata
    now = datetime.now()
    paper_metadata = {
        "id": paper_id,
        "filename": unique_filename,
        "file_path": file_path,
        "original_filename": filename,
        "content_type": file.content_type,
        "title": title or filename,
        "authors": author_list,
        "year": year,
        "abstract": abstract,
        "uploaded_by": current_user.username,
        "uploaded_at": now,
        "status": "uploaded"
    }
    
    # Save to database
    db.papers.insert_one(paper_metadata)
    
    return {
        "id": paper_id,
        "filename": unique_filename,
        "title": title or filename,
        "authors": author_list,
        "year": year,
        "uploaded_at": now,
        "status": "uploaded",
        "message": "Paper uploaded successfully"
    }


@router.get(
    "/papers/", 
    response_model=List[Dict[str, Any]],
    summary="List uploaded papers"
)
async def list_papers(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    List papers uploaded by the current user.
    
    Args:
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        List[Dict[str, Any]]: List of papers
    """
    # Query database
    cursor = db.papers.find(
        {"uploaded_by": current_user.username}
    ).sort("uploaded_at", -1).skip(offset).limit(limit)
    
    papers = []
    for paper in cursor:
        # Convert ObjectId to string for JSON serialization
        paper["_id"] = str(paper["_id"])
        papers.append(paper)
    
    return papers


@router.get(
    "/papers/{paper_id}", 
    response_model=Dict[str, Any],
    summary="Get paper details"
)
async def get_paper(
    paper_id: str = Path(..., description="The ID of the paper to retrieve"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get details about a specific paper.
    
    Args:
        paper_id: ID of the paper to retrieve
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Paper details
        
    Raises:
        HTTPException: If paper is not found
    """
    # Query database
    paper = db.papers.find_one({
        "id": paper_id,
        "uploaded_by": current_user.username
    })
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Convert ObjectId to string for JSON serialization
    paper["_id"] = str(paper["_id"])
    
    return paper


@router.post(
    "/implementations/", 
    response_model=Implementation, 
    status_code=201,
    summary="Request implementation"
)
async def request_implementation(
    request: ImplementationRequestCreate,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Implementation:
    """
    Request an implementation of a research paper.
    
    Args:
        request: Implementation request data
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Implementation: Created implementation
    """
    # Create a new implementation
    implementation_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Parse paper info
    paper_info_dict = request.paper_info.dict()
    
    # Create implementation document
    implementation_doc = {
        "id": implementation_id,
        "paper_info": paper_info_dict,
        "implementation_language": request.implementation_language,
        "focus_areas": request.focus_areas or [],
        "additional_notes": request.additional_notes,
        "status": ImplementationStatus.REQUESTED.value,
        "created_at": now,
        "updated_at": now,
        "requested_by": current_user.username,
        "files": [],
        "repository_url": None
    }
    
    # Save to database
    db.implementations.insert_one(implementation_doc)
    
    # Convert document to API model
    authors = [
        Author(**author) 
        for author in paper_info_dict.get("authors", [])
    ]
    
    paper_info = PaperInfo(
        title=paper_info_dict.get("title"),
        authors=authors,
        abstract=paper_info_dict.get("abstract"),
        year=paper_info_dict.get("year"),
        doi=paper_info_dict.get("doi"),
        arxiv_id=paper_info_dict.get("arxiv_id"),
        url=paper_info_dict.get("url"),
        keywords=paper_info_dict.get("keywords", []),
        venue=paper_info_dict.get("venue")
    )
    
    return Implementation(
        id=implementation_id,
        paper_info=paper_info,
        implementation_language=request.implementation_language,
        focus_areas=request.focus_areas or [],
        additional_notes=request.additional_notes,
        status=ImplementationStatus.REQUESTED,
        created_at=now,
        updated_at=now,
        requested_by=current_user.username,
        files=[],
        repository_url=None
    )


@router.get(
    "/implementations/", 
    response_model=List[Implementation],
    summary="List implementations"
)
async def list_implementations(
    status: Optional[str] = Query(None, description="Filter by implementation status"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Implementation]:
    """
    List implementations for the current user.
    
    Args:
        status: Optional status filter
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        List[Implementation]: List of implementations
    """
    # Prepare query
    query = {"requested_by": current_user.username}
    
    if status:
        query["status"] = status
    
    # Query database
    cursor = db.implementations.find(query).sort(
        "created_at", -1
    ).skip(offset).limit(limit)
    
    # Convert to implementation models
    implementations = []
    for impl_doc in cursor:
        # Convert paper info
        paper_info_dict = impl_doc.get("paper_info", {})
        authors = [
            Author(**author) 
            for author in paper_info_dict.get("authors", [])
        ]
        
        paper_info = PaperInfo(
            title=paper_info_dict.get("title"),
            authors=authors,
            abstract=paper_info_dict.get("abstract"),
            year=paper_info_dict.get("year"),
            doi=paper_info_dict.get("doi"),
            arxiv_id=paper_info_dict.get("arxiv_id"),
            url=paper_info_dict.get("url"),
            keywords=paper_info_dict.get("keywords", []),
            venue=paper_info_dict.get("venue")
        )
        
        # Convert status
        status_value = impl_doc.get("status", "requested")
        try:
            status_enum = ImplementationStatus(status_value)
        except ValueError:
            status_enum = ImplementationStatus.REQUESTED
        
        implementations.append(
            Implementation(
                id=impl_doc["id"],
                paper_info=paper_info,
                implementation_language=impl_doc.get("implementation_language", "python"),
                focus_areas=impl_doc.get("focus_areas", []),
                additional_notes=impl_doc.get("additional_notes"),
                status=status_enum,
                created_at=impl_doc.get("created_at"),
                updated_at=impl_doc.get("updated_at"),
                completed_at=impl_doc.get("completed_at"),
                requested_by=impl_doc["requested_by"],
                files=impl_doc.get("files", []),
                repository_url=impl_doc.get("repository_url")
            )
        )
    
    return implementations


@router.get(
    "/implementations/{implementation_id}", 
    response_model=Implementation,
    summary="Get implementation"
)
async def get_implementation(
    implementation_id: str = Path(..., description="The ID of the implementation to retrieve"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Implementation:
    """
    Get a specific implementation by ID.
    
    Args:
        implementation_id: ID of the implementation to retrieve
        db: Database connection
        current_user: Current authenticated user
        
    Returns:
        Implementation: Implementation
        
    Raises:
        HTTPException: If implementation is not found
    """
    # Query database
    impl_doc = db.implementations.find_one({
        "id": implementation_id,
        "requested_by": current_user.username
    })
    
    if not impl_doc:
        raise HTTPException(status_code=404, detail="Implementation not found")
    
    # Convert paper info
    paper_info_dict = impl_doc.get("paper_info", {})
    authors = [
        Author(**author) 
        for author in paper_info_dict.get("authors", [])
    ]
    
    paper_info = PaperInfo(
        title=paper_info_dict.get("title"),
        authors=authors,
        abstract=paper_info_dict.get("abstract"),
        year=paper_info_dict.get("year"),
        doi=paper_info_dict.get("doi"),
        arxiv_id=paper_info_dict.get("arxiv_id"),
        url=paper_info_dict.get("url"),
        keywords=paper_info_dict.get("keywords", []),
        venue=paper_info_dict.get("venue")
    )
    
    # Convert status
    status_value = impl_doc.get("status", "requested")
    try:
        status_enum = ImplementationStatus(status_value)
    except ValueError:
        status_enum = ImplementationStatus.REQUESTED
    
    return Implementation(
        id=impl_doc["id"],
        paper_info=paper_info,
        implementation_language=impl_doc.get("implementation_language", "python"),
        focus_areas=impl_doc.get("focus_areas", []),
        additional_notes=impl_doc.get("additional_notes"),
        status=status_enum,
        created_at=impl_doc.get("created_at"),
        updated_at=impl_doc.get("updated_at"),
        completed_at=impl_doc.get("completed_at"),
        requested_by=impl_doc["requested_by"],
        files=impl_doc.get("files", []),
        repository_url=impl_doc.get("repository_url")
    )


@router.delete(
    "/implementations/{implementation_id}", 
    status_code=204,
    summary="Cancel implementation"
)
async def cancel_implementation(
    implementation_id: str = Path(..., description="The ID of the implementation to cancel"),
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Cancel an implementation request.
    
    Args:
        implementation_id: ID of the implementation to cancel
        db: Database connection
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If implementation is not found
    """
    # Check if implementation exists
    impl_doc = db.implementations.find_one({
        "id": implementation_id,
        "requested_by": current_user.username
    })
    
    if not impl_doc:
        raise HTTPException(status_code=404, detail="Implementation not found")
    
    # Get implementation status
    status = impl_doc.get("status", "requested")
    
    # If implementation is in progress, cancel it
    if status in ["requested", "analyzing", "planning", "implementing", "testing"]:
        db.implementations.update_one(
            {"id": implementation_id},
            {
                "$set": {
                    "status": ImplementationStatus.CANCELLED.value,
                    "updated_at": datetime.now()
                }
            }
        )
    # If implementation is completed or failed, delete it
    else:
        db.implementations.delete_one({"id": implementation_id})
    
    # 204 No Content response handled by FastAPI