'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SearchFilters as ISearchFilters } from '@/types';

interface SearchBarProps {
  onSearch?: (query: string, filters: ISearchFilters) => void;
  placeholder?: string;
}

export default function SearchBar({ onSearch, placeholder = "Search wrestlers, schools, coaches..." }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [filters, setFilters] = useState<ISearchFilters>({
    entityType: 'all',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch?.(query, filters);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex gap-2">
          <Input
            type="text"
            placeholder={placeholder}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" variant="primary">
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
          <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-md shadow-lg mt-1 p-4 z-10">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type
                </label>
                <select
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  value={filters.entityType}
                  onChange={(e) => setFilters({ ...filters, entityType: e.target.value as 'all' | 'wrestler' | 'school' | 'coach' | 'tournament' })}
                >
                  <option value="all">All</option>
                  <option value="wrestler">Wrestlers</option>
                  <option value="school">Schools</option>
                  <option value="coach">Coaches</option>
                  <option value="tournament">Tournaments</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Weight Class
                </label>
                <select
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  value={filters.weightClass || ''}
                  onChange={(e) => setFilters({ ...filters, weightClass: e.target.value || undefined })}
                >
                  <option value="">All Weights</option>
                  <option value="125">125</option>
                  <option value="133">133</option>
                  <option value="141">141</option>
                  <option value="149">149</option>
                  <option value="157">157</option>
                  <option value="165">165</option>
                  <option value="174">174</option>
                  <option value="184">184</option>
                  <option value="197">197</option>
                  <option value="285">285</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Year
                </label>
                <select
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  value={filters.year || ''}
                  onChange={(e) => setFilters({ ...filters, year: e.target.value || undefined })}
                >
                  <option value="">All Years</option>
                  <option value="Freshman">Freshman</option>
                  <option value="Sophomore">Sophomore</option>
                  <option value="Junior">Junior</option>
                  <option value="Senior">Senior</option>
                </select>
              </div>
              
              <div className="flex items-end">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => setFilters({ entityType: 'all' })}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}