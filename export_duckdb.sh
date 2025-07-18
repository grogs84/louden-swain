#!/bin/bash
# Export all tables from DuckDB to CSV files
# Then import to Supabase using SQL commands

echo "🔄 Exporting DuckDB tables to CSV..."

# Create export directory
mkdir -p duckdb_export

# Python script to export all tables
python3 << 'EOF'
import duckdb
import os

# Connect to DuckDB
conn = duckdb.connect('backend/wrestling.duckdb')

# Get all tables
tables = conn.execute("SHOW TABLES").fetchall()
table_names = [row[0] for row in tables]

print(f"Found tables: {table_names}")

# Export each table to CSV
for table in table_names:
    csv_file = f"duckdb_export/{table}.csv"
    print(f"Exporting {table} to {csv_file}...")
    conn.execute(f"COPY {table} TO '{csv_file}' (HEADER, DELIMITER ',')")

conn.close()
print("✅ Export completed!")
EOF

echo "📤 CSV files created in duckdb_export/ directory"
echo "🔧 Next steps:"
echo "1. Set your Supabase connection details"
echo "2. Run the SQL import commands"
echo "3. Or use the Python migration script with proper credentials"
