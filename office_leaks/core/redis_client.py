import logging
import redis
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Centralized Redis client singleton for Office Leaks.

    Usage:
        from core.redis_client import get_redis_client

        r = get_redis_client()
        r.set("key", "value", ex=300)   # Set string key with 300s TTL
        val = r.get("key")               # Get value
        r.delete("key")                  # Delete key
        r.hset("hash_name", "k", "v")    # Hash operations
        r.incrby("counter_key", 1)       # Increment counter
    """

    _client: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """Return raw Redis connection instance (lazy initialization)."""
        if cls._client is None:
            redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/0')
            cls._client = redis.Redis.from_url(
                redis_url,
                decode_responses=True  # Converts Redis byte responses directly to Python strings
            )
            logger.info("Initialized Redis client connection.")
        return cls._client

    @classmethod
    def ping(cls) -> bool:
        """Check if Redis server is online and responding."""
        try:
            return cls.get_client().ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False


def get_redis_client() -> redis.Redis:
    """Helper function to quickly obtain the Redis client instance."""
    return RedisClient.get_client()
