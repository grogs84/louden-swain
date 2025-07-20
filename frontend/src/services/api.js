import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor for adding auth headers if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
    }
    return Promise.reject(error);
  }
);

// Search API endpoints
export const searchAPI = {
  // Universal search across all entities
  searchAll: (query, params = {}) => {
    return api.get('/api/search', {
      params: { q: query, ...params }
    });
  },

  // Search wrestlers specifically
  searchWrestlers: (query, params = {}) => {
    return api.get('/api/search/wrestlers', {
      params: { q: query, ...params }
    });
  },

  // Search schools specifically
  searchSchools: (query, params = {}) => {
    return api.get('/api/search/schools', {
      params: { q: query, ...params }
    });
  },

  // Simple people search (for testing)
  searchPeople: (query, params = {}) => {
    return api.get('/api/search/people', {
      params: { q: query, ...params }
    });
  },

  // Test database connection
  testDatabase: () => {
    return api.get('/api/search/test-db');
  },
};

// Wrestlers API endpoints
export const wrestlersAPI = {
  getAll: (params = {}) => {
    return api.get('/api/wrestlers', { params });
  },

  getById: (id) => {
    return api.get(`/api/wrestlers/${id}`);
  },

  getStats: (id) => {
    return api.get(`/api/wrestlers/${id}/stats`);
  },

  create: (data) => {
    return api.post('/api/wrestlers', data);
  },

  update: (id, data) => {
    return api.put(`/api/wrestlers/${id}`, data);
  },

  delete: (id) => {
    return api.delete(`/api/wrestlers/${id}`);
  },
};

// Schools API endpoints
export const schoolsAPI = {
  getAll: (params = {}) => {
    return api.get('/api/schools', { params });
  },

  getById: (id) => {
    return api.get(`/api/schools/${id}`);
  },

  getStats: (id) => {
    return api.get(`/api/schools/${id}/stats`);
  },

  create: (data) => {
    return api.post('/api/schools', data);
  },

  update: (id, data) => {
    return api.put(`/api/schools/${id}`, data);
  },

  delete: (id) => {
    return api.delete(`/api/schools/${id}`);
  },
};

// Tournaments API endpoints
export const tournamentsAPI = {
  getAll: (params = {}) => {
    return api.get('/api/tournaments', { params });
  },

  getById: (id) => {
    return api.get(`/api/tournaments/${id}`);
  },

  create: (data) => {
    return api.post('/api/tournaments', data);
  },

  update: (id, data) => {
    return api.put(`/api/tournaments/${id}`, data);
  },

  delete: (id) => {
    return api.delete(`/api/tournaments/${id}`);
  },
};

// Brackets API endpoints
export const bracketsAPI = {
  getByTournament: (tournamentId) => {
    return api.get(`/api/brackets/tournament/${tournamentId}`);
  },

  getById: (id) => {
    return api.get(`/api/brackets/${id}`);
  },

  getData: (id) => {
    return api.get(`/api/brackets/${id}/data`);
  },

  create: (data) => {
    return api.post('/api/brackets', data);
  },

  updateData: (id, data) => {
    return api.put(`/api/brackets/${id}/data`, data);
  },
};

export default api;