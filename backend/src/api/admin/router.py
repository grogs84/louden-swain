"""
Admin-specific endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/users")
async def list_users():
    """List all users (admin only)"""
    return {"message": "List users - to be implemented"}


@router.get("/system/health")
async def system_health():
    """System health check (admin only)"""
    return {"message": "System health - to be implemented"}


@router.post("/data/import")
async def import_data():
    """Import data (admin only)"""
    return {"message": "Data import - to be implemented"}


@router.post("/data/export")
async def export_data():
    """Export data (admin only)"""
    return {"message": "Data export - to be implemented"}
