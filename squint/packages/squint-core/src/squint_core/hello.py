import asyncio

from squint_core import cache, postgres, s3, temporal


async def hello_world() -> None:
    checks = {
        "postgres": postgres.ping,
        "cache": cache.ping,
        "s3": s3.ping,
        "temporal": temporal.ping,
    }
    results = await asyncio.gather(
        *(check() for check in checks.values()), return_exceptions=True
    )
    for name, result in zip(checks, results):
        if isinstance(result, BaseException):
            print(f"FAIL {name}: {result!r}")
        else:
            print(f"ok   {name}: {result}")
