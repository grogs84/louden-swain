from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional, Union, Dict, Any
from app.database.database import get_db

router = APIRouter()

def title_case_name(name: str) -> str:
    """Apply title case formatting to names (updated for Supabase)"""
    if not name:
        return name
    
    # Common prefixes and suffixes that should be lowercase
    lowercase_words = {
        'jr', 'sr', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
        'van', 'von', 'de', 'del', 'della', 'di', 'du', 'la', 'le', 'mac', 'mc',
        'o\'', 'st', 'st.', 'and', 'the', 'of', 'in', 'at', 'to', 'for', 'with'
    }
    
    # Split by spaces and handle each word
    words = name.strip().split()
    result = []
    
    for i, word in enumerate(words):
        # Handle hyphenated names
        if '-' in word:
            parts = word.split('-')
            parts = [part.capitalize() if part.lower() not in lowercase_words or i == 0 
                    else part.lower() for part in parts]
            result.append('-'.join(parts))
        # Handle apostrophes (O'Connor, D'Angelo)
        elif '\'' in word:
            parts = word.split('\'')
            formatted_parts = []
            for j, part in enumerate(parts):
                if j == 0 or (j == 1 and parts[0].lower() in ['o', 'd', 'mc']):
                    formatted_parts.append(part.capitalize())
                else:
                    formatted_parts.append(part.lower() if part.lower() in lowercase_words else part.capitalize())
            result.append('\''.join(formatted_parts))
        # Handle regular words
        else:
            if word.lower() in lowercase_words and i > 0:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
    
    return ' '.join(result)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_wrestlers(
    skip: int = 0,
    limit: int = 100,
    weight_class: Optional[int] = None,
    school_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all wrestlers with optional filtering"""
    
    # Build the WHERE clause conditions
    where_conditions = ["r.role_type = 'wrestler'"]
    params = {"offset": skip, "limit": limit}
    
    if weight_class:
        where_conditions.append("pt.weight_class = :weight_class")
        params["weight_class"] = weight_class
    
    if school_id:
        where_conditions.append("pt.school_id = :school_id")
        params["school_id"] = school_id
    
    where_clause = " AND ".join(where_conditions)
    
    query = text(f"""
        WITH wrestler_summary AS (
            SELECT 
                p.person_id,
                p.first_name,
                p.last_name,
                pt.weight_class,
                pt.year,
                s.name as school_name,
                s.location as school_location,
                s.school_id,
                ROW_NUMBER() OVER (PARTITION BY p.person_id ORDER BY pt.year DESC) as rn
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            LEFT JOIN school s ON pt.school_id = s.school_id
            WHERE {where_clause}
        )
        SELECT 
            person_id,
            first_name,
            last_name,
            weight_class,
            year,
            school_name,
            school_location,
            school_id
        FROM wrestler_summary 
        WHERE rn = 1
        ORDER BY last_name, first_name
        OFFSET :offset LIMIT :limit
    """)
    
    result = await db.execute(query, params)
    wrestlers = result.fetchall()
    
    return [
        {
            "id": wrestler.person_id,
            "person_id": wrestler.person_id,
            "first_name": title_case_name(wrestler.first_name),
            "last_name": title_case_name(wrestler.last_name),
            "weight_class": wrestler.weight_class,
            "year": wrestler.year,
            "school": {
                "id": wrestler.school_id,
                "name": title_case_name(wrestler.school_name) if wrestler.school_name else None,
                "location": title_case_name(wrestler.school_location) if wrestler.school_location else None
            } if wrestler.school_name else None
        }
        for wrestler in wrestlers
    ]

@router.get("/{wrestler_id}", response_model=Dict[str, Any])
async def get_wrestler(
    wrestler_id: Union[int, str],
    db: AsyncSession = Depends(get_db)
):
    """Get a specific wrestler by ID with basic details and simplified match history"""
    
    # First get basic wrestler info
    wrestler_query = text("""
        WITH wrestler_info AS (
            SELECT 
                p.person_id,
                p.first_name,
                p.last_name,
                pt.weight_class,
                pt.year,
                s.name as school_name,
                s.location as school_location,
                s.school_id,
                ROW_NUMBER() OVER (PARTITION BY p.person_id ORDER BY pt.year DESC) as rn
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            LEFT JOIN school s ON pt.school_id = s.school_id
            WHERE r.role_type = 'wrestler' AND p.person_id = :wrestler_id
        )
        SELECT * FROM wrestler_info WHERE rn = 1
    """)
    
    result = await db.execute(wrestler_query, {"wrestler_id": wrestler_id})
    wrestler = result.fetchone()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    # Get simplified match count and basic stats
    stats_query = text("""
        SELECT 
            COUNT(*) as total_matches,
            COUNT(CASE WHEN mr.winner_role_id = r_self.role_id THEN 1 END) as wins
        FROM person p_self
        JOIN role r_self ON p_self.person_id = r_self.person_id
        JOIN participant pt_self ON r_self.role_id = pt_self.role_id
        JOIN match m ON (pt_self.role_id = m.participant1_role_id OR pt_self.role_id = m.participant2_role_id)
        LEFT JOIN match_result mr ON m.match_id = mr.match_id
        WHERE p_self.person_id = :wrestler_id AND r_self.role_type = 'wrestler'
    """)
    
    result = await db.execute(stats_query, {"wrestler_id": wrestler_id})
    stats = result.fetchone()
    
    total_matches = stats.total_matches if stats else 0
    wins = stats.wins if stats else 0
    losses = total_matches - wins
    
    return {
        "id": wrestler.person_id,
        "person_id": wrestler.person_id,
        "first_name": title_case_name(wrestler.first_name),
        "last_name": title_case_name(wrestler.last_name),
        "weight_class": wrestler.weight_class,
        "year": wrestler.year,
        "school": {
            "id": wrestler.school_id,
            "name": title_case_name(wrestler.school_name) if wrestler.school_name else None,
            "location": title_case_name(wrestler.school_location) if wrestler.school_location else None
        } if wrestler.school_name else None,
        "stats": {
            "total_matches": total_matches,
            "wins": wins,
            "losses": losses,
            "win_percentage": round((wins / total_matches * 100), 1) if total_matches > 0 else 0
        },
        "matches": []  # Simplified - no detailed match history for now
    }
