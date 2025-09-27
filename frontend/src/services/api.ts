import { io, Socket } from 'socket.io-client';

export interface TenderData {
  tender_reference: string;
  publication_date: string;
  contracting_authority: {
    name: string;
    address: string;
  };
  subject: string;
  description: string;
  estimated_budget_eur: number;
  eligibility_requirements: string[];
  tender_deadline: string;
  contact: {
    name: string;
    email: string;
  };
}

export interface GroundTruthData {
  tender_reference: string;
  publication_date: string;
  contracting_authority: {
    name: string;
    address: string;
  };
  subject: string;
  description: string;
  estimated_budget_eur: number;
  eligibility_requirements: string[];
  tender_deadline: string;
  contact: {
    name: string;
    email: string;
  };
}

export interface ExtractionResponse {
  document_id: string;
  processing_status: string;
  extracted_data: TenderData;
  confidence_score: number;
  processing_time: number;
  evaluation_metrics?: EvaluationMetrics;
}

export interface EvaluationMetrics {
  overall_accuracy: number;
  field_accuracy: {
    [key: string]: number;
  };
  completeness: number;
  discrepancies: Array<{
    field: string;
    extracted_value: any;
    ground_truth_value: any;
    similarity: number;
  }>;
  evaluation_timestamp: string;
}

export interface EvaluationResponse {
  document_id: string;
  evaluation_status: string;
  evaluation_metrics: EvaluationMetrics;
  processing_time: number;
}

class ApiService {
  private baseUrl: string;
  private socket: Socket | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  /**
   * Extract structured data from a document
   */
  async extractDocument(
    file: File, 
    groundTruth?: GroundTruthData,
    onProgress?: (progress: string) => void
  ): Promise<ExtractionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (groundTruth) {
      formData.append('ground_truth', JSON.stringify(groundTruth));
    }

    try {
      const response = await fetch(`${this.baseUrl}/extract`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Connect to WebSocket for real-time updates if processing is in progress
      if (result.processing_status === 'processing' && onProgress) {
        this.connectWebSocket(result.document_id, onProgress);
      }

      return result;
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Extraction failed:', error);
      throw error;
    }
  }

  /**
   * Evaluate extracted data against ground truth
   */
  async evaluateExtraction(
    documentId: string,
    extractedData: TenderData,
    groundTruth: GroundTruthData
  ): Promise<EvaluationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/evaluate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          extracted_data: extractedData,
          ground_truth: groundTruth,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Evaluation failed:', error);
      throw error;
    }
  }

  /**
   * Connect to WebSocket for real-time processing updates
   */
  private connectWebSocket(documentId: string, onProgress: (progress: string) => void): void {
    if (this.socket) {
      this.socket.disconnect();
    }

    this.socket = io(this.baseUrl, {
      transports: ['websocket', 'polling']
    });

    this.socket.on('connect', () => {
      // eslint-disable-next-line no-console
      console.log('WebSocket connected');
      this.socket?.emit('join_document', { document_id: documentId });
    });

    this.socket.on('processing_update', (data: { progress: string; status: string }) => {
      // eslint-disable-next-line no-console
      console.log('Processing update:', data);
      onProgress(data.progress);
    });

    this.socket.on('processing_complete', (data: { document_id: string; result: any }) => {
      // eslint-disable-next-line no-console
      console.log('Processing complete:', data);
      this.socket?.disconnect();
    });

    this.socket.on('processing_error', (data: { document_id: string; error: string }) => {
      // eslint-disable-next-line no-console
      console.error('Processing error:', data);
      onProgress(`Error: ${data.error}`);
      this.socket?.disconnect();
    });

    this.socket.on('disconnect', () => {
      // eslint-disable-next-line no-console
      console.log('WebSocket disconnected');
    });
  }

  /**
   * Disconnect WebSocket
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  /**
   * Get processing status for a document
   */
  async getProcessingStatus(documentId: string): Promise<{ status: string; progress?: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/status/${documentId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get processing status:', error);
      throw error;
    }
  }

  /**
   * Validate file before upload
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'text/plain'];
    const allowedExtensions = ['.pdf', '.txt'];

    if (file.size > maxSize) {
      return { valid: false, error: 'File size must be less than 10MB' };
    }

    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'File must be a PDF or text file' };
    }

    const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedExtensions.includes(extension)) {
      return { valid: false, error: 'File must have .pdf or .txt extension' };
    }

    return { valid: true };
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Format currency for display
   */
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-EU', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  /**
   * Format date for display
   */
  formatDate(dateString: string): string {
    try {
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
