"""
LLM extractor service for structured data extraction.

This service uses LLM APIs to extract structured data from text content.
"""
import json
import yaml
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import openai
from huggingface_hub import InferenceClient
import os
from pathlib import Path

from ..models.tender_data import TenderData
from ..models.processing_result import ProcessingResult


class LLMExtractor:
    """Service for extracting structured data using LLM APIs."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize LLM extractor.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.openai_client = None
        self.huggingface_client = None
        
        # Initialize clients
        self._initialize_clients()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-4o-mini',
                'max_tokens': 4000,
                'temperature': 0.1
            },
            'huggingface': {
                'api_key': os.getenv('HUGGINGFACE_API_KEY'),
                'model': 'microsoft/DialoGPT-medium',
                'max_tokens': 2000,
                'temperature': 0.1
            },
            'extraction': {
                'max_retries': 3,
                'retry_delay': 1.0,
                'timeout': 30.0
            }
        }
    
    def _initialize_clients(self):
        """Initialize LLM API clients."""
        # Initialize OpenAI client
        if self.config['openai']['api_key']:
            self.openai_client = openai.OpenAI(
                api_key=self.config['openai']['api_key']
            )
        
        # Initialize Hugging Face client
        if self.config['huggingface']['api_key']:
            self.huggingface_client = InferenceClient(
                token=self.config['huggingface']['api_key']
            )
    
    def extract_structured_data(self, text: str, ground_truth: Optional[Dict[str, Any]] = None) -> TenderData:
        """
        Extract structured data from text using LLM.
        
        Args:
            text: Input text content
            ground_truth: Optional ground truth data for context
            
        Returns:
            Extracted TenderData object
            
        Raises:
            Exception: If extraction fails
        """
        # Try OpenAI first, then Hugging Face as fallback
        try:
            return self._extract_with_openai(text, ground_truth)
        except Exception as e:
            print(f"OpenAI extraction failed: {e}")
            if self.huggingface_client:
                try:
                    return self._extract_with_huggingface(text, ground_truth)
                except Exception as e2:
                    print(f"Hugging Face extraction failed: {e2}")
                    raise Exception(f"All LLM extraction methods failed. OpenAI: {e}, Hugging Face: {e2}")
            else:
                raise e
    
    def _extract_with_openai(self, text: str, ground_truth: Optional[Dict[str, Any]] = None) -> TenderData:
        """Extract data using OpenAI API."""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        prompt = self._build_extraction_prompt(text, ground_truth)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from government tender documents. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['openai']['max_tokens'],
                temperature=self.config['openai']['temperature']
            )
            
            content = response.choices[0].message.content
            return self._parse_extraction_response(content)
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _extract_with_huggingface(self, text: str, ground_truth: Optional[Dict[str, Any]] = None) -> TenderData:
        """Extract data using Hugging Face API."""
        if not self.huggingface_client:
            raise Exception("Hugging Face client not initialized")
        
        prompt = self._build_extraction_prompt(text, ground_truth)
        
        try:
            response = self.huggingface_client.text_generation(
                prompt,
                max_new_tokens=self.config['huggingface']['max_tokens'],
                temperature=self.config['huggingface']['temperature'],
                return_full_text=False
            )
            
            return self._parse_extraction_response(response)
        
        except Exception as e:
            raise Exception(f"Hugging Face API error: {str(e)}")
    
    def _build_extraction_prompt(self, text: str, ground_truth: Optional[Dict[str, Any]] = None) -> str:
        """Build extraction prompt for LLM."""
        prompt = f"""
Extract structured data from the following government tender document text. Return the result as a valid JSON object with the exact structure shown below.

Text to analyze:
{text}

Required JSON structure:
{{
    "tender_reference": "string",
    "publication_date": "YYYY-MM-DD",
    "contracting_authority": {{
        "name": "string",
        "address": "string"
    }},
    "subject": "string",
    "description": "string",
    "estimated_budget_eur": "float",
    "eligibility_requirements": ["string"],
    "tender_deadline": "YYYY-MM-DD HH:MM TZ",
    "contact": {{
        "name": "string",
        "email": "string"
    }}
}}

