import base64
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import SimpleNamespace
from uuid import UUID

import pytest
from capo_s3.errors import NoSuchKey
from squint_core.documents import DOCUMENT_DELETED
from squint_core.embedding import EncodedQuery
from squint_vector.pages import TOKENS_FIELD
from temporalio.exceptions import ApplicationError
from temporalio.testing import ActivityEnvironment

from activities import (
    DENSE_CANDIDATES,
    MIN_RERANK_CANDIDATES,
    Box,
    ExtractActivities,
    FindPagesInput,
    LocateInput,
)

DOCUMENT_ID = "V3kQ9xTz2m"
USER_ID = UUID("0f8fad5b-d9cb-469f-a165-70867728950e")
DENSE_SEARCH_MIN_PAGES = 50
PAGE_IMAGE = b"\xff\xd8 a page \xff\xd9"

QUERY = EncodedQuery(dense=[0.5] * 1024, tokens=[[1] * 128, [2] * 128])


def declining(
    page_count: int, best: float = 0.6, step: float = 0.001
) -> dict[int, float]:
    """Scores without any drop, best on page 1."""
    return {page: best - step * page for page in range(1, page_count + 1)}


class FakeMilvus:
    """Scores each page by the field searched, and limits a search to its candidates."""

    def __init__(
        self, late: dict[int, float], dense: dict[int, float] | None = None
    ) -> None:
        self.late = late
        self.dense = dense or {}
        self.searches: list[dict] = []
        self.counted: list[dict] = []

    async def query(self, _collection: str, **options) -> list[dict]:
        self.counted.append(options["filter_params"])
        return [{"count(*)": len(self.late)}]

    async def search(self, _collection: str, **options) -> list[list[dict]]:
        self.searches.append(options)
        scores = self.dense if options["anns_field"] == "dense" else self.late
        ids = options["filter_params"].get("ids")
        ranked = sorted(
            (
                (page, score)
                for page, score in scores.items()
                if ids is None or f"{DOCUMENT_ID}-{page}" in ids
            ),
            key=lambda item: -item[1],
        )
        return [
            [
                {
                    "id": f"{DOCUMENT_ID}-{page}",
                    "distance": score,
                    "entity": {"document_id": DOCUMENT_ID, "page_number": page},
                }
                for page, score in ranked[: options["limit"]]
            ]
        ]

    def fields(self) -> list[str]:
        return [search["anns_field"] for search in self.searches]


class FakeS3:
    def __init__(self, missing: bool = False) -> None:
        self.missing = missing
        self.keys: list[str] = []

    @asynccontextmanager
    async def get_object(self, _bucket: str, key: str):
        self.keys.append(key)
        if self.missing:
            raise NoSuchKey({}, response=None)  # ty: ignore[invalid-argument-type]

        async def body() -> AsyncIterator[bytes]:
            yield PAGE_IMAGE

        yield {"body": body()}


class FakeVlm:
    def __init__(self, occurrences: list[dict]) -> None:
        self.chat = SimpleNamespace(completions=self)
        self.content = json.dumps({"occurrences": occurrences})
        self.requests: list[dict] = []

    async def create(self, **request) -> SimpleNamespace:
        self.requests.append(request)
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def extract_activities(
    milvus: FakeMilvus | None = None,
    s3: FakeS3 | None = None,
    vlm: FakeVlm | None = None,
) -> ExtractActivities:
    return ExtractActivities(
        s3 or FakeS3(),  # ty: ignore[invalid-argument-type]
        milvus or FakeMilvus({}),  # ty: ignore[invalid-argument-type]
        vlm or FakeVlm([]),  # ty: ignore[invalid-argument-type]
        DENSE_SEARCH_MIN_PAGES,
    )


async def find_pages(milvus: FakeMilvus, document_id: str | None = None) -> list[int]:
    matches = await ActivityEnvironment().run(
        extract_activities(milvus).find_pages,
        FindPagesInput(user_id=USER_ID, document_id=document_id, query=QUERY),
    )
    return [match.page_number for match in matches]


async def test_scores_every_page_with_late_interaction_below_the_threshold():
    milvus = FakeMilvus({1: 900.0, 2: 880.0, 3: 300.0, 4: 290.0, 5: 280.0, 6: 270.0})

    pages = await find_pages(milvus)

    assert pages == [1, 2]
    assert milvus.fields() == [TOKENS_FIELD]


