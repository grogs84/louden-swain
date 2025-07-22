// Enhanced TypeScript types for the new search API

export interface SearchResult {
  id: string;
  type: 'wrestler' | 'school' | 'tournament' | 'match';
  title: string;
  subtitle?: string;
  relevance_score: number;
  metadata?: {
    [key: string]: string | number | boolean | null;
  };
}

export interface SearchResponse {
  query: string;
  total_count: number;
  results: SearchResult[];
  offset: number;
  limit: number;
}

export interface SearchSuggestion {
  text: string;
  type: 'wrestler' | 'school' | 'tournament';
  count?: number;
}

export interface SearchSuggestionsResponse {
  query: string;
  suggestions: SearchSuggestion[];
}

export interface SearchFilters {
  type?: 'wrestler' | 'school' | 'tournament' | 'match';
  offset?: number;
  limit?: number;
}

// Legacy types for backward compatibility
export interface LegacySearchResult {
  type: string;
  id: string;
  name: string;
  additional_info?: string;
}

export interface LegacySearchResponse {
  query: string;
  wrestlers: LegacySearchResult[];
  schools: LegacySearchResult[];
  tournaments: LegacySearchResult[];
}