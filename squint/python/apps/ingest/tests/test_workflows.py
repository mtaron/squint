import uuid
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

import pytest
from squint_core.documents import DOCUMENT_DELETED
from squint_core.embedding import EMBED_TASK_QUEUE, EmbedPagesInput
from temporalio import activity
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.contrib.workflow_streams import WorkflowStreamClient
from temporalio.exceptions import ApplicationError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from test_activities import FIXTURES, INPUT, FakeDb, FakeS3

from activities import (
    DocumentActivities,
    IngestError,
    IngestEvent,
    IngestInput,
    PagesStored,
    PageWorkers,
    signal_pages_stored,
)
from workflows import IngestDocumentWorkflow


@pytest.fixture(scope="session")
async def env():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as env:
        yield env


class FakeActivities:
    def __init__(
        self,
        page_count: int = 3,
        rasterize_error: Exception | None = None,
        record_error: Exception | None = None,
        embed_error: Callable[[list[int]], Exception | None] = lambda _pages: None,
        signals: tuple[PagesStored, ...] = (),
    ) -> None:
        self.page_count = page_count
        self.rasterize_error = rasterize_error
        self.record_error = record_error
        self.embed_error = embed_error
        self.signals = signals
        self.calls: list[str] = []
        self.embedded: list[list[int]] = []

    @activity.defn(name="rasterize_pdf")
    async def rasterize_pdf(self, input: IngestInput) -> int:
        self.calls.append("rasterize_pdf")
        for stored in self.signals:
            await signal_pages_stored(stored)
        if self.rasterize_error:
            raise self.rasterize_error
        return self.page_count

    @activity.defn(name="record_page_count")
    async def record_page_count(self, input: IngestInput, page_count: int) -> None:
        self.calls.append(f"record_page_count {page_count}")
        if self.record_error:
            raise self.record_error

    @activity.defn(name="discard_document")
    async def discard_document(self, input: IngestInput) -> None:
        self.calls.append("discard_document")

    @activity.defn(name="embed_pages")
    async def embed_pages(self, input: EmbedPagesInput) -> None:
        self.embedded.append(input.page_numbers)
        if error := self.embed_error(input.page_numbers):
            raise error

    @activity.defn(name="deleteDocumentVectors")
    async def delete_document_vectors(self, document_ids: list[str]) -> None:
        self.calls.append(f"deleteDocumentVectors {document_ids}")

    @asynccontextmanager
    async def embed_worker(self, client: Client) -> AsyncGenerator[None]:
        async with Worker(
            client,
            task_queue=EMBED_TASK_QUEUE,
            activities=[self.embed_pages, self.delete_document_vectors],
        ):
            yield


async def read_status(client: Client, workflow_id: str) -> list[IngestEvent]:
    stream = WorkflowStreamClient.create(client, workflow_id)
    events = []
    async for item in stream.topic("status", type=IngestEvent).subscribe():
        events.append(item.data)
        if item.data.state in ("ingested", "failed", "deleted"):
            return events
    return events


async def ingest(env: WorkflowEnvironment, fakes: FakeActivities) -> list[IngestEvent]:
    task_queue = f"test-{uuid.uuid4()}"
    async with (
        fakes.embed_worker(env.client),
        Worker(
            env.client,
            task_queue=task_queue,
            workflows=[IngestDocumentWorkflow],
            activities=[
                fakes.rasterize_pdf,
                fakes.record_page_count,
                fakes.discard_document,
            ],
        ),
    ):
        handle = await env.client.start_workflow(
            IngestDocumentWorkflow.run,
            INPUT,
            id=f"ingest-{uuid.uuid4()}",
            task_queue=task_queue,
        )
        events = await read_status(env.client, handle.id)
        await handle.result()
    return events


def stored(page_count: int, *page_numbers: int) -> PagesStored:
    return PagesStored(page_count=page_count, page_numbers=list(page_numbers))


