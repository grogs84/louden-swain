# Manual Supabase Table Creation Guide

Since direct SQL execution through the REST API requires special permissions, you'll need to create the tables manually through the Supabase dashboard.

## Steps:

1. **Go to your Supabase Dashboard**
   - Visit: https://app.supabase.com
   - Sign in to your account
   - Select your project: `dsnwqmkklslwqpeuewcq`

2. **Open the SQL Editor**
   - In the left sidebar, click "SQL Editor"
   - Click "New query"

3. **Copy and paste the following SQL**
   - Copy the entire contents of `create_tables.sql`
   - Paste it into the SQL editor
   - Click "Run" to execute

4. **Verify table creation**
   - Go to "Table Editor" in the left sidebar
   - You should see 6 tables: schools, wrestlers, coaches, tournaments, brackets, matches

## Alternative: Create tables one by one

If the full SQL doesn't work, you can create tables individually using the Table Editor:

### 1. Schools Table
```sql
CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    state VARCHAR(2),
    city VARCHAR(100),
    conference VARCHAR(100),
    division VARCHAR(10),
    website VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Wrestlers Table
```sql
CREATE TABLE wrestlers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    weight_class INTEGER,
    year VARCHAR(20),
    school_id INTEGER REFERENCES schools(id),
    hometown VARCHAR(100),
    high_school VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Coaches Table
```sql
CREATE TABLE coaches (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    school_id INTEGER REFERENCES schools(id),
    title VARCHAR(100),
    years_experience INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Tournaments Table
```sql
CREATE TABLE tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    division VARCHAR(10),
    location VARCHAR(255),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Brackets Table
```sql
CREATE TABLE brackets (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    weight_class INTEGER NOT NULL,
    bracket_data TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6. Matches Table
```sql
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id),
    bracket_id INTEGER REFERENCES brackets(id),
    wrestler1_id INTEGER REFERENCES wrestlers(id),
    wrestler2_id INTEGER REFERENCES wrestlers(id),
    winner_id INTEGER REFERENCES wrestlers(id),
    weight_class INTEGER,
    round INTEGER,
    match_type VARCHAR(50),
    score VARCHAR(50),
    bout_number INTEGER,
    match_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## After Creating Tables

Once the tables are created, you can test the API:

1. **Start the backend server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8001
   ```

2. **Test endpoints:**
   - Health check: http://localhost:8001/health
   - API docs: http://localhost:8001/docs
   - Schools: http://localhost:8001/api/schools
   - Wrestlers: http://localhost:8001/api/wrestlers

3. **Add sample data (optional):**
   - Use the SQL from the sample data section in `create_tables.sql`
   - Or use the API endpoints to add data through the frontend

## Notes:
- The tables will be empty initially
- You can add sample data through the API or SQL editor
- Row Level Security (RLS) is disabled for now for easier development
- You may want to enable RLS for production use
