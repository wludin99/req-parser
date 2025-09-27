"""
Simple unit tests for LLMExtractor service.

Tests the basic LLM extraction functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
import json

from src.services.llm_extractor import LLMExtractor
from src.models.tender_data import TenderData, ContractingAuthority, Contact
from datetime import date


class TestLLMExtractor:
    """Test LLMExtractor service functionality."""
    
    def test_initialization(self):
        """Test LLMExtractor initialization."""
        extractor = LLMExtractor()
        
        assert extractor.config is not None
        assert 'openai' in extractor.config
        assert 'huggingface' in extractor.config
        assert 'free_models' in extractor.config
    
    def test_load_config_default(self):
        """Test loading default configuration."""
        extractor = LLMExtractor()
        config = extractor._load_config(None)
        
        assert 'openai' in config
        assert 'huggingface' in config
        assert 'free_models' in config
        assert config['openai']['model'] == 'gpt-4o-mini'
    
    def test_extract_structured_data_mock_mode(self):
        """Test extraction in mock mode when no API keys are available."""
        extractor = LLMExtractor()
        
        # Set API keys to None to trigger mock mode
        extractor.config['openai']['api_key'] = None
        extractor.config['huggingface']['api_key'] = None
        result = extractor.extract_structured_data("Sample text", None)
        
        assert isinstance(result, TenderData)
        assert result.tender_reference == "EU-EN-2024-056"
        assert result.subject == "Supply and installation of solar photovoltaic systems"
    
    def test_extract_with_mock(self):
        """Test mock extraction fallback."""
        extractor = LLMExtractor()
        
        result = extractor._extract_with_mock("Sample text", None)
        
        assert isinstance(result, TenderData)
        assert result.tender_reference == "EU-EN-2024-056"
        assert result.subject == "Supply and installation of solar photovoltaic systems"
        assert result.estimated_budget_eur == 2500000.0
    
    def test_parse_extraction_response_valid_json(self):
        """Test parsing valid JSON response."""
        extractor = LLMExtractor()
        
        valid_json = json.dumps({
            "tender_reference": "EU-EN-2024-003",
            "publication_date": "2024-01-17",
            "contracting_authority": {
                "name": "Ministry of Health",
                "address": "789 Health Street"
            },
            "subject": "Healthcare Infrastructure",
            "description": "Development of healthcare infrastructure",
            "estimated_budget_eur": 1500000.0,
            "eligibility_requirements": ["EU registered company"],
            "tender_deadline": "2024-03-17",
            "contact": {
                "name": "Dr. Smith",
                "email": "dr.smith@ministry.gov"
            }
        })
        
        result = extractor._parse_extraction_response(valid_json)
        
        assert isinstance(result, TenderData)
        assert result.tender_reference == "EU-EN-2024-003"
        assert result.subject == "Healthcare Infrastructure"
        assert result.estimated_budget_eur == 1500000.0
    
    def test_parse_extraction_response_empty_json(self):
        """Test parsing empty JSON response."""
        extractor = LLMExtractor()
        
        empty_json = "{}"
        result = extractor._parse_extraction_response(empty_json)
        
        # Should fall back to mock data
        assert isinstance(result, TenderData)
        assert result.tender_reference == "TBD"
    
    def test_build_extraction_prompt(self):
        """Test extraction prompt generation."""
        extractor = LLMExtractor()
        
        prompt = extractor._build_extraction_prompt("Sample text", None)
        
        assert "Sample text" in prompt
        assert "JSON" in prompt
        assert "tender_reference" in prompt
        assert "contracting_authority" in prompt
    
    def test_build_extraction_prompt_with_ground_truth(self):
        """Test extraction prompt generation with ground truth."""
        extractor = LLMExtractor()
        
        ground_truth = {
            "tender_reference": "EU-EN-2024-001",
            "subject": "Test Tender"
        }
        
        prompt = extractor._build_extraction_prompt("Sample text", ground_truth)
        
        assert "Sample text" in prompt
        assert "ground truth" in prompt.lower()
        assert "EU-EN-2024-001" in prompt
    
    def test_get_available_models(self):
        """Test getting available models."""
        extractor = LLMExtractor()
        
        models = extractor.get_available_models()
        
        assert isinstance(models, dict)
        assert 'openai' in models
        assert 'huggingface' in models
    
    def test_is_available(self):
        """Test service availability check."""
        extractor = LLMExtractor()
        
        # Check availability (may be False if no API keys, but mock mode should work)
        availability = extractor.is_available()
        assert isinstance(availability, bool)
    
    def test_get_service_status(self):
        """Test getting service status."""
        extractor = LLMExtractor()
        
        status = extractor.get_service_status()
        
        assert isinstance(status, dict)
        assert 'openai' in status
        assert 'huggingface' in status
