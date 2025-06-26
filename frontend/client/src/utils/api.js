import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor to add any auth headers if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      // localStorage.removeItem('authToken');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Upload files for general CSV comparison
  uploadAndAnalyze: (file1, file2, options = {}) => {
    const formData = new FormData();
    formData.append('file1', file1);
    formData.append('file2', file2);
    formData.append('analysisType', options.analysisType || 'general');
    formData.append('outputFormat', options.outputFormat || 'html');

    return api.post('/upload-and-analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Upload file for fund analysis
  uploadFundAnalysis: (file, options = {}) => {
    const formData = new FormData();
    formData.append('fundFile', file);
    if (options.fundAlias) {
      formData.append('fundAlias', options.fundAlias);
    }
    formData.append('referenceDate', options.referenceDate || '2025-05-30');
    formData.append('outputFormat', options.outputFormat || 'excel');

    return api.post('/upload-fund-analysis', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get analysis status
  getAnalysisStatus: (jobId) => api.get(`/analysis/${jobId}`),

  // Get analysis results
  getAnalysisResults: (jobId) => api.get(`/results/${jobId}`),

  // Download results file
  downloadResults: (jobId) => {
    return api.get(`/download/${jobId}`, {
      responseType: 'blob',
    });
  },
};

export default api; 