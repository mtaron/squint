import asyncio
import contextlib
from enum import StrEnum
from itertools import batched
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
from uuid import UUID

import asyncpg
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from capo_s3 import AsyncS3Client
from capo_s3.errors import NoSuchBucket
from capo_s3.types.object_identifier import ObjectIdentifier
from squint_core import documents
from squint_core.documents import DocumentPage, document_deleted
from squint_core.embedding import EMBED_BATCH_SIZE
from squint_core.models import CamelModel
from squint_core.processes import ProcessWorkers
from temporalio import activity
from temporalio.exceptions import ApplicationError

from rasterize import RasterizedPage, rasterize_page

# The UI names this limit in its message for TOO_MANY_PAGES (MAX_PDF_PAGES in upload-limits.ts)
MAX_PDF_PAGES = 2000
# Groups of pages being worked on, which keeps more pages waiting than a pod's processes can take
GROUPS_AT_ONCE = 6
PAGES_STORED_SIGNAL = "pages_stored"


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
    state: Literal[
        "validating", "rasterizing", "embedding", "ingested", "failed", "deleted"
    ]
    page_count: int | None = None
    pages_done: int | None = None
    pages_embedded: int | None = None
    error: IngestError | None = None


class PagesStored(CamelModel):
    """A group of pages that's been recorded, and so is ready to embed."""

    page_count: int
    page_numbers: list[int]


def invalid_document(error: IngestError, detail: str) -> ApplicationError:
    """A failure the user has to fix by uploading a different file, so retrying can't help."""
    return ApplicationError(detail, type=error, non_retryable=True)


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


class PageWorkers(ProcessWorkers):
    """Processes for everything that touches a PDF, since PDFium isn't thread safe. They're the
    only way to render in parallel, and each one holds a PDF open just for the page it's on."""


async def signal_pages_stored(stored: PagesStored) -> None:
    info = activity.info()
    assert info.workflow_id is not None, "rasterize_pdf only runs in a workflow"
    handle = activity.client().get_workflow_handle(
        info.workflow_id, run_id=info.workflow_run_id
    )
    await handle.signal(PAGES_STORED_SIGNAL, stored)


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

    async def store_group(
        self,
        input: IngestInput,
        path: Path,
        page_count: int,
        page_numbers: tuple[int, ...],
    ) -> None:
        """Pages are recorded before the workflow hears about them, since embedding needs their
        rows. If this dies in between, the workflow embeds the group once rasterizing ends."""
        async with asyncio.TaskGroup() as pages:
            stored = [
                pages.create_task(self.rasterize_and_store(input, path, page_number))
                for page_number in page_numbers
            ]
        try:
            await documents.upsert_pages(self.db, [page.result() for page in stored])
        except asyncpg.ForeignKeyViolationError as error:
            raise document_deleted() from error
        await signal_pages_stored(
            PagesStored(page_count=page_count, page_numbers=list(page_numbers))
        )

    async def rasterize_pages(
        self, input: IngestInput, path: Path, page_count: int
    ) -> None:
        """Each group records its pages together, so a retry only has to skip whole groups."""
        recorded = await documents.recorded_pages(self.db, input.document_id)
        groups = batched(range(1, page_count + 1), EMBED_BATCH_SIZE)
        unrecorded = [group for group in groups if group[0] not in recorded]
        for running in batched(unrecorded, GROUPS_AT_ONCE):
            try:
                async with asyncio.TaskGroup() as tasks:
                    for page_numbers in running:
                        tasks.create_task(
                            self.store_group(input, path, page_count, page_numbers)
                        )
            except* ApplicationError as errors:
                # Temporal only sees that a failure is non-retryable outside of a group
                raise errors.exceptions[0] from None

    @activity.defn
    async def rasterize_pdf(self, input: IngestInput) -> int:
        """Validates the PDF, stores an image of each page, and returns the page count. One
        activity does all of it so the PDF is only downloaded once. Tells the workflow as each group
        of pages is ready to embed."""
        with TemporaryDirectory(prefix="ingest-") as directory:
            path = Path(directory) / "document.pdf"
            await download(self.s3, input, path)
            page_count = await self.page_workers.run(count_pages, path)
            if page_count > MAX_PDF_PAGES:
                raise invalid_document(
                    IngestError.TOO_MANY_PAGES,
                    f"{page_count} pages is over the limit of {MAX_PDF_PAGES}",
                )
            await self.rasterize_pages(input, path, page_count)
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
        """Removes what's left of a document that failed ingestion or was deleted during it.
        Deleting a user takes their bucket with it."""
        with contextlib.suppress(NoSuchBucket):
            await delete_objects_under(
                self.s3, input.bucket, documents.document_prefix(input.document_id)
            )
        await documents.delete_document(self.db, input.document_id)
