import asyncio
import signal
from collections.abc import Callable, Sequence
from concurrent.futures import Executor
from datetime import timedelta

from temporalio.common import VersioningBehavior, WorkerDeploymentVersion
from temporalio.runtime import PrometheusConfig, Runtime, TelemetryConfig
from temporalio.worker import Worker, WorkerDeploymentConfig

from squint_core.config import require_env
from squint_core.temporal import create_client

METRICS_ADDRESS = "0.0.0.0:9090"


def deployment_version() -> WorkerDeploymentVersion:
    """The Worker Deployment Version that temporal-worker-controller assigned to this pod."""
    return WorkerDeploymentVersion(
        deployment_name=require_env("TEMPORAL_DEPLOYMENT_NAME"),
        build_id=require_env("TEMPORAL_WORKER_BUILD_ID"),
    )


def shutdown_timeout() -> timedelta:
    """How long in-flight activities get to finish, which the squint-worker chart keeps below the
    pod's termination grace period."""
    return timedelta(seconds=int(require_env("WORKER_SHUTDOWN_TIMEOUT_SECONDS")))


def create_runtime(version: WorkerDeploymentVersion) -> Runtime:
    """A runtime serving Prometheus metrics labeled the way the controller's per-version HPA
    selectors expect."""
    return Runtime(
        telemetry=TelemetryConfig(
            metrics=PrometheusConfig(bind_address=METRICS_ADDRESS),
            global_tags={
                # Kubernetes label values can't contain the "/" in "<namespace>/<name>"
                "temporal_worker_deployment_name": version.deployment_name.replace(
                    "/", "_", 1
                ),
                "temporal_worker_build_id": version.build_id,
                "temporal_namespace": require_env("TEMPORAL_NAMESPACE"),
            },
        )
    )


async def run_worker(
    task_queue: str,
    workflows: Sequence[type],
    activities: Sequence[Callable],
    *,
    max_concurrent_activities: int,
    activity_executor: Executor | None = None,
) -> None:
    """Run a versioned worker until SIGTERM or SIGINT, then drain in-flight tasks."""
    version = deployment_version()
    client = await create_client(create_runtime(version))
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=workflows,
        activities=activities,
        max_concurrent_activities=max_concurrent_activities,
        activity_executor=activity_executor,
        graceful_shutdown_timeout=shutdown_timeout(),
        deployment_config=WorkerDeploymentConfig(
            version=version,
            use_worker_versioning=True,
            default_versioning_behavior=VersioningBehavior.PINNED,
        ),
    )

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    async with worker:
        print(
            f"{task_queue} worker started: {version.deployment_name} build {version.build_id}"
        )
        await stop.wait()
