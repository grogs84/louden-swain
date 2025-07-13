#!/bin/bash

# Script to create tables in Supabase using the SQL file
# This requires the Supabase CLI to be installed

echo "Setting up Supabase database tables..."

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Supabase CLI is not installed. Please install it first:"
    echo "npm install -g supabase"
    echo "Or follow instructions at: https://supabase.com/docs/guides/cli"
    exit 1
fi

# Check if we're in a Supabase project directory
if [ ! -f "supabase/config.toml" ]; then
    echo "Initializing Supabase project..."
    supabase init
fi

# Check if we have the SQL file
if [ ! -f "create_tables.sql" ]; then
    echo "Error: create_tables.sql file not found"
    exit 1
fi

# Apply the SQL migration
echo "Creating database tables..."
supabase db reset --linked

# Or you can run the SQL directly
echo "Applying SQL schema..."
supabase db push

echo "Database setup complete!"
echo ""
echo "To verify the setup worked:"
echo "1. Check your Supabase dashboard at https://app.supabase.com"
echo "2. Go to the Table Editor"
echo "3. You should see the following tables:"
echo "   - schools"
echo "   - wrestlers" 
echo "   - coaches"
echo "   - tournaments"
echo "   - brackets"
echo "   - matches"
echo ""
echo "You can also test the API endpoints by running:"
echo "python -m uvicorn app.main:app --reload"
echo "Then visit http://localhost:8000/docs"
