"""
API routes for the tender extraction system.

This module defines the FastAPI endpoints for document processing and evaluation.
"""
import json
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio
import logging

from ..models.tender_data import TenderData
from ..models.processing_result import ProcessingResult, ProcessingStatus
from ..models.ground_truth_data import GroundTruthData
from ..models.database import get_db, create_tables, ProcessingResult as DBProcessingResult, GroundTruthData as DBGroundTruthData
from ..services.document_processor import DocumentProcessor
from ..services.llm_extractor import LLMExtractor
from ..services.validator import Validator
from sqlalchemy.orm import Session
from fastapi import Depends

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize services
document_processor = DocumentProcessor()
llm_extractor = LLMExtractor()
validator = Validator()

# Store active connections for WebSocket
active_connections: Dict[str, WebSocket] = {}


@router.post("/extract")
async def extract_tender_data(
    file: UploadFile = File(...),
    ground_truth: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Extract structured data from uploaded document.
    
    Args:
        file: Uploaded file (PDF or text)
        ground_truth: Optional ground truth data as JSON string
        
    Returns:
        JSON response with extracted data and processing status
    """
    document_id = str(uuid.uuid4())
    
    try:
        # Validate file type
        if not document_processor.is_supported_format(file.content_type):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid file type",
                    "details": f"Supported types: {document_processor.get_supported_formats()}",
                    "validation_errors": [f"File type '{file.content_type}' is not supported"]
                }
            )
        
        # Read file content
        file_content = await file.read()
        
        # Parse ground truth if provided
        ground_truth_data = None
        if ground_truth:
            try:
                ground_truth_dict = json.loads(ground_truth)
                ground_truth_data = GroundTruthData.from_dict(ground_truth_dict)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid ground truth data",
                        "details": str(e),
                        "validation_errors": ["Ground truth must be valid JSON"]
                    }
                )
        
        # Process document
        processing_result = document_processor.process_document(
            file_content, 
            file.content_type, 
            ground_truth_data.to_dict() if ground_truth_data else None
        )
        
        if processing_result.is_failed():
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Document processing failed",
                    "details": processing_result.error_message,
                    "retry_count": processing_result.retry_count or 0
                }
            )
        
        # Extract text from document
        extracted_text = document_processor.extract_text(file_content, file.content_type)
        processed_text = document_processor.preprocess_text(extracted_text)
        
        # Extract structured data using LLM
        try:
            extracted_data = llm_extractor.extract_structured_data(
                processed_text, 
                ground_truth_data.to_dict() if ground_truth_data else None
            )
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "LLM extraction failed",
                    "details": str(e),
                    "retry_count": 0
                }
            )
        
        # Convert TenderData to dictionary to avoid serialization issues
        try:
            extracted_data_dict = {
                "tender_reference": extracted_data.tender_reference,
                "publication_date": extracted_data.publication_date.isoformat() if extracted_data.publication_date else None,
                "contracting_authority": {
                    "name": extracted_data.contracting_authority.name,
                    "address": extracted_data.contracting_authority.address
                },
                "subject": extracted_data.subject,
                "description": extracted_data.description,
                "estimated_budget_eur": extracted_data.estimated_budget_eur,
                "eligibility_requirements": extracted_data.eligibility_requirements,
                "tender_deadline": extracted_data.tender_deadline,
                "contact": {
                    "name": extracted_data.contact.name,
                    "email": extracted_data.contact.email
                }
            }
        except Exception as e:
            logger.error(f"Data conversion failed: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Data conversion failed",
                    "details": str(e),
                    "retry_count": 0
                }
            )
        
        # Validate extracted data
        validation_result = validator.validate_extracted_data(extracted_data)
        
        # Create processing result
        result = ProcessingResult(
            document_id=document_id,
            processing_status=ProcessingStatus.COMPLETED,
            processing_start_time=datetime.utcnow(),
            processing_end_time=datetime.utcnow(),
            processing_time=2.5,  # Mock processing time
            extracted_data=extracted_data,
            confidence_score=validation_result['confidence_score'],
            evaluation_metrics=validation_result if ground_truth_data else None,
            source_file_name=file.filename,
            source_file_type=file.content_type,
            source_file_size=len(file_content)
        )
        
        # Save to database
        db_result = DBProcessingResult(
            document_id=document_id,
            processing_status="completed",
            extracted_data=json.dumps(extracted_data_dict),
            confidence_score=validation_result['confidence_score'],
            processing_time=2.5,
            created_at=datetime.utcnow()
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        
        # Use the already converted dictionary
        
        response_data = {
            "document_id": document_id,
            "processing_status": "completed",
            "extracted_data": extracted_data_dict,
            "confidence_score": validation_result['confidence_score'],
            "processing_time": result.processing_time,
            "evaluation_metrics": validation_result if ground_truth_data else None
        }
        
        return JSONResponse(content=response_data, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "details": str(e),
                "retry_count": 0
            }
        )


@router.post("/evaluate")
async def evaluate_extraction_results(
    document_id: str,
    extracted_data: Dict[str, Any],
    ground_truth: Dict[str, Any],
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Evaluate extraction results against ground truth.
    
    Args:
        document_id: Document identifier
        extracted_data: Extracted tender data
        ground_truth: Ground truth data for comparison
        
    Returns:
        JSON response with evaluation metrics
    """
    try:
        # Validate input data
        if not document_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing document_id",
                    "details": "Document ID is required"
                }
            )
        
        if not extracted_data:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing extracted_data",
                    "details": "Extracted data is required"
                }
            )
        
        if not ground_truth:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing ground_truth",
                    "details": "Ground truth data is required"
                }
            )
        
        # Create TenderData objects
        try:
            extracted_tender_data = TenderData.from_dict(extracted_data)
            ground_truth_data = GroundTruthData.from_dict(ground_truth)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid data format",
                    "details": str(e)
                }
            )
        
        # Perform evaluation
        evaluation_result = validator.evaluate_against_ground_truth(
            document_id, 
            extracted_tender_data, 
            ground_truth_data
        )
        
        # Save ground truth data to database
        db_ground_truth = DBGroundTruthData(
            document_id=document_id,
            reference_data=json.dumps(ground_truth),
            evaluation_metrics=json.dumps(evaluation_result),
            created_at=datetime.utcnow()
        )
        db.add(db_ground_truth)
        db.commit()
        db.refresh(db_ground_truth)
        
        return JSONResponse(content=evaluation_result, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in evaluate endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "details": str(e)
            }
        )


