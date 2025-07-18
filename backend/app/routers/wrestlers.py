from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional, Union, Dict, Any
from app.database.database import get_db

router = APIRouter()

def title_case_name(name: str) -> str:
    """Apply title case formatting to names (updated for Supabase - simplified)"""
    if not name:
        return name
    
    # Simple title case for now
    return ' '.join(word.capitalize() for word in name.split())

@router.get("/", response_model=List[Dict[str, Any]])
async def get_wrestlers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all wrestlers with basic info only"""
    
    # Simple query that should work fast
    query = text("""
        SELECT 
            p.person_id,
            p.first_name,
            p.last_name
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        WHERE r.role_type = 'wrestler'
        ORDER BY p.last_name, p.first_name
        OFFSET :offset LIMIT :limit
    """)
    
    result = await db.execute(query, {"offset": skip, "limit": limit})
    wrestlers = result.fetchall()
    
    return [
        {
            "id": wrestler.person_id,
            "person_id": wrestler.person_id,
            "first_name": title_case_name(wrestler.first_name),
            "last_name": title_case_name(wrestler.last_name),
            "weight_class": None,
            "year": None,
            "school": None
        }
        for wrestler in wrestlers
    ]

@router.get("/{wrestler_id}", response_model=Dict[str, Any])
async def get_wrestler(
    wrestler_id: Union[int, str],
    db: AsyncSession = Depends(get_db)
):
    """Get a specific wrestler by ID with basic info only"""
    
    # Simple query for basic wrestler info
    query = text("""
        SELECT 
            p.person_id,
            p.first_name,
            p.last_name
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        WHERE r.role_type = 'wrestler' AND p.person_id = :wrestler_id
        LIMIT 1
    """)
    
    result = await db.execute(query, {"wrestler_id": wrestler_id})
    wrestler = result.fetchone()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    return {
        "id": wrestler.person_id,
        "person_id": wrestler.person_id,
        "first_name": title_case_name(wrestler.first_name),
        "last_name": title_case_name(wrestler.last_name),
        "weight_class": None,
        "year": None,
        "school": None,
        "stats": {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_percentage": 0
        },
        "matches": []
    }

@router.get("/{wrestler_id}/stats", response_model=Dict[str, Any])
async def get_wrestler_stats(
    wrestler_id: Union[int, str],
    db: AsyncSession = Depends(get_db)
):
    """Get wrestler statistics"""
    
    # Simple stats query
    query = text("""
        SELECT 
            COUNT(*) as total_matches,
            COUNT(CASE WHEN mr.winner_role_id = r.role_id THEN 1 END) as wins
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        JOIN participant pt ON r.role_id = pt.role_id
        JOIN match m ON (pt.role_id = m.participant1_role_id OR pt.role_id = m.participant2_role_id)
        LEFT JOIN match_result mr ON m.match_id = mr.match_id
        WHERE r.role_type = 'wrestler' AND p.person_id = :wrestler_id
    """)
    
    result = await db.execute(query, {"wrestler_id": wrestler_id})
    stats = result.fetchone()
    
    if not stats:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    total_matches = stats.total_matches or 0
    wins = stats.wins or 0
    losses = total_matches - wins
    win_percentage = round((wins / total_matches * 100), 1) if total_matches > 0 else 0
    
    return {
        "total_matches": total_matches,
        "wins": wins,
        "losses": losses,
        "win_percentage": win_percentage
    }

@router.get("/{wrestler_id}/matches", response_model=List[Dict[str, Any]])
async def get_wrestler_matches(
    wrestler_id: Union[int, str],
    limit: int = 10,
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get wrestler match history"""
    
    # Simple matches query
    query = text("""
        SELECT 
            m.match_id,
            m.year,
            t.name as tournament_name,
            CASE 
                WHEN mr.winner_role_id = r.role_id THEN 'W'
                WHEN mr.winner_role_id IS NOT NULL THEN 'L'
                ELSE 'N/A'
            END as result,
            CASE 
                WHEN mr.winner_role_id = r.role_id THEN
                    COALESCE(mr.winner_score, 0) || '-' || COALESCE(mr.loser_score, 0)
                WHEN mr.winner_role_id IS NOT NULL THEN
                    COALESCE(mr.loser_score, 0) || '-' || COALESCE(mr.winner_score, 0)
                ELSE 'N/A'
            END as score,
            COALESCE(mr.result_type, 'decision') as result_type
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        JOIN participant pt ON r.role_id = pt.role_id
        JOIN match m ON (pt.role_id = m.participant1_role_id OR pt.role_id = m.participant2_role_id)
        LEFT JOIN match_result mr ON m.match_id = mr.match_id
        LEFT JOIN tournament t ON m.tournament_id = t.tournament_id
        WHERE r.role_type = 'wrestler' AND p.person_id = :wrestler_id
        ORDER BY m.year DESC, m.match_id DESC
        OFFSET :offset LIMIT :limit
    """)
    
    result = await db.execute(query, {"wrestler_id": wrestler_id, "offset": skip, "limit": limit})
    matches = result.fetchall()
    
    return [
        {
            "match_id": match.match_id,
            "year": match.year,
            "tournament": {
                "name": title_case_name(match.tournament_name) if match.tournament_name else "Unknown Tournament"
            },
            "result": match.result,
            "score": match.score,
            "result_type": match.result_type.replace('_', ' ').title() if match.result_type else 'Decision',
            "opponent": {
                "first_name": "Unknown",
                "last_name": "Opponent",
                "school": {"name": "Unknown School"}
            }
        }
        for match in matches
    ]
