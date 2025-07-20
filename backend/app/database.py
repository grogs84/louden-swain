"""
Database connection and utilities for Supabase PostgreSQL
"""
import asyncpg
import asyncio
from typing import List, Dict, Any, Optional
from .config import settings

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create database connection pool"""
        if not self.pool and settings.database_url:
            try:
                self.pool = await asyncpg.create_pool(
                    settings.database_url,
                    min_size=1,
                    max_size=20,
                    command_timeout=60
                )
                print("✅ Connected to Supabase database successfully")
            except Exception as e:
                print(f"❌ Failed to connect to database: {e}")
                raise e
        return self.pool
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute query and return all rows"""
        pool = await self.connect()
        async with pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute query and return one row"""
        pool = await self.connect()
        async with pool.acquire() as connection:
            row = await connection.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def execute(self, query: str, *args) -> str:
        """Execute query and return status"""
        pool = await self.connect()
        async with pool.acquire() as connection:
            return await connection.execute(query, *args)

# Global database instance
db = Database()

# Dependency for FastAPI
async def get_db():
    return db
