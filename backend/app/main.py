from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config import settings
from app.database.database import get_db
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
        
        # Test a simple query
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        
        return {
            "status": "success",
            "database": "connected",
            "test_query_result": result,
            "connection_type": "asyncpg"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }

@app.get("/test-supabase")
async def test_supabase_connection():
    """Test Supabase connection and basic queries"""
    try:
        from app.database.database import get_db
        from sqlalchemy import text
        
        # Get database session
        db = None
        async for session in get_db():
            db = session
            break
        
        if not db:
            return {"error": "Could not get database session"}
        
        # Test a simple query
        result = await db.execute(text("SELECT COUNT(*) as person_count FROM person LIMIT 1"))
        person_count = result.scalar()
        
        return {
            "status": "success",
            "database": "supabase",
            "person_count": person_count,
            "connection_type": "sqlalchemy + asyncpg"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Supabase connection test failed: {str(e)}"
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

@app.get("/debug/check-spencer")
async def debug_check_spencer():
    """Check if Spencer Lee exists in database"""
    try:
        from app.database.database import get_db
        db = None
        async for session in get_db():
            db = session
            break
        
        if not db:
            return {"error": "Could not get database session"}
        
        # Check for Spencer Lee by UUID
        from sqlalchemy import text
        uuid_query = text("SELECT person_id, first_name, last_name FROM person WHERE person_id = :id")
        result = await db.execute(uuid_query, {"id": "5ccf054b-6630-494e-beff-e9c4b8e3bb6a"})
        spencer_by_uuid = result.fetchone()
        
        # Check for Spencer Lee by name
        name_query = text("SELECT person_id, first_name, last_name FROM person WHERE first_name ILIKE '%spencer%' AND last_name ILIKE '%lee%' LIMIT 5")
        result = await db.execute(name_query)
        spencer_by_name = result.fetchall()
        
        return {
            "spencer_by_uuid": dict(spencer_by_uuid) if spencer_by_uuid else None,
            "spencer_by_name": [(row[0], row[1], row[2]) for row in spencer_by_name],
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }

@app.get("/debug/sample-people")
async def debug_sample_people():
    """Get a sample of people from the database"""
    try:
        from app.database.database import get_db
        db = None
        async for session in get_db():
            db = session
            break
        
        if not db:
            return {"error": "Could not get database session"}
        
        # Get first 10 people
        from sqlalchemy import text
        result = await db.execute(text("""
            SELECT person_id, first_name, last_name 
            FROM person 
            ORDER BY last_name, first_name 
            LIMIT 10
        """))
        people = result.fetchall()
        
        return {
            "sample_people": [
                {
                    "person_id": p.person_id,
                    "first_name": p.first_name,
                    "last_name": p.last_name
                }
                for p in people
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/spencer-variations")
async def debug_spencer_variations():
    """Look for Spencer Lee with different name variations"""
    try:
        from app.database.database import get_db
        db = None
        async for session in get_db():
            db = session
            break
        
        if not db:
            return {"error": "Could not get database session"}
        
        from sqlalchemy import text
        # Look for anyone with Spencer in first name and Lee in last name
        result = await db.execute(text("""
            SELECT person_id, first_name, last_name 
            FROM person 
            WHERE first_name ILIKE '%spencer%' 
            OR last_name ILIKE '%lee%'
            ORDER BY last_name, first_name 
            LIMIT 20
        """))
        people = result.fetchall()
        
        return {
            "spencer_lee_variants": [
                {
                    "person_id": p.person_id,
                    "first_name": p.first_name,
                    "last_name": p.last_name
                }
                for p in people
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/check-roles/{person_id}")
async def debug_check_roles(person_id: str):
    """Check what roles exist for a specific person"""
    try:
        from app.database.database import get_db
        db = None
        async for session in get_db():
            db = session
            break
        
        if not db:
            return {"error": "Could not get database session"}
        
        from sqlalchemy import text
        # Check roles for this person
        result = await db.execute(text("""
            SELECT r.role_id, r.role_type, r.person_id
            FROM role r
            WHERE r.person_id = :person_id
        """), {"person_id": person_id})
        roles = result.fetchall()
        
        # Check participants for this person
        result2 = await db.execute(text("""
            SELECT pt.role_id, pt.weight_class, pt.year, pt.school_id
            FROM role r
            JOIN participant pt ON r.role_id = pt.role_id
            WHERE r.person_id = :person_id
        """), {"person_id": person_id})
        participants = result2.fetchall()
        
        return {
            "person_id": person_id,
            "roles": [
                {
                    "role_id": r.role_id,
                    "role_type": r.role_type,
                    "person_id": r.person_id
                }
                for r in roles
            ],
            "participants": [
                {
                    "role_id": p.role_id,
                    "weight_class": p.weight_class,
                    "year": p.year,
                    "school_id": p.school_id
                }
                for p in participants
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/wrestler/{wrestler_id}")
async def debug_wrestler_data(wrestler_id: str, db: AsyncSession = Depends(get_db)):
    """Debug endpoint to check wrestler data in detail"""
    try:
        # Check if person exists
        person_query = text("SELECT person_id, first_name, last_name FROM person WHERE person_id = :wrestler_id")
        result = await db.execute(person_query, {"wrestler_id": wrestler_id})
        person = result.fetchone()
        
        if not person:
            return {"error": "Person not found", "wrestler_id": wrestler_id}
        
        # Check roles for this person
        roles_query = text("SELECT role_id, role_type FROM role WHERE person_id = :wrestler_id")
        result = await db.execute(roles_query, {"wrestler_id": wrestler_id})
        roles = result.fetchall()
        
        # Check participants for this person
        participants_query = text("""
            SELECT pt.role_id, pt.weight_class, pt.year, pt.school_id 
            FROM participant pt 
            JOIN role r ON pt.role_id = r.role_id 
            WHERE r.person_id = :wrestler_id
        """)
        result = await db.execute(participants_query, {"wrestler_id": wrestler_id})
        participants = result.fetchall()
        
        # Check matches for this person
        matches_query = text("""
            SELECT m.match_id, m.year 
            FROM match m 
            JOIN participant pt ON (m.participant1_role_id = pt.role_id OR m.participant2_role_id = pt.role_id)
            JOIN role r ON pt.role_id = r.role_id 
            WHERE r.person_id = :wrestler_id 
            LIMIT 5
        """)
        result = await db.execute(matches_query, {"wrestler_id": wrestler_id})
        matches = result.fetchall()
        
        return {
            "person": {
                "person_id": person.person_id,
                "first_name": person.first_name,
                "last_name": person.last_name
            },
            "roles": [{"role_id": r.role_id, "role_type": r.role_type} for r in roles],
            "participants": [{"role_id": p.role_id, "weight_class": p.weight_class, "year": p.year, "school_id": p.school_id} for p in participants],
            "matches": [{"match_id": m.match_id, "year": m.year} for m in matches],
            "match_count": len(matches)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/schema")
async def debug_schema():
    """Debug endpoint to check table schemas"""
    try:
        from app.database.database import get_db
        db = None
        async for session in get_db():
            db = session
            break
        
        # Check table structures
        tables_info = {}
        
        # Check person table structure
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'person' 
            ORDER BY ordinal_position
        """))
        tables_info['person'] = [(row[0], row[1]) for row in result.fetchall()]
        
        # Check match table structure
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'match' 
            ORDER BY ordinal_position
        """))
        tables_info['match'] = [(row[0], row[1]) for row in result.fetchall()]
        
        # Check participant table structure
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'participant' 
            ORDER BY ordinal_position
        """))
        tables_info['participant'] = [(row[0], row[1]) for row in result.fetchall()]
        
        # Check role table structure
        result = await db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'role' 
            ORDER BY ordinal_position
        """))
        tables_info['role'] = [(row[0], row[1]) for row in result.fetchall()]
        
        return {
            "tables": tables_info,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }
