'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { mockWrestlers, mockSchools, mockCoaches, mockTournaments } from '@/lib/mock-data';
import { Wrestler, School, Coach, Tournament } from '@/types';

type MixedEntity = (Wrestler | School | Coach | Tournament) & { type?: string };

function BrowseContent() {
  const searchParams = useSearchParams();
  const type = searchParams.get('type') || 'all';

  const getDataForType = () => {
    switch (type) {
      case 'wrestler':
        return { data: mockWrestlers as MixedEntity[], title: 'Wrestlers', icon: '🤼' };
      case 'school':
        return { data: mockSchools as MixedEntity[], title: 'Schools', icon: '🏫' };
      case 'coach':
        return { data: mockCoaches as MixedEntity[], title: 'Coaches', icon: '👨‍🏫' };
      case 'tournament':
        return { data: mockTournaments as MixedEntity[], title: 'Tournaments', icon: '🏆' };
      default:
        return { 
          data: [
            ...mockWrestlers.map(w => ({ ...w, type: 'wrestler' as const })),
            ...mockSchools.map(s => ({ ...s, type: 'school' as const })),
            ...mockCoaches.map(c => ({ ...c, type: 'coach' as const })),
            ...mockTournaments.map(t => ({ ...t, type: 'tournament' as const }))
          ] as MixedEntity[], 
          title: 'All Content', 
          icon: '📋' 
        };
    }
  };

  const { data, title, icon } = getDataForType();

  const renderWrestlerCard = (wrestler: Wrestler) => (
    <Link href={`/profile/${wrestler.id}`} key={wrestler.id}>
      <Card className="hover:shadow-lg transition-all duration-200">
        <CardHeader>
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold text-gray-600">
                {wrestler.name.split(' ').map((n: string) => n[0]).join('')}
              </span>
            </div>
            <div>
              <CardTitle className="text-lg">{wrestler.name}</CardTitle>
              <CardDescription>
                {wrestler.weight_class} lbs • {wrestler.school_name}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between text-sm">
            <span><strong>{wrestler.wins}</strong> W</span>
            <span><strong>{wrestler.losses}</strong> L</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );

  const renderSchoolCard = (school: School) => (
    <Link href={`/profile/${school.id}`}>
      <Card className="hover:shadow-lg transition-all duration-200">
        <CardHeader>
          <CardTitle className="text-lg">{school.name}</CardTitle>
          <CardDescription>{school.location}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div><strong>Conference:</strong> {school.conference}</div>
            <div><strong>Head Coach:</strong> {school.coach_name}</div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );

  const renderCoachCard = (coach: Coach) => (
    <Link href={`/profile/${coach.id}`}>
      <Card className="hover:shadow-lg transition-all duration-200">
        <CardHeader>
          <CardTitle className="text-lg">{coach.name}</CardTitle>
          <CardDescription>{coach.school_name}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-sm">
            <div><strong>{coach.years_coaching}</strong> years coaching</div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );

  const renderTournamentCard = (tournament: Tournament) => (
    <Link href={`/tournament/${tournament.id}`}>
      <Card className="hover:shadow-lg transition-all duration-200">
        <CardHeader>
          <CardTitle className="text-lg">{tournament.name}</CardTitle>
          <CardDescription>{tournament.location}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-sm">
            <div><strong>Date:</strong> {new Date(tournament.date).toLocaleDateString()}</div>
            <div><strong>Brackets:</strong> {tournament.brackets.length} weight classes</div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );

  const renderCard = (item: MixedEntity) => {
    if (type === 'wrestler' || item.type === 'wrestler') return renderWrestlerCard(item as Wrestler);
    if (type === 'school' || item.type === 'school') return renderSchoolCard(item as School);
    if (type === 'coach' || item.type === 'coach') return renderCoachCard(item as Coach);
    if (type === 'tournament' || item.type === 'tournament') return renderTournamentCard(item as Tournament);
    return null;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="text-4xl">{icon}</div>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Browse {title}</h1>
            <p className="text-gray-600 mt-2">
              Found {data.length} {title.toLowerCase()}
            </p>
          </div>
        </div>
        
        {/* Type Filter Buttons */}
        <div className="flex space-x-2">
          <Link href="/browse">
            <Button variant={type === 'all' ? 'primary' : 'outline'} size="sm">
              All
            </Button>
          </Link>
          <Link href="/browse?type=wrestler">
            <Button variant={type === 'wrestler' ? 'primary' : 'outline'} size="sm">
              Wrestlers
            </Button>
          </Link>
          <Link href="/browse?type=school">
            <Button variant={type === 'school' ? 'primary' : 'outline'} size="sm">
              Schools
            </Button>
          </Link>
          <Link href="/browse?type=coach">
            <Button variant={type === 'coach' ? 'primary' : 'outline'} size="sm">
              Coaches
            </Button>
          </Link>
          <Link href="/browse?type=tournament">
            <Button variant={type === 'tournament' ? 'primary' : 'outline'} size="sm">
              Tournaments
            </Button>
          </Link>
        </div>
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.map((item) => (
          <div key={item.id}>
            {renderCard(item)}
          </div>
        ))}
      </div>

      {/* Empty State */}
      {data.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">Try browsing a different category or check back later.</p>
        </div>
      )}
    </div>
  );
}

export default function BrowsePage() {
  return (
    <Suspense fallback={<div className="text-center py-8">Loading...</div>}>
      <BrowseContent />
    </Suspense>
  );
}