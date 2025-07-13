from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from app.database.database import get_db
from app.models.models import Coach as CoachModel
from app.models.schemas import Coach, CoachCreate, CoachUpdate, CoachWithSchool

router = APIRouter()

@router.get("/", response_model=List[CoachWithSchool])
async def get_coaches(
    skip: int = 0,
    limit: int = 100,
    school_id: int = None,
    position: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(CoachModel).options(selectinload(CoachModel.school))
    
    if school_id:
        query = query.where(CoachModel.school_id == school_id)
    if position:
        query = query.where(CoachModel.position == position)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    coaches = result.scalars().all()
    return coaches

@router.get("/{coach_id}", response_model=CoachWithSchool)
async def get_coach(coach_id: int, db: AsyncSession = Depends(get_db)):
    query = select(CoachModel).options(selectinload(CoachModel.school)).where(CoachModel.id == coach_id)
    result = await db.execute(query)
    coach = result.scalar_one_or_none()
    
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    return coach

@router.post("/", response_model=Coach, status_code=status.HTTP_201_CREATED)
async def create_coach(coach: CoachCreate, db: AsyncSession = Depends(get_db)):
    db_coach = CoachModel(**coach.dict())
    db.add(db_coach)
    await db.commit()
    await db.refresh(db_coach)
    return db_coach

@router.put("/{coach_id}", response_model=Coach)
async def update_coach(
    coach_id: int,
    coach_update: CoachUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(CoachModel).where(CoachModel.id == coach_id)
    result = await db.execute(query)
    coach = result.scalar_one_or_none()
    
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    update_data = coach_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(coach, field, value)
    
    await db.commit()
    await db.refresh(coach)
    return coach

@router.delete("/{coach_id}")
async def delete_coach(coach_id: int, db: AsyncSession = Depends(get_db)):
    query = select(CoachModel).where(CoachModel.id == coach_id)
    result = await db.execute(query)
    coach = result.scalar_one_or_none()
    
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    await db.delete(coach)
    await db.commit()
    return {"message": "Coach deleted successfully"}
