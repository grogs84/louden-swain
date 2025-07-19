# Wrestling Data Hub - Clean Start Plan

## Project Vision
A clean, modern NCAA D1 Wrestling Championship data platform with:
- **Backend**: FastAPI + Supabase (PostgreSQL)
- **Frontend**: React with Material-UI
- **Focus**: Simple, maintainable, production-ready code

## What We're Building

### Core Features
1. **Wrestler Profiles**
   - Personal info (name, school, weight class)
   - Career statistics (wins/losses, pins, etc.)
   - Match history with opponents and results
   - Tournament participation

2. **School Programs** 
   - School information (name, location, conference)
   - Team statistics and history
   - Current and historical wrestlers

3. **Tournament Data**
   - Tournament brackets and results
   - Championship history
   - Match results and scores

4. **Search & Discovery**
   - Search wrestlers by name or school
   - Search schools by name or location
   - Filter by year, weight class, etc.

## Database Schema (Supabase/PostgreSQL)

### Core Tables
```sql
-- People (wrestlers, coaches, etc.)
people (
  id: UUID PRIMARY KEY,
  first_name: TEXT,
  last_name: TEXT,
  created_at: TIMESTAMP
)

-- Schools
schools (
  id: UUID PRIMARY KEY,
  name: TEXT NOT NULL,
  location: TEXT,
  state: TEXT,
  created_at: TIMESTAMP
)

-- Tournaments
tournaments (
  id: UUID PRIMARY KEY,
  name: TEXT NOT NULL,
  year: INTEGER NOT NULL,
  location: TEXT,
  division: TEXT DEFAULT 'Division I',
  created_at: TIMESTAMP
)

-- Participants (wrestlers in specific tournaments)
participants (
  id: UUID PRIMARY KEY,
  person_id: UUID REFERENCES people(id),
  school_id: UUID REFERENCES schools(id),
  tournament_id: UUID REFERENCES tournaments(id),
  weight_class: TEXT,
  seed: INTEGER,
  year: INTEGER,
  created_at: TIMESTAMP
)

-- Matches
matches (
  id: UUID PRIMARY KEY,
  tournament_id: UUID REFERENCES tournaments(id),
  winner_id: UUID REFERENCES participants(id),
  loser_id: UUID REFERENCES participants(id),
  round: TEXT,
  match_result: TEXT, -- 'Fall', 'Decision', 'Major Decision', etc.
  score: TEXT,
  weight_class: TEXT,
  created_at: TIMESTAMP
)
```

## API Endpoints (Clean & Simple)

### Wrestlers
- `GET /api/wrestlers` - List wrestlers with pagination
- `GET /api/wrestlers/{id}` - Get wrestler details
- `GET /api/wrestlers/{id}/matches` - Get wrestler's match history
- `GET /api/wrestlers/{id}/stats` - Get wrestler's statistics

### Schools
- `GET /api/schools` - List schools with pagination  
- `GET /api/schools/{id}` - Get school details
- `GET /api/schools/{id}/wrestlers` - Get school's wrestlers
- `GET /api/schools/{id}/stats` - Get school statistics

### Tournaments
- `GET /api/tournaments` - List tournaments
- `GET /api/tournaments/{id}` - Get tournament details
- `GET /api/tournaments/{id}/brackets` - Get tournament brackets

### Search
- `GET /api/search?q={query}` - Universal search
- `GET /api/search/wrestlers?q={query}` - Search wrestlers
- `GET /api/search/schools?q={query}` - Search schools

## File Structure (Simplified)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Supabase connection
│   ├── models.py            # Pydantic models
│   └── routers/
│       ├── __init__.py
│       ├── wrestlers.py     # Wrestler endpoints
│       ├── schools.py       # School endpoints  
│       ├── tournaments.py   # Tournament endpoints
│       └── search.py        # Search endpoints
├── requirements.txt
└── .env                     # Environment variables

frontend/
├── src/
│   ├── App.js
│   ├── index.js
│   ├── components/
│   │   └── common/          # Reusable components
│   ├── pages/
│   │   ├── HomePage.js
│   │   ├── WrestlerPage.js
│   │   ├── SchoolPage.js
│   │   └── SearchPage.js
│   └── services/
│       └── api.js           # API client
├── package.json
└── public/
```

## Development Approach

### Phase 1: Backend Foundation
1. Clean up backend - remove old files
2. Set up Supabase connection
3. Create clean API routers
4. Test with sample data

### Phase 2: Frontend Integration  
1. Clean up frontend - remove unused code
2. Update API service
3. Test core pages (home, search, wrestler profile)

### Phase 3: Polish & Deploy
1. Add error handling
2. Optimize performance  
3. Deploy to production

## Key Principles
- **Keep it simple**: One database, one API structure, clear naming
- **No legacy code**: Remove all experimental/unused files
- **Clean separation**: Backend API ↔ Frontend React app
- **Production ready**: Error handling, validation, documentation

## Next Steps
1. Clean up existing files (remove DuckDB, old routers, etc.)
2. Set up Supabase connection with your credentials
3. Create clean API structure
4. Test with existing frontend
5. Deploy when ready

Would you like to proceed with this clean approach?
