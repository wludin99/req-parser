"""
Contract tests for POST /evaluate endpoint.

Tests the API contract as defined in contracts/evaluate.yaml
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


class TestEvaluateAPI:
    """Contract tests for the /evaluate endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client for the FastAPI app."""
        # This will fail until we implement the actual FastAPI app
        from src.main import app
        return TestClient(app)
    
    @pytest.fixture
    def sample_extracted_data(self):
        """Sample extracted data for testing."""
        return {
            "tender_reference": "EU-EN-2024-056",
            "publication_date": "2024-06-14",
            "contracting_authority": {
                "name": "Ministry of Energy Transition",
                "address": "12 Rue de Rivoli, 75001 Paris, France"
            },
            "subject": "Supply and installation of solar photovoltaic systems for public schools in the Île-de-France region.",
            "description": "The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems with a minimum installed capacity of 500 kW across 10 schools. The contractor is also responsible for maintenance for 5 years.",
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
    
    @pytest.fixture
    def sample_ground_truth(self):
        """Sample ground truth data for testing."""
        return {
            "tender_reference": "EU-EN-2024-056",
            "publication_date": "2024-06-14",
            "contracting_authority": {
                "name": "Ministry of Energy Transition",
                "address": "12 Rue de Rivoli, 75001 Paris, France"
            },
            "subject": "Supply and installation of solar photovoltaic systems for public schools in the Île-de-France region.",
            "description": "The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems with a minimum installed capacity of 500 kW across 10 schools. The contractor is also responsible for maintenance for 5 years.",
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
    
    def test_evaluate_perfect_match(self, client, sample_extracted_data, sample_ground_truth):
        """Test evaluation with perfect match."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator.return_value.evaluate_against_ground_truth.return_value = {
                "document_id": "test-doc-123",
                "overall_accuracy": 1.0,
                "field_accuracy": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 1.0,
                    "subject": 1.0,
                    "description": 1.0,
                    "estimated_budget_eur": 1.0,
                    "eligibility_requirements": 1.0,
                    "tender_deadline": 1.0,
                    "contact": 1.0
                },
                "completeness": 1.0,
                "discrepancies": [],
                "evaluation_timestamp": "2024-09-27T21:00:00Z"
            }
            
            response = client.post(
                "/evaluate",
                json={
                    "document_id": "test-doc-123",
                    "extracted_data": sample_extracted_data,
                    "ground_truth": sample_ground_truth
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate response structure according to contract
            assert "document_id" in data
            assert "overall_accuracy" in data
            assert "field_accuracy" in data
            assert "completeness" in data
            assert "discrepancies" in data
            assert "evaluation_timestamp" in data
            
            # Validate accuracy scores
            assert 0.0 <= data["overall_accuracy"] <= 1.0
            assert 0.0 <= data["completeness"] <= 1.0
            
            # Validate field accuracy structure
            field_accuracy = data["field_accuracy"]
            expected_fields = [
                "tender_reference", "publication_date", "contracting_authority",
                "subject", "description", "estimated_budget_eur",
                "eligibility_requirements", "tender_deadline", "contact"
            ]
            for field in expected_fields:
                assert field in field_accuracy
                assert 0.0 <= field_accuracy[field] <= 1.0
    
    def test_evaluate_with_discrepancies(self, client, sample_ground_truth):
        """Test evaluation with some discrepancies."""
        # Create extracted data with some differences
        extracted_data = sample_ground_truth.copy()
        extracted_data["contracting_authority"]["name"] = "Ministry of Energy"  # Missing "Transition"
        extracted_data["estimated_budget_eur"] = 2500000  # Same value but different type
        extracted_data["contact"]["email"] = "marie.dubois@example.com"  # Different email
        
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator.return_value.evaluate_against_ground_truth.return_value = {
                "document_id": "test-doc-456",
                "overall_accuracy": 0.85,
                "field_accuracy": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 0.8,
                    "subject": 1.0,
                    "description": 1.0,
                    "estimated_budget_eur": 1.0,
                    "eligibility_requirements": 1.0,
                    "tender_deadline": 1.0,
                    "contact": 0.7
                },
                "completeness": 1.0,
                "discrepancies": [
                    {
                        "field": "contracting_authority.name",
                        "extracted_value": "Ministry of Energy",
                        "ground_truth_value": "Ministry of Energy Transition",
                        "similarity_score": 0.8
                    },
                    {
                        "field": "contact.email",
                        "extracted_value": "marie.dubois@example.com",
                        "ground_truth_value": "marie.dubois@transition.gouv.fr",
                        "similarity_score": 0.7
                    }
                ],
                "evaluation_timestamp": "2024-09-27T21:00:00Z"
            }
            
            response = client.post(
                "/evaluate",
                json={
                    "document_id": "test-doc-456",
                    "extracted_data": extracted_data,
                    "ground_truth": sample_ground_truth
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["overall_accuracy"] == 0.85
            assert len(data["discrepancies"]) == 2
            
            # Validate discrepancy structure
            for discrepancy in data["discrepancies"]:
                assert "field" in discrepancy
                assert "extracted_value" in discrepancy
                assert "ground_truth_value" in discrepancy
                assert "similarity_score" in discrepancy
                assert 0.0 <= discrepancy["similarity_score"] <= 1.0
    
    def test_evaluate_missing_fields(self, client, sample_ground_truth):
        """Test evaluation with missing fields."""
        # Create extracted data with missing fields
        extracted_data = {
            "tender_reference": "EU-EN-2024-056",
            "publication_date": "2024-06-14",
            "contracting_authority": {
                "name": "Ministry of Energy Transition",
                "address": "12 Rue de Rivoli, 75001 Paris, France"
            },
            "subject": "Supply and installation of solar photovoltaic systems",
            # Missing description, estimated_budget_eur, eligibility_requirements, tender_deadline, contact
        }
        
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator.return_value.evaluate_against_ground_truth.return_value = {
                "document_id": "test-doc-789",
                "overall_accuracy": 0.6,
                "field_accuracy": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 1.0,
                    "subject": 1.0,
                    "description": 0.0,
                    "estimated_budget_eur": 0.0,
                    "eligibility_requirements": 0.0,
                    "tender_deadline": 0.0,
                    "contact": 0.0
                },
                "completeness": 0.4,  # 4 out of 10 fields present
                "discrepancies": [],
                "evaluation_timestamp": "2024-09-27T21:00:00Z"
            }
            
            response = client.post(
                "/evaluate",
                json={
                    "document_id": "test-doc-789",
                    "extracted_data": extracted_data,
                    "ground_truth": sample_ground_truth
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["overall_accuracy"] == 0.6
            assert data["completeness"] == 0.4
    
    def test_evaluate_missing_document_id(self, client, sample_extracted_data, sample_ground_truth):
        """Test evaluation without document_id."""
        response = client.post(
            "/evaluate",
            json={
                "extracted_data": sample_extracted_data,
                "ground_truth": sample_ground_truth
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "document_id" in data["error"].lower()
    
    def test_evaluate_missing_extracted_data(self, client, sample_ground_truth):
        """Test evaluation without extracted_data."""
        response = client.post(
            "/evaluate",
            json={
                "document_id": "test-doc-123",
                "ground_truth": sample_ground_truth
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "extracted_data" in data["error"].lower()
    
    def test_evaluate_missing_ground_truth(self, client, sample_extracted_data):
        """Test evaluation without ground_truth."""
        response = client.post(
            "/evaluate",
            json={
                "document_id": "test-doc-123",
                "extracted_data": sample_extracted_data
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "ground_truth" in data["error"].lower()
    
    def test_evaluate_invalid_data_format(self, client):
        """Test evaluation with invalid data format."""
        response = client.post(
            "/evaluate",
            json={
                "document_id": "test-doc-123",
                "extracted_data": "invalid_format",
                "ground_truth": "invalid_format"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "details" in data
    
    def test_evaluate_document_not_found(self, client, sample_extracted_data, sample_ground_truth):
        """Test evaluation with non-existent document."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator.return_value.evaluate_against_ground_truth.side_effect = FileNotFoundError("Document not found")
            
            response = client.post(
                "/evaluate",
                json={
                    "document_id": "non-existent-doc",
                    "extracted_data": sample_extracted_data,
                    "ground_truth": sample_ground_truth
                }
            )
            
            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert "not found" in data["error"].lower()
    
    def test_evaluate_server_error(self, client, sample_extracted_data, sample_ground_truth):
        """Test evaluation with server error."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator.return_value.evaluate_against_ground_truth.side_effect = Exception("Server error")
            
            response = client.post(
                "/evaluate",
                json={
                    "document_id": "test-doc-123",
                    "extracted_data": sample_extracted_data,
                    "ground_truth": sample_ground_truth
                }
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert "details" in data
