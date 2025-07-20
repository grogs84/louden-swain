// TypeScript definitions for the wrestling platform

export interface Wrestler {
  id: string;
  name: string;
  weight_class: string;
  school_id: string;
  school_name?: string;
  image_url?: string;
  wins?: number;
  losses?: number;
  year?: string;
  hometown?: string;
}

export interface School {
  id: string;
  name: string;
  location: string;
  conference?: string;
  image_url?: string;
  website?: string;
  coach_name?: string;
}

export interface Coach {
  id: string;
  name: string;
  school_id: string;
  school_name?: string;
  image_url?: string;
  years_coaching?: number;
  bio?: string;
}

export interface Tournament {
  id: string;
  name: string;
  date: string;
  location: string;
  brackets: BracketData[];
}

export interface BracketData {
  weight_class: string;
  rounds: Round[];
}

export interface Round {
  title: string;
  seeds: Seed[];
}

export interface Seed {
  id: number;
  date: string;
  teams: Team[];
}

export interface Team {
  name: string;
  score?: string;
}

export interface SearchResult {
  id: string;
  name: string;
  type: 'wrestler' | 'school' | 'coach' | 'tournament';
  description?: string;
  image_url?: string;
}

export interface SearchFilters {
  entityType?: 'wrestler' | 'school' | 'coach' | 'tournament' | 'all';
  weightClass?: string;
  school?: string;
  year?: string;
}