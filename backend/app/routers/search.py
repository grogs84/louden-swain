from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, func
from typing import List, Dict, Any
from app.database.database import get_db
from app.models.models import Wrestler as WrestlerModel, School as SchoolModel, Coach as CoachModel
from app.models.schemas import SearchResults, SearchResult

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def search_all(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum results per category"),
    db: AsyncSession = Depends(get_db)
):
    """Search across wrestlers, schools, and coaches"""
    
    results = {
        "query": q,
        "wrestlers": [],
        "schools": [],
        "coaches": []
    }
    
    try:
        # Search wrestlers by name
        wrestler_query = select(WrestlerModel).options(selectinload(WrestlerModel.school)).where(
            or_(
                WrestlerModel.first_name.ilike(f"%{q}%"),
                WrestlerModel.last_name.ilike(f"%{q}%"),
                func.concat(WrestlerModel.first_name, ' ', WrestlerModel.last_name).ilike(f"%{q}%")
            )
        ).limit(limit)
        
        wrestler_result = await db.execute(wrestler_query)
        wrestlers = wrestler_result.scalars().all()
        
        for wrestler in wrestlers:
            results["wrestlers"].append({
                "type": "wrestler",
                "id": wrestler.id,
                "name": f"{wrestler.first_name} {wrestler.last_name}",
                "additional_info": f"{wrestler.school.name if wrestler.school else 'Unknown School'} - {wrestler.weight_class}lbs",
                "weight_class": wrestler.weight_class,
                "year": wrestler.year,
                "school_id": wrestler.school_id,
                "school_name": wrestler.school.name if wrestler.school else None
            })
        
        # Search schools by name or conference
        school_query = select(SchoolModel).where(
            or_(
                SchoolModel.name.ilike(f"%{q}%"),
                SchoolModel.conference.ilike(f"%{q}%")
            )
        ).limit(limit)
        
        school_result = await db.execute(school_query)
        schools = school_result.scalars().all()
        
        for school in schools:
            results["schools"].append({
                "type": "school",
                "id": school.id,
                "name": school.name,
                "additional_info": f"{school.conference or 'N/A'} - {school.state or 'N/A'}",
                "conference": school.conference,
                "state": school.state,
                "city": school.city
            })
        
        # Search coaches by name
        coach_query = select(CoachModel).options(selectinload(CoachModel.school)).where(
            or_(
                CoachModel.first_name.ilike(f"%{q}%"),
                CoachModel.last_name.ilike(f"%{q}%"),
                func.concat(CoachModel.first_name, ' ', CoachModel.last_name).ilike(f"%{q}%")
            )
        ).limit(limit)
        
        coach_result = await db.execute(coach_query)
        coaches = coach_result.scalars().all()
        
        for coach in coaches:
            results["coaches"].append({
                "type": "coach",
                "id": coach.id,
                "name": f"{coach.first_name} {coach.last_name}",
                "additional_info": f"{coach.school.name if coach.school else 'Unknown School'} - {coach.position or 'Coach'}",
                "position": coach.position,
                "school_id": coach.school_id,
                "school_name": coach.school.name if coach.school else None
            })
        
        return results
        
    except Exception as e:
        return {
            "query": q,
            "error": f"Search failed: {str(e)}",
            "wrestlers": [],
            "schools": [],
            "coaches": []
        }

@router.get("/wrestlers", response_model=List[Dict[str, Any]])
async def search_wrestlers(
    q: str = Query(..., min_length=2, description="Search query"),
    weight_class: int = Query(None, description="Filter by weight class"),
    school_id: int = Query(None, description="Filter by school"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """Search wrestlers with additional filters"""
    
    try:
        query = select(WrestlerModel).options(selectinload(WrestlerModel.school)).where(
            or_(
                WrestlerModel.first_name.ilike(f"%{q}%"),
                WrestlerModel.last_name.ilike(f"%{q}%"),
                func.concat(WrestlerModel.first_name, ' ', WrestlerModel.last_name).ilike(f"%{q}%")
            )
        )
        
        # Apply filters
        if weight_class:
            query = query.where(WrestlerModel.weight_class == weight_class)
        if school_id:
            query = query.where(WrestlerModel.school_id == school_id)
        
        query = query.limit(limit)
        result = await db.execute(query)
        wrestlers = result.scalars().all()
        
        return [
            {
                "id": wrestler.id,
                "name": f"{wrestler.first_name} {wrestler.last_name}",
                "weight_class": wrestler.weight_class,
                "year": wrestler.year,
                "school": wrestler.school.name if wrestler.school else "Unknown School",
                "school_id": wrestler.school_id,
                "conference": wrestler.school.conference if wrestler.school else None,
                "state": wrestler.state
            } for wrestler in wrestlers
        ]
        
    except Exception as e:
        return [{"error": f"Wrestler search failed: {str(e)}"}]

@router.get("/schools", response_model=List[Dict[str, Any]])
async def search_schools(
    q: str = Query(..., min_length=2, description="Search query"),
    state: str = Query(None, description="Filter by state"),
    conference: str = Query(None, description="Filter by conference"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """Search schools with additional filters"""
    
    try:
        query = select(SchoolModel).where(
            SchoolModel.name.ilike(f"%{q}%")
        )
        
        # Apply filters
        if state:
            query = query.where(SchoolModel.state.ilike(f"%{state}%"))
        if conference:
            query = query.where(SchoolModel.conference.ilike(f"%{conference}%"))
        
        query = query.limit(limit)
        result = await db.execute(query)
        schools = result.scalars().all()
        
        return [
            {
                "id": school.id,
                "name": school.name,
                "state": school.state,
                "conference": school.conference,
                "city": school.city,
                "website": school.website
            } for school in schools
        ]
        
    except Exception as e:
        return [{"error": f"School search failed: {str(e)}"}]
