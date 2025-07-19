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
    """Get all wrestlers with complete info"""
    
    # Enhanced query to get complete wrestler data including weight_class, year, and school
    query = text("""
        SELECT DISTINCT
            p.person_id,
            p.first_name,
            p.last_name,
            pt.weight_class,
            pt.year,
            s.name as school_name
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        JOIN participant pt ON r.role_id = pt.role_id
        LEFT JOIN school s ON pt.school_id = s.school_id
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
            "weight_class": wrestler.weight_class,
            "year": wrestler.year,
            "school": {
                "name": title_case_name(wrestler.school_name) if wrestler.school_name else None
            } if wrestler.school_name else None
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
        # Enhanced query to get complete wrestler info including weight_class, year, and school
        query = text("""
            SELECT DISTINCT
                p.person_id::text as person_id,
                p.first_name,
                p.last_name,
                pt.weight_class,
                pt.year,
                s.name as school_name
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            LEFT JOIN school s ON pt.school_id = s.school_id
            WHERE r.role_type = 'wrestler' AND p.person_id::text = :wrestler_id
            LIMIT 1
        """)
        
        result = await db.execute(query, {"wrestler_id": str(wrestler_id)})
        wrestler = result.fetchone()
        
        if not wrestler:
            raise HTTPException(status_code=404, detail="Wrestler not found")
        
        # Get actual statistics instead of hardcoded zeros
        stats_query = text("""
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN pm.is_winner = true THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pm.is_winner = false THEN 1 ELSE 0 END) as losses
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            JOIN participant_match pm ON pt.participant_id = pm.participant_id
            WHERE p.person_id::text = :wrestler_id AND r.role_type = 'wrestler'
        """)
        
        stats_result = await db.execute(stats_query, {"wrestler_id": str(wrestler_id)})
        stats = stats_result.fetchone()
        
        total_matches = stats.total_matches if stats else 0
        wins = stats.wins if stats else 0
        losses = stats.losses if stats else 0
        win_percentage = round((wins / total_matches * 100), 1) if total_matches > 0 else 0
        
        return {
            "id": wrestler.person_id,
            "person_id": wrestler.person_id,
            "first_name": title_case_name(wrestler.first_name),
            "last_name": title_case_name(wrestler.last_name),
            "weight_class": wrestler.weight_class,
            "year": wrestler.year,
            "school": {
                "name": title_case_name(wrestler.school_name) if wrestler.school_name else None
            } if wrestler.school_name else None,
            "stats": {
                "total_matches": total_matches,
                "wins": wins,
                "losses": losses,
                "win_percentage": win_percentage
            },
            "matches": []
        }
    except Exception as e:
        # Return minimal data if query fails, but still try to get basic info
        try:
            basic_query = text("""
                SELECT 
                    p.person_id::text as person_id,
                    p.first_name,
                    p.last_name
                FROM person p
                JOIN role r ON p.person_id = r.person_id
                WHERE r.role_type = 'wrestler' AND p.person_id::text = :wrestler_id
                LIMIT 1
            """)
            
            basic_result = await db.execute(basic_query, {"wrestler_id": str(wrestler_id)})
            basic_wrestler = basic_result.fetchone()
            
            if basic_wrestler:
                return {
                    "id": basic_wrestler.person_id,
                    "person_id": basic_wrestler.person_id,
                    "first_name": title_case_name(basic_wrestler.first_name),
                    "last_name": title_case_name(basic_wrestler.last_name),
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
        except:
            pass
            
        # Final fallback
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
    """Get wrestler statistics matching DuckDB format for frontend compatibility"""
    try:
        # Get match statistics using the participant_match bridge table with better result type mapping
        stats_query = text("""
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN pm.is_winner = true THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pm.is_winner = false THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN pm.result_type = 'fall' THEN 1 ELSE 0 END) as falls,
                SUM(CASE WHEN pm.result_type = 'dec' THEN 1 ELSE 0 END) as decisions,
                SUM(CASE WHEN pm.result_type = 'tech fall' OR pm.result_type = 'tech_fall' THEN 1 ELSE 0 END) as tech_falls,
                SUM(CASE WHEN pm.result_type = 'maj dec' OR pm.result_type = 'major_dec' THEN 1 ELSE 0 END) as major_decisions
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            JOIN participant_match pm ON pt.participant_id = pm.participant_id
            WHERE p.person_id::text = :wrestler_id AND r.role_type = 'wrestler'
        """)
        
        result = await db.execute(stats_query, {"wrestler_id": str(wrestler_id)})
        stats = result.fetchone()
        
        if stats and stats.total_matches > 0:
            total_matches = stats.total_matches or 0
            wins = stats.wins or 0
            losses = stats.losses or 0
            falls = stats.falls or 0
            decisions = stats.decisions or 0
            tech_falls = stats.tech_falls or 0
            major_decisions = stats.major_decisions or 0
            win_percentage = round((wins / total_matches * 100), 1) if total_matches > 0 else 0
        else:
            total_matches = wins = losses = falls = decisions = tech_falls = major_decisions = win_percentage = 0
        
        # Return format matching DuckDB version for frontend compatibility
        return {
            "total_matches": total_matches,
            "wins": wins,
            "losses": losses,
            "pins": falls,  # Map falls to pins for frontend
            "tech_falls": tech_falls,
            "major_decisions": major_decisions,
            "win_percentage": win_percentage
        }
        
    except Exception as e:
        # Return same format as DuckDB version with zeros
        return {
            "total_matches": 0,
            "wins": 0,
            "losses": 0,
            "pins": 0,
            "tech_falls": 0,
            "major_decisions": 0,
            "win_percentage": 0
        }

@router.get("/{wrestler_id}/matches", response_model=List[Dict[str, Any]])
async def get_wrestler_matches(
    wrestler_id: Union[int, str],
    limit: int = 10,
    skip: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get wrestler match history using participant_match table"""
    
    try:
        # Get match history with opponent info using participant_match bridge table
        matches_query = text("""
            SELECT DISTINCT
                m.match_id,
                m.round,
                m.round_order,
                pm.is_winner,
                pm.score,
                pm.result_type,
                pm.fall_time,
                t.name as tournament_name,
                t.year as tournament_year,
                t.location as tournament_location,
                -- Get opponent info
                p_opp.person_id as opponent_id,
                p_opp.first_name as opponent_first_name,
                p_opp.last_name as opponent_last_name,
                s_opp.name as opponent_school_name
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            JOIN participant pt ON r.role_id = pt.role_id
            JOIN participant_match pm ON pt.participant_id = pm.participant_id
            JOIN match m ON pm.match_id = m.match_id
            LEFT JOIN tournament t ON m.tournament_id = t.tournament_id
            -- Get opponent participant in same match
            LEFT JOIN participant_match pm_opp ON m.match_id = pm_opp.match_id AND pm_opp.participant_id != pm.participant_id
            LEFT JOIN participant pt_opp ON pm_opp.participant_id = pt_opp.participant_id
            LEFT JOIN role r_opp ON pt_opp.role_id = r_opp.role_id
            LEFT JOIN person p_opp ON r_opp.person_id = p_opp.person_id
            LEFT JOIN school s_opp ON pt_opp.school_id = s_opp.school_id
            WHERE p.person_id = :wrestler_id AND r.role_type = 'wrestler'
            ORDER BY t.year DESC, m.round_order ASC
            OFFSET :skip LIMIT :limit
        """)
        
        result = await db.execute(matches_query, {
            "wrestler_id": wrestler_id, 
            "skip": skip, 
            "limit": limit
        })
        matches = result.fetchall()
        
        # Format matches for response
        formatted_matches = []
        for match in matches:
            result_display = "W" if match.is_winner else "L"
            
            formatted_match = {
                "match_id": match.match_id,
                "tournament": {
                    "name": title_case_name(match.tournament_name) if match.tournament_name else "Unknown Tournament",
                    "year": match.tournament_year,
                    "location": title_case_name(match.tournament_location) if match.tournament_location else None
                },
                "round": match.round,
                "result": result_display,
                "score": str(match.score) if match.score else "N/A",
                "result_type": title_case_name(match.result_type) if match.result_type else "Decision",
                "fall_time": match.fall_time,
                "opponent": {
                    "id": match.opponent_id,
                    "first_name": title_case_name(match.opponent_first_name) if match.opponent_first_name else None,
                    "last_name": title_case_name(match.opponent_last_name) if match.opponent_last_name else None,
                    "school": {
                        "name": title_case_name(match.opponent_school_name) if match.opponent_school_name else None
                    }
                }
            }
            formatted_matches.append(formatted_match)
        
        return formatted_matches
        
    except Exception as e:
        # Return empty matches if query fails
        return []
