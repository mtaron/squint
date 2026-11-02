import asyncio
import os
from collections.abc import AsyncIterator, Iterator
from concurrent.futures.process import BrokenProcessPool
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Self
from uuid import UUID

import asyncpg
import pytest
from temporalio.exceptions import ApplicationError
from temporalio.testing import ActivityEnvironment

import activities
from activities import (
    DOCUMENT_DELETED,
    DocumentActivities,
    IngestError,
    IngestEvent,
    IngestInput,
    PageWorkers,
)

FIXTURES = Path(__file__).parent / "fixtures"
DOCUMENT_ID = "V3kQ9xTz2m"
PDF_KEY = f"documents/{DOCUMENT_ID}/original.pdf"

INPUT = IngestInput(
    document_id=DOCUMENT_ID,
    user_id=UUID("0f8fad5b-d9cb-469f-a165-70867728950e"),
    bucket="squint-u-0f8fad5b-d9cb-469f-a165-70867728950e",
    key=PDF_KEY,
)


class FakeS3:
    """A bucket in memory, holding the uploaded PDF."""

    def __init__(self, pdf: Path) -> None:
        self.objects = {PDF_KEY: pdf.read_bytes()}
        self.content_types: dict[str, str] = {}
        self.downloads = 0

    @asynccontextmanager
    async def get_object(self, _bucket: str, key: str):
        self.downloads += 1

        async def body() -> AsyncIterator[bytes]:
            yield self.objects[key]

        yield {"body": body()}

    async def put_object(
        self, _bucket: str, key: str, *, body: bytes, content_type: str
    ) -> None:
        self.objects[key] = body
        self.content_types[key] = content_type

    async def iter_list_objects_v2(self, _bucket: str, *, prefix: str):
        keys = [key for key in self.objects if key.startswith(prefix)]
        yield {"contents": [{"key": key} for key in keys]}

    async def delete_objects(self, _bucket: str, delete: dict) -> dict:
        for object in delete["objects"]:
            del self.objects[object["key"]]
        return {}


class FakeDb:
    def __init__(self, recorded: int = 0) -> None:
        self.recorded = recorded
        self.rows: list[tuple] = []
        self.deleted: list[str] = []

    async def fetchval(self, _query: str, _document_id: str) -> int:
        return self.recorded

    async def executemany(self, _query: str, rows: list[tuple]) -> None:
        self.rows.extend(rows)
        self.recorded += len(rows)

    async def execute(self, _query: str, document_id: str) -> str:
        self.deleted.append(document_id)
        return "DELETE 1"


class FakeStream:
    published: list[IngestEvent]

    @classmethod
    def from_within_activity(cls) -> FakeStream:
        return cls()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exception: object) -> None:
        pass

    def topic(self, _name: str, *, type: type) -> FakeStream:
        return self

    def publish(self, event: IngestEvent) -> None:
        self.published.append(event)


@pytest.fixture(scope="module")
def page_workers() -> Iterator[PageWorkers]:
    with PageWorkers(2) as workers:
        yield workers


@pytest.fixture
def progress(monkeypatch: pytest.MonkeyPatch) -> list[IngestEvent]:
    published: list[IngestEvent] = []
    monkeypatch.setattr(FakeStream, "published", published, raising=False)
    monkeypatch.setattr(activities, "WorkflowStreamClient", FakeStream)
    return published


async def rasterize(s3: FakeS3, db: FakeDb, page_workers: PageWorkers) -> int:
    document_activities = DocumentActivities(db, s3, page_workers)  # ty: ignore[invalid-argument-type]
    return await ActivityEnvironment().run(document_activities.rasterize_pdf, INPUT)


@pytest.mark.usefixtures("progress")
async def test_stores_an_image_and_a_thumbnail_for_each_page(
    page_workers: PageWorkers,
):
    s3 = FakeS3(FIXTURES / "three-pages.pdf")
    db = FakeDb()

    page_count = await rasterize(s3, db, page_workers)

    assert page_count == 3
    prefix = f"documents/{DOCUMENT_ID}"
    assert set(s3.content_types) == {
        *(f"{prefix}/pages/{page}.jpg" for page in (1, 2, 3)),
        *(f"{prefix}/thumbnails/{page}.webp" for page in (1, 2, 3)),
    }
    assert s3.content_types[f"{prefix}/pages/1.jpg"] == "image/jpeg"
    assert s3.content_types[f"{prefix}/thumbnails/1.webp"] == "image/webp"


@pytest.mark.usefixtures("progress")
async def test_records_each_page(page_workers: PageWorkers):
    db = FakeDb()

    await rasterize(FakeS3(FIXTURES / "three-pages.pdf"), db, page_workers)

    assert [row[:2] for row in db.rows] == [
        (DOCUMENT_ID, 1),
        (DOCUMENT_ID, 2),
        (DOCUMENT_ID, 3),
    ]


@pytest.mark.usefixtures("progress")
async def test_downloads_the_pdf_once(page_workers: PageWorkers):
    s3 = FakeS3(FIXTURES / "three-pages.pdf")

    await rasterize(s3, FakeDb(), page_workers)

    assert s3.downloads == 1


@pytest.mark.usefixtures("progress")
async def test_a_retry_resumes_after_the_last_recorded_page(
    page_workers: PageWorkers,
):
    s3 = FakeS3(FIXTURES / "three-pages.pdf")
    db = FakeDb(recorded=2)

    page_count = await rasterize(s3, db, page_workers)

    assert page_count == 3
    assert [row[1] for row in db.rows] == [3]
    assert set(s3.content_types) == {
        f"documents/{DOCUMENT_ID}/pages/3.jpg",
        f"documents/{DOCUMENT_ID}/thumbnails/3.webp",
    }


