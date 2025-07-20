'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import SearchBar from '@/components/search/search-bar';
import { SearchFilters } from '@/types';
import { mockWrestlers } from '@/lib/mock-data';

export default function HomePage() {
  const handleSearch = (query: string, filters: SearchFilters) => {
    // Mock search functionality - in real app this would call API
    console.log('Searching for:', query, 'with filters:', filters);
  };

  const browseCards = [
    {
      title: 'Browse Wrestlers',
      description: 'Discover wrestler profiles, stats, and career highlights',
      href: '/browse?type=wrestler',
      icon: '🤼'
    },
    {
      title: 'Browse Schools',
      description: 'Explore wrestling programs and team information',
      href: '/browse?type=school',
      icon: '🏫'
    },
    {
      title: 'Browse Coaches',
      description: 'Learn about coaching staff and their achievements',
      href: '/browse?type=coach',
      icon: '👨‍🏫'
    },
    {
      title: 'Browse Tournaments',
      description: 'View tournament brackets and championship results',
      href: '/browse?type=tournament',
      icon: '🏆'
    }
  ];

  const featuredWrestlers = mockWrestlers.slice(0, 3);

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-foreground">
            Louden Swain
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Your comprehensive NCAA D1 Wrestling Championship data platform. 
            Search wrestlers, explore school programs, and view tournament brackets.
          </p>
        </div>
        
        {/* Search Interface */}
        <div className="max-w-4xl mx-auto">
          <SearchBar onSearch={handleSearch} />
        </div>
      </section>

      {/* Browse Cards */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Explore Wrestling Data</h2>
          <p className="text-gray-600">Discover comprehensive wrestling information across multiple categories</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {browseCards.map((card, index) => (
            <Link key={index} href={card.href}>
              <Card className="h-full hover:shadow-lg transition-all duration-200 hover:scale-105">
                <CardHeader className="text-center">
                  <div className="text-4xl mb-2">{card.icon}</div>
                  <CardTitle className="text-lg">{card.title}</CardTitle>
                  <CardDescription>{card.description}</CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  <Button variant="outline" className="w-full">
                    Explore
                  </Button>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Content */}
      <section className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">Featured Wrestlers</h2>
          <p className="text-gray-600">Spotlight on top performers in NCAA wrestling</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {featuredWrestlers.map((wrestler) => (
            <Link key={wrestler.id} href={`/profile/${wrestler.id}`}>
              <Card className="hover:shadow-lg transition-all duration-200">
                <CardHeader>
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-lg font-bold text-gray-600">
                        {wrestler.name.split(' ').map(n => n[0]).join('')}
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
                    <span><strong>{wrestler.wins}</strong> Wins</span>
                    <span><strong>{wrestler.losses}</strong> Losses</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
        
        <div className="text-center">
          <Link href="/browse?type=wrestler">
            <Button variant="primary" size="lg">
              View All Wrestlers
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}