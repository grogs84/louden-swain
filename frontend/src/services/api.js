import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Wrestlers API
export const wrestlersAPI = {
  getAll: (params = {}) => apiClient.get('/wrestlers', { params }),
  getById: (id) => apiClient.get(`/wrestlers/${id}`),
  getStats: (id) => apiClient.get(`/wrestlers/${id}/stats`),
  create: (data) => apiClient.post('/wrestlers', data),
  update: (id, data) => apiClient.put(`/wrestlers/${id}`, data),
  delete: (id) => apiClient.delete(`/wrestlers/${id}`),
};

// Schools API
export const schoolsAPI = {
  getAll: (params = {}) => apiClient.get('/schools', { params }),
  getById: (id) => apiClient.get(`/schools/${id}`),
  getStats: (id) => apiClient.get(`/schools/${id}/stats`),
  create: (data) => apiClient.post('/schools', data),
  update: (id, data) => apiClient.put(`/schools/${id}`, data),
  delete: (id) => apiClient.delete(`/schools/${id}`),
};

// Coaches API
export const coachesAPI = {
  getAll: (params = {}) => apiClient.get('/coaches', { params }),
  getById: (id) => apiClient.get(`/coaches/${id}`),
  create: (data) => apiClient.post('/coaches', data),
  update: (id, data) => apiClient.put(`/coaches/${id}`, data),
  delete: (id) => apiClient.delete(`/coaches/${id}`),
};

// Tournaments API
export const tournamentsAPI = {
  getAll: (params = {}) => apiClient.get('/tournaments', { params }),
  getById: (id) => apiClient.get(`/tournaments/${id}`),
  create: (data) => apiClient.post('/tournaments', data),
};

// Brackets API
export const bracketsAPI = {
  getByTournament: (tournamentId) => apiClient.get(`/brackets/tournament/${tournamentId}`),
  getById: (id) => apiClient.get(`/brackets/${id}`),
  getData: (id) => apiClient.get(`/brackets/${id}/data`),
  create: (data) => apiClient.post('/brackets', data),
  updateData: (id, data) => apiClient.put(`/brackets/${id}/data`, data),
};

// Search API
export const searchAPI = {
  searchAll: (query, limit = 10) => apiClient.get('/search/', { params: { q: query, limit } }),
  searchWrestlers: (query, params = {}) => apiClient.get('/search/wrestlers/', { params: { q: query, ...params } }),
  searchSchools: (query, params = {}) => apiClient.get('/search/schools/', { params: { q: query, ...params } }),
};

export default apiClient;
