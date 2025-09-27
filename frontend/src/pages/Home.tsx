import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import ExtractionResults from '../components/ExtractionResults';
import EvaluationMetrics from '../components/EvaluationMetrics';
import { apiService, TenderData, GroundTruthData, ExtractionResponse, EvaluationMetrics as EvaluationMetricsType } from '../services/api';

const Home: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [groundTruth, setGroundTruth] = useState<GroundTruthData | null>(null);
  const [extractionResult, setExtractionResult] = useState<ExtractionResponse | null>(null);
  const [evaluationMetrics, setEvaluationMetrics] = useState<EvaluationMetricsType | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingProgress, setProcessingProgress] = useState<string>('');

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
    setExtractionResult(null);
    setEvaluationMetrics(null);
  };

  const handleProcessingStart = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);
    setExtractionResult(null);
    setEvaluationMetrics(null);
    setProcessingProgress('Starting document processing...');

    try {
      const result = await apiService.extractDocument(
        selectedFile,
        groundTruth || undefined,
        (progress) => {
          setProcessingProgress(progress);
        }
      );

      setExtractionResult(result);
      
      // If we have ground truth data, automatically evaluate
      if (groundTruth && result.extracted_data) {
        await handleEvaluation(result.extracted_data, groundTruth);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during processing');
    } finally {
      setIsProcessing(false);
      setProcessingProgress('');
    }
  };

  const handleEvaluation = async (extractedData: TenderData, groundTruthData: GroundTruthData) => {
    if (!extractionResult) return;

    setIsEvaluating(true);
    setError(null);

    try {
      const evaluationResult = await apiService.evaluateExtraction(
        extractionResult.document_id,
        extractedData,
        groundTruthData
      );

      setEvaluationMetrics(evaluationResult.evaluation_metrics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during evaluation');
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleGroundTruthUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        setGroundTruth(data);
        setError(null);
      } catch (err) {
        setError('Invalid JSON file for ground truth data');
      }
    };
    reader.readAsText(file);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setGroundTruth(null);
    setExtractionResult(null);
    setEvaluationMetrics(null);
    setError(null);
    setIsProcessing(false);
    setIsEvaluating(false);
    setProcessingProgress('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">TenderInsight</h1>
              <p className="text-gray-600 mt-1">Government Tender Data Extraction</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Upload Section */}
          {!extractionResult && (
            <div className="bg-white rounded-lg shadow">
              <DocumentUpload
                onFileSelect={handleFileSelect}
                onProcessingStart={handleProcessingStart}
                isProcessing={isProcessing}
                error={error || undefined}
              />
            </div>
          )}

          {/* Ground Truth Upload */}
          {!groundTruth && !isProcessing && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Optional: Upload Ground Truth Data
              </h3>
              <p className="text-gray-600 mb-4">
                Upload a JSON file with ground truth data to evaluate extraction accuracy
              </p>
              <div className="flex items-center space-x-4">
                <input
                  type="file"
                  accept=".json"
                  onChange={handleGroundTruthUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {groundTruth && (
                  <span className="text-sm text-green-600">✓ Ground truth loaded</span>
                )}
              </div>
            </div>
          )}

          {/* Processing Progress */}
          {isProcessing && processingProgress && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center space-x-3">
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent"></div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Processing Document</h3>
                  <p className="text-gray-600">{processingProgress}</p>
                </div>
              </div>
            </div>
          )}

          {/* Extraction Results */}
          {extractionResult && (
            <div className="bg-white rounded-lg shadow">
              <ExtractionResults
                extractedData={extractionResult.extracted_data}
                confidenceScore={extractionResult.confidence_score}
                processingTime={extractionResult.processing_time}
                isProcessing={false}
                error={error || undefined}
              />
            </div>
          )}

          {/* Evaluation Metrics */}
          {evaluationMetrics && (
            <div className="bg-white rounded-lg shadow">
              <EvaluationMetrics
                metrics={evaluationMetrics}
                isEvaluating={isEvaluating}
                error={error || undefined}
              />
            </div>
          )}

          {/* Error Display */}
          {error && !isProcessing && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-center space-x-3">
                <div className="text-red-500 text-2xl">⚠️</div>
                <div>
                  <h3 className="text-lg font-semibold text-red-800">Error</h3>
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}
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

export default Home;
