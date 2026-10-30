import uuid

import pytest
from temporalio import activity
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.contrib.workflow_streams import WorkflowStreamClient
from temporalio.exceptions import ApplicationError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from test_activities import INPUT

from activities import IngestError, IngestEvent, IngestInput
from workflows import IngestDocumentWorkflow


@pytest.fixture(scope="session")
async def env():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as env:
        yield env


class FakeActivities:
    def __init__(self, rasterize_error: Exception | None = None) -> None:
        self.rasterize_error = rasterize_error
        self.calls: list[str] = []

    @activity.defn(name="rasterize_pdf")
    async def rasterize_pdf(self, input: IngestInput) -> int:
        self.calls.append("rasterize_pdf")
        if self.rasterize_error:
            raise self.rasterize_error
        return 3

    @activity.defn(name="record_page_count")
    async def record_page_count(self, input: IngestInput, page_count: int) -> None:
        self.calls.append(f"record_page_count {page_count}")

    @activity.defn(name="discard_document")
    async def discard_document(self, input: IngestInput) -> None:
        self.calls.append("discard_document")


async def read_status(client: Client, workflow_id: str) -> list[IngestEvent]:
    stream = WorkflowStreamClient.create(client, workflow_id)
    events = []
    async for item in stream.topic("status", type=IngestEvent).subscribe():
        events.append(item.data)
        if item.data.state != "validating":
            return events
    return events


async def ingest(env: WorkflowEnvironment, fakes: FakeActivities) -> list[IngestEvent]:
    task_queue = f"test-{uuid.uuid4()}"
    async with Worker(
        env.client,
        task_queue=task_queue,
        workflows=[IngestDocumentWorkflow],
        activities=[
            fakes.rasterize_pdf,
            fakes.record_page_count,
            fakes.discard_document,
        ],
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


async def test_records_the_page_count(env: WorkflowEnvironment):
    fakes = FakeActivities()

    events = await ingest(env, fakes)

    assert fakes.calls == ["rasterize_pdf", "record_page_count 3"]
    assert events == [
        IngestEvent(state="validating"),
        IngestEvent(state="ingested", page_count=3),
    ]


async def test_discards_invalid_documents(env: WorkflowEnvironment):
    fakes = FakeActivities(
        ApplicationError(
            "password required",
            type=IngestError.PASSWORD_PROTECTED,
            non_retryable=True,
        )
    )

    events = await ingest(env, fakes)

    assert fakes.calls == ["rasterize_pdf", "discard_document"]
    assert events[-1] == IngestEvent(
        state="failed", error=IngestError.PASSWORD_PROTECTED
    )


async def test_reports_unexpected_errors_without_details(env: WorkflowEnvironment):
    fakes = FakeActivities(ApplicationError("S3 is down", non_retryable=True))

    events = await ingest(env, fakes)

    assert fakes.calls == ["rasterize_pdf", "discard_document"]
    assert events[-1] == IngestEvent(state="failed", error=IngestError.UNEXPECTED)


async def test_publishes_error_codes_for_the_ui(env: WorkflowEnvironment):
    fakes = FakeActivities(
        ApplicationError("too big", type=IngestError.TOO_MANY_PAGES, non_retryable=True)
    )

    async with Worker(
        env.client,
        task_queue="test-wire",
        workflows=[IngestDocumentWorkflow],
        activities=[
            fakes.rasterize_pdf,
            fakes.record_page_count,
            fakes.discard_document,
        ],
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
            if item.data["state"] != "validating":
                break
        await handle.result()

    assert raw[-1] == {"state": "failed", "pageCount": None, "error": "too_many_pages"}
