from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # App
    APP_NAME: str = Field("Theatre Time Utilisation Service", env="APP_NAME")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DEBUG: bool = Field(True, env="DEBUG")
    API_PREFIX: str = Field("/api", env="API_PREFIX")
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")

    # Postgres
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = Field("redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")

    # Main/Auth service
    MAIN_SERVICE_BASE_URL: str
    MAIN_SERVICE_TIMEOUT: int = 10
    MAIN_SERVICE_API_KEY: Optional[str] = None

    # JWT
    JWT_PUBLIC_KEY_PATH: str = Field("public.pem", env="JWT_PUBLIC_KEY_PATH")
    JWT_ALGORITHM: str = Field("RS256", env="JWT_ALGORITHM")
    JWT_AUDIENCE: Optional[str] = None
    JWT_ISSUER: Optional[str] = None

    # CORS
    CORS_ORIGINS: List[str] = Field(["*"], env="CORS_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def JWT_PUBLIC_KEY(self) -> str:
        p = Path(self.JWT_PUBLIC_KEY_PATH)
        if p.exists():
            return p.read_text()
        logger.warning("JWT public key file not found: %s", p)
        return ""


settings = Settings()
