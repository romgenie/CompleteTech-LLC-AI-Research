# API Schemas for Paper Processing Pipeline

## Overview

This directory contains the Pydantic models for API requests and responses in the Paper Processing Pipeline. These schemas enable validation and documentation of the API endpoints.

## Components

### Request Schemas

The `requests.py` file defines the schemas for API requests:

- **Process Paper Request**: Validates parameters for processing a paper
- **Batch Process Request**: Validates parameters for batch processing multiple papers
- **Paper Search Request**: Validates search and filter parameters
- **Paper Upload Request**: Validates paper upload parameters

### Response Schemas

The `responses.py` file defines the schemas for API responses:

- **Paper Status Response**: Format for paper status information
- **Processing Result Response**: Format for processing results
- **Batch Status Response**: Format for batch processing status
- **Paper Search Response**: Format for search results
- **Processing Statistics Response**: Format for processing statistics

## Schema Examples

### Request Schema Example

```python
class ProcessPaperRequest(BaseModel):
    """Request model for processing a paper."""
    
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Processing options"
    )
    priority: Optional[int] = Field(
        None,
        description="Processing priority (1-10, higher is more important)",
        ge=1,
        le=10
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "options": {
                    "extract_citations": True,
                    "build_knowledge_graph": True,
                    "check_implementation_readiness": True
                },
                "priority": 5
            }
        }
```

### Response Schema Example

```python
class PaperStatusResponse(BaseModel):
    """Response model for paper status."""
    
    paper_id: str = Field(..., description="Paper ID")
    title: str = Field(..., description="Paper title")
    status: PaperStatus = Field(..., description="Current status")
    progress: float = Field(..., description="Overall progress (0-1)", ge=0.0, le=1.0)
    uploaded_at: datetime = Field(..., description="When the paper was uploaded")
    last_updated: datetime = Field(..., description="When the status was last updated")
    history: List[ProcessingEvent] = Field(default_factory=list, description="Processing history")
    steps: List[ProcessingStepStatus] = Field(default_factory=list, description="Processing steps status")
    task_id: Optional[str] = Field(None, description="Celery task ID if processing")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    message: Optional[str] = Field(None, description="Status message")
```

## Usage

The schemas are used by the FastAPI routes to validate requests and generate responses:

```python
@router.post("/{paper_id}/process")
async def process_paper(
    paper_id: str = Path(..., description="The ID of the paper to process"),
    request: ProcessPaperRequest = Body(...),
) -> PaperStatusResponse:
    """
    Process a paper.
    
    Initiates the processing of a paper that has been uploaded.
    
    Args:
        paper_id: The ID of the paper to process
        request: Processing options and parameters
        
    Returns:
        Paper status information
    """
    # Validate the request using Pydantic
    # Process the paper
    # Return a validated response
```

## Benefits

- **Validation**: Automatic validation of request and response data
- **Documentation**: Automatic API documentation generation
- **Type Safety**: Type hints for IDE support and static analysis
- **Examples**: Example data for API documentation and testing
- **Consistency**: Consistent API format across endpoints

## Future Work

- **Advanced Validation**: Add more complex validation rules
- **Custom Validators**: Implement custom validators for specific fields
- **Dynamic Schemas**: Support dynamic schema generation based on configuration
- **Versioning**: Support API versioning with schema versions
- **Response Formatting**: Add support for different response formats