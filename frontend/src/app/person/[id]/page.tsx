'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface PersonProfile {
  person_id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  search_name?: string;
  date_of_birth?: string;
  city_of_origin?: string;
  state_of_origin?: string;
  roles: Array<{
    role_id: string;
    role_type: string;
  }>;
  primary_affiliation?: {
    type: string;
    school: string;
    location?: string;
    year?: number;
    weight_class?: string;
  };
}

interface WrestlerData {
  person_id: string;
  stats: {
    total_matches: number;
    wins: number;
    losses: number;
    win_percentage: number;
    pins: number;
    tech_falls: number;
    major_decisions: number;
  };
  participation_history: Array<{
    year: number;
    weight_class: string;
    seed?: number;
    school: string;
    school_location?: string;
    tournament?: string;
    tournament_location?: string;
  }>;
  matches: unknown[];
}

interface CoachingData {
  person_id: string;
  coaching_data: {
    current_position?: string;
    coaching_record: {
      total_seasons: number;
      total_wins: number;
      total_losses: number;
      win_percentage: number;
    };
    career_highlights: Array<string>;
    coached_wrestlers: unknown[];
  };
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function PersonProfilePage() {
  const params = useParams();
  const personId = params.id as string;

  const [profile, setProfile] = useState<PersonProfile | null>(null);
  const [wrestlerData, setWrestlerData] = useState<WrestlerData | null>(null);
  const [coachingData, setCoachingData] = useState<CoachingData | null>(null);
  const [activeTab, setActiveTab] = useState<'wrestling' | 'coaching'>('wrestling');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch person profile
        const profileResponse = await fetch(`${API_BASE_URL}/api/persons/${personId}`);
        if (!profileResponse.ok) {
          throw new Error(`Failed to fetch profile: ${profileResponse.status}`);
        }
        const profileData = await profileResponse.json();
        setProfile(profileData);

        // Determine default tab based on roles
        const hasWrestlerRole = profileData.roles.some((r: { role_type: string }) => r.role_type === 'wrestler');
        const hasCoachRole = profileData.roles.some((r: { role_type: string }) => r.role_type === 'coach');
        
        if (hasWrestlerRole) {
          setActiveTab('wrestling');
          // Fetch wrestler data
          try {
            const wrestlerResponse = await fetch(`${API_BASE_URL}/api/persons/${personId}/wrestler`);
            if (wrestlerResponse.ok) {
              const wrestlerDataResult = await wrestlerResponse.json();
              setWrestlerData(wrestlerDataResult);
            }
          } catch (err) {
            console.warn('Failed to fetch wrestler data:', err);
          }
        } else if (hasCoachRole) {
          setActiveTab('coaching');
        }

        // Fetch coaching data if has coach role
        if (hasCoachRole) {
          try {
            const coachResponse = await fetch(`${API_BASE_URL}/api/persons/${personId}/coach`);
            if (coachResponse.ok) {
              const coachDataResult = await coachResponse.json();
              setCoachingData(coachDataResult);
            }
          } catch (err) {
            console.warn('Failed to fetch coaching data:', err);
          }
        }

      } catch (err) {
        console.error('Error fetching person profile:', err);
        setError(err instanceof Error ? err.message : 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    if (personId) {
      fetchProfile();
    }
  }, [personId]);

