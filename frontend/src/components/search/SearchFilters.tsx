'use client';

import { SearchFilters as ISearchFilters } from '@/types/search';

interface SearchFiltersProps {
  filters: ISearchFilters;
  onFiltersChange: (filters: ISearchFilters) => void;
  totalResults?: number;
}

export default function SearchFilters({ filters, onFiltersChange, totalResults }: SearchFiltersProps) {
  const typeOptions = [
    { value: undefined, label: 'All Types' },
    { value: 'wrestler', label: 'Wrestlers' },
    { value: 'school', label: 'Schools' },
    { value: 'tournament', label: 'Tournaments' },
    { value: 'match', label: 'Matches' },
  ] as const;

  const limitOptions = [
    { value: 10, label: '10 per page' },
    { value: 20, label: '20 per page' },
    { value: 50, label: '50 per page' },
  ];

  const handleTypeChange = (type: string) => {
    onFiltersChange({
      ...filters,
      type: type === 'all' ? undefined : type as 'wrestler' | 'school' | 'tournament' | 'match',
      offset: 0, // Reset to first page when changing filters
    });
  };

  const handleLimitChange = (limit: number) => {
    onFiltersChange({
      ...filters,
      limit,
      offset: 0, // Reset to first page when changing page size
    });
  };

  const clearFilters = () => {
    onFiltersChange({
      offset: 0,
      limit: 20,
    });
  };

  const hasActiveFilters = filters.type !== undefined;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left side - Filter controls */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Results count */}
          {totalResults !== undefined && (
            <div className="text-sm text-gray-600">
              {totalResults.toLocaleString()} result{totalResults !== 1 ? 's' : ''}
            </div>
          )}
          
          {/* Type filter */}
          <div className="flex items-center space-x-2">
            <label htmlFor="type-filter" className="text-sm font-medium text-gray-700">
              Type:
            </label>
            <select
              id="type-filter"
              value={filters.type || 'all'}
              onChange={(e) => handleTypeChange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {typeOptions.map((option) => (
                <option key={option.value || 'all'} value={option.value || 'all'}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          {/* Results per page */}
          <div className="flex items-center space-x-2">
            <label htmlFor="limit-filter" className="text-sm font-medium text-gray-700">
              Show:
            </label>
            <select
              id="limit-filter"
              value={filters.limit || 20}
              onChange={(e) => handleLimitChange(Number(e.target.value))}
              className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {limitOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {/* Right side - Clear filters */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear filters
          </button>
        )}
      </div>
      
      {/* Active filters display */}
      {hasActiveFilters && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Active filters:</span>
            {filters.type && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {typeOptions.find(opt => opt.value === filters.type)?.label}
                <button
                  onClick={() => handleTypeChange('all')}
                  className="ml-1 hover:text-blue-600"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}