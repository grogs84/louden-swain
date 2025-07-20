'use client';

import { Tournament } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface TournamentInfoProps {
  tournament: Tournament;
}

export default function TournamentInfo({ tournament }: TournamentInfoProps) {
  return (
    <Card variant="elevated" className="mb-8">
      <CardHeader>
        <CardTitle className="text-2xl">{tournament.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-1">Date</h4>
            <p className="text-gray-900">
              {new Date(tournament.date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </p>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-1">Location</h4>
            <p className="text-gray-900">{tournament.location}</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-1">Weight Classes</h4>
            <p className="text-gray-900">
              {tournament.brackets.length} weight class{tournament.brackets.length !== 1 ? 'es' : ''}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}