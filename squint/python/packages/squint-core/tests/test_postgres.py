import asyncio

import pytest

from squint_core import postgres


def test_a_pod_holds_only_a_few_connections(monkeypatch: pytest.MonkeyPatch):
    for name in ("PGHOST", "PGUSER", "PGPASSWORD", "PGDATABASE"):
        monkeypatch.setenv(name, "squint")
    monkeypatch.setenv("PGPORT", "5432")
    options = {}

    async def create_pool(**kwargs):
        options.update(kwargs)

    monkeypatch.setattr(postgres.asyncpg, "create_pool", create_pool)

    asyncio.run(postgres.create_client())

    assert options["max_size"] * 8 < 50
