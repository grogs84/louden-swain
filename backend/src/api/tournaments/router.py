"""
Tournament CRUD endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_tournaments():
    """List tournaments"""
    return {"message": "List tournaments - to be implemented"}


@router.get("/{tournament_id}")
async def get_tournament(tournament_id: str):
    """Get tournament by ID"""
    return {"message": f"Get tournament {tournament_id} - to be implemented"}


@router.post("/")
async def create_tournament():
    """Create new tournament"""
    return {"message": "Create tournament - to be implemented"}


@router.put("/{tournament_id}")
async def update_tournament(tournament_id: str):
    """Update tournament"""
    return {"message": f"Update tournament {tournament_id} - to be implemented"}


@router.delete("/{tournament_id}")
async def delete_tournament(tournament_id: str):
    """Delete tournament"""
    return {"message": f"Delete tournament {tournament_id} - to be implemented"}
