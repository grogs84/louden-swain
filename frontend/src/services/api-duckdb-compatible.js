import axios from 'axios';

// Determine if we're using DuckDB based on environment
const USE_DUCKDB = process.env.REACT_APP_USE_DUCKDB === 'true';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to ensure trailing slash for DuckDB endpoints
const ensureTrailingSlash = (url) => {
  if (USE_DUCKDB && !url.endsWith('/')) {
    return url + '/';
  }
  return url;
};

// Enhanced API client that handles both PostgreSQL and DuckDB endpoints
const makeRequest = (method, url, config = {}) => {
  const finalUrl = ensureTrailingSlash(url);
  return apiClient[method](finalUrl, config);
};

// Wrestlers API
export const wrestlersAPI = {
  getAll: (params = {}) => makeRequest('get', '/wrestlers', { params }),
  getById: (id) => makeRequest('get', `/wrestlers/${id}`),
  getStats: (id) => makeRequest('get', `/wrestlers/${id}/stats`),
  create: (data) => USE_DUCKDB ? Promise.reject(new Error('Create not supported in DuckDB mode')) : apiClient.post('/wrestlers', data),
  update: (id, data) => USE_DUCKDB ? Promise.reject(new Error('Update not supported in DuckDB mode')) : apiClient.put(`/wrestlers/${id}`, data),
  delete: (id) => USE_DUCKDB ? Promise.reject(new Error('Delete not supported in DuckDB mode')) : apiClient.delete(`/wrestlers/${id}`),
};

// Schools API
export const schoolsAPI = {
  getAll: (params = {}) => makeRequest('get', '/schools', { params }),
  getById: (id) => makeRequest('get', `/schools/${id}`),
  getStats: (id) => makeRequest('get', `/schools/${id}/stats`),
  create: (data) => USE_DUCKDB ? Promise.reject(new Error('Create not supported in DuckDB mode')) : apiClient.post('/schools', data),
  update: (id, data) => USE_DUCKDB ? Promise.reject(new Error('Update not supported in DuckDB mode')) : apiClient.put(`/schools/${id}`, data),
  delete: (id) => USE_DUCKDB ? Promise.reject(new Error('Delete not supported in DuckDB mode')) : apiClient.delete(`/schools/${id}`),
};

// Coaches API
export const coachesAPI = {
  getAll: (params = {}) => makeRequest('get', '/coaches', { params }),
  getById: (id) => makeRequest('get', `/coaches/${id}`),
  create: (data) => USE_DUCKDB ? Promise.reject(new Error('Create not supported in DuckDB mode')) : apiClient.post('/coaches', data),
  update: (id, data) => USE_DUCKDB ? Promise.reject(new Error('Update not supported in DuckDB mode')) : apiClient.put(`/coaches/${id}`, data),
  delete: (id) => USE_DUCKDB ? Promise.reject(new Error('Delete not supported in DuckDB mode')) : apiClient.delete(`/coaches/${id}`),
};

// Tournaments API
export const tournamentsAPI = {
  getAll: (params = {}) => makeRequest('get', '/tournaments', { params }),
  getById: (id) => makeRequest('get', `/tournaments/${id}`),
  create: (data) => USE_DUCKDB ? Promise.reject(new Error('Create not supported in DuckDB mode')) : apiClient.post('/tournaments', data),
};

// Brackets API
export const bracketsAPI = {
  getByTournament: (tournamentId) => makeRequest('get', `/brackets/tournament/${tournamentId}`),
  getById: (id) => makeRequest('get', `/brackets/${id}`),
  getData: (id) => makeRequest('get', `/brackets/${id}/data`),
  create: (data) => USE_DUCKDB ? Promise.reject(new Error('Create not supported in DuckDB mode')) : apiClient.post('/brackets', data),
  updateData: (id, data) => USE_DUCKDB ? Promise.reject(new Error('Update not supported in DuckDB mode')) : apiClient.put(`/brackets/${id}/data`, data),
};

// Search API - DuckDB has different search endpoints
export const searchAPI = {
  searchAll: (query, limit = 10) => {
    if (USE_DUCKDB) {
      // DuckDB doesn't have a combined search, so search wrestlers and schools separately
      return Promise.all([
        makeRequest('get', '/search/wrestlers', { params: { q: query, limit: Math.ceil(limit/2) } }),
        makeRequest('get', '/search/schools', { params: { q: query, limit: Math.ceil(limit/2) } })
      ]).then(([wrestlersRes, schoolsRes]) => ({
        data: {
          wrestlers: wrestlersRes.data,
          schools: schoolsRes.data,
          coaches: []
        }
      }));
    } else {
      return makeRequest('get', '/search', { params: { q: query, limit } });
    }
  },
  searchWrestlers: (query, params = {}) => makeRequest('get', '/search/wrestlers', { params: { q: query, ...params } }),
  searchSchools: (query, params = {}) => makeRequest('get', '/search/schools', { params: { q: query, ...params } }),
};

export default apiClient;
