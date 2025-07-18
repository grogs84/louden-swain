"""
Script to examine the DuckDB wrestling database schema
"""

import duckdb
import json
from pathlib import Path

def examine_duckdb_schema():
    """Examine the schema and data in the wrestling.duckdb file"""
    
    db_path = Path("wrestling.duckdb")
    if not db_path.exists():
        print("Error: wrestling.duckdb file not found")
        return
    
    print("🏆 Examining Wrestling DuckDB Database")
    print("=" * 50)
    
    # Connect to DuckDB
    conn = duckdb.connect(str(db_path))
    
    try:
        # Get all tables
        print("\n📋 TABLES IN DATABASE:")
        tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        tables = conn.execute(tables_query).fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"  • {table_name}")
        
        print(f"\nFound {len(tables)} tables")
        
        # Examine each table schema and sample data
        for table in tables:
            table_name = table[0]
            print(f"\n" + "="*60)
            print(f"🏗️  TABLE: {table_name.upper()}")
            print("="*60)
            
            # Get column information
            columns_query = f"""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
            """
            columns = conn.execute(columns_query).fetchall()
            
            print("\n📊 SCHEMA:")
            for col in columns:
                col_name, data_type, nullable = col
                null_str = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"  {col_name:<20} {data_type:<15} {null_str}")
            
            # Get row count
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            row_count = conn.execute(count_query).fetchone()[0]
            print(f"\n📈 ROW COUNT: {row_count}")
            
            # Show sample data (first 5 rows)
            if row_count > 0:
                sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                sample_data = conn.execute(sample_query).fetchall()
                
                # Get column names for display
                col_names = [col[0] for col in columns]
                
                print(f"\n🔍 SAMPLE DATA (first 5 rows):")
                print("-" * 100)
                
                # Print header
                header = " | ".join([name[:15].ljust(15) for name in col_names])
                print(header)
                print("-" * len(header))
                
                # Print sample rows
                for row in sample_data:
                    row_str = " | ".join([str(val)[:15].ljust(15) if val is not None else "NULL".ljust(15) for val in row])
                    print(row_str)
        
        # Check for foreign key relationships (if any)
        print(f"\n" + "="*60)
        print("🔗 FOREIGN KEY RELATIONSHIPS:")
        print("="*60)
        
        fk_query = """
        SELECT 
            fk.table_name as from_table,
            fk.column_name as from_column,
            pk.table_name as to_table,
            pk.column_name as to_column
        FROM information_schema.key_column_usage fk
        JOIN information_schema.key_column_usage pk 
        ON fk.referenced_table_name = pk.table_name 
        AND fk.referenced_column_name = pk.column_name
        WHERE fk.referenced_table_name IS NOT NULL
        """
        
        try:
            fks = conn.execute(fk_query).fetchall()
            if fks:
                for fk in fks:
                    print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
            else:
                print("  No explicit foreign key constraints found")
        except Exception as e:
            print(f"  Could not query foreign keys: {e}")
        
    except Exception as e:
        print(f"Error examining database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    examine_duckdb_schema()
