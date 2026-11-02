import asyncio
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from enum import StrEnum
from itertools import batched
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal, Self
from uuid import UUID

import asyncpg
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from capo_s3 import AsyncS3Client
from capo_s3.types.object_identifier import ObjectIdentifier
from squint_core import documents
from squint_core.documents import DocumentPage
from squint_core.models import CamelModel
from temporalio import activity
from temporalio.contrib.workflow_streams import TopicHandle, WorkflowStreamClient
from temporalio.exceptions import ApplicationError

from rasterize import RasterizedPage, rasterize_page

# The UI names this limit in its message for TOO_MANY_PAGES (MAX_PDF_PAGES in upload-limits.ts)
MAX_PDF_PAGES = 2000
# A retry resumes from the last recorded page, and progress is reported as pages are recorded
PAGES_PER_RECORD = 25
# The type of the failure raised when ingestion finds that the user deleted its document
DOCUMENT_DELETED = "document_deleted"


class IngestError(StrEnum):
    """Why ingestion failed. The UI turns each one into a message for the user."""

    PASSWORD_PROTECTED = "password_protected"
    DAMAGED = "damaged"
    TOO_MANY_PAGES = "too_many_pages"
    UNEXPECTED = "unexpected"


class IngestInput(CamelModel):
    document_id: str
    user_id: UUID
    bucket: str
    key: str


class IngestEvent(CamelModel):
    state: Literal["validating", "rasterizing", "ingested", "failed", "deleted"]
    page_count: int | None = None
    pages_done: int | None = None
    error: IngestError | None = None


def invalid_document(error: IngestError, detail: str) -> ApplicationError:
    """A failure the user has to fix by uploading a different file, so retrying can't help."""
    return ApplicationError(detail, type=error, non_retryable=True)


def document_deleted() -> ApplicationError:
    return ApplicationError(
        "The document was deleted", type=DOCUMENT_DELETED, non_retryable=True
    )


async def download(s3: AsyncS3Client, input: IngestInput, destination: Path) -> None:
    """Streams the object to disk, so a large PDF is never held in memory."""
    with destination.open("wb") as file:
        async with s3.get_object(input.bucket, input.key) as response:
            async for chunk in response["body"]:
                file.write(chunk)
                activity.heartbeat()


def open_pdf(path: Path) -> pdfium.PdfDocument:
    """Opens the PDF by path, so PDFium reads it from disk as needed."""
    try:
        pdf = pdfium.PdfDocument(path)
    except pdfium.PdfiumError as error:
        if error.err_code in (pdfium_c.FPDF_ERR_PASSWORD, pdfium_c.FPDF_ERR_SECURITY):
            raise invalid_document(
                IngestError.PASSWORD_PROTECTED, str(error)
            ) from error
        raise invalid_document(IngestError.DAMAGED, str(error)) from error
    pdf.init_forms()
    return pdf


def count_pages(path: Path) -> int:
    with open_pdf(path) as pdf:
        return len(pdf)


def rasterize_page_number(path: Path, page_number: int) -> RasterizedPage:
    with open_pdf(path) as pdf:
        page = pdf[page_number - 1]
        try:
            return rasterize_page(page)
        finally:
            page.close()


class PageWorkers:
    """Processes for everything that touches a PDF, since PDFium isn't thread safe. They're the
    only way to render in parallel, and each one holds a PDF open just for the page it's on."""

    def __init__(self, size: int) -> None:
        self.size = size
        self.pool = self.create_pool()

    def create_pool(self) -> ProcessPoolExecutor:
        return ProcessPoolExecutor(self.size)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exception: object) -> None:
        self.pool.shutdown()

    async def run[T](self, function: Callable[..., T], *args: object) -> T:
        pool = self.pool
        try:
            return await asyncio.get_running_loop().run_in_executor(
                pool, function, *args
            )
        except BrokenProcessPool:
            # One process dying breaks the pool for good, and retries on it would use up the
            # attempts of every document on this pod
            if pool is self.pool:
                self.pool = self.create_pool()
            raise


