'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { searchAPI, SearchAPIError } from '@/api/search';
import { SearchResponse, SearchFilters } from '@/types/search';
import SearchResultCard from '@/components/search/SearchResultCard';
import SearchFiltersComponent from '@/components/search/SearchFilters';
import { Button } from '@/components/ui/button';

function SearchPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const query = searchParams.get('q') || '';
  const typeFilter = searchParams.get('type') as 'wrestler' | 'school' | 'tournament' | 'match' | undefined;
  const offset = parseInt(searchParams.get('offset') || '0');
  const limit = parseInt(searchParams.get('limit') || '20');
  
  const filters: SearchFilters = {
    type: typeFilter,
    offset,
    limit,
  };

  const updateURL = (newFilters: SearchFilters, newQuery?: string) => {
    const params = new URLSearchParams();
    const searchQuery = newQuery !== undefined ? newQuery : query;
    
    if (searchQuery) params.set('q', searchQuery);
    if (newFilters.type) params.set('type', newFilters.type);
    if (newFilters.offset && newFilters.offset > 0) params.set('offset', newFilters.offset.toString());
    if (newFilters.limit && newFilters.limit !== 20) params.set('limit', newFilters.limit.toString());
    
    router.push(`/search?${params.toString()}`);
  };

  const performSearch = async (searchQuery: string, searchFilters: SearchFilters) => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const results = await searchAPI(searchQuery, searchFilters);
      setSearchResults(results);
    } catch (err) {
      if (err instanceof SearchAPIError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred while searching.');
      }
      setSearchResults(null);
    } finally {
      setLoading(false);
    }
  };

  // Perform search when query or filters change
  useEffect(() => {
    if (query) {
      performSearch(query, filters);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, typeFilter, offset, limit]);

  const handleFiltersChange = (newFilters: SearchFilters) => {
    updateURL(newFilters);
  };

  const handlePagination = (newOffset: number) => {
    updateURL({ ...filters, offset: newOffset });
  };

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = searchResults ? Math.ceil(searchResults.total_count / limit) : 0;
  const hasNextPage = searchResults && offset + limit < searchResults.total_count;
  const hasPrevPage = offset > 0;

  // If no query, show empty state
  if (!query) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🔍</div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">
              Start Your Search
            </h1>
            <p className="text-gray-600 mb-6">
              Search for wrestlers, schools, tournaments, and matches to explore NCAA wrestling data.
            </p>
            <Button 
              onClick={() => router.push('/')}
              variant="primary"
            >
              Go to Homepage
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Search Results
          </h1>
          <p className="text-gray-600">
            Results for &ldquo;{query}&rdquo;
          </p>
        </div>

        {/* Filters */}
        <SearchFiltersComponent
          filters={filters}
          onFiltersChange={handleFiltersChange}
          totalResults={searchResults?.total_count}
        />

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Searching...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p className="text-red-800">
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {searchResults && !loading && (
          <>
            {searchResults.results.length > 0 ? (
              <>
                {/* Results Grid */}
                <div className="space-y-4 mb-8">
                  {searchResults.results.map((result) => (
                    <SearchResultCard
                      key={`${result.type}-${result.id}`}
                      result={result}
                    />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between bg-white border border-gray-200 rounded-lg p-4">
                    <div className="text-sm text-gray-700">
                      Showing {offset + 1} to {Math.min(offset + limit, searchResults.total_count)} of{' '}
                      {searchResults.total_count} results
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Button
                        onClick={() => handlePagination(offset - limit)}
                        disabled={!hasPrevPage}
                        variant="outline"
                        size="sm"
                      >
                        Previous
                      </Button>
                      
                      <span className="text-sm text-gray-600">
                        Page {currentPage} of {totalPages}
                      </span>
                      
                      <Button
                        onClick={() => handlePagination(offset + limit)}
                        disabled={!hasNextPage}
                        variant="outline"
                        size="sm"
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              // No Results State
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">📭</div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  No results found
                </h2>
                <p className="text-gray-600 mb-6">
                  Try adjusting your search terms or filters to find what you&apos;re looking for.
                </p>
                <Button 
                  onClick={() => handleFiltersChange({ offset: 0, limit: 20 })}
                  variant="outline"
                >
                  Clear Filters
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default function SearchResultsPage() {
  return (
    <Suspense fallback={<div className="flex justify-center py-8">Loading search...</div>}>
      <SearchPageContent />
    </Suspense>
  );
}