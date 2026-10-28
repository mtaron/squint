from datetime import timedelta

from temporalio import workflow
from temporalio.common import VersioningBehavior

with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.workflow_streams import WorkflowStream, WorkflowStreamState

    from models import LibraryInput

STATUS_TOPIC = "document_status"
RETAINED_EVENTS = 1000
IDLE_TIMEOUT = timedelta(hours=24)


def library_workflow_id(user_id: str) -> str:
    return f"library-{user_id}"


def retain_recent(state: WorkflowStreamState) -> WorkflowStreamState:
    dropped = max(0, len(state.log) - RETAINED_EVENTS)
    return WorkflowStreamState(
        log=state.log[dropped:],
        base_offset=state.base_offset + dropped,
        publishers=state.publishers,
    )


def next_offset(state: WorkflowStreamState) -> int:
    return state.base_offset + len(state.log)


# Long-lived and passive, so it follows new worker builds instead of pinning to the one it
# started on
@workflow.defn(versioning_behavior=VersioningBehavior.AUTO_UPGRADE)
class LibraryWorkflow:
    """Hosts a user's stream of document status events, which the UI follows to update the
    document list live. The UI starts it on demand; it completes after a day without events."""

    @workflow.init
    def __init__(self, input: LibraryInput) -> None:
        self.stream = WorkflowStream(prior_state=input.stream_state)

    @workflow.run
    async def run(self, input: LibraryInput) -> None:
        while True:
            offset = next_offset(self.stream.get_state())
            try:
                await workflow.wait_condition(
                    lambda: workflow.info().is_continue_as_new_suggested(),
                    timeout=IDLE_TIMEOUT,
                )
            except TimeoutError:
                if next_offset(self.stream.get_state()) == offset:
                    self.stream.detach_pollers()
                    await workflow.wait_condition(workflow.all_handlers_finished)
                    return
                continue
            await self.stream.continue_as_new(
                lambda state: [LibraryInput(stream_state=retain_recent(state))]
            )
