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
    PROJECT_VERSION: str = "0.0.1"
    HOST_HTTP: str = os.environ.get("HOST_HTTP", "http://")
    HOST_URL: str = os.environ.get("HOST_URL")
    HOST_PORT: int = int(os.environ.get("HOST_PORT"))

    BASE_URL: str = HOST_HTTP + HOST_URL + ":" + str(HOST_PORT)
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", )
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER")
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 6
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    LOGGING_FILE_NAME = 'logs'
    UAA_URi = os.environ.get("UAA_URi")

    """ -------- MOODLE ENDPOINT  -------"""
    SITE_URL = 'http://45.132.242.170/webservice/rest/server.php'
    SITE_DOMAIN = 'http://45.132.242.170'
    TOKEN = '9454c6efdb94236e618c9a7b1a67138b'

    """ -------- SR2 ENDPOINT  -------"""
    SR2_URL = 'http://197.250.34.41:4747/api/v2/'
    SR2_TOKEN = '9454c6efdb94236e618c9a7b1a67138b'

    # SR2_SERVICE_URL = os.environ.get("SR2_SERVICE_URL")
    # MOODLE_SITE_URL = os.environ.get("MOODLE_SITE_URL")
    # MOODLE_SITE_DOMAIN = os.environ.get("MOODLE_SITE_DOMAIN")
    # MOODLE_TOKEN = os.environ.get("MOODLE_TOKEN")
    RABBIT_HOST = os.environ.get("RABBIT_HOST")
    RABBIT_PORT = int(os.environ.get("RABBIT_PORT"))
    RABBIT_USERNAME = os.environ.get("RABBIT_USERNAME")
    RABBIT_PASSWORD = os.environ.get("RABBIT_PASSWORD")



settings = Settings()

QUEUES = [
    {
        "name": "sua-esb-permission-queue",
        "exchange": "sua-esb-permission-exchange",
        "routing_key": "sua-esb-permission-routing-key",
        "type": "fanout"
    },
]


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
