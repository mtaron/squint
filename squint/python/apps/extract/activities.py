import base64
import json
from typing import Annotated, Literal
from uuid import UUID

import numpy as np
from capo_s3 import AsyncS3Client
from capo_s3.errors import NoSuchBucket, NoSuchKey
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from pymilvus import AsyncMilvusClient
from squint_core import documents
from squint_core.documents import document_deleted
from squint_core.embedding import EncodedQuery
from squint_core.models import CamelModel
from squint_vector import pages
from squint_vector.pages import PageMatch, SearchOptions
from temporalio import activity

from cutoff import Drop, cliff

# The search-bench branch measured dense candidates in steps up to 100
DENSE_CANDIDATES = 100
# Dense vectors rank worse than late interaction, so however sharply their scores drop, the rerank
# gets enough candidates to recover a page they ranked low
MIN_RERANK_CANDIDATES = 20
# Enough scores past the ones that matter to tell a drop from a steady decline
LATE_CANDIDATES = 20
# Qwen reads one page per request, and in dev its KV cache holds about one request at a time
MAX_LOCATE_PAGES = 5
SCORE_DROP = Drop(of_spread=0.25, of_best=0.05)
# Dense scores that drop this sharply leave nothing for a rerank to change
DEFINITIVE_DROP = Drop(of_spread=0.6, of_best=0.3)

VLM_MODEL = "vlm"
LOCATE_MAX_TOKENS = 512


class SearchInput(CamelModel):
    user_id: UUID
    bucket: str
    query: str
    document_id: str | None = None


class Box(CamelModel):
    """Corners on a 0–1000 scale relative to the page image, the way Qwen reports them."""

    x1: int
    y1: int
    x2: int
    y2: int


class SearchHit(CamelModel):
    document_id: str
    page_number: int
    score: float
    # None until Qwen has looked at the page. Empty when it found no occurrence, which makes the
    # page related to the query rather than a match for it.
    boxes: list[Box] | None = None

    @property
    def page_key(self) -> tuple[str, int]:
        return self.document_id, self.page_number


type SearchState = Literal["searching", "locating", "done", "failed"]


class SearchEvent(CamelModel):
    state: SearchState
    pages: list[SearchHit] = Field(default_factory=list)


class FindPagesInput(CamelModel):
    user_id: UUID
    document_id: str | None
    query: EncodedQuery


class LocateInput(CamelModel):
    bucket: str
    document_id: str
    page_number: int
    text: str


class Occurrence(BaseModel):
    text: str
    bbox_2d: Annotated[list[int], Field(min_length=4, max_length=4)]


class Occurrences(BaseModel):
    occurrences: list[Occurrence]


def scores(ranked: list[PageMatch]) -> list[float]:
    return [page.score for page in ranked]


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def box(bbox_2d: list[int]) -> Box | None:
    x1, y1, x2, y2 = (min(max(value, 0), 1000) for value in bbox_2d)
    if x1 == x2 or y1 == y2:
        return None
    return Box(x1=min(x1, x2), y1=min(y1, y2), x2=max(x1, x2), y2=max(y1, y2))


def locate_prompt(text: str) -> str:
    return (
        f"Find every place this page shows the text {json.dumps(text)}. For each occurrence, give "
        "the text exactly as printed and its bbox_2d [x1, y1, x2, y2] relative to the image on a "
        "0-1000 scale. If the text does not appear, return no occurrences."
    )


class ExtractActivities:
    def __init__(
        self,
        s3: AsyncS3Client,
        milvus: AsyncMilvusClient,
        vlm: AsyncOpenAI,
        dense_search_min_pages: int,
    ) -> None:
        self.s3 = s3
        self.milvus = milvus
        self.vlm = vlm
        self.dense_search_min_pages = dense_search_min_pages

    async def rank_pages(
        self, options: SearchOptions, query: EncodedQuery
    ) -> list[PageMatch]:
        tokens = np.array(query.tokens, dtype=np.int8)
        page_count = await pages.count_pages(self.milvus, options)
        if page_count < self.dense_search_min_pages:
            activity.logger.info(f"Late-interaction search over {page_count} pages")
            return await pages.late_search(
                self.milvus, options, tokens, limit=LATE_CANDIDATES
            )

        dense = await pages.dense_search(
            self.milvus,
            options,
            np.array(query.dense, dtype=np.float32),
            limit=DENSE_CANDIDATES,
        )
        activity.logger.info(f"Dense scores over {page_count} pages: {scores(dense)}")
        if definitive := cliff(scores(dense), DEFINITIVE_DROP, within=MAX_LOCATE_PAGES):
            return dense[:definitive]
        dense_cliff = cliff(scores(dense), SCORE_DROP, within=len(dense))
        candidates = dense[: max(dense_cliff or len(dense), MIN_RERANK_CANDIDATES)]
        return await pages.late_search(
            self.milvus, options, tokens, limit=len(candidates), candidates=candidates
        )

    @activity.defn
    async def find_pages(self, input: FindPagesInput) -> list[PageMatch]:
        """The pages worth asking Qwen about, best first."""
        options = SearchOptions(
            user_id=str(input.user_id), document_id=input.document_id
        )
        ranked = await self.rank_pages(options, input.query)
        activity.logger.info(f"Ranked scores: {scores(ranked)}")
        located = cliff(scores(ranked), SCORE_DROP, within=MAX_LOCATE_PAGES)
        return ranked[: located or MAX_LOCATE_PAGES]

    async def read_page(self, input: LocateInput) -> bytes:
        key = documents.page_image_key(input.document_id, input.page_number)
        try:
            async with self.s3.get_object(input.bucket, key) as response:
                return b"".join([chunk async for chunk in response["body"]])
        except (NoSuchKey, NoSuchBucket) as error:
            raise document_deleted() from error

    @activity.defn
    async def locate_text(self, input: LocateInput) -> list[Box]:
        """Where the page shows the text. Qwen sometimes reports text that isn't the query, so
        only occurrences whose printed text contains it count."""
        image = base64.b64encode(await self.read_page(input)).decode()
        response = await self.vlm.chat.completions.create(
            model=VLM_MODEL,
            temperature=0,
            max_tokens=LOCATE_MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                        },
                        {"type": "text", "text": locate_prompt(input.text)},
                    ],
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "occurrences",
                    "schema": Occurrences.model_json_schema(),
                    "strict": True,
                },
            },
        )
        found = Occurrences.model_validate_json(
            response.choices[0].message.content or ""
        )
        wanted = normalize(input.text)
        return [
            located
            for occurrence in found.occurrences
            if wanted in normalize(occurrence.text)
            and (located := box(occurrence.bbox_2d)) is not None
        ]