  const handleTabChange = async (tab: 'wrestling' | 'coaching') => {
    setActiveTab(tab);
    
    // Lazy load data for the selected tab
    if (tab === 'wrestling' && !wrestlerData && profile?.roles.some(r => r.role_type === 'wrestler')) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/persons/${personId}/wrestler`);
        if (response.ok) {
          const data = await response.json();
          setWrestlerData(data);
        }
      } catch (err) {
        console.warn('Failed to fetch wrestler data:', err);
      }
    }
    
    if (tab === 'coaching' && !coachingData && profile?.roles.some(r => r.role_type === 'coach')) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/persons/${personId}/coach`);
        if (response.ok) {
          const data = await response.json();
          setCoachingData(data);
        }
      } catch (err) {
        console.warn('Failed to fetch coaching data:', err);
      }
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h1 className="text-2xl font-bold text-red-800 mb-2">Error Loading Profile</h1>
            <p className="text-red-600 mb-4">{error}</p>
            <Link href="/search">
              <Button variant="outline">Back to Search</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Profile Not Found</h1>
            <p className="text-gray-600 mb-4">The person you&apos;re looking for could not be found.</p>
            <Link href="/search">
              <Button variant="outline">Back to Search</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const hasWrestlerRole = profile.roles.some(r => r.role_type === 'wrestler');
  const hasCoachRole = profile.roles.some(r => r.role_type === 'coach');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Breadcrumb */}
        <nav className="mb-4 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">Home</Link>
          {' / '}
          <Link href="/search" className="hover:text-blue-600">Search</Link>
          {' / '}
          <span className="text-gray-900">{profile.full_name}</span>
        </nav>

        {/* Profile Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="mb-4 md:mb-0">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {profile.full_name}
              </h1>
              {profile.search_name && profile.search_name !== profile.full_name && (
                <p className="text-lg text-gray-600 mb-2">
                  Also known as: {profile.search_name}
                </p>
              )}
              {profile.primary_affiliation && (
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                  <span className="flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 2L3 7v11h4v-6h6v6h4V7l-7-5z" clipRule="evenodd" />
                    </svg>
                    {profile.primary_affiliation.school}
                    {profile.primary_affiliation.location && ` - ${profile.primary_affiliation.location}`}
                  </span>
                  {profile.primary_affiliation.weight_class && (
                    <span>{profile.primary_affiliation.weight_class} lbs</span>
                  )}
                  {profile.primary_affiliation.year && (
                    <span>{profile.primary_affiliation.year}</span>
                  )}
                </div>
              )}
              {profile.city_of_origin && profile.state_of_origin && (
                <p className="text-sm text-gray-600 mt-2">
                  From: {profile.city_of_origin}, {profile.state_of_origin}
                </p>
              )}
            </div>
            
            {/* Role badges */}
            <div className="flex flex-wrap gap-2">
              {profile.roles.map((role) => (
                <span
                  key={role.role_id}
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    role.role_type === 'wrestler'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-green-100 text-green-800'
                  }`}
                >
                  {role.role_type.charAt(0).toUpperCase() + role.role_type.slice(1)}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Role Tabs */}
        {(hasWrestlerRole || hasCoachRole) && (
          <div className="bg-white rounded-lg shadow-md">
            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex">
                {hasWrestlerRole && (
                  <button
                    onClick={() => handleTabChange('wrestling')}
                    className={`py-4 px-6 border-b-2 font-medium text-sm ${
                      activeTab === 'wrestling'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Wrestling
                  </button>
                )}
                {hasCoachRole && (
                  <button
                    onClick={() => handleTabChange('coaching')}
                    className={`py-4 px-6 border-b-2 font-medium text-sm ${
                      activeTab === 'coaching'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Coaching
                  </button>
                )}
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'wrestling' && hasWrestlerRole && (
                <WrestlingTab data={wrestlerData} />
              )}
              {activeTab === 'coaching' && hasCoachRole && (
                <CoachingTab data={coachingData} />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Wrestling Tab Component
function WrestlingTab({ data }: { data: WrestlerData | null }) {
  if (!data) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading wrestling data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Wrestling Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{data.stats.total_matches}</div>
            <div className="text-sm text-gray-600">Total Matches</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">{data.stats.wins}</div>
            <div className="text-sm text-gray-600">Wins</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">{data.stats.losses}</div>
            <div className="text-sm text-gray-600">Losses</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">{data.stats.win_percentage.toFixed(1)}%</div>
            <div className="text-sm text-gray-600">Win %</div>
          </div>
        </div>
      </div>

      {/* Participation History */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Participation History</h3>
        {data.participation_history.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-200 rounded-lg">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weight Class</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">School</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Seed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.participation_history.map((entry, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{entry.year}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{entry.weight_class} lbs</td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {entry.school}
                      {entry.school_location && (
                        <div className="text-xs text-gray-500">{entry.school_location}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900">
                      {entry.seed ? `#${entry.seed}` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-600 text-center py-4">No participation history available</p>
        )}
      </div>
    </div>
  );
}

// Coaching Tab Component
function CoachingTab({ data }: { data: CoachingData | null }) {
  if (!data) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading coaching data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Coaching Record */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Coaching Record</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{data.coaching_data.coaching_record.total_seasons}</div>
            <div className="text-sm text-gray-600">Seasons</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">{data.coaching_data.coaching_record.total_wins}</div>
            <div className="text-sm text-gray-600">Wins</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">{data.coaching_data.coaching_record.total_losses}</div>
            <div className="text-sm text-gray-600">Losses</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">{data.coaching_data.coaching_record.win_percentage.toFixed(1)}%</div>
            <div className="text-sm text-gray-600">Win %</div>
          </div>
        </div>
      </div>

      {/* Current Position */}
      {data.coaching_data.current_position && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Position</h3>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-900">{data.coaching_data.current_position}</p>
          </div>
        </div>
      )}

      {/* Career Highlights */}
      {data.coaching_data.career_highlights.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Career Highlights</h3>
          <ul className="space-y-2">
            {data.coaching_data.career_highlights.map((highlight, index) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-600 mr-2">🏆</span>
                <span className="text-gray-700">{highlight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Placeholder for future coaching data */}
      <div className="text-center py-8 text-gray-500">
        <p>Detailed coaching statistics and achievements coming soon.</p>
      </div>
    </div>
  );
}