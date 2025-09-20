import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const apiEndpoints = {
  // Health check
  health: () => api.get('/health'),

  // File upload and processing
  uploadPitchDeck: (formData) => 
    api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 2 minutes for processing
    }),

  // Startup endpoints
  getStartup: (id) => api.get(`/api/startup/${id}`),
  getStartupComplete: (id) => api.get(`/api/startup/${id}/complete`),
  updateStartup: (id, data) => api.put(`/api/startup/${id}`, data),
  deleteStartup: (id) => api.delete(`/api/startup/${id}`),
  listStartups: (params = {}) => api.get('/api/startups', { params }),

  // Founder endpoints
  getFounders: (startupId) => api.get(`/api/startup/${startupId}/founders`),

  // Benchmark endpoints
  getBenchmarks: (startupId) => api.get(`/api/startup/${startupId}/benchmarks`),

  // Risk endpoints
  getRisks: (startupId) => api.get(`/api/startup/${startupId}/risks`),

  // Interview endpoints
  getInterviews: (startupId) => api.get(`/api/startup/${startupId}/interview`),
  getInterviewFiles: (startupId, interviewId) => 
    api.get(`/api/startup/${startupId}/interview/${interviewId}/files`),
  getInterviewQuestions: (startupId) => api.get(`/api/interview/questions${startupId ? `?startup_id=${startupId}` : ''}`),

  // Final evaluation endpoints
  getFinalEvaluation: (startupId) => api.get(`/api/startup/${startupId}/final`),

  // Memo endpoints
  getInvestmentMemo: (startupId) => api.get(`/api/startup/${startupId}/memo`),

  // Statistics
  getStats: () => api.get('/api/stats'),
};

// Helper functions for common operations
export const apiHelpers = {
  // Upload pitch deck with progress tracking
  uploadWithProgress: (formData, onProgress) => {
    return api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      },
    });
  },

  // Handle API errors consistently
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
      return {
        message,
        status: error.response.status,
        data: error.response.data,
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'Network error - please check your connection',
        status: 0,
        data: null,
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'An unexpected error occurred',
        status: 0,
        data: null,
      };
    }
  },

  // Format startup data for display
  formatStartupData: (startup) => {
    return {
      ...startup,
      formattedRevenue: startup.revenue ? `$${(startup.revenue / 1000000).toFixed(1)}M` : 'N/A',
      formattedFunding: startup.funding_raised ? `$${(startup.funding_raised / 1000000).toFixed(1)}M` : 'N/A',
      formattedValuation: startup.valuation ? `$${(startup.valuation / 1000000).toFixed(1)}M` : 'N/A',
      formattedGrowthRate: startup.growth_rate ? `${(startup.growth_rate * 100).toFixed(1)}%` : 'N/A',
      formattedChurnRate: startup.churn_rate ? `${(startup.churn_rate * 100).toFixed(1)}%` : 'N/A',
      formattedCAC: startup.cac ? `$${startup.cac.toLocaleString()}` : 'N/A',
      formattedLTV: startup.ltv ? `$${startup.ltv.toLocaleString()}` : 'N/A',
      ltvCacRatio: startup.cac && startup.ltv ? (startup.ltv / startup.cac).toFixed(1) : 'N/A',
    };
  },

  // Format risk severity for display
  formatRiskSeverity: (severity) => {
    const severityMap = {
      red: { color: '#f44336', label: 'High Risk', icon: '🔴' },
      yellow: { color: '#ff9800', label: 'Medium Risk', icon: '🟡' },
      green: { color: '#4caf50', label: 'Low Risk', icon: '🟢' },
    };
    return severityMap[severity] || { color: '#757575', label: 'Unknown', icon: '⚪' };
  },

  // Format recommendation for display
  formatRecommendation: (recommendation) => {
    const recMap = {
      pass: { color: '#4caf50', label: 'Recommend Investment', icon: '✅' },
      maybe: { color: '#ff9800', label: 'Conditional Recommendation', icon: '⚠️' },
      reject: { color: '#f44336', label: 'Do Not Recommend', icon: '❌' },
    };
    return recMap[recommendation] || { color: '#757575', label: 'Under Review', icon: '⏳' };
  },

  // Format score for display
  formatScore: (score, maxScore = 10) => {
    if (!score) return 'N/A';
    const percentage = (score / maxScore) * 100;
    let color = '#f44336'; // Red for low scores
    
    if (percentage >= 70) color = '#4caf50'; // Green for high scores
    else if (percentage >= 50) color = '#ff9800'; // Orange for medium scores
    
    return {
      value: score.toFixed(1),
      percentage: percentage.toFixed(0),
      color,
      display: `${score.toFixed(1)}/${maxScore}`,
    };
  },
};

export default api;
