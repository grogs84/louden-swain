-- Wrestling Data Hub Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Schools table
CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    conference VARCHAR(100),
    state VARCHAR(2),
    city VARCHAR(100),
    logo_url TEXT,
    website TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Wrestlers table
CREATE TABLE IF NOT EXISTS wrestlers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    weight_class INTEGER NOT NULL,
    school_id INTEGER REFERENCES schools(id) ON DELETE CASCADE,
    year VARCHAR(20),
    hometown VARCHAR(100),
    state VARCHAR(2),
    height VARCHAR(10),
    weight INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Coaches table
CREATE TABLE IF NOT EXISTS coaches (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    school_id INTEGER REFERENCES schools(id) ON DELETE CASCADE,
    position VARCHAR(50),
    years_experience INTEGER,
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tournaments table
CREATE TABLE IF NOT EXISTS tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    division VARCHAR(10) DEFAULT 'D1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Brackets table
CREATE TABLE IF NOT EXISTS brackets (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id) ON DELETE CASCADE,
    weight_class INTEGER NOT NULL,
    bracket_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    bracket_id INTEGER REFERENCES brackets(id) ON DELETE CASCADE,
    wrestler1_id INTEGER REFERENCES wrestlers(id),
    wrestler2_id INTEGER REFERENCES wrestlers(id),
    winner_id INTEGER REFERENCES wrestlers(id),
    round_name VARCHAR(50),
    match_number INTEGER,
    decision_type VARCHAR(50),
    score VARCHAR(20),
    duration VARCHAR(10),
    match_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_wrestlers_school_id ON wrestlers(school_id);
CREATE INDEX IF NOT EXISTS idx_wrestlers_weight_class ON wrestlers(weight_class);
CREATE INDEX IF NOT EXISTS idx_coaches_school_id ON coaches(school_id);
CREATE INDEX IF NOT EXISTS idx_brackets_tournament_id ON brackets(tournament_id);
CREATE INDEX IF NOT EXISTS idx_brackets_weight_class ON brackets(weight_class);
CREATE INDEX IF NOT EXISTS idx_matches_bracket_id ON matches(bracket_id);
CREATE INDEX IF NOT EXISTS idx_matches_wrestler1_id ON matches(wrestler1_id);
CREATE INDEX IF NOT EXISTS idx_matches_wrestler2_id ON matches(wrestler2_id);

-- Insert some sample data
INSERT INTO schools (name, conference, state, city) VALUES
('Iowa State University', 'Big 12', 'IA', 'Ames'),
('University of Iowa', 'Big Ten', 'IA', 'Iowa City'),
('Penn State University', 'Big Ten', 'PA', 'University Park'),
('Oklahoma State University', 'Big 12', 'OK', 'Stillwater'),
('Ohio State University', 'Big Ten', 'OH', 'Columbus')
ON CONFLICT (name) DO NOTHING;

-- Insert sample wrestlers
INSERT INTO wrestlers (first_name, last_name, weight_class, school_id, year, hometown, state) VALUES
('David', 'Taylor', 165, 3, 'Senior', 'St. Paris', 'OH'),
('Kyle', 'Dake', 174, 3, 'Graduate', 'Lansing', 'NY'),
('Bo', 'Nickal', 184, 3, 'Graduate', 'Allen', 'TX'),
('Carter', 'Starocci', 174, 3, 'Junior', 'Malvern', 'PA'),
('Spencer', 'Lee', 125, 2, 'Senior', 'Murrysville', 'PA')
ON CONFLICT DO NOTHING;

-- Insert sample coaches
INSERT INTO coaches (first_name, last_name, school_id, position, years_experience) VALUES
('Cael', 'Sanderson', 3, 'Head Coach', 15),
('Tom', 'Brands', 2, 'Head Coach', 20),
('Kevin', 'Dresser', 1, 'Head Coach', 25),
('John', 'Smith', 4, 'Head Coach', 30),
('Tom', 'Ryan', 5, 'Head Coach', 18)
ON CONFLICT DO NOTHING;
