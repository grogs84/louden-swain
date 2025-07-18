from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any
from app.database.database import get_db

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
        # Search wrestlers using the same structure as DuckDB
        wrestler_query = text("""
        WITH wrestler_summary AS (
            SELECT 
                p.person_id,
                p.first_name,
                p.last_name,
                pt.weight_class,
                pt.year,
                s.name as school_name,
                s.location as school_location,
                ROW_NUMBER() OVER (PARTITION BY p.person_id ORDER BY pt.year DESC) as rn
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            LEFT JOIN school s ON pt.school_id = s.school_id
            WHERE r.role_type = 'wrestler'
            AND (
                p.first_name ILIKE :search_term OR 
                p.last_name ILIKE :search_term OR
                CONCAT(p.first_name, ' ', p.last_name) ILIKE :search_term
            )
        )
        SELECT 
            person_id,
            first_name,
            last_name,
            weight_class,
            year,
            school_name,
            school_location
        FROM wrestler_summary 
        WHERE rn = 1
        ORDER BY last_name, first_name
        LIMIT :limit
        """)
        
        wrestler_result = await db.execute(wrestler_query, {
            "search_term": f"%{q}%",
            "limit": limit
        })
        
        for row in wrestler_result:
            results["wrestlers"].append({
                "type": "wrestler",
                "id": row.person_id,
                "name": f"{row.first_name} {row.last_name}",
                "additional_info": f"{row.school_name or 'Unknown School'} - {row.weight_class or 'N/A'}lbs",
                "first_name": row.first_name,
                "last_name": row.last_name,
                "weight_class": row.weight_class,
                "year": row.year,
                "school": row.school_name,
                "school_name": row.school_name
            })
        
        # Search schools
        school_query = text("""
        SELECT 
            s.school_id,
            s.name,
            s.location,
            COUNT(DISTINCT pt.participant_id) as total_participants
        FROM school s
        LEFT JOIN participant pt ON s.school_id = pt.school_id
        WHERE s.name ILIKE :search_term
        GROUP BY s.school_id, s.name, s.location
        ORDER BY total_participants DESC
        LIMIT :limit
        """)
        
        school_result = await db.execute(school_query, {
            "search_term": f"%{q}%",
            "limit": limit
        })
        
        for row in school_result:
            results["schools"].append({
                "type": "school",
                "id": row.school_id,
                "name": row.name,
                "additional_info": f"{row.location or 'Unknown Location'} - {row.total_participants} wrestlers",
                "location": row.location,
                "total_participants": row.total_participants
            })
        
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        return results
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
        # Build dynamic query with filters
        where_conditions = [
            "(p.first_name ILIKE :search_term OR p.last_name ILIKE :search_term OR CONCAT(p.first_name, ' ', p.last_name) ILIKE :search_term)"
        ]
        params = {"search_term": f"%{q}%", "limit": limit}
        
        if weight_class:
            where_conditions.append("pt.weight_class = :weight_class")
            params["weight_class"] = weight_class
        
        if school_id:
            where_conditions.append("pt.school_id = :school_id")
            params["school_id"] = school_id
        
        where_clause = " AND ".join(where_conditions)
        
        wrestler_query = text(f"""
        WITH wrestler_summary AS (
            SELECT 
                p.person_id,
                p.first_name,
                p.last_name,
                pt.weight_class,
                pt.year,
                s.name as school_name,
                s.location as school_location,
                ROW_NUMBER() OVER (PARTITION BY p.person_id ORDER BY pt.year DESC) as rn
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            LEFT JOIN school s ON pt.school_id = s.school_id
            WHERE r.role_type = 'wrestler' AND {where_clause}
        )
        SELECT 
            person_id,
            first_name,
            last_name,
            weight_class,
            year,
            school_name,
            school_location
        FROM wrestler_summary 
        WHERE rn = 1
        ORDER BY last_name, first_name
        LIMIT :limit
        """)
        
        result = await db.execute(wrestler_query, params)
        
        return [
            {
                "id": row.person_id,
                "name": f"{row.first_name} {row.last_name}",
                "first_name": row.first_name,
                "last_name": row.last_name,
                "weight_class": row.weight_class,
                "year": row.year,
                "school": row.school_name or "Unknown School",
                "school_name": row.school_name,
                "school_location": row.school_location
            } for row in result
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
        # Build dynamic query with filters
        where_conditions = ["s.name ILIKE :search_term"]
        params = {"search_term": f"%{q}%", "limit": limit}
        
        if state:
            where_conditions.append("s.location ILIKE :state")
            params["state"] = f"%{state}%"
        
        if conference:
            # Note: conference might not be in our schema, but we'll include the filter logic
            where_conditions.append("s.conference ILIKE :conference")
            params["conference"] = f"%{conference}%"
        
        where_clause = " AND ".join(where_conditions)
        
        school_query = text(f"""
        SELECT 
            s.school_id,
            s.name,
            s.location,
            COUNT(DISTINCT pt.participant_id) as total_participants
        FROM school s
        LEFT JOIN participant pt ON s.school_id = pt.school_id
        WHERE {where_clause}
        GROUP BY s.school_id, s.name, s.location
        ORDER BY total_participants DESC, s.name
        LIMIT :limit
        """)
        
        result = await db.execute(school_query, params)
        
        return [
            {
                "id": row.school_id,
                "name": row.name,
                "location": row.location,
                "total_participants": row.total_participants,
                "additional_info": f"{row.location or 'Unknown Location'} - {row.total_participants} wrestlers"
            } for row in result
        ]
        
    except Exception as e:
        return [{"error": f"School search failed: {str(e)}"}]
