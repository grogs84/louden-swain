from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List
from app.database.database import get_db
from app.models.models import Wrestler as WrestlerModel, School as SchoolModel, Coach as CoachModel
from app.models.schemas import SearchResults, SearchResult

router = APIRouter()

@router.get("/", response_model=SearchResults)
async def search_all(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum results per category"),
    db: AsyncSession = Depends(get_db)
):
    """Search across wrestlers, schools, and coaches"""
    
    search_results = SearchResults()
    
    # Search wrestlers
    wrestler_query = select(WrestlerModel, SchoolModel).join(SchoolModel).where(
        or_(
            WrestlerModel.first_name.ilike(f"%{q}%"),
            WrestlerModel.last_name.ilike(f"%{q}%"),
            (WrestlerModel.first_name + " " + WrestlerModel.last_name).ilike(f"%{q}%")
        )
    ).limit(limit)
    
    wrestler_result = await db.execute(wrestler_query)
    wrestlers = wrestler_result.all()
    
    for wrestler, school in wrestlers:
        search_results.wrestlers.append(
            SearchResult(
                type="wrestler",
                id=wrestler.id,
                name=f"{wrestler.first_name} {wrestler.last_name}",
                additional_info=f"{school.name} - {wrestler.weight_class}lbs"
            )
        )
    
    # Search schools
    school_query = select(SchoolModel).where(
        or_(
            SchoolModel.name.ilike(f"%{q}%"),
            SchoolModel.conference.ilike(f"%{q}%")
        )
    ).limit(limit)
    
    school_result = await db.execute(school_query)
    schools = school_result.scalars().all()
    
    for school in schools:
        search_results.schools.append(
            SearchResult(
                type="school",
                id=school.id,
                name=school.name,
                additional_info=f"{school.conference} - {school.state}" if school.conference and school.state else school.state
            )
        )
    
    # Search coaches
    coach_query = select(CoachModel, SchoolModel).join(SchoolModel).where(
        or_(
            CoachModel.first_name.ilike(f"%{q}%"),
            CoachModel.last_name.ilike(f"%{q}%"),
            (CoachModel.first_name + " " + CoachModel.last_name).ilike(f"%{q}%")
        )
    ).limit(limit)
    
    coach_result = await db.execute(coach_query)
    coaches = coach_result.all()
    
    for coach, school in coaches:
        search_results.coaches.append(
            SearchResult(
                type="coach",
                id=coach.id,
                name=f"{coach.first_name} {coach.last_name}",
                additional_info=f"{school.name} - {coach.position}" if coach.position else school.name
            )
        )
    
    return search_results

@router.get("/wrestlers", response_model=List[SearchResult])
async def search_wrestlers(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    weight_class: int = None,
    school_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Search wrestlers specifically"""
    query = select(WrestlerModel, SchoolModel).join(SchoolModel).where(
        or_(
            WrestlerModel.first_name.ilike(f"%{q}%"),
            WrestlerModel.last_name.ilike(f"%{q}%"),
            (WrestlerModel.first_name + " " + WrestlerModel.last_name).ilike(f"%{q}%")
        )
    )
    
    if weight_class:
        query = query.where(WrestlerModel.weight_class == weight_class)
    if school_id:
        query = query.where(WrestlerModel.school_id == school_id)
    
    query = query.limit(limit)
    result = await db.execute(query)
    wrestlers = result.all()
    
    return [
        SearchResult(
            type="wrestler",
            id=wrestler.id,
            name=f"{wrestler.first_name} {wrestler.last_name}",
            additional_info=f"{school.name} - {wrestler.weight_class}lbs"
        )
        for wrestler, school in wrestlers
    ]

@router.get("/schools", response_model=List[SearchResult])
async def search_schools(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    state: str = None,
    conference: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Search schools specifically"""
    query = select(SchoolModel).where(
        or_(
            SchoolModel.name.ilike(f"%{q}%"),
            SchoolModel.conference.ilike(f"%{q}%")
        )
    )
    
    if state:
        query = query.where(SchoolModel.state == state)
    if conference:
        query = query.where(SchoolModel.conference == conference)
    
    query = query.limit(limit)
    result = await db.execute(query)
    schools = result.scalars().all()
    
    return [
        SearchResult(
            type="school",
            id=school.id,
            name=school.name,
            additional_info=f"{school.conference} - {school.state}" if school.conference and school.state else school.state
        )
        for school in schools
    ]
