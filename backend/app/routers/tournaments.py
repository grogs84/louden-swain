from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.database.supabase_client import supabase_client
from app.models.schemas import Tournament, TournamentCreate

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_tournaments(
    skip: int = 0,
    limit: int = 100,
    year: Optional[int] = None,
    division: Optional[str] = None,
):
    """Get all tournaments with optional filtering"""
    try:
        # Build filters
        filters = {}
        if year:
            filters["year"] = year
        if division:
            filters["division"] = division
        
        tournaments = await supabase_client.select(
            table="tournaments",
            filters=filters,
            limit=limit
        )
        
        # Apply skip manually for now
        if skip > 0:
            tournaments = tournaments[skip:]
        
        return tournaments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tournaments: {str(e)}")

@router.get("/{tournament_id}", response_model=dict)
async def get_tournament(tournament_id: int):
    """Get a specific tournament by ID"""
    try:
        tournaments = await supabase_client.select(
            table="tournaments",
            filters={"id": tournament_id}
        )
        
        if not tournaments:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        return tournaments[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tournament: {str(e)}")

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tournament(tournament: TournamentCreate):
    """Create a new tournament"""
    try:
        result = await supabase_client.insert(
            table="tournaments",
            data=tournament.dict()
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create tournament")
        
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating tournament: {str(e)}")

@router.get("/{tournament_id}/brackets")
async def get_tournament_brackets(tournament_id: int):
    """Get bracket data for a tournament"""
    try:
        # Check if tournament exists
        tournaments = await supabase_client.select(
            table="tournaments",
            filters={"id": tournament_id}
        )
        
        if not tournaments:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        # Get matches for this tournament organized by weight class
        matches = await supabase_client.select(
            table="matches",
            filters={"tournament_id": tournament_id}
        )
        
        # Organize matches into bracket structure
        brackets = {}
        for match in matches:
            weight_class = match.get('weight_class', 'Unknown')
            if weight_class not in brackets:
                brackets[weight_class] = {
                    "weight_class": weight_class,
                    "rounds": {}
                }
            
            round_num = match.get('round', 1)
            if round_num not in brackets[weight_class]["rounds"]:
                brackets[weight_class]["rounds"][round_num] = []
            
            brackets[weight_class]["rounds"][round_num].append({
                "id": match.get("id"),
                "wrestler1_id": match.get("wrestler1_id"),
                "wrestler2_id": match.get("wrestler2_id"),
                "winner_id": match.get("winner_id"),
                "match_type": match.get("match_type"),
                "score": match.get("score"),
                "bout_number": match.get("bout_number")
            })
        
        return {
            "tournament_id": tournament_id,
            "tournament_name": tournaments[0].get('name'),
            "year": tournaments[0].get('year'),
            "brackets": list(brackets.values())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tournament brackets: {str(e)}")
