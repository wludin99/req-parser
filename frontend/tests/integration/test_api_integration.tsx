/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import App from '../../src/App';

// Mock the API service
const mockApiService = {
  uploadDocument: jest.fn(),
  getProcessingStatus: jest.fn(),
  getExtractionResults: jest.fn(),
  evaluateResults: jest.fn(),
};

jest.mock('../../src/services/api', () => mockApiService);

// Mock WebSocket service
const mockWebSocketService = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  onProcessingUpdate: jest.fn(),
  sendMessage: jest.fn(),
};

jest.mock('../../src/services/websocket', () => mockWebSocketService);

describe('API Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderWithRouter = (component: React.ReactElement) => {
    return render(
      <BrowserRouter>
        {component}
      </BrowserRouter>
    );
  };

  describe('Document Upload Flow', () => {
    it('handles complete document upload and processing flow', async () => {
      // Mock successful upload
      mockApiService.uploadDocument.mockResolvedValue({
        document_id: 'test-doc-123',
        processing_status: 'pending',
        extracted_data: null,
        confidence_score: 0,
        processing_time: 0,
        evaluation_metrics: null
      });

      // Mock processing status updates
      mockWebSocketService.onProcessingUpdate.mockImplementation((callback) => {
        // Simulate processing updates
        setTimeout(() => callback({
          document_id: 'test-doc-123',
          processing_status: 'processing',
          progress: 50
        }), 100);
        
        setTimeout(() => callback({
          document_id: 'test-doc-123',
          processing_status: 'completed',
          progress: 100
        }), 200);
      });

      // Mock final results
      mockApiService.getExtractionResults.mockResolvedValue({
        document_id: 'test-doc-123',
        processing_status: 'completed',
        extracted_data: {
          tender_reference: 'EU-EN-2024-056',
          publication_date: '2024-06-14',
          contracting_authority: {
            name: 'Ministry of Energy Transition',
            address: '12 Rue de Rivoli, 75001 Paris, France'
          },
          subject: 'Supply and installation of solar photovoltaic systems',
          description: 'The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems',
          estimated_budget_eur: 2500000.0,
          eligibility_requirements: [
            'At least 3 prior contracts of similar scope in the last 5 years.',
            'Certification in ISO 14001 (Environmental Management).',
            'Proof of financial capacity.'
          ],
          tender_deadline: '2024-07-30 17:00 CET',
          contact: {
            name: 'Marie Dubois',
            email: 'marie.dubois@transition.gouv.fr'
          }
        },
        confidence_score: 0.95,
        processing_time: 2.5,
        evaluation_metrics: {
          accuracy: 0.95,
          completeness: 1.0,
          field_accuracy: {
            tender_reference: 1.0,
            publication_date: 1.0,
            contracting_authority: 0.9,
            subject: 1.0,
            description: 0.95,
            estimated_budget_eur: 1.0,
            eligibility_requirements: 1.0,
            tender_deadline: 1.0,
            contact: 1.0
          }
        }
      });

      renderWithRouter(<App />);

      // Navigate to upload page
      const uploadLink = screen.getByText(/Upload Document/);
      fireEvent.click(uploadLink);

      // Upload a file
      const fileInput = screen.getByLabelText(/select file/i);
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      // Verify upload API call
      await waitFor(() => {
        expect(mockApiService.uploadDocument).toHaveBeenCalledWith(file, null);
      });

      // Verify WebSocket connection
      expect(mockWebSocketService.connect).toHaveBeenCalled();

      // Wait for processing updates
      await waitFor(() => {
        expect(screen.getByText(/Processing/)).toBeInTheDocument();
      });

      // Wait for completion
      await waitFor(() => {
        expect(screen.getByText(/Completed/)).toBeInTheDocument();
      });

      // Verify results are displayed
      await waitFor(() => {
        expect(screen.getByText('EU-EN-2024-056')).toBeInTheDocument();
        expect(screen.getByText('Ministry of Energy Transition')).toBeInTheDocument();
        expect(screen.getByText('€2,500,000')).toBeInTheDocument();
      });
    });

    it('handles upload error and retry', async () => {
      // Mock upload failure
      mockApiService.uploadDocument.mockRejectedValue(new Error('Upload failed'));

      renderWithRouter(<App />);

      const uploadLink = screen.getByText(/Upload Document/);
      fireEvent.click(uploadLink);

      const fileInput = screen.getByLabelText(/select file/i);
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      // Wait for error
      await waitFor(() => {
        expect(screen.getByText(/Upload failed/)).toBeInTheDocument();
      });

      // Retry upload
      mockApiService.uploadDocument.mockResolvedValue({
        document_id: 'test-doc-456',
        processing_status: 'pending',
        extracted_data: null,
        confidence_score: 0,
        processing_time: 0,
        evaluation_metrics: null
      });

      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(mockApiService.uploadDocument).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Evaluation Flow', () => {
    it('handles complete evaluation flow', async () => {
      // Mock initial results
      mockApiService.getExtractionResults.mockResolvedValue({
        document_id: 'test-doc-123',
        processing_status: 'completed',
        extracted_data: {
          tender_reference: 'EU-EN-2024-056',
          publication_date: '2024-06-14',
          contracting_authority: {
            name: 'Ministry of Energy Transition',
            address: '12 Rue de Rivoli, 75001 Paris, France'
          },
          subject: 'Supply and installation of solar photovoltaic systems',
          description: 'The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems',
          estimated_budget_eur: 2500000.0,
          eligibility_requirements: [
            'At least 3 prior contracts of similar scope in the last 5 years.',
            'Certification in ISO 14001 (Environmental Management).',
            'Proof of financial capacity.'
          ],
          tender_deadline: '2024-07-30 17:00 CET',
          contact: {
            name: 'Marie Dubois',
            email: 'marie.dubois@transition.gouv.fr'
          }
        },
        confidence_score: 0.95,
        processing_time: 2.5,
        evaluation_metrics: null
      });

      // Mock evaluation results
      mockApiService.evaluateResults.mockResolvedValue({
        document_id: 'test-doc-123',
        overall_accuracy: 0.95,
        field_accuracy: {
          tender_reference: 1.0,
          publication_date: 1.0,
          contracting_authority: 0.9,
          subject: 1.0,
          description: 0.95,
          estimated_budget_eur: 1.0,
          eligibility_requirements: 1.0,
          tender_deadline: 1.0,
          contact: 1.0
        },
        completeness: 1.0,
        discrepancies: [],
        evaluation_timestamp: '2024-09-27T21:00:00Z'
      });

      renderWithRouter(<App />);

      // Navigate to results page
      const resultsLink = screen.getByText(/View Results/);
      fireEvent.click(resultsLink);

      // Wait for results to load
      await waitFor(() => {
        expect(screen.getByText('EU-EN-2024-056')).toBeInTheDocument();
      });

      // Click evaluate button
      const evaluateButton = screen.getByRole('button', { name: /evaluate/i });
      fireEvent.click(evaluateButton);

      // Wait for evaluation
      await waitFor(() => {
        expect(mockApiService.evaluateResults).toHaveBeenCalledWith('test-doc-123');
      });

      // Verify evaluation results are displayed
      await waitFor(() => {
        expect(screen.getByText(/Overall Accuracy: 95%/)).toBeInTheDocument();
        expect(screen.getByText(/Completeness: 100%/)).toBeInTheDocument();
      });
    });

    it('handles evaluation error', async () => {
      mockApiService.getExtractionResults.mockResolvedValue({
        document_id: 'test-doc-123',
        processing_status: 'completed',
        extracted_data: {
          tender_reference: 'EU-EN-2024-056'
        },
        confidence_score: 0.95,
        processing_time: 2.5,
        evaluation_metrics: null
      });

      mockApiService.evaluateResults.mockRejectedValue(new Error('Evaluation failed'));

      renderWithRouter(<App />);

      const resultsLink = screen.getByText(/View Results/);
      fireEvent.click(resultsLink);

      await waitFor(() => {
        expect(screen.getByText('EU-EN-2024-056')).toBeInTheDocument();
      });

      const evaluateButton = screen.getByRole('button', { name: /evaluate/i });
      fireEvent.click(evaluateButton);

      await waitFor(() => {
        expect(screen.getByText(/Evaluation failed/)).toBeInTheDocument();
      });
    });
  });

  describe('Real-time Updates', () => {
    it('handles WebSocket processing updates', async () => {
      let processingCallback: (data: any) => void;
      
      mockWebSocketService.onProcessingUpdate.mockImplementation((callback) => {
        processingCallback = callback;
      });

      mockApiService.uploadDocument.mockResolvedValue({
        document_id: 'test-doc-123',
        processing_status: 'pending',
        extracted_data: null,
        confidence_score: 0,
        processing_time: 0,
        evaluation_metrics: null
      });

      renderWithRouter(<App />);

      const uploadLink = screen.getByText(/Upload Document/);
      fireEvent.click(uploadLink);

      const fileInput = screen.getByLabelText(/select file/i);
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(mockWebSocketService.connect).toHaveBeenCalled();
      });

      // Simulate processing updates
      if (processingCallback) {
        processingCallback({
          document_id: 'test-doc-123',
          processing_status: 'processing',
          progress: 25
        });

        await waitFor(() => {
          expect(screen.getByText(/Processing: 25%/)).toBeInTheDocument();
        });

        processingCallback({
          document_id: 'test-doc-123',
          processing_status: 'processing',
          progress: 75
        });

        await waitFor(() => {
          expect(screen.getByText(/Processing: 75%/)).toBeInTheDocument();
        });

        processingCallback({
          document_id: 'test-doc-123',
          processing_status: 'completed',
          progress: 100
        });

        await waitFor(() => {
          expect(screen.getByText(/Completed/)).toBeInTheDocument();
        });
      }
    });

    it('handles WebSocket connection errors', async () => {
      mockWebSocketService.connect.mockImplementation(() => {
        throw new Error('WebSocket connection failed');
      });

      mockApiService.uploadDocument.mockResolvedValue({
        document_id: 'test-doc-123',
        processing_status: 'pending',
        extracted_data: null,
        confidence_score: 0,
        processing_time: 0,
        evaluation_metrics: null
      });

      renderWithRouter(<App />);

      const uploadLink = screen.getByText(/Upload Document/);
      fireEvent.click(uploadLink);

      const fileInput = screen.getByLabelText(/select file/i);
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText(/WebSocket connection failed/)).toBeInTheDocument();
        expect(screen.getByText(/Real-time updates unavailable/)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('handles network errors gracefully', async () => {
      mockApiService.uploadDocument.mockRejectedValue(new Error('Network error'));

      renderWithRouter(<App />);

      const uploadLink = screen.getByText(/Upload Document/);
      fireEvent.click(uploadLink);

      const fileInput = screen.getByLabelText(/select file/i);
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText(/Network error/)).toBeInTheDocument();
        expect(screen.getByText(/Please check your connection/)).toBeInTheDocument();
      });
    });

    it('handles server errors with retry options', async () => {
      mockApiService.uploadDocument.mockRejectedValue(new Error('Server error: 500'));

      renderWithRouter(<App />);

      const uploadLink = screen.getByText(/Upload Document/);
      fireEvent.click(uploadLink);

      const fileInput = screen.getByLabelText(/select file/i);
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });

      const uploadButton = screen.getByRole('button', { name: /upload/i });
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(screen.getByText(/Server error: 500/)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });
    });
  });

  describe('Data Persistence', () => {
    it('persists results across page navigation', async () => {
      mockApiService.getExtractionResults.mockResolvedValue({
        document_id: 'test-doc-123',
        processing_status: 'completed',
        extracted_data: {
          tender_reference: 'EU-EN-2024-056',
          publication_date: '2024-06-14'
        },
        confidence_score: 0.95,
        processing_time: 2.5,
        evaluation_metrics: null
      });

      renderWithRouter(<App />);

      // Navigate to results
      const resultsLink = screen.getByText(/View Results/);
      fireEvent.click(resultsLink);

      await waitFor(() => {
        expect(screen.getByText('EU-EN-2024-056')).toBeInTheDocument();
      });

      // Navigate away and back
      const uploadLink = screen.getByText(/Upload Document/);
      fireEvent.click(uploadLink);

      const resultsLink2 = screen.getByText(/View Results/);
      fireEvent.click(resultsLink2);

      // Results should still be there
      await waitFor(() => {
        expect(screen.getByText('EU-EN-2024-056')).toBeInTheDocument();
      });
    });
  });
});
