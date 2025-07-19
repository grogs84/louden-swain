"""
Search API endpoints
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from ..database import get_db, Database
from ..models import SearchResult, SearchResponse, WrestlerSearchResult

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search_all(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum results per category"),
    db: Database = Depends(get_db)
):
    """Universal search across wrestlers, schools, and tournaments"""
    
    # Search wrestlers
    wrestler_query = """
    SELECT DISTINCT
        p.person_id as id,
        p.first_name || ' ' || p.last_name as name,
        s.name as additional_info
    FROM person p
    JOIN role r ON p.person_id = r.person_id
    LEFT JOIN participant pt ON r.role_id = pt.role_id
    LEFT JOIN school s ON pt.school_id = s.school_id
    WHERE r.role_type = 'wrestler' 
      AND (p.first_name ILIKE $1 OR p.last_name ILIKE $1 
           OR (p.first_name || ' ' || p.last_name) ILIKE $1)
    ORDER BY name
    LIMIT $2
    """
    
    wrestlers = await db.fetch_all(wrestler_query, f"%{q}%", limit)
    wrestler_results = [
        SearchResult(
            type="wrestler",
            id=w["id"],
            name=w["name"],
            additional_info=w["additional_info"]
        )
        for w in wrestlers
    ]
    
    # Search schools
    school_query = """
    SELECT 
        school_id as id,
        name,
        location as additional_info
    FROM school
    WHERE name ILIKE $1 OR location ILIKE $1
    ORDER BY name
    LIMIT $2
    """
    
    schools = await db.fetch_all(school_query, f"%{q}%", limit)
    school_results = [
        SearchResult(
            type="school",
            id=s["id"],
            name=s["name"],
            additional_info=s["additional_info"]
        )
        for s in schools
    ]
    
    # Search tournaments
    tournament_query = """
    SELECT 
        tournament_id as id,
        name,
        year::text || ' - ' || location as additional_info
    FROM tournament
    WHERE name ILIKE $1
    ORDER BY year DESC, name
    LIMIT $2
    """
    
    tournaments = await db.fetch_all(tournament_query, f"%{q}%", limit)
    tournament_results = [
        SearchResult(
            type="tournament",
            id=t["id"],
            name=t["name"],
            additional_info=t["additional_info"]
        )
        for t in tournaments
    ]
    
    return SearchResponse(
        query=q,
        wrestlers=wrestler_results,
        schools=school_results,
        tournaments=tournament_results
    )

@router.get("/search/wrestlers", response_model=List[WrestlerSearchResult])
async def search_wrestlers(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, le=50, description="Maximum results"),
    db: Database = Depends(get_db)
):
    """Search wrestlers with disambiguation hints (last school, year, weight class)"""
    query = """
    WITH wrestler_latest AS (
      SELECT DISTINCT ON (p.person_id)
        p.person_id,
        p.first_name,
        p.last_name,
        s.name as last_school,
        part.year as last_year,
        part.weight_class as last_weight_class
      FROM person p
      JOIN role r ON p.person_id = r.person_id
      JOIN participant part ON r.role_id = part.role_id
      JOIN school s ON part.school_id = s.school_id
      WHERE r.role_type = 'wrestler'
      ORDER BY p.person_id, part.year DESC
    )
    SELECT 
      person_id,
      first_name,
      last_name,
      last_school,
      last_year,
      last_weight_class
    FROM wrestler_latest
    WHERE (first_name || ' ' || last_name) ILIKE $1
       OR COALESCE(first_name, '') ILIKE $1
       OR COALESCE(last_name, '') ILIKE $1
    ORDER BY last_name, first_name
    LIMIT $2
    """
    
    wrestlers = await db.fetch_all(query, f"%{q}%", limit)
    return [
        WrestlerSearchResult(
            person_id=w["person_id"],
            first_name=w["first_name"],
            last_name=w["last_name"],
            last_school=w["last_school"],
            last_year=w["last_year"],
            last_weight_class=w["last_weight_class"]
        )
        for w in wrestlers
    ]

@router.get("/search/schools", response_model=List[SearchResult])
async def search_schools(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db: Database = Depends(get_db)
):
    """Search schools specifically"""
    query = """
    SELECT 
        school_id as id,
        name,
        location as additional_info
    FROM school
    WHERE name ILIKE $1 OR location ILIKE $1
    ORDER BY name
    LIMIT $2
    """
    
    schools = await db.fetch_all(query, f"%{q}%", limit)
    return [
        SearchResult(
            type="school",
            id=s["id"],
            name=s["name"],
            additional_info=s["additional_info"]
        )
        for s in schools
    ]

@router.get("/search/test-db", response_model=dict)
async def test_database_connection(
    db: Database = Depends(get_db)
):
    """Test database connectivity and show sample data"""
    try:
        # Test connection
        query = "SELECT COUNT(*) as total FROM person"
        result = await db.fetch_one(query)
        
        # Get a few sample persons
        sample_query = "SELECT person_id, first_name, last_name FROM person LIMIT 3"
        samples = await db.fetch_all(sample_query)
        
        return {
            "status": "connected",
            "total_people": result["total"] if result else 0,
            "sample_people": samples
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/search/debug-wrestlers", response_model=dict)
async def debug_wrestlers(
    db: Database = Depends(get_db)
):
    """Debug wrestler data structure"""
    try:
        # Check total people
        people_count = await db.fetch_one("SELECT COUNT(*) as total FROM person")
        
        # Check roles
        role_count = await db.fetch_one("SELECT COUNT(*) as total FROM role")
        wrestler_count = await db.fetch_one("SELECT COUNT(*) as total FROM role WHERE role_type = 'wrestler'")
        
        # Check participants
        participant_count = await db.fetch_one("SELECT COUNT(*) as total FROM participant")
        
        # Get sample wrestler with their info
        sample_wrestler = await db.fetch_one("""
            SELECT 
                p.person_id,
                p.first_name,
                p.last_name,
                r.role_type,
                part.year,
                part.weight_class,
                s.name as school_name
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            LEFT JOIN participant part ON r.role_id = part.role_id
            LEFT JOIN school s ON part.school_id = s.school_id
            WHERE r.role_type = 'wrestler'
            LIMIT 1
        """)
        
        return {
            "total_people": people_count["total"] if people_count else 0,
            "total_roles": role_count["total"] if role_count else 0,
            "total_wrestlers": wrestler_count["total"] if wrestler_count else 0,
            "total_participants": participant_count["total"] if participant_count else 0,
            "sample_wrestler": sample_wrestler
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/search/people", response_model=List[dict])
async def search_people_simple(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, le=50, description="Maximum results"),
    db: Database = Depends(get_db)
):
    """Simple search in person table only (for testing during migration)"""
    query = """
    SELECT 
      person_id,
      first_name,
      last_name,
      search_name,
      city_of_origin,
      state_of_origin
    FROM person
    WHERE (first_name || ' ' || last_name) ILIKE $1
       OR COALESCE(search_name, '') ILIKE $1
       OR COALESCE(first_name, '') ILIKE $1
       OR COALESCE(last_name, '') ILIKE $1
    ORDER BY last_name, first_name
    LIMIT $2
    """
    
    people = await db.fetch_all(query, f"%{q}%", limit)
    return [dict(person) for person in people]
