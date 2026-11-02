"""What the ingest worker needs to know to hand pages to the embed worker, without importing torch."""

from uuid import UUID

from squint_core.models import CamelModel

EMBED_TASK_QUEUE = "embed"
EMBED_PAGES_ACTIVITY = "embed_pages"
# The TypeScript worker calls these too, so they're named the way its activities are
DELETE_DOCUMENT_VECTORS_ACTIVITY = "deleteDocumentVectors"
DELETE_USER_VECTORS_ACTIVITY = "deleteUserVectors"

# Pages are embedded and recorded together in groups of this size. Measured on an RTX 5070 Ti with
# FlashAttention 2 and torch.compile: throughput plateaued at 4 pages. The worker no longer compiles
# the model, since nearly every batch of cropped pages is a new shape, and eager it reaches 27
# letter pages/s and 21 pages/s for 2048x2048 squares (32 pages/s one page at a time), with
# ~1.4 GiB of GPU memory reserved on squares.
EMBED_BATCH_SIZE = 4


class EmbedPagesInput(CamelModel):
    document_id: str
    user_id: UUID
    bucket: str
    page_numbers: list[int]
