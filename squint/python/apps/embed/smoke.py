"""Checks what the tests can't: real retrieval through the cluster's Milvus, in a throwaway
collection. Run it with `task embed-smoke` after changing the model, schema or quantization."""

import asyncio
import json
import math
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image
from pymilvus import AsyncMilvusClient
from squint_core.embedding import EMBED_BATCH_SIZE
from squint_core.processes import ProcessWorkers
from squint_vector import milvus, pages
from squint_vector.pages import PageVectors

from encoder import Encoded, Encoder, load_model
from token_compression import limit_to_one_thread

FIXTURES = Path(__file__).parent / "tests" / "fixtures"
USER_ID = "smoke"
OTHER_USER_ID = "someone-else"


def sum_of_best_matches(query: np.ndarray, page: np.ndarray) -> float:
    """What MAX_SIM_IP should score, if Milvus doesn't normalize anything."""
    similarities = query.astype(np.int64) @ page.astype(np.int64).T
    return float(similarities.max(axis=1).sum())


async def encode_fixtures(encoder: Encoder) -> dict[str, Encoded]:
    """One page at a time, since this shares a GPU with the running worker."""
    encoded = {}
    for path in sorted(FIXTURES.glob("*.jpg")):
        image = Image.open(path).convert("RGB")
        [encoded[path.stem]] = await encoder.encode_pages([image])
    return encoded


async def check_retrieval(
    client: AsyncMilvusClient,
    collection: str,
    encoder: Encoder,
    encoded: dict[str, Encoded],
) -> None:
    await pages.upsert_pages(
        client,
        [
            PageVectors(
                document_id=name,
                user_id=USER_ID,
                page_number=1,
                dense=page.dense,
                tokens=page.tokens,
            )
            for name, page in encoded.items()
        ],
        collection,
    )

    entries = json.loads((FIXTURES / "queries.json").read_text())
    queries = encoder.encode_queries([entry["query"] for entry in entries])
    for entry, query in zip(entries, queries, strict=True):
        matches = await pages.search_pages(
            client, USER_ID, query.tokens, limit=len(encoded), collection=collection
        )
        best = matches[0]
        assert best.document_id == Path(entry["page"]).stem, (entry, matches)
        for match in matches:
            expected = sum_of_best_matches(
                query.tokens, encoded[match.document_id].tokens
            )
            assert math.isclose(match.score, expected, rel_tol=1e-6), (match, expected)
        print(f"found {best.document_id} for {entry['query']!r}")

        others = await pages.search_pages(
            client, OTHER_USER_ID, query.tokens, limit=1, collection=collection
        )
        assert not others, others

    deleted = next(iter(encoded))
    await pages.delete_documents(client, [deleted], collection)
    remaining = await pages.search_pages(
        client, USER_ID, queries[0].tokens, limit=len(encoded), collection=collection
    )
    assert deleted not in {match.document_id for match in remaining}, remaining


async def run() -> None:
    processor, model = load_model()
    client = milvus.create_client()
    collection = f"smoke_{uuid4().hex}"
    try:
        with ProcessWorkers(EMBED_BATCH_SIZE, limit_to_one_thread) as workers:
            encoder = Encoder(processor, model, workers)
            encoded = await encode_fixtures(encoder)
            await pages.ensure_collection(client, collection)
            await check_retrieval(client, collection, encoder, encoded)
    finally:
        await client.drop_collection(collection)
        await client.close()
    print("embed smoke test passed")


if __name__ == "__main__":
    asyncio.run(run())
