import asyncpg


async def ping() -> str:
    """Connect to postgres and return the server version.

    Connection settings come from the standard PG* environment variables
    (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE), defaulting to localhost.
    """
    conn = await asyncpg.connect()
    try:
        return await conn.fetchval("SELECT version()")
    finally:
        await conn.close()
