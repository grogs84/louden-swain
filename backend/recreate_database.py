"""
Script to recreate tables and populate with sample data using direct PostgreSQL connection
This replaces the old Supabase REST API approach
"""

import asyncio
import asyncpg
import os
from datetime import datetime, date

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Convert SQLAlchemy URL format to standard PostgreSQL format for asyncpg
if DATABASE_URL and DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

async def recreate_tables():
    """Drop existing tables and recreate them"""
    print("Recreating tables...")
    
    # SQL to drop all tables (in correct order due to foreign keys)
    drop_sql = """
    DROP TABLE IF EXISTS matches CASCADE;
    DROP TABLE IF EXISTS brackets CASCADE;
    DROP TABLE IF EXISTS tournaments CASCADE;
    DROP TABLE IF EXISTS coaches CASCADE;
    DROP TABLE IF EXISTS wrestlers CASCADE;
    DROP TABLE IF EXISTS schools CASCADE;
    """
    
    # SQL to create all tables
    create_sql = """
    -- Schools table
    CREATE TABLE schools (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        conference VARCHAR(100),
        state VARCHAR(2),
        city VARCHAR(100),
        logo_url TEXT,
        website TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Wrestlers table
    CREATE TABLE wrestlers (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        weight_class INTEGER NOT NULL,
        school_id INTEGER REFERENCES schools(id),
        year VARCHAR(20),
        hometown VARCHAR(100),
        state VARCHAR(2),
        height VARCHAR(10),
        weight INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Coaches table
    CREATE TABLE coaches (
        id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        school_id INTEGER REFERENCES schools(id),
        position VARCHAR(100),
        years_experience INTEGER,
        bio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tournaments table
    CREATE TABLE tournaments (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        year INTEGER NOT NULL,
        start_date DATE,
        end_date DATE,
        location VARCHAR(255),
        division VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Brackets table
    CREATE TABLE brackets (
        id SERIAL PRIMARY KEY,
        tournament_id INTEGER REFERENCES tournaments(id),
        weight_class INTEGER NOT NULL,
        bracket_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Matches table
    CREATE TABLE matches (
        id SERIAL PRIMARY KEY,
        tournament_id INTEGER REFERENCES tournaments(id),
        bracket_id INTEGER REFERENCES brackets(id),
        wrestler1_id INTEGER REFERENCES wrestlers(id),
        wrestler2_id INTEGER REFERENCES wrestlers(id),
        winner_id INTEGER REFERENCES wrestlers(id),
        match_type VARCHAR(50),
        result_type VARCHAR(50),
        score VARCHAR(20),
        round_number INTEGER,
        match_order INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for better performance
    CREATE INDEX idx_wrestlers_school_id ON wrestlers(school_id);
    CREATE INDEX idx_wrestlers_weight_class ON wrestlers(weight_class);
    CREATE INDEX idx_coaches_school_id ON coaches(school_id);
    CREATE INDEX idx_matches_tournament_id ON matches(tournament_id);
    CREATE INDEX idx_matches_wrestler1_id ON matches(wrestler1_id);
    CREATE INDEX idx_matches_wrestler2_id ON matches(wrestler2_id);
    """
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Drop existing tables
        await conn.execute(drop_sql)
        print("✓ Dropped existing tables")
        
        # Create new tables
        await conn.execute(create_sql)
        print("✓ Created new tables")
        
    except Exception as e:
        print(f"✗ Error recreating tables: {e}")
        raise
    finally:
        await conn.close()

