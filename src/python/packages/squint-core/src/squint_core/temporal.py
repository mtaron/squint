import os

from temporalio.client import Client


async def ping() -> bool:
    """Connect to temporal and return whether the workflow service is healthy.

    The address comes from TEMPORAL_ADDRESS, defaulting to localhost:7233.
    """
    client = await Client.connect(os.environ.get("TEMPORAL_ADDRESS", "localhost:7233"))
    return await client.service_client.check_health()
