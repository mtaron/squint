import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.contrib.workflow_streams import WorkflowStream
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from squint_core.documents import DOCUMENT_DELETED
    from squint_core.embedding import (
        EMBED_TASK_QUEUE,
        ENCODE_QUERY_ACTIVITY,
        QUERY_PRIORITY,
        EncodedQuery,
    )

    from activities import (
        ExtractActivities,
        FindPagesInput,
        LocateInput,
        SearchEvent,
        SearchHit,
        SearchInput,
        SearchState,
    )

# Subscribers poll for new events, so the final one stays readable for a while after the
# workflow is otherwise done
STREAM_LINGER = timedelta(seconds=30)


def is_document_deleted(error: ActivityError) -> bool:
    cause = error.cause
    return isinstance(cause, ApplicationError) and cause.type == DOCUMENT_DELETED


@workflow.defn
class SearchWorkflow:
    """Finds the pages that best match a query, then asks Qwen where each one shows it. Started by
    the UI, which follows the `search` topic of the stream. Every event carries every page found
    so far, so a subscriber only needs the latest."""

    @workflow.init
    def __init__(self, input: SearchInput) -> None:
        self.input = input
        self.stream = WorkflowStream()
        self.events = self.stream.topic("search", type=SearchEvent)
        self.hits: list[SearchHit] = []

    def snapshot(self, state: SearchState) -> SearchEvent:
        event = SearchEvent(state=state, pages=self.hits)
        self.events.publish(event)
        return event

    async def find_pages(self, input: SearchInput) -> list[SearchHit]:
        query = await workflow.execute_activity(
            ENCODE_QUERY_ACTIVITY,
            input.query,
            task_queue=EMBED_TASK_QUEUE,
            result_type=EncodedQuery,
            priority=QUERY_PRIORITY,
            schedule_to_close_timeout=timedelta(minutes=1),
            start_to_close_timeout=timedelta(seconds=20),
        )
        matches = await workflow.execute_activity_method(
            ExtractActivities.find_pages,
            FindPagesInput(
                user_id=input.user_id, document_id=input.document_id, query=query
            ),
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        return [
            SearchHit(
                document_id=match.document_id,
                page_number=match.page_number,
                score=match.score,
            )
            for match in matches
        ]

    async def locate(self, hit: SearchHit) -> None:
        """A page Qwen can't read stays related to the query, while a deleted document's pages
        leave the results."""
        try:
            boxes = await workflow.execute_activity_method(
                ExtractActivities.locate_text,
                LocateInput(
                    bucket=self.input.bucket,
                    document_id=hit.document_id,
                    page_number=hit.page_number,
                    text=self.input.query,
                ),
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
        except ActivityError as error:
            if is_document_deleted(error):
                self.hits = [
                    other for other in self.hits if other.document_id != hit.document_id
                ]
                self.snapshot("locating")
                return
            workflow.logger.warning(
                f"Failed to locate the query on {hit.document_id} page {hit.page_number}: {error}"
            )
            boxes = []
        self.hits = [
            other.model_copy(update={"boxes": boxes})
            if other.page_key == hit.page_key
            else other
            for other in self.hits
        ]
        self.snapshot("locating")

    @workflow.run
    async def run(self, input: SearchInput) -> SearchEvent:
        self.snapshot("searching")
        try:
            self.hits = await self.find_pages(input)
        except ActivityError as error:
            workflow.logger.warning(f"Failed to find pages: {error}")
            final = self.snapshot("failed")
        else:
            pending = list(self.hits)
            self.snapshot("locating")
            await asyncio.gather(*(self.locate(hit) for hit in pending))
            final = self.snapshot("done")
        await workflow.sleep(STREAM_LINGER)
        return final
