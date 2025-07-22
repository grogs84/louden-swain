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

  try {
    // Use mock endpoint for demonstration
    const response = await fetch(`${API_BASE_URL}/api/search/mock?${params}`, {
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
    // Use mock endpoint for demonstration
    const response = await fetch(`${API_BASE_URL}/api/search/suggestions/mock?${params}`, {
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

// Debounced version of getSearchSuggestions for real-time autocomplete
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>): void => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

export const getDebouncedSearchSuggestions = debounce(getSearchSuggestions, 300);

// Helper function to get result link based on type
export function getResultLink(result: { type: string; id: string }): string {
  switch (result.type) {
    case 'wrestler':
      return `/profile/${result.id}`;
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