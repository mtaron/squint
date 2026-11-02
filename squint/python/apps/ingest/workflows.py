from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.contrib.workflow_streams import WorkflowStream
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from activities import (
        DOCUMENT_DELETED,
        DocumentActivities,
        IngestError,
        IngestEvent,
        IngestInput,
    )

# Subscribers poll for new events, so the final one stays readable for a while after the
# workflow is otherwise done
STREAM_LINGER = timedelta(seconds=30)


def failure_event(error: ActivityError) -> IngestEvent:
    cause = error.cause
    if isinstance(cause, ApplicationError):
        if cause.type == DOCUMENT_DELETED:
            return IngestEvent(state="deleted")
        if cause.type in IngestError:
            return IngestEvent(state="failed", error=IngestError(cause.type))
    return IngestEvent(state="failed", error=IngestError.UNEXPECTED)


@workflow.defn
class IngestDocumentWorkflow:
    """Validates an uploaded PDF, stores an image of each page, and records the page count.
    Started by the UI once the upload has finished; progress is published on the `status` topic
    of the workflow's stream, by the activity while it works through the pages."""

    @workflow.init
    def __init__(self, input: IngestInput) -> None:
        self.stream = WorkflowStream()
        self.status = self.stream.topic("status", type=IngestEvent)

    @workflow.run
    async def run(self, input: IngestInput) -> None:
        self.status.publish(IngestEvent(state="validating"))
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
        except ActivityError as error:
            self.status.publish(failure_event(error))
            await workflow.execute_activity_method(
                DocumentActivities.discard_document,
                input,
                start_to_close_timeout=timedelta(minutes=5),
            )
        else:
            self.status.publish(IngestEvent(state="ingested", page_count=page_count))
        await workflow.sleep(STREAM_LINGER)
