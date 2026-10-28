from contextlib import asynccontextmanager
from pathlib import Path

import activities
import pikepdf
import pypdfium2 as pdfium
import pytest
from temporalio.exceptions import ApplicationError
from temporalio.testing import ActivityEnvironment

from models import IngestDocumentInput, IngestError


def write_pdf(path: Path, pages: int) -> Path:
    pdf = pdfium.PdfDocument.new()
    for _ in range(pages):
        pdf.new_page(612, 792)
    pdf.save(path)
    pdf.close()
    return path


def write_encrypted_pdf(path: Path, *, user_password: str) -> Path:
    with pikepdf.new() as pdf:
        pdf.add_blank_page()
        pdf.save(path, encryption=pikepdf.Encryption(user=user_password, owner="owner"))
    return path


def error_type(error: pytest.ExceptionInfo[ApplicationError]) -> str | None:
    return error.value.type


def test_counts_pages(tmp_path: Path):
    assert activities.count_pages(write_pdf(tmp_path / "three.pdf", 3)) == 3


def test_rejects_password_protected_pdf(tmp_path: Path):
    path = write_encrypted_pdf(tmp_path / "locked.pdf", user_password="secret")
    with pytest.raises(ApplicationError) as error:
        activities.count_pages(path)
    assert error_type(error) == IngestError.PASSWORD_PROTECTED
    assert error.value.non_retryable


def test_accepts_pdf_with_only_an_owner_password(tmp_path: Path):
    path = write_encrypted_pdf(tmp_path / "restricted.pdf", user_password="")
    assert activities.count_pages(path) == 1


def test_rejects_corrupt_pdf(tmp_path: Path):
    path = tmp_path / "truncated.pdf"
    path.write_bytes(write_pdf(tmp_path / "whole.pdf", 2).read_bytes()[:200])
    with pytest.raises(ApplicationError) as error:
        activities.count_pages(path)
    assert error_type(error) == IngestError.UNREADABLE


def test_rejects_pdf_over_the_page_limit(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(activities, "MAX_PDF_PAGES", 2)
    with pytest.raises(ApplicationError) as error:
        activities.count_pages(write_pdf(tmp_path / "long.pdf", 3))
    assert error_type(error) == IngestError.TOO_MANY_PAGES


class FakeS3:
    def __init__(self, objects: dict[tuple[str, str], bytes]):
        self.objects = objects

    @asynccontextmanager
    async def get_object(self, *, bucket: str, key: str):
        data = self.objects[(bucket, key)]

        async def chunks():
            for start in range(0, len(data), 1024):
                yield data[start : start + 1024]

        yield {"body": chunks()}


async def test_rasterize_pdf_downloads_and_counts_pages(tmp_path: Path, monkeypatch):
    pdf = write_pdf(tmp_path / "doc.pdf", 4).read_bytes()
    monkeypatch.setattr(
        activities, "s3_client", lambda: FakeS3({("bucket", "doc.pdf"): pdf})
    )
    input = IngestDocumentInput(
        document_id="d", upload_id="u", user_id="user", bucket="bucket", key="doc.pdf"
    )
    info = await ActivityEnvironment().run(activities.rasterize_pdf, input)
    assert info.page_count == 4
