import os

from redis.asyncio import Redis


async def ping() -> str:
    """Round-trip a key through the cache (dragonfly) and return the value read back.

    The address comes from REDIS_URL, defaulting to redis://localhost:6379.
    """
    client = Redis.from_url(
        os.environ.get("REDIS_URL", "redis://localhost:6379"), decode_responses=True
    )
    try:
        await client.set("squint:ping", "pong", ex=60)
        return str(await client.get("squint:ping"))
    finally:
        await client.aclose()
