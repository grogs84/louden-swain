import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.params);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Wrestlers API
export const wrestlersAPI = {
  getById: (id) => apiClient.get(`/wrestlers/${id}`),
  getStats: (id) => apiClient.get(`/wrestlers/${id}/stats`),
  getMatches: (id, params = {}) => apiClient.get(`/wrestlers/${id}/matches`, { params }),
  search: (params) => apiClient.get('/wrestlers', { params }),
};

// Schools API
export const schoolsAPI = {
  getById: (id) => apiClient.get(`/schools/${id}`),
  getStats: (id) => apiClient.get(`/schools/${id}/stats`),
  getWrestlers: (id, params = {}) => apiClient.get(`/schools/${id}/wrestlers`, { params }),
  search: (params) => apiClient.get('/schools', { params }),
};

// Search API
export const searchAPI = {
  search: (query, params = {}) => apiClient.get('/search', { params: { q: query, ...params } }),
  wrestlers: (query, params = {}) => apiClient.get('/search/wrestlers', { params: { q: query, ...params } }),
  schools: (query, params = {}) => apiClient.get('/search/schools', { params: { q: query, ...params } }),
};

// Tournaments API
export const tournamentsAPI = {
  getById: (id) => apiClient.get(`/tournaments/${id}`),
  getBrackets: (id, params = {}) => apiClient.get(`/tournaments/${id}/brackets`, { params }),
  search: (params) => apiClient.get('/tournaments', { params }),
};

export default apiClient;
