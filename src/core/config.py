from __future__ import annotations

import dataclasses
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Load .env next to this file as fallback
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

logger = logging.getLogger(__name__)


class Settings:
    def __init__(self):
        # App
        self.APP_NAME: str = os.environ.get("APP_NAME", "Theatre Time Utilisation Service")
        self.ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
        self.SYSTEM_DEBUG_MODE: bool = os.environ.get("SYSTEM_DEBUG_MODE", "false").lower() in ("1", "true", "yes")
        self.API_PREFIX: str = os.environ.get("API_PREFIX", "/api")
        self.HOST: str = os.environ.get("HOST", "0.0.0.0")
        self.PORT: int = int(os.environ.get("PORT", 8000))

        # Postgres
        self.POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "")
        self.POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", 5432))
        self.POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "postgres")

        @property
        def DATABASE_URL(self) -> str:
            """Async database URL for SQLAlchemy."""
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        @property
        def DATABASE_URL_SYNC(self) -> str:
            """Sync database URL for Alembic migrations."""
            return (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Redis
        self.REDIS_URL: str | None = os.environ.get("REDIS_URL")
        self.REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
        self.REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))
        self.REDIS_DB: int = int(os.environ.get("REDIS_DB", 0))
        self.REDIS_PASSWORD: str = os.environ.get("REDIS_PASSWORD", "")

        # Main/Auth service
        self.MAIN_SERVICE_BASE_URL: str = os.environ.get("MAIN_SERVICE_BASE_URL", "http://localhost:8000")
        self.MAIN_SERVICE_TIMEOUT: int = int(os.environ.get("MAIN_SERVICE_TIMEOUT", 10))
        self.MAIN_SERVICE_API_KEY: str | None = os.environ.get("MAIN_SERVICE_API_KEY")

        # JWT
        self.JWT_PUBLIC_KEY_PATH: str = os.environ.get("JWT_PUBLIC_KEY_PATH", "public.pem")
        self.JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "RS256")
        self.JWT_AUDIENCE = os.environ.get("JWT_AUDIENCE")
        self.JWT_ISSUER = os.environ.get("JWT_ISSUER")

        # CORS
        cors = os.environ.get("CORS_ORIGINS", "*")
        self.CORS_ORIGINS: List[str] = [c.strip() for c in cors.split(",")] if cors else ["*"]

    @property
    def JWT_PUBLIC_KEY(self) -> str:
        p = Path(self.JWT_PUBLIC_KEY_PATH)
        if p.exists():
            return p.read_text()
        logger.warning("JWT public key file not found: %s", p)
        return ""

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()

QUEUES = [
    # example queue definitions
]


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
