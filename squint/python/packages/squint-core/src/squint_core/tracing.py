import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk.resources import SERVICE_VERSION, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from temporalio.client import Plugin
from temporalio.contrib.opentelemetry import (
    OpenTelemetryPlugin,
    ReplaySafeTracerProvider,
    create_tracer_provider,
)

from squint_core.config import require_env


def configure_tracing(*instrumentors: BaseInstrumentor) -> None:
    """Export traces to OTEL_EXPORTER_OTLP_ENDPOINT, if it is set, and install asyncpg's
    instrumentation along with the given ones. The service name and other resource attributes come
    from the standard OTEL_* environment variables.

    Call this before creating any clients: some instrumentations, like gRPC's, only trace
    connections opened after they are installed."""
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return

    # Replay-safe, so workflow spans aren't exported again when a worker replays a history
    provider = create_tracer_provider(
        resource=Resource.create(
            {SERVICE_VERSION: require_env("TEMPORAL_WORKER_BUILD_ID")}
        )
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    for instrumentor in (AsyncPGInstrumentor(), *instrumentors):
        instrumentor.instrument()


def temporal_plugins() -> list[Plugin]:
    """The Temporal client plugins that trace workflows and activities, once tracing is configured.
    Workers created from the client inherit them."""
    if not isinstance(trace.get_tracer_provider(), ReplaySafeTracerProvider):
        return []
    return [OpenTelemetryPlugin(add_temporal_spans=True)]
