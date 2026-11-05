from uuid import UUID

from temporalio.common import Priority

from squint_core.models import CamelModel

EMBED_TASK_QUEUE = "embed"
EMBED_PAGES_ACTIVITY = "embed_pages"
ENCODE_QUERY_ACTIVITY = "encode_query"
# The TypeScript worker calls these too, so they're named the way its activities are
DELETE_DOCUMENT_VECTORS_ACTIVITY = "deleteDocumentVectors"
DELETE_USER_VECTORS_ACTIVITY = "deleteUserVectors"
EMBED_BATCH_SIZE = 4


class EmbedPagesInput(CamelModel):
    document_id: str
    user_id: UUID
    bucket: str
    page_numbers: list[int]


class EncodedQuery(CamelModel):
    """NeoMME's dense vector for a query, and its quantized late-interaction tokens."""

    dense: list[float]
    tokens: list[list[int]]


# Someone is waiting on a search, so its query skips ahead of the page batches queued at the
# default priority of 3
QUERY_PRIORITY = Priority(priority_key=1)
