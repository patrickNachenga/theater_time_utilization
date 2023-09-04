from typing import Set, Any

from aioredis import Redis as RedisConnection
from aioredis import from_url

from src.core.config import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD


class RedisBackend:
    redis_connection: RedisConnection

    @staticmethod
    async def init(url: str) -> "RedisBackend":
        redis = RedisBackend()
        redis.redis_connection = await from_url(url)
        return redis

    async def get(self, key: str):
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

    async def delete(self, key: str):
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


class RedisDependency:
    """FastAPI Dependency for Redis Connections"""

    redis = None

    async def __call__(self):
        if self.redis is None:
            await self.init()
        return self.redis

    async def init(self):
        """Initialises the Redis Dependency"""
        if settings.DEBUG_MODE:
            self.redis = await RedisBackend.init(f"redis://{REDIS_HOST}:{REDIS_PORT}")
        else:
            self.redis = await RedisBackend.init(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}")


redis_dependency: RedisDependency = RedisDependency()


async def get_redis() -> RedisBackend:
    """Returns a NEW Redis connection"""
    if settings.DEBUG_MODE:
        return await RedisBackend.init(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    return await RedisBackend.init(f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}")
