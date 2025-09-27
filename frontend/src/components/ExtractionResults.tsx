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
      <div className="w-full max-w-4xl mx-auto p-8">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent mx-auto"></div>
            <div className="absolute inset-0 rounded-full border-4 border-blue-200 mx-auto"></div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Processing Document</h2>
          <p className="text-gray-600 text-lg">Extracting structured data from your document...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl mx-auto p-8">
        <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200/50 rounded-2xl shadow-xl p-8">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
              <span className="text-white text-xl">⚠️</span>
            </div>
            <div>
              <h3 className="text-xl font-bold text-red-800 mb-2">Extraction Failed</h3>
              <p className="text-red-700 text-lg">{error}</p>
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
    <div className="w-full max-w-4xl mx-auto p-8">
      <div className="mb-8">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-bold text-xl">✓</span>
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-700 bg-clip-text text-transparent">
            Extraction Results
          </h2>
        </div>
        <div className="flex items-center space-x-6 text-lg">
          <div className="flex items-center space-x-2">
            <span className="text-gray-600 font-medium">Confidence:</span>
            <span className={`font-bold text-xl ${
              confidenceScore >= 0.8 ? 'text-green-600' : 
              confidenceScore >= 0.6 ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {Math.round(confidenceScore * 100)}%
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-600 font-medium">Processing time:</span>
            <span className="font-bold text-xl text-blue-600">{processingTime.toFixed(2)}s</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Basic Information */}
        <div className="space-y-6">
          <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">📋</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Basic Information</h3>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Tender Reference</label>
                <p className="text-gray-900 font-mono text-lg bg-gray-50 p-2 rounded-lg">{extractedData.tender_reference}</p>
              </div>
              <div>
                <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Publication Date</label>
                <p className="text-gray-900 text-lg font-medium">{formatDate(extractedData.publication_date)}</p>
              </div>
              <div>
                <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Subject</label>
                <p className="text-gray-900 text-lg">{extractedData.subject}</p>
              </div>
            </div>
          </div>

          {/* Contracting Authority */}
          <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">🏛️</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Contracting Authority</h3>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Name</label>
                <p className="text-gray-900 text-lg font-medium">{extractedData.contracting_authority.name}</p>
              </div>
              <div>
                <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Address</label>
                <p className="text-gray-900 text-lg">{extractedData.contracting_authority.address}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Financial & Requirements */}
        <div className="space-y-6">
          {/* Financial Information */}
          <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">💰</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Financial Information</h3>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Estimated Budget</label>
                <p className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-700 bg-clip-text text-transparent">
                  {formatCurrency(extractedData.estimated_budget_eur)}
                </p>
              </div>
            </div>
          </div>

          {/* Eligibility Requirements */}
          <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">📋</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Eligibility Requirements</h3>
            </div>
            <ul className="space-y-3">
              {extractedData.eligibility_requirements.map((requirement, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mt-0.5">
                    <span className="text-white text-xs font-bold">{index + 1}</span>
                  </div>
                  <span className="text-gray-900 text-lg">{requirement}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Timeline */}
          <div className="bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all duration-300">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-red-500 to-pink-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">⏰</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Timeline</h3>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Tender Deadline</label>
                <p className="text-gray-900 text-xl font-bold">{extractedData.tender_deadline}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="mt-8 bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">📝</span>
          </div>
          <h3 className="text-xl font-bold text-gray-900">Description</h3>
        </div>
        <p className="text-gray-900 leading-relaxed text-lg">{extractedData.description}</p>
      </div>

      {/* Contact Information */}
      <div className="mt-8 bg-white/80 backdrop-blur-sm border border-gray-200/50 rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">📞</span>
          </div>
          <h3 className="text-xl font-bold text-gray-900">Contact Information</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Contact Person</label>
            <p className="text-gray-900 text-lg font-medium">{extractedData.contact.name}</p>
          </div>
          <div>
            <label className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Email</label>
            <a 
              href={`mailto:${extractedData.contact.email}`}
              className="text-blue-600 hover:text-blue-800 underline text-lg font-medium"
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
