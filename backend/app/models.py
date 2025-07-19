"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

# Base models
class PersonBase(BaseModel):
    first_name: str
    last_name: str

class SchoolBase(BaseModel):
    name: str
    location: Optional[str] = None
    state: Optional[str] = None

class TournamentBase(BaseModel):
    name: str
    year: int
    location: Optional[str] = None
    division: str = "Division I"

# Response models
class Person(PersonBase):
    id: UUID
    
    class Config:
        from_attributes = True

class School(SchoolBase):
    id: UUID
    
    class Config:
        from_attributes = True

class Tournament(TournamentBase):
    id: UUID
    
    class Config:
        from_attributes = True

class Participant(BaseModel):
    id: UUID
    person_id: UUID
    school_id: UUID
    tournament_id: UUID
    weight_class: Optional[str] = None
    seed: Optional[int] = None
    year: int
    
    class Config:
        from_attributes = True

class Match(BaseModel):
    id: UUID
    tournament_id: UUID
    winner_id: UUID
    loser_id: UUID
    round: Optional[str] = None
    match_result: Optional[str] = None
    score: Optional[str] = None
    weight_class: Optional[str] = None
    
    class Config:
        from_attributes = True

# Enhanced response models with joined data
class WrestlerProfile(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    school_name: Optional[str] = None
    school_location: Optional[str] = None

class WrestlerStats(BaseModel):
    wrestler_id: UUID
    total_matches: int = 0
    wins: int = 0
    losses: int = 0
    pins: int = 0
    tech_falls: int = 0
    major_decisions: int = 0
    win_percentage: float = 0.0

class WrestlerMatch(BaseModel):
    id: UUID
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

class SchoolStats(BaseModel):
    school_id: UUID
    total_wrestlers: int = 0
    total_matches: int = 0
    total_wins: int = 0
    total_losses: int = 0
    years_active: int = 0
    first_year: Optional[int] = None
    last_year: Optional[int] = None
    win_percentage: float = 0.0

# Search models
class SearchResult(BaseModel):
    type: str  # "wrestler", "school", "tournament"
    id: UUID
    name: str
    additional_info: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    wrestlers: List[SearchResult]
    schools: List[SearchResult]
    tournaments: List[SearchResult] = []
