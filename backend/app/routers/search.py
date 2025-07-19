"""
Search API endpoints
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from ..database import get_db, Database
from ..models import SearchResult, SearchResponse

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
        p.id,
        p.first_name || ' ' || p.last_name as name,
        s.name as additional_info
    FROM people p
    LEFT JOIN participants pt ON p.id = pt.person_id
    LEFT JOIN schools s ON pt.school_id = s.id
    WHERE p.first_name ILIKE $1 OR p.last_name ILIKE $1
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
        id,
        name,
        location as additional_info
    FROM schools
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
        id,
        name,
        year::text || ' - ' || location as additional_info
    FROM tournaments
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

@router.get("/search/wrestlers", response_model=List[SearchResult])
async def search_wrestlers(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db: Database = Depends(get_db)
):
    """Search wrestlers specifically"""
    query = """
    SELECT DISTINCT
        p.id,
        p.first_name || ' ' || p.last_name as name,
        s.name as additional_info
    FROM people p
    LEFT JOIN participants pt ON p.id = pt.person_id
    LEFT JOIN schools s ON pt.school_id = s.id
    WHERE p.first_name ILIKE $1 OR p.last_name ILIKE $1
    ORDER BY name
    LIMIT $2
    """
    
    wrestlers = await db.fetch_all(query, f"%{q}%", limit)
    return [
        SearchResult(
            type="wrestler",
            id=w["id"],
            name=w["name"],
            additional_info=w["additional_info"]
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
        id,
        name,
        location as additional_info
    FROM schools
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
