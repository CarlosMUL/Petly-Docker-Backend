import redis.asyncio as aioredis

from config import settings

_client: aioredis.Redis | None = None


async def connect() -> None:
    global _client
    _client = aioredis.from_url(settings.redis_url, decode_responses=True)


async def close() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None


def get_client() -> aioredis.Redis:
    if _client is None:
        raise RuntimeError("Redis no inicializado. Llama a connect() primero.")
    return _client
