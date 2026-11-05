import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from squint_core.documents import document_deleted
from squint_core.embedding import EMBED_TASK_QUEUE, EncodedQuery
from squint_vector.pages import PageMatch
from temporalio import activity
from temporalio.client import Client, WorkflowHandle
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.contrib.workflow_streams import WorkflowStreamClient
from temporalio.exceptions import ApplicationError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from test_activities import DOCUMENT_ID, QUERY, USER_ID

from activities import (
    Box,
    FindPagesInput,
    LocateInput,
    SearchEvent,
    SearchHit,
    SearchInput,
)
from workflows import SearchWorkflow

OTHER_DOCUMENT_ID = "Hw7pLc4Rn8"
BOX = Box(x1=100, y1=200, x2=300, y2=220)

INPUT = SearchInput(user_id=USER_ID, bucket=f"squint-u-{USER_ID}", query="net revenue")


@pytest.fixture(scope="session")
async def env():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as env:
        yield env


def match(document_id: str, page_number: int, score: float) -> PageMatch:
    return PageMatch(document_id=document_id, page_number=page_number, score=score)


class FakeActivities:
    def __init__(
        self,
        matches: list[PageMatch],
        boxes: dict[int, list[Box] | Exception] | None = None,
        encode_error: Exception | None = None,
    ) -> None:
        self.matches = matches
        self.boxes = boxes or {}
        self.encode_error = encode_error
        self.queries: list[str] = []
        self.found: list[FindPagesInput] = []

    @activity.defn(name="encode_query")
    async def encode_query(self, query: str) -> EncodedQuery:
        self.queries.append(query)
        if self.encode_error:
            raise self.encode_error
        return QUERY

    @activity.defn(name="find_pages")
    async def find_pages(self, input: FindPagesInput) -> list[PageMatch]:
        self.found.append(input)
        return self.matches

    @activity.defn(name="locate_text")
    async def locate_text(self, input: LocateInput) -> list[Box]:
        boxes = self.boxes.get(input.page_number, [])
        if isinstance(boxes, Exception):
            raise boxes
        return boxes

    @asynccontextmanager
    async def workers(self, client: Client, task_queue: str) -> AsyncGenerator[None]:
        async with (
            Worker(client, task_queue=EMBED_TASK_QUEUE, activities=[self.encode_query]),
            Worker(
                client,
                task_queue=task_queue,
                workflows=[SearchWorkflow],
                activities=[self.find_pages, self.locate_text],
            ),
        ):
            yield


async def read_events(client: Client, workflow_id: str) -> list[SearchEvent]:
    stream = WorkflowStreamClient.create(client, workflow_id)
    events = []
    async for item in stream.topic("search", type=SearchEvent).subscribe():
        events.append(item.data)
        if item.data.state in ("done", "failed"):
            return events
    return events


async def search(
    env: WorkflowEnvironment, fakes: FakeActivities, input: SearchInput = INPUT
) -> tuple[list[SearchEvent], WorkflowHandle]:
    task_queue = f"test-{uuid.uuid4()}"
    async with fakes.workers(env.client, task_queue):
        handle = await env.client.start_workflow(
            SearchWorkflow.run,
            input,
            id=f"search-{uuid.uuid4()}",
            task_queue=task_queue,
        )
        events = await read_events(env.client, handle.id)
        await handle.result()
    return events, handle


async def test_publishes_the_ranked_pages_then_where_each_shows_the_query(
    env: WorkflowEnvironment,
):
    fakes = FakeActivities(
        [match(DOCUMENT_ID, 3, 900.0), match(DOCUMENT_ID, 7, 850.0)],
        boxes={3: [BOX]},
    )

    events, _handle = await search(env, fakes)

    assert fakes.queries == ["net revenue"]
    assert [event.state for event in events][:2] == ["searching", "locating"]
    assert events[1].pages == [
        SearchHit(document_id=DOCUMENT_ID, page_number=3, score=900.0),
        SearchHit(document_id=DOCUMENT_ID, page_number=7, score=850.0),
    ]
    assert events[-1] == SearchEvent(
        state="done",
        pages=[
            SearchHit(document_id=DOCUMENT_ID, page_number=3, score=900.0, boxes=[BOX]),
            SearchHit(document_id=DOCUMENT_ID, page_number=7, score=850.0, boxes=[]),
        ],
    )


async def test_searches_the_document_it_was_given(env: WorkflowEnvironment):
    fakes = FakeActivities([])

    events, _handle = await search(
        env, fakes, INPUT.model_copy(update={"document_id": DOCUMENT_ID})
    )

    assert fakes.found[0].document_id == DOCUMENT_ID
    assert fakes.found[0].query == QUERY
    assert events[-1] == SearchEvent(state="done", pages=[])


async def test_encodes_the_query_ahead_of_queued_pages(env: WorkflowEnvironment):
    fakes = FakeActivities([])

    _events, handle = await search(env, fakes)

    priorities = {
        event.activity_task_scheduled_event_attributes.activity_type.name: (
            event.activity_task_scheduled_event_attributes.priority.priority_key
        )
        async for event in handle.fetch_history_events()
        if event.HasField("activity_task_scheduled_event_attributes")
    }
    assert priorities["encode_query"] == 1


async def test_a_page_qwen_cannot_read_stays_related(env: WorkflowEnvironment):
    fakes = FakeActivities(
        [match(DOCUMENT_ID, 3, 900.0)],
        boxes={3: ApplicationError("vLLM is down", non_retryable=True)},
    )

    events, _handle = await search(env, fakes)

    assert events[-1].pages == [
        SearchHit(document_id=DOCUMENT_ID, page_number=3, score=900.0, boxes=[])
    ]


async def test_drops_the_pages_of_a_deleted_document(env: WorkflowEnvironment):
    fakes = FakeActivities(
        [match(OTHER_DOCUMENT_ID, 1, 900.0), match(DOCUMENT_ID, 2, 850.0)],
        boxes={1: document_deleted(), 2: [BOX]},
    )

    events, _handle = await search(env, fakes)

    assert events[-1].pages == [
        SearchHit(document_id=DOCUMENT_ID, page_number=2, score=850.0, boxes=[BOX])
    ]


async def test_reports_a_search_that_could_not_run(env: WorkflowEnvironment):
    fakes = FakeActivities(
        [], encode_error=ApplicationError("no GPU", non_retryable=True)
    )

    events, _handle = await search(env, fakes)

    assert events[-1] == SearchEvent(state="failed", pages=[])
