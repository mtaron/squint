import asyncio
import uuid
from datetime import UTC, datetime

from library import (
    RETAINED_EVENTS,
    STATUS_TOPIC,
    LibraryWorkflow,
    library_workflow_id,
    retain_recent,
)
from temporalio.api.workflowservice.v1 import SetWorkerDeploymentCurrentVersionRequest
from temporalio.client import Client
from temporalio.common import WorkerDeploymentVersion
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.contrib.workflow_streams import (
    PublisherState,
    WorkflowStreamClient,
    WorkflowStreamState,
)
from temporalio.contrib.workflow_streams._types import _WorkflowStreamWireItem
from temporalio.service import RPCError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker, WorkerDeploymentConfig

from models import DocumentStatus, DocumentStatusEvent, LibraryInput


async def make_current(client: Client, version: WorkerDeploymentVersion) -> None:
    """Route new workflows to `version` once its worker has registered with the server."""
    request = SetWorkerDeploymentCurrentVersionRequest(
        namespace=client.namespace,
        deployment_name=version.deployment_name,
        build_id=version.build_id,
    )
    async with asyncio.timeout(10):
        while True:
            try:
                await client.workflow_service.set_worker_deployment_current_version(
                    request
                )
                return
            except RPCError:
                await asyncio.sleep(0.2)


def test_retain_recent_keeps_offsets_monotonic():
    publishers = {"p": PublisherState(sequence=3, last_seen=datetime.now(UTC))}
    state = WorkflowStreamState(
        log=[
            _WorkflowStreamWireItem(topic=STATUS_TOPIC, data=str(i))
            for i in range(RETAINED_EVENTS + 5)
        ],
        base_offset=10,
        publishers=publishers,
    )
    retained = retain_recent(state)
    assert len(retained.log) == RETAINED_EVENTS
    assert retained.log[0].data == "5"
    assert retained.base_offset == 15
    assert retained.publishers == publishers


async def test_subscribers_receive_published_status():
    async with await WorkflowEnvironment.start_local(
        data_converter=pydantic_data_converter
    ) as env:
        task_queue = str(uuid.uuid4())
        workflow_id = library_workflow_id(str(uuid.uuid4()))
        version = WorkerDeploymentVersion(deployment_name="test", build_id=task_queue)
        async with Worker(
            env.client,
            task_queue=task_queue,
            workflows=[LibraryWorkflow],
            deployment_config=WorkerDeploymentConfig(
                version=version, use_worker_versioning=True
            ),
        ):
            await make_current(env.client, version)
            await env.client.start_workflow(
                LibraryWorkflow.run,
                LibraryInput(),
                id=workflow_id,
                task_queue=task_queue,
            )
            event = DocumentStatusEvent(
                document_id="doc",
                upload_id="upload",
                status=DocumentStatus.READY,
                page_count=3,
                error_code=None,
                error_detail=None,
            )
            publisher = WorkflowStreamClient.create(env.client, workflow_id)
            async with publisher:
                publisher.topic(STATUS_TOPIC, type=DocumentStatusEvent).publish(
                    event, force_flush=True
                )

            subscriber = WorkflowStreamClient.create(env.client, workflow_id)
            items = subscriber.topic(STATUS_TOPIC, type=DocumentStatusEvent).subscribe()
            received = await asyncio.wait_for(anext(aiter(items)), timeout=10)
            assert received.data == event
