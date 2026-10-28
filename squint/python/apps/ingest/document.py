from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError, ApplicationError

with workflow.unsafe.imports_passed_through():
    from activities import rasterize_pdf, record_result

    from models import (
        DOCUMENT_ERRORS,
        DocumentResult,
        DocumentStatus,
        IngestDocumentInput,
        IngestError,
    )

RASTERIZE_RETRY = RetryPolicy(
    maximum_attempts=5,
    non_retryable_error_types=[error.value for error in DOCUMENT_ERRORS],
)


def failure(input: IngestDocumentInput, error: ActivityError) -> DocumentResult:
    cause = error.cause
    if isinstance(cause, ApplicationError) and cause.type in DOCUMENT_ERRORS:
        code = IngestError(cause.type)
        detail = cause.message
    else:
        code = IngestError.INTERNAL
        detail = str(cause or error)
    return DocumentResult(
        document_id=input.document_id,
        upload_id=input.upload_id,
        user_id=input.user_id,
        status=DocumentStatus.FAILED,
        error_code=code,
        error_detail=detail,
    )


@workflow.defn
class IngestDocumentWorkflow:
    """Checks that an uploaded PDF can be opened and records its page count."""

    @workflow.run
    async def run(self, input: IngestDocumentInput) -> DocumentResult:
        try:
            info = await workflow.execute_activity(
                rasterize_pdf,
                input,
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=RASTERIZE_RETRY,
            )
            result = DocumentResult(
                document_id=input.document_id,
                upload_id=input.upload_id,
                user_id=input.user_id,
                status=DocumentStatus.READY,
                page_count=info.page_count,
            )
        except ActivityError as error:
            result = failure(input, error)

        # Next: start embedding the rendered pages

        await workflow.execute_activity(
            record_result, result, start_to_close_timeout=timedelta(minutes=1)
        )
        return result
