import shutil
from pathlib import Path
from uuid import UUID

import pytest
from temporalio.exceptions import ApplicationError
from temporalio.testing import ActivityEnvironment

import activities
from activities import IngestError, IngestInput, PdfActivities

FIXTURES = Path(__file__).parent / "fixtures"

INPUT = IngestInput(
    document_id=UUID("0193b4a4-7a39-7f5e-8a1b-4b3c2d1e0f00"),
    user_id=UUID("0f8fad5b-d9cb-469f-a165-70867728950e"),
    bucket="squint-u-0f8fad5b-d9cb-469f-a165-70867728950e",
    key="documents/0193b4a4-7a39-7f5e-8a1b-4b3c2d1e0f00.pdf",
)


def rasterize(monkeypatch: pytest.MonkeyPatch, source: Path) -> int:
    monkeypatch.setattr(
        activities,
        "download",
        lambda _s3, _input, destination: shutil.copy(source, destination),
    )
    return ActivityEnvironment().run(PdfActivities(s3=None).rasterize_pdf, INPUT)  # ty: ignore[invalid-argument-type]


def test_counts_pages(monkeypatch: pytest.MonkeyPatch):
    assert rasterize(monkeypatch, FIXTURES / "three-pages.pdf") == 3


def test_rejects_password_protected_pdfs(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(ApplicationError) as error:
        rasterize(monkeypatch, FIXTURES / "password-protected.pdf")
    assert error.value.type == IngestError.PASSWORD_PROTECTED
    assert error.value.non_retryable


def test_rejects_files_that_arent_pdfs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    not_a_pdf = tmp_path / "not-a.pdf"
    not_a_pdf.write_bytes(b"just some text")
    with pytest.raises(ApplicationError) as error:
        rasterize(monkeypatch, not_a_pdf)
    assert error.value.type == IngestError.DAMAGED


def test_rejects_pdfs_over_the_page_limit(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(activities, "MAX_PDF_PAGES", 2)
    with pytest.raises(ApplicationError) as error:
        rasterize(monkeypatch, FIXTURES / "three-pages.pdf")
    assert error.value.type == IngestError.TOO_MANY_PAGES
