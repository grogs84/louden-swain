from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.database.supabase_client import supabase_client
from app.models.schemas import SearchResults, SearchResult

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def search_all(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum results per category"),
):
    """Search across wrestlers, schools, and coaches"""
    
    try:
        results = {
            "query": q,
            "wrestlers": [],
            "schools": [],
            "coaches": []
        }
        
        # Search wrestlers by name using improved text search
        wrestler_matches = []
        
        # Search by first name
        first_name_matches = await supabase_client.select_with_text_search(
            table="wrestlers",
            columns="*, schools(name, conference)",
            search_column="first_name",
            search_term=q,
            limit=limit
        )
        
        # Search by last name
        last_name_matches = await supabase_client.select_with_text_search(
            table="wrestlers",
            columns="*, schools(name, conference)",
            search_column="last_name",
            search_term=q,
            limit=limit
        )
        
        # Combine and deduplicate results
        all_wrestler_matches = first_name_matches + last_name_matches
        seen_ids = set()
        
        for wrestler in all_wrestler_matches:
            wrestler_id = wrestler.get("id")
            if wrestler_id not in seen_ids:
                seen_ids.add(wrestler_id)
                wrestler_matches.append({
                    "type": "wrestler",
                    "id": wrestler_id,
                    "name": f"{wrestler.get('first_name', '')} {wrestler.get('last_name', '')}",
                    "additional_info": f"{wrestler.get('schools', {}).get('name', 'Unknown School')} - {wrestler.get('weight_class', 'N/A')}lbs",
                    "weight_class": wrestler.get('weight_class'),
                    "year": wrestler.get('year'),
                    "school_id": wrestler.get('school_id')
                })
        
        results["wrestlers"] = wrestler_matches[:limit]
        
        # Search schools by name
        school_name_matches = await supabase_client.select_with_text_search(
            table="schools",
            search_column="name",
            search_term=q,
            limit=limit
        )
        
        # Search schools by conference
        school_conference_matches = await supabase_client.select_with_text_search(
            table="schools",
            search_column="conference",
            search_term=q,
            limit=limit
        )
        
        # Combine and deduplicate school results
        all_school_matches = school_name_matches + school_conference_matches
        seen_school_ids = set()
        school_matches = []
        
        for school in all_school_matches:
            school_id = school.get("id")
            if school_id not in seen_school_ids:
                seen_school_ids.add(school_id)
                school_matches.append({
                    "type": "school",
                    "id": school_id,
                    "name": school.get('name', ''),
                    "additional_info": f"{school.get('conference', 'N/A')} - {school.get('state', 'N/A')}",
                    "conference": school.get('conference'),
                    "state": school.get('state'),
                    "division": school.get('division')
                })
        
        results["schools"] = school_matches[:limit]
        
        # Search coaches by name
        coach_first_matches = await supabase_client.select_with_text_search(
            table="coaches",
            columns="*, schools(name, conference)",
            search_column="first_name",
            search_term=q,
            limit=limit
        )
        
        coach_last_matches = await supabase_client.select_with_text_search(
            table="coaches",
            columns="*, schools(name, conference)",
            search_column="last_name",
            search_term=q,
            limit=limit
        )
        
        # Combine and deduplicate coach results
        all_coach_matches = coach_first_matches + coach_last_matches
        seen_coach_ids = set()
        coach_matches = []
        
        for coach in all_coach_matches:
            coach_id = coach.get("id")
            if coach_id not in seen_coach_ids:
                seen_coach_ids.add(coach_id)
                coach_matches.append({
                    "type": "coach",
                    "id": coach_id,
                    "name": f"{coach.get('first_name', '')} {coach.get('last_name', '')}",
                    "additional_info": f"{coach.get('schools', {}).get('name', 'Unknown School')} - {coach.get('title', 'Coach')}",
                    "title": coach.get('title'),
                    "school_id": coach.get('school_id')
                })
        
        results["coaches"] = coach_matches[:limit]
        
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
    limit: int = Query(20, le=100, description="Maximum results")
):
    """Search wrestlers with additional filters"""
    
    try:
        # Get all wrestlers with school info
        wrestlers = await supabase_client.select(
            table="wrestlers",
            columns="*, schools(name, conference, division)"
        )
        
        matches = []
        for wrestler in wrestlers:
            # Text search
            full_name = f"{wrestler.get('first_name', '')} {wrestler.get('last_name', '')}".lower()
            if q.lower() not in full_name:
                continue
            
            # Apply filters
            if weight_class and wrestler.get('weight_class') != weight_class:
                continue
            if school_id and wrestler.get('school_id') != school_id:
                continue
            
            matches.append({
                "id": wrestler.get("id"),
                "name": f"{wrestler.get('first_name', '')} {wrestler.get('last_name', '')}",
                "weight_class": wrestler.get('weight_class'),
                "year": wrestler.get('year'),
                "school": wrestler.get('schools', {}).get('name', 'Unknown School'),
                "school_id": wrestler.get('school_id'),
                "conference": wrestler.get('schools', {}).get('conference'),
                "division": wrestler.get('schools', {}).get('division')
            })
        
        return matches[:limit]
        
    except Exception as e:
        return [{"error": f"Wrestler search failed: {str(e)}"}]

@router.get("/schools", response_model=List[Dict[str, Any]])
async def search_schools(
    q: str = Query(..., min_length=2, description="Search query"),
    state: str = Query(None, description="Filter by state"),
    conference: str = Query(None, description="Filter by conference"),
    limit: int = Query(20, le=100, description="Maximum results")
):
    """Search schools with additional filters"""
    
    try:
        schools = await supabase_client.select(table="schools")
        
        matches = []
        for school in schools:
            # Text search
            school_name = school.get('name', '').lower()
            if q.lower() not in school_name:
                continue
            
            # Apply filters
            if state and school.get('state', '').lower() != state.lower():
                continue
            if conference and school.get('conference', '').lower() != conference.lower():
                continue
            
            matches.append({
                "id": school.get("id"),
                "name": school.get('name'),
                "state": school.get('state'),
                "conference": school.get('conference'),
                "division": school.get('division'),
                "city": school.get('city'),
                "website": school.get('website')
            })
        
        return matches[:limit]
        
    except Exception as e:
        return [{"error": f"School search failed: {str(e)}"}]
