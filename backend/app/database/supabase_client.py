import httpx
from typing import List, Dict, Any, Optional
from app.config import settings

class SupabaseClient:
    def __init__(self):
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def create_table(self, table_name: str, columns: Dict[str, str]):
        """Create a table using Supabase SQL API (if available)"""
        # Note: Table creation is typically done through Supabase dashboard
        # This is a placeholder for the structure
        pass
    
    async def select(self, table: str, columns: str = "*", filters: Dict[str, Any] = None, 
                     limit: int = None, offset: int = None, order: str = None):
        """Select data from a table with enhanced filtering"""
        url = f"{self.base_url}/{table}"
        params = {"select": columns}
        
        if filters:
            for key, value in filters.items():
                if isinstance(value, str) and "%" in value:
                    # Handle LIKE queries
                    params[f"{key}"] = f"like.{value}"
                elif isinstance(value, list):
                    # Handle IN queries
                    params[f"{key}"] = f"in.({','.join(map(str, value))})"
                else:
                    # Standard equality
                    params[f"{key}"] = f"eq.{value}"
        
        if limit:
            params["limit"] = limit
            
        if offset:
            params["offset"] = offset
            
        if order:
            params["order"] = order
            
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def select_with_text_search(self, table: str, columns: str = "*", 
                                      search_column: str = None, search_term: str = None,
                                      filters: Dict[str, Any] = None, limit: int = None):
        """Select with text search capability"""
        url = f"{self.base_url}/{table}"
        params = {"select": columns}
        
        if search_column and search_term:
            # Use ilike for case-insensitive text search
            params[f"{search_column}"] = f"ilike.*{search_term}*"
        
        if filters:
            for key, value in filters.items():
                params[f"{key}"] = f"eq.{value}"
        
        if limit:
            params["limit"] = limit
            
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def count(self, table: str, filters: Dict[str, Any] = None):
        """Count rows in a table"""
        url = f"{self.base_url}/{table}"
        headers = {**self.headers, "Prefer": "count=exact"}
        params = {"select": "id"}  # Select minimal data for counting
        
        if filters:
            for key, value in filters.items():
                params[f"{key}"] = f"eq.{value}"
        
        async with httpx.AsyncClient() as client:
            response = await client.head(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Extract count from Content-Range header
            content_range = response.headers.get("Content-Range", "")
            if "/" in content_range:
                return int(content_range.split("/")[1])
            return 0
    
    async def insert(self, table: str, data: Dict[str, Any]):
        """Insert data into a table"""
        url = f"{self.base_url}/{table}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def insert_batch(self, table: str, data: List[Dict[str, Any]]):
        """Insert multiple rows at once"""
        url = f"{self.base_url}/{table}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def update(self, table: str, filters: Dict[str, Any], data: Dict[str, Any]):
        """Update data in a table"""
        url = f"{self.base_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
            
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, params=params, json=data)
            response.raise_for_status()
            return response.json()
    
    async def delete(self, table: str, filters: Dict[str, Any]):
        """Delete data from a table"""
        url = f"{self.base_url}/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
            
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def rpc(self, function_name: str, params: Dict[str, Any] = None):
        """Call a stored procedure/function"""
        url = f"{self.base_url}/rpc/{function_name}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=params or {})
            response.raise_for_status()
            return response.json()

# Global instance
supabase_client = SupabaseClient()
