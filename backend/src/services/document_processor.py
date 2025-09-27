"""
Document processor service for extracting text from various document formats.

This service handles PDF and text file processing, including chunking for large documents.
"""
import os
import tempfile
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import PyPDF2
import io
import re
from datetime import datetime

from ..models.processing_result import ProcessingResult, ProcessingStatus


class DocumentProcessor:
    """Service for processing documents and extracting text content."""
    
    def __init__(self, max_chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor.
        
        Args:
            max_chunk_size: Maximum size of text chunks for processing
            chunk_overlap: Overlap between consecutive chunks
        """
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_formats = ['.pdf', '.txt']
    
    def extract_text(self, file_content: bytes, content_type: str) -> str:
        """
        Extract text from document content.
        
        Args:
            file_content: Raw file content as bytes
            content_type: MIME type of the file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is not supported
            Exception: If text extraction fails
        """
        if content_type == 'application/pdf':
            return self._extract_pdf_text(file_content)
        elif content_type == 'text/plain':
            return self._extract_text_content(file_content)
        else:
            raise ValueError(f"Unsupported file type: {content_type}")
    
    def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF content."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                except Exception as e:
                    # Log error but continue with other pages
                    print(f"Error extracting text from page {page_num}: {e}")
                    continue
            
            return '\n\n'.join(text_content)
        
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_text_content(self, text_content: bytes) -> str:
        """Extract text from plain text content."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    return text_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 with error handling
            return text_content.decode('utf-8', errors='replace')
        
        except Exception as e:
            raise Exception(f"Failed to extract text from content: {str(e)}")
    
    def chunk_document(self, text: str) -> List[str]:
        """
        Split document into chunks for processing.
        
        Args:
            text: Full document text
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.max_chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start, end - 200)
                sentence_end = text.rfind('.', search_start, end)
                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for word boundaries
                    word_end = text.rfind(' ', start, end)
                    if word_end > start:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess extracted text for better LLM processing.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Preprocessed text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\@\#\$\%\&\*\+\=\<\>\|\\]', '', text)
        
        return text.strip()
    
    def validate_document(self, file_content: bytes, content_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate document before processing.
        
        Args:
            file_content: Raw file content
            content_type: MIME type of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            return False, f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB"
        
        # Check if file is empty
        if len(file_content) == 0:
            return False, "File is empty"
        
        # Validate content type
        if content_type not in ['application/pdf', 'text/plain']:
            return False, f"Unsupported file type: {content_type}"
        
        # Additional PDF validation
        if content_type == 'application/pdf':
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                if len(pdf_reader.pages) == 0:
                    return False, "PDF file contains no pages"
            except Exception as e:
                return False, f"Invalid PDF file: {str(e)}"
        
        return True, None
    
    def get_document_metadata(self, file_content: bytes, content_type: str) -> Dict[str, Any]:
        """
        Extract metadata from document.
        
        Args:
            file_content: Raw file content
            content_type: MIME type of the file
            
        Returns:
            Dictionary containing document metadata
        """
        metadata = {
            'file_size': len(file_content),
            'content_type': content_type,
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        if content_type == 'application/pdf':
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                metadata.update({
                    'page_count': len(pdf_reader.pages),
                    'pdf_info': pdf_reader.metadata or {}
                })
            except Exception:
                pass
        
        return metadata
    
    def process_document(self, file_content: bytes, content_type: str, 
                        ground_truth: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Process a document and return processing result.
        
        Args:
            file_content: Raw file content
            content_type: MIME type of the file
            ground_truth: Optional ground truth data for evaluation
            
        Returns:
            ProcessingResult object
        """
        # Create processing result
        result = ProcessingResult.create_pending(
            document_id=f"doc-{datetime.utcnow().timestamp()}"
        )
        
        try:
            # Start processing
            result.start_processing()
            result.update_progress("validation", 10.0)
            
            # Validate document
            is_valid, error_message = self.validate_document(file_content, content_type)
            if not is_valid:
                result.mark_failed(f"Document validation failed: {error_message}")
                return result
            
            result.update_progress("text_extraction", 30.0)
            
            # Extract text
            text = self.extract_text(file_content, content_type)
            if not text.strip():
                result.mark_failed("No text content found in document")
                return result
            
            result.update_progress("text_preprocessing", 50.0)
            
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            result.update_progress("chunking", 70.0)
            
            # Chunk document if necessary
            chunks = self.chunk_document(processed_text)
            
            result.update_progress("completion", 90.0)
            
            # Store processing metadata
            result.source_file_size = len(file_content)
            result.total_chunks = len(chunks)
            result.processed_chunks = len(chunks)
            
            # Mark as completed (extracted data will be added by LLM service)
            result.processing_status = ProcessingStatus.COMPLETED
            result.processing_end_time = datetime.utcnow()
            result.processing_time = (result.processing_end_time - result.processing_start_time).total_seconds()
            result.progress_percentage = 100.0
            
            return result
        
        except Exception as e:
            result.mark_failed(f"Document processing failed: {str(e)}")
            return result
    
    def save_processed_text(self, text: str, output_path: str) -> None:
        """
        Save processed text to file.
        
        Args:
            text: Processed text content
            output_path: Path to save the text file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    def load_processed_text(self, input_path: str) -> str:
        """
        Load processed text from file.
        
        Args:
            input_path: Path to the text file
            
        Returns:
            Text content
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return self.supported_formats.copy()
    
    def is_supported_format(self, content_type: str) -> bool:
        """Check if file format is supported."""
        return content_type in ['application/pdf', 'text/plain']
