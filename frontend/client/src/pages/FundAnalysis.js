import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../components/FileUpload';
import { apiService } from '../utils/api';
import { TrendingUp, Settings, AlertCircle, Calendar, Building2, Search } from 'lucide-react';

const FundAnalysis = () => {
  const navigate = useNavigate();
  const [fundFile, setFundFile] = useState(null);
  const [fundType, setFundType] = useState('predefined'); // 'predefined' or 'custom'
  const [fundAlias, setFundAlias] = useState('pi');
  const [customFundId, setCustomFundId] = useState('');
  const [fundInfo, setFundInfo] = useState(null);
  const [isFetchingFundInfo, setIsFetchingFundInfo] = useState(false);
  const [referenceDate, setReferenceDate] = useState('2025-05-30');
  const [outputFormat, setOutputFormat] = useState('excel');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    setFundFile(file);
    setError(null);
  };

  const handleFileRemove = () => {
    setFundFile(null);
  };

  const handleFundTypeChange = (type) => {
    setFundType(type);
    setFundInfo(null);
    setError(null);
    if (type === 'predefined') {
      setCustomFundId('');
    }
  };

  const handleCustomFundIdChange = (e) => {
    setCustomFundId(e.target.value);
    setFundInfo(null);
    setError(null);
  };

  const fetchFundInfo = async () => {
    if (!customFundId.trim()) {
      setError('Please enter a fund ID.');
      return;
    }

    setIsFetchingFundInfo(true);
    setError(null);
    setFundInfo(null);

    try {
      const response = await apiService.getFundInfo(customFundId.trim());
      const fundData = response.data;
      
      if (fundData && fundData.fund_name) {
        setFundInfo(fundData);
        setError(null);
      } else {
        setError('Fund not found or no data available for this ID.');
        setFundInfo(null);
      }
    } catch (err) {
      console.error('Failed to fetch fund info:', err);
      setError(
        err.response?.data?.error || 
        'Failed to fetch fund information. Please check the fund ID and try again.'
      );
      setFundInfo(null);
    } finally {
      setIsFetchingFundInfo(false);
    }
  };

  const handleAnalyze = async () => {
    if (!fundFile) {
      setError('Please upload a fund CSV file before starting the analysis.');
      return;
    }

    if (fundType === 'custom' && !fundInfo) {
      setError('Please fetch fund information before starting the analysis.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const analysisParams = {
        referenceDate,
        outputFormat
      };

      if (fundType === 'predefined') {
        analysisParams.fundAlias = fundAlias;
      } else {
        analysisParams.fundUserId = customFundId;
        analysisParams.fundName = fundInfo.fund_name;
      }

      const response = await apiService.uploadFundAnalysis(fundFile, analysisParams);
      const { jobId } = response.data;
      
      // Navigate to results page to show progress and results
      navigate(`/results/${jobId}`);
      
    } catch (err) {
      console.error('Fund analysis failed:', err);
      setError(
        err.response?.data?.details || 
        err.response?.data?.error || 
        'Failed to start fund analysis. Please try again.'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Fund Analysis</h2>
        <p className="text-gray-600">
          Upload a fund position report to analyze against internal data. This tool extracts internal 
          fund data, performs comprehensive comparison, and generates detailed difference reports.
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
        <div className="mb-6">
          <FileUpload
            label="Fund Position Report (CSV)"
            onFileSelect={handleFileSelect}
            acceptedFile={fundFile}
            onFileRemove={handleFileRemove}
            disabled={isAnalyzing}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Building2 className="h-5 w-5 text-gray-500" />
              <label className="block text-sm font-medium text-gray-700">
                Fund Selection
              </label>
            </div>
            
            <div className="space-y-4">
              {/* Fund Type Selection */}
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="fundType"
                    value="predefined"
                    checked={fundType === 'predefined'}
                    onChange={(e) => handleFundTypeChange(e.target.value)}
                    className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                    disabled={isAnalyzing}
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">
                    Predefined Funds
                  </span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="fundType"
                    value="custom"
                    checked={fundType === 'custom'}
                    onChange={(e) => handleFundTypeChange(e.target.value)}
                    className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                    disabled={isAnalyzing}
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">
                    Custom Fund ID
                  </span>
                </label>
              </div>

              {/* Predefined Fund Selection */}
              {fundType === 'predefined' && (
                <div className="ml-6 space-y-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="fundAlias"
                      value="pi"
                      checked={fundAlias === 'pi'}
                      onChange={(e) => setFundAlias(e.target.value)}
                      className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                      disabled={isAnalyzing}
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      PI Fund
                      <span className="block text-xs text-gray-500">Fund ID: 20697244</span>
                    </span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="fundAlias"
                      value="ai"
                      checked={fundAlias === 'ai'}
                      onChange={(e) => setFundAlias(e.target.value)}
                      className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                      disabled={isAnalyzing}
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      AI Fund
                      <span className="block text-xs text-gray-500">Fund ID: 19441218</span>
                    </span>
                  </label>
                </div>
              )}

              {/* Custom Fund ID Input */}
              {fundType === 'custom' && (
                <div className="ml-6 space-y-3">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Enter fund user ID (e.g., 12345678)"
                      value={customFundId}
                      onChange={handleCustomFundIdChange}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      disabled={isAnalyzing || isFetchingFundInfo}
                    />
                    <button
                      onClick={fetchFundInfo}
                      disabled={!customFundId.trim() || isAnalyzing || isFetchingFundInfo}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        (!customFundId.trim() || isAnalyzing || isFetchingFundInfo)
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500'
                      }`}
                    >
                      {isFetchingFundInfo ? (
                        <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                      ) : (
                        <Search className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  
                  {/* Fund Info Display */}
                  {fundInfo && (
                    <div className="bg-green-50 border border-green-200 rounded-md p-3">
                      <div className="flex items-center space-x-2">
                        <Building2 className="h-4 w-4 text-green-600" />
                        <div>
                          <p className="text-sm font-medium text-green-800">
                            {fundInfo.fund_name}
                          </p>
                          <p className="text-xs text-green-600">
                            ID: {fundInfo.user_id} | Alias: {fundInfo.fund_alias || 'N/A'}
                          </p>
                          {fundInfo.total_orders > 0 && (
                            <p className="text-xs text-green-600">
                              {fundInfo.total_orders} orders, {fundInfo.total_cessions} cessions
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Calendar className="h-5 w-5 text-gray-500" />
              <label htmlFor="referenceDate" className="block text-sm font-medium text-gray-700">
                Reference Date
              </label>
            </div>
            
            <input
              type="date"
              id="referenceDate"
              value={referenceDate}
              onChange={(e) => setReferenceDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              disabled={isAnalyzing}
            />
            <p className="text-xs text-gray-500 mt-1">
              Date for internal data extraction
            </p>
          </div>
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
                value="excel"
                checked={outputFormat === 'excel'}
                onChange={(e) => setOutputFormat(e.target.value)}
                className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                disabled={isAnalyzing}
              />
              <span className="ml-2 text-sm text-gray-700">
                Excel Report
                <span className="block text-xs text-gray-500">Formatted spreadsheet</span>
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
                <span className="block text-xs text-gray-500">Raw data format</span>
              </span>
            </label>
            
            <label className="flex items-center">
              <input
                type="radio"
                name="outputFormat"
                value="google_sheets"
                checked={outputFormat === 'google_sheets'}
                onChange={(e) => setOutputFormat(e.target.value)}
                className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                disabled={isAnalyzing}
              />
              <span className="ml-2 text-sm text-gray-700">
                Google Sheets
                <span className="block text-xs text-gray-500">Cloud spreadsheet</span>
              </span>
            </label>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-6">
          <button
            onClick={handleAnalyze}
            disabled={!fundFile || isAnalyzing || (fundType === 'custom' && !fundInfo)}
            className={`w-full flex items-center justify-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
              (!fundFile || isAnalyzing || (fundType === 'custom' && !fundInfo))
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
            }`}
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin -ml-1 mr-3 h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                Running Fund Analysis...
              </>
            ) : (
              <>
                <TrendingUp className="h-5 w-5 mr-2" />
                Start Fund Analysis
              </>
            )}
          </button>
        </div>
      </div>

      <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-green-800 mb-2">Fund Analysis Process</h3>
        <ul className="text-sm text-green-700 space-y-1">
          <li>• Extracts internal fund data from BigQuery for the reference date</li>
          <li>• Compares fund report with internal data using advanced algorithms</li>
          <li>• Identifies differences in face values, acquisition values, and other metrics</li>
          <li>• Filters out insignificant differences (&lt; 0.5 cents) to focus on meaningful discrepancies</li>
          <li>• Generates comprehensive reports with statistics and downloadable exports</li>
          <li>• Supports multiple output formats for different analysis needs</li>
        </ul>
      </div>

      <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-amber-800 mb-2">Requirements</h3>
        <ul className="text-sm text-amber-700 space-y-1">
          <li>• Fund CSV file must contain "NumeroContrato" column for matching</li>
          <li>• Internal data access requires proper BigQuery credentials</li>
          <li>• Google Sheets export requires google_credentials.json configuration</li>
          <li>• For custom funds: Enter the fund user ID and fetch fund information before analysis</li>
        </ul>
      </div>
    </div>
  );
};

export default FundAnalysis; 