from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.contrib.workflow_streams import WorkflowStream
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from activities import (
        DocumentActivities,
        IngestError,
        IngestEvent,
        IngestInput,
        PdfActivities,
    )

# Subscribers poll for new events, so the final one stays readable for a while after the
# workflow is otherwise done
STREAM_LINGER = timedelta(seconds=30)


def failure_reason(error: ActivityError) -> IngestError:
    cause = error.cause
    if isinstance(cause, ApplicationError) and cause.type in IngestError:
        return IngestError(cause.type)
    return IngestError.UNEXPECTED


@workflow.defn
class IngestDocumentWorkflow:
    """Validates an uploaded PDF and records its page count. Started by the UI once the upload
    has finished; progress is published on the `status` topic of the workflow's stream."""

    @workflow.init
    def __init__(self, input: IngestInput) -> None:
        self.stream = WorkflowStream()
        self.status = self.stream.topic("status", type=IngestEvent)

    @workflow.run
    async def run(self, input: IngestInput) -> None:
        self.status.publish(IngestEvent(state="validating"))
        try:
            page_count = await workflow.execute_activity_method(
                PdfActivities.rasterize_pdf,
                input,
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(minutes=1),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
        except ActivityError as error:
            self.status.publish(
                IngestEvent(state="failed", error=failure_reason(error))
            )
            await workflow.execute_activity_method(
                DocumentActivities.discard_document,
                input,
                start_to_close_timeout=timedelta(minutes=1),
            )
        else:
            await workflow.execute_activity_method(
                DocumentActivities.record_page_count,
                args=[input, page_count],
                start_to_close_timeout=timedelta(minutes=1),
            )
            self.status.publish(IngestEvent(state="ingested", page_count=page_count))
        await workflow.sleep(STREAM_LINGER)
