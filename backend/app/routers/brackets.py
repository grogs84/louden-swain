from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import json
from app.database.database import get_db
from app.models.models import Bracket as BracketModel, Tournament as TournamentModel, Match as MatchModel
from app.models.schemas import Bracket, BracketCreate, BracketUpdate, BracketWithTournament

router = APIRouter()

@router.get("/tournament/{tournament_id}", response_model=List[BracketWithTournament])
async def get_tournament_brackets(tournament_id: int, db: AsyncSession = Depends(get_db)):
    """Get all brackets for a tournament"""
    query = select(BracketModel).options(selectinload(BracketModel.tournament)).where(BracketModel.tournament_id == tournament_id)
    result = await db.execute(query)
    brackets = result.scalars().all()
    return brackets

@router.get("/{bracket_id}", response_model=BracketWithTournament)
async def get_bracket(bracket_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific bracket by ID"""
    query = select(BracketModel).options(selectinload(BracketModel.tournament)).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    return bracket

@router.get("/{bracket_id}/data")
async def get_bracket_data(bracket_id: int, db: AsyncSession = Depends(get_db)):
    """Get bracket data formatted for react-brackets"""
    query = select(BracketModel).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    # If bracket_data exists, parse it
    if bracket.bracket_data:
        try:
            return json.loads(bracket.bracket_data)
        except json.JSONDecodeError:
            return {"error": "Invalid bracket data format"}
    
    # Otherwise, build bracket from matches
    matches_query = select(MatchModel).options(
        selectinload(MatchModel.wrestler1),
        selectinload(MatchModel.wrestler2)
    ).where(MatchModel.bracket_id == bracket_id)
    matches_result = await db.execute(matches_query)
    matches = matches_result.scalars().all()
    
    # Organize matches into rounds for react-brackets format
    rounds = {}
    for match in matches:
        round_name = match.round_name or "Round 1"
        if round_name not in rounds:
            rounds[round_name] = []
        
        # Format match for react-brackets
        formatted_match = {
            "id": match.id,
            "participants": [],
            "winner": None
        }
        
        # Add wrestler1
        if match.wrestler1:
            formatted_match["participants"].append({
                "id": match.wrestler1.id,
                "name": f"{match.wrestler1.first_name} {match.wrestler1.last_name}",
                "isWinner": match.winner_id == match.wrestler1.id
            })
        
        # Add wrestler2
        if match.wrestler2:
            formatted_match["participants"].append({
                "id": match.wrestler2.id,
                "name": f"{match.wrestler2.first_name} {match.wrestler2.last_name}",
                "isWinner": match.winner_id == match.wrestler2.id
            })
        
        rounds[round_name].append(formatted_match)
    
    # Convert to react-brackets format (ordered rounds)
    ordered_rounds = []
    for round_name in sorted(rounds.keys()):
        ordered_rounds.append(rounds[round_name])
    
    bracket_data = {
        "rounds": ordered_rounds,
        "weight_class": bracket.weight_class,
        "tournament_id": bracket.tournament_id
    }
    
    return bracket_data

@router.post("/", response_model=Bracket, status_code=status.HTTP_201_CREATED)
async def create_bracket(bracket: BracketCreate, db: AsyncSession = Depends(get_db)):
    """Create a new bracket"""
    db_bracket = BracketModel(**bracket.dict())
    db.add(db_bracket)
    await db.commit()
    await db.refresh(db_bracket)
    return db_bracket

@router.put("/{bracket_id}", response_model=Bracket)
async def update_bracket(
    bracket_id: int,
    bracket_update: BracketUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a bracket"""
    query = select(BracketModel).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    update_data = bracket_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bracket, field, value)
    
    await db.commit()
    await db.refresh(bracket)
    return bracket

@router.put("/{bracket_id}/data")
async def update_bracket_data(bracket_id: int, bracket_data: dict, db: AsyncSession = Depends(get_db)):
    """Update bracket data (for saving bracket changes)"""
    query = select(BracketModel).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    # Update bracket data
    bracket.bracket_data = json.dumps(bracket_data)
    await db.commit()
    
    return {"message": "Bracket data updated successfully"}

