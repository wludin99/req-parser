"""
Unit tests for Validator service.

Tests the validation and evaluation functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from src.services.validator import Validator
from src.models.tender_data import TenderData, ContractingAuthority, Contact


class TestValidator:
    """Test Validator service functionality."""
    
    def test_initialization(self):
        """Test Validator initialization."""
        validator = Validator()
        
        assert validator is not None
        assert hasattr(validator, 'validate_extraction_result')
        assert hasattr(validator, 'evaluate_against_ground_truth')
    
    def test_validate_extraction_result_valid_data(self):
        """Test validation of valid extraction result."""
        validator = Validator()
        
        # Create valid tender data
        tender_data = TenderData(
            tender_reference="EU-EN-2024-001",
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="Ministry of Energy",
                address="123 Government Street"
            ),
            subject="Renewable Energy Project",
            description="Development of renewable energy infrastructure",
            estimated_budget_eur=1000000.0,
            eligibility_requirements=["EU registered company"],
            tender_deadline="2024-03-15",
            contact=Contact(
                name="John Doe",
                email="john@ministry.gov"
            )
        )
        
        result = validator.validate_extraction_result(tender_data)
        
        assert result['is_valid'] is True
        assert result['confidence_score'] > 0.0
        assert 'field_accuracy' in result
        assert 'quality_indicators' in result
    
    def test_validate_extraction_result_invalid_data(self):
        """Test validation of invalid extraction result."""
        validator = Validator()
        
        # Create invalid tender data with missing required fields
        tender_data = TenderData(
            tender_reference="",  # Empty reference
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="",  # Empty name
                address="123 Government Street"
            ),
            subject="",  # Empty subject
            description="Development of renewable energy infrastructure",
            estimated_budget_eur=0.0,  # Zero budget
            eligibility_requirements=[],  # Empty requirements
            tender_deadline="",  # Empty deadline
            contact=Contact(
                name="John Doe",
                email=""  # Empty email
            )
        )
        
        result = validator.validate_extraction_result(tender_data)
        
        assert result['is_valid'] is False
        assert result['confidence_score'] < 0.5
        assert 'field_accuracy' in result
        assert 'quality_indicators' in result
    
    def test_evaluate_against_ground_truth_perfect_match(self):
        """Test evaluation with perfect match."""
        validator = Validator()
        
        # Create extracted data
        extracted_data = TenderData(
            tender_reference="EU-EN-2024-001",
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="Ministry of Energy",
                address="123 Government Street"
            ),
            subject="Renewable Energy Project",
            description="Development of renewable energy infrastructure",
            estimated_budget_eur=1000000.0,
            eligibility_requirements=["EU registered company"],
            tender_deadline="2024-03-15",
            contact=Contact(
                name="John Doe",
                email="john@ministry.gov"
            )
        )
        
        # Create identical ground truth
        ground_truth = {
            "tender_reference": "EU-EN-2024-001",
            "publication_date": "2024-01-15",
            "contracting_authority": {
                "name": "Ministry of Energy",
                "address": "123 Government Street"
            },
            "subject": "Renewable Energy Project",
            "description": "Development of renewable energy infrastructure",
            "estimated_budget_eur": 1000000.0,
            "eligibility_requirements": ["EU registered company"],
            "tender_deadline": "2024-03-15",
            "contact": {
                "name": "John Doe",
                "email": "john@ministry.gov"
            }
        }
        
        result = validator.evaluate_against_ground_truth(extracted_data, ground_truth)
        
        assert result['overall_accuracy'] == 1.0
        assert result['field_accuracy']['tender_reference'] == 1.0
        assert result['field_accuracy']['subject'] == 1.0
        assert len(result['discrepancies']) == 0
    
    def test_evaluate_against_ground_truth_partial_match(self):
        """Test evaluation with partial match."""
        validator = Validator()
        
        # Create extracted data
        extracted_data = TenderData(
            tender_reference="EU-EN-2024-001",
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="Ministry of Energy",
                address="123 Government Street"
            ),
            subject="Renewable Energy Project",
            description="Development of renewable energy infrastructure",
            estimated_budget_eur=1000000.0,
            eligibility_requirements=["EU registered company"],
            tender_deadline="2024-03-15",
            contact=Contact(
                name="John Doe",
                email="john@ministry.gov"
            )
        )
        
        # Create ground truth with some differences
        ground_truth = {
            "tender_reference": "EU-EN-2024-001",
            "publication_date": "2024-01-15",
            "contracting_authority": {
                "name": "Ministry of Energy",
                "address": "123 Government Street"
            },
            "subject": "Solar Energy Project",  # Different subject
            "description": "Development of solar energy infrastructure",  # Different description
            "estimated_budget_eur": 1500000.0,  # Different budget
            "eligibility_requirements": ["EU registered company"],
            "tender_deadline": "2024-03-15",
            "contact": {
                "name": "John Doe",
                "email": "john@ministry.gov"
            }
        }
        
        result = validator.evaluate_against_ground_truth(extracted_data, ground_truth)
        
        assert result['overall_accuracy'] < 1.0
        assert result['overall_accuracy'] > 0.0
        assert result['field_accuracy']['tender_reference'] == 1.0
        assert result['field_accuracy']['subject'] == 0.0
        assert len(result['discrepancies']) > 0
    
    def test_validate_publication_date_valid(self):
        """Test publication date validation with valid date."""
        validator = Validator()
        
        result = validator._validate_publication_date(date(2024, 1, 15))
        
        assert result['is_valid'] is True
        assert result['value'] == date(2024, 1, 15)
        assert result['error'] is None
    
    def test_validate_publication_date_invalid(self):
        """Test publication date validation with invalid date."""
        validator = Validator()
        
        result = validator._validate_publication_date("invalid-date")
        
        assert result['is_valid'] is False
        assert result['error'] is not None
    
    def test_validate_contracting_authority_valid(self):
        """Test contracting authority validation with valid data."""
        validator = Validator()
        
        authority = ContractingAuthority(
            name="Ministry of Energy",
            address="123 Government Street"
        )
        
        result = validator._validate_contracting_authority(authority)
        
        assert result['is_valid'] is True
        assert result['name_valid'] is True
        assert result['address_valid'] is True
    
    def test_validate_contracting_authority_invalid(self):
        """Test contracting authority validation with invalid data."""
        validator = Validator()
        
        authority = ContractingAuthority(
            name="",  # Empty name
            address=""  # Empty address
        )
        
        result = validator._validate_contracting_authority(authority)
        
        assert result['is_valid'] is False
        assert result['name_valid'] is False
        assert result['address_valid'] is False
    
    def test_validate_contact_valid(self):
        """Test contact validation with valid data."""
        validator = Validator()
        
        contact = Contact(
            name="John Doe",
            email="john@ministry.gov"
        )
        
        result = validator._validate_contact(contact)
        
        assert result['is_valid'] is True
        assert result['name_valid'] is True
        assert result['email_valid'] is True
    
    def test_validate_contact_invalid(self):
        """Test contact validation with invalid data."""
        validator = Validator()
        
        contact = Contact(
            name="",  # Empty name
            email=""  # Empty email
        )
        
        result = validator._validate_contact(contact)
        
        assert result['is_valid'] is False
        assert result['name_valid'] is False
        assert result['email_valid'] is False
    
    def test_get_quality_indicators(self):
        """Test quality indicators calculation."""
        validator = Validator()
        
        tender_data = TenderData(
            tender_reference="EU-EN-2024-001",
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="Ministry of Energy",
                address="123 Government Street"
            ),
            subject="Renewable Energy Project",
            description="Development of renewable energy infrastructure",
            estimated_budget_eur=1000000.0,
            eligibility_requirements=["EU registered company"],
            tender_deadline="2024-03-15",
            contact=Contact(
                name="John Doe",
                email="john@ministry.gov"
            )
        )
        
        indicators = validator._get_quality_indicators(tender_data)
        
        assert 'has_contact' in indicators
        assert 'has_budget' in indicators
        assert 'has_requirements' in indicators
        assert 'completeness_score' in indicators
    
    def test_calculate_field_accuracy(self):
        """Test field accuracy calculation."""
        validator = Validator()
        
        extracted_data = TenderData(
            tender_reference="EU-EN-2024-001",
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="Ministry of Energy",
                address="123 Government Street"
            ),
            subject="Renewable Energy Project",
            description="Development of renewable energy infrastructure",
            estimated_budget_eur=1000000.0,
            eligibility_requirements=["EU registered company"],
            tender_deadline="2024-03-15",
            contact=Contact(
                name="John Doe",
                email="john@ministry.gov"
            )
        )
        
        ground_truth = {
            "tender_reference": "EU-EN-2024-001",
            "subject": "Renewable Energy Project",
            "estimated_budget_eur": 1000000.0
        }
        
        accuracy = validator._calculate_field_accuracy(extracted_data, ground_truth)
        
        assert accuracy['tender_reference'] == 1.0
        assert accuracy['subject'] == 1.0
        assert accuracy['estimated_budget_eur'] == 1.0
        assert 'overall_accuracy' in accuracy
    
    def test_find_discrepancies(self):
        """Test discrepancy detection."""
        validator = Validator()
        
        extracted_data = TenderData(
            tender_reference="EU-EN-2024-001",
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="Ministry of Energy",
                address="123 Government Street"
            ),
            subject="Renewable Energy Project",
            description="Development of renewable energy infrastructure",
            estimated_budget_eur=1000000.0,
            eligibility_requirements=["EU registered company"],
            tender_deadline="2024-03-15",
            contact=Contact(
                name="John Doe",
                email="john@ministry.gov"
            )
        )
        
        ground_truth = {
            "tender_reference": "EU-EN-2024-001",
            "subject": "Solar Energy Project",  # Different
            "estimated_budget_eur": 1500000.0  # Different
        }
        
        discrepancies = validator._find_discrepancies(extracted_data, ground_truth)
        
        assert len(discrepancies) == 2
        assert any(d['field'] == 'subject' for d in discrepancies)
        assert any(d['field'] == 'estimated_budget_eur' for d in discrepancies)
