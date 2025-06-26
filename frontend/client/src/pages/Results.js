import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../utils/api';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Download, 
  ArrowLeft, 
  AlertCircle,
  Loader2,
  FileText,
  ExternalLink
} from 'lucide-react';

const Results = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [jobStatus, setJobStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadLoading, setDownloadLoading] = useState(false);

  useEffect(() => {
    let intervalId;
    
    const fetchJobStatus = async () => {
      try {
        const response = await apiService.getAnalysisStatus(jobId);
        const status = response.data;
        setJobStatus(status);
        
        if (status.status === 'completed') {
          // Fetch results
          try {
            const resultsResponse = await apiService.getAnalysisResults(jobId);
            setResults(resultsResponse.data);
          } catch (resultsError) {
            if (resultsError.response?.status !== 202) {
              console.error('Error fetching results:', resultsError);
            }
          }
          
          // Clear polling interval
          if (intervalId) {
            clearInterval(intervalId);
          }
        } else if (status.status === 'failed') {
          // Clear polling interval
          if (intervalId) {
            clearInterval(intervalId);
          }
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching job status:', err);
        setError('Failed to get analysis status');
        setLoading(false);
        
        // Clear polling interval
        if (intervalId) {
          clearInterval(intervalId);
        }
      }
    };

    // Initial fetch
    fetchJobStatus();
    
    // Poll for updates every 2 seconds if job is still processing
    intervalId = setInterval(() => {
      if (jobStatus?.status === 'processing') {
        fetchJobStatus();
      }
    }, 2000);

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [jobId, jobStatus?.status]);

  const handleDownload = async () => {
    if (!results?.downloadUrl) return;
    
    setDownloadLoading(true);
    try {
      const response = await apiService.downloadResults(jobId);
      
      // Create blob and download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = results.filename || `analysis_results_${jobId}.${jobStatus.outputFormat}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      setError('Failed to download results');
    } finally {
      setDownloadLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-8 w-8 text-green-600" />;
      case 'failed':
        return <XCircle className="h-8 w-8 text-red-600" />;
      case 'processing':
        return <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />;
      default:
        return <Clock className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Analysis Complete';
      case 'failed':
        return 'Analysis Failed';
      case 'processing':
        return 'Analysis in Progress';
      default:
        return 'Waiting...';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-800 bg-green-100';
      case 'failed':
        return 'text-red-800 bg-red-100';
      case 'processing':
        return 'text-blue-800 bg-blue-100';
      default:
        return 'text-gray-800 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
        <p className="text-gray-600">Loading analysis status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-red-800 mb-2">Error</h3>
          <p className="text-red-700">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!jobStatus) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <p className="text-gray-600">Job not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center mb-6">
          {getStatusIcon(jobStatus.status)}
          <h2 className="text-2xl font-bold text-gray-900 mt-4 mb-2">
            {getStatusText(jobStatus.status)}
          </h2>
          <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(jobStatus.status)}`}>
            {jobStatus.status.toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="space-y-3">
            <h3 className="text-lg font-medium text-gray-900">Job Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Job ID:</span>
                <span className="font-mono text-gray-900">{jobStatus.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Type:</span>
                <span className="text-gray-900 capitalize">{jobStatus.analysisType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Format:</span>
                <span className="text-gray-900 uppercase">{jobStatus.outputFormat}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Started:</span>
                <span className="text-gray-900">
                  {new Date(jobStatus.startTime).toLocaleString()}
                </span>
              </div>
              {jobStatus.endTime && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Completed:</span>
                  <span className="text-gray-900">
                    {new Date(jobStatus.endTime).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-lg font-medium text-gray-900">Files</h3>
            <div className="space-y-2 text-sm">
              {jobStatus.files.file1 && (
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-600">File 1:</span>
                  <span className="text-gray-900 truncate">{jobStatus.files.file1}</span>
                </div>
              )}
              {jobStatus.files.file2 && (
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-600">File 2:</span>
                  <span className="text-gray-900 truncate">{jobStatus.files.file2}</span>
                </div>
              )}
              {jobStatus.files.fundFile && (
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-600">Fund File:</span>
                  <span className="text-gray-900 truncate">{jobStatus.files.fundFile}</span>
                </div>
              )}
              {jobStatus.fundAlias && (
                <div className="flex items-center space-x-2">
                  <span className="text-gray-600">Fund:</span>
                  <span className="text-gray-900 uppercase">{jobStatus.fundAlias}</span>
                </div>
              )}
              {jobStatus.referenceDate && (
                <div className="flex items-center space-x-2">
                  <span className="text-gray-600">Reference Date:</span>
                  <span className="text-gray-900">{jobStatus.referenceDate}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {jobStatus.status === 'failed' && jobStatus.error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="text-sm font-medium text-red-800 mb-2">Error Details</h3>
            <p className="text-sm text-red-700">{jobStatus.error}</p>
          </div>
        )}

        {jobStatus.logs && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Analysis Logs</h3>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <pre className="text-sm text-gray-700 overflow-x-auto whitespace-pre-wrap">
                {jobStatus.logs}
              </pre>
            </div>
          </div>
        )}

        {results && (
          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Results</h3>
            
            {results.type === 'html' ? (
              <div className="space-y-4">
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">HTML Report</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Interactive HTML report with detailed analysis results.
                  </p>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        const newWindow = window.open('', '_blank');
                        newWindow.document.write(results.content);
                        newWindow.document.close();
                      }}
                      className="inline-flex items-center px-3 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 transition-colors"
                    >
                      <ExternalLink className="h-4 w-4 mr-2" />
                      View Report
                    </button>
                    <button
                      onClick={handleDownload}
                      disabled={downloadLoading}
                      className="inline-flex items-center px-3 py-2 bg-gray-600 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors disabled:opacity-50"
                    >
                      {downloadLoading ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Download className="h-4 w-4 mr-2" />
                      )}
                      Download
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Analysis Results</h4>
                <p className="text-sm text-gray-600 mb-4">
                  Download the analysis results in {jobStatus.outputFormat.toUpperCase()} format.
                </p>
                <button
                  onClick={handleDownload}
                  disabled={downloadLoading}
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50"
                >
                  {downloadLoading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4 mr-2" />
                  )}
                  Download Results
                </button>
              </div>
            )}
          </div>
        )}

        {jobStatus.status === 'processing' && (
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mr-3" />
              <span className="text-gray-600">Analysis in progress... Please wait.</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Results; 