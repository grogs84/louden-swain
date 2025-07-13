from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.database.supabase_client import supabase_client
from app.models.schemas import Wrestler, WrestlerCreate, WrestlerUpdate, WrestlerWithSchool

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_wrestlers(
    skip: int = 0,
    limit: int = 100,
    weight_class: Optional[int] = None,
    school_id: Optional[int] = None,
):
    """Get all wrestlers with optional filtering"""
    try:
        # Build filters
        filters = {}
        if weight_class:
            filters["weight_class"] = weight_class
        if school_id:
            filters["school_id"] = school_id
        
        # Select wrestlers with school information (using join)
        columns = "*, schools(name, conference, division)"
        
        wrestlers = await supabase_client.select(
            table="wrestlers",
            columns=columns,
            filters=filters,
            limit=limit
        )
        
        # Apply skip manually for now (could be improved with range headers)
        if skip > 0:
            wrestlers = wrestlers[skip:]
        
        return wrestlers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wrestlers: {str(e)}")

@router.get("/{wrestler_id}", response_model=dict)
async def get_wrestler(wrestler_id: int):
    """Get a specific wrestler by ID"""
    try:
        wrestlers = await supabase_client.select(
            table="wrestlers",
            columns="*, schools(name, conference, division)",
            filters={"id": wrestler_id}
        )
        
        if not wrestlers:
            raise HTTPException(status_code=404, detail="Wrestler not found")
        
        return wrestlers[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wrestler: {str(e)}")

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_wrestler(wrestler: WrestlerCreate):
    """Create a new wrestler"""
    try:
        result = await supabase_client.insert(
            table="wrestlers",
            data=wrestler.dict()
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create wrestler")
        
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating wrestler: {str(e)}")

@router.put("/{wrestler_id}", response_model=dict)
async def update_wrestler(wrestler_id: int, wrestler_update: WrestlerUpdate):
    """Update a wrestler"""
    try:
        # Check if wrestler exists first
        existing = await supabase_client.select(
            table="wrestlers",
            filters={"id": wrestler_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Wrestler not found")
        
        # Update with only the fields that were provided
        update_data = wrestler_update.dict(exclude_unset=True)
        
        result = await supabase_client.update(
            table="wrestlers",
            filters={"id": wrestler_id},
            data=update_data
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update wrestler")
        
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating wrestler: {str(e)}")

@router.delete("/{wrestler_id}")
async def delete_wrestler(wrestler_id: int):
    """Delete a wrestler"""
    try:
        # Check if wrestler exists first
        existing = await supabase_client.select(
            table="wrestlers",
            filters={"id": wrestler_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Wrestler not found")
        
        await supabase_client.delete(
            table="wrestlers",
            filters={"id": wrestler_id}
        )
        
        return {"message": "Wrestler deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting wrestler: {str(e)}")

@router.get("/{wrestler_id}/stats")
async def get_wrestler_stats(wrestler_id: int):
    """Get detailed statistics for a wrestler including match history"""
    try:
        # Check if wrestler exists
        wrestler = await supabase_client.select(
            table="wrestlers",
            filters={"id": wrestler_id}
        )
        
        if not wrestler:
            raise HTTPException(status_code=404, detail="Wrestler not found")
        
        # Get match history for this wrestler
        # This would involve querying matches table and calculating stats
        # For now, returning a placeholder structure with the actual wrestler data
        return {
            "wrestler_id": wrestler_id,
            "wrestler_name": f"{wrestler[0].get('first_name', '')} {wrestler[0].get('last_name', '')}",
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_percentage": 0.0,
            "pins": 0,
            "tech_falls": 0,
            "major_decisions": 0,
            "decisions": 0,
            "weight_class": wrestler[0].get('weight_class'),
            "year": wrestler[0].get('year')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wrestler stats: {str(e)}")