async def delete_objects_under(s3: AsyncS3Client, bucket: str, prefix: str) -> None:
    async for listing in s3.iter_list_objects_v2(bucket, prefix=prefix):
        objects: list[ObjectIdentifier] = [
            {"key": object["key"]} for object in listing.get("contents", [])
        ]
        if objects:
            output = await s3.delete_objects(
                bucket, {"objects": objects, "quiet": True}
            )
            if errors := output.get("errors"):
                raise RuntimeError(f"Failed to delete from {bucket}: {errors}")
        activity.heartbeat()


class DocumentActivities:
    def __init__(
        self, db: asyncpg.Pool, s3: AsyncS3Client, page_workers: PageWorkers
    ) -> None:
        self.db = db
        self.s3 = s3
        self.page_workers = page_workers

    async def store_page(
        self, input: IngestInput, page_number: int, page: RasterizedPage
    ) -> None:
        await asyncio.gather(
            self.s3.put_object(
                input.bucket,
                documents.page_image_key(input.document_id, page_number),
                body=page.image,
                content_type="image/jpeg",
            ),
            self.s3.put_object(
                input.bucket,
                documents.thumbnail_key(input.document_id, page_number),
                body=page.thumbnail,
                content_type="image/webp",
            ),
        )

    async def rasterize_and_store(
        self, input: IngestInput, path: Path, page_number: int
    ) -> DocumentPage:
        page = await self.page_workers.run(rasterize_page_number, path, page_number)
        await self.store_page(input, page_number, page)
        activity.heartbeat()
        return DocumentPage(
            document_id=input.document_id,
            page_number=page_number,
            width=page.width,
            height=page.height,
            is_scan=page.is_scan,
            skew_degrees=page.skew_degrees,
            content_box=page.content_box,
        )

    async def rasterize_pages(
        self,
        input: IngestInput,
        path: Path,
        page_count: int,
        status: TopicHandle[IngestEvent],
    ) -> None:
        def report_progress(pages_done: int) -> None:
            status.publish(
                IngestEvent(
                    state="rasterizing", page_count=page_count, pages_done=pages_done
                )
            )

        recorded = await documents.pages_recorded(self.db, input.document_id)
        report_progress(recorded)
        unrecorded = range(recorded + 1, page_count + 1)
        for page_numbers in batched(unrecorded, PAGES_PER_RECORD):
            async with asyncio.TaskGroup() as pages:
                stored = [
                    pages.create_task(
                        self.rasterize_and_store(input, path, page_number)
                    )
                    for page_number in page_numbers
                ]
            try:
                await documents.upsert_pages(
                    self.db, [page.result() for page in stored]
                )
            except asyncpg.ForeignKeyViolationError as error:
                raise document_deleted() from error
            report_progress(page_numbers[-1])

    @activity.defn
    async def rasterize_pdf(self, input: IngestInput) -> int:
        """Validates the PDF, stores an image of each page, and returns the page count. One
        activity does all of it so the PDF is only downloaded once."""
        with TemporaryDirectory(prefix="ingest-") as directory:
            path = Path(directory) / "document.pdf"
            await download(self.s3, input, path)
            page_count = await self.page_workers.run(count_pages, path)
            if page_count > MAX_PDF_PAGES:
                raise invalid_document(
                    IngestError.TOO_MANY_PAGES,
                    f"{page_count} pages is over the limit of {MAX_PDF_PAGES}",
                )
            async with WorkflowStreamClient.from_within_activity() as stream:
                status = stream.topic("status", type=IngestEvent)
                await self.rasterize_pages(input, path, page_count, status)
            return page_count

    @activity.defn
    async def record_page_count(self, input: IngestInput, page_count: int) -> None:
        if (
            await documents.set_page_count(self.db, input.document_id, page_count)
            is None
        ):
            raise document_deleted()

    @activity.defn
    async def discard_document(self, input: IngestInput) -> None:
        """Removes what's left of a document that failed ingestion or was deleted during it."""
        await delete_objects_under(
            self.s3, input.bucket, documents.document_prefix(input.document_id)
        )
        await documents.delete_document(self.db, input.document_id)
