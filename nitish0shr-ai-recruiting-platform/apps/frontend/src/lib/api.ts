import axios from 'axios';
import { toast } from 'react-toastify';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    } else if (error.message) {
      toast.error(error.message);
    }
    return Promise.reject(error);
  }
);

// API helper functions
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },

  register: async (userData: any) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

export const jobsAPI = {
  getJobs: async (params?: any) => {
    const response = await api.get('/api/jobs', { params });
    return response.data;
  },

  getJob: async (id: string) => {
    const response = await api.get(`/api/jobs/${id}`);
    return response.data;
  },

  createJob: async (jobData: any) => {
    const response = await api.post('/api/jobs', jobData);
    return response.data;
  },

  updateJob: async (id: string, jobData: any) => {
    const response = await api.put(`/api/jobs/${id}`, jobData);
    return response.data;
  },

  deleteJob: async (id: string) => {
    const response = await api.delete(`/api/jobs/${id}`);
    return response.data;
  },
};

export const candidatesAPI = {
  getCandidates: async (params?: any) => {
    const response = await api.get('/api/candidates', { params });
    return response.data;
  },

  getCandidate: async (id: string) => {
    const response = await api.get(`/api/candidates/${id}`);
    return response.data;
  },

  createCandidate: async (candidateData: any) => {
    const response = await api.post('/api/candidates', candidateData);
    return response.data;
  },

  uploadResume: async (candidateId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('candidate_id', candidateId);
    
    const response = await api.post('/api/candidates/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  searchCandidates: async (query: string, filters?: any) => {
    const response = await api.get('/api/candidates/search', {
      params: { query, ...filters },
    });
    return response.data;
  },
};

export const fitScoreAPI = {
  calculateFitScore: async (jobId: string, candidateId: string) => {
    const response = await api.post('/api/fit-score', { job_id: jobId, candidate_id: candidateId });
    return response.data;
  },

  getTopCandidates: async (jobId: string, limit: number = 10) => {
    const response = await api.get(`/api/jobs/${jobId}/top-candidates`, {
      params: { limit },
    });
    return response.data;
  },
};

export const applicationsAPI = {
  getApplications: async (params?: any) => {
    const response = await api.get('/api/applications', { params });
    return response.data;
  },

  getApplication: async (id: string) => {
    const response = await api.get(`/api/applications/${id}`);
    return response.data;
  },

  updateApplicationStatus: async (id: string, status: string) => {
    const response = await api.patch(`/api/applications/${id}`, { status });
    return response.data;
  },
};

export const interviewsAPI = {
  getUpcomingInterviews: async () => {
    const response = await api.get('/api/interviews/upcoming');
    return response.data;
  },

  scheduleInterview: async (interviewData: any) => {
    const response = await api.post('/api/interviews', interviewData);
    return response.data;
  },

  conductInterview: async (id: string) => {
    const response = await api.post(`/api/interviews/${id}/conduct`);
    return response.data;
  },

  completeInterview: async (id: string, feedback: any, rating: number) => {
    const response = await api.patch(`/api/interviews/${id}`, {
      status: 'completed',
      feedback,
      rating,
    });
    return response.data;
  },
};

export const campaignsAPI = {
  getCampaigns: async () => {
    const response = await api.get('/api/campaigns');
    return response.data;
  },

  createCampaign: async (campaignData: any) => {
    const response = await api.post('/api/campaigns', campaignData);
    return response.data;
  },

  launchCampaign: async (id: string) => {
    const response = await api.post(`/api/campaigns/${id}/launch`);
    return response.data;
  },
};

export const analyticsAPI = {
  getDashboardData: async () => {
    const response = await api.get('/api/analytics/dashboard');
    return response.data;
  },

  getDetailedAnalytics: async (startDate?: string, endDate?: string) => {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get('/api/analytics/detailed', { params });
    return response.data;
  },
};

export const notificationsAPI = {
  getNotifications: async () => {
    const response = await api.get('/api/notifications');
    return response.data;
  },

  markAsRead: async (id: string) => {
    const response = await api.post(`/api/notifications/${id}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.post('/api/notifications/mark-all-read');
    return response.data;
  },
};