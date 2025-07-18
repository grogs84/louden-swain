"""
DuckDB integration for local development and testing
This script provides utilities to work with the wrestling.duckdb database
"""

import duckdb
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

class WrestlingDuckDB:
    """Interface for the wrestling DuckDB database"""
    
    def __init__(self, db_path: str = "wrestling.duckdb"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the DuckDB database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"DuckDB file not found: {self.db_path}")
        
        self.conn = duckdb.connect(self.db_path)
        return self.conn
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        if not self.conn:
            raise RuntimeError("Not connected to database")
        
        result = self.conn.execute(query).fetchall()
        columns = [desc[0] for desc in self.conn.description]
        
        return [dict(zip(columns, row)) for row in result]
    
    def get_wrestlers(self, limit: int = 20, name_filter: str = None) -> List[Dict[str, Any]]:
        """Get wrestlers with their most recent competition information"""
        query = """
        WITH wrestler_summary AS (
            SELECT 
                p.person_id,
                p.first_name,
                p.last_name,
                pt.weight_class,
                pt.year,
                pt.seed,
                s.name as school_name,
                s.location as school_location,
                ROW_NUMBER() OVER (PARTITION BY p.person_id ORDER BY pt.year DESC) as rn
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            LEFT JOIN school s ON pt.school_id = s.school_id
            WHERE r.role_type = 'wrestler'
        )
        SELECT 
            person_id,
            first_name,
            last_name,
            weight_class,
            year,
            seed,
            school_name,
            school_location
        FROM wrestler_summary 
        WHERE rn = 1
        """
        
        if name_filter:
            # Handle full name searches (first name + last name)
            search_parts = name_filter.strip().split()
            
            if len(search_parts) >= 2:
                # Multi-word search - likely first + last name
                first_part = search_parts[0]
                last_part = ' '.join(search_parts[1:])  # Handle multi-word last names
                name_condition = f"""
                AND (
                    (p.first_name ILIKE '%{first_part}%' AND p.last_name ILIKE '%{last_part}%') OR
                    (p.first_name ILIKE '%{last_part}%' AND p.last_name ILIKE '%{first_part}%') OR
                    (CONCAT(p.first_name, ' ', p.last_name) ILIKE '%{name_filter}%') OR
                    (p.first_name ILIKE '%{name_filter}%' OR p.last_name ILIKE '%{name_filter}%')
                )
                """
            else:
                # Single word search - search in both first and last name
                name_condition = f"AND (p.first_name ILIKE '%{name_filter}%' OR p.last_name ILIKE '%{name_filter}%')"
            
            # For name filtering, we need to add the filter before the window function
            query = f"""
            WITH wrestler_summary AS (
                SELECT 
                    p.person_id,
                    p.first_name,
                    p.last_name,
                    pt.weight_class,
                    pt.year,
                    pt.seed,
                    s.name as school_name,
                    s.location as school_location,
                    ROW_NUMBER() OVER (PARTITION BY p.person_id ORDER BY pt.year DESC) as rn
                FROM person p
                JOIN role r ON p.person_id = r.person_id
                JOIN participant pt ON r.role_id = pt.role_id
                LEFT JOIN school s ON pt.school_id = s.school_id
                WHERE r.role_type = 'wrestler'
                {name_condition}
            )
            SELECT 
                person_id,
                first_name,
                last_name,
                weight_class,
                year,
                seed,
                school_name,
                school_location
            FROM wrestler_summary 
            WHERE rn = 1
            """
        
        query += f" ORDER BY last_name, first_name LIMIT {limit}"
        
        return self.execute_query(query)
    
    def get_schools(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get schools with participant counts"""
        query = f"""
        SELECT 
            s.school_id,
            s.name,
            s.location,
            COUNT(DISTINCT pt.participant_id) as total_participants,
            COUNT(DISTINCT pt.year) as years_active,
            MIN(pt.year) as first_year,
            MAX(pt.year) as last_year
        FROM school s
        LEFT JOIN participant pt ON s.school_id = pt.school_id
        GROUP BY s.school_id, s.name, s.location
        ORDER BY total_participants DESC
        LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def get_tournaments(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get tournaments with match counts"""
        query = f"""
        SELECT 
            t.tournament_id,
            t.name,
            t.year,
            t.location,
            COUNT(DISTINCT m.match_id) as total_matches,
            COUNT(DISTINCT pm.participant_id) as total_participants
        FROM tournament t
        LEFT JOIN match m ON t.tournament_id = m.tournament_id
        LEFT JOIN participant_match pm ON m.match_id = pm.match_id
        GROUP BY t.tournament_id, t.name, t.year, t.location
        ORDER BY t.year DESC
        LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def get_matches(self, tournament_id: str = None, weight_class: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get matches with participant details"""
        query = """
        SELECT 
            m.match_id,
            m.round,
            m.round_order,
            m.bracket_order,
            t.name as tournament_name,
            t.year as tournament_year,
            pm.is_winner,
            pm.result_type,
            pm.fall_time,
            p.first_name,
            p.last_name,
            pt.weight_class,
            s.name as school_name
        FROM match m
        JOIN tournament t ON m.tournament_id = t.tournament_id
        JOIN participant_match pm ON m.match_id = pm.match_id
        JOIN participant pt ON pm.participant_id = pt.participant_id
        JOIN role r ON pt.role_id = r.role_id
        JOIN person p ON r.person_id = p.person_id
        LEFT JOIN school s ON pt.school_id = s.school_id
        WHERE 1=1
        """
        
        if tournament_id:
            query += f" AND m.tournament_id = '{tournament_id}'"
        
        if weight_class:
            query += f" AND pt.weight_class = '{weight_class}'"
        
        query += f" ORDER BY t.year DESC, m.round, m.bracket_order LIMIT {limit}"
        
        return self.execute_query(query)
    
    def search_wrestlers(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search wrestlers by name - returns unique wrestlers"""
        # Handle full name searches (first name + last name)
        search_parts = search_term.strip().split()
        
        if len(search_parts) >= 2:
            # Multi-word search - likely first + last name
            first_part = search_parts[0]
            last_part = ' '.join(search_parts[1:])  # Handle multi-word last names
            name_condition = f"""
            (
                (p.first_name ILIKE '%{first_part}%' AND p.last_name ILIKE '%{last_part}%') OR
                (p.first_name ILIKE '%{last_part}%' AND p.last_name ILIKE '%{first_part}%') OR
                (CONCAT(p.first_name, ' ', p.last_name) ILIKE '%{search_term}%') OR
                (p.first_name ILIKE '%{search_term}%' OR p.last_name ILIKE '%{search_term}%')
            )
            """
        else:
            # Single word search - search in both first and last name
            name_condition = f"(p.first_name ILIKE '%{search_term}%' OR p.last_name ILIKE '%{search_term}%')"
        
        query = f"""
        WITH wrestler_summary AS (
            SELECT 
                p.person_id,
                p.first_name,
                p.last_name,
                pt.weight_class,
                pt.year,
                s.name as school_name,
                s.location as school_location,
                ROW_NUMBER() OVER (PARTITION BY p.person_id ORDER BY pt.year DESC) as rn
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            LEFT JOIN school s ON pt.school_id = s.school_id
            WHERE r.role_type = 'wrestler'
            AND {name_condition}
        )
        SELECT 
            person_id,
            first_name,
            last_name,
            weight_class,
            year,
            school_name,
            school_location
        FROM wrestler_summary 
        WHERE rn = 1
        ORDER BY last_name, first_name
        LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def search_schools(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search schools by name"""
        query = f"""
        SELECT 
            s.school_id,
            s.name,
            s.location,
            COUNT(DISTINCT pt.participant_id) as total_participants
        FROM school s
        LEFT JOIN participant pt ON s.school_id = pt.school_id
        WHERE s.name ILIKE '%{search_term}%'
        GROUP BY s.school_id, s.name, s.location
        ORDER BY total_participants DESC
        LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def get_wrestler_stats(self, person_id: str) -> Dict[str, Any]:
        """Get detailed stats for a specific wrestler"""
        # Get basic info
        wrestler_query = """
        SELECT 
            p.person_id,
            p.first_name,
            p.last_name,
            pt.weight_class,
            pt.year,
            s.name as school_name,
            s.location as school_location
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        JOIN participant pt ON r.role_id = pt.role_id
        LEFT JOIN school s ON pt.school_id = s.school_id
        WHERE p.person_id = ? AND r.role_type = 'wrestler'
        LIMIT 1
        """
        
        # Get match record
        record_query = """
        SELECT 
            COUNT(*) as total_matches,
            SUM(CASE WHEN pm.is_winner THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN NOT pm.is_winner THEN 1 ELSE 0 END) as losses,
            COUNT(CASE WHEN pm.result_type = 'fall' THEN 1 END) as falls,
            COUNT(CASE WHEN pm.result_type = 'dec' THEN 1 END) as decisions,
            COUNT(CASE WHEN pm.result_type = 'mfft' THEN 1 END) as forfeits
        FROM participant_match pm
        JOIN participant pt ON pm.participant_id = pt.participant_id
        JOIN role r ON pt.role_id = r.role_id
        WHERE r.person_id = ?
        """
        
        wrestler_info = self.conn.execute(wrestler_query, [person_id]).fetchone()
        if not wrestler_info:
            return {}
        
        record_info = self.conn.execute(record_query, [person_id]).fetchone()
        
        # Combine results
        columns = [desc[0] for desc in self.conn.description]
        wrestler_data = dict(zip([desc[0] for desc in self.conn.execute(wrestler_query, [person_id]).description], wrestler_info))
        
        if record_info:
            record_columns = [desc[0] for desc in self.conn.execute(record_query, [person_id]).description]
            record_data = dict(zip(record_columns, record_info))
            wrestler_data.update(record_data)
        
        return wrestler_data
    
    def get_weight_classes(self) -> List[str]:
        """Get all weight classes in the database"""
        query = "SELECT DISTINCT weight_class FROM participant WHERE weight_class IS NOT NULL ORDER BY CAST(weight_class AS INTEGER)"
        result = self.execute_query(query)
        return [row['weight_class'] for row in result]
    
    def get_years(self) -> List[int]:
        """Get all tournament years in the database"""
        query = "SELECT DISTINCT year FROM tournament WHERE year IS NOT NULL ORDER BY year DESC"
        result = self.execute_query(query)
        return [row['year'] for row in result]

def create_sample_api_data():
    """Create sample data in the format expected by our current API"""
    
    with WrestlingDuckDB() as db:
        print("🔄 Converting DuckDB data to API format...")
        
        # Get wrestlers
        wrestlers = db.get_wrestlers(limit=50)
        api_wrestlers = []
        
        for i, wrestler in enumerate(wrestlers, 1):
            api_wrestler = {
                "id": i,
                "first_name": wrestler.get('first_name', '').title() if wrestler.get('first_name') else 'Unknown',
                "last_name": wrestler.get('last_name', '').title() if wrestler.get('last_name') else 'Wrestler',
                "weight_class": int(wrestler.get('weight_class', 125)) if wrestler.get('weight_class') and wrestler.get('weight_class').isdigit() else 125,
                "year": "Senior",  # Default since DuckDB year is tournament year
                "school_id": 1,  # We'll map this properly
                "wins": 10,  # Default values
                "losses": 2,
                "created_at": "2024-01-01T00:00:00"
            }
            api_wrestlers.append(api_wrestler)
        
        # Get schools
        schools = db.get_schools(limit=30)
        api_schools = []
        
        for i, school in enumerate(schools, 1):
            api_school = {
                "id": i,
                "name": school.get('name', '').title() if school.get('name') else f'School {i}',
                "state": school.get('location', 'Unknown')[:2].upper() if school.get('location') else 'US',
                "city": school.get('location', 'Unknown City'),
                "conference": "Unknown Conference",
                "division": "Division I",
                "website": f"https://{school.get('name', 'school').lower().replace(' ', '')}.edu",
                "created_at": "2024-01-01T00:00:00"
            }
            api_schools.append(api_school)
        
        # Get tournaments
        tournaments = db.get_tournaments(limit=20)
        api_tournaments = []
        
        for i, tournament in enumerate(tournaments, 1):
            api_tournament = {
                "id": i,
                "name": tournament.get('name', f'Tournament {i}'),
                "year": tournament.get('year', 2024),
                "location": tournament.get('location', 'Unknown Location'),
                "start_date": f"{tournament.get('year', 2024)}-03-01",
                "end_date": f"{tournament.get('year', 2024)}-03-03",
                "division": "Division I",
                "created_at": "2024-01-01T00:00:00"
            }
            api_tournaments.append(api_tournament)
        
        return {
            "wrestlers": api_wrestlers,
            "schools": api_schools,
            "tournaments": api_tournaments,
            "weight_classes": db.get_weight_classes(),
            "years": db.get_years()
        }

if __name__ == "__main__":
    try:
        # Test the DuckDB integration
        with WrestlingDuckDB() as db:
            print("🏆 Testing DuckDB Integration")
            print("=" * 50)
            
            # Test wrestlers
            wrestlers = db.get_wrestlers(limit=5)
            print(f"✅ Found {len(wrestlers)} wrestlers")
            for wrestler in wrestlers[:2]:
                print(f"  • {wrestler.get('first_name', '')} {wrestler.get('last_name', '')} ({wrestler.get('weight_class', 'N/A')}lbs) - {wrestler.get('school_name', 'No School')}")
            
            # Test schools
            schools = db.get_schools(limit=5)
            print(f"\n✅ Found {len(schools)} schools")
            for school in schools[:2]:
                print(f"  • {school.get('name', 'Unknown')} - {school.get('total_participants', 0)} participants")
            
            # Test search
            search_results = db.search_wrestlers("smith", limit=3)
            print(f"\n✅ Search for 'smith': {len(search_results)} results")
            
            print("\n🎯 DuckDB integration is working!")
            
    except Exception as e:
        print(f"❌ Error testing DuckDB: {e}")
        print("Make sure wrestling.duckdb exists and duckdb is installed: pip install duckdb")
