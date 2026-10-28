import { fileURLToPath } from "node:url";
import { loadClientConnectConfig } from "@temporalio/envconfig";
import { NativeConnection, Runtime, Worker } from "@temporalio/worker";
import { createActivities } from "./activities.ts";
import { requireEnv } from "./config.ts";
import { createS3Client } from "./s3.ts";

const TASK_QUEUE = "lifecycle";
const METRICS_ADDRESS = "0.0.0.0:9090";
// Kubernetes sends SIGKILL 30s after SIGTERM by default
const GRACEFUL_SHUTDOWN_TIMEOUT = "25s";

// The Worker Deployment Version that temporal-worker-controller assigned to this pod
const version = {
  deploymentName: requireEnv("TEMPORAL_DEPLOYMENT_NAME"),
  buildId: requireEnv("TEMPORAL_WORKER_BUILD_ID"),
};

// Prometheus metrics labeled the way the controller's per-version HPA selectors expect
Runtime.install({
  telemetryOptions: {
    metrics: {
      prometheus: { bindAddress: METRICS_ADDRESS },
      globalTags: {
        // Kubernetes label values can't contain the "/" in "<namespace>/<name>"
        temporal_worker_deployment_name: version.deploymentName.replace("/", "_"),
        temporal_worker_build_id: version.buildId,
        temporal_namespace: requireEnv("TEMPORAL_NAMESPACE"),
      },
    },
  },
});

const { connectionOptions, namespace } = loadClientConnectConfig();
const connection = await NativeConnection.connect(connectionOptions);
try {
  const worker = await Worker.create({
    connection,
    namespace,
    taskQueue: TASK_QUEUE,
    workflowsPath: fileURLToPath(new URL("./workflows.ts", import.meta.url)),
    activities: createActivities(createS3Client()),
    shutdownGraceTime: GRACEFUL_SHUTDOWN_TIMEOUT,
    workerDeploymentOptions: {
      version,
      useWorkerVersioning: true,
      defaultVersioningBehavior: "PINNED",
    },
  });
  console.log(`${TASK_QUEUE} worker started: ${version.deploymentName} build ${version.buildId}`);
  // Runs until SIGTERM or SIGINT, then drains in-flight tasks
  await worker.run();
} finally {
  await connection.close();
}