async def insert_sample_data():
    """Insert comprehensive sample data"""
    print("Inserting sample data...")
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Insert schools
        schools_data = [
            ("Iowa State University", "Big 12", "IA", "Ames", None, "https://www.cyclones.com"),
            ("University of Iowa", "Big Ten", "IA", "Iowa City", None, "https://hawkeyesports.com"),
            ("Penn State University", "Big Ten", "PA", "University Park", None, "https://gopsusports.com"),
            ("Oklahoma State University", "Big 12", "OK", "Stillwater", None, "https://okstate.com"),
            ("Ohio State University", "Big Ten", "OH", "Columbus", None, "https://ohiostatebuckeyes.com"),
            ("University of Michigan", "Big Ten", "MI", "Ann Arbor", None, "https://mgoblue.com"),
            ("University of Nebraska", "Big Ten", "NE", "Lincoln", None, "https://huskers.com"),
            ("University of Wisconsin", "Big Ten", "WI", "Madison", None, "https://uwbadgers.com"),
            ("Virginia Tech", "ACC", "VA", "Blacksburg", None, "https://hokiesports.com"),
            ("North Carolina State", "ACC", "NC", "Raleigh", None, "https://gopack.com")
        ]
        
        school_ids = []
        for school_data in schools_data:
            school_id = await conn.fetchval(
                "INSERT INTO schools (name, conference, state, city, logo_url, website) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
                *school_data
            )
            school_ids.append(school_id)
        
        print(f"✓ Inserted {len(schools_data)} schools")
        
        # Insert wrestlers
        wrestlers_data = [
            # Penn State (school_id = 3)
            ("David", "Taylor", 165, school_ids[2], "Senior", "St. Paris", "OH", "5'8\"", 165),
            ("Kyle", "Dake", 174, school_ids[2], "Graduate", "Lansing", "NY", "5'10\"", 174),
            ("Bo", "Nickal", 184, school_ids[2], "Graduate", "Allen", "TX", "6'0\"", 184),
            ("Carter", "Starocci", 174, school_ids[2], "Junior", "Malvern", "PA", "5'11\"", 174),
            ("Roman", "Bravo-Young", 133, school_ids[2], "Senior", "Tucson", "AZ", "5'6\"", 133),
            
            # Iowa (school_id = 2)
            ("Spencer", "Lee", 125, school_ids[1], "Senior", "Murrysville", "PA", "5'4\"", 125),
            ("Jaydin", "Eierman", 141, school_ids[1], "Senior", "Lee's Summit", "MO", "5'7\"", 141),
            ("Alex", "Marinelli", 165, school_ids[1], "Senior", "Apple Valley", "MN", "5'8\"", 165),
            ("Michael", "Kemerer", 174, school_ids[1], "Senior", "Franklin Regional", "PA", "5'9\"", 174),
            ("Tony", "Cassioppi", 285, school_ids[1], "Junior", "Roscoe", "IL", "6'2\"", 285),
            
            # Oklahoma State (school_id = 4)
            ("Daton", "Fix", 133, school_ids[3], "Senior", "Sand Springs", "OK", "5'6\"", 133),
            ("Boo", "Lewallen", 141, school_ids[3], "Junior", "Westmoore", "OK", "5'8\"", 141),
            ("Dustin", "Plott", 174, school_ids[3], "Sophomore", "Broken Arrow", "OK", "5'10\"", 174),
            ("Derek", "White", 197, school_ids[3], "Senior", "York", "PA", "6'1\"", 197),
            
            # Ohio State (school_id = 5)
            ("Malik", "Heinselman", 125, school_ids[4], "Junior", "Lorain", "OH", "5'5\"", 125),
            ("Dylan", "D'Emilio", 133, school_ids[4], "Sophomore", "Bethel Park", "PA", "5'7\"", 133),
            ("Sammy", "Sasso", 149, school_ids[4], "Junior", "Nazareth", "PA", "5'8\"", 149),
            ("Kaleb", "Romero", 165, school_ids[4], "Junior", "Mechanicsburg", "OH", "5'9\"", 165),
            
            # Michigan (school_id = 6)
            ("Nick", "Suriano", 125, school_ids[5], "Senior", "Bergen Catholic", "NJ", "5'5\"", 125),
            ("Stevan", "Micic", 133, school_ids[5], "Senior", "Westland", "MI", "5'7\"", 133),
            ("Kanen", "Storr", 157, school_ids[5], "Sophomore", "Leslie", "MI", "5'9\"", 157),
            ("Cam", "Amine", 174, school_ids[5], "Senior", "Detroit", "MI", "5'10\"", 174)
        ]
        
        wrestler_ids = []
        for wrestler_data in wrestlers_data:
            wrestler_id = await conn.fetchval(
                "INSERT INTO wrestlers (first_name, last_name, weight_class, school_id, year, hometown, state, height, weight) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id",
                *wrestler_data
            )
            wrestler_ids.append(wrestler_id)
        
        print(f"✓ Inserted {len(wrestlers_data)} wrestlers")
        
        # Insert coaches
        coaches_data = [
            ("Cael", "Sanderson", school_ids[2], "Head Coach", 15, "Former Olympic Champion and NCAA standout"),
            ("Casey", "Cunningham", school_ids[2], "Associate Head Coach", 10, "Former Penn State wrestler"),
            ("Tom", "Brands", school_ids[1], "Head Coach", 25, "Former Olympic medalist"),
            ("Terry", "Brands", school_ids[1], "Associate Head Coach", 25, "Former Olympic competitor"),
            ("John", "Smith", school_ids[3], "Head Coach", 30, "Two-time Olympic Champion"),
            ("Pat", "Smith", school_ids[3], "Associate Head Coach", 20, "Former World Champion"),
            ("Tom", "Ryan", school_ids[4], "Head Coach", 20, "Long-time collegiate coach"),
            ("J", "Jaggers", school_ids[4], "Associate Head Coach", 15, "Former Ohio State wrestler"),
            ("Sean", "Bormet", school_ids[5], "Head Coach", 12, "Former Michigan wrestler"),
            ("Tony", "Robie", school_ids[5], "Associate Head Coach", 18, "Experienced collegiate coach")
        ]
        
        for coach_data in coaches_data:
            await conn.execute(
                "INSERT INTO coaches (first_name, last_name, school_id, position, years_experience, bio) VALUES ($1, $2, $3, $4, $5, $6)",
                *coach_data
            )
        
        print(f"✓ Inserted {len(coaches_data)} coaches")
        
        # Insert tournaments
        tournaments_data = [
            ("NCAA Division I Wrestling Championships", 2024, date(2024, 3, 21), date(2024, 3, 23), "Kansas City, MO", "Division I"),
            ("NCAA Division I Wrestling Championships", 2023, date(2023, 3, 16), date(2023, 3, 18), "Tulsa, OK", "Division I"),
            ("NCAA Division I Wrestling Championships", 2022, date(2022, 3, 17), date(2022, 3, 19), "Detroit, MI", "Division I"),
            ("Big Ten Wrestling Championships", 2024, date(2024, 3, 2), date(2024, 3, 3), "Minneapolis, MN", "Conference"),
            ("Big 12 Wrestling Championships", 2024, date(2024, 3, 9), date(2024, 3, 10), "Tulsa, OK", "Conference")
        ]
        
        tournament_ids = []
        for tournament_data in tournaments_data:
            tournament_id = await conn.fetchval(
                "INSERT INTO tournaments (name, year, start_date, end_date, location, division) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
                *tournament_data
            )
            tournament_ids.append(tournament_id)
        
        print(f"✓ Inserted {len(tournaments_data)} tournaments")
        
        # Insert sample brackets
        weight_classes = [125, 133, 141, 149, 157, 165, 174, 184, 197, 285]
        
        for tournament_id in tournament_ids[:3]:  # Only for NCAA championships
            for weight_class in weight_classes:
                await conn.execute(
                    "INSERT INTO brackets (tournament_id, weight_class, bracket_data) VALUES ($1, $2, $3)",
                    tournament_id, weight_class, f"Bracket data for {weight_class} lbs - Tournament {tournament_id}"
                )
        
        print(f"✓ Inserted brackets for 3 tournaments × 10 weight classes = 30 brackets")
        
        print("✓ Sample data insertion complete!")
        
    except Exception as e:
        print(f"✗ Error inserting sample data: {e}")
        raise
    finally:
        await conn.close()

