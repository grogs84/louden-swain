/**
 * API service configuration for frontend
 */

// Get API URL from environment or default to localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (
  process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8000' 
    : 'https://louden-swain-production.up.railway.app'
);

/**
 * Make API request with proper URL
 */
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    throw error;
  }
};

/**
 * Search API endpoints
 */
export const searchAPI = {
  // Enhanced search
  search: (query, options = {}) => {
    const params = new URLSearchParams({
      q: query,
      offset: options.offset || 0,
      limit: options.limit || 20,
      ...(options.type_filter && { type_filter: options.type_filter }),
    });
    return apiRequest(`/api/search?${params}`);
  },

  // Search suggestions
  suggestions: (query, limit = 5) => {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    return apiRequest(`/api/search/suggestions?${params}`);
  },

  // Legacy search
  legacy: (query, limit = 10) => {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    return apiRequest(`/api/search/legacy?${params}`);
  },
};

// Export API base URL for debugging
export { API_BASE_URL };
