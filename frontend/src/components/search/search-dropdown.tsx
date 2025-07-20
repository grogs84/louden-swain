'use client';

import Link from 'next/link';
import { SearchResult } from '@/types';

interface SearchDropdownProps {
  results: SearchResult[];
  isOpen: boolean;
  onClose: () => void;
}

export default function SearchDropdown({ results, isOpen, onClose }: SearchDropdownProps) {
  if (!isOpen || results.length === 0) {
    return null;
  }

  const getResultLink = (result: SearchResult) => {
    switch (result.type) {
      case 'wrestler':
      case 'school':
      case 'coach':
        return `/profile/${result.id}`;
      case 'tournament':
        return `/tournament/${result.id}`;
      default:
        return '#';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'wrestler':
        return 'Wrestler';
      case 'school':
        return 'School';
      case 'coach':
        return 'Coach';
      case 'tournament':
        return 'Tournament';
      default:
        return type;
    }
  };

  return (
    <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-md shadow-lg mt-1 z-20 max-h-96 overflow-y-auto">
      {results.map((result) => (
        <Link
          key={`${result.type}-${result.id}`}
          href={getResultLink(result)}
          onClick={onClose}
          className="block px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
        >
          <div className="flex items-start space-x-3">
            {result.image_url && (
              <div className="w-12 h-12 bg-gray-200 rounded-full flex-shrink-0 flex items-center justify-center">
                <span className="text-xs font-medium text-gray-600">
                  {result.name.charAt(0)}
                </span>
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {result.name}
                </p>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800">
                  {getTypeLabel(result.type)}
                </span>
              </div>
              {result.description && (
                <p className="text-sm text-gray-500 truncate">
                  {result.description}
                </p>
              )}
            </div>
          </div>
        </Link>
      ))}
      
      {results.length === 0 && (
        <div className="px-4 py-8 text-center text-gray-500">
          <p>No results found</p>
        </div>
      )}
    </div>
  );
}