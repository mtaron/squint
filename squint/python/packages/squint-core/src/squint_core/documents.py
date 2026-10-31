"""Uploaded documents, stored in the `document` table defined in squint/javascript/db."""

from datetime import datetime
from uuid import UUID

import asyncpg
from asyncpg.pool import PoolConnectionProxy
from pydantic import BaseModel, ConfigDict

# Pass a connection rather than the pool to run inside its transaction
type Executor = asyncpg.Pool | asyncpg.Connection | PoolConnectionProxy


class Document(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    user_id: UUID
    name: str
    sha256: str
    size_bytes: int
    page_count: int | None
    uploaded_at: datetime


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
