"""
Person profile API endpoints
Provides unified person data with all roles (wrestler, coach)
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from ..database import Database, get_db
from ..models import Person

router = APIRouter()


@router.get("/persons/{person_id}")
async def get_person_profile(person_id: str, db: Database = Depends(get_db)):
    """Get complete person profile with all roles"""
    
    # Get basic person information
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
    
    # Get current/primary affiliation (most recent participation)
    affiliation_query = """
    SELECT DISTINCT ON (r.role_type)
        r.role_type,
        s.name as school_name,
        s.location as school_location,
        part.year,
        part.weight_class
    FROM role r
    LEFT JOIN participant part ON r.role_id = part.role_id
    LEFT JOIN school s ON part.school_id = s.school_id
    WHERE r.person_id = $1 AND part.year IS NOT NULL
    ORDER BY r.role_type, part.year DESC
    """
    
    affiliations = await db.fetch_all(affiliation_query, person_id)
    
    # Build response with person data and roles
    response = {
        "person_id": person["person_id"],
        "first_name": person["first_name"],
        "last_name": person["last_name"],
        "full_name": f"{person['first_name']} {person['last_name']}",
        "search_name": person["search_name"],
        "date_of_birth": person["date_of_birth"],
        "city_of_origin": person["city_of_origin"],
        "state_of_origin": person["state_of_origin"],
        "roles": [{"role_id": r["role_id"], "role_type": r["role_type"]} for r in roles],
        "primary_affiliation": None,
        "wrestler_data": None,
        "coach_data": None
    }
    
    # Set primary affiliation (prefer wrestler, then coach)
    wrestler_affiliation = next((a for a in affiliations if a["role_type"] == "wrestler"), None)
    coach_affiliation = next((a for a in affiliations if a["role_type"] == "coach"), None)
    
    if wrestler_affiliation:
        response["primary_affiliation"] = {
            "type": "wrestler",
            "school": wrestler_affiliation["school_name"],
            "location": wrestler_affiliation["school_location"], 
            "year": wrestler_affiliation["year"],
            "weight_class": wrestler_affiliation["weight_class"]
        }
    elif coach_affiliation:
        response["primary_affiliation"] = {
            "type": "coach",
            "school": coach_affiliation["school_name"],
            "location": coach_affiliation["school_location"],
            "year": coach_affiliation["year"]
        }
    
    return response


@router.get("/persons/{person_id}/wrestler")
async def get_person_wrestler_data(person_id: str, db: Database = Depends(get_db)):
    """Get detailed wrestler data for a person"""
    
    # Verify person exists and has wrestler role
    role_query = """
    SELECT role_id FROM role 
    WHERE person_id = $1 AND role_type = 'wrestler'
    """
    
    wrestler_role = await db.fetch_one(role_query, person_id)
    if not wrestler_role:
        raise HTTPException(status_code=404, detail="Person is not a wrestler")
    
    # Get wrestler statistics (placeholder for when match data is available)
    stats = {
        "total_matches": 0,
        "wins": 0,
        "losses": 0,
        "win_percentage": 0.0,
        "pins": 0,
        "tech_falls": 0,
        "major_decisions": 0
    }
    
    # Get participation history
    participation_query = """
    SELECT 
        part.year,
        part.weight_class,
        part.seed,
        s.name as school_name,
        s.location as school_location,
        t.name as tournament_name,
        t.location as tournament_location
    FROM participant part
    JOIN school s ON part.school_id = s.school_id
    LEFT JOIN tournament t ON t.year = part.year
    WHERE part.role_id = $1
    ORDER BY part.year DESC
    """
    
    participation = await db.fetch_all(participation_query, wrestler_role["role_id"])
    
    return {
        "person_id": person_id,
        "stats": stats,
        "participation_history": [
            {
                "year": p["year"],
                "weight_class": p["weight_class"],
                "seed": p["seed"],
                "school": p["school_name"],
                "school_location": p["school_location"],
                "tournament": p["tournament_name"],
                "tournament_location": p["tournament_location"]
            }
            for p in participation
        ],
        "matches": []  # Will be populated when match data is available
    }


@router.get("/persons/{person_id}/coach") 
async def get_person_coach_data(person_id: str, db: Database = Depends(get_db)):
    """Get detailed coaching data for a person"""
    
    # Verify person exists and has coach role
    role_query = """
    SELECT role_id FROM role
    WHERE person_id = $1 AND role_type = 'coach'
    """
    
    coach_role = await db.fetch_one(role_query, person_id)
    if not coach_role:
        raise HTTPException(status_code=404, detail="Person is not a coach")
    
    # Get coaching history (placeholder structure)
    coaching_history = {
        "current_position": None,
        "coaching_record": {
            "total_seasons": 0,
            "total_wins": 0,
            "total_losses": 0,
            "win_percentage": 0.0
        },
        "career_highlights": [],
        "coached_wrestlers": []
    }
    
    return {
        "person_id": person_id,
        "coaching_data": coaching_history
    }