async def test_records_the_page_count_and_embeds_the_pages(env: WorkflowEnvironment):
    fakes = FakeActivities()

    events = await ingest(env, fakes)

    assert fakes.calls == ["rasterize_pdf", "record_page_count 3"]
    assert fakes.embedded == [[1, 2, 3]]
    assert events == [
        IngestEvent(state="validating", pages_done=0, pages_embedded=0),
        IngestEvent(state="embedding", page_count=3, pages_done=3, pages_embedded=0),
        IngestEvent(state="embedding", page_count=3, pages_done=3, pages_embedded=3),
        IngestEvent(state="ingested", page_count=3, pages_done=3, pages_embedded=3),
    ]


async def test_progress_carries_both_counts_while_rasterizing(env: WorkflowEnvironment):
    fakes = FakeActivities(
        page_count=6, signals=(stored(6, 1, 2, 3, 4), stored(6, 5, 6))
    )

    events = await ingest(env, fakes)

    rasterizing = [event for event in events if event.state == "rasterizing"]
    assert [event.pages_done for event in rasterizing][:2] == [4, 6]
    assert {event.page_count for event in rasterizing} == {6}
    assert events[-1].pages_embedded == 6


async def test_long_documents_only_publish_as_progress_moves_a_percent(
    env: WorkflowEnvironment,
):
    fakes = FakeActivities(page_count=1000)

    events = await ingest(env, fakes)

    embedding = [event for event in events if event.state == "embedding"]
    assert len(embedding) <= 101
    assert events[-1].pages_embedded == 1000


async def test_embeds_a_group_once_when_a_retry_repeats_its_signal(
    env: WorkflowEnvironment,
):
    fakes = FakeActivities(
        page_count=4, signals=(stored(4, 1, 2, 3, 4), stored(4, 1, 2, 3, 4))
    )

    events = await ingest(env, fakes)

    assert fakes.embedded == [[1, 2, 3, 4]]
    assert events[-1].pages_embedded == 4


async def test_embeds_groups_whose_signal_was_lost(env: WorkflowEnvironment):
    fakes = FakeActivities(page_count=10, signals=(stored(10, 1, 2, 3, 4),))

    events = await ingest(env, fakes)

    assert sorted(fakes.embedded) == [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]
    assert events[-1].pages_embedded == 10


async def test_a_batch_that_keeps_failing_does_not_fail_the_document(
    env: WorkflowEnvironment,
):
    fakes = FakeActivities(
        page_count=8,
        embed_error=lambda pages: (
            ApplicationError("GPU", non_retryable=True) if pages[0] == 5 else None
        ),
    )

    events = await ingest(env, fakes)

    assert "discard_document" not in fakes.calls
    assert events[-1] == IngestEvent(
        state="ingested", page_count=8, pages_done=8, pages_embedded=4
    )


async def test_cleans_up_a_document_deleted_while_embedding(env: WorkflowEnvironment):
    deleted = ApplicationError("gone", type=DOCUMENT_DELETED, non_retryable=True)
    fakes = FakeActivities(page_count=8, embed_error=lambda _pages: deleted)

    events = await ingest(env, fakes)

    assert fakes.calls[-2:] == [
        "discard_document",
        f"deleteDocumentVectors {[INPUT.document_id]}",
    ]
    assert events[-1] == IngestEvent(state="deleted")


async def test_progress_from_the_activity_arrives_before_the_final_event(
    env: WorkflowEnvironment,
):
    task_queue = f"test-{uuid.uuid4()}"
    db = FakeDb()
    fakes = FakeActivities()
    with PageWorkers(1) as page_workers:
        activities = DocumentActivities(
            db,  # ty: ignore[invalid-argument-type]
            FakeS3(FIXTURES / "three-pages.pdf"),  # ty: ignore[invalid-argument-type]
            page_workers,
        )

        async def record_page_count(_input: IngestInput, _page_count: int) -> None:
            pass

        record_page_count = activity.defn(name="record_page_count")(record_page_count)

        async with (
            fakes.embed_worker(env.client),
            Worker(
                env.client,
                task_queue=task_queue,
                workflows=[IngestDocumentWorkflow],
                activities=[
                    activities.rasterize_pdf,
                    record_page_count,
                    activities.discard_document,
                ],
            ),
        ):
            handle = await env.client.start_workflow(
                IngestDocumentWorkflow.run,
                INPUT,
                id=f"ingest-{uuid.uuid4()}",
                task_queue=task_queue,
            )
            events = await read_status(env.client, handle.id)
            await handle.result()

    states = [event.state for event in events]
    assert states[0] == "validating"
    assert "rasterizing" in states
    assert states[-1] == "ingested"
    assert fakes.embedded == [[1, 2, 3]]


