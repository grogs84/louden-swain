"""
Wrestlers API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from ..database import get_db, Database
from ..models import WrestlerProfile, WrestlerStats, WrestlerMatch

router = APIRouter()

@router.get("/wrestlers", response_model=List[WrestlerProfile])
async def get_wrestlers(
    limit: int = Query(20, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    name: Optional[str] = Query(None, description="Filter by wrestler name"),
    school: Optional[str] = Query(None, description="Filter by school name"),
    weight_class: Optional[str] = Query(None, description="Filter by weight class"),
    db: Database = Depends(get_db)
):
    """Get wrestlers with optional filtering"""
    query = """
    SELECT DISTINCT 
        p.id,
        p.first_name,
        p.last_name,
        s.name as school_name,
        s.location as school_location
    FROM people p
    LEFT JOIN participants pt ON p.id = pt.person_id
    LEFT JOIN schools s ON pt.school_id = s.id
    WHERE 1=1
    """
    params = []
    
    if name:
        query += " AND (p.first_name ILIKE $" + str(len(params) + 1) + " OR p.last_name ILIKE $" + str(len(params) + 1) + ")"
        params.append(f"%{name}%")
    
    if school:
        query += " AND s.name ILIKE $" + str(len(params) + 1)
        params.append(f"%{school}%")
    
    if weight_class:
        query += " AND pt.weight_class = $" + str(len(params) + 1)
        params.append(weight_class)
    
    query += f" ORDER BY p.last_name, p.first_name LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])
    
    rows = await db.fetch_all(query, *params)
    return rows

@router.get("/wrestlers/{wrestler_id}", response_model=WrestlerProfile)
async def get_wrestler(
    wrestler_id: UUID,
    db: Database = Depends(get_db)
):
    """Get wrestler by ID"""
    query = """
    SELECT 
        p.id,
        p.first_name,
        p.last_name,
        s.name as school_name,
        s.location as school_location
    FROM people p
    LEFT JOIN participants pt ON p.id = pt.person_id
    LEFT JOIN schools s ON pt.school_id = s.id
    WHERE p.id = $1
    LIMIT 1
    """
    
    wrestler = await db.fetch_one(query, wrestler_id)
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    return wrestler

@router.get("/wrestlers/{wrestler_id}/stats", response_model=WrestlerStats)
async def get_wrestler_stats(
    wrestler_id: UUID,
    db: Database = Depends(get_db)
):
    """Get wrestler statistics"""
    query = """
    WITH wrestler_matches AS (
        SELECT 
            CASE 
                WHEN m.winner_id = pt.id THEN 'W'
                WHEN m.loser_id = pt.id THEN 'L'
            END as result,
            m.match_result
        FROM participants pt
        LEFT JOIN matches m ON (pt.id = m.winner_id OR pt.id = m.loser_id)
        WHERE pt.person_id = $1 AND m.id IS NOT NULL
    )
    SELECT 
        COUNT(*) as total_matches,
        COUNT(CASE WHEN result = 'W' THEN 1 END) as wins,
        COUNT(CASE WHEN result = 'L' THEN 1 END) as losses,
        COUNT(CASE WHEN result = 'W' AND match_result = 'Fall' THEN 1 END) as pins,
        COUNT(CASE WHEN result = 'W' AND match_result = 'Tech Fall' THEN 1 END) as tech_falls,
        COUNT(CASE WHEN result = 'W' AND match_result = 'Major Decision' THEN 1 END) as major_decisions
    FROM wrestler_matches
    """
    
    stats = await db.fetch_one(query, wrestler_id)
    if not stats:
        stats = {
            "total_matches": 0, "wins": 0, "losses": 0,
            "pins": 0, "tech_falls": 0, "major_decisions": 0
        }
    
    # Calculate win percentage
    total = stats["total_matches"] or 0
    wins = stats["wins"] or 0
    win_percentage = (wins / total * 100) if total > 0 else 0.0
    
    return {
        "wrestler_id": wrestler_id,
        "total_matches": total,
        "wins": wins,
        "losses": stats["losses"] or 0,
        "pins": stats["pins"] or 0,
        "tech_falls": stats["tech_falls"] or 0,
        "major_decisions": stats["major_decisions"] or 0,
        "win_percentage": round(win_percentage, 1)
    }

@router.get("/wrestlers/{wrestler_id}/matches", response_model=List[WrestlerMatch])
async def get_wrestler_matches(
    wrestler_id: UUID,
    limit: int = Query(100, le=500, description="Maximum number of matches"),
    db: Database = Depends(get_db)
):
    """Get wrestler's match history"""
    query = """
    SELECT 
        m.id,
        CASE 
            WHEN m.winner_id = pt.id THEN op_p.first_name
            ELSE winner_p.first_name
        END as opponent_first_name,
        CASE 
            WHEN m.winner_id = pt.id THEN op_p.last_name
            ELSE winner_p.last_name
        END as opponent_last_name,
        CASE 
            WHEN m.winner_id = pt.id THEN op_s.name
            ELSE winner_s.name
        END as opponent_school,
        CASE 
            WHEN m.winner_id = pt.id THEN 'W'
            ELSE 'L'
        END as result,
        m.match_result as decision,
        m.score,
        t.name as tournament_name,
        m.round,
        t.year,
        m.weight_class
    FROM participants pt
    JOIN matches m ON (pt.id = m.winner_id OR pt.id = m.loser_id)
    JOIN tournaments t ON m.tournament_id = t.id
    LEFT JOIN participants winner_pt ON m.winner_id = winner_pt.id
    LEFT JOIN participants loser_pt ON m.loser_id = loser_pt.id
    LEFT JOIN people winner_p ON winner_pt.person_id = winner_p.id
    LEFT JOIN people op_p ON loser_pt.person_id = op_p.id
    LEFT JOIN schools winner_s ON winner_pt.school_id = winner_s.id
    LEFT JOIN schools op_s ON loser_pt.school_id = op_s.id
    WHERE pt.person_id = $1
    ORDER BY t.year ASC, m.round
    LIMIT $2
    """
    
    matches = await db.fetch_all(query, wrestler_id, limit)
    return matches
