"""Times dense and multi-vector searches over a growing number of pages, in a throwaway collection on
the cluster's Milvus, to choose DENSE_SEARCH_MIN_PAGES for this deployment. Run it with
`task search-bench`, which renders the pages and copies them here.

Below the threshold, a search scores every page with the late-interaction vectors. Above it, a
dense search picks candidates for the late-interaction vectors to rerank. That pays off once
scoring all the pages takes longer than the dense search plus the rerank."""

import asyncio
import json
import shutil
import statistics
import sys
import time
from collections.abc import Awaitable
from pathlib import Path
from uuid import uuid4

import numpy as np
from pymilvus import AsyncMilvusClient, DataType
from pymilvus.client.embedding_list import EmbeddingList
from squint_core.embedding import EMBED_BATCH_SIZE
from squint_core.processes import ProcessWorkers
from squint_vector import milvus, pages
from squint_vector.pages import TOKENS_FIELD, TOKENS_METRIC, PageVectors

from activities import decode_page
from encoder import Encoded, Encoder, load_model
from token_compression import compress_tokens, limit_to_one_thread

USER_ID = "search-bench"
QUERY_COUNT = 20
PAGE_COUNTS = [1, 2, 5, 10, 20, 50, 100, 150, 200, 300, 400, 600]
CANDIDATE_COUNTS = [10, 20, 50, 100]
RESULT_LIMIT = 10
WARM_UP_SEARCHES = 20
UPSERT_BATCH_SIZE = 64


def load_cached(path: Path) -> list[PageVectors]:
    cache = np.load(path)
    tokens = np.split(cache["tokens"], np.cumsum(cache["token_counts"])[:-1])
    return [
        PageVectors(
            document_id=str(document_id),
            user_id=USER_ID,
            page_number=int(page_number),
            dense=dense,
            tokens=page_tokens,
        )
        for document_id, page_number, dense, page_tokens in zip(
            cache["document_ids"],
            cache["page_numbers"],
            cache["dense"],
            tokens,
            strict=True,
        )
    ]


def save_cached(path: Path, encoded: list[PageVectors]) -> None:
    np.savez(
        path,
        document_ids=np.array([page.document_id for page in encoded]),
        page_numbers=np.array([page.page_number for page in encoded]),
        dense=np.stack([page.dense for page in encoded]),
        tokens=np.concatenate([page.tokens for page in encoded]),
        token_counts=np.array([len(page.tokens) for page in encoded]),
    )


async def encode_pages(encoder: Encoder, bench: Path) -> list[PageVectors]:
    """Encoding takes minutes, so the vectors are kept for the next run, and the pages, which take
    gigabytes, are removed."""
    cache = bench / "vectors.npz"
    if cache.exists():
        return load_cached(cache)

    content_boxes = json.loads((bench / "content_boxes.json").read_text())
    # The GPU, shared with the running worker and vLLM, only has room for one page at a time, while
    # pooling takes several times as long and runs a page per process
    in_flight = asyncio.Semaphore(2 * encoder.workers.size)
    gpu = asyncio.Lock()

    async def encode(document_id: str, page_number: str, box: list[int] | None):
        path = bench / "pages" / document_id / f"{page_number}.jpg"
        async with in_flight:
            image = await asyncio.to_thread(decode_page, path.read_bytes(), box)
            async with gpu:
                [tokens], [dense] = await asyncio.to_thread(
                    encoder.forward_pages, [image]
                )
            pooled = await encoder.workers.run(compress_tokens, tokens.numpy())
        return PageVectors(
            document_id=document_id,
            user_id=USER_ID,
            page_number=int(page_number),
            dense=dense,
            tokens=pooled,
        )

    encoded = await asyncio.gather(
        *(
            encode(document_id, page_number, box)
            for document_id, boxes in content_boxes.items()
            for page_number, box in boxes.items()
        )
    )
    save_cached(cache, encoded)
    shutil.rmtree(bench / "pages")
    return encoded


