'use client';

import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SearchFilters as ISearchFilters } from '@/types';
import { searchAPI, getSearchSuggestions } from '@/api/search';
import { SearchResult, SearchSuggestion } from '@/types/search';
import Link from 'next/link';

// Utility function to convert text to title case
const toTitleCase = (str: string): string => {
  if (!str) return str;
  return str.toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase());
};

interface EnhancedSearchBarProps {
  onSearch?: (query: string, filters: ISearchFilters, results: SearchResult[]) => void;
  placeholder?: string;
  showResults?: boolean;
}

export default function EnhancedSearchBar({ 
  onSearch, 
  placeholder = "Search wrestlers, schools, coaches...",
  showResults = false 
}: EnhancedSearchBarProps) {
  const [query, setQuery] = useState('');
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const [filters, setFilters] = useState<ISearchFilters>({
    entityType: 'all',
  });

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Fetch suggestions and results as user types
  useEffect(() => {
    const fetchSuggestionsAndResults = async () => {
      if (query.length < 2) {
        setSuggestions([]);
        setSearchResults([]);
        setIsDropdownOpen(false);
        return;
      }

      setIsLoading(true);
      try {
        const [suggestionsRes, searchRes] = await Promise.all([
          getSearchSuggestions(query, 5),
          searchAPI(query, { limit: 8, offset: 0 })
        ]);
        
        setSuggestions(suggestionsRes.suggestions);
        setSearchResults(searchRes.results);
        setIsDropdownOpen(true);
      } catch (error) {
        console.error('Error fetching suggestions/results:', error);
      } finally {
        setIsLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchSuggestionsAndResults, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const results = await searchAPI(query, { 
        type: filters.entityType === 'all' ? undefined : filters.entityType as any,
        limit: 20,
        offset: 0 
      });
      
      onSearch?.(query, filters, results.results);
      setIsDropdownOpen(false);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setQuery(suggestion.text);
    setIsDropdownOpen(false);
    inputRef.current?.focus();
  };

  const getResultLink = (result: SearchResult) => {
    switch (result.type) {
      case 'wrestler':
        return `/profile/${result.id}`;
      case 'school':
        return `/browse?type=school&id=${result.id}`;
      case 'tournament':
        return `/tournament/${result.id}`;
      default:
        return '#';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'wrestler':
        return '🤼';
      case 'school':
        return '🏫';
      case 'tournament':
        return '🏆';
      default:
        return '📄';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'wrestler':
        return 'bg-blue-100 text-blue-800';
      case 'school':
        return 'bg-green-100 text-green-800';
      case 'tournament':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto" ref={searchRef}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Input
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => query.length >= 2 && setIsDropdownOpen(true)}
              className="flex-1"
            />
            {isLoading && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="animate-spin h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full"></div>
              </div>
            )}
          </div>
          <Button type="submit" variant="primary" disabled={isLoading}>
            Search
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => setIsFiltersOpen(!isFiltersOpen)}
          >
            Filters
          </Button>
        </div>
        
        {/* Filters Panel */}
        {isFiltersOpen && (
          <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-md shadow-lg mt-1 p-4 z-30">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search In
                </label>
                <select
                  value={filters.entityType}
                  onChange={(e) => setFilters({ ...filters, entityType: e.target.value as any })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="all">All Categories</option>
                  <option value="wrestler">Wrestlers</option>
                  <option value="school">Schools</option>
                  <option value="tournament">Tournaments</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Search Dropdown */}
        {isDropdownOpen && (query.length >= 2) && (
          <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-md shadow-lg mt-1 z-20 max-h-96 overflow-y-auto">
            {/* Suggestions Section */}
            {suggestions.length > 0 && (
              <div className="border-b border-gray-100">
                <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Suggestions
                </div>
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center space-x-3"
                  >
                    <span className="text-lg">{getTypeIcon(suggestion.type)}</span>
                    <div>
                      <span className="text-sm text-gray-900">{suggestion.text}</span>
                      <span className={`ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getTypeColor(suggestion.type)}`}>
                        {suggestion.type}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Search Results Section */}
            {searchResults.length > 0 && (
              <div>
                <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Results
                </div>
                {searchResults.map((result) => (
                  <Link
                    key={result.id}
                    href={getResultLink(result)}
                    onClick={() => setIsDropdownOpen(false)}
                    className="block px-4 py-3 hover:bg-gray-50"
                  >
                    <div className="flex items-start space-x-3">
                      <span className="text-lg mt-0.5">{getTypeIcon(result.type)}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {toTitleCase(result.title)}
                          </p>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getTypeColor(result.type)}`}>
                            {toTitleCase(result.type)}
                          </span>
                        </div>
                        {result.subtitle && (
                          <p className="text-sm text-gray-500 truncate">
                            {toTitleCase(result.subtitle)}
                          </p>
                        )}
                        <p className="text-xs text-gray-400">
                          Relevance: {Math.round(result.relevance_score * 100)}%
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}

            {/* No Results */}
            {!isLoading && query.length >= 2 && suggestions.length === 0 && searchResults.length === 0 && (
              <div className="px-4 py-8 text-center text-gray-500">
                <p>No suggestions or results found for "{query}"</p>
              </div>
            )}
          </div>
        )}
      </form>
    </div>
  );
}
