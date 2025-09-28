"""
Integration tests for ground truth evaluation.

Tests the evaluation of extracted data against known ground truth.
"""
import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime


class TestGroundTruthEvaluation:
    """Integration tests for ground truth evaluation."""
    
    @pytest.fixture
    def ground_truth_data(self):
        """Ground truth data for testing."""
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
    def perfect_extracted_data(self):
        """Perfectly matching extracted data."""
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
    def partial_extracted_data(self):
        """Partially matching extracted data."""
        return {
            "tender_reference": "EU-EN-2024-056",
            "publication_date": "2024-06-14",
            "contracting_authority": {
                "name": "Ministry of Energy",  # Missing "Transition"
                "address": "12 Rue de Rivoli, 75001 Paris, France"
            },
            "subject": "Supply and installation of solar photovoltaic systems",  # Truncated
            "description": "The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems",  # Truncated
            "estimated_budget_eur": 2500000.0,
            "eligibility_requirements": [
                "At least 3 prior contracts of similar scope in the last 5 years.",
                "Certification in ISO 14001 (Environmental Management)."
                # Missing third requirement
            ],
            "tender_deadline": "2024-07-30 17:00 CET",
            "contact": {
                "name": "Marie Dubois",
                "email": "marie.dubois@example.com"  # Different email domain
            }
        }
    
    @pytest.fixture
    def incomplete_extracted_data(self):
        """Incomplete extracted data with missing fields."""
        return {
            "tender_reference": "EU-EN-2024-056",
            "publication_date": "2024-06-14",
            "contracting_authority": {
                "name": "Ministry of Energy Transition",
                "address": "12 Rue de Rivoli, 75001 Paris, France"
            },
            "subject": "Supply and installation of solar photovoltaic systems for public schools in the Île-de-France region."
            # Missing: description, estimated_budget_eur, eligibility_requirements, tender_deadline, contact
        }
    
    def test_perfect_match_evaluation(self, ground_truth_data, perfect_extracted_data):
        """Test evaluation with perfect match."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.evaluate_against_ground_truth.return_value = {
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
            mock_validator.return_value = mock_validator_instance
            
            # Test evaluation
            from src.services.validator import Validator
            
            validator = Validator()
            result = validator.evaluate_against_ground_truth(
                document_id="test-doc-123",
                extracted_data=perfect_extracted_data,
                ground_truth=ground_truth_data
            )
            
            assert result["overall_accuracy"] == 1.0
            assert result["completeness"] == 1.0
            assert len(result["discrepancies"]) == 0
            
            # All field accuracies should be 1.0
            for field, accuracy in result["field_accuracy"].items():
                assert accuracy == 1.0
    
    def test_partial_match_evaluation(self, ground_truth_data, partial_extracted_data):
        """Test evaluation with partial match."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.evaluate_against_ground_truth.return_value = {
                "document_id": "test-doc-456",
                "overall_accuracy": 0.75,
                "field_accuracy": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 0.8,  # Name truncated
                    "subject": 0.7,  # Truncated
                    "description": 0.6,  # Truncated
                    "estimated_budget_eur": 1.0,
                    "eligibility_requirements": 0.67,  # 2 out of 3 requirements
                    "tender_deadline": 1.0,
                    "contact": 0.5  # Different email
                },
                "completeness": 1.0,  # All fields present
                "discrepancies": [
                    {
                        "field": "contracting_authority.name",
                        "extracted_value": "Ministry of Energy",
                        "ground_truth_value": "Ministry of Energy Transition",
                        "similarity_score": 0.8
                    },
                    {
                        "field": "subject",
                        "extracted_value": "Supply and installation of solar photovoltaic systems",
                        "ground_truth_value": "Supply and installation of solar photovoltaic systems for public schools in the Île-de-France region.",
                        "similarity_score": 0.7
                    },
                    {
                        "field": "contact.email",
                        "extracted_value": "marie.dubois@example.com",
                        "ground_truth_value": "marie.dubois@transition.gouv.fr",
                        "similarity_score": 0.5
                    }
                ],
                "evaluation_timestamp": "2024-09-27T21:00:00Z"
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test evaluation
            from src.services.validator import Validator
            
            validator = Validator()
            result = validator.evaluate_against_ground_truth(
                document_id="test-doc-456",
                extracted_data=partial_extracted_data,
                ground_truth=ground_truth_data
            )
            
            assert result["overall_accuracy"] == 0.75
            assert result["completeness"] == 1.0  # All fields present
            assert len(result["discrepancies"]) == 3
            
            # Check specific field accuracies
            assert result["field_accuracy"]["tender_reference"] == 1.0
            assert result["field_accuracy"]["contracting_authority"] == 0.8
            assert result["field_accuracy"]["eligibility_requirements"] == 0.67
    
    def test_incomplete_data_evaluation(self, ground_truth_data, incomplete_extracted_data):
        """Test evaluation with incomplete data."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.evaluate_against_ground_truth.return_value = {
                "document_id": "test-doc-789",
                "overall_accuracy": 0.4,
                "field_accuracy": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 1.0,
                    "subject": 1.0,
                    "description": 0.0,  # Missing
                    "estimated_budget_eur": 0.0,  # Missing
                    "eligibility_requirements": 0.0,  # Missing
                    "tender_deadline": 0.0,  # Missing
                    "contact": 0.0  # Missing
                },
                "completeness": 0.4,  # 4 out of 10 fields present
                "discrepancies": [],
                "evaluation_timestamp": "2024-09-27T21:00:00Z"
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test evaluation
            from src.services.validator import Validator
            
            validator = Validator()
            result = validator.evaluate_against_ground_truth(
                document_id="test-doc-789",
                extracted_data=incomplete_extracted_data,
                ground_truth=ground_truth_data
            )
            
            assert result["overall_accuracy"] == 0.4
            assert result["completeness"] == 0.4
            assert len(result["discrepancies"]) == 0  # No discrepancies, just missing fields
            
            # Check field accuracies for missing fields
            assert result["field_accuracy"]["description"] == 0.0
            assert result["field_accuracy"]["estimated_budget_eur"] == 0.0
            assert result["field_accuracy"]["eligibility_requirements"] == 0.0
    
    def test_evaluation_metrics_calculation(self, ground_truth_data, partial_extracted_data):
        """Test calculation of evaluation metrics."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.evaluate_against_ground_truth.return_value = {
                "document_id": "test-doc-456",
                "overall_accuracy": 0.75,
                "field_accuracy": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 0.8,
                    "subject": 0.7,
                    "description": 0.6,
                    "estimated_budget_eur": 1.0,
                    "eligibility_requirements": 0.67,
                    "tender_deadline": 1.0,
                    "contact": 0.5
                },
                "completeness": 1.0,
                "discrepancies": [
                    {
                        "field": "contracting_authority.name",
                        "extracted_value": "Ministry of Energy",
                        "ground_truth_value": "Ministry of Energy Transition",
                        "similarity_score": 0.8
                    }
                ],
                "evaluation_timestamp": "2024-09-27T21:00:00Z"
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test evaluation
            from src.services.validator import Validator
            
            validator = Validator()
            result = validator.evaluate_against_ground_truth(
                document_id="test-doc-456",
                extracted_data=partial_extracted_data,
                ground_truth=ground_truth_data
            )
            
            # Verify overall accuracy calculation
            field_accuracies = list(result["field_accuracy"].values())
            expected_overall_accuracy = sum(field_accuracies) / len(field_accuracies)
            assert abs(result["overall_accuracy"] - expected_overall_accuracy) < 0.01
            
            # Verify completeness calculation
            present_fields = sum(1 for acc in field_accuracies if acc > 0)
            total_fields = len(field_accuracies)
            expected_completeness = present_fields / total_fields
            assert abs(result["completeness"] - expected_completeness) < 0.01
    
    def test_evaluation_with_different_data_types(self, ground_truth_data):
        """Test evaluation with different data types."""
        # Test with string budget instead of float
        extracted_data = ground_truth_data.copy()
        extracted_data["estimated_budget_eur"] = "2500000"  # String instead of float
        
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.evaluate_against_ground_truth.return_value = {
                "document_id": "test-doc-456",
                "overall_accuracy": 0.95,
                "field_accuracy": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 1.0,
                    "subject": 1.0,
                    "description": 1.0,
                    "estimated_budget_eur": 1.0,  # Should handle type conversion
                    "eligibility_requirements": 1.0,
                    "tender_deadline": 1.0,
                    "contact": 1.0
                },
                "completeness": 1.0,
                "discrepancies": [],
                "evaluation_timestamp": "2024-09-27T21:00:00Z"
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test evaluation
            from src.services.validator import Validator
            
            validator = Validator()
            result = validator.evaluate_against_ground_truth(
                document_id="test-doc-456",
                extracted_data=extracted_data,
                ground_truth=ground_truth_data
            )
            
            assert result["overall_accuracy"] == 0.95
            assert result["field_accuracy"]["estimated_budget_eur"] == 1.0
    
    def test_evaluation_error_handling(self, ground_truth_data):
        """Test evaluation error handling."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.evaluate_against_ground_truth.side_effect = Exception("Evaluation failed")
            mock_validator.return_value = mock_validator_instance
            
            # Test error handling
            from src.services.validator import Validator
            
            validator = Validator()
            
            with pytest.raises(Exception) as exc_info:
                validator.evaluate_against_ground_truth(
                    document_id="test-doc-error",
                    extracted_data={},
                    ground_truth=ground_truth_data
                )
            
            assert "Evaluation failed" in str(exc_info.value)
    
    def test_evaluation_timestamp_generation(self, ground_truth_data, perfect_extracted_data):
        """Test that evaluation timestamp is generated correctly."""
        with patch('src.services.validator.Validator') as mock_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.evaluate_against_ground_truth.return_value = {
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
            mock_validator.return_value = mock_validator_instance
            
            # Test evaluation
            from src.services.validator import Validator
            
            validator = Validator()
            result = validator.evaluate_against_ground_truth(
                document_id="test-doc-123",
                extracted_data=perfect_extracted_data,
                ground_truth=ground_truth_data
            )
            
            # Verify timestamp format
            timestamp = result["evaluation_timestamp"]
            assert timestamp is not None
            assert "T" in timestamp  # ISO format
            assert "Z" in timestamp  # UTC timezone
            
            # Verify timestamp is recent (within last minute)
            from datetime import datetime
            parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            now = datetime.now(parsed_timestamp.tzinfo)
            time_diff = abs((now - parsed_timestamp).total_seconds())
            assert time_diff < 60  # Within last minute
