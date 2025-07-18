from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import text, func
from typing import List, Optional, Union
from app.database.database import get_db
from app.models.models import Wrestler as WrestlerModel
from app.models.schemas import Wrestler, WrestlerCreate, WrestlerUpdate, WrestlerWithSchool

router = APIRouter()

@router.get("/", response_model=List[WrestlerWithSchool])
async def get_wrestlers(
    skip: int = 0,
    limit: int = 100,
    weight_class: Optional[int] = None,
    school_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all wrestlers with optional filtering"""
    query = select(WrestlerModel).options(selectinload(WrestlerModel.school))
    
    if weight_class:
        query = query.where(WrestlerModel.weight_class == weight_class)
    if school_id:
        query = query.where(WrestlerModel.school_id == school_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    wrestlers = result.scalars().all()
    return wrestlers

@router.get("/{wrestler_id}")
async def get_wrestler(wrestler_id: Union[int, str], db: AsyncSession = Depends(get_db)):
    """Get a specific wrestler by ID (supports both numeric IDs and UUIDs)"""
    
    # Handle both numeric IDs and UUIDs
    try:
        # Try to convert to int first for sequential IDs
        wrestler_numeric_id = int(wrestler_id)
        
        # Use raw SQL to get wrestler data with proper UUID support
        query = text("""
        SELECT 
            person.person_id,
            person.first_name,
            person.last_name,
            p.weight_class,
            p.year,
            s.name as school_name,
            s.location as school_location
        FROM person
        JOIN role r ON person.person_id = r.person_id
        JOIN participant p ON r.role_id = p.role_id
        LEFT JOIN school s ON p.school_id = s.school_id
        WHERE person.person_id = (SELECT person_id FROM person WHERE id = :wrestler_id)
          AND r.role_type = 'wrestler'
        LIMIT 1
        """)
        params = {"wrestler_id": wrestler_numeric_id}
        
    except ValueError:
        # Treat as UUID
        query = text("""
        SELECT 
            person.person_id,
            person.first_name,
            person.last_name,
            p.weight_class,
            p.year,
            s.name as school_name,
            s.location as school_location
        FROM person
        JOIN role r ON person.person_id = r.person_id
        JOIN participant p ON r.role_id = p.role_id
        LEFT JOIN school s ON p.school_id = s.school_id
        WHERE person.person_id = :wrestler_id
          AND r.role_type = 'wrestler'
        LIMIT 1
        """)
        params = {"wrestler_id": str(wrestler_id)}
    
    result = await db.execute(query, params)
    wrestler_data = result.first()
    
    if not wrestler_data:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    # Return data in expected format
    return {
        "id": wrestler_data.person_id,
        "person_id": wrestler_data.person_id,
        "first_name": wrestler_data.first_name,
        "last_name": wrestler_data.last_name,
        "weight_class": int(wrestler_data.weight_class) if wrestler_data.weight_class else None,
        "year": str(wrestler_data.year) if wrestler_data.year else None,
        "school_id": None,  # We don't have this from our query
        "school": {
            "id": None,  # We don't have this from our query
            "name": wrestler_data.school_name,
            "location": wrestler_data.school_location
        } if wrestler_data.school_name else None
    }

@router.post("/", response_model=Wrestler, status_code=status.HTTP_201_CREATED)
async def create_wrestler(wrestler: WrestlerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new wrestler"""
    db_wrestler = WrestlerModel(**wrestler.dict())
    db.add(db_wrestler)
    await db.commit()
    await db.refresh(db_wrestler)
    return db_wrestler

@router.put("/{wrestler_id}", response_model=Wrestler)
async def update_wrestler(
    wrestler_id: int,
    wrestler_update: WrestlerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a wrestler"""
    query = select(WrestlerModel).where(WrestlerModel.id == wrestler_id)
    result = await db.execute(query)
    wrestler = result.scalar_one_or_none()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    update_data = wrestler_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wrestler, field, value)
    
    await db.commit()
    await db.refresh(wrestler)
    return wrestler

@router.delete("/{wrestler_id}")
async def delete_wrestler(wrestler_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a wrestler"""
    query = select(WrestlerModel).where(WrestlerModel.id == wrestler_id)
    result = await db.execute(query)
    wrestler = result.scalar_one_or_none()
    
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    await db.delete(wrestler)
    await db.commit()
    return {"message": "Wrestler deleted successfully"}

@router.get("/{wrestler_id}/matches")
async def get_wrestler_matches(wrestler_id: Union[int, str], db: AsyncSession = Depends(get_db)):
    """Get all matches for a specific wrestler with proper tournament round sorting"""
    
    # Handle both numeric IDs and UUIDs
    try:
        # Try to convert to int first for sequential IDs
        wrestler_numeric_id = int(wrestler_id)
        wrestler_condition = "person.person_id = (SELECT person_id FROM person WHERE id = :wrestler_id)"
        params = {"wrestler_id": wrestler_numeric_id}
    except ValueError:
        # Treat as UUID
        wrestler_condition = "person.person_id = :wrestler_id"
        params = {"wrestler_id": str(wrestler_id)}
    
    # Complex SQL query with proper tournament round sorting
    query = text(f"""
    WITH data_table AS (
        SELECT
            p.year,
            p.weight_class,
            m.round,
            person.first_name as fname1,
            person.last_name as lname1,
            pm.is_winner,
            pm.score as score1,
            pm.result_type,
            pm.fall_time,
            per1.first_name as fname2,
            per1.last_name as lname2,
            pm1.score as score2,
            s1.name as school1,
            s2.name as school2,
            t.name as tournament_name
        FROM person
        JOIN role r ON r.person_id = person.person_id
        JOIN participant p ON r.role_id = p.role_id
        JOIN participant_match pm ON pm.participant_id = p.participant_id
        JOIN match m ON pm.match_id = m.match_id
        JOIN participant_match pm1 ON pm1.match_id = m.match_id 
            AND pm1.participant_id != p.participant_id
        JOIN participant p1 ON p1.participant_id = pm1.participant_id
        JOIN role r1 ON r1.role_id = p1.role_id
        JOIN person per1 ON per1.person_id = r1.person_id
        LEFT JOIN school s1 ON s1.school_id = p.school_id
        LEFT JOIN school s2 ON s2.school_id = p1.school_id
        LEFT JOIN tournament t ON t.tournament_id = m.tournament_id
        WHERE {wrestler_condition}
    )
    SELECT
        d.year as year,
        d.weight_class as weight,
        d.round as round,
        d.fname1 || ' ' || d.lname1 as name,
        d.is_winner as winner,
        d.result_type as match_result,
        CASE 
            WHEN d.result_type = 'fall' THEN 'Fall ' || COALESCE(d.fall_time::text, '')
            WHEN d.result_type = 'mfft' THEN 'Medical Forfeit'
            WHEN d.result_type = 'fft' THEN 'Forfeit'
            WHEN d.result_type = 'dq' THEN 'Disqualification'
            WHEN d.score1 IS NOT NULL AND d.score2 IS NOT NULL THEN d.score1::text || ' - ' || d.score2::text
            ELSE d.result_type
        END as score,
        d.fname2 as opponent_first_name,
        d.lname2 as opponent_last_name,
        d.fname2 || ' ' || d.lname2 as opponent,
        d.school2 as opponent_school,
        d.tournament_name as tournament
    FROM data_table d
    ORDER BY d.year ASC, 
        CASE 
            WHEN d.round = 'champ 64' THEN 1
            WHEN d.round = 'champ 32' THEN 2
            WHEN d.round = 'champ 16' THEN 3
            WHEN d.round = 'champ 8' THEN 4
            WHEN d.round = 'champ 4' THEN 5
            WHEN d.round = '1st' THEN 6
            WHEN d.round = '2nd' THEN 7
            WHEN d.round = 'consi 32 #2' THEN 8
            WHEN d.round = 'consi 16 #1' THEN 9
            WHEN d.round = 'consi 16 #2' THEN 10
            WHEN d.round = 'consi 8 #1' THEN 11
            WHEN d.round = 'consi 8 #2' THEN 12
            WHEN d.round = 'consi 4 #1' THEN 13
            WHEN d.round = 'consi 4 #2' THEN 14
            WHEN d.round = '3rd' THEN 15
            WHEN d.round = '5th' THEN 15
            WHEN d.round = '7th' THEN 15
            WHEN d.round IN ('r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7') THEN 16
            -- Fallback patterns for variations in naming
            WHEN d.round LIKE '%64%' THEN 1
            WHEN d.round LIKE '%32%' THEN 2
            WHEN d.round LIKE '%16%' THEN 3
            WHEN d.round LIKE '%quarter%' OR d.round LIKE '%8%' THEN 4
            WHEN d.round LIKE '%semi%' OR d.round LIKE '%4%' THEN 5
            WHEN d.round LIKE '%final%' AND d.round NOT LIKE '%semi%' THEN 6
            WHEN d.round LIKE '%1st%' OR d.round LIKE '%first%' THEN 6
            WHEN d.round LIKE '%2nd%' OR d.round LIKE '%second%' THEN 7
            WHEN d.round LIKE '%3rd%' OR d.round LIKE '%third%' THEN 15
            WHEN d.round LIKE '%consol%' THEN 10
            WHEN d.round LIKE '%pre%' OR d.round LIKE '%qualifier%' THEN 0
            ELSE 99
        END
    """)
    
    result = await db.execute(query, params)
    matches = []
    
    for row in result:
        match_dict = dict(row._mapping)
        
        # Convert winner boolean to result string for frontend compatibility
        if 'winner' in match_dict:
            match_dict['result'] = 'W' if match_dict['winner'] else 'L'
        
        # Ensure weight_class is available for frontend
        if 'weight' in match_dict and 'weight_class' not in match_dict:
            match_dict['weight_class'] = match_dict['weight']
            
        matches.append(match_dict)
    
    return matches

@router.get("/{wrestler_id}/stats")
async def get_wrestler_stats(wrestler_id: Union[int, str], db: AsyncSession = Depends(get_db)):
    """Get detailed statistics for a wrestler including match history"""
    
    # Handle both numeric IDs and UUIDs
    try:
        # Try to convert to int first for sequential IDs
        wrestler_numeric_id = int(wrestler_id)
        wrestler_condition = "person.person_id = (SELECT person_id FROM person WHERE id = :wrestler_id)"
        params = {"wrestler_id": wrestler_numeric_id}
    except ValueError:
        # Treat as UUID
        wrestler_condition = "person.person_id = :wrestler_id"
        params = {"wrestler_id": str(wrestler_id)}
    
    # Get basic wrestler info
    wrestler_query = text(f"""
    SELECT 
        person.person_id,
        person.first_name,
        person.last_name,
        p.weight_class,
        p.year,
        s.name as school_name,
        s.location as school_location
    FROM person
    JOIN role r ON person.person_id = r.person_id
    JOIN participant p ON r.role_id = p.role_id
    LEFT JOIN school s ON p.school_id = s.school_id
    WHERE {wrestler_condition} AND r.role_type = 'wrestler'
    LIMIT 1
    """)
    
    # Get match statistics with proper tech fall calculation
    stats_query = text(f"""
    SELECT 
        COUNT(*) as total_matches,
        SUM(CASE WHEN pm.is_winner THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN NOT pm.is_winner THEN 1 ELSE 0 END) as losses,
        COUNT(CASE WHEN pm.result_type = 'fall' THEN 1 END) as pins,
        COUNT(CASE WHEN pm.result_type = 'tech fall' OR 
                      (pm.is_winner AND pm.score IS NOT NULL AND pm2.score IS NOT NULL 
                       AND (pm.score - pm2.score) >= 15) THEN 1 END) as tech_falls,
        COUNT(CASE WHEN pm.result_type = 'major dec' OR 
                      (pm.is_winner AND pm.score IS NOT NULL AND pm2.score IS NOT NULL 
                       AND (pm.score - pm2.score) >= 8 AND (pm.score - pm2.score) < 15) THEN 1 END) as major_decisions,
        COUNT(CASE WHEN pm.result_type = 'dec' OR 
                      (pm.is_winner AND pm.score IS NOT NULL AND pm2.score IS NOT NULL 
                       AND (pm.score - pm2.score) >= 1 AND (pm.score - pm2.score) < 8) THEN 1 END) as decisions
    FROM participant_match pm
    JOIN participant pt ON pm.participant_id = pt.participant_id
    JOIN role r ON pt.role_id = r.role_id
    JOIN person ON r.person_id = person.person_id
    JOIN match m ON pm.match_id = m.match_id
    LEFT JOIN participant_match pm2 ON pm2.match_id = m.match_id AND pm2.participant_id != pm.participant_id
    WHERE {wrestler_condition}
    """)
    
    wrestler_result = await db.execute(wrestler_query, params)
    wrestler_info = wrestler_result.first()
    
    if not wrestler_info:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    stats_result = await db.execute(stats_query, params)
    stats_info = stats_result.first()
    
    # Calculate win percentage
    total_matches = stats_info.total_matches if stats_info else 0
    wins = stats_info.wins if stats_info else 0
    win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0
    
    return {
        "person_id": wrestler_info.person_id,
        "first_name": wrestler_info.first_name,
        "last_name": wrestler_info.last_name,
        "weight_class": wrestler_info.weight_class,
        "year": wrestler_info.year,
        "school_name": wrestler_info.school_name,
        "school_location": wrestler_info.school_location,
        "total_matches": total_matches,
        "wins": wins,
        "losses": stats_info.losses if stats_info else 0,
        "win_percentage": win_percentage,
        "pins": stats_info.pins if stats_info else 0,
        "tech_falls": stats_info.tech_falls if stats_info else 0,
        "major_decisions": stats_info.major_decisions if stats_info else 0,
        "decisions": stats_info.decisions if stats_info else 0
    }
