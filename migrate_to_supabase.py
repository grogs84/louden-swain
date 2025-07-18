#!/usr/bin/env python3
"""
Migration script to transfer data from DuckDB to Supabase PostgreSQL
"""

import duckdb
import psycopg2
import os
from typing import List, Dict, Any
import json

def get_supabase_connection():
    """Create connection to Supabase PostgreSQL"""
    # You'll need to set these environment variables
    return psycopg2.connect(
        host=os.getenv('SUPABASE_HOST'),
        database=os.getenv('SUPABASE_DB'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD'),
        port=os.getenv('SUPABASE_PORT', 5432),
        sslmode='require'
    )

def get_duckdb_connection():
    """Create connection to DuckDB"""
    return duckdb.connect('backend/wrestling.duckdb')

def get_table_schema(duck_conn, table_name: str) -> List[Dict]:
    """Get table schema from DuckDB"""
    result = duck_conn.execute(f"DESCRIBE {table_name}").fetchall()
    columns = duck_conn.execute(f"DESCRIBE {table_name}").description
    
    schema = []
    for row in result:
        column_info = dict(zip([col[0] for col in columns], row))
        schema.append(column_info)
    
    return schema

def convert_duckdb_type_to_postgres(duck_type: str) -> str:
    """Convert DuckDB data types to PostgreSQL equivalents"""
    type_mapping = {
        'VARCHAR': 'TEXT',
        'INTEGER': 'INTEGER',
        'BIGINT': 'BIGINT',
        'DOUBLE': 'DOUBLE PRECISION',
        'BOOLEAN': 'BOOLEAN',
        'DATE': 'DATE',
        'TIMESTAMP': 'TIMESTAMP',
        'UUID': 'UUID',
        'DECIMAL': 'DECIMAL',
        'REAL': 'REAL'
    }
    
    # Handle types with parameters like VARCHAR(255)
    base_type = duck_type.split('(')[0].upper()
    return type_mapping.get(base_type, duck_type)

def create_table_in_postgres(pg_conn, table_name: str, schema: List[Dict]):
    """Create table in PostgreSQL with proper schema"""
    cursor = pg_conn.cursor()
    
    # Drop table if exists
    cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
    
    # Build CREATE TABLE statement
    columns = []
    for col in schema:
        col_name = col['column_name']
        col_type = convert_duckdb_type_to_postgres(col['column_type'])
        nullable = "" if col['null'] == 'YES' else "NOT NULL"
        columns.append(f"{col_name} {col_type} {nullable}")
    
    create_sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n)"
    
    print(f"Creating table {table_name}...")
    print(create_sql)
    cursor.execute(create_sql)
    pg_conn.commit()
    cursor.close()

def migrate_table_data(duck_conn, pg_conn, table_name: str):
    """Migrate data from DuckDB table to PostgreSQL"""
    print(f"Migrating data for table {table_name}...")
    
    # Get data from DuckDB
    duck_data = duck_conn.execute(f"SELECT * FROM {table_name}").fetchall()
    columns = [desc[0] for desc in duck_conn.description]
    
    if not duck_data:
        print(f"No data found in {table_name}")
        return
    
    # Prepare PostgreSQL insert
    pg_cursor = pg_conn.cursor()
    
    # Build INSERT statement
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Insert data in batches
    batch_size = 1000
    for i in range(0, len(duck_data), batch_size):
        batch = duck_data[i:i + batch_size]
        pg_cursor.executemany(insert_sql, batch)
        print(f"  Inserted {min(i + batch_size, len(duck_data))}/{len(duck_data)} rows")
    
    pg_conn.commit()
    pg_cursor.close()

def get_all_tables(duck_conn) -> List[str]:
    """Get list of all tables in DuckDB"""
    result = duck_conn.execute("SHOW TABLES").fetchall()
    return [row[0] for row in result]

def main():
    """Main migration function"""
    print("🔄 Starting DuckDB to Supabase migration...")
    
    # Connect to databases
    duck_conn = get_duckdb_connection()
    pg_conn = get_supabase_connection()
    
    try:
        # Get all tables
        tables = get_all_tables(duck_conn)
        print(f"Found {len(tables)} tables: {tables}")
        
        # Define migration order (respecting foreign key dependencies)
        migration_order = [
            'school',
            'tournament', 
            'person',
            'role',
            'participant',
            'match',
            'participant_match'
        ]
        
        # Migrate each table
        for table_name in migration_order:
            if table_name in tables:
                print(f"\n📋 Processing table: {table_name}")
                
                # Get schema
                schema = get_table_schema(duck_conn, table_name)
                
                # Create table in PostgreSQL
                create_table_in_postgres(pg_conn, table_name, schema)
                
                # Migrate data
                migrate_table_data(duck_conn, pg_conn, table_name)
                
                print(f"✅ Completed migration for {table_name}")
            else:
                print(f"⚠️  Table {table_name} not found in DuckDB")
        
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        pg_conn.rollback()
        raise
    
    finally:
        duck_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main()
