"""
Wrestlers API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from ..database import get_db, Database
from ..models import WrestlerProfile, WrestlerStats, WrestlerMatch, PersonProfile, WrestlerRoleStats

router = APIRouter()

@router.get("/wrestlers", response_model=List[WrestlerProfile])
async def get_wrestlers(
    limit: int = Query(20, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    name: Optional[str] = Query(None, description="Filter by wrestler name"),
    school: Optional[str] = Query(None, description="Filter by school name"),
    weight_class: Optional[str] = Query(None, description="Filter by weight class"),
    db: Database = Depends(get_db)
):
    """Get wrestlers with optional filtering"""
    query = """
    SELECT DISTINCT 
        p.id,
        p.first_name,
        p.last_name,
        s.name as school_name,
        s.location as school_location
    FROM people p
    LEFT JOIN participants pt ON p.id = pt.person_id
    LEFT JOIN schools s ON pt.school_id = s.id
    WHERE 1=1
    """
    params = []
    
    if name:
        query += " AND (p.first_name ILIKE $" + str(len(params) + 1) + " OR p.last_name ILIKE $" + str(len(params) + 1) + ")"
        params.append(f"%{name}%")
    
    if school:
        query += " AND s.name ILIKE $" + str(len(params) + 1)
        params.append(f"%{school}%")
    
    if weight_class:
        query += " AND pt.weight_class = $" + str(len(params) + 1)
        params.append(weight_class)
    
    query += f" ORDER BY p.last_name, p.first_name LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
    params.extend([limit, offset])
    
    rows = await db.fetch_all(query, *params)
    return rows

@router.get("/wrestlers/{wrestler_id}", response_model=WrestlerProfile)
async def get_wrestler(
    wrestler_id: UUID,
    db: Database = Depends(get_db)
):
    """Get wrestler by ID"""
    query = """
    SELECT 
        p.id,
        p.first_name,
        p.last_name,
        s.name as school_name,
        s.location as school_location
    FROM people p
    LEFT JOIN participants pt ON p.id = pt.person_id
    LEFT JOIN schools s ON pt.school_id = s.id
    WHERE p.id = $1
    LIMIT 1
    """
    
    wrestler = await db.fetch_one(query, wrestler_id)
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    return wrestler

@router.get("/wrestlers/{wrestler_id}/stats", response_model=WrestlerStats)
async def get_wrestler_stats(
    wrestler_id: UUID,
    db: Database = Depends(get_db)
):
    """Get wrestler statistics"""
    # Updated query to match Supabase schema and include AA count
    query = """
    WITH wrestler_matches AS (
        SELECT 
            pm.is_winner,
            m.result_type,
            m.round_order,
            pm.match_id
        FROM role r
        JOIN participant part ON r.role_id = part.role_id
        JOIN participant_match pm ON part.participant_id = pm.participant_id
        JOIN match m ON pm.match_id = m.match_id
        WHERE r.person_id = $1::text
    )
    SELECT 
        COUNT(*) as match_count,
        COUNT(CASE WHEN is_winner = true THEN 1 END) as wins,
        COUNT(CASE WHEN is_winner = false THEN 1 END) as losses,
        COUNT(CASE WHEN is_winner = true AND result_type = 'Fall' THEN 1 END) as pins,
        COUNT(CASE WHEN is_winner = true AND result_type = 'Tech Fall' THEN 1 END) as tech_falls,
        COUNT(CASE WHEN is_winner = true AND result_type = 'Major Decision' THEN 1 END) as major_decisions,
        COUNT(CASE WHEN round_order IN (6, 15) THEN 1 END) as aa_count
    FROM wrestler_matches
    """
    
    stats = await db.fetch_one(query, str(wrestler_id))
    if not stats:
        stats = {
            "match_count": 0, "wins": 0, "losses": 0,
            "pins": 0, "tech_falls": 0, "major_decisions": 0, "aa_count": 0
        }
    
    # Calculate win percentage
    total = stats["match_count"] or 0
    wins = stats["wins"] or 0
    win_percentage = (wins / total * 100) if total > 0 else 0.0
    
    return {
        "person_id": str(wrestler_id),
        "match_count": total,
        "wins": wins,
        "losses": stats["losses"] or 0,
        "win_percentage": round(win_percentage, 1),
        "aa_count": stats["aa_count"] or 0,
        "pins": stats["pins"] or 0,
        "tech_falls": stats["tech_falls"] or 0,
        "major_decisions": stats["major_decisions"] or 0,
        "total_matches": total  # Keep for backward compatibility
    }

@router.get("/wrestlers/{wrestler_id}/matches", response_model=List[WrestlerMatch])
async def get_wrestler_matches(
    wrestler_id: UUID,
    limit: int = Query(100, le=500, description="Maximum number of matches"),
    db: Database = Depends(get_db)
):
    """Get wrestler's match history"""
    # Updated query to match Supabase schema and required format
    query = """
    SELECT 
        m.match_id,
        part.year,
        part.weight_class,
        m.round,
        INITCAP(per.search_name) as wrestler_name,
        COALESCE(pm.score::text, m.fall_time) AS scored,
        INITCAP(per2.search_name) as opponent,
        COALESCE(pm1.score::text, '-') as opponent_scored,
        m.result_type
    FROM role r
    JOIN person per ON per.person_id = r.person_id
    JOIN participant part ON r.role_id = part.role_id
    JOIN participant_match pm ON part.participant_id = pm.participant_id
    JOIN match m ON pm.match_id = m.match_id
    JOIN participant_match pm1 ON m.match_id = pm1.match_id AND pm.participant_id != pm1.participant_id
    JOIN participant part2 ON part2.participant_id = pm1.participant_id
    JOIN role r2 ON part2.role_id = r2.role_id
    JOIN person per2 ON per2.person_id = r2.person_id
    WHERE r.person_id = $1::text
    ORDER BY part.year ASC, m.round_order ASC
    LIMIT $2
    """
    
    matches = await db.fetch_all(query, str(wrestler_id), limit)
    
    # Convert to response format with both new and legacy fields
    formatted_matches = []
    for match in matches:
        formatted_match = {
            "match_id": match["match_id"],
            "year": match["year"],
            "weight_class": match["weight_class"],
            "round": match["round"],
            "wrestler_name": match["wrestler_name"],
            "scored": match["scored"],
            "opponent": match["opponent"],
            "opponent_scored": match["opponent_scored"],
            "result_type": match["result_type"],
            # Legacy fields for backward compatibility
            "opponent_first_name": match["opponent"].split()[0] if match["opponent"] else "",
            "opponent_last_name": " ".join(match["opponent"].split()[1:]) if match["opponent"] and len(match["opponent"].split()) > 1 else "",
            "result": "W" if match["scored"] and match["opponent_scored"] and match["scored"] != '-' and match["opponent_scored"] != '-' else "L",
            "decision": match["result_type"],
            "score": match["scored"],
            "tournament_name": None,  # Not available in this query
        }
        formatted_matches.append(formatted_match)
    
    return formatted_matches

