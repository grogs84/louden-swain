'use client';

import Link from 'next/link';
import { SearchResult } from '@/types/search';
import { getResultLink, formatResultType } from '@/api/search';

interface SearchResultCardProps {
  result: SearchResult;
  onSelect?: (result: SearchResult) => void;
}

export default function SearchResultCard({ result, onSelect }: SearchResultCardProps) {
  const handleClick = () => {
    onSelect?.(result);
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.9) return 'bg-green-100 text-green-800';
    if (score >= 0.8) return 'bg-blue-100 text-blue-800';
    if (score >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-600';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'wrestler':
        return '🤼';
      case 'school':
        return '🏫';
      case 'tournament':
        return '🏆';
      case 'match':
        return '⚔️';
      default:
        return '📋';
    }
  };

  const getMetadataDisplay = () => {
    if (!result.metadata) return null;
    
    const { metadata } = result;
    const items = [];
    
    if (metadata.school) items.push(`School: ${metadata.school}`);
    if (metadata.weight_class) items.push(`Weight: ${metadata.weight_class} lbs`);
    if (metadata.year) items.push(`Year: ${metadata.year}`);
    if (metadata.location) items.push(`Location: ${metadata.location}`);
    if (metadata.record) items.push(`Record: ${metadata.record}`);
    if (metadata.ranking) items.push(`Rank: #${metadata.ranking}`);
    
    return items.slice(0, 3).join(' • ');
  };

  return (
    <Link
      href={getResultLink(result)}
      onClick={handleClick}
      className="block p-4 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-colors group"
    >
      <div className="flex items-start space-x-3">
        {/* Type Icon */}
        <div className="flex-shrink-0 w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-lg">
          {getTypeIcon(result.type)}
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:text-blue-600">
              {result.title}
            </h3>
            
            {/* Relevance Score */}
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getRelevanceColor(result.relevance_score)}`}>
              {Math.round(result.relevance_score * 100)}% match
            </span>
          </div>
          
          {/* Subtitle */}
          {result.subtitle && (
            <p className="text-sm text-gray-600 mb-2">
              {result.subtitle}
            </p>
          )}
          
          {/* Type Badge and Metadata */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                {formatResultType(result.type)}
              </span>
              
              {/* Metadata */}
              {getMetadataDisplay() && (
                <span className="text-xs text-gray-500">
                  {getMetadataDisplay()}
                </span>
              )}
            </div>
            
            {/* Action Indicator */}
            <svg 
              className="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
    </Link>
  );
}