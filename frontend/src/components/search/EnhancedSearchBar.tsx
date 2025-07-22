'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { getSearchSuggestions, SearchAPIError } from '@/api/search';
import { SearchSuggestion } from '@/types/search';

interface EnhancedSearchBarProps {
  placeholder?: string;
  defaultValue?: string;
  autoFocus?: boolean;
  showSuggestions?: boolean;
  onSearch?: (query: string) => void;
}

export default function EnhancedSearchBar({ 
  placeholder = "Search wrestlers, schools, tournaments...",
  defaultValue = "",
  autoFocus = false,
  showSuggestions = true,
  onSearch 
}: EnhancedSearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(defaultValue);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [showSuggestionsDropdown, setShowSuggestionsDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Debounced suggestions loading
  useEffect(() => {
    if (!showSuggestions || query.length < 2) {
      setSuggestions([]);
      setShowSuggestionsDropdown(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await getSearchSuggestions(query, 8);
        setSuggestions(response.suggestions);
        setShowSuggestionsDropdown(response.suggestions.length > 0);
      } catch (error) {
        if (error instanceof SearchAPIError) {
          console.warn('Suggestions failed:', error.message);
        }
        setSuggestions([]);
        setShowSuggestionsDropdown(false);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, showSuggestions]);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestionsDropdown || suggestions.length === 0) {
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > -1 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSuggestionSelect(suggestions[selectedIndex].text);
        } else {
          handleSubmit();
        }
        break;
      case 'Escape':
        setShowSuggestionsDropdown(false);
        setSelectedIndex(-1);
        break;
    }
  };

  // Handle form submission
  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    
    if (!query.trim()) return;
    
    setShowSuggestionsDropdown(false);
    setSelectedIndex(-1);
    
    if (onSearch) {
      onSearch(query.trim());
    } else {
      // Navigate to search results page
      const params = new URLSearchParams({ q: query.trim() });
      router.push(`/search?${params.toString()}`);
    }
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestionText: string) => {
    setQuery(suggestionText);
    setShowSuggestionsDropdown(false);
    setSelectedIndex(-1);
    
    if (onSearch) {
      onSearch(suggestionText);
    } else {
      const params = new URLSearchParams({ q: suggestionText });
      router.push(`/search?${params.toString()}`);
    }
  };

  // Handle input blur (with delay to allow clicking suggestions)
  const handleBlur = () => {
    setTimeout(() => {
      setShowSuggestionsDropdown(false);
      setSelectedIndex(-1);
    }, 200);
  };

  // Handle input focus
  const handleFocus = () => {
    if (suggestions.length > 0) {
      setShowSuggestionsDropdown(true);
    }
  };

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'wrestler':
        return '🤼';
      case 'school':
        return '🏫';
      case 'tournament':
        return '🏆';
      default:
        return '🔍';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto relative">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Input
              ref={inputRef}
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={handleBlur}
              onFocus={handleFocus}
              autoFocus={autoFocus}
              className="w-full"
            />
            
            {/* Loading indicator */}
            {loading && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              </div>
            )}
          </div>
          
          <Button type="submit" variant="primary">
            Search
          </Button>
        </div>
        
        {/* Suggestions Dropdown */}
        {showSuggestionsDropdown && suggestions.length > 0 && (
          <div 
            ref={suggestionsRef}
            className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-md shadow-lg mt-1 z-20 max-h-80 overflow-y-auto"
          >
            {suggestions.map((suggestion, index) => (
              <button
                key={`${suggestion.type}-${suggestion.text}`}
                type="button"
                onClick={() => handleSuggestionSelect(suggestion.text)}
                className={`w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 flex items-center space-x-3 ${
                  index === selectedIndex ? 'bg-blue-50 border-blue-200' : ''
                }`}
              >
                <span className="text-lg">
                  {getSuggestionIcon(suggestion.type)}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 truncate">
                      {suggestion.text}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      {suggestion.type}
                    </span>
                  </div>
                  {suggestion.count && suggestion.count > 1 && (
                    <div className="text-xs text-gray-500">
                      {suggestion.count} results
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  );
}