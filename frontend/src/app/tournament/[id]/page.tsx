'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import { mockTournaments } from '@/lib/mock-data';
import TournamentInfo from '@/components/tournament/tournament-info';
import BracketDisplay from '@/components/tournament/bracket-display';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function TournamentPage() {
  const params = useParams();
  const id = params.id as string;

  const tournament = mockTournaments.find(t => t.id === id);
  const [selectedWeightClass, setSelectedWeightClass] = useState(
    tournament?.brackets[0]?.weight_class || '174'
  );

  if (!tournament) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🏆</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Tournament Not Found</h1>
        <p className="text-gray-600 mb-4">The tournament you&apos;re looking for doesn&apos;t exist.</p>
        <Link href="/browse?type=tournament">
          <Button variant="primary">Browse Tournaments</Button>
        </Link>
      </div>
    );
  }

  const selectedBracket = tournament.brackets.find(
    b => b.weight_class === selectedWeightClass
  );

  return (
    <div className="space-y-8">
      {/* Tournament Info */}
      <TournamentInfo tournament={tournament} />

      {/* Weight Class Navigation */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-foreground">Championship Brackets</h2>
        <div className="flex flex-wrap gap-2">
          {tournament.brackets.map((bracket) => (
            <Button
              key={bracket.weight_class}
              variant={selectedWeightClass === bracket.weight_class ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSelectedWeightClass(bracket.weight_class)}
            >
              {bracket.weight_class} lbs
            </Button>
          ))}
        </div>
      </div>

      {/* Bracket Display */}
      {selectedBracket ? (
        <BracketDisplay bracketData={selectedBracket} />
      ) : (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🤼</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No bracket data available
          </h3>
          <p className="text-gray-600">
            Bracket information for {selectedWeightClass} lbs is not yet available.
          </p>
        </div>
      )}

      {/* Additional Tournament Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Placeholder for match results, highlights, etc. */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Tournament Highlights</h3>
            <div className="text-center py-8 text-gray-500">
              Tournament highlights and match results would be displayed here...
            </div>
          </div>
        </div>
        
        <div className="space-y-6">
          {/* Tournament Stats */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Tournament Stats</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Weight Classes:</span>
                <span className="font-medium">{tournament.brackets.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Date:</span>
                <span className="font-medium">
                  {new Date(tournament.date).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Location:</span>
                <span className="font-medium">{tournament.location}</span>
              </div>
            </div>
          </div>
          
          {/* Quick Links */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <div className="space-y-2">
              <Link href="/browse?type=wrestler">
                <Button variant="ghost" className="w-full justify-start">
                  Browse Wrestlers
                </Button>
              </Link>
              <Link href="/browse?type=school">
                <Button variant="ghost" className="w-full justify-start">
                  Browse Schools
                </Button>
              </Link>
              <Link href="/browse?type=tournament">
                <Button variant="ghost" className="w-full justify-start">
                  Other Tournaments
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}