async def test_discards_invalid_documents(env: WorkflowEnvironment):
    fakes = FakeActivities(
        rasterize_error=ApplicationError(
            "password required",
            type=IngestError.PASSWORD_PROTECTED,
            non_retryable=True,
        )
    )

    events = await ingest(env, fakes)

    assert fakes.calls == [
        "rasterize_pdf",
        "discard_document",
        f"deleteDocumentVectors {[INPUT.document_id]}",
    ]
    assert events[-1] == IngestEvent(
        state="failed", error=IngestError.PASSWORD_PROTECTED
    )


async def test_clears_the_vectors_of_pages_embedded_before_rasterizing_failed(
    env: WorkflowEnvironment,
):
    fakes = FakeActivities(
        page_count=8,
        signals=(stored(8, 1, 2, 3, 4),),
        rasterize_error=ApplicationError("too big", non_retryable=True),
    )

    events = await ingest(env, fakes)

    assert fakes.calls[-1] == f"deleteDocumentVectors {[INPUT.document_id]}"
    assert events[-1] == IngestEvent(state="failed", error=IngestError.UNEXPECTED)


async def test_reports_unexpected_errors_without_details(env: WorkflowEnvironment):
    fakes = FakeActivities(
        rasterize_error=ApplicationError("S3 is down", non_retryable=True)
    )

    events = await ingest(env, fakes)

    assert fakes.calls[:2] == ["rasterize_pdf", "discard_document"]
    assert events[-1] == IngestEvent(state="failed", error=IngestError.UNEXPECTED)


async def test_cleans_up_a_document_deleted_while_rasterizing(env: WorkflowEnvironment):
    fakes = FakeActivities(
        rasterize_error=ApplicationError(
            "gone", type=DOCUMENT_DELETED, non_retryable=True
        )
    )

    events = await ingest(env, fakes)

    assert fakes.calls[:2] == ["rasterize_pdf", "discard_document"]
    assert events[-1] == IngestEvent(state="deleted")


async def test_cleans_up_a_document_deleted_before_its_page_count_is_recorded(
    env: WorkflowEnvironment,
):
    fakes = FakeActivities(
        record_error=ApplicationError("gone", type=DOCUMENT_DELETED, non_retryable=True)
    )

    events = await ingest(env, fakes)

    assert fakes.calls[:3] == [
        "rasterize_pdf",
        "record_page_count 3",
        "discard_document",
    ]
    assert events[-1] == IngestEvent(state="deleted")


async def test_publishes_error_codes_for_the_ui(env: WorkflowEnvironment):
    fakes = FakeActivities(
        rasterize_error=ApplicationError(
            "too big", type=IngestError.TOO_MANY_PAGES, non_retryable=True
        )
    )

    async with (
        fakes.embed_worker(env.client),
        Worker(
            env.client,
            task_queue="test-wire",
            workflows=[IngestDocumentWorkflow],
            activities=[
                fakes.rasterize_pdf,
                fakes.record_page_count,
                fakes.discard_document,
            ],
        ),
    ):
        handle = await env.client.start_workflow(
            IngestDocumentWorkflow.run,
            INPUT,
            id=f"ingest-{uuid.uuid4()}",
            task_queue="test-wire",
        )
        stream = WorkflowStreamClient.create(env.client, handle.id)
        raw = []
        async for item in stream.subscribe("status"):
            raw.append(item.data)
            if item.data["state"] == "failed":
                break
        await handle.result()

    assert raw[-1] == {
        "state": "failed",
        "pageCount": None,
        "pagesDone": None,
        "pagesEmbedded": None,
        "error": "too_many_pages",
    }
