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
    
    # Next.js Frontend Environment Variables
    next_public_supabase_url: str = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
    next_public_supabase_anon_key: str = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    
    # JWT Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    
    # Admin User
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # API
    api_title: str = "Wrestling Data Hub API"
    api_version: str = "1.0.0"
    api_description: str = "NCAA D1 Wrestling Championship data platform"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
