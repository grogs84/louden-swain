# DuckDB Integration for NCAA Wrestling Championship API

## Overview

The NCAA Wrestling Championship API now supports **local development using DuckDB** as an alternative to PostgreSQL/Supabase. This allows developers to work with the full wrestling dataset locally without needing external database connections.

## Quick Start

### 1. Enable DuckDB Mode

Set the environment variable to enable DuckDB mode:

```bash
export USE_DUCKDB=true
```

Or create a `.env.local` file:

```bash
USE_DUCKDB=true
DUCKDB_PATH=wrestling.duckdb
DATABASE_URL=postgresql://dummy
SECRET_KEY=your-secret-key-here-for-local-dev
SUPABASE_URL=https://dummy
SUPABASE_KEY=dummy
```

### 2. Start the API Server

```bash
cd backend
source venv/bin/activate
USE_DUCKDB=true python -m uvicorn app.main:app --reload --port 8000
```

### 3. Access DuckDB Endpoints

The DuckDB-based API is available at: `http://localhost:8000/api/duckdb/`

## Available Endpoints

### Information
- `GET /api/duckdb/` - API information and endpoint list

### Schools
- `GET /api/duckdb/schools/` - Get all schools (supports `limit`, `name` filters)
- `GET /api/duckdb/schools/{school_id}/` - Get specific school by ID

### Wrestlers  
- `GET /api/duckdb/wrestlers/` - Get all wrestlers (supports `limit`, `name`, `weight_class`, `school` filters)
- `GET /api/duckdb/wrestlers/{wrestler_id}/` - Get specific wrestler by ID

### Tournaments
- `GET /api/duckdb/tournaments/` - Get all tournaments (supports `limit`, `year` filters)
- `GET /api/duckdb/tournaments/{tournament_id}/` - Get specific tournament by ID

### Search
- `GET /api/duckdb/search/wrestlers/?q={query}` - Search wrestlers by name
- `GET /api/duckdb/search/schools/?q={query}` - Search schools by name

### Utility
- `GET /api/duckdb/weight-classes/` - Get all weight classes
- `GET /api/duckdb/years/` - Get all tournament years
- `GET /api/duckdb/stats/` - Get database statistics

## Example API Calls

### Get Top 3 Schools
```bash
curl "http://localhost:8000/api/duckdb/schools/?limit=3"
```

### Search for Wrestlers Named "John"
```bash
curl "http://localhost:8000/api/duckdb/search/wrestlers/?q=john"
```

### Get Recent Tournaments
```bash
curl "http://localhost:8000/api/duckdb/tournaments/?limit=5"
```

### Get Database Statistics
```bash
curl "http://localhost:8000/api/duckdb/stats/"
```

## Database Schema

The DuckDB database contains the following tables:

- **person** - Individual people (wrestlers, coaches, etc.)
- **role** - Roles that people have (wrestler, coach, etc.)
- **school** - Educational institutions
- **participant** - Person participating in a tournament (links person, role, school)
- **tournament** - Wrestling tournaments by year
- **match** - Individual wrestling matches
- **participant_match** - Results of matches for each participant

## Data Statistics

- **Total Records**: 
  - 13,155 people
  - 323 schools  
  - 94 tournaments (1928-2025)
  - 39,395 matches
  - 78,754 match participations

- **Weight Classes**: 37 different weight classes from 114 to 450 lbs
- **Time Span**: 1928 to 2025 (97 years of data)

## API Response Format

### Schools
```json
{
  "id": 1,
  "school_id": "456eb3bb-e003-4981-bec9-6dc0f34c9616",
  "name": "Oklahoma State", 
  "location": "Unknown",
  "state": "US",
  "conference": "NCAA Division I",
  "total_participants": 828,
  "years_active": 93,
  "first_year": 1928,
  "last_year": 2025
}
```

### Wrestlers
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "weight_class": 165,
  "year": "Senior", 
  "school_id": 1,
  "school_name": "Oklahoma State",
  "wins": 15,
  "losses": 3,
  "person_id": "uuid-here",
  "seed": 1
}
```

### Tournaments
```json
{
  "id": 1,
  "tournament_id": "uuid-here",
  "name": "NCAA Division I Wrestling Championships 2025",
  "year": 2025,
  "location": "Unknown Location",
  "total_matches": 640,
  "total_participants": 330,
  "division": "Division I"
}
```

## Development Notes

### File Structure
- `duckdb_integration.py` - Core DuckDB query logic
- `app/models/duckdb_models.py` - SQLAlchemy models for DuckDB schema
- `app/routers/duckdb_router.py` - FastAPI endpoints
- `wrestling.duckdb` - SQLite database file
- `examine_duckdb.py` - Database exploration script

### Important Notes
- **Trailing Slashes**: All endpoints require trailing slashes (e.g., `/schools/` not `/schools`)
- **Performance**: DuckDB is fast for analytics but queries may be slower than indexed PostgreSQL
- **Data Integrity**: This is read-only data - the DuckDB is not updated in real-time
- **Production**: This is for local development only - production uses PostgreSQL/Supabase

### Switching Between Databases
- **DuckDB (Local)**: Set `USE_DUCKDB=true`
- **PostgreSQL (Production)**: Set `USE_DUCKDB=false` or unset the variable

## Testing the Integration

Test DuckDB directly:
```python
from duckdb_integration import WrestlingDuckDB

db = WrestlingDuckDB('wrestling.duckdb')
with db:
    schools = db.get_schools(limit=3)
    print(schools)
```

Test API endpoints:
```bash
# Info endpoint
curl "http://localhost:8000/api/duckdb/"

# Data endpoints  
curl "http://localhost:8000/api/duckdb/schools/?limit=3"
curl "http://localhost:8000/api/duckdb/wrestlers/?limit=3"
curl "http://localhost:8000/api/duckdb/tournaments/?limit=3"

# Search
curl "http://localhost:8000/api/duckdb/search/wrestlers/?q=john"
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure `duckdb` package is installed: `pip install duckdb`
2. **File Not Found**: Verify `wrestling.duckdb` exists in the backend directory
3. **307 Redirects**: Add trailing slashes to endpoint URLs
4. **Hanging Requests**: Check server logs for SQLAlchemy connection attempts

### Logs
The server will log:
- `"DuckDB router enabled for local development"` when DuckDB mode is active
- SQLAlchemy connection attempts to PostgreSQL (these can be ignored in DuckDB mode)

This integration provides a complete local development environment with the full NCAA wrestling dataset!
