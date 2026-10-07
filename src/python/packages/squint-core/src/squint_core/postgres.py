import asyncpg

from squint_core.config import require_env


async def create_client() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        host=require_env("PGHOST"),
        port=int(require_env("PGPORT")),
        user=require_env("PGUSER"),
        password=require_env("PGPASSWORD"),
        database=require_env("PGDATABASE"),
    )
