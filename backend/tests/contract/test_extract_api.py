"""
Contract tests for POST /extract endpoint.

Tests the API contract as defined in contracts/extract.yaml
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json


class TestExtractAPI:
    """Contract tests for the /extract endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client for the FastAPI app."""
        # This will fail until we implement the actual FastAPI app
        from src.main import app
        return TestClient(app)
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF content for testing."""
        # Create a minimal valid PDF for testing
        return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(European Union Tender Notice) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000204 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
298
%%EOF"""
    
    @pytest.fixture
    def sample_text_content(self):
        """Sample text content for testing."""
        return b"Sample text content for testing"
    
    @pytest.fixture
    def sample_ground_truth(self):
        """Sample ground truth data."""
        return {
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
        }
    
    def test_extract_pdf_success(self, client, sample_pdf_content):
        """Test successful PDF extraction."""
        # This test will fail until we implement the endpoint
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor:
            mock_processor.return_value.process_document.return_value = {
                "document_id": "test-doc-123",
                "processing_status": "completed",
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
                "processing_time": 2.5,
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
                }
            }
            
            response = client.post(
                "/extract",
                files={"file": ("test.txt", b"European Union Tender Notice\nPublication Date: 14 June 2024\nTender Reference: EU-EN-2024-056", "text/plain")}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure according to contract
            assert "document_id" in data
            assert "processing_status" in data
            assert "extracted_data" in data
            assert "confidence_score" in data
            assert "processing_time" in data
            assert "evaluation_metrics" in data
            
            # Validate extracted_data structure
            extracted = data["extracted_data"]
            assert "tender_reference" in extracted
            assert "publication_date" in extracted
            assert "contracting_authority" in extracted
            assert "subject" in extracted
            assert "description" in extracted
            assert "estimated_budget_eur" in extracted
            assert "eligibility_requirements" in extracted
            assert "tender_deadline" in extracted
            assert "contact" in extracted
            
            # Validate processing status
            assert data["processing_status"] in ["pending", "processing", "completed", "failed"]
            
            # Validate confidence score range
            assert 0.0 <= data["confidence_score"] <= 1.0
    
    def test_extract_text_success(self, client, sample_text_content):
        """Test successful text file extraction."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor:
            mock_processor.return_value.process_document.return_value = {
                "document_id": "test-doc-456",
                "processing_status": "completed",
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
                "confidence_score": 0.92,
                "processing_time": 1.8,
                "evaluation_metrics": {
                    "accuracy": 0.92,
                    "completeness": 1.0,
                    "field_accuracy": {
                        "tender_reference": 1.0,
                        "publication_date": 1.0,
                        "contracting_authority": 0.9,
                        "subject": 1.0,
                        "description": 0.92,
                        "estimated_budget_eur": 1.0,
                        "eligibility_requirements": 1.0,
                        "tender_deadline": 1.0,
                        "contact": 1.0
                    }
                }
            }
            
            response = client.post(
                "/extract",
                files={"file": ("test.txt", sample_text_content, "text/plain")}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["processing_status"] == "completed"
            assert data["confidence_score"] == 0.92
    
    def test_extract_with_ground_truth(self, client, sample_pdf_content, sample_ground_truth):
        """Test extraction with ground truth data."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor:
            mock_processor.return_value.process_document.return_value = {
                "document_id": "test-doc-789",
                "processing_status": "completed",
                "extracted_data": sample_ground_truth,
                "confidence_score": 0.98,
                "processing_time": 3.2,
                "evaluation_metrics": {
                    "accuracy": 0.98,
                    "completeness": 1.0,
                    "field_accuracy": {
                        "tender_reference": 1.0,
                        "publication_date": 1.0,
                        "contracting_authority": 1.0,
                        "subject": 1.0,
                        "description": 0.95,
                        "estimated_budget_eur": 1.0,
                        "eligibility_requirements": 1.0,
                        "tender_deadline": 1.0,
                        "contact": 1.0
                    }
                }
            }
            
            response = client.post(
                "/extract",
                files={"file": ("test.pdf", sample_pdf_content, "application/pdf")},
                data={"ground_truth": json.dumps(sample_ground_truth)}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["processing_status"] == "completed"
            assert data["confidence_score"] == 0.98
    
    def test_extract_invalid_file_type(self, client):
        """Test extraction with invalid file type."""
        response = client.post(
            "/extract",
            files={"file": ("test.exe", b"executable content", "application/x-msdownload")}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Invalid file type" in data["error"]
    
    def test_extract_missing_file(self, client):
        """Test extraction without file."""
        response = client.post("/extract")
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "file" in data["error"].lower()
    
    def test_extract_processing_error(self, client, sample_pdf_content):
        """Test extraction with processing error."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor:
            mock_processor.return_value.process_document.side_effect = Exception("Processing failed")
            
            response = client.post(
                "/extract",
                files={"file": ("test.pdf", sample_pdf_content, "application/pdf")}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "details" in data
            assert "retry_count" in data
    
    def test_extract_server_error(self, client, sample_pdf_content):
        """Test extraction with server error."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor:
            mock_processor.side_effect = Exception("Server error")
            
            response = client.post(
                "/extract",
                files={"file": ("test.pdf", sample_pdf_content, "application/pdf")}
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "details" in data
