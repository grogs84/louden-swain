from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
import json
from app.database.database import get_db
from app.models.models import Bracket as BracketModel, Tournament as TournamentModel
from app.models.schemas import Bracket, BracketCreate, BracketWithTournament

router = APIRouter()

@router.get("/tournament/{tournament_id}", response_model=List[BracketWithTournament])
async def get_tournament_brackets(tournament_id: int, db: AsyncSession = Depends(get_db)):
    query = select(BracketModel).options(selectinload(BracketModel.tournament)).where(BracketModel.tournament_id == tournament_id)
    result = await db.execute(query)
    brackets = result.scalars().all()
    return brackets

@router.get("/{bracket_id}", response_model=BracketWithTournament)
async def get_bracket(bracket_id: int, db: AsyncSession = Depends(get_db)):
    query = select(BracketModel).options(selectinload(BracketModel.tournament)).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    return bracket

@router.get("/{bracket_id}/data")
async def get_bracket_data(bracket_id: int, db: AsyncSession = Depends(get_db)):
    """Get bracket data formatted for react-brackets"""
    query = select(BracketModel).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    if bracket.bracket_data:
        try:
            return json.loads(bracket.bracket_data)
        except json.JSONDecodeError:
            return {"error": "Invalid bracket data format"}
    
    # Return empty bracket structure if no data exists
    return {
        "rounds": [],
        "weight_class": bracket.weight_class,
        "tournament_id": bracket.tournament_id
    }

@router.post("/", response_model=Bracket, status_code=status.HTTP_201_CREATED)
async def create_bracket(bracket: BracketCreate, db: AsyncSession = Depends(get_db)):
    db_bracket = BracketModel(**bracket.dict())
    db.add(db_bracket)
    await db.commit()
    await db.refresh(db_bracket)
    return db_bracket

@router.put("/{bracket_id}/data")
async def update_bracket_data(
    bracket_id: int,
    bracket_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update bracket data (for react-brackets format)"""
    query = select(BracketModel).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    bracket.bracket_data = json.dumps(bracket_data)
    await db.commit()
    await db.refresh(bracket)
    
    return {"message": "Bracket data updated successfully"}
