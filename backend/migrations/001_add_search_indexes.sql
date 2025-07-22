-- Add search indexes for improved performance
-- This migration adds database indexes to optimize search queries

-- Indexes for person table (wrestler searches)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_person_first_name_gin 
ON person USING gin(to_tsvector('english', COALESCE(first_name, '')));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_person_last_name_gin 
ON person USING gin(to_tsvector('english', COALESCE(last_name, '')));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_person_full_name_gin 
ON person USING gin(to_tsvector('english', COALESCE(first_name || ' ' || last_name, '')));

-- Simple text pattern indexes for ILIKE searches
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_person_first_name_text 
ON person(first_name text_pattern_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_person_last_name_text 
ON person(last_name text_pattern_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_person_search_name_text 
ON person(search_name text_pattern_ops);

-- Indexes for school table
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_school_name_gin 
ON school USING gin(to_tsvector('english', COALESCE(name, '')));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_school_name_text 
ON school(name text_pattern_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_school_location_text 
ON school(location text_pattern_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_school_mascot_text 
ON school(mascot text_pattern_ops);

-- Indexes for tournament table
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tournament_name_gin 
ON tournament USING gin(to_tsvector('english', COALESCE(name, '')));

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tournament_name_text 
ON tournament(name text_pattern_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tournament_location_text 
ON tournament(location text_pattern_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tournament_year 
ON tournament(year);

-- Indexes for role table to speed up wrestler filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_role_type 
ON role(role_type);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_role_person_type 
ON role(person_id, role_type);

-- Indexes for participant table to speed up joins
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participant_role_id 
ON participant(role_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participant_school_id 
ON participant(school_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participant_year 
ON participant(year);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participant_weight_class 
ON participant(weight_class);

-- Composite indexes for common query patterns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participant_role_year 
ON participant(role_id, year DESC);

-- For search result ordering and pagination
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_person_name_order 
ON person(last_name, first_name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_school_name_order 
ON school(name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tournament_name_year_order 
ON tournament(name, year DESC);