from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database.database import get_db
from app.models.models import Tournament as TournamentModel
from app.models.schemas import Tournament, TournamentCreate

router = APIRouter()

@router.get("/", response_model=List[Tournament])
async def get_tournaments(
    skip: int = 0,
    limit: int = 100,
    year: int = None,
    division: str = None,
    db: AsyncSession = Depends(get_db)
):
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
    query = select(TournamentModel).where(TournamentModel.id == tournament_id)
    result = await db.execute(query)
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    return tournament

@router.post("/", response_model=Tournament, status_code=status.HTTP_201_CREATED)
async def create_tournament(tournament: TournamentCreate, db: AsyncSession = Depends(get_db)):
    db_tournament = TournamentModel(**tournament.dict())
    db.add(db_tournament)
    await db.commit()
    await db.refresh(db_tournament)
    return db_tournament
