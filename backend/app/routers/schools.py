"""
Schools API endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import Database, get_db
from ..models import School, SchoolStats, WrestlerProfile

router = APIRouter()


@router.get("/schools", response_model=List[School])
async def get_schools(
    limit: int = Query(20, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    name: Optional[str] = Query(None, description="Filter by school name"),
    state: Optional[str] = Query(None, description="Filter by state"),
    db: Database = Depends(get_db),
):
    """Get schools with optional filtering"""
    query = "SELECT id, name, location, state FROM schools WHERE 1=1"
    params = []

    if name:
        query += " AND name ILIKE $" + str(len(params) + 1)
        params.append(f"%{name}%")

    if state:
        query += " AND state ILIKE $" + str(len(params) + 1)
        params.append(f"%{state}%")

    query += f" ORDER BY name LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])

    rows = await db.fetch_all(query, *params)
    return rows


@router.get("/schools/{school_id}", response_model=School)
async def get_school(school_id: UUID, db: Database = Depends(get_db)):
    """Get school by ID"""
    query = "SELECT id, name, location, state FROM schools WHERE id = $1"

    school = await db.fetch_one(query, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    return school


@router.get("/schools/{school_id}/stats", response_model=SchoolStats)
async def get_school_stats(school_id: UUID, db: Database = Depends(get_db)):
    """Get school statistics"""
    query = """
    WITH school_data AS (
        SELECT
            pt.person_id,
            pt.year,
            CASE
                WHEN m.winner_id = pt.id THEN 'W'
                WHEN m.loser_id = pt.id THEN 'L'
            END as result
        FROM participants pt
        LEFT JOIN matches m ON (pt.id = m.winner_id OR pt.id = m.loser_id)
        WHERE pt.school_id = $1
    )
    SELECT
        COUNT(DISTINCT person_id) as total_wrestlers,
        COUNT(*) as total_matches,
        COUNT(CASE WHEN result = 'W' THEN 1 END) as total_wins,
        COUNT(CASE WHEN result = 'L' THEN 1 END) as total_losses,
        COUNT(DISTINCT year) as years_active,
        MIN(year) as first_year,
        MAX(year) as last_year
    FROM school_data
    WHERE result IS NOT NULL
    """

    stats = await db.fetch_one(query, school_id)
    if not stats:
        stats = {
            "total_wrestlers": 0,
            "total_matches": 0,
            "total_wins": 0,
            "total_losses": 0,
            "years_active": 0,
            "first_year": None,
            "last_year": None,
        }

    # Calculate win percentage
    total_games = (stats["total_wins"] or 0) + (stats["total_losses"] or 0)
    wins = stats["total_wins"] or 0
    win_percentage = (wins / total_games * 100) if total_games > 0 else 0.0

    return {
        "school_id": school_id,
        "total_wrestlers": stats["total_wrestlers"] or 0,
        "total_matches": stats["total_matches"] or 0,
        "total_wins": wins,
        "total_losses": stats["total_losses"] or 0,
        "years_active": stats["years_active"] or 0,
        "first_year": stats["first_year"],
        "last_year": stats["last_year"],
        "win_percentage": round(win_percentage, 1),
    }


@router.get("/schools/{school_id}/wrestlers", response_model=List[WrestlerProfile])
async def get_school_wrestlers(
    school_id: UUID,
    limit: int = Query(50, le=200, description="Maximum number of wrestlers"),
    db: Database = Depends(get_db),
):
    """Get wrestlers from a specific school"""
    query = """
    SELECT DISTINCT
        p.id,
        p.first_name,
        p.last_name,
        s.name as school_name,
        s.location as school_location
    FROM people p
    JOIN participants pt ON p.id = pt.person_id
    JOIN schools s ON pt.school_id = s.id
    WHERE pt.school_id = $1
    ORDER BY p.last_name, p.first_name
    LIMIT $2
    """

    wrestlers = await db.fetch_all(query, school_id, limit)
    return wrestlers
