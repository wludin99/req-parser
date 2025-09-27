"""
ProcessingResult model for document processing outcomes.

This model represents the result of processing a document through the extraction pipeline.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from .tender_data import TenderData


class ProcessingStatus(str, Enum):
    """Processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingResult(BaseModel):
    """Result of document processing."""
    
    # Core identification
    document_id: str = Field(..., description="Unique identifier for the document")
    processing_status: ProcessingStatus = Field(..., description="Current processing status")
    
    # Processing metadata
    processing_start_time: Optional[datetime] = Field(None, description="When processing started")
    processing_end_time: Optional[datetime] = Field(None, description="When processing completed")
    processing_time: Optional[float] = Field(None, ge=0, description="Total processing time in seconds")
    
    # Results
    extracted_data: Optional[TenderData] = Field(None, description="Extracted structured data")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence score")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    retry_count: Optional[int] = Field(None, ge=0, description="Number of retry attempts")
    
    # Evaluation metrics
    evaluation_metrics: Optional[Dict[str, Any]] = Field(None, description="Evaluation metrics if ground truth available")
    
    # Processing steps
    processing_steps: Optional[List[str]] = Field(None, description="List of processing steps completed")
    current_step: Optional[str] = Field(None, description="Current processing step")
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Processing progress percentage")
    
    # Source information
    source_file_name: Optional[str] = Field(None, description="Original file name")
    source_file_type: Optional[str] = Field(None, description="Original file type")
    source_file_size: Optional[int] = Field(None, ge=0, description="Original file size in bytes")
    
    # Chunking information
    total_chunks: Optional[int] = Field(None, ge=0, description="Total number of document chunks")
    processed_chunks: Optional[int] = Field(None, ge=0, description="Number of chunks processed")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "document_id": "doc-123",
                "processing_status": "completed",
                "processing_start_time": "2024-09-27T21:00:00Z",
                "processing_end_time": "2024-09-27T21:02:30Z",
                "processing_time": 150.5,
                "extracted_data": {
                    "tender_reference": "EU-EN-2024-056",
                    "publication_date": "2024-06-14",
                    "contracting_authority": {
                        "name": "Ministry of Energy Transition",
                        "address": "12 Rue de Rivoli, 75001 Paris, France"
                    },
                    "subject": "Supply and installation of solar photovoltaic systems",
                    "description": "The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems",
                    "estimated_budget_eur": 2500000.0,
                    "eligibility_requirements": [
                        "At least 3 prior contracts of similar scope in the last 5 years.",
                        "Certification in ISO 14001 (Environmental Management).",
                        "Proof of financial capacity."
                    ],
                    "tender_deadline": "2024-07-30 17:00 CET",
                    "contact": {
                        "name": "Marie Dubois",
                        "email": "marie.dubois@transition.gouv.fr"
                    }
                },
                "confidence_score": 0.95,
                "evaluation_metrics": {
                    "accuracy": 0.95,
                    "completeness": 1.0,
                    "field_accuracy": {
                        "tender_reference": 1.0,
                        "publication_date": 1.0,
                        "contracting_authority": 0.9,
                        "subject": 1.0,
                        "description": 0.95,
                        "estimated_budget_eur": 1.0,
                        "eligibility_requirements": 1.0,
                        "tender_deadline": 1.0,
                        "contact": 1.0
                    }
                },
                "processing_steps": [
                    "document_upload",
                    "text_extraction",
                    "chunking",
                    "llm_processing",
                    "validation",
                    "completion"
                ],
                "current_step": "completion",
                "progress_percentage": 100.0,
                "source_file_name": "tender_document.pdf",
                "source_file_type": "application/pdf",
                "source_file_size": 1024000,
                "total_chunks": 3,
                "processed_chunks": 3
            }
        }
    
    def is_completed(self) -> bool:
        """Check if processing is completed successfully."""
        return self.processing_status == ProcessingStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if processing failed."""
        return self.processing_status == ProcessingStatus.FAILED
    
    def is_processing(self) -> bool:
        """Check if processing is in progress."""
        return self.processing_status == ProcessingStatus.PROCESSING
    
    def is_pending(self) -> bool:
        """Check if processing is pending."""
        return self.processing_status == ProcessingStatus.PENDING
    
    def get_processing_duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.processing_start_time and self.processing_end_time:
            return (self.processing_end_time - self.processing_start_time).total_seconds()
        return None
    
    def update_progress(self, step: str, percentage: float) -> None:
        """Update processing progress."""
        self.current_step = step
        self.progress_percentage = min(100.0, max(0.0, percentage))
        
        if self.processing_steps is None:
            self.processing_steps = []
        
        if step not in self.processing_steps:
            self.processing_steps.append(step)
    
    def mark_completed(self, extracted_data: TenderData, confidence_score: float) -> None:
        """Mark processing as completed with results."""
        self.processing_status = ProcessingStatus.COMPLETED
        self.extracted_data = extracted_data
        self.confidence_score = confidence_score
        self.processing_end_time = datetime.utcnow()
        self.progress_percentage = 100.0
        
        if self.processing_start_time:
            self.processing_time = (self.processing_end_time - self.processing_start_time).total_seconds()
    
    def mark_failed(self, error_message: str, error_details: Optional[Dict[str, Any]] = None) -> None:
        """Mark processing as failed with error information."""
        self.processing_status = ProcessingStatus.FAILED
        self.error_message = error_message
        self.error_details = error_details
        self.processing_end_time = datetime.utcnow()
        
        if self.processing_start_time:
            self.processing_time = (self.processing_end_time - self.processing_start_time).total_seconds()
    
    def start_processing(self) -> None:
        """Mark processing as started."""
        self.processing_status = ProcessingStatus.PROCESSING
        self.processing_start_time = datetime.utcnow()
        self.processing_steps = []
        self.progress_percentage = 0.0
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        if self.retry_count is None:
            self.retry_count = 0
        self.retry_count += 1
    
    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if processing can be retried."""
        if self.retry_count is None:
            return True
        return self.retry_count < max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingResult':
        """Create model from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProcessingResult':
        """Create model from JSON string."""
        return cls.parse_raw(json_str)
    
    @classmethod
    def create_pending(cls, document_id: str, source_file_name: Optional[str] = None) -> 'ProcessingResult':
        """Create a new pending processing result."""
        return cls(
            document_id=document_id,
            processing_status=ProcessingStatus.PENDING,
            source_file_name=source_file_name
        )