@router.get("/profile/{person_id}", response_model=PersonProfile)
async def get_person_profile(
    person_id: str,
    db: Database = Depends(get_db)
):
    """Get person profile with all their roles"""
    # Get person basic info
    person_query = """
    SELECT 
        person_id,
        first_name,
        last_name,
        search_name,
        date_of_birth,
        city_of_origin,
        state_of_origin
    FROM person
    WHERE person_id = $1
    """
    
    person = await db.fetch_one(person_query, person_id)
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    # Get all roles for this person
    roles_query = """
    SELECT 
        role_id,
        role_type
    FROM role
    WHERE person_id = $1
    ORDER BY role_type
    """
    
    roles = await db.fetch_all(roles_query, person_id)
    
    return {
        "person_id": person["person_id"],
        "first_name": person["first_name"],
        "last_name": person["last_name"],
        "full_name": f"{person['first_name']} {person['last_name']}",
        "search_name": person["search_name"],
        "date_of_birth": person["date_of_birth"],
        "city_of_origin": person["city_of_origin"],
        "state_of_origin": person["state_of_origin"],
        "roles": [
            {
                "role_id": role["role_id"],
                "role_type": role["role_type"]
            }
            for role in roles
        ]
    }

@router.get("/profile/{person_id}/stats")
async def get_person_role_stats(
    person_id: str,
    role_type: str = Query(..., description="Role type (wrestler, coach, etc.)"),
    db: Database = Depends(get_db)
):
    """Get stats for a specific role of a person"""
    if role_type.lower() == "wrestler":
        return await get_wrestler_stats_for_person(person_id, db)
    elif role_type.lower() == "coach":
        # TODO: Implement coach stats when needed
        return {
            "person_id": person_id,
            "role_type": "coach",
            "message": "Coach stats not yet implemented"
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported role type: {role_type}")

@router.get("/profile/{person_id}/matches")
async def get_person_role_matches(
    person_id: str,
    role_type: str = Query(..., description="Role type (wrestler, coach, etc.)"),
    limit: int = Query(100, le=500, description="Maximum number of matches"),
    db: Database = Depends(get_db)
):
    """Get matches for a specific role of a person"""
    if role_type.lower() == "wrestler":
        return await get_wrestler_matches_for_person(person_id, limit, db)
    elif role_type.lower() == "coach":
        # TODO: Implement coach matches when needed
        return []
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported role type: {role_type}")

async def get_wrestler_stats_for_person(person_id: str, db: Database):
    """Helper function to get wrestler stats for a person"""
    # Updated query to match Supabase schema and include AA count
    query = """
    WITH wrestler_matches AS (
        SELECT 
            pm.is_winner,
            m.result_type,
            m.round_order,
            pm.match_id
        FROM role r
        JOIN participant part ON r.role_id = part.role_id
        JOIN participant_match pm ON part.participant_id = pm.participant_id
        JOIN match m ON pm.match_id = m.match_id
        WHERE r.person_id = $1::text AND r.role_type = 'wrestler'
    )
    SELECT 
        COUNT(*) as match_count,
        COUNT(CASE WHEN is_winner = true THEN 1 END) as wins,
        COUNT(CASE WHEN is_winner = false THEN 1 END) as losses,
        COUNT(CASE WHEN is_winner = true AND result_type = 'Fall' THEN 1 END) as pins,
        COUNT(CASE WHEN is_winner = true AND result_type = 'Tech Fall' THEN 1 END) as tech_falls,
        COUNT(CASE WHEN is_winner = true AND result_type = 'Major Decision' THEN 1 END) as major_decisions,
        COUNT(CASE WHEN round_order IN (6, 15) THEN 1 END) as aa_count
    FROM wrestler_matches
    """
    
    stats = await db.fetch_one(query, person_id)
    if not stats:
        stats = {
            "match_count": 0, "wins": 0, "losses": 0,
            "pins": 0, "tech_falls": 0, "major_decisions": 0, "aa_count": 0
        }
    
    # Calculate win percentage
    total = stats["match_count"] or 0
    wins = stats["wins"] or 0
    win_percentage = (wins / total * 100) if total > 0 else 0.0
    
    return {
        "person_id": person_id,
        "role_type": "wrestler",
        "match_count": total,
        "wins": wins,
        "losses": stats["losses"] or 0,
        "win_percentage": round(win_percentage, 1),
        "aa_count": stats["aa_count"] or 0,
        "pins": stats["pins"] or 0,
        "tech_falls": stats["tech_falls"] or 0,
        "major_decisions": stats["major_decisions"] or 0,
        "total_matches": total  # Keep for backward compatibility
    }

async def get_wrestler_matches_for_person(person_id: str, limit: int, db: Database):
    """Helper function to get wrestler matches for a person"""
    # Updated query to match Supabase schema and required format
    query = """
    SELECT 
        m.match_id,
        part.year,
        part.weight_class,
        m.round,
        INITCAP(per.search_name) as wrestler_name,
        COALESCE(pm.score::text, m.fall_time) AS scored,
        INITCAP(per2.search_name) as opponent,
        COALESCE(pm1.score::text, '-') as opponent_scored,
        m.result_type
    FROM role r
    JOIN person per ON per.person_id = r.person_id
    JOIN participant part ON r.role_id = part.role_id
    JOIN participant_match pm ON part.participant_id = pm.participant_id
    JOIN match m ON pm.match_id = m.match_id
    JOIN participant_match pm1 ON m.match_id = pm1.match_id AND pm.participant_id != pm1.participant_id
    JOIN participant part2 ON part2.participant_id = pm1.participant_id
    JOIN role r2 ON part2.role_id = r2.role_id
    JOIN person per2 ON per2.person_id = r2.person_id
    WHERE r.person_id = $1::text AND r.role_type = 'wrestler'
    ORDER BY part.year ASC, m.round_order ASC
    LIMIT $2
    """
    
    matches = await db.fetch_all(query, person_id, limit)
    
    # Convert to response format with both new and legacy fields
    formatted_matches = []
    for match in matches:
        formatted_match = {
            "match_id": match["match_id"],
            "year": match["year"],
            "weight_class": match["weight_class"],
            "round": match["round"],
            "wrestler_name": match["wrestler_name"],
            "scored": match["scored"],
            "opponent": match["opponent"],
            "opponent_scored": match["opponent_scored"],
            "result_type": match["result_type"],
            # Legacy fields for backward compatibility
            "opponent_first_name": match["opponent"].split()[0] if match["opponent"] else "",
            "opponent_last_name": " ".join(match["opponent"].split()[1:]) if match["opponent"] and len(match["opponent"].split()) > 1 else "",
            "result": "W" if match["scored"] and match["opponent_scored"] and match["scored"] != '-' and match["opponent_scored"] != '-' else "L",
            "decision": match["result_type"],
            "score": match["scored"],
            "tournament_name": None,  # Not available in this query
        }
        formatted_matches.append(formatted_match)
    
    return formatted_matches

@router.get("/profile-simple/{person_id}")
async def get_wrestler_profile_simple(
    person_id: str,
    db: Database = Depends(get_db)
):
    """Get basic wrestler profile using only person table (for migration period)"""
    query = """
    SELECT 
        person_id,
        first_name,
        last_name,
        search_name,
        date_of_birth,
        city_of_origin,
        state_of_origin
    FROM person
    WHERE person_id = $1
    """
    
    wrestler = await db.fetch_one(query, person_id)
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    return {
        "person_id": wrestler["person_id"],
        "first_name": wrestler["first_name"],
        "last_name": wrestler["last_name"],
        "full_name": f"{wrestler['first_name']} {wrestler['last_name']}",
        "search_name": wrestler["search_name"],
        "date_of_birth": wrestler["date_of_birth"],
        "city_of_origin": wrestler["city_of_origin"],
        "state_of_origin": wrestler["state_of_origin"],
        "status": "Migration in progress - full profile coming soon"
    }
