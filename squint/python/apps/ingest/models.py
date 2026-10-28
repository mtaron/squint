from enum import StrEnum

from pydantic import BaseModel
from temporalio.contrib.workflow_streams import WorkflowStreamState

# Column values of the UI's `document` table (squint/javascript/ui/src/lib/server/db/documents.schema.ts)


class DocumentStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class IngestError(StrEnum):
    PASSWORD_PROTECTED = "password_protected"
    UNSUPPORTED_SECURITY = "unsupported_security"
    UNREADABLE = "unreadable"
    TOO_MANY_PAGES = "too_many_pages"
    INTERNAL = "internal"


DOCUMENT_ERRORS = frozenset(IngestError) - {IngestError.INTERNAL}


class IngestDocumentInput(BaseModel):
    document_id: str
    upload_id: str
    user_id: str
    bucket: str
    key: str


class PdfInfo(BaseModel):
    page_count: int


class DocumentResult(BaseModel):
    document_id: str
    upload_id: str
    user_id: str
    status: DocumentStatus
    page_count: int | None = None
    error_code: IngestError | None = None
    error_detail: str | None = None


class DocumentStatusEvent(BaseModel):
    document_id: str
    upload_id: str
    status: DocumentStatus
    page_count: int | None
    error_code: IngestError | None
    error_detail: str | None


class LibraryInput(BaseModel):
    stream_state: WorkflowStreamState | None = None
