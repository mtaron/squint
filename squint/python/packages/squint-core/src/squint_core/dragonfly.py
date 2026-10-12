from redis.asyncio import Redis

from squint_core.config import require_env


def create_client() -> Redis:
    return Redis.from_url(require_env("REDIS_URL"), decode_responses=True)
