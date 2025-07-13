from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database.database import get_db
from app.models.models import Wrestler as WrestlerModel
from app.models.schemas import Wrestler, WrestlerCreate, WrestlerUpdate, WrestlerWithSchool

router = APIRouter()

@router.get("/", response_model=List[WrestlerWithSchool])
async def get_wrestlers(
    skip: int = 0,
    limit: int = 100,
    weight_class: Optional[int] = None,
    school_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all wrestlers with optional filtering"""
    query = select(WrestlerModel).options(selectinload(WrestlerModel.school))
    
    if weight_class:
        query = query.where(WrestlerModel.weight_class == weight_class)
    if school_id:
        query = query.where(WrestlerModel.school_id == school_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    wrestlers = result.scalars().all()
    return wrestlers

@router.get("/{wrestler_id}", response_model=WrestlerWithSchool)
async def get_wrestler(wrestler_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific wrestler by ID"""
    query = select(WrestlerModel).options(selectinload(WrestlerModel.school)).where(WrestlerModel.id == wrestler_id)
    result = await db.execute(query)
    wrestler = result.scalar_one_or_none()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    return wrestler

@router.post("/", response_model=Wrestler, status_code=status.HTTP_201_CREATED)
async def create_wrestler(wrestler: WrestlerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new wrestler"""
    db_wrestler = WrestlerModel(**wrestler.dict())
    db.add(db_wrestler)
    await db.commit()
    await db.refresh(db_wrestler)
    return db_wrestler

@router.put("/{wrestler_id}", response_model=Wrestler)
async def update_wrestler(
    wrestler_id: int,
    wrestler_update: WrestlerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a wrestler"""
    query = select(WrestlerModel).where(WrestlerModel.id == wrestler_id)
    result = await db.execute(query)
    wrestler = result.scalar_one_or_none()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    update_data = wrestler_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wrestler, field, value)
    
    await db.commit()
    await db.refresh(wrestler)
    return wrestler

@router.delete("/{wrestler_id}")
async def delete_wrestler(wrestler_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a wrestler"""
    query = select(WrestlerModel).where(WrestlerModel.id == wrestler_id)
    result = await db.execute(query)
    wrestler = result.scalar_one_or_none()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    await db.delete(wrestler)
    await db.commit()
    return {"message": "Wrestler deleted successfully"}

@router.get("/{wrestler_id}/stats")
async def get_wrestler_stats(wrestler_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed statistics for a wrestler including match history"""
    # First verify wrestler exists
    query = select(WrestlerModel).where(WrestlerModel.id == wrestler_id)
    result = await db.execute(query)
    wrestler = result.scalar_one_or_none()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    # This would typically involve complex queries to calculate wins, losses, etc.
    # For now, returning a placeholder structure with wrestler info
    return {
        "wrestler_id": wrestler_id,
        "wrestler_name": f"{wrestler.first_name} {wrestler.last_name}",
        "weight_class": wrestler.weight_class,
        "year": wrestler.year,
        "total_matches": 0,
        "wins": 0,
        "losses": 0,
        "win_percentage": 0.0,
        "pins": 0,
        "tech_falls": 0,
        "major_decisions": 0,
        "decisions": 0
    }
