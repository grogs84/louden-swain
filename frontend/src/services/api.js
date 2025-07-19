import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Wrestlers API
export const wrestlersAPI = {
  getAll: (params = {}) => apiClient.get('/api/wrestlers', { params }),
  getById: (id) => apiClient.get(`/api/wrestlers/${id}`),
  getStats: (id) => apiClient.get(`/api/wrestlers/${id}/stats`),
  getMatches: (id, params = {}) => apiClient.get(`/api/wrestlers/${id}/matches`, { params }),
  create: (data) => apiClient.post('/api/wrestlers', data),
  update: (id, data) => apiClient.put(`/api/wrestlers/${id}`, data),
  delete: (id) => apiClient.delete(`/api/wrestlers/${id}`),
};

// Schools API
export const schoolsAPI = {
  getAll: (params = {}) => apiClient.get('/api/schools', { params }),
  getById: (id) => apiClient.get(`/api/schools/${id}`),
  getStats: (id) => apiClient.get(`/api/schools/${id}/stats`),
  create: (data) => apiClient.post('/api/schools', data),
  update: (id, data) => apiClient.put(`/api/schools/${id}`, data),
  delete: (id) => apiClient.delete(`/api/schools/${id}`),
};

// Coaches API
export const coachesAPI = {
  getAll: (params = {}) => apiClient.get('/api/coaches', { params }),
  getById: (id) => apiClient.get(`/api/coaches/${id}`),
  create: (data) => apiClient.post('/api/coaches', data),
  update: (id, data) => apiClient.put(`/api/coaches/${id}`, data),
  delete: (id) => apiClient.delete(`/api/coaches/${id}`),
};

// Tournaments API
export const tournamentsAPI = {
  getAll: (params = {}) => apiClient.get('/tournaments', { params }),
  getById: (id) => apiClient.get(`/tournaments/${id}`),
  create: (data) => apiClient.post('/tournaments', data),
};

// Brackets API
export const bracketsAPI = {
  getByTournament: (tournamentId) => apiClient.get(`/api/brackets/tournament/${tournamentId}`),
  getById: (id) => apiClient.get(`/api/brackets/${id}`),
  getData: (id) => apiClient.get(`/api/brackets/${id}/data`),
  getDataByTournamentWeight: (tournamentId, weightClass) => 
    apiClient.get(`/api/brackets/data/tournament/${tournamentId}/weight/${weightClass}`),
  create: (data) => apiClient.post('/api/brackets', data),
  updateData: (id, data) => apiClient.put(`/api/brackets/${id}/data`, data),
};

// Search API
export const searchAPI = {
  searchAll: (query, limit = 10) => apiClient.get('/api/search/', { params: { q: query, limit } }),
  searchWrestlers: (query, params = {}) => apiClient.get('/api/search/wrestlers', { params: { q: query, ...params } }),
  searchSchools: (query, params = {}) => apiClient.get('/api/search/schools', { params: { q: query, ...params } }),
};

export default apiClient;
