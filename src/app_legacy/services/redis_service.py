from __future__ import annotations

import json
import logging
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError

from app.config import settings
from app.schemas.auth import PermissionResponse

logger = logging.getLogger(__name__)

REDIS_PERMISSION_CACHE_KEY_PREFIX = "auth:user:"
REDIS_PERMISSION_CACHE_TTL_SECONDS = 7200


class RedisService:
    def __init__(self):
        self.redis_client: Optional[Redis] = None

    async def connect(self):
        try:
            url = settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            self.redis_client = redis.from_url(url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except ConnectionError as e:
            logger.error(f"Could not connect to Redis: {e}")
            self.redis_client = None

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis.")

    def _get_key(self, user_guid: str) -> str:
        return f"{REDIS_PERMISSION_CACHE_KEY_PREFIX}{user_guid}"

    async def get_user_permissions(self, user_guid: str) -> PermissionResponse | None:
        if not self.redis_client:
            logger.warning("Redis client not initialized. Cannot get user permissions from cache.")
            return None
        try:
            cached_data = await self.redis_client.get(self._get_key(user_guid))
            if cached_data:
                data = json.loads(cached_data)
                return PermissionResponse(**data)
            return None
        except RedisError as e:
            logger.error(f"Redis error while getting permissions for user {user_guid}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for cached permissions for user {user_guid}: {e}")
            await self.redis_client.delete(self._get_key(user_guid))
            return None

    async def set_user_permissions(self, user_guid: str, permissions: PermissionResponse):
        if not self.redis_client:
            logger.warning("Redis client not initialized. Cannot set user permissions in cache.")
            return
        try:
            await self.redis_client.setex(
                self._get_key(user_guid),
                REDIS_PERMISSION_CACHE_TTL_SECONDS,
                permissions.model_dump_json() if hasattr(permissions, 'model_dump_json') else permissions.json(),
            )
            logger.debug(f"Permissions for user {user_guid} set in Redis cache.")
        except RedisError as e:
            logger.error(f"Redis error while setting permissions for user {user_guid}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while setting permissions for user {user_guid}: {e}")


redis_service = RedisService()
