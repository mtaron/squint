import ssl

from capo_s3 import AsyncS3Client
from zapros import AsyncStdNetworkHandler

from squint_core.config import require_env


def create_client() -> AsyncS3Client:
    ssl_context = ssl.create_default_context(cafile=require_env("AWS_CA_BUNDLE"))
    return AsyncS3Client(
        http_handler=AsyncStdNetworkHandler(ssl_context=ssl_context),
        endpoint=require_env("AWS_ENDPOINT_URL"),
        region=require_env("AWS_REGION"),
        credentials={
            "access_key": require_env("AWS_ACCESS_KEY_ID"),
            "secret_key": require_env("AWS_SECRET_ACCESS_KEY"),
        },
        force_path_style=True,
    )
