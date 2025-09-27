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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-lg border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">T</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                  TenderInsight
                </h1>
                <p className="text-gray-600 mt-1 font-medium">AI-Powered Government Tender Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleReset}
                className="px-6 py-2.5 text-sm font-semibold text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-300/50 rounded-xl hover:bg-white hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
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
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 hover:shadow-2xl transition-all duration-300">
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
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8 hover:shadow-2xl transition-all duration-300">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold">📊</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900">
                  Optional: Upload Ground Truth Data
                </h3>
              </div>
              <p className="text-gray-600 mb-6 text-lg">
                Upload a JSON file with ground truth data to evaluate extraction accuracy
              </p>
              <div className="flex items-center space-x-4">
                <input
                  type="file"
                  accept=".json"
                  onChange={handleGroundTruthUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-blue-50 file:to-indigo-50 file:text-blue-700 hover:file:from-blue-100 hover:file:to-indigo-100 transition-all duration-200"
                />
                {groundTruth && (
                  <span className="text-sm text-green-600 font-semibold flex items-center space-x-2">
                    <span className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-xs">✓</span>
                    </span>
                    <span>Ground truth loaded</span>
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Processing Progress */}
          {isProcessing && processingProgress && (
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <div className="animate-spin rounded-full h-8 w-8 border-3 border-blue-600 border-t-transparent"></div>
                  <div className="absolute inset-0 rounded-full border-3 border-blue-200"></div>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Processing Document</h3>
                  <p className="text-gray-600 text-lg">{processingProgress}</p>
                  <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Extraction Results */}
          {extractionResult && (
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 hover:shadow-2xl transition-all duration-300">
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
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 hover:shadow-2xl transition-all duration-300">
              <EvaluationMetrics
                metrics={evaluationMetrics}
                isEvaluating={isEvaluating}
                error={error || undefined}
              />
            </div>
          )}

          {/* Error Display */}
          {error && !isProcessing && (
            <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200/50 rounded-2xl shadow-xl p-8">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <span className="text-white text-xl">⚠️</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-red-800 mb-2">Error</h3>
                  <p className="text-red-700 text-lg">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-sm border-t border-gray-200/50 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                TenderInsight
              </span>
            </div>
            <p className="text-gray-600 text-lg font-medium mb-2">AI-Powered Government Tender Data Extraction</p>
            <p className="text-gray-500 text-sm">Powered by DeepSeek, OpenAI, and Hugging Face</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
