import asyncio
import tempfile
import threading
from datetime import timedelta
from functools import cache
from pathlib import Path

import asyncpg
import pypdfium2 as pdfium
from capo_s3 import AsyncS3Client
from library import STATUS_TOPIC, library_workflow_id
from limits import MAX_PDF_PAGES
from squint_core import postgres, s3
from temporalio import activity
from temporalio.contrib.workflow_streams import WorkflowStreamClient
from temporalio.exceptions import ApplicationError

from models import (
    DocumentResult,
    DocumentStatusEvent,
    IngestDocumentInput,
    IngestError,
    PdfInfo,
)

# PDFium is not thread-safe
pdfium_lock = threading.Lock()
postgres_pool_lock = asyncio.Lock()
postgres_pool: asyncpg.Pool | None = None


@cache
def s3_client() -> AsyncS3Client:
    return s3.create_client()


async def get_postgres_pool() -> asyncpg.Pool:
    global postgres_pool
    async with postgres_pool_lock:
        if postgres_pool is None:
            postgres_pool = await postgres.create_client()
    return postgres_pool


def document_error(code: IngestError, message: str) -> ApplicationError:
    return ApplicationError(message, type=code.value, non_retryable=True)


def open_error(error: pdfium.PdfiumError) -> ApplicationError:
    match error.err_code:
        case pdfium.raw.FPDF_ERR_PASSWORD:
            return document_error(
                IngestError.PASSWORD_PROTECTED, "The PDF requires a password to open"
            )
        case pdfium.raw.FPDF_ERR_SECURITY:
            return document_error(
                IngestError.UNSUPPORTED_SECURITY,
                "The PDF uses an unsupported security handler",
            )
        case _:
            return document_error(IngestError.UNREADABLE, str(error))


def count_pages(path: Path) -> int:
    with pdfium_lock:
        try:
            pdf = pdfium.PdfDocument(path)
        except pdfium.PdfiumError as error:
            raise open_error(error) from error
        try:
            page_count = len(pdf)
        finally:
            pdf.close()
    if page_count > MAX_PDF_PAGES:
        raise document_error(
            IngestError.TOO_MANY_PAGES,
            f"The PDF has {page_count} pages; the limit is {MAX_PDF_PAGES}",
        )
    return page_count


async def download(bucket: str, key: str, destination) -> None:
    async with s3_client().get_object(bucket=bucket, key=key) as output:
        async for chunk in output["body"]:
            destination.write(chunk)
    destination.flush()


@activity.defn
async def rasterize_pdf(input: IngestDocumentInput) -> PdfInfo:
    # PDFium seeks to the cross-reference table at the end of the file, so it reads from disk
    # rather than the response stream
    with tempfile.NamedTemporaryFile(suffix=".pdf") as file:
        await download(input.bucket, input.key, file)
        page_count = await asyncio.to_thread(count_pages, Path(file.name))
        # Next: render each page and a thumbnail for the web app
    return PdfInfo(page_count=page_count)


async def publish_status(result: DocumentResult) -> None:
    stream = WorkflowStreamClient.create(
        activity.client(),
        library_workflow_id(result.user_id),
        max_retry_duration=timedelta(seconds=10),
    )
    event = DocumentStatusEvent(
        document_id=result.document_id,
        upload_id=result.upload_id,
        status=result.status,
        page_count=result.page_count,
        error_code=result.error_code,
        error_detail=result.error_detail,
    )
    async with stream:
        stream.topic(STATUS_TOPIC, type=DocumentStatusEvent).publish(
            event, force_flush=True
        )


@activity.defn
async def record_result(result: DocumentResult) -> None:
    pool = await get_postgres_pool()
    status = await pool.execute(
        """
        UPDATE document
        SET status = $3, page_count = $4, error_code = $5, error_detail = $6, updated_at = now()
        WHERE id = $1 AND upload_id = $2
        """,
        result.document_id,
        result.upload_id,
        result.status.value,
        result.page_count,
        result.error_code.value if result.error_code else None,
        result.error_detail,
    )
    # The document was deleted or replaced while this upload was ingesting
    if status == "UPDATE 0":
        return
    # The list reloads from Postgres when it reconnects, so a missed event only delays an update
    try:
        await publish_status(result)
    except Exception:  # noqa: BLE001
        activity.logger.warning(
            "could not publish the status of document %s",
            result.document_id,
            exc_info=True,
        )
