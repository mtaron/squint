from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.runtime import Runtime


async def create_client(runtime: Runtime | None = None) -> Client:
    """Connect to Temporal using the TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE and TEMPORAL_TLS_*
    environment variables."""
    return await Client.connect(
        **ClientConfig.load_client_connect_config(), runtime=runtime
    )