def sample_queries(bench: Path) -> list[str]:
    queries = json.loads((bench / "queries.json").read_text())
    return queries[:: len(queries) // QUERY_COUNT][:QUERY_COUNT]


def scope(document_id: str, page_count: int) -> str:
    """The first pages of one document, the way extraction will search a document's pages."""
    return (
        f"user_id == '{USER_ID}' and document_id == '{document_id}'"
        f" and page_number <= {page_count}"
    )


async def dense_search(
    client: AsyncMilvusClient, collection: str, query: Encoded, filter: str, limit: int
) -> list[str]:
    results = await client.search(
        collection,
        data=[query.dense],
        anns_field="dense",
        search_params={"metric_type": "COSINE"},
        filter=filter,
        limit=limit,
    )
    return [hit["id"] for hit in results[0]]


async def multi_vector_search(
    client: AsyncMilvusClient,
    collection: str,
    query: Encoded,
    filter: str,
    limit: int,
    filter_params: dict | None = None,
) -> list[str]:
    results = await client.search(
        collection,
        data=[EmbeddingList(query.tokens, dtype=DataType.INT8_VECTOR)],
        anns_field=TOKENS_FIELD,
        search_params={"metric_type": TOKENS_METRIC},
        filter=filter,
        filter_params=filter_params or {},
        limit=limit,
    )
    return [hit["id"] for hit in results[0]]


def rerank(
    client: AsyncMilvusClient, collection: str, query: Encoded, candidates: list[str]
) -> Awaitable[list[str]]:
    return multi_vector_search(
        client,
        collection,
        query,
        "id in {ids}",
        RESULT_LIMIT,
        filter_params={"ids": candidates},
    )


async def timed(search: Awaitable[list[str]]) -> float:
    """Milliseconds, as the worker would wait for them."""
    start = time.perf_counter()
    await search
    return (time.perf_counter() - start) * 1000


def summarize(samples: list[float]) -> dict[str, float]:
    deciles = statistics.quantiles(samples, n=10)
    return {"p50": statistics.median(samples), "p90": deciles[-1]}


async def measure(
    client: AsyncMilvusClient,
    collection: str,
    documents: dict[str, int],
    queries: list[Encoded],
) -> dict:
    """Each query against each document long enough, alternating the two searches so drift hits
    both."""
    shortest = min(documents.values())
    for query in queries[:WARM_UP_SEARCHES]:
        filter = scope(next(iter(documents)), shortest)
        await dense_search(client, collection, query, filter, RESULT_LIMIT)
        await multi_vector_search(client, collection, query, filter, RESULT_LIMIT)

    full_scans = {}
    longest = max(documents.values())
    for page_count in [count for count in PAGE_COUNTS if count <= longest]:
        dense, multi_vector = [], []
        long_enough = [
            document_id
            for document_id, document_pages in documents.items()
            if document_pages >= page_count
        ]
        for document_id in long_enough:
            filter = scope(document_id, page_count)
            for query in queries:
                dense.append(
                    await timed(
                        dense_search(
                            client, collection, query, filter, max(CANDIDATE_COUNTS)
                        )
                    )
                )
                multi_vector.append(
                    await timed(
                        multi_vector_search(
                            client, collection, query, filter, RESULT_LIMIT
                        )
                    )
                )
        full_scans[page_count] = {
            "dense": summarize(dense),
            "multi_vector": summarize(multi_vector),
        }

    reranks = {}
    for candidate_count in CANDIDATE_COUNTS:
        samples = []
        for document_id in documents:
            for query in queries:
                candidates = await dense_search(
                    client,
                    collection,
                    query,
                    scope(document_id, shortest),
                    candidate_count,
                )
                samples.append(
                    await timed(rerank(client, collection, query, candidates))
                )
        reranks[candidate_count] = summarize(samples)
    return {"full_scans": full_scans, "reranks": reranks}


def crossover(result: dict, candidate_count: int) -> float | None:
    """The page count where scoring every page starts costing more than a dense search and a
    rerank, interpolated between the measured counts."""
    rerank_ms = result["reranks"][candidate_count]["p50"]
    previous = None
    for page_count, scans in result["full_scans"].items():
        if page_count <= candidate_count:
            continue
        excess = scans["multi_vector"]["p50"] - scans["dense"]["p50"] - rerank_ms
        if excess > 0:
            if previous is None:
                return page_count
            previous_count, previous_excess = previous
            return previous_count + (page_count - previous_count) * (
                -previous_excess / (excess - previous_excess)
            )
        previous = (page_count, excess)
    return None


def report(phase: str, segments: list, result: dict) -> None:
    print(f"\n== {phase}: {segments}")
    print(f"{'pages':>6} {'dense p50/p90 ms':>18} {'multi-vector p50/p90 ms':>25}")
    for page_count, scans in result["full_scans"].items():
        dense, multi_vector = scans["dense"], scans["multi_vector"]
        print(
            f"{page_count:>6} {dense['p50']:>9.1f} / {dense['p90']:<6.1f}"
            f" {multi_vector['p50']:>12.1f} / {multi_vector['p90']:<6.1f}"
        )
    for candidate_count, rerank_ms in result["reranks"].items():
        threshold = crossover(result, candidate_count)
        print(
            f"rerank {candidate_count:>3} candidates: {rerank_ms['p50']:.1f} / "
            f"{rerank_ms['p90']:.1f} ms; dense first from "
            + (f"{threshold:.0f} pages" if threshold else "beyond the pages measured")
        )


async def segment_states(client: AsyncMilvusClient, collection: str) -> list:
    segments = await client.list_segments(collection)
    return sorted((str(segment.state), segment.num_rows) for segment in segments)


async def wait_for_indexes(client: AsyncMilvusClient, collection: str) -> None:
    for index_name in await client.list_indexes(collection):
        while True:
            index = await client.describe_index(collection, index_name)
            if index["pending_index_rows"] == 0 and index["state"] == "Finished":
                break
            await asyncio.sleep(1)


async def benchmark(
    client: AsyncMilvusClient,
    collection: str,
    encoded: list[PageVectors],
    queries: list[Encoded],
) -> dict:
    documents = {}
    for page in encoded:
        documents[page.document_id] = documents.get(page.document_id, 0) + 1

    await pages.ensure_collection(client, collection)
    for start in range(0, len(encoded), UPSERT_BATCH_SIZE):
        await pages.upsert_pages(
            client, encoded[start : start + UPSERT_BATCH_SIZE], collection
        )

    results = {}
    # Extraction can follow embedding closely enough that the pages haven't been sealed yet
    segments = await segment_states(client, collection)
    results["growing"] = await measure(client, collection, documents, queries)
    report("growing", segments, results["growing"])

    await client.flush(collection)
    await wait_for_indexes(client, collection)
    await client.release_collection(collection)
    await client.load_collection(collection)
    segments = await segment_states(client, collection)
    results["sealed"] = await measure(client, collection, documents, queries)
    report("sealed", segments, results["sealed"])
    return results


async def run(bench: Path) -> None:
    processor, model = load_model()
    client = milvus.create_client()
    collection = f"search_bench_{uuid4().hex}"
    try:
        with ProcessWorkers(EMBED_BATCH_SIZE, limit_to_one_thread) as workers:
            encoder = Encoder(processor, model, workers)
            encoded = await encode_pages(encoder, bench)
            queries = encoder.encode_queries(sample_queries(bench))
        print(
            f"{len(encoded)} pages averaging"
            f" {np.mean([len(page.tokens) for page in encoded]):.0f} tokens;"
            f" {len(queries)} queries averaging"
            f" {np.mean([len(query.tokens) for query in queries]):.0f} tokens"
        )
        results = await benchmark(client, collection, encoded, queries)
        (bench / "results.json").write_text(json.dumps(results, indent=2))
    finally:
        await client.drop_collection(collection)
        await client.close()


if __name__ == "__main__":
    asyncio.run(run(Path(sys.argv[1])))
