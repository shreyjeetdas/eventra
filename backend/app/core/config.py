import os
from typing import Optional, List

class Settings:
    PROJECT_NAME: str = "EVENTRA Intelligent Operations Center"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database (Defaults to local SQLite, easily switchable to PostgreSQL/Supabase via DATABASE_URL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eventra.db")
    
    # Notion Configuration
    NOTION_API_KEY: Optional[str] = os.getenv("NOTION_API_KEY", "")
    NOTION_DATABASE_ID_EVENTS: Optional[str] = os.getenv("NOTION_DATABASE_ID_EVENTS", "")
    NOTION_DATABASE_ID_TASKS: Optional[str] = os.getenv("NOTION_DATABASE_ID_TASKS", "")
    NOTION_DATABASE_ID_CHANGELOGS: Optional[str] = os.getenv("NOTION_DATABASE_ID_CHANGELOGS", "")
    NOTION_DATABASE_ID_KNOWLEDGE: Optional[str] = os.getenv("NOTION_DATABASE_ID_KNOWLEDGE", "")
    NOTION_DATABASE_ID_BRIEFINGS: Optional[str] = os.getenv("NOTION_DATABASE_ID_BRIEFINGS", "")
    
    # AI Provider Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

settings = Settings()
