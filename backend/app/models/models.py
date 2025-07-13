from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class Wrestler(Base):
    __tablename__ = "wrestlers"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    weight_class = Column(Integer, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    year = Column(String)  # Freshman, Sophomore, Junior, Senior
    hometown = Column(String)
    state = Column(String)
    height = Column(String)
    weight = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="wrestlers")
    matches_as_wrestler1 = relationship("Match", foreign_keys="Match.wrestler1_id", back_populates="wrestler1")
    matches_as_wrestler2 = relationship("Match", foreign_keys="Match.wrestler2_id", back_populates="wrestler2")
    wins = relationship("Match", foreign_keys="Match.winner_id", back_populates="winner")

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    conference = Column(String)
    state = Column(String)
    city = Column(String)
    logo_url = Column(String)
    website = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    wrestlers = relationship("Wrestler", back_populates="school")
    coaches = relationship("Coach", back_populates="school")

class Coach(Base):
    __tablename__ = "coaches"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    position = Column(String)  # Head Coach, Assistant Coach, etc.
    years_experience = Column(Integer)
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    school = relationship("School", back_populates="coaches")

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String)
    division = Column(String, default="D1")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    brackets = relationship("Bracket", back_populates="tournament")

class Bracket(Base):
    __tablename__ = "brackets"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    weight_class = Column(Integer, nullable=False)
    bracket_data = Column(Text)  # JSON string containing bracket structure
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="brackets")
    matches = relationship("Match", back_populates="bracket")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    bracket_id = Column(Integer, ForeignKey("brackets.id"), nullable=False)
    wrestler1_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    wrestler2_id = Column(Integer, ForeignKey("wrestlers.id"))
    winner_id = Column(Integer, ForeignKey("wrestlers.id"))
    round_name = Column(String)  # "Round 1", "Quarterfinals", "Semifinals", "Finals", etc.
    match_number = Column(Integer)
    decision_type = Column(String)  # "Decision", "Major Decision", "Technical Fall", "Pin", "Forfeit"
    score = Column(String)  # "7-2", "15-0", "Fall 1:23", etc.
    duration = Column(String)  # Match duration
    match_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    bracket = relationship("Bracket", back_populates="matches")
    wrestler1 = relationship("Wrestler", foreign_keys=[wrestler1_id], back_populates="matches_as_wrestler1")
    wrestler2 = relationship("Wrestler", foreign_keys=[wrestler2_id], back_populates="matches_as_wrestler2")
    winner = relationship("Wrestler", foreign_keys=[winner_id], back_populates="wins")
