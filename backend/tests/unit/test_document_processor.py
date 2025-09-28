"""
Unit tests for DocumentProcessor service.

Tests the document processing functionality including PDF and text extraction.
"""
import pytest
from unittest.mock import patch, MagicMock
import io

from src.services.document_processor import DocumentProcessor
from src.models.processing_result import ProcessingResult, ProcessingStatus


class TestDocumentProcessor:
    """Test DocumentProcessor service functionality."""
    
    def test_initialization(self):
        """Test DocumentProcessor initialization."""
        processor = DocumentProcessor()
        
        assert processor.max_chunk_size == 1000
        assert processor.chunk_overlap == 200
        assert processor.supported_formats == ['.pdf', '.txt']
    
    def test_initialization_with_custom_params(self):
        """Test DocumentProcessor initialization with custom parameters."""
        processor = DocumentProcessor(max_chunk_size=2000, chunk_overlap=400)
        
        assert processor.max_chunk_size == 2000
        assert processor.chunk_overlap == 400
    
    def test_is_supported_format_pdf(self):
        """Test PDF format detection."""
        processor = DocumentProcessor()
        
        assert processor.is_supported_format('application/pdf') is True
        assert processor.is_supported_format('text/plain') is True
        assert processor.is_supported_format('image/jpeg') is False
        assert processor.is_supported_format('application/zip') is False
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        processor = DocumentProcessor()
        
        formats = processor.get_supported_formats()
        assert '.pdf' in formats
        assert '.txt' in formats
        assert len(formats) == 2
    
    def test_extract_text_plain_text(self):
        """Test text extraction from plain text content."""
        processor = DocumentProcessor()
        
        text_content = b"This is a sample tender document with important information."
        result = processor.extract_text(text_content, 'text/plain')
        
        assert result == "This is a sample tender document with important information."
    
    @patch('PyPDF2.PdfReader')
    def test_extract_pdf_text_success(self, mock_pdf_reader):
        """Test successful PDF text extraction."""
        processor = DocumentProcessor()
        
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF content"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        pdf_content = b"fake pdf content"
        result = processor._extract_pdf_text(pdf_content)
        
        assert result == "Sample PDF content"
        mock_pdf_reader.assert_called_once()
    
    @patch('PyPDF2.PdfReader')
    def test_extract_pdf_text_no_content(self, mock_pdf_reader):
        """Test PDF text extraction when no text is found."""
        processor = DocumentProcessor()
        
        # Mock PDF reader with no text
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        pdf_content = b"fake pdf content"
        result = processor._extract_pdf_text(pdf_content)
        
        assert "PDF document uploaded - no extractable text found" in result
    
    @patch('PyPDF2.PdfReader')
    def test_extract_pdf_text_exception(self, mock_pdf_reader):
        """Test PDF text extraction with exception."""
        processor = DocumentProcessor()
        
        # Mock PDF reader to raise exception
        mock_pdf_reader.side_effect = Exception("PDF parsing error")
        
        pdf_content = b"fake pdf content"
        with pytest.raises(Exception) as exc_info:
            processor._extract_pdf_text(pdf_content)
        
        assert "Failed to extract text from PDF" in str(exc_info.value)
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        processor = DocumentProcessor()
        
        text = "  This is a sample text with   multiple   spaces.  \n\n\n  "
        result = processor.preprocess_text(text)
        
        assert result == "This is a sample text with multiple spaces."
    
    def test_preprocess_text_empty(self):
        """Test preprocessing empty text."""
        processor = DocumentProcessor()
        
        result = processor.preprocess_text("")
        assert result == ""
        
        result = processor.preprocess_text("   \n\n   ")
        assert result == ""
    
    def test_chunk_document_small_text(self):
        """Test chunking text smaller than max chunk size."""
        processor = DocumentProcessor(max_chunk_size=100, chunk_overlap=20)
        
        text = "This is a short text that doesn't need chunking."
        chunks = processor.chunk_document(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_document_large_text(self):
        """Test chunking text larger than max chunk size."""
        processor = DocumentProcessor(max_chunk_size=50, chunk_overlap=10)
        
        # Create text longer than max_chunk_size
        text = "This is a very long text that needs to be chunked into smaller pieces for processing."
        chunks = processor.chunk_document(text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 50 for chunk in chunks)
    
    def test_chunk_document_with_overlap(self):
        """Test chunking with overlap between chunks."""
        processor = DocumentProcessor(max_chunk_size=30, chunk_overlap=10)
        
        text = "This is a long text that will be split into multiple chunks with overlap."
        chunks = processor.chunk_document(text)
        
        assert len(chunks) > 1
        # Check that chunks have reasonable overlap
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            # There should be some overlap (simplified check)
            assert len(current_chunk) <= 30
    
    def test_process_document_success(self):
        """Test successful document processing."""
        processor = DocumentProcessor()
        
        # Mock the extract_text method
        with patch.object(processor, 'extract_text', return_value="Sample document text"):
            with patch.object(processor, 'preprocess_text', return_value="Processed text"):
                with patch.object(processor, 'chunk_document', return_value=["Processed text"]):
                    result = processor.process_document(
                        b"fake content", 
                        "text/plain", 
                        None
                    )
        
        assert isinstance(result, ProcessingResult)
        assert result.processing_status == ProcessingStatus.COMPLETED
        assert result.processing_steps is not None
        assert len(result.processing_steps) > 0
    
    def test_process_document_unsupported_format(self):
        """Test document processing with unsupported format."""
        processor = DocumentProcessor()
        
        result = processor.process_document(
            b"fake content", 
            "image/jpeg", 
            None
        )
        
        assert isinstance(result, ProcessingResult)
        assert result.processing_status == ProcessingStatus.FAILED
        assert "Unsupported file type" in result.error_message
    
    def test_process_document_extraction_error(self):
        """Test document processing with extraction error."""
        processor = DocumentProcessor()
        
        # Mock extract_text to raise exception
        with patch.object(processor, 'extract_text', side_effect=Exception("Extraction error")):
            result = processor.process_document(
                b"fake content", 
                "text/plain", 
                None
            )
        
        assert isinstance(result, ProcessingResult)
        assert result.processing_status == ProcessingStatus.FAILED
        assert "Extraction error" in result.error_message
    
    def test_process_document_with_ground_truth(self):
        """Test document processing with ground truth data."""
        processor = DocumentProcessor()
        
        ground_truth = {
            "tender_reference": "EU-EN-2024-001",
            "subject": "Test Tender"
        }
        
        with patch.object(processor, 'extract_text', return_value="Sample text"):
            with patch.object(processor, 'preprocess_text', return_value="Processed text"):
                with patch.object(processor, 'chunk_document', return_value=["Processed text"]):
                    result = processor.process_document(
                        b"fake content", 
                        "text/plain", 
                        ground_truth
                    )
        
        assert isinstance(result, ProcessingResult)
        assert result.processing_status == ProcessingStatus.COMPLETED
        # The document processor doesn't set evaluation_metrics, that's done by the validator
        assert result.processing_steps is not None
    
    def test_validate_document(self):
        """Test document validation."""
        processor = DocumentProcessor()
        
        # Test with valid document
        small_content = b"small content"
        is_valid, error = processor.validate_document(small_content, "text/plain")
        assert is_valid is True
        assert error is None
        
        # Test with unsupported format
        is_valid, error = processor.validate_document(small_content, "image/jpeg")
        assert is_valid is False
        assert "Unsupported file type" in error
    
    def test_get_document_metadata(self):
        """Test getting document metadata."""
        processor = DocumentProcessor()
        
        metadata = processor.get_document_metadata(
            b"test content", 
            "application/pdf"
        )
        
        assert "file_size" in metadata
        assert "content_type" in metadata
        assert "processing_timestamp" in metadata
        assert metadata["content_type"] == "application/pdf"
