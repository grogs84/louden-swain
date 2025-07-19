"""
Updated SQLAlchemy models based on the DuckDB wrestling database schema
This reflects a proper tournament/match/participant structure for wrestling data
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Person(Base):
    """Individual person (wrestler, coach, etc.)"""
    __tablename__ = "person"
    
    person_id = Column(String, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    roles = relationship("Role", back_populates="person")
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Unknown"

class School(Base):
    """Wrestling school/university"""
    __tablename__ = "school"
    
    school_id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    location = Column(String, nullable=True)  # Could be state, city, etc.
    created_at = Column(DateTime, default=func.now())
    
    # Additional fields we might want to add
    conference = Column(String, nullable=True)
    division = Column(String, nullable=True)
    website = Column(String, nullable=True)
    
    # Relationships
    participants = relationship("Participant", back_populates="school")

class Role(Base):
    """Role of a person (wrestler, coach, etc.)"""
    __tablename__ = "role"
    
    role_id = Column(String, primary_key=True)
    person_id = Column(String, ForeignKey("person.person_id"), nullable=True)
    role_type = Column(String, nullable=True)  # wrestler, coach, etc.
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    person = relationship("Person", back_populates="roles")
    participants = relationship("Participant", back_populates="role")

class Tournament(Base):
    """Wrestling tournament"""
    __tablename__ = "tournament"
    
    tournament_id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Additional fields we might want
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    division = Column(String, nullable=True)
    season = Column(String, nullable=True)
    
    # Relationships
    matches = relationship("Match", back_populates="tournament")
    participants = relationship("Participant", back_populates="tournament")

class Participant(Base):
    """A person participating in a tournament (usually a wrestler)"""
    __tablename__ = "participant"
    
    participant_id = Column(String, primary_key=True)
    role_id = Column(String, ForeignKey("role.role_id"), nullable=True)
    school_id = Column(String, ForeignKey("school.school_id"), nullable=True)
    tournament_id = Column(String, ForeignKey("tournament.tournament_id"), nullable=True)
    year = Column(Integer, nullable=True)  # Tournament year
    weight_class = Column(String, nullable=True)  # e.g., "125", "133", etc.
    seed = Column(Integer, nullable=True)  # Tournament seeding
    created_at = Column(DateTime, default=func.now())
    
    # Additional fields we might want
    class_year = Column(String, nullable=True)  # Freshman, Sophomore, etc.
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    
    # Relationships
    role = relationship("Role", back_populates="participants")
    school = relationship("School", back_populates="participants")
    tournament = relationship("Tournament", back_populates="participants")
    match_participations = relationship("ParticipantMatch", back_populates="participant")
    
    @property
    def wrestler_name(self):
        """Get wrestler name through role->person relationship"""
        if self.role and self.role.person:
            return self.role.person.full_name
        return "Unknown Wrestler"

class Match(Base):
    """Individual wrestling match"""
    __tablename__ = "match"
    
    match_id = Column(String, primary_key=True)
    tournament_id = Column(String, ForeignKey("tournament.tournament_id"), nullable=True)
    round = Column(String, nullable=True)  # "1st", "2nd", "champ 4", "champ 8", etc.
    round_order = Column(Integer, nullable=True)  # Order within round
    bracket_order = Column(Integer, nullable=True)  # Position in bracket
    created_at = Column(DateTime, default=func.now())
    
    # Additional fields we might want
    weight_class = Column(String, nullable=True)
    match_date = Column(DateTime, nullable=True)
    mat_number = Column(Integer, nullable=True)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    participants = relationship("ParticipantMatch", back_populates="match")

class ParticipantMatch(Base):
    """Junction table linking participants to matches with results"""
    __tablename__ = "participant_match"
    
    # Composite primary key
    match_id = Column(String, ForeignKey("match.match_id"), primary_key=True)
    participant_id = Column(String, ForeignKey("participant.participant_id"), primary_key=True)
    
    # Match result data
    is_winner = Column(Boolean, nullable=True)
    score = Column(Integer, nullable=True)  # Points scored
    result_type = Column(String, nullable=True)  # "dec", "mfft", "fall", "tech", etc.
    fall_time = Column(String, nullable=True)  # Time of fall if applicable
    next_match_id = Column(String, ForeignKey("match.match_id"), nullable=True)  # Bracket progression
    created_at = Column(DateTime, default=func.now())
    
    # Additional fields we might want
    tech_fall_score = Column(String, nullable=True)  # e.g., "15-0"
    decision_score = Column(String, nullable=True)   # e.g., "7-4"
    overtime = Column(Boolean, default=False)
    
    # Relationships
    match = relationship("Match", back_populates="participants", foreign_keys=[match_id])
    participant = relationship("Participant", back_populates="match_participations")
    next_match = relationship("Match", foreign_keys=[next_match_id])

# Note: Legacy compatibility classes removed as they are no longer needed
# The API now uses the proper Person->Role->Participant->Match structure directly
