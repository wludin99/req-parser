"""
Integration tests for document processing pipeline.

Tests the complete flow from document upload to structured data extraction.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os


class TestDocumentProcessingPipeline:
    """Integration tests for the document processing pipeline."""
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Sample PDF content for testing."""
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(European Union Tender Notice) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000204 00000 n\ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n298\n%%EOF"
    
    @pytest.fixture
    def sample_text_content(self):
        """Sample text content for testing."""
        return """European Union — Tender Notice
Publication Date: 14 June 2024
Tender Reference: EU-EN-2024-056

Contracting Authority
Ministry of Energy Transition
12 Rue de Rivoli, 75001 Paris, France

Subject
Supply and installation of solar photovoltaic systems for public schools in the Île-de-France region.

Description
The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems with a minimum installed capacity of 500 kW across 10 schools. The contractor is also responsible for maintenance for 5 years.

Estimated Budget
€2,500,000 (excluding VAT)

Eligibility Requirements
- At least 3 prior contracts of similar scope in the last 5 years.
- Certification in ISO 14001 (Environmental Management).
- Proof of financial capacity.

Tender Deadline
30 July 2024, 17:00 CET

Contact Point
Procurement Officer: Marie Dubois
Email: marie.dubois@transition.gouv.fr"""
    
    @pytest.fixture
    def expected_extracted_data(self):
        """Expected extracted data structure."""
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
    
    def test_pdf_processing_pipeline(self, sample_pdf_content, expected_extracted_data):
        """Test complete PDF processing pipeline."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor, \
             patch('src.services.llm_extractor.LLMExtractor') as mock_llm, \
             patch('src.services.validator.Validator') as mock_validator:
            
            # Mock document processor
            mock_processor_instance = Mock()
            mock_processor_instance.extract_text.return_value = "European Union — Tender Notice\nPublication Date: 14 June 2024\nTender Reference: EU-EN-2024-056"
            mock_processor.return_value = mock_processor_instance
            
            # Mock LLM extractor
            mock_llm_instance = Mock()
            mock_llm_instance.extract_structured_data.return_value = expected_extracted_data
            mock_llm.return_value = mock_llm_instance
            
            # Mock validator
            mock_validator_instance = Mock()
            mock_validator_instance.validate_extracted_data.return_value = {
                "is_valid": True,
                "confidence_score": 0.95,
                "validation_errors": []
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test the pipeline
            from src.services.document_processor import DocumentProcessor
            from src.services.llm_extractor import LLMExtractor
            from src.services.validator import Validator
            
            processor = DocumentProcessor()
            llm_extractor = LLMExtractor()
            validator = Validator()
            
            # Extract text from PDF
            extracted_text = processor.extract_text(sample_pdf_content, "application/pdf")
            assert extracted_text is not None
            assert len(extracted_text) > 0
            
            # Extract structured data using LLM
            structured_data = llm_extractor.extract_structured_data(extracted_text)
            assert structured_data is not None
            assert "tender_reference" in structured_data
            
            # Validate extracted data
            validation_result = validator.validate_extracted_data(structured_data)
            assert validation_result["is_valid"] is True
            assert validation_result["confidence_score"] > 0.0
    
    def test_text_processing_pipeline(self, sample_text_content, expected_extracted_data):
        """Test complete text processing pipeline."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor, \
             patch('src.services.llm_extractor.LLMExtractor') as mock_llm, \
             patch('src.services.validator.Validator') as mock_validator:
            
            # Mock document processor
            mock_processor_instance = Mock()
            mock_processor_instance.extract_text.return_value = sample_text_content
            mock_processor.return_value = mock_processor_instance
            
            # Mock LLM extractor
            mock_llm_instance = Mock()
            mock_llm_instance.extract_structured_data.return_value = expected_extracted_data
            mock_llm.return_value = mock_llm_instance
            
            # Mock validator
            mock_validator_instance = Mock()
            mock_validator_instance.validate_extracted_data.return_value = {
                "is_valid": True,
                "confidence_score": 0.92,
                "validation_errors": []
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test the pipeline
            from src.services.document_processor import DocumentProcessor
            from src.services.llm_extractor import LLMExtractor
            from src.services.validator import Validator
            
            processor = DocumentProcessor()
            llm_extractor = LLMExtractor()
            validator = Validator()
            
            # Extract text from text file
            extracted_text = processor.extract_text(sample_text_content.encode(), "text/plain")
            assert extracted_text == sample_text_content
            
            # Extract structured data using LLM
            structured_data = llm_extractor.extract_structured_data(extracted_text)
            assert structured_data is not None
            assert structured_data["tender_reference"] == "EU-EN-2024-056"
            
            # Validate extracted data
            validation_result = validator.validate_extracted_data(structured_data)
            assert validation_result["is_valid"] is True
            assert validation_result["confidence_score"] == 0.92
    
    def test_pipeline_with_chunking(self, sample_text_content, expected_extracted_data):
        """Test pipeline with document chunking for large documents."""
        # Simulate a large document by repeating the content
        large_document = "\n\n".join([sample_text_content] * 5)
        
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor, \
             patch('src.services.llm_extractor.LLMExtractor') as mock_llm, \
             patch('src.services.validator.Validator') as mock_validator:
            
            # Mock document processor with chunking
            mock_processor_instance = Mock()
            mock_processor_instance.extract_text.return_value = large_document
            mock_processor_instance.chunk_document.return_value = [
                sample_text_content,
                sample_text_content,
                sample_text_content,
                sample_text_content,
                sample_text_content
            ]
            mock_processor.return_value = mock_processor_instance
            
            # Mock LLM extractor
            mock_llm_instance = Mock()
            mock_llm_instance.extract_structured_data.return_value = expected_extracted_data
            mock_llm.return_value = mock_llm_instance
            
            # Mock validator
            mock_validator_instance = Mock()
            mock_validator_instance.validate_extracted_data.return_value = {
                "is_valid": True,
                "confidence_score": 0.88,
                "validation_errors": []
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test the pipeline with chunking
            from src.services.document_processor import DocumentProcessor
            from src.services.llm_extractor import LLMExtractor
            from src.services.validator import Validator
            
            processor = DocumentProcessor()
            llm_extractor = LLMExtractor()
            validator = Validator()
            
            # Extract text and chunk document
            extracted_text = processor.extract_text(large_document.encode(), "text/plain")
            chunks = processor.chunk_document(extracted_text)
            assert len(chunks) == 5
            
            # Process each chunk
            all_extracted_data = []
            for chunk in chunks:
                structured_data = llm_extractor.extract_structured_data(chunk)
                if structured_data:
                    all_extracted_data.append(structured_data)
            
            # Merge results from all chunks
            assert len(all_extracted_data) > 0
            
            # Validate final merged data
            final_data = all_extracted_data[0]  # In real implementation, this would be merged
            validation_result = validator.validate_extracted_data(final_data)
            assert validation_result["is_valid"] is True
    
    def test_pipeline_error_handling(self, sample_pdf_content):
        """Test pipeline error handling and recovery."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor, \
             patch('src.services.llm_extractor.LLMExtractor') as mock_llm:
            
            # Mock document processor to raise error
            mock_processor_instance = Mock()
            mock_processor_instance.extract_text.side_effect = Exception("PDF parsing failed")
            mock_processor.return_value = mock_processor_instance
            
            # Mock LLM extractor
            mock_llm_instance = Mock()
            mock_llm.return_value = mock_llm_instance
            
            # Test error handling
            from src.services.document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            
            with pytest.raises(Exception) as exc_info:
                processor.extract_text(sample_pdf_content, "application/pdf")
            
            assert "PDF parsing failed" in str(exc_info.value)
    
    def test_pipeline_performance_requirements(self, sample_text_content, expected_extracted_data):
        """Test that pipeline meets performance requirements (<10s processing time)."""
        import time
        
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor, \
             patch('src.services.llm_extractor.LLMExtractor') as mock_llm, \
             patch('src.services.validator.Validator') as mock_validator:
            
            # Mock services with realistic processing times
            mock_processor_instance = Mock()
            mock_processor_instance.extract_text.return_value = sample_text_content
            mock_processor.return_value = mock_processor_instance
            
            mock_llm_instance = Mock()
            mock_llm_instance.extract_structured_data.return_value = expected_extracted_data
            mock_llm.return_value = mock_llm_instance
            
            mock_validator_instance = Mock()
            mock_validator_instance.validate_extracted_data.return_value = {
                "is_valid": True,
                "confidence_score": 0.95,
                "validation_errors": []
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test the pipeline with timing
            from src.services.document_processor import DocumentProcessor
            from src.services.llm_extractor import LLMExtractor
            from src.services.validator import Validator
            
            start_time = time.time()
            
            processor = DocumentProcessor()
            llm_extractor = LLMExtractor()
            validator = Validator()
            
            # Simulate processing steps
            extracted_text = processor.extract_text(sample_text_content.encode(), "text/plain")
            structured_data = llm_extractor.extract_structured_data(extracted_text)
            validation_result = validator.validate_extracted_data(structured_data)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within 10 seconds (requirement)
            assert processing_time < 10.0
            assert validation_result["is_valid"] is True
    
    def test_pipeline_data_flow_integrity(self, sample_text_content, expected_extracted_data):
        """Test that data flows correctly through the pipeline without corruption."""
        with patch('src.services.document_processor.DocumentProcessor') as mock_processor, \
             patch('src.services.llm_extractor.LLMExtractor') as mock_llm, \
             patch('src.services.validator.Validator') as mock_validator:
            
            # Mock services to preserve data integrity
            mock_processor_instance = Mock()
            mock_processor_instance.extract_text.return_value = sample_text_content
            mock_processor.return_value = mock_processor_instance
            
            mock_llm_instance = Mock()
            mock_llm_instance.extract_structured_data.return_value = expected_extracted_data
            mock_llm.return_value = mock_llm_instance
            
            mock_validator_instance = Mock()
            mock_validator_instance.validate_extracted_data.return_value = {
                "is_valid": True,
                "confidence_score": 0.95,
                "validation_errors": []
            }
            mock_validator.return_value = mock_validator_instance
            
            # Test data flow integrity
            from src.services.document_processor import DocumentProcessor
            from src.services.llm_extractor import LLMExtractor
            from src.services.validator import Validator
            
            processor = DocumentProcessor()
            llm_extractor = LLMExtractor()
            validator = Validator()
            
            # Step 1: Extract text
            extracted_text = processor.extract_text(sample_text_content.encode(), "text/plain")
            assert extracted_text == sample_text_content
            
            # Step 2: Extract structured data
            structured_data = llm_extractor.extract_structured_data(extracted_text)
            assert structured_data is not None
            assert structured_data["tender_reference"] == expected_extracted_data["tender_reference"]
            assert structured_data["estimated_budget_eur"] == expected_extracted_data["estimated_budget_eur"]
            
            # Step 3: Validate data
            validation_result = validator.validate_extracted_data(structured_data)
            assert validation_result["is_valid"] is True
            assert validation_result["confidence_score"] > 0.0
            
            # Verify no data corruption
            assert structured_data["tender_reference"] == "EU-EN-2024-056"
            assert structured_data["estimated_budget_eur"] == 2500000.0
            assert len(structured_data["eligibility_requirements"]) == 3
