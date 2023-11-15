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
    PROJECT_TITLE: str = "Registration App"
    SYSTEM_DEBUG_MODE: bool = os.environ.get("SYSTEM_DEBUG_MODE")
    PROJECT_VERSION: str = "0.0.1"
    HOST_HTTP: str = os.environ.get("HOST_HTTP", "http://")
    HOST_URL: str = os.environ.get("HOST_URL")
    HOST_PORT: int = int(os.environ.get("HOST_PORT"))
    os.environ["RABBIT_PORT"] = "5672"
    BASE_URL: str = HOST_HTTP + HOST_URL + ":" + str(HOST_PORT)
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", )
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER")
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB")
    POSTGRES_UAA_DB: str = os.environ.get("POSTGRES_UAA_DB")
    POSTGRES_ACCOMMODATION_DB: str = os.environ.get("POSTGRES_ACCOMMODATION_DB")
    POSTGRES_REGISTRATION_DB: str = os.environ.get("POSTGRES_REGISTRATION_DB")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    DATABASE_UAA_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_UAA_DB}"
    DATABASE_ACCOMMODATION_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_ACCOMMODATION_DB}"

    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 6
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
    LOGGING_FILE_NAME = 'logs'
    UAA_URi: str = os.environ.get("UAA_URi")
    SR2_TOKEN: str = os.environ.get("SR2_TOKEN")
    SR2_SERVICE_URL: str = os.environ.get("SR2_SERVICE_URL")
    MOODLE_SITE_URL: str = os.environ.get("MOODLE_SITE_URL")
    MOODLE_SITE_DOMAIN: str = os.environ.get("MOODLE_SITE_DOMAIN")
    MOODLE_TOKEN: str = os.environ.get("MOODLE_TOKEN")
    RABBIT_HOST: str = os.environ.get("RABBIT_HOST")
    RABBIT_PORT = int(os.environ.get("RABBIT_PORT"))
    RABBIT_USERNAME: str = os.environ.get("RABBIT_USERNAME")
    RABBIT_PASSWORD: str = os.environ.get("RABBIT_PASSWORD")


settings = Settings()

QUEUES = [
    {
        "name": "sua-esb-permission-queue",
        "exchange": "sua-esb-permission-exchange",
        "routing_key": "sua-esb-permission-routing-key",
        "type": "fanout"
    },
    {
        "name": "sua-esb-audit-log-queue",
        "exchange": "sua-esb-audit-log-exchange",
        "routing_key": "sua-esb-audit-log-routing-key",
        "type": "fanout"
    },
]


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
