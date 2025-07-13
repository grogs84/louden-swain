from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import asyncpg
from app.config import settings

app = FastAPI(
    title="NCAA Wrestling Championship API - Test",
    description="Simple API to test database connection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NCAA Wrestling Championship API - Test Version"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test-db")
async def test_database_connection():
    """Test the database connection without creating tables"""
    try:
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
