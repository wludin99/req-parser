"""
Unit tests for LLMExtractor service.

Tests the LLM extraction functionality including API integration and fallback mechanisms.
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
    
    def test_initialization_with_config_path(self):
        """Test LLMExtractor initialization with config file."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open_config()):
                extractor = LLMExtractor(config_path="test_config.yaml")
                assert extractor.config is not None
    
    def test_load_config_default(self):
        """Test loading default configuration."""
        extractor = LLMExtractor()
        config = extractor._load_config(None)
        
        assert 'openai' in config
        assert 'huggingface' in config
        assert 'free_models' in config
        assert config['openai']['model'] == 'gpt-4o-mini'
    
    @patch('os.getenv')
    def test_load_config_with_env_vars(self, mock_getenv):
        """Test loading configuration with environment variables."""
        mock_getenv.side_effect = lambda key: {
            'OPENAI_API_KEY': 'test_openai_key',
            'HUGGINGFACE_API_KEY': 'test_hf_key'
        }.get(key)
        
        extractor = LLMExtractor()
        config = extractor._load_config(None)
        
        assert config['openai']['api_key'] == 'test_openai_key'
        assert config['huggingface']['api_key'] == 'test_hf_key'
    
    def test_extract_structured_data_mock_mode(self):
        """Test extraction in mock mode when no API keys are available."""
        extractor = LLMExtractor()
        
        # Mock the API key checks to return None
        # Mock the API key checks by setting config values
        extractor.config['openai']['api_key'] = None
        extractor.config['huggingface']['api_key'] = None
        result = extractor.extract_structured_data("Sample text", None)
        
        assert isinstance(result, TenderData)
        assert result.tender_reference == "EU-EN-2024-056"
        assert result.subject == "Supply and installation of solar photovoltaic systems"
    
    def test_extract_structured_data_openai_success(self):
        """Test successful extraction with OpenAI."""
        extractor = LLMExtractor()
        
        # Set OpenAI API key to trigger OpenAI path
        extractor.config['openai']['api_key'] = 'test_key'
        extractor.config['huggingface']['api_key'] = None
        
        # Mock the OpenAI extraction method
        with patch.object(extractor, '_extract_with_openai') as mock_openai:
            mock_openai.return_value = TenderData(
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
            
            result = extractor.extract_structured_data("Sample text", None)
        
        assert isinstance(result, TenderData)
        assert result.tender_reference == "EU-EN-2024-001"
        assert result.subject == "Renewable Energy Project"
        assert result.estimated_budget_eur == 1000000.0
    
    def test_extract_structured_data_openai_error(self):
        """Test OpenAI extraction with error handling."""
        extractor = LLMExtractor()
        
        # Set OpenAI API key to trigger OpenAI path
        extractor.config['openai']['api_key'] = 'test_key'
        extractor.config['huggingface']['api_key'] = None
        
        # Mock the OpenAI extraction method to raise exception
        with patch.object(extractor, '_extract_with_openai', side_effect=Exception("API Error")):
            result = extractor.extract_structured_data("Sample text", None)
        
        # Should fall back to mock mode
        assert isinstance(result, TenderData)
        assert result.tender_reference == "EU-EN-2024-056"
    
    def test_extract_with_huggingface_providers_success(self):
        """Test successful extraction with Hugging Face providers."""
        extractor = LLMExtractor()
        
        # Mock the Hugging Face providers extraction method
        with patch.object(extractor, '_extract_with_huggingface_providers') as mock_hf:
            mock_hf.return_value = TenderData(
                tender_reference="EU-EN-2024-002",
                publication_date=date(2024, 1, 16),
                contracting_authority=ContractingAuthority(
                    name="Ministry of Transport",
                    address="456 Transport Street"
                ),
                subject="Transport Infrastructure",
                description="Development of transport infrastructure",
                estimated_budget_eur=2000000.0,
                eligibility_requirements=["EU registered company", "5 years experience"],
                tender_deadline="2024-03-16",
                contact=Contact(
                    name="Jane Smith",
                    email="jane@ministry.gov"
                )
            )
            
            result = extractor._extract_with_huggingface_providers("Sample text", None)
        
        assert isinstance(result, TenderData)
        assert result.tender_reference == "EU-EN-2024-002"
        assert result.subject == "Transport Infrastructure"
        assert result.estimated_budget_eur == 2000000.0
    
    @patch('requests.post')
    def test_extract_with_huggingface_providers_error(self, mock_post):
        """Test Hugging Face extraction with error handling."""
        extractor = LLMExtractor()
        
        # Mock request to raise exception
        mock_post.side_effect = Exception("Network error")
        
        with patch.object(extractor, '_has_huggingface_key', return_value=True):
            result = extractor._extract_with_huggingface_providers("Sample text", None)
        
        # Should fall back to mock mode
        assert isinstance(result, TenderData)
        assert result.tender_reference == "TBD"
    
    def test_extract_with_mock(self):
        """Test mock extraction fallback."""
        extractor = LLMExtractor()
        
        result = extractor._extract_with_mock("Sample text", None)
        
        assert isinstance(result, TenderData)
        assert result.tender_reference == "TBD"
        assert result.subject == "Document Analysis"
        assert result.estimated_budget_eur == 0.0
    
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
    
    def test_parse_extraction_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        extractor = LLMExtractor()
        
        invalid_json = "invalid json content"
        result = extractor._parse_extraction_response(invalid_json)
        
        # Should fall back to mock data
        assert isinstance(result, TenderData)
        assert result.tender_reference == "TBD"
    
    def test_parse_extraction_response_empty_json(self):
        """Test parsing empty JSON response."""
        extractor = LLMExtractor()
        
        empty_json = "{}"
        result = extractor._parse_extraction_response(empty_json)
        
        # Should fall back to mock data
        assert isinstance(result, TenderData)
        assert result.tender_reference == "TBD"
    
    def test_has_openai_key_true(self):
        """Test OpenAI API key detection when key is present."""
        extractor = LLMExtractor()
        extractor.config['openai']['api_key'] = 'test_key'
        
        assert extractor._has_openai_key() is True
    
    def test_has_openai_key_false(self):
        """Test OpenAI API key detection when key is missing."""
        extractor = LLMExtractor()
        extractor.config['openai']['api_key'] = None
        
        assert extractor._has_openai_key() is False
    
    def test_has_huggingface_key_true(self):
        """Test Hugging Face API key detection when key is present."""
        extractor = LLMExtractor()
        extractor.config['huggingface']['api_key'] = 'test_key'
        
        assert extractor._has_huggingface_key() is True
    
    def test_has_huggingface_key_false(self):
        """Test Hugging Face API key detection when key is missing."""
        extractor = LLMExtractor()
        extractor.config['huggingface']['api_key'] = None
        
        assert extractor._has_huggingface_key() is False
    
    def test_get_extraction_prompt(self):
        """Test extraction prompt generation."""
        extractor = LLMExtractor()
        
        prompt = extractor._get_extraction_prompt("Sample text", None)
        
        assert "Sample text" in prompt
        assert "JSON" in prompt
        assert "tender_reference" in prompt
        assert "contracting_authority" in prompt
    
    def test_get_extraction_prompt_with_ground_truth(self):
        """Test extraction prompt generation with ground truth."""
        extractor = LLMExtractor()
        
        ground_truth = {
            "tender_reference": "EU-EN-2024-001",
            "subject": "Test Tender"
        }
        
        prompt = extractor._get_extraction_prompt("Sample text", ground_truth)
        
        assert "Sample text" in prompt
        assert "ground truth" in prompt.lower()
        assert "EU-EN-2024-001" in prompt


def mock_open_config():
    """Mock function for opening config files."""
    import yaml
    config_content = {
        'openai': {
            'api_key': 'test_key',
            'model': 'gpt-4'
        },
        'huggingface': {
            'api_key': 'test_hf_key',
            'model': 'test_model'
        }
    }
    
    def mock_open(file_path, mode):
        class MockFile:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return yaml.dump(config_content)
        return MockFile()
    
    return mock_open
