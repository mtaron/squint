"""Page vectors, stored in Milvus: one row per page, holding NeoMME's dense vector and its pooled,
quantized late-interaction vectors."""

import numpy as np
from pydantic import BaseModel, ConfigDict
from pymilvus import AsyncMilvusClient, DataType
from pymilvus.client.embedding_list import EmbeddingList

COLLECTION = "pages"
DENSE_DIMENSIONS = 1024
TOKEN_DIMENSIONS = 128
# Pool factor 10 leaves at most 417 of the 4,162 tokens a square page has at NeoMME's 2048 px cap
MAX_TOKENS_PER_PAGE = 512
TOKENS_FIELD = "tokens[embedding]"
# Named outright since plain MAX_SIM means cosine. NeoMME's scores are dot products of unit vectors,
# and the quantized tokens all share one scale, so this keeps those scores up to that scale. Milvus
# sums each query token's best match where NeoMME's MeanMaxSim averages them, which ranks the same.
TOKENS_METRIC = "MAX_SIM_IP"


class PageVectors(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    document_id: str
    user_id: str
    page_number: int
    dense: np.ndarray
    tokens: np.ndarray


class PageMatch(BaseModel):
    model_config = ConfigDict(frozen=True)

    document_id: str
    page_number: int
    score: float


class SearchOptions(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: str
    document_id: str | None = None

    def filter(self) -> tuple[str, dict[str, str]]:
        if self.document_id is None:
            return "user_id == {user_id}", {"user_id": self.user_id}
        return (
            "user_id == {user_id} and document_id == {document_id}",
            {"user_id": self.user_id, "document_id": self.document_id},
        )


def page_id(document_id: str, page_number: int) -> str:
    return f"{document_id}-{page_number}"


async def ensure_collection(
    client: AsyncMilvusClient, collection: str = COLLECTION
) -> None:
    if await client.has_collection(collection):
        return

    schema = client.create_schema(auto_id=False, enable_dynamic_field=False)
    schema.add_field("id", DataType.VARCHAR, is_primary=True, max_length=64)
    # One partition key per user keeps each search to the partitions holding that user's pages
    schema.add_field("user_id", DataType.VARCHAR, max_length=36, is_partition_key=True)
    schema.add_field("document_id", DataType.VARCHAR, max_length=32)
    schema.add_field("page_number", DataType.INT32)
    schema.add_field("dense", DataType.FLOAT_VECTOR, dim=DENSE_DIMENSIONS)
    token = client.create_struct_field_schema()
    token.add_field("embedding", DataType.INT8_VECTOR, dim=TOKEN_DIMENSIONS)
    schema.add_field(
        "tokens",
        DataType.ARRAY,
        element_type=DataType.STRUCT,
        struct_schema=token,
        max_capacity=MAX_TOKENS_PER_PAGE,
    )

    indexes = client.prepare_index_params()
    indexes.add_index("document_id", index_type="INVERTED")
    indexes.add_index(field_name="dense", index_type="AUTOINDEX", metric_type="COSINE")
    # Milvus only indexes int8 embedding lists with the HNSW family, so AUTOINDEX isn't an option
    indexes.add_index(
        TOKENS_FIELD,
        index_type="HNSW",
        metric_type=TOKENS_METRIC,
        params={"M": 16, "efConstruction": 200},
    )
    await client.create_collection(
        collection,
        schema=schema,
        index_params=indexes,
        consistency_level="Strong",
    )


async def upsert_pages(
    client: AsyncMilvusClient, pages: list[PageVectors], collection: str = COLLECTION
) -> None:
    await client.upsert(
        collection,
        [
            {
                "id": page_id(page.document_id, page.page_number),
                "user_id": page.user_id,
                "document_id": page.document_id,
                "page_number": page.page_number,
                "dense": page.dense,
                "tokens": [{"embedding": token} for token in page.tokens],
            }
            for page in pages
        ],
    )


def matches(results: list) -> list[PageMatch]:
    return [
        PageMatch(
            document_id=hit["entity"]["document_id"],
            page_number=hit["entity"]["page_number"],
            score=hit["distance"],
        )
        for hit in results[0]
    ]


async def count_pages(
    client: AsyncMilvusClient, options: SearchOptions, collection: str = COLLECTION
) -> int:
    filter, filter_params = options.filter()
    [row] = await client.query(
        collection,
        filter=filter,
        filter_params=filter_params,
        output_fields=["count(*)"],
    )
    return row["count(*)"]


async def dense_search(
    client: AsyncMilvusClient,
    options: SearchOptions,
    query_dense: np.ndarray,
    *,
    limit: int,
    collection: str = COLLECTION,
) -> list[PageMatch]:
    filter, filter_params = options.filter()
    results = await client.search(
        collection,
        data=[query_dense],
        anns_field="dense",
        search_params={"metric_type": "COSINE"},
        filter=filter,
        filter_params=filter_params,
        limit=limit,
        output_fields=["document_id", "page_number"],
    )
    return matches(results)


async def late_search(
    client: AsyncMilvusClient,
    options: SearchOptions,
    query_tokens: np.ndarray,
    *,
    limit: int,
    candidates: list[PageMatch] | None = None,
    collection: str = COLLECTION,
) -> list[PageMatch]:
    filter, filter_params = options.filter()
    if candidates is not None:
        filter = f"{filter} and id in {{ids}}"
        filter_params = {
            **filter_params,
            "ids": [page_id(page.document_id, page.page_number) for page in candidates],
        }
    results = await client.search(
        collection,
        data=[EmbeddingList(query_tokens, dtype=DataType.INT8_VECTOR)],
        anns_field=TOKENS_FIELD,
        search_params={"metric_type": TOKENS_METRIC},
        filter=filter,
        filter_params=filter_params,
        limit=limit,
        output_fields=["document_id", "page_number"],
    )
    return matches(results)


async def delete_documents(
    client: AsyncMilvusClient, document_ids: list[str], collection: str = COLLECTION
) -> None:
    await client.delete(
        collection,
        filter="document_id in {document_ids}",
        filter_params={"document_ids": document_ids},
    )


async def delete_user(
    client: AsyncMilvusClient, user_id: str, collection: str = COLLECTION
) -> None:
    await client.delete(
        collection,
        filter="user_id == {user_id}",
        filter_params={"user_id": user_id},
    )
