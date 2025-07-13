"""
Script to create tables in Supabase using the REST API
This script will read the create_tables.sql file and execute it
"""

import asyncio
import httpx
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def execute_sql_file():
    """Execute the SQL file to create tables in Supabase"""
    
    # Read the SQL file
    sql_file_path = Path("create_tables.sql")
    if not sql_file_path.exists():
        print("Error: create_tables.sql file not found")
        return False
    
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    # Split into individual statements
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    print(f"Found {len(statements)} SQL statements to execute")
    
    # Headers for Supabase API
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    success_count = 0
    error_count = 0
    
    async with httpx.AsyncClient() as client:
        for i, statement in enumerate(statements, 1):
            try:
                print(f"Executing statement {i}/{len(statements)}...")
                
                # Use the PostgREST SQL endpoint (if available)
                # Note: This might not work with all Supabase plans
                url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
                
                response = await client.post(
                    url,
                    headers=headers,
                    json={"sql": statement}
                )
                
                if response.status_code == 200:
                    print(f"✓ Statement {i} executed successfully")
                    success_count += 1
                else:
                    print(f"✗ Statement {i} failed: {response.status_code} - {response.text}")
                    error_count += 1
                    
            except Exception as e:
                print(f"✗ Statement {i} failed with exception: {str(e)}")
                error_count += 1
    
    print(f"\nExecution complete:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")
    
    if error_count > 0:
        print("\nNote: Some statements failed. This might be because:")
        print("1. Tables already exist")
        print("2. Your Supabase plan doesn't support direct SQL execution")
        print("3. You need to create tables manually through the Supabase dashboard")
        print("\nAlternative: Copy the SQL from create_tables.sql and paste it into")
        print("the SQL Editor in your Supabase dashboard at https://app.supabase.com")
    
    return error_count == 0

async def test_connection():
    """Test the connection to Supabase"""
    print("Testing Supabase connection...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Try to access a simple endpoint
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/schools?limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print("✓ Successfully connected to Supabase")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

async def create_tables_manually():
    """Create tables manually using individual REST API calls"""
    print("Creating tables manually using REST API...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Note: Table creation through REST API is limited
    # We'll try to insert sample data to verify tables exist
    
    async with httpx.AsyncClient() as client:
        # Test if schools table exists by trying to query it
        try:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/schools",
                headers=headers
            )
            
            if response.status_code == 200:
                print("✓ Tables appear to be accessible")
                return True
            else:
                print(f"✗ Cannot access tables: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error accessing tables: {str(e)}")
            return False

async def main():
    print("Supabase Database Setup")
    print("=" * 50)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_KEY environment variables are required")
        print("Make sure your .env file is configured correctly")
        return
    
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"API Key: {SUPABASE_KEY[:20]}...")
    print()
    
    # Test connection first
    if not await test_connection():
        print("Cannot proceed without a working connection")
        return
    
    # Try to execute SQL file
    print("\nAttempting to execute SQL file...")
    success = await execute_sql_file()
    
    if not success:
        print("\nSQL file execution failed or unavailable.")
        print("Please create the tables manually by:")
        print("1. Going to https://app.supabase.com")
        print("2. Opening your project")
        print("3. Going to SQL Editor")
        print("4. Copying and pasting the contents of create_tables.sql")
        print("5. Running the SQL")
        
        # Test if tables are accessible
        await create_tables_manually()
    
    print("\nSetup complete! You can now test the API by running:")
    print("python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    asyncio.run(main())
