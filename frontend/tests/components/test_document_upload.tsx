/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DocumentUpload from '../../src/components/DocumentUpload';

// Mock the API service
jest.mock('../../src/services/api', () => ({
  uploadDocument: jest.fn(),
  getProcessingStatus: jest.fn(),
}));

// Mock WebSocket for real-time updates
jest.mock('../../src/services/websocket', () => ({
  connect: jest.fn(),
  disconnect: jest.fn(),
  onProcessingUpdate: jest.fn(),
}));

describe('DocumentUpload Component', () => {
  const mockOnUploadSuccess = jest.fn();
  const mockOnUploadError = jest.fn();
  const mockOnProcessingUpdate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload form with file input', () => {
    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    // Check for file input
    const fileInput = screen.getByLabelText(/select file/i);
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveAttribute('type', 'file');
    expect(fileInput).toHaveAttribute('accept', '.pdf,.txt');

    // Check for upload button
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    expect(uploadButton).toBeInTheDocument();
    expect(uploadButton).toBeDisabled(); // Should be disabled initially
  });

  it('enables upload button when file is selected', () => {
    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const uploadButton = screen.getByRole('button', { name: /upload/i });

    // Initially disabled
    expect(uploadButton).toBeDisabled();

    // Create a mock file
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    // Simulate file selection
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Button should now be enabled
    expect(uploadButton).toBeEnabled();
  });

  it('shows file information when file is selected', () => {
    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Check that file information is displayed
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
    expect(screen.getByText(/application\/pdf/)).toBeInTheDocument();
  });

  it('handles PDF file upload successfully', async () => {
    const { uploadDocument } = require('../../src/services/api');
    uploadDocument.mockResolvedValue({
      document_id: 'test-doc-123',
      processing_status: 'pending',
      extracted_data: null,
      confidence_score: 0,
      processing_time: 0,
      evaluation_metrics: null
    });

    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    fireEvent.click(uploadButton);

    // Check loading state
    expect(screen.getByText(/uploading/i)).toBeInTheDocument();
    expect(uploadButton).toBeDisabled();

    await waitFor(() => {
      expect(uploadDocument).toHaveBeenCalledWith(file, null);
      expect(mockOnUploadSuccess).toHaveBeenCalledWith({
        document_id: 'test-doc-123',
        processing_status: 'pending',
        extracted_data: null,
        confidence_score: 0,
        processing_time: 0,
        evaluation_metrics: null
      });
    });
  });

  it('handles text file upload successfully', async () => {
    const { uploadDocument } = require('../../src/services/api');
    uploadDocument.mockResolvedValue({
      document_id: 'test-doc-456',
      processing_status: 'pending',
      extracted_data: null,
      confidence_score: 0,
      processing_time: 0,
      evaluation_metrics: null
    });

    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(uploadDocument).toHaveBeenCalledWith(file, null);
      expect(mockOnUploadSuccess).toHaveBeenCalled();
    });
  });

  it('handles upload with ground truth data', async () => {
    const { uploadDocument } = require('../../src/services/api');
    uploadDocument.mockResolvedValue({
      document_id: 'test-doc-789',
      processing_status: 'pending',
      extracted_data: null,
      confidence_score: 0,
      processing_time: 0,
      evaluation_metrics: null
    });

    const groundTruthData = {
      tender_reference: 'EU-EN-2024-056',
      publication_date: '2024-06-14',
      contracting_authority: {
        name: 'Ministry of Energy Transition',
        address: '12 Rue de Rivoli, 75001 Paris, France'
      }
    };

    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
        groundTruthData={groundTruthData}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(uploadDocument).toHaveBeenCalledWith(file, groundTruthData);
      expect(mockOnUploadSuccess).toHaveBeenCalled();
    });
  });

  it('handles upload error', async () => {
    const { uploadDocument } = require('../../src/services/api');
    uploadDocument.mockRejectedValue(new Error('Upload failed'));

    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockOnUploadError).toHaveBeenCalledWith('Upload failed');
      expect(screen.getByText(/upload failed/i)).toBeInTheDocument();
    });
  });

  it('validates file type', () => {
    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const file = new File(['test content'], 'test.exe', { type: 'application/x-msdownload' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
  });

  it('shows file size validation', () => {
    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
        maxFileSize={1024 * 1024} // 1MB
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    // Create a large file (2MB)
    const largeFile = new File(['x'.repeat(2 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [largeFile] } });

    expect(screen.getByText(/file too large/i)).toBeInTheDocument();
  });

  it('shows drag and drop functionality', () => {
    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const dropZone = screen.getByTestId('drop-zone');
    expect(dropZone).toBeInTheDocument();
    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
  });

  it('handles drag and drop file upload', async () => {
    const { uploadDocument } = require('../../src/services/api');
    uploadDocument.mockResolvedValue({
      document_id: 'test-doc-123',
      processing_status: 'pending',
      extracted_data: null,
      confidence_score: 0,
      processing_time: 0,
      evaluation_metrics: null
    });

    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const dropZone = screen.getByTestId('drop-zone');
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.dragOver(dropZone);
    fireEvent.drop(dropZone, { dataTransfer: { files: [file] } });

    await waitFor(() => {
      expect(uploadDocument).toHaveBeenCalledWith(file, null);
      expect(mockOnUploadSuccess).toHaveBeenCalled();
    });
  });

  it('shows processing status updates', async () => {
    const { getProcessingStatus } = require('../../src/services/api');
    getProcessingStatus.mockResolvedValue({
      document_id: 'test-doc-123',
      processing_status: 'processing',
      progress: 50
    });

    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    // Simulate processing status update
    const { onProcessingUpdate } = require('../../src/services/websocket');
    onProcessingUpdate.mockImplementation((callback) => {
      callback({
        document_id: 'test-doc-123',
        processing_status: 'processing',
        progress: 50
      });
    });

    await waitFor(() => {
      expect(mockOnProcessingUpdate).toHaveBeenCalledWith({
        document_id: 'test-doc-123',
        processing_status: 'processing',
        progress: 50
      });
    });
  });

  it('resets form after successful upload', async () => {
    const { uploadDocument } = require('../../src/services/api');
    uploadDocument.mockResolvedValue({
      document_id: 'test-doc-123',
      processing_status: 'pending',
      extracted_data: null,
      confidence_score: 0,
      processing_time: 0,
      evaluation_metrics: null
    });

    render(
      <DocumentUpload
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        onProcessingUpdate={mockOnProcessingUpdate}
      />
    );

    const fileInput = screen.getByLabelText(/select file/i);
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalled();
    });

    // Form should be reset
    expect(fileInput.files).toHaveLength(0);
    expect(uploadButton).toBeDisabled();
  });
});
