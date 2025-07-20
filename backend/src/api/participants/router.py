"""
Participant endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_participants():
    """List participants"""
    return {"message": "List participants - to be implemented"}


@router.get("/{participant_id}")
async def get_participant(participant_id: str):
    """Get participant by ID"""
    return {"message": f"Get participant {participant_id} - to be implemented"}


@router.post("/")
async def create_participant():
    """Create new participant"""
    return {"message": "Create participant - to be implemented"}


@router.put("/{participant_id}")
async def update_participant(participant_id: str):
    """Update participant"""
    return {"message": f"Update participant {participant_id} - to be implemented"}


@router.delete("/{participant_id}")
async def delete_participant(participant_id: str):
    """Delete participant"""
    return {"message": f"Delete participant {participant_id} - to be implemented"}
