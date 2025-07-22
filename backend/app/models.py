"""
Pydantic models for API request/response validation
Aligned with Supabase schema using TEXT IDs
"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel


# Base models matching Supabase schema
class PersonBase(BaseModel):
    first_name: str
    last_name: str
    search_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    city_of_origin: Optional[str] = None
    state_of_origin: Optional[str] = None


class RoleBase(BaseModel):
    role_type: str  # "wrestler" or "coach"


class SchoolBase(BaseModel):
    name: str
    location: Optional[str] = None
    mascot: Optional[str] = None
    school_type: Optional[str] = None
    school_url: Optional[str] = None


class TournamentBase(BaseModel):
    name: str
    date: date
    year: Optional[int] = None
    location: Optional[str] = None


# Response models with TEXT IDs
class Person(PersonBase):
    person_id: str

    class Config:
        from_attributes = True


class Role(RoleBase):
    role_id: str
    person_id: str

    class Config:
        from_attributes = True


class School(SchoolBase):
    school_id: str

    class Config:
        from_attributes = True


class Tournament(TournamentBase):
    tournament_id: str

    class Config:
        from_attributes = True


class Participant(BaseModel):
    participant_id: str
    role_id: str
    school_id: str
    year: int
    weight_class: str
    seed: Optional[int] = None

    class Config:
        from_attributes = True


class Match(BaseModel):
    match_id: str
    round: str
    round_order: int
    bracket_order: int
    tournament_id: str
    result_type: Optional[str] = None
    fall_time: Optional[str] = None
    tech_time: Optional[str] = None
    winner_id: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipantMatch(BaseModel):
    match_id: str
    participant_id: str
    is_winner: Optional[bool] = None
    score: Optional[int] = None
    next_match_id: Optional[str] = None

    class Config:
        from_attributes = True


# Enhanced response models for MVP features
class WrestlerProfile(BaseModel):
    person_id: str
    first_name: str
    last_name: str
    search_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    city_of_origin: Optional[str] = None
    state_of_origin: Optional[str] = None
    role_id: Optional[str] = None


class WrestlerStats(BaseModel):
    person_id: str
    total_matches: int = 0
    wins: int = 0
    losses: int = 0
    pins: int = 0
    tech_falls: int = 0
    major_decisions: int = 0
    win_percentage: float = 0.0


class WrestlerMatch(BaseModel):
    match_id: str
    opponent_first_name: str
    opponent_last_name: str
    opponent_school: Optional[str] = None
    result: str  # "W" or "L"
    decision: Optional[str] = None
    score: Optional[str] = None
    tournament_name: Optional[str] = None
    round: Optional[str] = None
    year: int
    weight_class: Optional[str] = None


class SchoolProfile(BaseModel):
    school_id: str
    name: str
    location: Optional[str] = None
    mascot: Optional[str] = None
    school_type: Optional[str] = None
    school_url: Optional[str] = None


class SchoolStats(BaseModel):
    school_id: str
    total_wrestlers: int = 0
    total_matches: int = 0
    total_wins: int = 0
    total_losses: int = 0
    years_active: int = 0
    first_year: Optional[int] = None
    last_year: Optional[int] = None
    win_percentage: float = 0.0


# Enhanced search models for core search functionality
class SearchResult(BaseModel):
    """Enhanced search result with relevance scoring and metadata"""
    id: str
    type: str  # "wrestler", "school", "tournament", "match"
    title: str
    subtitle: Optional[str] = None
    relevance_score: float
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    """Enhanced search response with pagination and total count"""
    query: str
    total_count: int
    results: List[SearchResult] = []
    offset: int = 0
    limit: int = 20


class SearchSuggestion(BaseModel):
    """Search suggestion for autocomplete"""
    text: str
    type: str  # "wrestler", "school", "tournament"
    count: Optional[int] = None  # Number of results for this suggestion


class SearchSuggestionsResponse(BaseModel):
    """Response for search suggestions endpoint"""
    query: str
    suggestions: List[SearchSuggestion] = []


# Legacy search response for backward compatibility
class LegacySearchResult(BaseModel):
    type: str  # "wrestler", "school", "tournament"
    id: str
    name: str
    additional_info: Optional[str] = None


class LegacySearchResponse(BaseModel):
    query: str
    wrestlers: List[LegacySearchResult] = []
    schools: List[LegacySearchResult] = []
    tournaments: List[LegacySearchResult] = []


class WrestlerSearchResult(BaseModel):
    """Search result with disambiguation hints for wrestlers with common names"""

    person_id: str
    first_name: str
    last_name: str
    last_school: Optional[str] = None
    last_year: Optional[int] = None
    last_weight_class: Optional[str] = None

    class Config:
        from_attributes = True
