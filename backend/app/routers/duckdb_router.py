"""
DuckDB-based API router for local development and testing
This uses the wrestling.duckdb database instead of PostgreSQL
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

# Import our DuckDB integration
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

try:
    from duckdb_integration import WrestlingDuckDB
except ImportError:
    print("Warning: DuckDB integration not available")
    WrestlingDuckDB = None

router = APIRouter()

def get_duckdb():
    """Dependency to get DuckDB connection"""
    if not WrestlingDuckDB:
        raise HTTPException(status_code=503, detail="DuckDB not available")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'wrestling.duckdb')
    if not os.path.exists(db_path):
        raise HTTPException(status_code=503, detail=f"DuckDB file not found: {db_path}")
    
    return WrestlingDuckDB(db_path)

# Info endpoint
@router.get("/", response_model=dict)
async def duckdb_info():
    """Information about DuckDB-based API endpoints"""
    return {
        "message": "DuckDB-based API for NCAA Wrestling Championship data",
        "database": "wrestling.duckdb",
        "endpoints": {
            "wrestlers": "/wrestlers - Get all wrestlers",
            "wrestler_detail": "/wrestlers/{wrestler_id} - Get wrestler by ID",
            "schools": "/schools - Get all schools", 
            "school_detail": "/schools/{school_id} - Get school by ID",
            "tournaments": "/tournaments - Get all tournaments",
            "tournament_detail": "/tournaments/{tournament_id} - Get tournament by ID",
            "search_wrestlers": "/search/wrestlers?q=query - Search wrestlers",
            "search_schools": "/search/schools?q=query - Search schools"
        }
    }

# Wrestlers endpoints
@router.get("/wrestlers/", response_model=List[Dict[str, Any]])
async def get_wrestlers(
    limit: int = Query(20, le=100, description="Maximum results"),
    name: str = Query(None, description="Filter by name"),
    weight_class: str = Query(None, description="Filter by weight class"),
    school: str = Query(None, description="Filter by school name"),
    db = Depends(get_duckdb)
):
    """Get wrestlers from DuckDB"""
    try:
        with db:
            wrestlers = db.get_wrestlers(limit=limit, name_filter=name)
            
            # Apply additional filters
            if weight_class:
                wrestlers = [w for w in wrestlers if w.get('weight_class') == weight_class]
            
            if school:
                wrestlers = [w for w in wrestlers 
                           if school.lower() in (w.get('school_name', '') or '').lower()]
            
            # Convert to API format
            api_wrestlers = []
            for i, wrestler in enumerate(wrestlers):
                api_wrestler = {
                    "id": i + 1,
                    "first_name": (wrestler.get('first_name') or '').title(),
                    "last_name": (wrestler.get('last_name') or '').title(),
                    "weight_class": int(wrestler.get('weight_class', 125)) if wrestler.get('weight_class') and wrestler.get('weight_class').isdigit() else 125,
                    "year": "Senior",  # Default since DuckDB year is tournament year
                    "school_id": 1,  # Simplified for API compatibility
                    "school_name": (wrestler.get('school_name') or '').title(),
                    "wins": 15,  # Placeholder - would need to calculate from matches
                    "losses": 3,  # Placeholder
                    "person_id": wrestler.get('person_id'),
                    "seed": wrestler.get('seed')
                }
                api_wrestlers.append(api_wrestler)
            
            return api_wrestlers
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/wrestlers/{wrestler_id}", response_model=Dict[str, Any])
async def get_wrestler(
    wrestler_id: str,
    db = Depends(get_duckdb)
):
    """Get specific wrestler by person_id"""
    try:
        with db:
            wrestler_stats = db.get_wrestler_stats(wrestler_id)
            
            if not wrestler_stats:
                raise HTTPException(status_code=404, detail="Wrestler not found")
            
            # Convert to API format
            api_wrestler = {
                "id": 1,  # Simplified
                "person_id": wrestler_stats.get('person_id'),
                "first_name": (wrestler_stats.get('first_name') or '').title(),
                "last_name": (wrestler_stats.get('last_name') or '').title(),
                "weight_class": int(wrestler_stats.get('weight_class', 125)) if wrestler_stats.get('weight_class') and wrestler_stats.get('weight_class').isdigit() else 125,
                "year": "Senior",
                "school_name": (wrestler_stats.get('school_name') or '').title(),
                "school_location": wrestler_stats.get('school_location'),
                "wins": wrestler_stats.get('wins', 0),
                "losses": wrestler_stats.get('losses', 0),
                "total_matches": wrestler_stats.get('total_matches', 0),
                "falls": wrestler_stats.get('falls', 0),
                "decisions": wrestler_stats.get('decisions', 0),
                "forfeits": wrestler_stats.get('forfeits', 0)
            }
            
            return api_wrestler
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Schools endpoints
@router.get("/schools/", response_model=List[Dict[str, Any]])
async def get_schools(
    limit: int = Query(50, le=100, description="Maximum results"),
    name: str = Query(None, description="Filter by school name"),
    db = Depends(get_duckdb)
):
    """Get schools from DuckDB"""
    try:
        with db:
            if name:
                schools = db.search_schools(name, limit=limit)
            else:
                schools = db.get_schools(limit=limit)
            
            # Convert to API format
            api_schools = []
            for i, school in enumerate(schools):
                api_school = {
                    "id": i + 1,
                    "school_id": school.get('school_id'),
                    "name": (school.get('name') or '').title(),
                    "location": school.get('location') or 'Unknown',
                    "state": (school.get('location') or 'US')[:2].upper(),
                    "conference": "NCAA Division I",  # Default
                    "total_participants": school.get('total_participants', 0),
                    "years_active": school.get('years_active', 0),
                    "first_year": school.get('first_year'),
                    "last_year": school.get('last_year')
                }
                api_schools.append(api_school)
            
            return api_schools
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/schools/{school_id}", response_model=Dict[str, Any])
async def get_school(
    school_id: str,
    db = Depends(get_duckdb)
):
    """Get specific school by school_id"""
    try:
        with db:
            # Get school info
            schools = [s for s in db.get_schools(limit=1000) if s.get('school_id') == school_id]
            
            if not schools:
                raise HTTPException(status_code=404, detail="School not found")
            
            school = schools[0]
            
            # Get wrestlers for this school
            all_wrestlers = db.get_wrestlers(limit=1000)
            school_wrestlers = [w for w in all_wrestlers if w.get('school_name', '').lower() == school.get('name', '').lower()]
            
            api_school = {
                "id": 1,
                "school_id": school.get('school_id'),
                "name": (school.get('name') or '').title(),
                "location": school.get('location') or 'Unknown',
                "state": (school.get('location') or 'US')[:2].upper(),
                "conference": "NCAA Division I",
                "total_participants": school.get('total_participants', 0),
                "years_active": school.get('years_active', 0),
                "first_year": school.get('first_year'),
                "last_year": school.get('last_year'),
                "wrestlers_count": len(school_wrestlers),
                "wrestlers": school_wrestlers[:10]  # Sample of wrestlers
            }
            
            return api_school
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Tournaments endpoints
@router.get("/tournaments/", response_model=List[Dict[str, Any]])
async def get_tournaments(
    limit: int = Query(20, le=100, description="Maximum results"),
    year: int = Query(None, description="Filter by year"),
    db = Depends(get_duckdb)
):
    """Get tournaments from DuckDB"""
    try:
        with db:
            tournaments = db.get_tournaments(limit=limit)
            
            if year:
                tournaments = [t for t in tournaments if t.get('year') == year]
            
            # Convert to API format
            api_tournaments = []
            for i, tournament in enumerate(tournaments):
                api_tournament = {
                    "id": i + 1,
                    "tournament_id": tournament.get('tournament_id'),
                    "name": tournament.get('name') or f'Tournament {i+1}',
                    "year": tournament.get('year', 2024),
                    "location": tournament.get('location') or 'Unknown Location',
                    "total_matches": tournament.get('total_matches', 0),
                    "total_participants": tournament.get('total_participants', 0),
                    "division": "Division I"
                }
                api_tournaments.append(api_tournament)
            
            return api_tournaments
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Search endpoints
@router.get("/search/", response_model=Dict[str, Any])
async def search_all(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum results per category"),
    db = Depends(get_duckdb)
):
    """Search across wrestlers and schools"""
    try:
        with db:
            # Search wrestlers
            wrestlers = db.search_wrestlers(q, limit=limit)
            wrestler_results = []
            for wrestler in wrestlers:
                wrestler_results.append({
                    "type": "wrestler",
                    "id": wrestler.get('person_id'),
                    "name": f"{wrestler.get('first_name', '')} {wrestler.get('last_name', '')}".strip(),
                    "additional_info": f"{wrestler.get('school_name', 'Unknown School')} - {wrestler.get('weight_class', 'N/A')}lbs",
                    "weight_class": wrestler.get('weight_class'),
                    "school_name": wrestler.get('school_name')
                })
            
            # Search schools
            schools = db.search_schools(q, limit=limit)
            school_results = []
            for school in schools:
                school_results.append({
                    "type": "school",
                    "id": school.get('school_id'),
                    "name": school.get('name', ''),
                    "additional_info": f"{school.get('location', 'Unknown Location')} - {school.get('total_participants', 0)} participants",
                    "location": school.get('location'),
                    "total_participants": school.get('total_participants', 0)
                })
            
            return {
                "query": q,
                "wrestlers": wrestler_results,
                "schools": school_results,
                "coaches": []  # Not implemented yet
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/search/wrestlers/", response_model=List[Dict[str, Any]])
async def search_wrestlers(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db = Depends(get_duckdb)
):
    """Search wrestlers specifically"""
    try:
        with db:
            wrestlers = db.search_wrestlers(q, limit=limit)
            
            results = []
            for wrestler in wrestlers:
                results.append({
                    "id": wrestler.get('person_id'),
                    "name": f"{wrestler.get('first_name', '')} {wrestler.get('last_name', '')}".strip(),
                    "weight_class": wrestler.get('weight_class'),
                    "year": wrestler.get('year'),
                    "school": wrestler.get('school_name'),
                    "school_location": wrestler.get('school_location')
                })
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/search/schools/", response_model=List[Dict[str, Any]])
async def search_schools(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db = Depends(get_duckdb)
):
    """Search schools specifically"""
    try:
        with db:
            schools = db.search_schools(q, limit=limit)
            
            results = []
            for school in schools:
                results.append({
                    "id": school.get('school_id'),
                    "name": school.get('name'),
                    "location": school.get('location'),
                    "total_participants": school.get('total_participants', 0)
                })
            
            return results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Utility endpoints
@router.get("/weight-classes/", response_model=List[str])
async def get_weight_classes(db = Depends(get_duckdb)):
    """Get all weight classes available in the database"""
    try:
        with db:
            return db.get_weight_classes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/years/", response_model=List[int])
async def get_years(db = Depends(get_duckdb)):
    """Get all years available in the database"""
    try:
        with db:
            return db.get_years()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/stats/", response_model=Dict[str, Any])
async def get_database_stats(db = Depends(get_duckdb)):
    """Get overall database statistics"""
    try:
        with db:
            stats = {
                "total_wrestlers": len(db.get_wrestlers(limit=10000)),
                "total_schools": len(db.get_schools(limit=1000)),
                "total_tournaments": len(db.get_tournaments(limit=1000)),
                "weight_classes": db.get_weight_classes(),
                "years_span": {
                    "earliest": min(db.get_years()) if db.get_years() else None,
                    "latest": max(db.get_years()) if db.get_years() else None
                }
            }
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Add compatibility endpoints for frontend
@router.get("/wrestlers/{wrestler_id}/stats/")
async def get_wrestler_stats(wrestler_id: str, db = Depends(get_duckdb)):
    """Get wrestler statistics - compatibility endpoint"""
    try:
        with db:
            # Get basic wrestler info
            wrestler = db.get_wrestler_by_id(wrestler_id)
            if not wrestler:
                raise HTTPException(status_code=404, detail="Wrestler not found")
            
            # Calculate basic stats from available data
            stats = {
                "total_matches": wrestler.get("total_matches", 0),
                "wins": wrestler.get("wins", 0), 
                "losses": wrestler.get("losses", 0),
                "win_percentage": wrestler.get("win_percentage", 0.0),
                "weight_class": wrestler.get("weight_class"),
                "years_active": 1,  # Placeholder
                "tournaments": 1,   # Placeholder
            }
            
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schools/{school_id}/stats/")
async def get_school_stats(school_id: str, db = Depends(get_duckdb)):
    """Get school statistics - compatibility endpoint"""
    try:
        with db:
            school = db.get_school_by_id(school_id)
            if not school:
                raise HTTPException(status_code=404, detail="School not found")
            
            stats = {
                "total_wrestlers": school.get("total_participants", 0),
                "total_matches": 0,  # Placeholder
                "championships": 0,  # Placeholder
                "years_active": school.get("years_active", 0),
                "first_year": school.get("first_year"),
                "last_year": school.get("last_year"),
            }
            
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brackets/tournament/{tournament_id}/")
async def get_tournament_brackets(tournament_id: str, db = Depends(get_duckdb)):
    """Get tournament brackets - placeholder for compatibility"""
    # This would require complex bracket generation from match data
    # For now, return a placeholder response
    return {
        "tournament_id": tournament_id,
        "brackets": [],
        "message": "Bracket visualization not yet implemented for DuckDB"
    }

@router.get("/coaches/")
async def get_coaches(db = Depends(get_duckdb)):
    """Get coaches - placeholder for compatibility"""
    # DuckDB doesn't have coach data separate from person/role
    return []

# Frontend-compatible endpoints (without /duckdb prefix)
@router.get("/wrestlers", response_model=List[dict])
async def get_wrestlers_frontend_compatible(
    limit: int = Query(20, le=100, description="Maximum results"),
    name: str = Query(None, description="Filter by name"),
    weight_class: str = Query(None, description="Filter by weight class"),
    school: str = Query(None, description="Filter by school name"),
    db = Depends(get_duckdb)
):
    """Get wrestlers (frontend compatible endpoint)"""
    try:
        with db:
            wrestlers = db.get_wrestlers(limit=limit, name_filter=name)
            return [format_wrestler_for_api(w) for w in wrestlers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/wrestlers/{wrestler_id}", response_model=dict)
async def get_wrestler_by_id_frontend_compatible(
    wrestler_id: str,
    db = Depends(get_duckdb)
):
    """Get specific wrestler by ID (frontend compatible)"""
    try:
        with db:
            wrestler = db.get_wrestler_by_id(wrestler_id)
            if not wrestler:
                raise HTTPException(status_code=404, detail="Wrestler not found")
            return format_wrestler_for_api(wrestler)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/wrestlers/{wrestler_id}/stats", response_model=dict)
async def get_wrestler_stats_frontend_compatible(
    wrestler_id: str,
    db = Depends(get_duckdb)
):
    """Get wrestler statistics (frontend compatible)"""
    try:
        with db:
            # Get wrestler basic info
            wrestler = db.get_wrestler_by_id(wrestler_id)
            if not wrestler:
                raise HTTPException(status_code=404, detail="Wrestler not found")
            
            # Get match statistics from participant_match table
            stats_query = """
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN is_winner = true THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN is_winner = false THEN 1 ELSE 0 END) as losses,
                COUNT(DISTINCT result_type) as different_result_types,
                array_agg(DISTINCT result_type) as result_types
            FROM participant_match pm
            JOIN participant p ON pm.participant_id = p.participant_id
            JOIN role r ON p.role_id = r.role_id
            WHERE r.person_id = ?
            """
            
            stats_result = db.execute_query(stats_query.replace('?', f"'{wrestler_id}'"))
            stats = stats_result[0] if stats_result else {}
            
            return {
                "wrestler_id": wrestler_id,
                "name": f"{wrestler.get('first_name', '')} {wrestler.get('last_name', '')}".strip(),
                "total_matches": stats.get('total_matches', 0),
                "wins": stats.get('wins', 0), 
                "losses": stats.get('losses', 0),
                "win_percentage": round((stats.get('wins', 0) / max(stats.get('total_matches', 1), 1)) * 100, 1),
                "result_types": stats.get('result_types', [])
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/schools", response_model=List[dict])
async def get_schools_frontend_compatible(
    limit: int = Query(20, le=100, description="Maximum results"),
    name: str = Query(None, description="Filter by name"),
    db = Depends(get_duckdb)
):
    """Get schools (frontend compatible endpoint)"""
    try:
        with db:
            schools = db.get_schools(limit=limit, name_filter=name)
            return [format_school_for_api(school) for school in schools]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/schools/{school_id}", response_model=dict)
async def get_school_by_id_frontend_compatible(
    school_id: str,
    db = Depends(get_duckdb)
):
    """Get specific school by ID (frontend compatible)"""
    try:
        with db:
            school = db.get_school_by_id(school_id)
            if not school:
                raise HTTPException(status_code=404, detail="School not found")
            return format_school_for_api(school)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/schools/{school_id}/stats", response_model=dict)
async def get_school_stats_frontend_compatible(
    school_id: str,
    db = Depends(get_duckdb)
):
    """Get school statistics (frontend compatible)"""
    try:
        with db:
            school = db.get_school_by_id(school_id)
            if not school:
                raise HTTPException(status_code=404, detail="School not found")
            
            # Get detailed school statistics
            stats_query = """
            SELECT 
                COUNT(DISTINCT p.participant_id) as total_wrestlers,
                COUNT(DISTINCT p.year) as years_competed,
                MIN(p.year) as first_year,
                MAX(p.year) as last_year,
                COUNT(DISTINCT p.weight_class) as weight_classes_competed,
                COUNT(CASE WHEN pm.is_winner = true THEN 1 END) as total_wins,
                COUNT(CASE WHEN pm.is_winner = false THEN 1 END) as total_losses
            FROM participant p
            LEFT JOIN participant_match pm ON p.participant_id = pm.participant_id
            WHERE p.school_id = ?
            """
            
            stats_result = db.execute_query(stats_query.replace('?', f"'{school_id}'"))
            stats = stats_result[0] if stats_result else {}
            
            return {
                "school_id": school_id,
                "name": school.get('name', ''),
                "total_wrestlers": stats.get('total_wrestlers', 0),
                "years_competed": stats.get('years_competed', 0),
                "first_year": stats.get('first_year'),
                "last_year": stats.get('last_year'),
                "weight_classes_competed": stats.get('weight_classes_competed', 0),
                "total_wins": stats.get('total_wins', 0),
                "total_losses": stats.get('total_losses', 0),
                "win_percentage": round((stats.get('total_wins', 0) / max(stats.get('total_wins', 0) + stats.get('total_losses', 0), 1)) * 100, 1)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/tournaments", response_model=List[dict])
async def get_tournaments_frontend_compatible(
    limit: int = Query(20, le=100, description="Maximum results"),
    year: int = Query(None, description="Filter by year"),
    db = Depends(get_duckdb)
):
    """Get tournaments (frontend compatible endpoint)"""
    try:
        with db:
            tournaments = db.get_tournaments(limit=limit, year_filter=year)
            return [format_tournament_for_api(tournament) for tournament in tournaments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/tournaments/{tournament_id}", response_model=dict)
async def get_tournament_by_id_frontend_compatible(
    tournament_id: str,
    db = Depends(get_duckdb)
):
    """Get specific tournament by ID (frontend compatible)"""
    try:
        with db:
            tournament = db.get_tournament_by_id(tournament_id)
            if not tournament:
                raise HTTPException(status_code=404, detail="Tournament not found")
            return format_tournament_for_api(tournament)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/search", response_model=dict)
async def search_all_frontend_compatible(
    q: str = Query(..., description="Search query"),
    db = Depends(get_duckdb)
):
    """Global search (frontend compatible)"""
    try:
        with db:
            wrestlers = db.search_wrestlers(q, limit=10)
            schools = db.search_schools(q, limit=10)
            
            return {
                "query": q,
                "wrestlers": wrestlers,
                "schools": schools,
                "coaches": []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
