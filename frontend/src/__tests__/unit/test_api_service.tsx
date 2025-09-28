/**
 * Unit tests for API service.
 * 
 * Tests the API service functionality including HTTP requests and WebSocket connections.
 */
import { jest } from '@jest/globals';

// Mock fetch globally
global.fetch = jest.fn();

// Mock WebSocket
global.WebSocket = jest.fn();

// Import the API service
import * as apiService from '../../services/api';

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('extract', () => {
    it('should make POST request to /extract endpoint', async () => {
      const mockResponse = {
        document_id: 'doc-123',
        processing_status: 'completed',
        extracted_data: {
          tender_reference: 'EU-EN-2024-001',
          subject: 'Test Tender'
        }
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const result = await apiService.extract(file);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/extract',
        expect.objectContaining({
          method: 'POST',
          headers: expect.any(Object)
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle extraction errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      
      await expect(apiService.extract(file)).rejects.toThrow('HTTP error! status: 500');
    });

    it('should include ground truth when provided', async () => {
      const mockResponse = { document_id: 'doc-123' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const groundTruth = { tender_reference: 'EU-EN-2024-001' };
      
      await apiService.extract(file, groundTruth);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/extract',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      );
    });
  });

  describe('evaluate', () => {
    it('should make POST request to /evaluate endpoint', async () => {
      const mockResponse = {
        overall_accuracy: 0.95,
        field_accuracy: {
          tender_reference: 1.0,
          subject: 0.9
        }
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const documentId = 'doc-123';
      const extractedData = { tender_reference: 'EU-EN-2024-001' };
      const groundTruth = { tender_reference: 'EU-EN-2024-001' };

      const result = await apiService.evaluate(documentId, extractedData, groundTruth);

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/evaluate',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            document_id: documentId,
            extracted_data: extractedData,
            ground_truth: groundTruth
          })
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle evaluation errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request'
      });

      const documentId = 'doc-123';
      const extractedData = { tender_reference: 'EU-EN-2024-001' };
      const groundTruth = { tender_reference: 'EU-EN-2024-001' };

      await expect(apiService.evaluate(documentId, extractedData, groundTruth))
        .rejects.toThrow('HTTP error! status: 400');
    });
  });

  describe('getProcessingStatus', () => {
    it('should make GET request to /status endpoint', async () => {
      const mockResponse = {
        document_id: 'doc-123',
        processing_status: 'processing',
        progress_percentage: 50
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const documentId = 'doc-123';
      const result = await apiService.getProcessingStatus(documentId);

      expect(global.fetch).toHaveBeenCalledWith(
        `http://localhost:8000/status/${documentId}`,
        expect.objectContaining({
          method: 'GET'
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle status request errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      const documentId = 'doc-123';

      await expect(apiService.getProcessingStatus(documentId))
        .rejects.toThrow('HTTP error! status: 404');
    });
  });

  describe('WebSocket connection', () => {
    it('should connect to WebSocket', () => {
      const mockWebSocket = {
        readyState: WebSocket.CONNECTING,
        close: jest.fn(),
        send: jest.fn()
      };
      (global.WebSocket as jest.Mock).mockImplementation(() => mockWebSocket);

      const onMessage = jest.fn();
      const onError = jest.fn();
      const onClose = jest.fn();

      apiService.connectWebSocket(onMessage, onError, onClose);

      expect(global.WebSocket).toHaveBeenCalledWith('ws://localhost:8000/ws');
    });

    it('should handle WebSocket messages', () => {
      const mockWebSocket = {
        readyState: WebSocket.OPEN,
        close: jest.fn(),
        send: jest.fn(),
        addEventListener: jest.fn()
      };
      (global.WebSocket as jest.Mock).mockImplementation(() => mockWebSocket);

      const onMessage = jest.fn();
      const onError = jest.fn();
      const onClose = jest.fn();

      apiService.connectWebSocket(onMessage, onError, onClose);

      expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('message', expect.any(Function));
      expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('close', expect.any(Function));
    });

    it('should disconnect WebSocket', () => {
      const mockWebSocket = {
        readyState: WebSocket.OPEN,
        close: jest.fn(),
        send: jest.fn()
      };
      (global.WebSocket as jest.Mock).mockImplementation(() => mockWebSocket);

      apiService.connectWebSocket(jest.fn(), jest.fn(), jest.fn());
      apiService.disconnectWebSocket();

      expect(mockWebSocket.close).toHaveBeenCalled();
    });

    it('should send messages via WebSocket', () => {
      const mockWebSocket = {
        readyState: WebSocket.OPEN,
        close: jest.fn(),
        send: jest.fn()
      };
      (global.WebSocket as jest.Mock).mockImplementation(() => mockWebSocket);

      apiService.connectWebSocket(jest.fn(), jest.fn(), jest.fn());
      apiService.sendWebSocketMessage({ type: 'test', data: 'test data' });

      expect(mockWebSocket.send).toHaveBeenCalledWith(JSON.stringify({
        type: 'test',
        data: 'test data'
      }));
    });
  });

  describe('error handling', () => {
    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      
      await expect(apiService.extract(file)).rejects.toThrow('Network error');
    });

    it('should handle JSON parsing errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      
      await expect(apiService.extract(file)).rejects.toThrow('Invalid JSON');
    });
  });

  describe('API configuration', () => {
    it('should use correct base URL', () => {
      // This test ensures the API service is configured with the correct base URL
      // The actual base URL is hardcoded in the service, so we test the behavior
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      
      apiService.extract(file);
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8000'),
        expect.any(Object)
      );
    });

    it('should include proper headers', async () => {
      const mockResponse = { document_id: 'doc-123' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      await apiService.extract(file);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Accept': 'application/json'
          })
        })
      );
    });
  });
});
