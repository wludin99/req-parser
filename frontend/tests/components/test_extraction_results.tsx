/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ExtractionResults from '../../src/components/ExtractionResults';

// Mock the API service
jest.mock('../../src/services/api', () => ({
  getExtractionResults: jest.fn(),
  evaluateResults: jest.fn(),
}));

describe('ExtractionResults Component', () => {
  const mockExtractedData = {
    document_id: 'test-doc-123',
    processing_status: 'completed',
    extracted_data: {
      tender_reference: 'EU-EN-2024-056',
      publication_date: '2024-06-14',
      contracting_authority: {
        name: 'Ministry of Energy Transition',
        address: '12 Rue de Rivoli, 75001 Paris, France'
      },
      subject: 'Supply and installation of solar photovoltaic systems for public schools in the Île-de-France region.',
      description: 'The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems with a minimum installed capacity of 500 kW across 10 schools. The contractor is also responsible for maintenance for 5 years.',
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
  };

  const mockOnEvaluate = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders extraction results with all fields', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    // Check for main tender information
    expect(screen.getByText('EU-EN-2024-056')).toBeInTheDocument();
    expect(screen.getByText('2024-06-14')).toBeInTheDocument();
    expect(screen.getByText('Ministry of Energy Transition')).toBeInTheDocument();
    expect(screen.getByText('Supply and installation of solar photovoltaic systems')).toBeInTheDocument();
    expect(screen.getByText('€2,500,000')).toBeInTheDocument();
    expect(screen.getByText('2024-07-30 17:00 CET')).toBeInTheDocument();
    expect(screen.getByText('Marie Dubois')).toBeInTheDocument();
    expect(screen.getByText('marie.dubois@transition.gouv.fr')).toBeInTheDocument();
  });

  it('displays confidence score and processing time', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/95%/)).toBeInTheDocument();
    expect(screen.getByText(/2\.5s/)).toBeInTheDocument();
  });

  it('shows evaluation metrics when available', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/Accuracy: 95%/)).toBeInTheDocument();
    expect(screen.getByText(/Completeness: 100%/)).toBeInTheDocument();
  });

  it('renders eligibility requirements as a list', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    const requirements = screen.getAllByText(/At least 3 prior contracts/);
    expect(requirements).toHaveLength(1);
    
    expect(screen.getByText(/Certification in ISO 14001/)).toBeInTheDocument();
    expect(screen.getByText(/Proof of financial capacity/)).toBeInTheDocument();
  });

  it('handles missing or null data gracefully', () => {
    const incompleteData = {
      ...mockExtractedData,
      extracted_data: {
        tender_reference: 'EU-EN-2024-056',
        publication_date: '2024-06-14',
        // Missing other fields
      }
    };

    render(
      <ExtractionResults
        results={incompleteData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('EU-EN-2024-056')).toBeInTheDocument();
    expect(screen.getByText('2024-06-14')).toBeInTheDocument();
    expect(screen.getByText(/No data available/)).toBeInTheDocument();
  });

  it('shows processing status', () => {
    const processingData = {
      ...mockExtractedData,
      processing_status: 'processing'
    };

    render(
      <ExtractionResults
        results={processingData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/Processing/)).toBeInTheDocument();
  });

  it('shows error status', () => {
    const errorData = {
      ...mockExtractedData,
      processing_status: 'failed',
      error_message: 'Processing failed'
    };

    render(
      <ExtractionResults
        results={errorData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/Failed/)).toBeInTheDocument();
    expect(screen.getByText('Processing failed')).toBeInTheDocument();
  });

  it('handles evaluate button click', async () => {
    const { evaluateResults } = require('../../src/services/api');
    evaluateResults.mockResolvedValue({
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

    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    const evaluateButton = screen.getByRole('button', { name: /evaluate/i });
    fireEvent.click(evaluateButton);

    await waitFor(() => {
      expect(evaluateResults).toHaveBeenCalledWith('test-doc-123');
      expect(mockOnEvaluate).toHaveBeenCalled();
    });
  });

  it('handles evaluation error', async () => {
    const { evaluateResults } = require('../../src/services/api');
    evaluateResults.mockRejectedValue(new Error('Evaluation failed'));

    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    const evaluateButton = screen.getByRole('button', { name: /evaluate/i });
    fireEvent.click(evaluateButton);

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Evaluation failed');
    });
  });

  it('displays field accuracy breakdown', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
        showFieldAccuracy={true}
      />
    );

    expect(screen.getByText(/Field Accuracy/)).toBeInTheDocument();
    expect(screen.getByText(/Tender Reference: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/Contracting Authority: 90%/)).toBeInTheDocument();
  });

  it('formats currency correctly', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('€2,500,000')).toBeInTheDocument();
  });

  it('formats dates correctly', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('2024-06-14')).toBeInTheDocument();
    expect(screen.getByText('2024-07-30 17:00 CET')).toBeInTheDocument();
  });

  it('shows loading state during evaluation', async () => {
    const { evaluateResults } = require('../../src/services/api');
    evaluateResults.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    const evaluateButton = screen.getByRole('button', { name: /evaluate/i });
    fireEvent.click(evaluateButton);

    expect(screen.getByText(/Evaluating/)).toBeInTheDocument();
    expect(evaluateButton).toBeDisabled();

    await waitFor(() => {
      expect(mockOnEvaluate).toHaveBeenCalled();
    });
  });

  it('handles different confidence score ranges', () => {
    const lowConfidenceData = {
      ...mockExtractedData,
      confidence_score: 0.3
    };

    render(
      <ExtractionResults
        results={lowConfidenceData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/30%/)).toBeInTheDocument();
    expect(screen.getByText(/Low confidence/)).toBeInTheDocument();
  });

  it('shows high confidence indicator', () => {
    const highConfidenceData = {
      ...mockExtractedData,
      confidence_score: 0.98
    };

    render(
      <ExtractionResults
        results={highConfidenceData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/98%/)).toBeInTheDocument();
    expect(screen.getByText(/High confidence/)).toBeInTheDocument();
  });

  it('handles empty eligibility requirements', () => {
    const noRequirementsData = {
      ...mockExtractedData,
      extracted_data: {
        ...mockExtractedData.extracted_data,
        eligibility_requirements: []
      }
    };

    render(
      <ExtractionResults
        results={noRequirementsData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/No requirements specified/)).toBeInTheDocument();
  });

  it('displays contact information with proper formatting', () => {
    render(
      <ExtractionResults
        results={mockExtractedData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Marie Dubois')).toBeInTheDocument();
    expect(screen.getByText('marie.dubois@transition.gouv.fr')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'marie.dubois@transition.gouv.fr' })).toHaveAttribute('href', 'mailto:marie.dubois@transition.gouv.fr');
  });

  it('handles long descriptions with truncation', () => {
    const longDescriptionData = {
      ...mockExtractedData,
      extracted_data: {
        ...mockExtractedData.extracted_data,
        description: 'A'.repeat(500) // Very long description
      }
    };

    render(
      <ExtractionResults
        results={longDescriptionData}
        onEvaluate={mockOnEvaluate}
        onError={mockOnError}
      />
    );

    expect(screen.getByText(/Show more/)).toBeInTheDocument();
    
    const showMoreButton = screen.getByText(/Show more/);
    fireEvent.click(showMoreButton);
    
    expect(screen.getByText(/Show less/)).toBeInTheDocument();
  });
});
