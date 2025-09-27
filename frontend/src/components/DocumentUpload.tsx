import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface DocumentUploadProps {
  onFileSelect: (file: File) => void;
  onProcessingStart: () => void;
  isProcessing: boolean;
  error?: string;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onFileSelect,
  onProcessingStart,
  isProcessing,
  error
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    multiple: false,
    disabled: isProcessing
  });

  const handleProcess = () => {
    if (selectedFile) {
      onProcessingStart();
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-8">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center">
            <span className="text-white font-bold text-xl">📄</span>
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
            Upload Tender Document
          </h2>
        </div>
        <p className="text-gray-600 text-lg">
          Upload a PDF or text file containing government tender information
        </p>
      </div>

      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300
          ${isDragActive 
            ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-lg scale-105' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-gradient-to-br hover:from-gray-50 hover:to-blue-50 hover:shadow-lg'
          }
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <div className="space-y-6">
          <div className="text-8xl text-gray-400 transition-transform duration-300 hover:scale-110">
            📄
          </div>
          {isDragActive ? (
            <div className="space-y-2">
              <p className="text-2xl font-bold text-blue-600">Drop the file here...</p>
              <p className="text-blue-500">Release to upload</p>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-xl font-semibold text-gray-700 mb-2">
                Drag & drop a file here, or click to select
              </p>
              <p className="text-gray-500 text-lg">
                Supports PDF and TXT files
              </p>
              <div className="flex items-center justify-center space-x-4 text-sm text-gray-400">
                <span className="flex items-center space-x-1">
                  <span>📄</span>
                  <span>PDF</span>
                </span>
                <span className="flex items-center space-x-1">
                  <span>📝</span>
                  <span>TXT</span>
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Selected File Display */}
      {selectedFile && (
        <div className="mt-6 p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200/50 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <span className="text-white text-xl">📄</span>
              </div>
              <div>
                <p className="font-bold text-gray-900 text-lg">{selectedFile.name}</p>
                <p className="text-sm text-gray-600 font-medium">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-500 hover:text-gray-700 transition-colors duration-200"
              disabled={isProcessing}
            >
              <span className="text-sm">✕</span>
            </button>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-6 p-6 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200/50 rounded-2xl shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
              <span className="text-white text-lg">⚠️</span>
            </div>
            <p className="text-red-700 font-semibold text-lg">{error}</p>
          </div>
        </div>
      )}

      {/* Process Button */}
      <div className="mt-8 text-center">
        <button
          onClick={handleProcess}
          disabled={!selectedFile || isProcessing}
          className={`
            px-12 py-4 rounded-2xl font-bold text-lg transition-all duration-300 transform
            ${!selectedFile || isProcessing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white hover:from-blue-700 hover:to-indigo-800 hover:shadow-xl hover:scale-105'
            }
          `}
        >
          {isProcessing ? (
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
              <span>Processing...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span>🚀</span>
              <span>Extract Tender Data</span>
            </div>
          )}
        </button>
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <div className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200/50 rounded-2xl shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent"></div>
              <div className="absolute inset-0 rounded-full border-2 border-blue-200"></div>
            </div>
            <p className="text-blue-700 font-semibold text-lg">
              Analyzing document and extracting structured data...
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
