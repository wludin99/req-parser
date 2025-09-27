/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import EvaluationMetrics from '../../src/components/EvaluationMetrics';

describe('EvaluationMetrics Component', () => {
  const mockEvaluationData = {
    document_id: 'test-doc-123',
    overall_accuracy: 0.85,
    field_accuracy: {
      tender_reference: 1.0,
      publication_date: 1.0,
      contracting_authority: 0.8,
      subject: 0.9,
      description: 0.7,
      estimated_budget_eur: 1.0,
      eligibility_requirements: 0.67,
      tender_deadline: 1.0,
      contact: 0.6
    },
    completeness: 0.89,
    discrepancies: [
      {
        field: 'contracting_authority.name',
        extracted_value: 'Ministry of Energy',
        ground_truth_value: 'Ministry of Energy Transition',
        similarity_score: 0.8
      },
      {
        field: 'contact.email',
        extracted_value: 'marie.dubois@example.com',
        ground_truth_value: 'marie.dubois@transition.gouv.fr',
        similarity_score: 0.6
      }
    ],
    evaluation_timestamp: '2024-09-27T21:00:00Z'
  };

  const mockOnClose = jest.fn();
  const mockOnRetry = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders overall accuracy score', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Overall Accuracy: 85%/)).toBeInTheDocument();
  });

  it('renders completeness score', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Completeness: 89%/)).toBeInTheDocument();
  });

  it('displays field accuracy breakdown', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Field Accuracy/)).toBeInTheDocument();
    expect(screen.getByText(/Tender Reference: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/Contracting Authority: 80%/)).toBeInTheDocument();
    expect(screen.getByText(/Subject: 90%/)).toBeInTheDocument();
    expect(screen.getByText(/Description: 70%/)).toBeInTheDocument();
    expect(screen.getByText(/Estimated Budget: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/Eligibility Requirements: 67%/)).toBeInTheDocument();
    expect(screen.getByText(/Tender Deadline: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/Contact: 60%/)).toBeInTheDocument();
  });

  it('shows discrepancies when present', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Discrepancies/)).toBeInTheDocument();
    expect(screen.getByText(/Ministry of Energy/)).toBeInTheDocument();
    expect(screen.getByText(/Ministry of Energy Transition/)).toBeInTheDocument();
    expect(screen.getByText(/marie\.dubois@example\.com/)).toBeInTheDocument();
    expect(screen.getByText(/marie\.dubois@transition\.gouv\.fr/)).toBeInTheDocument();
  });

  it('displays evaluation timestamp', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Evaluated at: 2024-09-27 21:00:00/)).toBeInTheDocument();
  });

  it('handles perfect evaluation (no discrepancies)', () => {
    const perfectEvaluation = {
      ...mockEvaluationData,
      overall_accuracy: 1.0,
      field_accuracy: {
        tender_reference: 1.0,
        publication_date: 1.0,
        contracting_authority: 1.0,
        subject: 1.0,
        description: 1.0,
        estimated_budget_eur: 1.0,
        eligibility_requirements: 1.0,
        tender_deadline: 1.0,
        contact: 1.0
      },
      completeness: 1.0,
      discrepancies: []
    };

    render(
      <EvaluationMetrics
        evaluationData={perfectEvaluation}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Overall Accuracy: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/Completeness: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/Perfect match!/)).toBeInTheDocument();
    expect(screen.queryByText(/Discrepancies/)).not.toBeInTheDocument();
  });

  it('handles poor evaluation with low scores', () => {
    const poorEvaluation = {
      ...mockEvaluationData,
      overall_accuracy: 0.3,
      field_accuracy: {
        tender_reference: 0.5,
        publication_date: 0.2,
        contracting_authority: 0.1,
        subject: 0.4,
        description: 0.3,
        estimated_budget_eur: 0.0,
        eligibility_requirements: 0.2,
        tender_deadline: 0.1,
        contact: 0.0
      },
      completeness: 0.4,
      discrepancies: [
        {
          field: 'estimated_budget_eur',
          extracted_value: '0',
          ground_truth_value: '2500000',
          similarity_score: 0.0
        }
      ]
    };

    render(
      <EvaluationMetrics
        evaluationData={poorEvaluation}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Overall Accuracy: 30%/)).toBeInTheDocument();
    expect(screen.getByText(/Completeness: 40%/)).toBeInTheDocument();
    expect(screen.getByText(/Needs improvement/)).toBeInTheDocument();
  });

  it('handles close button click', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('handles retry button click', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    const retryButton = screen.getByRole('button', { name: /retry/i });
    fireEvent.click(retryButton);

    expect(mockOnRetry).toHaveBeenCalled();
  });

  it('shows accuracy color coding', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    // High accuracy fields should be green
    const highAccuracyFields = screen.getAllByText(/100%/);
    highAccuracyFields.forEach(field => {
      expect(field).toHaveClass('text-green-600');
    });

    // Low accuracy fields should be red
    const lowAccuracyFields = screen.getAllByText(/60%/);
    lowAccuracyFields.forEach(field => {
      expect(field).toHaveClass('text-red-600');
    });
  });

  it('displays progress bars for field accuracy', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    const progressBars = screen.getAllByRole('progressbar');
    expect(progressBars).toHaveLength(9); // One for each field

    // Check that progress bars have correct values
    const tenderRefBar = screen.getByLabelText(/Tender Reference/);
    expect(tenderRefBar).toHaveAttribute('aria-valuenow', '100');

    const contactBar = screen.getByLabelText(/Contact/);
    expect(contactBar).toHaveAttribute('aria-valuenow', '60');
  });

  it('handles missing field accuracy data', () => {
    const incompleteEvaluation = {
      ...mockEvaluationData,
      field_accuracy: {
        tender_reference: 1.0,
        publication_date: 1.0
        // Missing other fields
      }
    };

    render(
      <EvaluationMetrics
        evaluationData={incompleteEvaluation}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Tender Reference: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/Publication Date: 100%/)).toBeInTheDocument();
    expect(screen.getByText(/No data available/)).toBeInTheDocument();
  });

  it('formats similarity scores correctly', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Similarity: 80%/)).toBeInTheDocument();
    expect(screen.getByText(/Similarity: 60%/)).toBeInTheDocument();
  });

  it('shows summary statistics', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Summary/)).toBeInTheDocument();
    expect(screen.getByText(/Fields with 100% accuracy: 4/)).toBeInTheDocument();
    expect(screen.getByText(/Fields needing improvement: 5/)).toBeInTheDocument();
    expect(screen.getByText(/Total discrepancies: 2/)).toBeInTheDocument();
  });

  it('handles expandable discrepancy details', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    const expandButton = screen.getByText(/Show details/);
    fireEvent.click(expandButton);

    expect(screen.getByText(/Field: contracting_authority\.name/)).toBeInTheDocument();
    expect(screen.getByText(/Field: contact\.email/)).toBeInTheDocument();

    const collapseButton = screen.getByText(/Hide details/);
    fireEvent.click(collapseButton);

    expect(screen.queryByText(/Field: contracting_authority\.name/)).not.toBeInTheDocument();
  });

  it('displays evaluation recommendations', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Recommendations/)).toBeInTheDocument();
    expect(screen.getByText(/Focus on improving contact information extraction/)).toBeInTheDocument();
    expect(screen.getByText(/Review description parsing accuracy/)).toBeInTheDocument();
  });

  it('handles different evaluation statuses', () => {
    const pendingEvaluation = {
      ...mockEvaluationData,
      status: 'pending'
    };

    render(
      <EvaluationMetrics
        evaluationData={pendingEvaluation}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Evaluation pending/)).toBeInTheDocument();
  });

  it('shows export options', () => {
    render(
      <EvaluationMetrics
        evaluationData={mockEvaluationData}
        onClose={mockOnClose}
        onRetry={mockOnRetry}
      />
    );

    expect(screen.getByText(/Export Results/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Export CSV/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Export JSON/ })).toBeInTheDocument();
  });
});