async def verify_data():
    """Verify that data was inserted correctly"""
    print("Verifying data...")
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Count records in each table
        tables = ['schools', 'wrestlers', 'coaches', 'tournaments', 'brackets']
        
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {count} records")
        
        # Show some sample wrestler data with school names
        print("\nSample wrestlers with schools:")
        wrestlers = await conn.fetch("""
            SELECT w.first_name, w.last_name, w.weight_class, s.name as school_name, s.conference
            FROM wrestlers w
            JOIN schools s ON w.school_id = s.id
            ORDER BY s.name, w.weight_class
            LIMIT 10
        """)
        
        for wrestler in wrestlers:
            print(f"  {wrestler['first_name']} {wrestler['last_name']} ({wrestler['weight_class']} lbs) - {wrestler['school_name']} ({wrestler['conference']})")
        
    except Exception as e:
        print(f"✗ Error verifying data: {e}")
        raise
    finally:
        await conn.close()

async def main():
    print("PostgreSQL Database Recreation & Sample Data")
    print("=" * 50)
    
    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable is required")
        print("Make sure your .env file is configured correctly")
        return
    
    print(f"Database URL: {DATABASE_URL.split('@')[0]}@[HIDDEN]")
    print()
    
    try:
        # Test connection
        print("Testing database connection...")
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.close()
        print("✓ Database connection successful")
        print()
        
        # Recreate tables
        await recreate_tables()
        print()
        
        # Insert sample data
        await insert_sample_data()
        print()
        
        # Verify data
        await verify_data()
        print()
        
        print("🎉 Database recreation complete!")
        print("\nYou can now test the API endpoints:")
        print("- GET /api/wrestlers/ - List all wrestlers")
        print("- GET /api/schools/ - List all schools") 
        print("- GET /api/search/wrestlers?q=Taylor - Search wrestlers")
        print("- GET /api/wrestlers/1 - Get specific wrestler")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your DATABASE_URL and try again")

if __name__ == "__main__":
    asyncio.run(main())
