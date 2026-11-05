import io
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

import numpy as np
import pytest
from capo_s3.errors import NoSuchKey
from PIL import Image
from squint_core.documents import DOCUMENT_DELETED
from squint_core.embedding import EmbedPagesInput, EncodedQuery
from temporalio.exceptions import ApplicationError
from temporalio.testing import ActivityEnvironment

from activities import EmbedActivities
from encoder import Encoded

DOCUMENT_ID = "V3kQ9xTz2m"
USER_ID = UUID("0f8fad5b-d9cb-469f-a165-70867728950e")

INPUT = EmbedPagesInput(
    document_id=DOCUMENT_ID,
    user_id=USER_ID,
    bucket=f"squint-u-{USER_ID}",
    page_numbers=[1, 2],
)


def page_image() -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (200, 100), "white").save(output, format="JPEG")
    return output.getvalue()


class FakeDb:
    def __init__(self, rows: list[dict], updated: int = 2) -> None:
        self.rows = rows
        self.updated = updated
        self.marked: list[list[int]] = []

    async def fetch(self, _query: str, _document_id: str, _pages: list[int]) -> list:
        return self.rows

    async def execute(self, _query: str, _document_id: str, pages: list[int]) -> str:
        self.marked.append(pages)
        return f"UPDATE {self.updated}"


class FakeS3:
    def __init__(self, missing: bool = False) -> None:
        self.missing = missing

    @asynccontextmanager
    async def get_object(self, _bucket: str, _key: str):
        if self.missing:
            raise NoSuchKey({}, response=None)  # ty: ignore[invalid-argument-type]

        async def body() -> AsyncIterator[bytes]:
            yield page_image()

        yield {"body": body()}


class FakeMilvus:
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.deleted: list[dict] = []

    async def upsert(self, _collection: str, rows: list[dict]) -> None:
        self.rows.extend(rows)

    async def delete(self, _collection: str, **options) -> None:
        self.deleted.append(options)


class FakeEncoder:
    def __init__(self) -> None:
        self.sizes: list[tuple[int, int]] = []

    async def encode_pages(self, images: list[Image.Image]) -> list[Encoded]:
        self.sizes = [image.size for image in images]
        return [
            Encoded(
                dense=np.zeros(1024, dtype=np.float32),
                tokens=np.ones((3, 128), dtype=np.int8),
            )
            for _ in images
        ]

    def encode_queries(self, queries: list[str]) -> list[Encoded]:
        return [
            Encoded(
                dense=np.full(1024, 0.5, dtype=np.float32),
                tokens=np.full((len(query.split()), 128), -3, dtype=np.int8),
            )
            for query in queries
        ]


def rows() -> list[dict]:
    return [
        {"page_number": 1, "content_box": [10, 20, 110, 70]},
        {"page_number": 2, "content_box": None},
    ]


async def embed(db: FakeDb, s3: FakeS3 | None = None) -> tuple[FakeMilvus, FakeEncoder]:
    milvus = FakeMilvus()
    encoder = FakeEncoder()
    activities = EmbedActivities(
        db,  # ty: ignore[invalid-argument-type]
        s3 or FakeS3(),  # ty: ignore[invalid-argument-type]
        milvus,  # ty: ignore[invalid-argument-type]
        encoder,  # ty: ignore[invalid-argument-type]
    )
    await ActivityEnvironment().run(activities.embed_pages, INPUT)
    return milvus, encoder


async def test_crops_pages_to_their_content_but_leaves_blank_ones_whole():
    _milvus, encoder = await embed(FakeDb(rows()))

    assert encoder.sizes == [(100, 50), (200, 100)]


async def test_stores_a_row_for_each_page_with_the_owner():
    milvus, _encoder = await embed(FakeDb(rows()))

    assert [row["id"] for row in milvus.rows] == [
        f"{DOCUMENT_ID}-1",
        f"{DOCUMENT_ID}-2",
    ]
    assert {row["user_id"] for row in milvus.rows} == {str(USER_ID)}
    assert len(milvus.rows[0]["tokens"]) == 3


async def test_marks_the_pages_embedded_after_storing_them():
    db = FakeDb(rows())

    await embed(db)

    assert db.marked == [[1, 2]]


@pytest.mark.parametrize(
    "db, s3",
    [
        pytest.param(FakeDb([]), None, id="its rows are gone"),
        pytest.param(FakeDb(rows()), FakeS3(missing=True), id="its images are gone"),
        pytest.param(FakeDb(rows(), updated=0), None, id="deleted while embedding"),
    ],
)
async def test_notices_a_deleted_document(db: FakeDb, s3: FakeS3 | None):
    with pytest.raises(ApplicationError) as error:
        await embed(db, s3)

    assert error.value.type == DOCUMENT_DELETED
    assert error.value.non_retryable


async def test_deletes_vectors_by_document_and_by_user():
    milvus = FakeMilvus()
    activities = EmbedActivities(
        FakeDb([]),  # ty: ignore[invalid-argument-type]
        FakeS3(),  # ty: ignore[invalid-argument-type]
        milvus,  # ty: ignore[invalid-argument-type]
        FakeEncoder(),  # ty: ignore[invalid-argument-type]
    )

    await ActivityEnvironment().run(activities.delete_document_vectors, [DOCUMENT_ID])
    await ActivityEnvironment().run(activities.delete_user_vectors, str(USER_ID))

    assert milvus.deleted[0]["filter_params"] == {"document_ids": [DOCUMENT_ID]}
    assert milvus.deleted[1]["filter_params"] == {"user_id": str(USER_ID)}


async def test_encodes_a_query_into_plain_lists_for_the_search_workflow():
    activities = EmbedActivities(
        FakeDb([]),  # ty: ignore[invalid-argument-type]
        FakeS3(),  # ty: ignore[invalid-argument-type]
        FakeMilvus(),  # ty: ignore[invalid-argument-type]
        FakeEncoder(),  # ty: ignore[invalid-argument-type]
    )

    encoded = await ActivityEnvironment().run(activities.encode_query, "net revenue")

    assert isinstance(encoded, EncodedQuery)
    assert len(encoded.dense) == 1024
    assert encoded.tokens == [[-3] * 128, [-3] * 128]
