'use client';

import { Bracket, Seed, SeedItem, SeedTeam } from 'react-brackets';
import { BracketData } from '@/types';

interface BracketDisplayProps {
  bracketData: BracketData;
}

export default function BracketDisplay({ bracketData }: BracketDisplayProps) {
  // Transform our bracket data to react-brackets format
  const transformedRounds = bracketData.rounds.map((round) => ({
    title: round.title,
    seeds: round.seeds.map((seed) => ({
      id: seed.id,
      date: seed.date,
      teams: seed.teams.map((team) => ({
        name: team.name,
        score: team.score
      }))
    }))
  }));

  return (
    <div className="w-full overflow-x-auto bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {bracketData.weight_class} lbs Championship Bracket
        </h3>
      </div>
      
      <div className="min-w-max">
        <Bracket
          rounds={transformedRounds}
          renderSeedComponent={CustomSeed}
        />
      </div>
    </div>
  );
}

// Custom seed component for styling
const CustomSeed = ({ seed, breakpoint }: { seed: { teams?: { name?: string; score?: string }[] }; breakpoint: number }) => {
  return (
    <Seed mobileBreakpoint={breakpoint}>
      <SeedItem>
        <div className="bg-white border border-gray-300 rounded-md p-2 min-w-[200px]">
          {seed.teams?.map((team: { name?: string; score?: string }, index: number) => (
            <SeedTeam key={index} className={`${index === 0 ? 'mb-1' : ''}`}>
              <div className="flex justify-between items-center py-1">
                <span className="text-sm font-medium text-gray-900 truncate">
                  {team.name || 'TBD'}
                </span>
                {team.score && (
                  <span className="text-sm font-bold text-primary-600 ml-2">
                    {team.score}
                  </span>
                )}
              </div>
            </SeedTeam>
          ))}
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {(seed as any).date && (
            <div className="text-xs text-gray-500 mt-1 border-t border-gray-200 pt-1">
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {new Date((seed as any).date).toLocaleDateString()}
            </div>
          )}
        </div>
      </SeedItem>
    </Seed>
  );
};