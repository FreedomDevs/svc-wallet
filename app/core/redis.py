import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self._redis = None

    async def get_redis(self):
        if not self._redis:
            self._redis = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD or None,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

redis_client = RedisClient()
