from pydantic import BaseModel
from typing import Optional, List, ForwardRef
from datetime import datetime

# Base schemas
class WrestlerBase(BaseModel):
    first_name: str
    last_name: str
    weight_class: int
    school_id: int
    year: Optional[str] = None
    hometown: Optional[str] = None
    state: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[int] = None

class WrestlerCreate(WrestlerBase):
    pass

class WrestlerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    weight_class: Optional[int] = None
    school_id: Optional[int] = None
    year: Optional[str] = None
    hometown: Optional[str] = None
    state: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[int] = None

class Wrestler(WrestlerBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# School schemas
class SchoolBase(BaseModel):
    name: str
    conference: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    conference: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None

class School(SchoolBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Forward reference schemas (defined after base schemas)
class WrestlerWithSchool(Wrestler):
    school: School

class SchoolWithWrestlers(School):
    wrestlers: List[Wrestler] = []

# Coach schemas
class CoachBase(BaseModel):
    first_name: str
    last_name: str
    school_id: int
    position: Optional[str] = None
    years_experience: Optional[int] = None
    bio: Optional[str] = None

class CoachCreate(CoachBase):
    pass

class CoachUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    school_id: Optional[int] = None
    position: Optional[str] = None
    years_experience: Optional[int] = None
    bio: Optional[str] = None

class Coach(CoachBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CoachWithSchool(Coach):
    school: School

# Tournament schemas
class TournamentBase(BaseModel):
    name: str
    year: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    division: str = "D1"

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    division: Optional[str] = None

class Tournament(TournamentBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Bracket schemas
class BracketBase(BaseModel):
    tournament_id: int
    weight_class: int
    bracket_data: Optional[str] = None

class BracketCreate(BracketBase):
    pass

class BracketUpdate(BaseModel):
    tournament_id: Optional[int] = None
    weight_class: Optional[int] = None
    bracket_data: Optional[str] = None

class Bracket(BracketBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BracketWithTournament(Bracket):
    tournament: Tournament

# Match schemas
class MatchBase(BaseModel):
    bracket_id: int
    wrestler1_id: int
    wrestler2_id: Optional[int] = None
    winner_id: Optional[int] = None
    round_name: Optional[str] = None
    match_number: Optional[int] = None
    decision_type: Optional[str] = None
    score: Optional[str] = None
    duration: Optional[str] = None
    match_date: Optional[datetime] = None

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchWithWrestlers(Match):
    wrestler1: Wrestler
    wrestler2: Optional[Wrestler] = None
    winner: Optional[Wrestler] = None

# Search results
class SearchResult(BaseModel):
    type: str  # "wrestler", "school", "coach"
    id: int
    name: str
    additional_info: Optional[str] = None

class SearchResults(BaseModel):
    wrestlers: List[SearchResult] = []
    schools: List[SearchResult] = []
    coaches: List[SearchResult] = []
