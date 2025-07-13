from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import wrestlers, schools, coaches, tournaments, brackets, search

app = FastAPI(
    title="NCAA Wrestling Championship API",
    description="API for NCAA D1 Wrestling Championship data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(wrestlers.router, prefix="/api/wrestlers", tags=["wrestlers"])
app.include_router(schools.router, prefix="/api/schools", tags=["schools"])
app.include_router(coaches.router, prefix="/api/coaches", tags=["coaches"])
app.include_router(tournaments.router, prefix="/api/tournaments", tags=["tournaments"])
app.include_router(brackets.router, prefix="/api/brackets", tags=["brackets"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "NCAA Wrestling Championship API - Basic Test"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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
