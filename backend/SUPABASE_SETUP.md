# Supabase Backend Setup Instructions

## Overview
Your DuckDB data has been successfully migrated to Supabase. Now we need to configure the backend to use Supabase/PostgreSQL while preserving all the improvements we made with DuckDB.

## What We've Already Done
✅ Updated backend routers to use raw SQL queries compatible with Supabase schema
✅ Fixed search endpoints to work with the new database structure
✅ Preserved match sorting logic and title case formatting
✅ Maintained flexible ID handling (both numeric and UUID)
✅ Updated database connection to use asyncpg for async operations

## What You Need to Do

### 1. Update Environment Variables
Update your `.env` file with your actual Supabase credentials:

```env
# Production environment with Supabase
USE_DUCKDB=false
DUCKDB_PATH=wrestling.duckdb

# Replace these with your actual Supabase credentials
DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@YOUR_PROJECT_REF.supabase.co:5432/postgres
SECRET_KEY=your-secret-key-here-for-production
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_ACTUAL_ANON_KEY
```

### 2. Find Your Supabase Credentials
1. Go to your Supabase dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to Settings → Database
4. Copy the connection string and replace the placeholders in `.env`
5. Go to Settings → API to get your anon key

### 3. Test the Connection
After updating your credentials, test the backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the API Endpoints
Test key endpoints to ensure everything works:

```bash
# Health check
curl "http://localhost:8000/health"

# Search functionality
curl "http://localhost:8000/api/search?q=spencer&limit=3"

# Get wrestler details (replace with actual UUID from your data)
curl "http://localhost:8000/api/wrestlers/86e7f24b-c92c-42c2-b1ce-fbcb643536bc"

# Get wrestler matches
curl "http://localhost:8000/api/wrestlers/86e7f24b-c92c-42c2-b1ce-fbcb643536bc/matches"

# Get wrestler stats
curl "http://localhost:8000/api/wrestlers/86e7f24b-c92c-42c2-b1ce-fbcb643536bc/stats"
```

## Features Preserved from DuckDB
- ✅ Title case formatting (handled in frontend)
- ✅ Proper match sorting by year and tournament round
- ✅ Flexible wrestler ID handling (supports both sequential IDs and UUIDs)
- ✅ Comprehensive search across wrestlers, schools, and coaches
- ✅ Detailed wrestler statistics and match history
- ✅ All matches displayed in chronological order

## What's Different from DuckDB
- Database connection uses PostgreSQL/Supabase instead of DuckDB
- All SQL queries have been adapted for PostgreSQL syntax
- Using asyncpg driver for async database operations
- Environment variable `USE_DUCKDB=false` switches to Supabase mode

## Troubleshooting

### Database Connection Issues
If you get connection errors:
1. Verify your DATABASE_URL is correct
2. Check that your Supabase project is active
3. Ensure your password doesn't contain special characters that need URL encoding

### Query Issues
If specific endpoints fail:
1. Check the Supabase logs in your dashboard
2. Verify the data migration was successful
3. Test individual SQL queries in the Supabase SQL editor

### Frontend Issues
The frontend should work exactly the same as with DuckDB. If you see formatting issues:
1. Clear your browser cache
2. Restart the React development server
3. Check browser console for any API errors

## Next Steps
Once Supabase is working:
1. Test all frontend features (search, wrestler pages, match history)
2. Verify title case formatting is working
3. Check that match sorting displays correctly
4. Test the full user workflow

Need help? Check the specific error messages and match them against the troubleshooting guide above.
