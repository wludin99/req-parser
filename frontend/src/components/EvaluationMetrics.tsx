import React from 'react';

interface EvaluationMetricsData {
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

interface EvaluationMetricsProps {
  metrics: EvaluationMetricsData | null;
  isEvaluating: boolean;
  error?: string;
}

const EvaluationMetrics: React.FC<EvaluationMetricsProps> = ({
  metrics,
  isEvaluating,
  error
}) => {
  if (isEvaluating) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Evaluating Results</h2>
          <p className="text-gray-600">Comparing extracted data against ground truth...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <div className="text-red-500 text-2xl">⚠️</div>
            <div>
              <h3 className="text-lg font-semibold text-red-800">Evaluation Failed</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return null;
  }

  const getAccuracyColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getAccuracyBgColor = (score: number) => {
    if (score >= 0.9) return 'bg-green-100';
    if (score >= 0.7) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const formatFieldName = (fieldName: string) => {
    return fieldName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const fieldAccuracyEntries = Object.entries(metrics.field_accuracy);

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Evaluation Metrics</h2>
        <p className="text-gray-600">
          Performance analysis comparing extracted data against ground truth
        </p>
      </div>

      {/* Overall Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
          <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${getAccuracyBgColor(metrics.overall_accuracy)} mb-4`}>
            <span className={`text-2xl font-bold ${getAccuracyColor(metrics.overall_accuracy)}`}>
              {Math.round(metrics.overall_accuracy * 100)}%
            </span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Overall Accuracy</h3>
          <p className="text-sm text-gray-600">
            {metrics.overall_accuracy >= 0.9 ? 'Excellent' : 
             metrics.overall_accuracy >= 0.7 ? 'Good' : 'Needs Improvement'}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
          <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full ${getAccuracyBgColor(metrics.completeness)} mb-4`}>
            <span className={`text-2xl font-bold ${getAccuracyColor(metrics.completeness)}`}>
              {Math.round(metrics.completeness * 100)}%
            </span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Completeness</h3>
          <p className="text-sm text-gray-600">
            {metrics.completeness >= 0.9 ? 'Complete' : 
             metrics.completeness >= 0.7 ? 'Mostly Complete' : 'Incomplete'}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
            <span className="text-2xl font-bold text-blue-600">
              {metrics.discrepancies.length}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Discrepancies</h3>
          <p className="text-sm text-gray-600">
            {metrics.discrepancies.length === 0 ? 'Perfect Match' : 
             metrics.discrepancies.length <= 3 ? 'Minor Issues' : 'Multiple Issues'}
          </p>
        </div>
      </div>

      {/* Field-by-Field Accuracy */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Field-by-Field Accuracy</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {fieldAccuracyEntries.map(([field, accuracy]) => {
            const accuracyValue = typeof accuracy === 'number' ? accuracy : 0;
            return (
              <div key={field} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-900">
                  {formatFieldName(field)}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getAccuracyBgColor(accuracyValue)}`}
                      style={{ width: `${accuracyValue * 100}%` }}
                    ></div>
                  </div>
                  <span className={`font-medium ${getAccuracyColor(accuracyValue)}`}>
                    {Math.round(accuracyValue * 100)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Discrepancies */}
      {metrics.discrepancies.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Discrepancies Found</h3>
          <div className="space-y-4">
            {metrics.discrepancies.map((discrepancy: any, index: number) => (
              <div key={index} className="border border-yellow-200 bg-yellow-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">
                    {formatFieldName(discrepancy.field)}
                  </h4>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    discrepancy.similarity >= 0.8 ? 'bg-green-100 text-green-800' :
                    discrepancy.similarity >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {Math.round(discrepancy.similarity * 100)}% similar
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Extracted Value</label>
                    <p className="text-gray-900 text-sm bg-white p-2 rounded border">
                      {typeof discrepancy.extracted_value === 'object' 
                        ? JSON.stringify(discrepancy.extracted_value, null, 2)
                        : String(discrepancy.extracted_value)
                      }
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Ground Truth</label>
                    <p className="text-gray-900 text-sm bg-white p-2 rounded border">
                      {typeof discrepancy.ground_truth_value === 'object' 
                        ? JSON.stringify(discrepancy.ground_truth_value, null, 2)
                        : String(discrepancy.ground_truth_value)
                      }
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evaluation Timestamp */}
      <div className="mt-6 text-center text-sm text-gray-500">
        Evaluation completed at {new Date(metrics.evaluation_timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default EvaluationMetrics;
