from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.database.supabase_client import supabase_client
from app.models.schemas import School, SchoolCreate, SchoolUpdate, SchoolWithWrestlers

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_schools(
    skip: int = 0,
    limit: int = 100,
    state: Optional[str] = None,
    conference: Optional[str] = None,
):
    """Get all schools with optional filtering"""
    try:
        # Build filters
        filters = {}
        if state:
            filters["state"] = state
        if conference:
            filters["conference"] = conference
        
        schools = await supabase_client.select(
            table="schools",
            filters=filters,
            limit=limit
        )
        
        # Apply skip manually for now
        if skip > 0:
            schools = schools[skip:]
        
        return schools
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schools: {str(e)}")

@router.get("/{school_id}", response_model=dict)
async def get_school(school_id: int):
    """Get a specific school by ID with wrestlers"""
    try:
        schools = await supabase_client.select(
            table="schools",
            filters={"id": school_id}
        )
        
        if not schools:
            raise HTTPException(status_code=404, detail="School not found")
        
        school = schools[0]
        
        # Get wrestlers for this school
        wrestlers = await supabase_client.select(
            table="wrestlers",
            filters={"school_id": school_id}
        )
        
        school["wrestlers"] = wrestlers
        return school
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching school: {str(e)}")

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_school(school: SchoolCreate):
    """Create a new school"""
    try:
        result = await supabase_client.insert(
            table="schools",
            data=school.dict()
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create school")
        
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating school: {str(e)}")

@router.put("/{school_id}", response_model=dict)
async def update_school(school_id: int, school_update: SchoolUpdate):
    """Update a school"""
    try:
        # Check if school exists first
        existing = await supabase_client.select(
            table="schools",
            filters={"id": school_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Update with only the fields that were provided
        update_data = school_update.dict(exclude_unset=True)
        
        result = await supabase_client.update(
            table="schools",
            filters={"id": school_id},
            data=update_data
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update school")
        
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating school: {str(e)}")

@router.delete("/{school_id}")
async def delete_school(school_id: int):
    """Delete a school"""
    try:
        # Check if school exists first
        existing = await supabase_client.select(
            table="schools",
            filters={"id": school_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="School not found")
        
        await supabase_client.delete(
            table="schools",
            filters={"id": school_id}
        )
        
        return {"message": "School deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting school: {str(e)}")

@router.get("/{school_id}/stats")
async def get_school_stats(school_id: int):
    """Get statistics for a school including wrestler counts and performance"""
    try:
        # Check if school exists
        school = await supabase_client.select(
            table="schools",
            filters={"id": school_id}
        )
        
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Get wrestlers for this school
        wrestlers = await supabase_client.select(
            table="wrestlers",
            filters={"school_id": school_id}
        )
        
        # Calculate basic stats
        total_wrestlers = len(wrestlers)
        weight_class_counts = {}
        year_counts = {}
        
        for wrestler in wrestlers:
            # Count by weight class
            weight = wrestler.get('weight_class')
            if weight:
                weight_class_counts[weight] = weight_class_counts.get(weight, 0) + 1
            
            # Count by year
            year = wrestler.get('year')
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1
        
        return {
            "school_id": school_id,
            "school_name": school[0].get('name'),
            "total_wrestlers": total_wrestlers,
            "weight_class_distribution": weight_class_counts,
            "year_distribution": year_counts,
            "conference": school[0].get('conference'),
            "division": school[0].get('division'),
            "state": school[0].get('state')
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching school stats: {str(e)}")
