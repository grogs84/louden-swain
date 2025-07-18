from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    # Enable DuckDB for local development
    use_duckdb: bool = False
    duckdb_path: str = "wrestling.duckdb"

    class Config:
        env_file = ".env"

settings = Settings()
