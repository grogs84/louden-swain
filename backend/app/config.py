"""
Configuration settings for the Wrestling Data Hub API
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # API
    api_title: str = "Wrestling Data Hub API"
    api_version: str = "1.0.0"
    api_description: str = "NCAA D1 Wrestling Championship data platform"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
