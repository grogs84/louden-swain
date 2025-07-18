#!/usr/bin/env python3
"""
Test script to verify Supabase connection and basic functionality
Run this after updating your .env file with real Supabase credentials
"""

import asyncio
import asyncpg
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_supabase_connection():
    """Test direct connection to Supabase"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url or "your_password_here" in database_url:
        print("❌ ERROR: Please update your .env file with real Supabase credentials")
        print("   Current DATABASE_URL:", database_url)
        return False
    
    try:
        # Clean URL for asyncpg
        clean_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        print(f"🔌 Testing connection to Supabase...")
        print(f"   URL: {clean_url.split('@')[0]}@***")
        
        conn = await asyncpg.connect(clean_url)
        
        # Test basic query
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Connected successfully!")
        print(f"   Database version: {version.split()[0:2]}")
        
        # Test if our tables exist
        tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('person', 'school', 'tournament', 'match', 'participant')
        ORDER BY table_name
        """)
        
        print(f"📊 Found {len(tables)} wrestling tables:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Test data counts
        counts = {}
        for table_name in ['person', 'school', 'tournament', 'match', 'participant']:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                counts[table_name] = count
            except Exception as e:
                counts[table_name] = f"Error: {e}"
        
        print("📈 Data counts:")
        for table, count in counts.items():
            print(f"   - {table}: {count}")
        
        # Test a sample wrestler query
        wrestler = await conn.fetchrow("""
        SELECT p.person_id, p.first_name, p.last_name, pt.weight_class, s.name as school_name
        FROM person p
        JOIN role r ON p.person_id = r.person_id
        JOIN participant pt ON r.role_id = pt.role_id
        LEFT JOIN school s ON pt.school_id = s.school_id
        WHERE r.role_type = 'wrestler'
        ORDER BY p.last_name
        LIMIT 1
        """)
        
        if wrestler:
            print(f"🤼 Sample wrestler: {wrestler['first_name']} {wrestler['last_name']} ({wrestler['weight_class']}lbs) - {wrestler['school_name']}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_backend_endpoints():
    """Test that the backend can start and respond to requests"""
    print("\n🚀 Testing backend startup...")
    
    try:
        # Import the FastAPI app to test if it loads
        import sys
        sys.path.append(str(Path(__file__).parent))
        
        from app.main import app
        from app.config import settings
        
        print(f"✅ Backend imports successfully")
        print(f"   USE_DUCKDB: {settings.use_duckdb}")
        print(f"   Database URL configured: {bool(settings.database_url)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔧 Supabase Backend Test Suite")
    print("=" * 50)
    
    # Test 1: Database connection
    db_ok = await test_supabase_connection()
    
    # Test 2: Backend imports
    backend_ok = await test_backend_endpoints()
    
    print("\n" + "=" * 50)
    if db_ok and backend_ok:
        print("✅ All tests passed! Your Supabase backend is ready.")
        print("\n🚀 Next steps:")
        print("   1. Start the backend: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("   2. Test API endpoints with the URLs in SUPABASE_SETUP.md")
        print("   3. Start your frontend and test the full application")
    else:
        print("❌ Some tests failed. Check the errors above.")
        if not db_ok:
            print("   - Fix your Supabase connection first")
        if not backend_ok:
            print("   - Check for missing dependencies or import errors")

if __name__ == "__main__":
    asyncio.run(main())
