import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("taskforge.redis")


class RedisService:
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self._memory_cache: Dict[str, str] = {}
        self._subscribers: Dict[str, list] = {}
        self.is_connected = False

    async def connect(self):
        try:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2.0
            )
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Connected to Redis broker successfully.")
        except Exception as e:
            self.is_connected = False
            self.redis_client = None
            logger.warning(f"Could not connect to Redis at {settings.REDIS_URL} ({e}). Using in-memory fallback broker.")

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False

    async def ping(self) -> bool:
        if self.redis_client:
            try:
                res = await self.redis_client.ping()
                return bool(res)
            except Exception:
                return False
        return False

    async def get(self, key: str) -> Optional[str]:
        if self.is_connected and self.redis_client:
            try:
                return await self.redis_client.get(key)
            except Exception:
                pass
        return self._memory_cache.get(key)

    async def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        if self.is_connected and self.redis_client:
            try:
                await self.redis_client.set(key, value, ex=expire_seconds)
                return True
            except Exception:
                pass
        self._memory_cache[key] = value
        return True

    async def publish(self, channel: str, message: Any):
        payload = json.dumps(message) if not isinstance(message, str) else message
        if self.is_connected and self.redis_client:
            try:
                await self.redis_client.publish(channel, payload)
            except Exception as e:
                logger.error(f"Failed to publish to Redis: {e}")
        
        # Also broadcast in-memory to any registered listeners
        callbacks = self._subscribers.get(channel, [])
        for cb in callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    asyncio.create_task(cb(payload))
                else:
                    cb(payload)
            except Exception as e:
                logger.error(f"Error executing callback for channel {channel}: {e}")

    def subscribe_in_memory(self, channel: str, callback: Callable):
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)


redis_service = RedisService()
