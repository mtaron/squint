from enum import StrEnum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
from uuid import UUID

import asyncpg
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c
from capo_s3 import AsyncS3Client, S3Client
from squint_core import documents
from squint_core.models import CamelModel
from temporalio import activity
from temporalio.exceptions import ApplicationError

# The UI names this limit in its message for TOO_MANY_PAGES (MAX_PDF_PAGES in upload-limits.ts)
MAX_PDF_PAGES = 2000


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
    state: Literal["validating", "ingested", "failed"]
    page_count: int | None = None
    error: IngestError | None = None


def invalid_document(error: IngestError, detail: str) -> ApplicationError:
    """A failure the user has to fix by uploading a different file, so retrying can't help."""
    return ApplicationError(detail, type=error, non_retryable=True)


def download(s3: S3Client, input: IngestInput, destination: Path) -> None:
    """Streams the object to disk, so a large PDF is never held in memory."""
    with (
        destination.open("wb") as file,
        s3.get_object(input.bucket, input.key) as response,
    ):
        for chunk in response["body"]:
            file.write(chunk)
            activity.heartbeat()


def count_pages(path: Path) -> int:
    """Opens the PDF by path, so PDFium reads it from disk as needed."""
    try:
        pdf = pdfium.PdfDocument(path)
    except pdfium.PdfiumError as error:
        if error.err_code in (pdfium_c.FPDF_ERR_PASSWORD, pdfium_c.FPDF_ERR_SECURITY):
            raise invalid_document(
                IngestError.PASSWORD_PROTECTED, str(error)
            ) from error
        raise invalid_document(IngestError.DAMAGED, str(error)) from error
    try:
        return len(pdf)
    finally:
        pdf.close()


class PdfActivities:
    """Sync activities that use PDFium. PDFium isn't thread safe, so the worker runs them on a
    single thread, one at a time."""

    def __init__(self, s3: S3Client) -> None:
        self.s3 = s3

    @activity.defn
    def rasterize_pdf(self, input: IngestInput) -> int:
        """Validates the PDF and returns its page count."""
        with TemporaryDirectory(prefix="ingest-") as directory:
            path = Path(directory) / "document.pdf"
            download(self.s3, input, path)
            page_count = count_pages(path)
            if page_count > MAX_PDF_PAGES:
                raise invalid_document(
                    IngestError.TOO_MANY_PAGES,
                    f"{page_count} pages is over the limit of {MAX_PDF_PAGES}",
                )
            # TODO: render each page to an image and hand the pages off for embedding
            return page_count


class DocumentActivities:
    def __init__(self, db: asyncpg.Pool, s3: AsyncS3Client) -> None:
        self.db = db
        self.s3 = s3

    @activity.defn
    async def record_page_count(self, input: IngestInput, page_count: int) -> None:
        await documents.set_page_count(self.db, input.document_id, page_count)

    @activity.defn
    async def discard_document(self, input: IngestInput) -> None:
        """Removes a document that failed ingestion, so it disappears from the user's list."""
        await self.s3.delete_object(input.bucket, input.key)
        await documents.delete_document(self.db, input.document_id)
