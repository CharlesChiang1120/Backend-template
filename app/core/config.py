from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Defaulting to In-memory for testing, override via .env for Production (PostgreSQL)
    DATABASE_URL: str = "sqlite+aiosqlite:///./factory.db"
    OPENAI_API_KEY: Optional[str] = None
    FACTORY_LOCATION: str = "Unspecified"
    
    class Config:
        env_file = ".env"

settings = Settings()