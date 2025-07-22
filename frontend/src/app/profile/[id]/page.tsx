'use client';

import { useParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { mockWrestlers, mockSchools, mockCoaches, mockTournaments } from '@/lib/mock-data';
import { Wrestler, School, Coach } from '@/types';

export default function ProfilePage() {
  const params = useParams();
  const id = params.id as string;

  // Find the entity across all mock data
  const wrestler = mockWrestlers.find(w => w.id === id);
  const school = mockSchools.find(s => s.id === id);
  const coach = mockCoaches.find(c => c.id === id);
  const tournament = mockTournaments.find(t => t.id === id);

  const entity = wrestler || school || coach || tournament;
  
  if (!entity) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">❓</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Profile Not Found</h1>
        <p className="text-gray-600 mb-4">The profile you&apos;re looking for doesn&apos;t exist.</p>
        <Link href="/browse">
          <Button variant="primary">Browse All Profiles</Button>
        </Link>
      </div>
    );
  }

  const renderWrestlerProfile = (wrestler: Wrestler) => (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-700 text-white rounded-lg p-8">
        <div className="flex items-start space-x-6">
          <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-2xl font-bold">
              {wrestler.name.split(' ').map((n: string) => n[0]).join('')}
            </span>
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">{wrestler.name}</h1>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="font-medium">Weight Class</div>
                <div className="text-xl">{wrestler.weight_class} lbs</div>
              </div>
              <div>
                <div className="font-medium">School</div>
                <div>{wrestler.school_name}</div>
              </div>
              <div>
                <div className="font-medium">Year</div>
                <div>{wrestler.year}</div>
              </div>
              <div>
                <div className="font-medium">Hometown</div>
                <div>{wrestler.hometown}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card variant="elevated">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl text-green-600">{wrestler.wins}</CardTitle>
            <CardDescription>Wins</CardDescription>
          </CardHeader>
        </Card>
        <Card variant="elevated">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl text-red-600">{wrestler.losses}</CardTitle>
            <CardDescription>Losses</CardDescription>
          </CardHeader>
        </Card>
        <Card variant="elevated">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl text-primary-600">
              {wrestler.wins && wrestler.losses ? 
                `${((wrestler.wins / (wrestler.wins + wrestler.losses)) * 100).toFixed(1)}%` : 
                'N/A'
              }
            </CardTitle>
            <CardDescription>Win Rate</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Related Content */}
      <Card>
        <CardHeader>
          <CardTitle>School Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            School details would be loaded here...
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSchoolProfile = (school: School) => (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-secondary-600 to-secondary-800 text-white rounded-lg p-8">
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold">{school.name}</h1>
          <p className="text-xl">{school.location}</p>
          <div className="inline-flex items-center px-4 py-2 bg-white/20 rounded-full">
            <span className="font-medium">{school.conference} Conference</span>
          </div>
        </div>
      </div>

      {/* Information Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card variant="elevated">
          <CardHeader>
            <CardTitle>Program Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div><strong>Conference:</strong> {school.conference}</div>
            <div><strong>Location:</strong> {school.location}</div>
            <div><strong>Website:</strong> {school.website}</div>
          </CardContent>
        </Card>
        
        <Card variant="elevated">
          <CardHeader>
            <CardTitle>Coaching Staff</CardTitle>
          </CardHeader>
          <CardContent>
            <div><strong>Head Coach:</strong> {school.coach_name}</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderCoachProfile = (coach: Coach) => (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-accent-500 to-accent-700 text-white rounded-lg p-8">
        <div className="flex items-start space-x-6">
          <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-2xl font-bold">
              {coach.name.split(' ').map((n: string) => n[0]).join('')}
            </span>
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">{coach.name}</h1>
            <p className="text-xl mb-4">{coach.school_name}</p>
            <div className="inline-flex items-center px-4 py-2 bg-white/20 rounded-full">
              <span className="font-medium">{coach.years_coaching} years coaching</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bio */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle>Biography</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700">{coach.bio}</p>
        </CardContent>
      </Card>
    </div>
  );

  // Determine which profile to render
  if (wrestler) return renderWrestlerProfile(wrestler);
  if (school) return renderSchoolProfile(school);
  if (coach) return renderCoachProfile(coach);
  
  // Tournament profiles redirect to tournament page
  if (tournament) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">Tournament Profile</h1>
        <p className="text-gray-600 mb-4">Tournament details are available on the tournament page.</p>
        <Link href={`/tournament/${tournament.id}`}>
          <Button variant="primary">View Tournament</Button>
        </Link>
      </div>
    );
  }

  return null;
}