from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional, Union, Dict, Any
from app.database.database import get_db

router = APIRouter()

def title_case_name(name: str) -> str:
    """Apply title case formatting to names (updated for Supabase - simplified)"""
    if not name:
        return name
    
    # Simple title case for now
    return ' '.join(word.capitalize() for word in name.split())

@router.get("/", response_model=List[Dict[str, Any]])
async def get_wrestlers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all wrestlers with basic info only"""
    
    # Simple query that should work fast
    query = text("""
        SELECT 
            p.person_id,
            p.first_name,
            p.last_name
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        WHERE r.role_type = 'wrestler'
        ORDER BY p.last_name, p.first_name
        OFFSET :offset LIMIT :limit
    """)
    
    result = await db.execute(query, {"offset": skip, "limit": limit})
    wrestlers = result.fetchall()
    
    return [
        {
            "id": wrestler.person_id,
            "person_id": wrestler.person_id,
            "first_name": title_case_name(wrestler.first_name),
            "last_name": title_case_name(wrestler.last_name),
            "weight_class": None,
            "year": None,
            "school": None
        }
        for wrestler in wrestlers
    ]

@router.get("/{wrestler_id}", response_model=Dict[str, Any])
async def get_wrestler(
    wrestler_id: Union[int, str],
    db: AsyncSession = Depends(get_db)
):
    """Get a specific wrestler by ID with basic info only"""
    
    # Simple query for basic wrestler info
    query = text("""
        SELECT 
            p.person_id,
            p.first_name,
            p.last_name
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        WHERE r.role_type = 'wrestler' AND p.person_id = :wrestler_id
        LIMIT 1
    """)
    
    result = await db.execute(query, {"wrestler_id": wrestler_id})
    wrestler = result.fetchone()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    return {
        "id": wrestler.person_id,
        "person_id": wrestler.person_id,
        "first_name": title_case_name(wrestler.first_name),
        "last_name": title_case_name(wrestler.last_name),
        "weight_class": None,
        "year": None,
        "school": None,
        "stats": {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_percentage": 0
        },
        "matches": []
    }
