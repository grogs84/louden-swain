// API client for search endpoints with proper error handling
import { 
  SearchResponse, 
  SearchSuggestionsResponse, 
  SearchFilters
} from '@/types/search';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class SearchAPIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'SearchAPIError';
  }
}

export async function searchAPI(
  query: string, 
  filters: SearchFilters = {}
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    offset: (filters.offset || 0).toString(),
    limit: (filters.limit || 20).toString(),
  });
  
  if (filters.type) {
    params.append('type_filter', filters.type);
  }

  // Add wrestler-specific filters
  if (filters.school) {
    params.append('school', filters.school);
  }
  if (filters.weight_class) {
    params.append('weight_class', filters.weight_class);
  }
  if (filters.division) {
    params.append('division', filters.division);
  }

  try {
    // Use real search endpoint
    const response = await fetch(`${API_BASE_URL}/api/search?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new SearchAPIError(
        errorData.detail || `Search failed with status ${response.status}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof SearchAPIError) {
      throw error;
    }
    throw new SearchAPIError('Network error occurred while searching');
  }
}

export async function getSearchSuggestions(
  query: string,
  limit: number = 10
): Promise<SearchSuggestionsResponse> {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
  });

  try {
    // Use real suggestions endpoint
    const response = await fetch(`${API_BASE_URL}/api/search/suggestions?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new SearchAPIError(
        errorData.detail || `Suggestions failed with status ${response.status}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof SearchAPIError) {
      throw error;
    }
    throw new SearchAPIError('Network error occurred while getting suggestions');
  }
}

// Helper function to get result link based on type
export function getResultLink(result: { type: string; id: string }): string {
  switch (result.type) {
    case 'wrestler':
      return `/person/${result.id}`;  // Updated to use person profile
    case 'coach':
      return `/person/${result.id}`;  // Updated to use person profile
    case 'school':
      return `/school/${result.id}`;
    case 'tournament':
      return `/tournament/${result.id}`;
    case 'match':
      return `/match/${result.id}`;
    default:
      return '#';
  }
}

// Helper function to format result type for display
export function formatResultType(type: string): string {
  switch (type) {
    case 'wrestler':
      return 'Wrestler';
    case 'coach':
      return 'Coach';
    case 'school':
      return 'School';
    case 'tournament':
      return 'Tournament';
    case 'match':
      return 'Match';
    default:
      return type.charAt(0).toUpperCase() + type.slice(1);
  }
}