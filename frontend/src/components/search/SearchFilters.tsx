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
    { value: 'coach', label: 'Coaches' },
    { value: 'school', label: 'Schools' },
    { value: 'tournament', label: 'Tournaments' },
    { value: 'match', label: 'Matches' },
  ] as const;

  const limitOptions = [
    { value: 10, label: '10 per page' },
    { value: 20, label: '20 per page' },
    { value: 50, label: '50 per page' },
  ];

  const weightClassOptions = [
    '125', '133', '141', '149', '157', '165', '174', '184', '197', '285'
  ];

  const divisionOptions = [
    { value: 'D1', label: 'Division I' },
    { value: 'D2', label: 'Division II' },
    { value: 'D3', label: 'Division III' },
    { value: 'NAIA', label: 'NAIA' },
    { value: 'JUCO', label: 'JUCO' },
  ];

  const handleTypeChange = (type: string) => {
    const newFilters = {
      ...filters,
      type: type === 'all' ? undefined : type as 'wrestler' | 'school' | 'tournament' | 'match' | 'coach',
      offset: 0, // Reset to first page when changing filters
    };
    
    // Clear type-specific filters when changing type
    if (type !== 'wrestler') {
      delete newFilters.school;
      delete newFilters.weight_class;
      delete newFilters.division;
    }
    
    onFiltersChange(newFilters);
  };

  const handleLimitChange = (limit: number) => {
    onFiltersChange({
      ...filters,
      limit,
      offset: 0, // Reset to first page when changing page size
    });
  };

  const handleSpecificFilterChange = (key: string, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value || undefined,
      offset: 0, // Reset to first page when changing filters
    });
  };

  const clearFilters = () => {
    onFiltersChange({
      offset: 0,
      limit: 20,
    });
  };

  const hasActiveFilters = filters.type !== undefined || filters.school || filters.weight_class || filters.division;
  const showWrestlerFilters = filters.type === 'wrestler' || filters.type === undefined;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
      <div className="space-y-4">
        {/* First row - Basic filters */}
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

        {/* Second row - Specific filters for wrestlers */}
        {showWrestlerFilters && (
          <div className="flex flex-wrap items-center gap-4 pt-2 border-t border-gray-100">
            {/* School filter */}
            <div className="flex items-center space-x-2">
              <label htmlFor="school-filter" className="text-sm font-medium text-gray-700">
                School:
              </label>
              <input
                id="school-filter"
                type="text"
                placeholder="Enter school name"
                value={filters.school || ''}
                onChange={(e) => handleSpecificFilterChange('school', e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-40"
              />
            </div>

            {/* Weight class filter */}
            <div className="flex items-center space-x-2">
              <label htmlFor="weight-filter" className="text-sm font-medium text-gray-700">
                Weight:
              </label>
              <select
                id="weight-filter"
                value={filters.weight_class || ''}
                onChange={(e) => handleSpecificFilterChange('weight_class', e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All weights</option>
                {weightClassOptions.map((weight) => (
                  <option key={weight} value={weight}>
                    {weight} lbs
                  </option>
                ))}
              </select>
            </div>

            {/* Division filter */}
            <div className="flex items-center space-x-2">
              <label htmlFor="division-filter" className="text-sm font-medium text-gray-700">
                Division:
              </label>
              <select
                id="division-filter"
                value={filters.division || ''}
                onChange={(e) => handleSpecificFilterChange('division', e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All divisions</option>
                {divisionOptions.map((division) => (
                  <option key={division.value} value={division.value}>
                    {division.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
        
        {/* Active filters display */}
        {hasActiveFilters && (
          <div className="pt-3 border-t border-gray-200">
            <div className="flex flex-wrap items-center gap-2">
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
              {filters.school && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  School: {filters.school}
                  <button
                    onClick={() => handleSpecificFilterChange('school', '')}
                    className="ml-1 hover:text-green-600"
                  >
                    ×
                  </button>
                </span>
              )}
              {filters.weight_class && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  {filters.weight_class} lbs
                  <button
                    onClick={() => handleSpecificFilterChange('weight_class', '')}
                    className="ml-1 hover:text-purple-600"
                  >
                    ×
                  </button>
                </span>
              )}
              {filters.division && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                  {divisionOptions.find(d => d.value === filters.division)?.label}
                  <button
                    onClick={() => handleSpecificFilterChange('division', '')}
                    className="ml-1 hover:text-orange-600"
                  >
                    ×
                  </button>
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}