@pytest.mark.usefixtures("progress")
async def test_works_on_several_pages_at_once(page_workers: PageWorkers):
    class ConcurrentS3(FakeS3):
        """Each page stores two objects, so a third put can only come from another page."""

        third_put = asyncio.Barrier(3)

        async def put_object(
            self, _bucket: str, key: str, *, body: bytes, content_type: str
        ) -> None:
            await asyncio.wait_for(self.third_put.wait(), timeout=10)
            await super().put_object(_bucket, key, body=body, content_type=content_type)

    s3 = ConcurrentS3(FIXTURES / "three-pages.pdf")

    assert await rasterize(s3, FakeDb(), page_workers) == 3


@pytest.mark.usefixtures("progress")
async def test_records_nothing_past_a_page_that_failed(page_workers: PageWorkers):
    class FailingS3(FakeS3):
        async def put_object(
            self, _bucket: str, key: str, *, body: bytes, content_type: str
        ) -> None:
            if "/pages/2." in key:
                raise OSError("out of space")
            await super().put_object(_bucket, key, body=body, content_type=content_type)

    db = FakeDb()

    with pytest.raises(ExceptionGroup):
        await rasterize(FailingS3(FIXTURES / "three-pages.pdf"), db, page_workers)

    assert db.rows == []


def die() -> None:
    os._exit(1)


async def test_replaces_the_processes_when_one_dies():
    with PageWorkers(1) as workers:
        with pytest.raises(BrokenProcessPool):
            await workers.run(die)

        assert await workers.run(len, "still working") == 13


async def test_reports_progress_from_the_first_page(
    page_workers: PageWorkers, progress: list[IngestEvent]
):
    await rasterize(FakeS3(FIXTURES / "three-pages.pdf"), FakeDb(), page_workers)

    assert progress[0] == IngestEvent(state="rasterizing", page_count=3, pages_done=0)
    assert progress[-1] == IngestEvent(state="rasterizing", page_count=3, pages_done=3)


async def test_records_long_documents_in_chunks(
    monkeypatch: pytest.MonkeyPatch,
    page_workers: PageWorkers,
    progress: list[IngestEvent],
):
    monkeypatch.setattr(activities, "PAGES_PER_RECORD", 2)

    await rasterize(FakeS3(FIXTURES / "three-pages.pdf"), FakeDb(), page_workers)

    assert [event.pages_done for event in progress] == [0, 2, 3]


async def test_rejects_password_protected_pdfs(page_workers: PageWorkers):
    s3 = FakeS3(FIXTURES / "password-protected.pdf")

    with pytest.raises(ApplicationError) as error:
        await rasterize(s3, FakeDb(), page_workers)

    assert error.value.type == IngestError.PASSWORD_PROTECTED
    assert error.value.non_retryable


async def test_rejects_files_that_arent_pdfs(page_workers: PageWorkers, tmp_path: Path):
    not_a_pdf = tmp_path / "not-a.pdf"
    not_a_pdf.write_bytes(b"just some text")

    with pytest.raises(ApplicationError) as error:
        await rasterize(FakeS3(not_a_pdf), FakeDb(), page_workers)

    assert error.value.type == IngestError.DAMAGED


async def test_rejects_pdfs_over_the_page_limit(
    monkeypatch: pytest.MonkeyPatch, page_workers: PageWorkers
):
    monkeypatch.setattr(activities, "MAX_PDF_PAGES", 2)

    with pytest.raises(ApplicationError) as error:
        await rasterize(FakeS3(FIXTURES / "three-pages.pdf"), FakeDb(), page_workers)

    assert error.value.type == IngestError.TOO_MANY_PAGES


@pytest.mark.usefixtures("progress")
async def test_stops_when_the_document_is_deleted_while_rasterizing(
    page_workers: PageWorkers,
):
    class DeletedDb(FakeDb):
        async def executemany(self, _query: str, rows: list[tuple]) -> None:
            raise asyncpg.ForeignKeyViolationError("document is gone")

    with pytest.raises(ApplicationError) as error:
        await rasterize(FakeS3(FIXTURES / "three-pages.pdf"), DeletedDb(), page_workers)

    assert error.value.type == DOCUMENT_DELETED
    assert error.value.non_retryable


async def test_recording_the_page_count_notices_a_deleted_document(
    page_workers: PageWorkers,
):
    class DeletedDb(FakeDb):
        async def fetchrow(self, _query: str, _id: str, _page_count: int) -> None:
            return None

    s3 = FakeS3(FIXTURES / "three-pages.pdf")
    document_activities = DocumentActivities(DeletedDb(), s3, page_workers)  # ty: ignore[invalid-argument-type]

    with pytest.raises(ApplicationError) as error:
        await ActivityEnvironment().run(document_activities.record_page_count, INPUT, 3)

    assert error.value.type == DOCUMENT_DELETED
    assert error.value.non_retryable


async def test_discarding_removes_every_object_of_the_document(
    page_workers: PageWorkers,
):
    s3 = FakeS3(FIXTURES / "three-pages.pdf")
    s3.objects[f"documents/{DOCUMENT_ID}/pages/1.jpg"] = b"page"
    s3.objects[f"documents/{DOCUMENT_ID}/thumbnails/1.webp"] = b"thumbnail"
    s3.objects["documents/SomeOtherId/original.pdf"] = b"another document"
    db = FakeDb()
    document_activities = DocumentActivities(db, s3, page_workers)  # ty: ignore[invalid-argument-type]

    await ActivityEnvironment().run(document_activities.discard_document, INPUT)

    assert set(s3.objects) == {"documents/SomeOtherId/original.pdf"}
    assert db.deleted == [DOCUMENT_ID]