@router.delete("/{bracket_id}")
async def delete_bracket(bracket_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a bracket"""
    query = select(BracketModel).where(BracketModel.id == bracket_id)
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        raise HTTPException(status_code=404, detail="Bracket not found")
    
    await db.delete(bracket)
    await db.commit()
    return {"message": "Bracket deleted successfully"}

@router.get("/weight-class/{weight_class}/year/{year}")
async def get_brackets_by_weight_and_year(weight_class: int, year: int, db: AsyncSession = Depends(get_db)):
    """Get brackets for a specific weight class and year"""
    query = select(BracketModel).options(selectinload(BracketModel.tournament)).join(
        TournamentModel
    ).where(
        BracketModel.weight_class == weight_class,
        TournamentModel.year == year
    )
    result = await db.execute(query)
    brackets = result.scalars().all()
    return brackets

@router.get("/data/tournament/{tournament_id}/weight/{weight_class}")
async def get_bracket_data_by_tournament_weight(
    tournament_id: int, 
    weight_class: int, 
    db: AsyncSession = Depends(get_db)
):
    """Get bracket data formatted for bracket visualization by tournament and weight class"""
    # Find bracket for this tournament and weight class
    query = select(BracketModel).where(
        BracketModel.tournament_id == tournament_id,
        BracketModel.weight_class == weight_class
    )
    result = await db.execute(query)
    bracket = result.scalar_one_or_none()
    
    if not bracket:
        # Return mock bracket data for demonstration if no real data exists
        return {
            "rounds": [
                {
                    "title": "Quarterfinals",
                    "seeds": [
                        {
                            "id": 1,
                            "date": "2024-03-21",
                            "teams": [
                                {"name": "John Smith (Oklahoma State)", "id": 1, "isWinner": True},
                                {"name": "Mike Johnson (Iowa)", "id": 2, "isWinner": False}
                            ]
                        },
                        {
                            "id": 2,
                            "date": "2024-03-21",
                            "teams": [
                                {"name": "Dave Wilson (Penn State)", "id": 3, "isWinner": True},
                                {"name": "Tom Brown (Ohio State)", "id": 4, "isWinner": False}
                            ]
                        }
                    ]
                },
                {
                    "title": "Semifinals", 
                    "seeds": [
                        {
                            "id": 3,
                            "date": "2024-03-22",
                            "teams": [
                                {"name": "John Smith (Oklahoma State)", "id": 1, "isWinner": True},
                                {"name": "Dave Wilson (Penn State)", "id": 3, "isWinner": False}
                            ]
                        }
                    ]
                },
                {
                    "title": "Finals",
                    "seeds": [
                        {
                            "id": 4,
                            "date": "2024-03-23",
                            "teams": [
                                {"name": "John Smith (Oklahoma State)", "id": 1, "isWinner": True},
                                {"name": "TBD", "id": null, "isWinner": False}
                            ]
                        }
                    ]
                }
            ],
            "weight_class": weight_class,
            "tournament_id": tournament_id
        }
    
    # If bracket_data exists, parse it
    if bracket.bracket_data:
        try:
            return json.loads(bracket.bracket_data)
        except json.JSONDecodeError:
            return {"error": "Invalid bracket data format"}
    
    # Otherwise, build bracket from matches (existing logic)
    matches_query = select(MatchModel).options(
        selectinload(MatchModel.wrestler1),
        selectinload(MatchModel.wrestler2)
    ).where(MatchModel.bracket_id == bracket.id)
    matches_result = await db.execute(matches_query)
    matches = matches_result.scalars().all()
    
    # Organize matches into rounds for bracket format
    rounds = {}
    for match in matches:
        round_name = match.round_name or "Round 1"
        if round_name not in rounds:
            rounds[round_name] = []
        
        # Format match for bracket visualization
        formatted_match = {
            "id": match.id,
            "date": match.match_date.strftime("%Y-%m-%d") if match.match_date else "TBD",
            "teams": []
        }
        
        # Add wrestler1
        if match.wrestler1:
            formatted_match["teams"].append({
                "id": match.wrestler1.id,
                "name": f"{match.wrestler1.first_name} {match.wrestler1.last_name}",
                "isWinner": match.winner_id == match.wrestler1.id
            })
        
        # Add wrestler2  
        if match.wrestler2:
            formatted_match["teams"].append({
                "id": match.wrestler2.id,
                "name": f"{match.wrestler2.first_name} {match.wrestler2.last_name}",
                "isWinner": match.winner_id == match.wrestler2.id
            })
        
        rounds[round_name].append(formatted_match)
    
    # Convert to ordered rounds
    ordered_rounds = []
    round_order = ["Quarterfinals", "Semifinals", "Finals"]
    for round_name in round_order:
        if round_name in rounds:
            ordered_rounds.append({
                "title": round_name,
                "seeds": rounds[round_name]
            })
    
    bracket_data = {
        "rounds": ordered_rounds,
        "weight_class": bracket.weight_class,
        "tournament_id": bracket.tournament_id
    }
    
    return bracket_data
