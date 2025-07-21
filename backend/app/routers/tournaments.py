"""
Tournaments API endpoints
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import Database, get_db
from ..models import Tournament

router = APIRouter()


@router.get("/tournaments", response_model=List[Tournament])
async def get_tournaments(
    limit: int = Query(20, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    year: Optional[int] = Query(None, description="Filter by year"),
    name: Optional[str] = Query(None, description="Filter by tournament name"),
    db: Database = Depends(get_db),
):
    """Get tournaments with optional filtering"""
    query = "SELECT id, name, year, location, division FROM tournaments WHERE 1=1"
    params = []

    if year:
        query += " AND year = $" + str(len(params) + 1)
        params.append(year)

    if name:
        query += " AND name ILIKE $" + str(len(params) + 1)
        params.append(f"%{name}%")

    query += (
        f" ORDER BY year DESC, name LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    )
    params.extend([limit, offset])

    rows = await db.fetch_all(query, *params)
    return rows


@router.get("/tournaments/{tournament_id}", response_model=Tournament)
async def get_tournament(tournament_id: UUID, db: Database = Depends(get_db)):
    """Get tournament by ID"""
    query = "SELECT id, name, year, location, division FROM tournaments WHERE id = $1"

    tournament = await db.fetch_one(query, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return tournament


@router.get("/tournaments/{tournament_id}/brackets")
async def get_tournament_brackets(
    tournament_id: UUID,
    weight_class: Optional[str] = Query(None, description="Filter by weight class"),
    db: Database = Depends(get_db),
):
    """Get tournament brackets (simplified structure for now)"""
    query = """
    SELECT
        m.id,
        m.round,
        m.weight_class,
        winner_p.first_name || ' ' || winner_p.last_name as winner_name,
        loser_p.first_name || ' ' || loser_p.last_name as loser_name,
        winner_s.name as winner_school,
        loser_s.name as loser_school,
        m.match_result,
        m.score
    FROM matches m
    JOIN participants winner_pt ON m.winner_id = winner_pt.id
    JOIN participants loser_pt ON m.loser_id = loser_pt.id
    JOIN people winner_p ON winner_pt.person_id = winner_p.id
    JOIN people loser_p ON loser_pt.person_id = loser_p.id
    JOIN schools winner_s ON winner_pt.school_id = winner_s.id
    JOIN schools loser_s ON loser_pt.school_id = loser_s.id
    WHERE m.tournament_id = $1
    """
    params = [tournament_id]

    if weight_class:
        query += " AND m.weight_class = $2"
        params.append(weight_class)

    query += " ORDER BY m.weight_class, m.round"

    matches = await db.fetch_all(query, *params)

    # Group by weight class
    brackets = {}
    for match in matches:
        wc = match["weight_class"] or "Unknown"
        if wc not in brackets:
            brackets[wc] = []
        brackets[wc].append(match)

    return {"tournament_id": tournament_id, "brackets": brackets}
