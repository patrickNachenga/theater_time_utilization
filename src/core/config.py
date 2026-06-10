import dataclasses
import json
import os

from dotenv import load_dotenv
from pydantic import BaseSettings

# Load the environment variables
# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Connect the path with your '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'))


class Settings(BaseSettings):
    PROJECT_TITLE: str = os.environ.get("APP_NAME", "theatre_time_utilization")
    SYSTEM_DEBUG_MODE: bool = os.environ.get("SYSTEM_DEBUG_MODE", "false").lower() in ("1", "true", "yes")
    PROJECT_VERSION: str = "0.0.1"
    HOST_HTTP: str = os.environ.get("HOST_HTTP", "http://")
    HOST_URL: str = os.environ.get("HOST_URL", "localhost")
    HOST_PORT: int = int(os.environ.get("HOST_PORT", 8000))
    BASE_URL: str = HOST_HTTP + HOST_URL + ":" + str(HOST_PORT)

    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "")
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "postgres")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    JWT_PUBLIC_KEY_PATH =  os.environ.get("JWT_PUBLIC_KEY_PATH", "public.pem")
    JWT_ALGORITHM =  os.environ.get("JWT_ALGORITHM", "RS256")
    JWT_ISSUER =  os.environ.get("JWT_ISSUER", "mnh-auth-service")
    JWT_AUDIENCE =  os.environ.get("JWT_AUDIENCE", "mnh-services")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
    LOGGING_FILE_NAME = 'logs'

    RABBIT_HOST: str = os.environ.get("RABBIT_HOST", "localhost")
    RABBIT_PORT = int(os.environ.get("RABBIT_PORT", 5672))
    RABBIT_USERNAME: str = os.environ.get("RABBIT_USERNAME", "guest")
    RABBIT_PASSWORD: str = os.environ.get("RABBIT_PASSWORD", "guest")

    MAIN_SERVICE_BASE_URL: str = os.environ.get("MAIN_SERVICE_BASE_URL", "http://localhost:8000")

settings = Settings()

QUEUES = [
    # {
    #     "name": "mnh-connect-permission-queue",
    #     "exchange": "mnh-connect-permission-exchange",
    #     "routing_key": "mnh-connect-permission-routing-key",
    #     "type": "fanout"
    # },
    # {
    #     "name": "mnh-connect-audit-log-queue",
    #     "exchange": "mnh-connect-audit-log-exchange",
    #     "routing_key": "mnh-connect-audit-log-routing-key",
    #     "type": "fanout"
    # },
]


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
