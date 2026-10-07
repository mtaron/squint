from pymilvus import AsyncMilvusClient
from squint_core.config import require_env


def create_client() -> AsyncMilvusClient:
    return AsyncMilvusClient(
        uri=require_env("MILVUS_URI"),
        ca_pem_path=require_env("MILVUS_CA_PEM_PATH"),
        client_pem_path=require_env("MILVUS_CLIENT_PEM_PATH"),
        client_key_path=require_env("MILVUS_CLIENT_KEY_PATH"),
    )
