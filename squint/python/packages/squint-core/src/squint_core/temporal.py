from collections.abc import Sequence

from temporalio.client import Client, Plugin
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.envconfig import ClientConfig
from temporalio.runtime import Runtime


async def create_client(
    runtime: Runtime | None = None, plugins: Sequence[Plugin] = ()
) -> Client:
    """Connect to Temporal using the TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE and TEMPORAL_TLS_*
    environment variables."""
    return await Client.connect(
        **ClientConfig.load_client_connect_config(),
        runtime=runtime,
        data_converter=pydantic_data_converter,
        plugins=plugins,
    )
