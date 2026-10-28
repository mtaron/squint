import uuid

import pytest
from document import IngestDocumentWorkflow
from temporalio import activity
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.exceptions import ApplicationError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from models import (
    DocumentResult,
    DocumentStatus,
    IngestDocumentInput,
    IngestError,
    PdfInfo,
)

INPUT = IngestDocumentInput(
    document_id="doc", upload_id="upload", user_id="user", bucket="b", key="k"
)


@pytest.fixture(scope="module")
async def env():
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as env:
        yield env


async def run(env: WorkflowEnvironment, rasterize) -> tuple[DocumentResult, list]:
    recorded: list[DocumentResult] = []

    @activity.defn(name="record_result")
    async def record_result(result: DocumentResult) -> None:
        recorded.append(result)

    task_queue = str(uuid.uuid4())
    async with Worker(
        env.client,
        task_queue=task_queue,
        workflows=[IngestDocumentWorkflow],
        activities=[rasterize, record_result],
    ):
        result = await env.client.execute_workflow(
            IngestDocumentWorkflow.run,
            INPUT,
            id=str(uuid.uuid4()),
            task_queue=task_queue,
        )
    return result, recorded


async def test_records_page_count(env: WorkflowEnvironment):
    @activity.defn(name="rasterize_pdf")
    async def rasterize_pdf(input: IngestDocumentInput) -> PdfInfo:
        return PdfInfo(page_count=12)

    result, recorded = await run(env, rasterize_pdf)
    assert result.status == DocumentStatus.READY
    assert result.page_count == 12
    assert recorded == [result]


async def test_records_document_error_without_retrying(env: WorkflowEnvironment):
    attempts = 0

    @activity.defn(name="rasterize_pdf")
    async def rasterize_pdf(input: IngestDocumentInput) -> PdfInfo:
        nonlocal attempts
        attempts += 1
        raise ApplicationError(
            "needs a password",
            type=IngestError.PASSWORD_PROTECTED.value,
            non_retryable=True,
        )

    result, recorded = await run(env, rasterize_pdf)
    assert attempts == 1
    assert result.status == DocumentStatus.FAILED
    assert result.error_code == IngestError.PASSWORD_PROTECTED
    assert result.error_detail == "needs a password"
    assert recorded == [result]


async def test_records_internal_error_after_retries(env: WorkflowEnvironment):
    attempts = 0

    @activity.defn(name="rasterize_pdf")
    async def rasterize_pdf(input: IngestDocumentInput) -> PdfInfo:
        nonlocal attempts
        attempts += 1
        raise RuntimeError("storage unavailable")

    result, recorded = await run(env, rasterize_pdf)
    assert attempts == 5
    assert result.error_code == IngestError.INTERNAL
    assert recorded == [result]
