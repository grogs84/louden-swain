from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.database.supabase_client import supabase_client
from app.models.schemas import Coach, CoachCreate, CoachUpdate, CoachWithSchool

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_coaches(
    skip: int = 0,
    limit: int = 100,
    school_id: Optional[int] = None,
    title: Optional[str] = None,
):
    """Get all coaches with optional filtering"""
    try:
        # Build filters
        filters = {}
        if school_id:
            filters["school_id"] = school_id
        if title:
            filters["title"] = title
        
        # Select coaches with school information
        columns = "*, schools(name, conference, division)"
        
        coaches = await supabase_client.select(
            table="coaches",
            columns=columns,
            filters=filters,
            limit=limit
        )
        
        # Apply skip manually for now
        if skip > 0:
            coaches = coaches[skip:]
        
        return coaches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coaches: {str(e)}")

@router.get("/{coach_id}", response_model=dict)
async def get_coach(coach_id: int):
    """Get a specific coach by ID"""
    try:
        coaches = await supabase_client.select(
            table="coaches",
            columns="*, schools(name, conference, division)",
            filters={"id": coach_id}
        )
        
        if not coaches:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        return coaches[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coach: {str(e)}")

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_coach(coach: CoachCreate):
    """Create a new coach"""
    try:
        result = await supabase_client.insert(
            table="coaches",
            data=coach.dict()
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create coach")
        
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating coach: {str(e)}")

@router.put("/{coach_id}", response_model=dict)
async def update_coach(coach_id: int, coach_update: CoachUpdate):
    """Update a coach"""
    try:
        # Check if coach exists first
        existing = await supabase_client.select(
            table="coaches",
            filters={"id": coach_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        # Update with only the fields that were provided
        update_data = coach_update.dict(exclude_unset=True)
        
        result = await supabase_client.update(
            table="coaches",
            filters={"id": coach_id},
            data=update_data
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update coach")
        
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating coach: {str(e)}")

@router.delete("/{coach_id}")
async def delete_coach(coach_id: int):
    """Delete a coach"""
    try:
        # Check if coach exists first
        existing = await supabase_client.select(
            table="coaches",
            filters={"id": coach_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        await supabase_client.delete(
            table="coaches",
            filters={"id": coach_id}
        )
        
        return {"message": "Coach deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting coach: {str(e)}")
