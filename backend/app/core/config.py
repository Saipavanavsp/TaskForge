import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TaskForge"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Auth & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "taskforge-production-grade-jwt-secret-key-32chars-min!!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "taskforge")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('POSTGRES_SERVER', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'taskforge')}"
    )
    
    # SQLite fallback toggle for zero-dependency local runs
    USE_SQLITE_FALLBACK: bool = os.getenv("USE_SQLITE_FALLBACK", "true").lower() == "true"
    SQLITE_URL: str = "sqlite+aiosqlite:///./taskforge.db"

    # Redis Cache & PubSub
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:4000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4000",
        "https://app.taskforge.dev",
        "*"
    ]

    # Observability
    ENABLE_METRICS: bool = True
    ENABLE_TELEMETRY: bool = True

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="allow"
    )


settings = Settings()
