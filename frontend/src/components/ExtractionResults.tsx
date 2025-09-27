import React from 'react';

interface TenderData {
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

interface ExtractionResultsProps {
  extractedData: TenderData | null;
  confidenceScore: number;
  processingTime: number;
  isProcessing: boolean;
  error?: string;
}

const ExtractionResults: React.FC<ExtractionResultsProps> = ({
  extractedData,
  confidenceScore,
  processingTime,
  isProcessing,
  error
}) => {
  if (isProcessing) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Processing Document</h2>
          <p className="text-gray-600">Extracting structured data from your document...</p>
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
              <h3 className="text-lg font-semibold text-red-800">Extraction Failed</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!extractedData) {
    return null;
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-EU', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Extraction Results</h2>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <span>Confidence:</span>
            <span className={`font-medium ${
              confidenceScore >= 0.8 ? 'text-green-600' : 
              confidenceScore >= 0.6 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {Math.round(confidenceScore * 100)}%
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <span>Processing time:</span>
            <span className="font-medium">{processingTime.toFixed(2)}s</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Basic Information</h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Tender Reference</label>
                <p className="text-gray-900 font-mono">{extractedData.tender_reference}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Publication Date</label>
                <p className="text-gray-900">{formatDate(extractedData.publication_date)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Subject</label>
                <p className="text-gray-900">{extractedData.subject}</p>
              </div>
            </div>
          </div>

          {/* Contracting Authority */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Contracting Authority</h3>
            <div className="space-y-2">
              <div>
                <label className="text-sm font-medium text-gray-500">Name</label>
                <p className="text-gray-900">{extractedData.contracting_authority.name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Address</label>
                <p className="text-gray-900 text-sm">{extractedData.contracting_authority.address}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Financial & Requirements */}
        <div className="space-y-4">
          {/* Financial Information */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Financial Information</h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-500">Estimated Budget</label>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(extractedData.estimated_budget_eur)}
                </p>
              </div>
            </div>
          </div>

          {/* Eligibility Requirements */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Eligibility Requirements</h3>
            <ul className="space-y-2">
              {extractedData.eligibility_requirements.map((requirement, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span className="text-gray-900 text-sm">{requirement}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Timeline */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Timeline</h3>
            <div className="space-y-2">
              <div>
                <label className="text-sm font-medium text-gray-500">Tender Deadline</label>
                <p className="text-gray-900 font-medium">{extractedData.tender_deadline}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="mt-6 bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
        <p className="text-gray-900 leading-relaxed">{extractedData.description}</p>
      </div>

      {/* Contact Information */}
      <div className="mt-6 bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Contact Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Contact Person</label>
            <p className="text-gray-900">{extractedData.contact.name}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Email</label>
            <a 
              href={`mailto:${extractedData.contact.email}`}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {extractedData.contact.email}
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtractionResults;