Instructions:
1. Extract all available information from the text
2. If information is not available, use null or empty string as appropriate
3. Ensure dates are in the correct format
4. Ensure email addresses are valid
5. Return only the JSON object, no additional text
"""
        
        if ground_truth:
            prompt += f"\n\nGround truth reference (use as guidance but extract from the actual text):\n{json.dumps(ground_truth, indent=2)}"
        
        return prompt
    
    def _parse_extraction_response(self, response: str) -> TenderData:
        """Parse LLM response and create TenderData object."""
        try:
            # Clean up response
            response = response.strip()
            
            # Remove any markdown formatting
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # Parse JSON
            data = json.loads(response)
            
            # Create TenderData object
            return TenderData(
                tender_reference=data.get('tender_reference', ''),
                publication_date=data.get('publication_date', ''),
                contracting_authority=data.get('contracting_authority', {}),
                subject=data.get('subject', ''),
                description=data.get('description', ''),
                estimated_budget_eur=data.get('estimated_budget_eur', 0.0),
                eligibility_requirements=data.get('eligibility_requirements', []),
                tender_deadline=data.get('tender_deadline', ''),
                contact=data.get('contact', {}),
                confidence_score=0.8,  # Default confidence
                extraction_timestamp=datetime.utcnow()
            )
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to create TenderData: {str(e)}")
    
    def extract_with_retry(self, text: str, ground_truth: Optional[Dict[str, Any]] = None) -> TenderData:
        """
        Extract data with retry logic.
        
        Args:
            text: Input text content
            ground_truth: Optional ground truth data
            
        Returns:
            Extracted TenderData object
        """
        max_retries = self.config['extraction']['max_retries']
        retry_delay = self.config['extraction']['retry_delay']
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.extract_structured_data(text, ground_truth)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    print(f"Extraction attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                    asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        raise Exception(f"Extraction failed after {max_retries} attempts. Last error: {last_exception}")
    
    def validate_extraction_quality(self, extracted_data: TenderData) -> Dict[str, Any]:
        """
        Validate the quality of extracted data.
        
        Args:
            extracted_data: Extracted TenderData object
            
        Returns:
            Quality metrics dictionary
        """
        quality_metrics = {
            'completeness': 0.0,
            'field_scores': {},
            'overall_quality': 0.0,
            'missing_fields': [],
            'validation_errors': []
        }
        
        # Check completeness
        required_fields = [
            'tender_reference', 'publication_date', 'contracting_authority',
            'subject', 'description', 'estimated_budget_eur',
            'eligibility_requirements', 'tender_deadline', 'contact'
        ]
        
        present_fields = 0
        for field in required_fields:
            value = getattr(extracted_data, field)
            if value is not None and value != '' and value != []:
                present_fields += 1
                quality_metrics['field_scores'][field] = 1.0
            else:
                quality_metrics['missing_fields'].append(field)
                quality_metrics['field_scores'][field] = 0.0
        
        quality_metrics['completeness'] = present_fields / len(required_fields)
        
        # Check for validation errors
        try:
            extracted_data.validate()
        except Exception as e:
            quality_metrics['validation_errors'].append(str(e))
        
        # Calculate overall quality
        field_scores = list(quality_metrics['field_scores'].values())
        quality_metrics['overall_quality'] = sum(field_scores) / len(field_scores) if field_scores else 0.0
        
        return quality_metrics
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models for each provider."""
        models = {
            'openai': [],
            'huggingface': []
        }
        
        if self.openai_client:
            models['openai'] = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo']
        
        if self.huggingface_client:
            models['huggingface'] = [
                'microsoft/DialoGPT-medium',
                'microsoft/DialoGPT-large',
                'facebook/blenderbot-400M-distill'
            ]
        
        return models
    
    def is_available(self) -> bool:
        """Check if any LLM service is available."""
        return self.openai_client is not None or self.huggingface_client is not None
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of each LLM service."""
        return {
            'openai': self.openai_client is not None,
            'huggingface': self.huggingface_client is not None
        }
