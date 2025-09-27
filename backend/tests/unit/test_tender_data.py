"""
Unit tests for TenderData model validation.

Tests the Pydantic model validation for TenderData and related models.
"""
import pytest
from datetime import date, datetime
from decimal import Decimal

from src.models.tender_data import TenderData, ContractingAuthority, Contact


class TestContractingAuthority:
    """Test ContractingAuthority model validation."""
    
    def test_valid_contracting_authority(self):
        """Test valid contracting authority creation."""
        authority = ContractingAuthority(
            name="Ministry of Energy",
            address="123 Government Street, Capital City"
        )
        
        assert authority.name == "Ministry of Energy"
        assert authority.address == "123 Government Street, Capital City"
    
    def test_missing_name(self):
        """Test validation error for missing name."""
        with pytest.raises(ValueError):
            ContractingAuthority(
                address="123 Government Street, Capital City"
            )
    
    def test_missing_address(self):
        """Test validation error for missing address."""
        with pytest.raises(ValueError):
            ContractingAuthority(
                name="Ministry of Energy"
            )


class TestContact:
    """Test Contact model validation."""
    
    def test_valid_contact(self):
        """Test valid contact creation."""
        contact = Contact(
            name="John Doe",
            email="john.doe@ministry.gov"
        )
        
        assert contact.name == "John Doe"
        assert contact.email == "john.doe@ministry.gov"
    
    def test_missing_name(self):
        """Test validation error for missing name."""
        with pytest.raises(ValueError):
            Contact(
                email="john.doe@ministry.gov"
            )
    
    def test_missing_email(self):
        """Test validation error for missing email."""
        with pytest.raises(ValueError):
            Contact(
                name="John Doe"
            )
    
    def test_invalid_email(self):
        """Test that invalid email format is accepted (str type allows any string)."""
        # Since email is str type, it accepts any string
        contact = Contact(
            name="John Doe",
            email="invalid-email"
        )
        assert contact.email == "invalid-email"


class TestTenderData:
    """Test TenderData model validation."""
    
    def test_valid_tender_data(self):
        """Test valid tender data creation."""
        tender_data = TenderData(
            tender_reference="EU-EN-2024-001",
            publication_date=date(2024, 1, 15),
            contracting_authority=ContractingAuthority(
                name="Ministry of Energy",
                address="123 Government Street, Capital City"
            ),
            subject="Renewable Energy Infrastructure",
            description="Development of renewable energy infrastructure projects",
            estimated_budget_eur=1000000.0,
            eligibility_requirements=[
                "Must be EU registered company",
                "Minimum 5 years experience",
                "Valid ISO certification"
            ],
            tender_deadline="2024-03-15",
            contact=Contact(
                name="Jane Smith",
                email="jane.smith@ministry.gov"
            )
        )
        
        assert tender_data.tender_reference == "EU-EN-2024-001"
        assert tender_data.publication_date == date(2024, 1, 15)
        assert tender_data.contracting_authority.name == "Ministry of Energy"
        assert tender_data.subject == "Renewable Energy Infrastructure"
        assert tender_data.estimated_budget_eur == 1000000.0
        assert len(tender_data.eligibility_requirements) == 3
        assert tender_data.contact.name == "Jane Smith"
    
    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValueError):
            TenderData(
                tender_reference="EU-EN-2024-001",
                # Missing publication_date
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
            )
    
    def test_negative_budget(self):
        """Test validation error for negative budget."""
        with pytest.raises(ValueError):
            TenderData(
                tender_reference="EU-EN-2024-001",
                publication_date=date(2024, 1, 15),
                contracting_authority=ContractingAuthority(
                    name="Ministry of Energy",
                    address="123 Government Street"
                ),
                subject="Test Subject",
                description="Test Description",
                estimated_budget_eur=-1000.0,  # Negative budget
                eligibility_requirements=["Requirement 1"],
                tender_deadline="2024-03-15",
                contact=Contact(
                    name="John Doe",
                    email="john@example.com"
                )
            )
    
    def test_empty_eligibility_requirements(self):
        """Test validation error for empty eligibility requirements."""
        with pytest.raises(ValueError):
            TenderData(
                tender_reference="EU-EN-2024-001",
                publication_date=date(2024, 1, 15),
                contracting_authority=ContractingAuthority(
                    name="Ministry of Energy",
                    address="123 Government Street"
                ),
                subject="Test Subject",
                description="Test Description",
                estimated_budget_eur=100000.0,
                eligibility_requirements=[],  # Empty list
                tender_deadline="2024-03-15",
                contact=Contact(
                    name="John Doe",
                    email="john@example.com"
                )
            )
    
    def test_confidence_score_validation(self):
        """Test confidence score validation."""
        # Valid confidence score
        tender_data = TenderData(
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
            ),
            confidence_score=0.85
        )
        assert tender_data.confidence_score == 0.85
        
        # Invalid confidence score (too high)
        with pytest.raises(ValueError):
            TenderData(
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
                ),
                confidence_score=1.5  # Invalid: > 1.0
            )
    
    def test_from_dict_method(self):
        """Test from_dict class method."""
        data_dict = {
            "tender_reference": "EU-EN-2024-001",
            "publication_date": "2024-01-15",
            "contracting_authority": {
                "name": "Ministry of Energy",
                "address": "123 Government Street"
            },
            "subject": "Test Subject",
            "description": "Test Description",
            "estimated_budget_eur": 100000.0,
            "eligibility_requirements": ["Requirement 1"],
            "tender_deadline": "2024-03-15",
            "contact": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
        
        tender_data = TenderData.from_dict(data_dict)
        
        assert tender_data.tender_reference == "EU-EN-2024-001"
        assert tender_data.publication_date == date(2024, 1, 15)
        assert tender_data.contracting_authority.name == "Ministry of Energy"
    
    def test_to_dict_method(self):
        """Test to_dict method."""
        tender_data = TenderData(
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
        )
        
        data_dict = tender_data.to_dict()
        
        assert data_dict["tender_reference"] == "EU-EN-2024-001"
        assert data_dict["publication_date"] == date(2024, 1, 15)  # model_dump() returns date object
        assert data_dict["contracting_authority"]["name"] == "Ministry of Energy"
        assert data_dict["estimated_budget_eur"] == 100000.0
