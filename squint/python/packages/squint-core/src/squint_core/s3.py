import ssl

from capo_s3 import AsyncS3Client
from zapros import AsyncIOTransport, AsyncStdNetworkHandler

from squint_core.config import require_env


def _ssl_context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=require_env("AWS_CA_BUNDLE"))


def _connection_settings():
    return {
        "endpoint": require_env("AWS_ENDPOINT_URL"),
        "region": require_env("AWS_REGION"),
        "credentials": {
            "access_key": require_env("AWS_ACCESS_KEY_ID"),
            "secret_key": require_env("AWS_SECRET_ACCESS_KEY"),
        },
        "force_path_style": True,
    }


def create_client() -> AsyncS3Client:
    return AsyncS3Client(
        http_handler=AsyncStdNetworkHandler(
            transport=AsyncIOTransport(ssl_context=_ssl_context())
        ),
        **_connection_settings(),
    )
