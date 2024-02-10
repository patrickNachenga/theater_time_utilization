from datetime import datetime, timedelta
from typing import Dict

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

from src.core.config import settings
from src.core.redis import RedisBackend

Redis = RedisBackend

SECRET_KEY = settings.JWT_SECRET_KEY


def check_secret_key():
    if SECRET_KEY == "":
        raise Exception("You have to set a Secret Key for JWT Auth")


check_secret_key()

ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bearer_scheme = HTTPBearer()


async def get_token(token=Depends(bearer_scheme)) -> str:
    """Fastapi Dependency to get the JWT/Bearer Token"""
    return str(token.credentials)


def get_data(token: str) -> Dict | None:
    """Fastapi Dependency to get JWT Data from the User"""
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.exceptions.InvalidTokenError as e:
        if isinstance(e, jwt.exceptions.ExpiredSignatureError):
            print('Token is expired')
            # raise HTTPException(status_code=401, detail="Token is expired")
            return None
        else:
            print("Token is invalid")
            return None
            # raise HTTPException(status_code=401, detail="Token is invalid")
    return data

