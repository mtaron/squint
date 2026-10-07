from temporalio.client import Client

from squint_core.config import require_env


async def create_client() -> Client:
    return await Client.connect(require_env("TEMPORAL_ADDRESS"))
