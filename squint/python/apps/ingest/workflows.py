import asyncio
from datetime import timedelta
from itertools import batched
from typing import Literal

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.contrib.workflow_streams import WorkflowStream
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from squint_core.documents import DOCUMENT_DELETED
    from squint_core.embedding import (
        DELETE_DOCUMENT_VECTORS_ACTIVITY,
        EMBED_BATCH_SIZE,
        EMBED_PAGES_ACTIVITY,
        EMBED_TASK_QUEUE,
        EmbedPagesInput,
    )

    from activities import (
        PAGES_STORED_SIGNAL,
        DocumentActivities,
        IngestError,
        IngestEvent,
        IngestInput,
        PagesStored,
    )

# Subscribers poll for new events, so the final one stays readable for a while after the
# workflow is otherwise done
STREAM_LINGER = timedelta(seconds=30)


def is_document_deleted(error: ActivityError) -> bool:
    cause = error.cause
    return isinstance(cause, ApplicationError) and cause.type == DOCUMENT_DELETED


def failure_event(error: ActivityError) -> IngestEvent:
    if is_document_deleted(error):
        return IngestEvent(state="deleted")
    cause = error.cause
    if isinstance(cause, ApplicationError) and cause.type in IngestError:
        return IngestEvent(state="failed", error=IngestError(cause.type))
    return IngestEvent(state="failed", error=IngestError.UNEXPECTED)


@workflow.defn
class IngestDocumentWorkflow:
    """Validates an uploaded PDF, stores an image of each page, records the page count, and embeds
    the pages as they become ready. Started by the UI once the upload has finished. This is the
    only publisher on the `status` topic of the stream, so every event has both kinds of progress.
    The document is usable once its page count is recorded, whatever happens to its embeddings."""

    @workflow.init
    def __init__(self, input: IngestInput) -> None:
        self.input = input
        self.stream = WorkflowStream()
        self.status = self.stream.topic("status", type=IngestEvent)
        self.state: Literal["validating", "rasterizing", "embedding"] = "validating"
        self.page_count: int | None = None
        self.pages_done = 0
        self.pages_embedded = 0
        self.embedding: dict[int, asyncio.Task[None]] = {}
        self.published: tuple[str, int, int] | None = None

    def percent_of_pages(self, pages: int) -> int:
        return pages * 100 // (self.page_count or 1)

    def publish_progress(self) -> None:
        """Only as a bar moves a whole percent, since each event costs subscribers a poll in the
        workflow's history. A 2,000-page document would otherwise get near Temporal's 10k warning."""
        progress = (
            self.state,
            self.percent_of_pages(self.pages_done),
            self.percent_of_pages(self.pages_embedded),
        )
        if progress == self.published:
            return
        self.published = progress
        self.status.publish(
            IngestEvent(
                state=self.state,
                page_count=self.page_count,
                pages_done=self.pages_done,
                pages_embedded=self.pages_embedded,
            )
        )

    async def embed_group(self, page_numbers: list[int]) -> None:
        try:
            await workflow.execute_activity(
                EMBED_PAGES_ACTIVITY,
                EmbedPagesInput(
                    document_id=self.input.document_id,
                    user_id=self.input.user_id,
                    bucket=self.input.bucket,
                    page_numbers=page_numbers,
                ),
                task_queue=EMBED_TASK_QUEUE,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
        except ActivityError as error:
            if is_document_deleted(error):
                raise
            workflow.logger.warning(f"Failed to embed pages {page_numbers}: {error}")
        else:
            self.pages_embedded += len(page_numbers)
            self.publish_progress()

    def start_embedding(self, page_numbers: list[int]) -> bool:
        """Whether the group is new. A group's first page identifies it, since a retry of the
        activity can repeat a signal."""
        if page_numbers[0] in self.embedding:
            return False
        self.embedding[page_numbers[0]] = asyncio.create_task(
            self.embed_group(page_numbers)
        )
        return True

    @workflow.signal(name=PAGES_STORED_SIGNAL)
    def pages_stored(self, stored: PagesStored) -> None:
        if self.start_embedding(stored.page_numbers):
            self.state = "rasterizing"
            self.page_count = stored.page_count
            self.pages_done += len(stored.page_numbers)
            self.publish_progress()

    async def discard(self, error: ActivityError) -> None:
        """Waits for embedding to stop, so none of its vectors arrive after they're deleted. Once a
        document is gone, the batches still queued notice right away."""
        self.status.publish(failure_event(error))
        await asyncio.gather(*self.embedding.values(), return_exceptions=True)
        await workflow.execute_activity_method(
            DocumentActivities.discard_document,
            self.input,
            start_to_close_timeout=timedelta(minutes=5),
        )
        await workflow.execute_activity(
            DELETE_DOCUMENT_VECTORS_ACTIVITY,
            [self.input.document_id],
            task_queue=EMBED_TASK_QUEUE,
            start_to_close_timeout=timedelta(minutes=1),
        )

    @workflow.run
    async def run(self, input: IngestInput) -> None:
        self.publish_progress()
        try:
            page_count = await workflow.execute_activity_method(
                DocumentActivities.rasterize_pdf,
                input,
                start_to_close_timeout=timedelta(hours=1),
                heartbeat_timeout=timedelta(minutes=1),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
            await workflow.execute_activity_method(
                DocumentActivities.record_page_count,
                args=[input, page_count],
                start_to_close_timeout=timedelta(minutes=1),
            )
            # Picks up any group whose signal was lost to a failed attempt
            groups = batched(range(1, page_count + 1), EMBED_BATCH_SIZE)
            for group in groups:
                self.start_embedding(list(group))
            self.state = "embedding"
            self.page_count = page_count
            self.pages_done = page_count
            self.publish_progress()
            await asyncio.gather(*self.embedding.values())
        except ActivityError as error:
            await self.discard(error)
        else:
            self.status.publish(
                IngestEvent(
                    state="ingested",
                    page_count=page_count,
                    pages_done=page_count,
                    pages_embedded=self.pages_embedded,
                )
            )
        await workflow.sleep(STREAM_LINGER)
