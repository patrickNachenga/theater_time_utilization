import json
import logging
from typing import Any, Optional, Set

from redis.asyncio import Redis, from_url

from src.core.config import settings
from src.shared.models import PermissionResponse

logger = logging.getLogger(__name__)

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD

# ─── Permission Cache Constants ────────────────────────────────────────────

PERMISSION_CACHE_PREFIX = "auth:user:"
PERMISSION_CACHE_TTL_SECONDS = 900  # 15 minutes


def _permission_cache_key(user_guid: str) -> str:
    return f"{PERMISSION_CACHE_PREFIX}{user_guid}"


class RedisBackend:
    redis_connection: Redis

    @staticmethod
    async def init(url: str) -> "RedisBackend":
        redis = RedisBackend()
        redis.redis_connection = await from_url(url)
        return redis

    async def get(self, key: str) -> Any:
        """Get Value from Key"""
        return await self.redis_connection.get(key)

    async def set(self, key: str, value, expire: int = 0, pexpire: int = 0, exists=None):
        """Set Key to Value"""
        return await self.redis_connection.set(key, value, ex=expire, px=pexpire, nx=exists)

    async def pttl(self, key: str) -> int:
        """Get PTTL from a Key"""
        return int(await self.redis_connection.pttl(key))

    async def ttl(self, key: str) -> int:
        """Get TTL from a Key"""
        return int(await self.redis_connection.ttl(key))

    async def pexpire(self, key: str, pexpire: int) -> bool:
        """Sets and PTTL for a Key"""
        return bool(await self.redis_connection.pexpire(key, pexpire))

    async def expire(self, key: str, expire: int) -> bool:
        """Sets and TTL for a Key"""
        return bool(await self.redis_connection.expire(key, expire))

    async def incr(self, key: str) -> int:
        """Increases an Int Key"""
        return int(await self.redis_connection.incr(key))

    async def decr(self, key: str) -> int:
        """Decreases an Int Key"""
        return int(await self.redis_connection.decr(key))

    async def delete(self, key: str) -> Any:
        """Delete value of a Key"""
        return await self.redis_connection.delete(key)

    async def smembers(self, key: str) -> Set:
        """Gets Set Members"""
        return set(await self.redis_connection.smembers(key))

    async def sadd(self, key: str, value: Any) -> bool:
        """Adds a Member to a Dict"""
        return bool(await self.redis_connection.sadd(key, value))

    async def srem(self, key: str, member: Any) -> bool:
        """Removes a Member from a Set"""
        return bool(await self.redis_connection.srem(key, member))

    async def exists(self, key: str) -> bool:
        """Checks if a Key exists"""
        return bool(await self.redis_connection.exists(key))

    # ─── Permission Cache Methods ─────────────────────────────────────────

    async def set_cached_permissions(self, user_guid: str, permissions: PermissionResponse) -> bool:
        """
        Store user permissions in Redis cache with TTL.
        Returns True on success, False on failure.
        """
        key = _permission_cache_key(user_guid)
        try:
            # Serialize to JSON string — handle UUIDs and other non-serializable types
            data_dict = permissions.model_dump() if hasattr(permissions, 'model_dump') else permissions.dict()
            data_dict = {k: v for k, v in data_dict.items() if v is not None}
            json_data = json.dumps(data_dict, default=str)

            # Use setex (SET with expiry) — avoids any argument confusion
            await self.redis_connection.setex(key, PERMISSION_CACHE_TTL_SECONDS, json_data)
            logger.debug(f"Permissions cached for user {user_guid} (TTL={PERMISSION_CACHE_TTL_SECONDS}s)")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"JSON serialization error for user {user_guid}: {e}")
            return False
        except Exception as e:
            logger.error(f"Redis error caching permissions (user={user_guid}): {e}", exc_info=True)
            return False

    async def get_cached_permissions(self, user_guid: str) -> Optional[PermissionResponse]:
        """
        Retrieve cached user permissions from Redis.
        Returns None if not found, JSON corrupt, or model validation fails.
        """
        key = _permission_cache_key(user_guid)
        try:
            cached_data = await self.get(key)
            if not cached_data:
                return None
            data = json.loads(cached_data)
            # Try to build PermissionResponse; if model fields don't match (e.g. schema change), discard cache
            try:
                return PermissionResponse(**data)
            except Exception as model_err:
                logger.warning(f"Stale cache schema for user {user_guid}, discarding: {model_err}")
                await self.delete(key)
                return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for cached permissions (user={user_guid}): {e}")
            await self.delete(key)
            return None
        except Exception as e:
            logger.error(f"Redis error getting cached permissions (user={user_guid}): {e}")
            return None

    async def delete_cached_permissions(self, user_guid: str) -> bool:
        """
        Remove cached user permissions from Redis.
        Returns True if key existed, False otherwise.
        """
        key = _permission_cache_key(user_guid)
        try:
            result = await self.delete(key)
            if result:
                logger.debug(f"Cleared cached permissions for user {user_guid}")
            return bool(result)
        except Exception as e:
            logger.error(f"Redis error deleting cached permissions (user={user_guid}): {e}")
            return False


class RedisDependency:
    """FastAPI Dependency for Redis Connections"""

    redis = None

    async def __call__(self):
        if self.redis is None:
            await self.init()
        return self.redis

    async def init(self):
        """Initialises the Redis Dependency"""
        if settings.SYSTEM_DEBUG_MODE:
            self.redis = await RedisBackend.init(f"redis://{REDIS_HOST}:{REDIS_PORT}")
        else:
            self.redis = await RedisBackend.init(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}")


redis_dependency: RedisDependency = RedisDependency()


async def get_redis() -> RedisBackend:
    """Returns a NEW Redis connection"""
    if settings.SYSTEM_DEBUG_MODE:
        return await RedisBackend.init(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    return await RedisBackend.init(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}")