import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ExtractionResults from '../components/ExtractionResults';
import EvaluationMetrics from '../components/EvaluationMetrics';
import { ExtractionResponse, EvaluationMetrics as EvaluationMetricsType } from '../services/api';

const Results: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const [extractionResult, setExtractionResult] = useState<ExtractionResponse | null>(null);
  const [evaluationMetrics, setEvaluationMetrics] = useState<EvaluationMetricsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (documentId) {
      loadResults(documentId);
    }
  }, [documentId]);

  const loadResults = async (docId: string) => {
    try {
      setLoading(true);
      setError(null);

      // Try to get extraction results
      const response = await fetch(`/api/results/${docId}`);
      if (response.ok) {
        const data = await response.json();
        setExtractionResult(data.extraction);
        setEvaluationMetrics(data.evaluation);
      } else {
        throw new Error('Results not found');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const handleNewUpload = () => {
    navigate('/');
  };

  const handleDownloadResults = () => {
    if (!extractionResult) return;

    const data = {
      document_id: extractionResult.document_id,
      extracted_data: extractionResult.extracted_data,
      confidence_score: extractionResult.confidence_score,
      processing_time: extractionResult.processing_time,
      evaluation_metrics: evaluationMetrics,
      timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tender-results-${extractionResult.document_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    if (!extractionResult) return;

    const data = extractionResult.extracted_data;
    const csvContent = [
      'Field,Value',
      `Tender Reference,"${data.tender_reference}"`,
      `Publication Date,"${data.publication_date}"`,
      `Contracting Authority Name,"${data.contracting_authority.name}"`,
      `Contracting Authority Address,"${data.contracting_authority.address}"`,
      `Subject,"${data.subject}"`,
      `Description,"${data.description}"`,
      `Estimated Budget (EUR),${data.estimated_budget_eur}`,
      `Eligibility Requirements,"${data.eligibility_requirements.join('; ')}"`,
      `Tender Deadline,"${data.tender_deadline}"`,
      `Contact Name,"${data.contact.name}"`,
      `Contact Email,"${data.contact.email}"`,
      `Confidence Score,${extractionResult.confidence_score}`,
      `Processing Time,${extractionResult.processing_time}`
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tender-results-${extractionResult.document_id}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Results</h2>
          <p className="text-gray-600">Please wait while we load your extraction results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Results</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={handleNewUpload}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Start New Upload
          </button>
        </div>
      </div>
    );
  }

  if (!extractionResult) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="text-gray-400 text-6xl mb-4">📄</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Results Found</h2>
          <p className="text-gray-600 mb-6">The requested results could not be found.</p>
          <button
            onClick={handleNewUpload}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Start New Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Extraction Results</h1>
              <p className="text-gray-600 mt-1">Document ID: {extractionResult.document_id}</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleDownloadResults}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Download JSON
              </button>
              <button
                onClick={handleExportCSV}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Export CSV
              </button>
              <button
                onClick={handleNewUpload}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                New Upload
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Extraction Results */}
          <div className="bg-white rounded-lg shadow">
            <ExtractionResults
              extractedData={extractionResult.extracted_data}
              confidenceScore={extractionResult.confidence_score}
              processingTime={extractionResult.processing_time}
              isProcessing={false}
            />
          </div>

          {/* Evaluation Metrics */}
          {evaluationMetrics && (
            <div className="bg-white rounded-lg shadow">
              <EvaluationMetrics
                metrics={evaluationMetrics}
                isEvaluating={false}
              />
            </div>
          )}

          {/* Summary Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(extractionResult.confidence_score * 100)}%
                </div>
                <div className="text-sm text-gray-500">Confidence Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {extractionResult.processing_time.toFixed(2)}s
                </div>
                <div className="text-sm text-gray-500">Processing Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {evaluationMetrics ? Math.round(evaluationMetrics.overall_accuracy * 100) : 'N/A'}%
                </div>
                <div className="text-sm text-gray-500">Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-gray-500 text-sm">
            <p>TenderInsight - AI-Powered Government Tender Data Extraction</p>
            <p className="mt-1">Powered by DeepSeek, OpenAI, and Hugging Face</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Results;
