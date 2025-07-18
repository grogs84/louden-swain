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
    
    try:
        # Simple query for basic wrestler info - cast UUID to text for safety
        query = text("""
            SELECT 
                p.person_id::text as person_id,
                p.first_name,
                p.last_name
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            WHERE r.role_type = 'wrestler' AND p.person_id::text = :wrestler_id
            LIMIT 1
        """)
        
        result = await db.execute(query, {"wrestler_id": str(wrestler_id)})
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
    except Exception as e:
        # Return minimal data if query fails
        return {
            "id": wrestler_id,
            "person_id": wrestler_id,
            "first_name": "Unknown",
            "last_name": "Wrestler",
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

@router.get("/{wrestler_id}/stats", response_model=Dict[str, Any])
async def get_wrestler_stats(
    wrestler_id: Union[int, str],
    db: AsyncSession = Depends(get_db)
):
    """Get wrestler statistics - simplified for Supabase schema"""
    try:
        # Check if wrestler exists
        wrestler_query = text("""
            SELECT p.person_id, p.first_name, p.last_name
            FROM person p
            WHERE p.person_id = :wrestler_id
        """)
        
        result = await db.execute(wrestler_query, {"wrestler_id": wrestler_id})
        wrestler = result.fetchone()
        
        if not wrestler:
            return {
                "total_matches": 0,
                "wins": 0,
                "losses": 0,
                "win_percentage": 0
            }
        
        # Check if this person has wrestler roles
        role_query = text("""
            SELECT COUNT(*) as role_count
            FROM role r
            WHERE r.person_id = :wrestler_id AND r.role_type = 'wrestler'
        """)
        
        result = await db.execute(role_query, {"wrestler_id": wrestler_id})
        role_count = result.scalar() or 0
        
        # For now, return basic stats (match data needs proper schema mapping)
        return {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_percentage": 0,
            "wrestler_roles": role_count
        }
        
    except Exception as e:
        return {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_percentage": 0,
            "error": str(e)
        }
        return {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "win_percentage": 0
        }

@router.get("/{wrestler_id}/matches", response_model=List[Dict[str, Any]])
async def get_wrestler_matches(
    wrestler_id: Union[int, str],
    limit: int = 10,
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get wrestler match history - simplified for Supabase schema"""
    
    try:
        # Check if wrestler exists
        wrestler_query = text("""
            SELECT p.person_id, p.first_name, p.last_name
            FROM person p
            WHERE p.person_id = :wrestler_id
        """)
        
        result = await db.execute(wrestler_query, {"wrestler_id": wrestler_id})
        wrestler = result.fetchone()
        
        if not wrestler:
            return []
        
        # Get participant info for this wrestler
        participant_query = text("""
            SELECT pt.role_id, pt.weight_class, pt.year, pt.school_id
            FROM participant pt
            JOIN role r ON pt.role_id = r.role_id
            WHERE r.person_id = :wrestler_id AND r.role_type = 'wrestler'
            LIMIT 5
        """)
        
        result = await db.execute(participant_query, {"wrestler_id": wrestler_id})
        participants = result.fetchall()
        
        # For now, return empty matches since the schema doesn't support
        # the complex match queries until we understand the relationship
        return []
        
    except Exception as e:
        return []
    except Exception as e:
        # Return empty matches if query fails
        return []
