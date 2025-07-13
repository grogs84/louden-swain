from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import List, Optional
from app.database.database import get_db
from app.models.models import School as SchoolModel, Wrestler as WrestlerModel
from app.models.schemas import School, SchoolCreate, SchoolUpdate, SchoolWithWrestlers

router = APIRouter()

@router.get("/", response_model=List[School])
async def get_schools(
    skip: int = 0,
    limit: int = 100,
    state: Optional[str] = None,
    conference: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all schools with optional filtering"""
    query = select(SchoolModel)
    
    if state:
        query = query.where(SchoolModel.state == state)
    if conference:
        query = query.where(SchoolModel.conference == conference)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    schools = result.scalars().all()
    return schools

@router.get("/{school_id}", response_model=SchoolWithWrestlers)
async def get_school(school_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific school by ID with wrestlers"""
    query = select(SchoolModel).options(selectinload(SchoolModel.wrestlers)).where(SchoolModel.id == school_id)
    result = await db.execute(query)
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    return school

@router.post("/", response_model=School, status_code=status.HTTP_201_CREATED)
async def create_school(school: SchoolCreate, db: AsyncSession = Depends(get_db)):
    """Create a new school"""
    db_school = SchoolModel(**school.dict())
    db.add(db_school)
    await db.commit()
    await db.refresh(db_school)
    return db_school

@router.put("/{school_id}", response_model=School)
async def update_school(
    school_id: int,
    school_update: SchoolUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a school"""
    query = select(SchoolModel).where(SchoolModel.id == school_id)
    result = await db.execute(query)
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    update_data = school_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(school, field, value)
    
    await db.commit()
    await db.refresh(school)
    return school

@router.delete("/{school_id}")
async def delete_school(school_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a school"""
    query = select(SchoolModel).where(SchoolModel.id == school_id)
    result = await db.execute(query)
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    await db.delete(school)
    await db.commit()
    return {"message": "School deleted successfully"}

@router.get("/{school_id}/stats")
async def get_school_stats(school_id: int, db: AsyncSession = Depends(get_db)):
    """Get statistics for a school including wrestler counts and performance"""
    # First verify school exists
    query = select(SchoolModel).where(SchoolModel.id == school_id)
    result = await db.execute(query)
    school = result.scalar_one_or_none()
    
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Get wrestler statistics
    wrestler_count_query = select(func.count(WrestlerModel.id)).where(WrestlerModel.school_id == school_id)
    wrestler_count_result = await db.execute(wrestler_count_query)
    total_wrestlers = wrestler_count_result.scalar()
    
    # Get weight class distribution
    weight_class_query = select(WrestlerModel.weight_class, func.count(WrestlerModel.id)).where(
        WrestlerModel.school_id == school_id
    ).group_by(WrestlerModel.weight_class)
    weight_class_result = await db.execute(weight_class_query)
    weight_class_distribution = {str(weight): count for weight, count in weight_class_result.all()}
    
    # Get year distribution
    year_query = select(WrestlerModel.year, func.count(WrestlerModel.id)).where(
        WrestlerModel.school_id == school_id
    ).group_by(WrestlerModel.year)
    year_result = await db.execute(year_query)
    year_distribution = {year: count for year, count in year_result.all() if year}
    
    return {
        "school_id": school_id,
        "school_name": school.name,
        "total_wrestlers": total_wrestlers,
        "weight_class_distribution": weight_class_distribution,
        "year_distribution": year_distribution,
        "conference": school.conference,
        "state": school.state,
        "city": school.city
    }
