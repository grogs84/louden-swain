"""
Configuration settings for the Wrestling Tournament Management API
"""
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/dbname"

    # JWT Security
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Admin User
    admin_email: str = "admin@example.com"
    admin_password: str = "secure-admin-password"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    # Environment
    environment: str = "development"

    # API Configuration
    api_title: str = "Wrestling Tournament Management API"
    api_version: str = "1.0"
    api_description: str = "Backend API for wrestling tournament management platform"

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
