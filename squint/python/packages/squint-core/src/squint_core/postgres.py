import asyncpg

from squint_core.config import require_env

# Every worker pod connects, and they share max_connections with the UI and Temporal. Workers run
# few activities at a time, so asyncpg's default of 10 per pod would be wasted.
MAX_CONNECTIONS_PER_POD = 2


async def create_client() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        host=require_env("PGHOST"),
        port=int(require_env("PGPORT")),
        user=require_env("PGUSER"),
        password=require_env("PGPASSWORD"),
        database=require_env("PGDATABASE"),
        min_size=1,
        max_size=MAX_CONNECTIONS_PER_POD,
    )