async def test_sends_at_most_five_pages_when_scores_do_not_drop():
    milvus = FakeMilvus(declining(10, best=900.0, step=1.0))

    pages = await find_pages(milvus)

    assert pages == [1, 2, 3, 4, 5]


async def test_reranks_dense_candidates_above_the_threshold():
    late = declining(80, best=500.0, step=1.0) | {40: 900.0}
    milvus = FakeMilvus(late, dense=declining(80))

    pages = await find_pages(milvus)

    assert pages == [40]
    assert milvus.fields() == ["dense", TOKENS_FIELD]
    assert milvus.searches[0]["limit"] == DENSE_CANDIDATES
    assert len(milvus.searches[1]["filter_params"]["ids"]) == 80


async def test_reranks_only_the_dense_pages_above_a_drop_but_at_least_a_minimum():
    dense = declining(80, best=0.3) | {page: 0.4 - 0.001 * page for page in (1, 2, 3)}
    milvus = FakeMilvus(declining(80, best=500.0, step=1.0), dense=dense)

    await find_pages(milvus)

    assert len(milvus.searches[1]["filter_params"]["ids"]) == MIN_RERANK_CANDIDATES


async def test_skips_the_rerank_when_dense_scores_are_definitive():
    dense = declining(80, best=0.1, step=0.0001) | {7: 0.8}
    milvus = FakeMilvus(declining(80), dense=dense)

    pages = await find_pages(milvus)

    assert pages == [7]
    assert milvus.fields() == ["dense"]


async def test_searches_one_document_or_all_of_the_users_pages():
    milvus = FakeMilvus(declining(3))

    await find_pages(milvus, DOCUMENT_ID)
    await find_pages(milvus)

    assert milvus.counted == [
        {"user_id": str(USER_ID), "document_id": DOCUMENT_ID},
        {"user_id": str(USER_ID)},
    ]
    assert "document_id == {document_id}" in milvus.searches[0]["filter"]
    assert "document_id" not in milvus.searches[1]["filter"]


LOCATE = LocateInput(
    bucket=f"squint-u-{USER_ID}",
    document_id=DOCUMENT_ID,
    page_number=3,
    text="Net  Revenue",
)


async def locate(vlm: FakeVlm, s3: FakeS3 | None = None) -> list[Box]:
    return await ActivityEnvironment().run(
        extract_activities(s3=s3, vlm=vlm).locate_text, LOCATE
    )


async def test_boxes_each_occurrence_of_the_text():
    vlm = FakeVlm(
        [
            {"text": "net revenue", "bbox_2d": [100, 200, 300, 220]},
            {"text": "Total net revenue:", "bbox_2d": [100, 500, 400, 520]},
        ]
    )

    boxes = await locate(vlm)

    assert boxes == [
        Box(x1=100, y1=200, x2=300, y2=220),
        Box(x1=100, y1=500, x2=400, y2=520),
    ]


async def test_ignores_occurrences_of_other_text():
    vlm = FakeVlm([{"text": "Gross revenue", "bbox_2d": [100, 200, 300, 220]}])

    assert await locate(vlm) == []


async def test_keeps_boxes_on_the_page_and_drops_empty_ones():
    vlm = FakeVlm(
        [
            {"text": "Net Revenue", "bbox_2d": [300, 220, -5, 1200]},
            {"text": "Net Revenue", "bbox_2d": [100, 200, 100, 220]},
        ]
    )

    assert await locate(vlm) == [Box(x1=0, y1=220, x2=300, y2=1000)]


async def test_sends_qwen_the_page_image_and_the_quoted_text():
    s3 = FakeS3()
    vlm = FakeVlm([])

    await locate(vlm, s3)

    assert s3.keys == [f"documents/{DOCUMENT_ID}/pages/3.jpg"]
    [request] = vlm.requests
    image, prompt = request["messages"][0]["content"]
    encoded = base64.b64encode(PAGE_IMAGE).decode()
    assert image["image_url"]["url"] == f"data:image/jpeg;base64,{encoded}"
    assert '"Net  Revenue"' in prompt["text"]
    assert request["temperature"] == 0


async def test_notices_a_deleted_document():
    with pytest.raises(ApplicationError) as error:
        await locate(FakeVlm([]), FakeS3(missing=True))

    assert error.value.type == DOCUMENT_DELETED
    assert error.value.non_retryable
