"""Uploaded documents, stored in the tables defined in squint/javascript/db."""

from datetime import datetime
from uuid import UUID

import asyncpg
from asyncpg.pool import PoolConnectionProxy
from pydantic import BaseModel, ConfigDict
from temporalio.exceptions import ApplicationError

# Pass a connection rather than the pool to run inside its transaction
type Executor = asyncpg.Pool | asyncpg.Connection | PoolConnectionProxy

# The type of the failure raised when a worker finds that the user deleted its document
DOCUMENT_DELETED = "document_deleted"


def document_deleted() -> ApplicationError:
    return ApplicationError(
        "The document was deleted", type=DOCUMENT_DELETED, non_retryable=True
    )


def document_prefix(document_id: str) -> str:
    """Every object belonging to a document starts with this. Mirrors squint/javascript/db/src/storage.ts."""
    return f"documents/{document_id}/"


def page_image_key(document_id: str, page_number: int) -> str:
    return f"{document_prefix(document_id)}pages/{page_number}.jpg"


def thumbnail_key(document_id: str, page_number: int) -> str:
    return f"{document_prefix(document_id)}thumbnails/{page_number}.webp"


class Document(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    user_id: UUID
    name: str
    sha256: str
    size_bytes: int
    page_count: int | None
    uploaded_at: datetime


class DocumentPage(BaseModel):
    """What ingestion learned about a page. Pixel values are relative to its image in S3."""

    model_config = ConfigDict(frozen=True)

    document_id: str
    page_number: int
    width: int
    height: int
    is_scan: bool
    skew_degrees: float | None
    content_box: list[int] | None
    embedded_at: datetime | None = None


class NewDocument(BaseModel):
    id: str
    user_id: UUID
    name: str
    sha256: str
    size_bytes: int
    page_count: int | None = None


async def create_document(db: Executor, new: NewDocument) -> Document:
    row = await db.fetchrow(
        """
        insert into document (id, user_id, name, sha256, size_bytes, page_count)
        values ($1, $2, $3, $4, $5, $6)
        returning *
        """,
        new.id,
        new.user_id,
        new.name,
        new.sha256,
        new.size_bytes,
        new.page_count,
    )
    return Document.model_validate(dict(row))


async def get_document(db: Executor, id: str) -> Document | None:
    row = await db.fetchrow("select * from document where id = $1", id)
    return Document.model_validate(dict(row)) if row else None


async def find_document_by_sha256(
    db: Executor, user_id: UUID, sha256: str
) -> Document | None:
    """The user's earlier upload of the same file, if any."""
    row = await db.fetchrow(
        "select * from document where user_id = $1 and sha256 = $2", user_id, sha256
    )
    return Document.model_validate(dict(row)) if row else None


async def list_documents(db: Executor, user_id: UUID, *, limit: int) -> list[Document]:
    """The user's most recent uploads first."""
    rows = await db.fetch(
        """
        select * from document
        where user_id = $1
        order by uploaded_at desc
        limit $2
        """,
        user_id,
        limit,
    )
    return [Document.model_validate(dict(row)) for row in rows]


async def set_page_count(db: Executor, id: str, page_count: int) -> Document | None:
    row = await db.fetchrow(
        "update document set page_count = $2 where id = $1 returning *", id, page_count
    )
    return Document.model_validate(dict(row)) if row else None


async def delete_document(db: Executor, id: str) -> bool:
    """Whether a document was deleted."""
    status = await db.execute("delete from document where id = $1", id)
    return status == "DELETE 1"


async def upsert_pages(db: Executor, pages: list[DocumentPage]) -> None:
    await db.executemany(
        """
        insert into document_page
            (document_id, page_number, width, height, is_scan, skew_degrees, content_box)
        values ($1, $2, $3, $4, $5, $6, $7)
        on conflict (document_id, page_number) do update set
            width = excluded.width,
            height = excluded.height,
            is_scan = excluded.is_scan,
            skew_degrees = excluded.skew_degrees,
            content_box = excluded.content_box
        """,
        [
            (
                page.document_id,
                page.page_number,
                page.width,
                page.height,
                page.is_scan,
                page.skew_degrees,
                page.content_box,
            )
            for page in pages
        ],
    )


async def recorded_pages(db: Executor, document_id: str) -> set[int]:
    """The numbers of the document's recorded pages, which may be recorded out of order."""
    rows = await db.fetch(
        "select page_number from document_page where document_id = $1", document_id
    )
    return {row["page_number"] for row in rows}


async def content_boxes(
    db: Executor, document_id: str, page_numbers: list[int]
) -> dict[int, list[int] | None]:
    """Each recorded page's content box, by page number."""
    rows = await db.fetch(
        """
        select page_number, content_box from document_page
        where document_id = $1 and page_number = any($2)
        """,
        document_id,
        page_numbers,
    )
    return {row["page_number"]: row["content_box"] for row in rows}


async def mark_pages_embedded(
    db: Executor, document_id: str, page_numbers: list[int]
) -> int:
    """How many pages were marked, which is none once the document has been deleted."""
    status = await db.execute(
        """
        update document_page set embedded_at = now()
        where document_id = $1 and page_number = any($2)
        """,
        document_id,
        page_numbers,
    )
    return int(status.removeprefix("UPDATE "))