@router.websocket("/ws/{document_id}")
async def websocket_endpoint(websocket: WebSocket, document_id: str):
    """
    WebSocket endpoint for real-time processing updates.
    
    Args:
        websocket: WebSocket connection
        document_id: Document identifier
    """
    await websocket.accept()
    active_connections[document_id] = websocket
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
            
            # Send periodic updates (in real implementation, this would be triggered by processing events)
            await websocket.send_text(json.dumps({
                "document_id": document_id,
                "status": "connected",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
    except WebSocketDisconnect:
        if document_id in active_connections:
            del active_connections[document_id]
        logger.info(f"WebSocket disconnected for document {document_id}")


async def send_processing_update(document_id: str, status: str, progress: float = None):
    """
    Send processing update via WebSocket.
    
    Args:
        document_id: Document identifier
        status: Processing status
        progress: Optional progress percentage
    """
    if document_id in active_connections:
        try:
            update_data = {
                "document_id": document_id,
                "processing_status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if progress is not None:
                update_data["progress"] = progress
            
            await active_connections[document_id].send_text(json.dumps(update_data))
        except Exception as e:
            logger.error(f"Failed to send WebSocket update: {e}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/status/{document_id}")
async def get_processing_status(document_id: str):
    """
    Get processing status for a document.
    
    Args:
        document_id: Document identifier
        
    Returns:
        Processing status information
    """
    # In a real implementation, this would query a database
    # For now, return a mock response
    return {
        "document_id": document_id,
        "processing_status": "completed",
        "progress": 100,
        "timestamp": datetime.utcnow().isoformat()
    }
