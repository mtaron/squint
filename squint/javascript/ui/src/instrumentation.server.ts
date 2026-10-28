import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { GrpcInstrumentation } from "@opentelemetry/instrumentation-grpc";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { RedisInstrumentation } from "@opentelemetry/instrumentation-redis";
import { UndiciInstrumentation } from "@opentelemetry/instrumentation-undici";
import { NodeSDK } from "@opentelemetry/sdk-node";
import { register } from "import-in-the-middle/register-hooks.mjs";

// Read directly rather than through $app/env, since src/env.ts and its imports load before this file
// and couldn't be instrumented. The SDK reads its other standard OTEL_* variables itself.
const tracesEnabled = Boolean(process.env.OTEL_EXPORTER_OTLP_ENDPOINT);

if (tracesEnabled) {
  const instrumentations = [
    new HttpInstrumentation({
      ignoreIncomingRequestHook: (request) => request.url === "/health",
    }),
    new RedisInstrumentation(),
    new UndiciInstrumentation(),
    new GrpcInstrumentation(),
  ];

  // Wrapping every module breaks live bindings in SvelteKit's server chunks (`hooks` stays unset)
  register({
    include: instrumentations.flatMap((instrumentation) =>
      instrumentation.getModuleDefinitions().map((definition) => definition.name),
    ),
  });

  const sdk = new NodeSDK({
    serviceName: "squint-ui",
    traceExporter: new OTLPTraceExporter(),
    instrumentations,
  });

  sdk.start();

  // adapter-node emits this once in-flight requests finish, so the last spans are flushed before exit
  process.on("sveltekit:shutdown", () => sdk.shutdown());
}
