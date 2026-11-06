// Loaded with `node --import` so the HTTP instrumentation is in place before the AWS SDK loads.
// The Temporal OpenTelemetry plugin is built on OpenTelemetry JS 1.x, whose span shape its workflow
// span exporter produces, so this worker stays on the 1.x SDK while the UI runs 3.x.
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { detectResourcesSync, envDetectorSync, Resource } from "@opentelemetry/resources";
import { BatchSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { ATTR_SERVICE_VERSION } from "@opentelemetry/semantic-conventions";
import { requireEnv } from "./config.ts";

function startTracing() {
  // The service name and other attributes come from OTEL_SERVICE_NAME and OTEL_RESOURCE_ATTRIBUTES
  const resource = Resource.default()
    .merge(detectResourcesSync({ detectors: [envDetectorSync] }))
    .merge(new Resource({ [ATTR_SERVICE_VERSION]: requireEnv("TEMPORAL_WORKER_BUILD_ID") }));
  // Shared with the Temporal plugin, which exports workflow spans from the workflow sandbox through it
  const spanProcessor = new BatchSpanProcessor(new OTLPTraceExporter());
  const provider = new NodeTracerProvider({ resource, spanProcessors: [spanProcessor] });
  provider.register();
  registerInstrumentations({ instrumentations: [new HttpInstrumentation()] });
  return { resource, spanProcessor, shutdown: () => provider.shutdown() };
}

// The exporter reads the endpoint and the rest of its OTEL_EXPORTER_OTLP_* settings itself
export const tracing = process.env.OTEL_EXPORTER_OTLP_ENDPOINT ? startTracing() : undefined;
