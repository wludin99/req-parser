"""
Unit tests for ProcessingResult model validation.

Tests the Pydantic model validation for ProcessingResult and related models.
"""
import pytest
from datetime import datetime, date
from enum import Enum

from src.models.processing_result import ProcessingResult, ProcessingStatus
from src.models.tender_data import TenderData, ContractingAuthority, Contact


class TestProcessingStatus:
    """Test ProcessingStatus enum."""
    
    def test_processing_status_values(self):
        """Test ProcessingStatus enum values."""
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"


class TestProcessingResult:
    """Test ProcessingResult model validation."""
    
    def test_valid_processing_result(self):
        """Test valid processing result creation."""
        processing_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.COMPLETED,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
            processing_time=150.0,
            extracted_data=TenderData(
                tender_reference="EU-EN-2024-001",
                publication_date=date(2024, 1, 15),
                contracting_authority=ContractingAuthority(
                    name="Ministry of Energy",
                    address="123 Government Street"
                ),
                subject="Test Subject",
                description="Test Description",
                estimated_budget_eur=100000.0,
                eligibility_requirements=["Requirement 1"],
                tender_deadline="2024-03-15",
                contact=Contact(
                    name="John Doe",
                    email="john@example.com"
                )
            ),
            confidence_score=0.85,
            source_file_name="test_document.pdf",
            source_file_type="application/pdf",
            source_file_size=1024000
        )
        
        assert processing_result.document_id == "doc-123"
        assert processing_result.processing_status == ProcessingStatus.COMPLETED
        assert processing_result.processing_time == 150.0
        assert processing_result.confidence_score == 0.85
        assert processing_result.source_file_name == "test_document.pdf"
        assert processing_result.source_file_type == "application/pdf"
        assert processing_result.source_file_size == 1024000
    
    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValueError):
            ProcessingResult(
                # Missing document_id
                processing_status=ProcessingStatus.COMPLETED,
                processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
                processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
                processing_time=150.0
            )
    
    def test_negative_processing_time(self):
        """Test validation error for negative processing time."""
        with pytest.raises(ValueError):
            ProcessingResult(
                document_id="doc-123",
                processing_status=ProcessingStatus.COMPLETED,
                processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
                processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
                processing_time=-10.0  # Negative time
            )
    
    def test_invalid_confidence_score(self):
        """Test validation error for invalid confidence score."""
        with pytest.raises(ValueError):
            ProcessingResult(
                document_id="doc-123",
                processing_status=ProcessingStatus.COMPLETED,
                processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
                processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
                processing_time=150.0,
                confidence_score=1.5  # Invalid: > 1.0
            )
    
    def test_negative_retry_count(self):
        """Test validation error for negative retry count."""
        with pytest.raises(ValueError):
            ProcessingResult(
                document_id="doc-123",
                processing_status=ProcessingStatus.COMPLETED,
                processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
                processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
                processing_time=150.0,
                retry_count=-1  # Negative retry count
            )
    
    def test_is_completed_method(self):
        """Test is_completed method."""
        completed_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.COMPLETED,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
            processing_time=150.0
        )
        assert completed_result.is_completed() is True
        
        pending_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.PENDING,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_time=0.0
        )
        assert pending_result.is_completed() is False
    
    def test_is_failed_method(self):
        """Test is_failed method."""
        failed_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.FAILED,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
            processing_time=150.0,
            error_message="Processing failed"
        )
        assert failed_result.is_failed() is True
        
        completed_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.COMPLETED,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
            processing_time=150.0
        )
        assert completed_result.is_failed() is False
    
    def test_is_processing_method(self):
        """Test is_processing method."""
        processing_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.PROCESSING,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_time=0.0
        )
        assert processing_result.is_processing() is True
        
        completed_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.COMPLETED,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
            processing_time=150.0
        )
        assert completed_result.is_processing() is False
    
    def test_from_dict_method(self):
        """Test from_dict class method."""
        data_dict = {
            "document_id": "doc-123",
            "processing_status": "completed",
            "processing_start_time": "2024-01-15T10:00:00",
            "processing_end_time": "2024-01-15T10:02:30",
            "processing_time": 150.0,
            "confidence_score": 0.85,
            "source_file_name": "test_document.pdf",
            "source_file_type": "application/pdf",
            "source_file_size": 1024000
        }
        
        processing_result = ProcessingResult.from_dict(data_dict)
        
        assert processing_result.document_id == "doc-123"
        assert processing_result.processing_status == ProcessingStatus.COMPLETED
        assert processing_result.processing_time == 150.0
        assert processing_result.confidence_score == 0.85
    
    def test_to_dict_method(self):
        """Test to_dict method."""
        processing_result = ProcessingResult(
            document_id="doc-123",
            processing_status=ProcessingStatus.COMPLETED,
            processing_start_time=datetime(2024, 1, 15, 10, 0, 0),
            processing_end_time=datetime(2024, 1, 15, 10, 2, 30),
            processing_time=150.0,
            confidence_score=0.85,
            source_file_name="test_document.pdf",
            source_file_type="application/pdf",
            source_file_size=1024000
        )
        
        data_dict = processing_result.to_dict()
        
        assert data_dict["document_id"] == "doc-123"
        assert data_dict["processing_status"] == "completed"
        assert data_dict["processing_time"] == 150.0
        assert data_dict["confidence_score"] == 0.85
