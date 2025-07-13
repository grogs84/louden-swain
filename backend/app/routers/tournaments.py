from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database.database import get_db
from app.models.models import Tournament as TournamentModel
from app.models.schemas import Tournament, TournamentCreate, TournamentUpdate

router = APIRouter()

@router.get("/", response_model=List[Tournament])
async def get_tournaments(
    skip: int = 0,
    limit: int = 100,
    year: Optional[int] = None,
    division: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all tournaments with optional filtering"""
    query = select(TournamentModel)
    
    if year:
        query = query.where(TournamentModel.year == year)
    if division:
        query = query.where(TournamentModel.division == division)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tournaments = result.scalars().all()
    return tournaments

@router.get("/{tournament_id}", response_model=Tournament)
async def get_tournament(tournament_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific tournament by ID"""
    query = select(TournamentModel).where(TournamentModel.id == tournament_id)
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    return tournament

@router.post("/", response_model=Tournament, status_code=status.HTTP_201_CREATED)
async def create_tournament(tournament: TournamentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new tournament"""
    db_tournament = TournamentModel(**tournament.dict())
    db.add(db_tournament)
    await db.commit()
    await db.refresh(db_tournament)
    return db_tournament

@router.put("/{tournament_id}", response_model=Tournament)
async def update_tournament(
    tournament_id: int,
    tournament_update: TournamentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a tournament"""
    query = select(TournamentModel).where(TournamentModel.id == tournament_id)
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    update_data = tournament_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tournament, field, value)
    
    await db.commit()
    await db.refresh(tournament)
    return tournament

@router.delete("/{tournament_id}")
async def delete_tournament(tournament_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a tournament"""
    query = select(TournamentModel).where(TournamentModel.id == tournament_id)
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    await db.delete(tournament)
    await db.commit()
    return {"message": "Tournament deleted successfully"}

@router.get("/{tournament_id}/brackets")
async def get_tournament_brackets(tournament_id: int, db: AsyncSession = Depends(get_db)):
    """Get bracket data for a tournament"""
    from app.models.models import Bracket as BracketModel, Match as MatchModel
    
    # First verify tournament exists
    tournament_query = select(TournamentModel).where(TournamentModel.id == tournament_id)
    tournament_result = await db.execute(tournament_query)
    tournament = tournament_result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    # Get brackets for this tournament
    brackets_query = select(BracketModel).where(BracketModel.tournament_id == tournament_id)
    brackets_result = await db.execute(brackets_query)
    brackets = brackets_result.scalars().all()
    
    # Get matches for this tournament  
    matches_query = select(MatchModel).where(MatchModel.bracket_id.in_([b.id for b in brackets]))
    matches_result = await db.execute(matches_query)
    matches = matches_result.scalars().all()
    
    # Organize data by weight class
    bracket_data = {}
    for bracket in brackets:
        weight_class = bracket.weight_class
        if weight_class not in bracket_data:
            bracket_data[weight_class] = {
                "weight_class": weight_class,
                "bracket_id": bracket.id,
                "matches": []
            }
        
        # Add matches for this bracket
        bracket_matches = [m for m in matches if m.bracket_id == bracket.id]
        bracket_data[weight_class]["matches"] = [
            {
                "id": match.id,
                "wrestler1_id": match.wrestler1_id,
                "wrestler2_id": match.wrestler2_id,
                "winner_id": match.winner_id,
                "round_name": match.round_name,
                "match_number": match.match_number,
                "score": match.score
            } for match in bracket_matches
        ]
    
    return {
        "tournament_id": tournament_id,
        "tournament_name": tournament.name,
        "year": tournament.year,
        "brackets": list(bracket_data.values())
    }
