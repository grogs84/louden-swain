from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
import json
from app.database.supabase_client import supabase_client
from app.models.schemas import Bracket, BracketCreate, BracketWithTournament

router = APIRouter()

@router.get("/tournament/{tournament_id}", response_model=List[dict])
async def get_tournament_brackets(tournament_id: int):
    """Get all brackets for a tournament"""
    try:
        brackets = await supabase_client.select(
            table="brackets",
            columns="*, tournaments(name, year, division)",
            filters={"tournament_id": tournament_id}
        )
        
        return brackets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tournament brackets: {str(e)}")

@router.get("/{bracket_id}", response_model=dict)
async def get_bracket(bracket_id: int):
    """Get a specific bracket by ID"""
    try:
        brackets = await supabase_client.select(
            table="brackets",
            columns="*, tournaments(name, year, division)",
            filters={"id": bracket_id}
        )
        
        if not brackets:
            raise HTTPException(status_code=404, detail="Bracket not found")
        
        return brackets[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bracket: {str(e)}")

@router.get("/{bracket_id}/data")
async def get_bracket_data(bracket_id: int):
    """Get bracket data formatted for react-brackets"""
    try:
        brackets = await supabase_client.select(
            table="brackets",
            filters={"id": bracket_id}
        )
        
        if not brackets:
            raise HTTPException(status_code=404, detail="Bracket not found")
        
        bracket = brackets[0]
        
        # If bracket_data exists, parse it
        if bracket.get('bracket_data'):
            try:
                return json.loads(bracket['bracket_data'])
            except json.JSONDecodeError:
                return {"error": "Invalid bracket data format"}
        
        # Otherwise, build bracket from matches
        matches = await supabase_client.select(
            table="matches",
            columns="*, wrestler1:wrestlers!wrestler1_id(first_name, last_name), wrestler2:wrestlers!wrestler2_id(first_name, last_name)",
            filters={
                "tournament_id": bracket.get('tournament_id'),
                "weight_class": bracket.get('weight_class')
            }
        )
        
        # Organize matches into rounds for react-brackets format
        rounds = {}
        for match in matches:
            round_num = match.get('round', 1)
            if round_num not in rounds:
                rounds[round_num] = []
            
            # Format match for react-brackets
            formatted_match = {
                "id": match.get('id'),
                "participants": [],
                "winner": None
            }
            
            # Add wrestler1
            if match.get('wrestler1'):
                wrestler1_name = f"{match['wrestler1'].get('first_name', '')} {match['wrestler1'].get('last_name', '')}"
                formatted_match["participants"].append({
                    "id": match.get('wrestler1_id'),
                    "name": wrestler1_name.strip(),
                    "isWinner": match.get('winner_id') == match.get('wrestler1_id')
                })
            
            # Add wrestler2
            if match.get('wrestler2'):
                wrestler2_name = f"{match['wrestler2'].get('first_name', '')} {match['wrestler2'].get('last_name', '')}"
                formatted_match["participants"].append({
                    "id": match.get('wrestler2_id'),
                    "name": wrestler2_name.strip(),
                    "isWinner": match.get('winner_id') == match.get('wrestler2_id')
                })
            
            rounds[round_num].append(formatted_match)
        
        # Convert to react-brackets format
        bracket_data = {
            "rounds": [rounds[round_num] for round_num in sorted(rounds.keys())],
            "weight_class": bracket.get('weight_class'),
            "tournament_id": bracket.get('tournament_id')
        }
        
        return bracket_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bracket data: {str(e)}")

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_bracket(bracket: BracketCreate):
    """Create a new bracket"""
    try:
        result = await supabase_client.insert(
            table="brackets",
            data=bracket.dict()
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create bracket")
        
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bracket: {str(e)}")

@router.put("/{bracket_id}/data")
async def update_bracket_data(bracket_id: int, bracket_data: dict):
    """Update bracket data (for saving bracket changes)"""
    try:
        # Check if bracket exists
        existing = await supabase_client.select(
            table="brackets",
            filters={"id": bracket_id}
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Bracket not found")
        
        # Update bracket data
        result = await supabase_client.update(
            table="brackets",
            filters={"id": bracket_id},
            data={"bracket_data": json.dumps(bracket_data)}
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update bracket data")
        
        return {"message": "Bracket data updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating bracket data: {str(e)}")

@router.get("/weight-class/{weight_class}/year/{year}")
async def get_brackets_by_weight_and_year(weight_class: int, year: int):
    """Get brackets for a specific weight class and year"""
    try:
        brackets = await supabase_client.select(
            table="brackets",
            columns="*, tournaments(name, year, division, date)",
            filters={"weight_class": weight_class}
        )
        
        # Filter by year (since we can't easily filter on joined table with current client)
        filtered_brackets = [
            bracket for bracket in brackets 
            if bracket.get('tournaments', {}).get('year') == year
        ]
        
        return filtered_brackets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching brackets: {str(e)}")
