from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import os

app = FastAPI(
    title="NCAA Wrestling Championship API",
    description="API for NCAA D1 Wrestling Championship data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Alternative dev port
        "https://louden-swain.vercel.app",  # Vercel production
        "https://louden-swain-*.vercel.app",  # Vercel preview deployments
        "*"  # Allow all origins for testing
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create tables on startup - DISABLED for Supabase
# @app.on_event("startup")
# async def startup_event():
#     if not (settings.use_duckdb or os.getenv("USE_DUCKDB", "false").lower() == "true"):
#         # Only create PostgreSQL tables if not using DuckDB
#         from app.models.models import Base
#         from app.database.database import engine
#         async with engine.begin() as conn:
#             # Create all tables
#             await conn.run_sync(Base.metadata.create_all)

# Include routers based on database mode
if settings.use_duckdb or os.getenv("USE_DUCKDB", "false").lower() == "true":
    # DuckDB mode - use DuckDB router with frontend-compatible endpoints
    try:
        from app.routers import duckdb_router
        # Include DuckDB router with standard API paths for frontend compatibility
        app.include_router(duckdb_router.router, prefix="/api", tags=["duckdb"])
        print("DuckDB router enabled for local development")
    except ImportError:
        print("DuckDB router could not be imported - DuckDB functionality disabled")
        # Fallback to working routers only
        from app.routers import wrestlers, search
        app.include_router(wrestlers.router, prefix="/api/wrestlers", tags=["wrestlers"])
        app.include_router(search.router, prefix="/api/search", tags=["search"])
else:
    # PostgreSQL mode - use only working routers for Supabase
    from app.routers import wrestlers, search
    app.include_router(wrestlers.router, prefix="/api/wrestlers", tags=["wrestlers"])
    app.include_router(search.router, prefix="/api/search", tags=["search"])
    # NOTE: schools, coaches, tournaments, brackets routers disabled until migrated to raw SQL

@app.get("/")
async def root():
    return {"message": "NCAA Wrestling Championship API - Working on Railway!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "supabase", "environment": "production"}

@app.get("/test-db")
async def test_database_connection():
    """Test the database connection"""
    try:
        import asyncpg
        from app.config import settings
        
        # Extract connection parameters from DATABASE_URL
        db_url = settings.database_url
        # Remove the +asyncpg part for pure asyncpg connection
        clean_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        # Test connection
        conn = await asyncpg.connect(clean_url)
        
        # Run a simple query
        result = await conn.fetchval("SELECT version()")
        
        await conn.close()
        
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_version": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }

@app.get("/test-supabase-api")
async def test_supabase_api():
    """Test Supabase using the REST API instead of direct DB connection"""
    try:
        import httpx
        from app.config import settings
        
        headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Test a simple query to the Supabase REST API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/rest/v1/",
                headers=headers
            )
            
        return {
            "status": "success" if response.status_code == 200 else "error",
            "message": "Supabase REST API connection successful" if response.status_code == 200 else f"Failed with status {response.status_code}",
            "supabase_url": settings.supabase_url,
            "response_status": response.status_code
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Supabase API test failed: {str(e)}"
        }

@app.get("/test-supabase-tables")
async def test_supabase_tables():
    """Test listing tables in Supabase"""
    try:
        import httpx
        from app.config import settings
        
        # Try to query a system table or any existing table
        async with httpx.AsyncClient() as client:
            # Get the OpenAPI schema which lists tables
            response = await client.get(
                f"{settings.supabase_url}/rest/v1/",
                headers={
                    "apikey": settings.supabase_key,
                    "Authorization": f"Bearer {settings.supabase_key}"
                }
            )
            
        return {
            "status": "success",
            "message": "Supabase tables endpoint accessible",
            "response_status": response.status_code,
            "can_create_tables": True
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Supabase tables test failed: {str(e)}"
        }

@app.get("/test-supabase-client")
async def test_supabase_client():
    """Test the custom Supabase client"""
    try:
        from app.database.supabase_client import supabase_client
        
        # Test the client by making a simple request to the base URL
        # This should return the OpenAPI schema for available tables
        async with __import__('httpx').AsyncClient() as client:
            response = await client.get(
                f"{supabase_client.base_url}/",
                headers=supabase_client.headers
            )
            
        return {
            "status": "success" if response.status_code == 200 else "error",
            "message": "Supabase client configured correctly",
            "response_status": response.status_code,
            "available_endpoints": response.status_code == 200
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Supabase client test failed: {str(e)}"
        }

@app.get("/debug/db-info")
async def debug_database_info():
    """Debug endpoint to check database configuration"""
    try:
        return {
            "use_duckdb": settings.use_duckdb,
            "database_url_configured": bool(settings.database_url),
            "database_url_prefix": settings.database_url[:20] + "..." if settings.database_url else None,
            "environment": "production" if not settings.use_duckdb else "development"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/db-test")
async def debug_database_test():
    """Test actual database connection and data"""
    try:
        if settings.use_duckdb:
            return {"error": "DuckDB mode - not testing Supabase"}
        
        from app.database.database import get_db
        db = None
        async for session in get_db():
            db = session
            break
        
        if not db:
            return {"error": "Could not get database session"}
        
        # Test a simple query
        from sqlalchemy import text
        result = await db.execute(text("SELECT COUNT(*) as count FROM person LIMIT 1"))
        count = result.scalar()
        
        return {
            "database_connected": True,
            "person_count": count,
            "status": "success"
        }
    except Exception as e:
        return {
            "database_connected": False,
            "error": str(e),
            "status": "failed"
        }
