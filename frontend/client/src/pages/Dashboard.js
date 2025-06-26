import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import { apiService } from '../utils/api';
import { Play, Settings, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [file1, setFile1] = useState(null);
  const [file2, setFile2] = useState(null);
  const [outputFormat, setOutputFormat] = useState('html');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleFile1Select = (file) => {
    setFile1(file);
    setError(null);
  };

  const handleFile2Select = (file) => {
    setFile2(file);
    setError(null);
  };

  const handleFile1Remove = () => {
    setFile1(null);
  };

  const handleFile2Remove = () => {
    setFile2(null);
  };

  const handleAnalyze = async () => {
    if (!file1 || !file2) {
      setError('Please upload both CSV files before starting the analysis.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await apiService.uploadAndAnalyze(file1, file2, {
        analysisType: 'general',
        outputFormat: outputFormat
      });

      const { jobId } = response.data;
      
      // Navigate to results page to show progress and results
      navigate(`/results/${jobId}`);
      
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(
        err.response?.data?.details || 
        err.response?.data?.error || 
        'Failed to start analysis. Please try again.'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">CSV File Comparison</h2>
        <p className="text-gray-600">
          Upload two CSV files to compare their contents and identify differences. 
          This tool uses our advanced comparison engine to provide detailed analysis reports.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <FileUpload
            label="First CSV File"
            onFileSelect={handleFile1Select}
            acceptedFile={file1}
            onFileRemove={handleFile1Remove}
            disabled={isAnalyzing}
          />
          
          <FileUpload
            label="Second CSV File"
            onFileSelect={handleFile2Select}
            acceptedFile={file2}
            onFileRemove={handleFile2Remove}
            disabled={isAnalyzing}
          />
        </div>

        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <Settings className="h-5 w-5 text-gray-500" />
            <label className="block text-sm font-medium text-gray-700">
              Output Format
            </label>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <label className="flex items-center">
              <input
                type="radio"
                name="outputFormat"
                value="html"
                checked={outputFormat === 'html'}
                onChange={(e) => setOutputFormat(e.target.value)}
                className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                disabled={isAnalyzing}
              />
              <span className="ml-2 text-sm text-gray-700">
                HTML Report
                <span className="block text-xs text-gray-500">Interactive web report</span>
              </span>
            </label>
            
            <label className="flex items-center">
              <input
                type="radio"
                name="outputFormat"
                value="json"
                checked={outputFormat === 'json'}
                onChange={(e) => setOutputFormat(e.target.value)}
                className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                disabled={isAnalyzing}
              />
              <span className="ml-2 text-sm text-gray-700">
                JSON Data
                <span className="block text-xs text-gray-500">Structured data format</span>
              </span>
            </label>
            
            <label className="flex items-center">
              <input
                type="radio"
                name="outputFormat"
                value="csv"
                checked={outputFormat === 'csv'}
                onChange={(e) => setOutputFormat(e.target.value)}
                className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                disabled={isAnalyzing}
              />
              <span className="ml-2 text-sm text-gray-700">
                CSV Export
                <span className="block text-xs text-gray-500">Tabular differences</span>
              </span>
            </label>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-6">
          <button
            onClick={handleAnalyze}
            disabled={!file1 || !file2 || isAnalyzing}
            className={`w-full flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
              (!file1 || !file2 || isAnalyzing)
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin -ml-1 mr-3 h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                Starting Analysis...
              </>
            ) : (
              <>
                <Play className="h-5 w-5 mr-2" />
                Start Comparison Analysis
              </>
            )}
          </button>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">Analysis Features</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Advanced CSV parsing with encoding detection</li>
          <li>• Configurable comparison tolerances for numeric data</li>
          <li>• Detailed difference reporting with statistics</li>
          <li>• Support for large files with optimized processing</li>
          <li>• Multiple output formats for different use cases</li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard; 