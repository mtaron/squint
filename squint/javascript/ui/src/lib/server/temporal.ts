import { readFileSync } from "node:fs";
import { Client, Connection } from "@temporalio/client";
import { OpenTelemetryWorkflowClientInterceptor } from "@temporalio/interceptors-opentelemetry/lib/client";
import { TEMPORAL_ADDRESS, TEMPORAL_TLS_SERVER_CA_CERT_PATH } from "$app/env/private";

let client: Promise<Client> | undefined;

export function getTemporalClient(): Promise<Client> {
  client ??= Connection.connect({
    address: TEMPORAL_ADDRESS,
    tls: { serverRootCACertificate: readFileSync(TEMPORAL_TLS_SERVER_CA_CERT_PATH) },
  })
    .then(
      (connection) =>
        new Client({
          connection,
          interceptors: { workflow: [new OpenTelemetryWorkflowClientInterceptor()] },
        }),
    )
    .catch((error) => {
      client = undefined;
      throw error;
    });
  return client;
}
