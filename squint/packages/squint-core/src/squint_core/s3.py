import os

from capo_s3 import AsyncS3Client


async def ping() -> list[str]:
    """List the buckets in object storage (versitygw) and return their names.

    The endpoint comes from AWS_ENDPOINT_URL, defaulting to http://localhost:7070.
    Credentials come from AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
    """
    async with AsyncS3Client(
        endpoint=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:7070"),
        region=os.environ.get("AWS_REGION", "us-east-1"),
        force_path_style=True,
    ) as client:
        output = await client.list_buckets()
        return [name for b in output.get("buckets", []) if (name := b.get("name"))]
