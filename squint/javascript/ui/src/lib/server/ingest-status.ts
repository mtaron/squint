import { setTimeout as sleep } from "node:timers/promises";
import { WorkflowStreamClient } from "@temporalio/workflow-streams/client";
import { ingestWorkflowId, isFinalIngestEvent, type IngestEvent } from "#lib/ingest.ts";
import { pageCount } from "#lib/server/documents.ts";
import { getTemporalClient } from "#lib/server/temporal.ts";

// The workflow may not have started yet, or the stream ended without a final event
const RECHECK_DELAY_MS = 2000;

async function readStream(
  documentId: string,
  onEvent: (event: IngestEvent) => void,
  signal: AbortSignal,
): Promise<IngestEvent | undefined> {
  const client = await getTemporalClient();
  return client.withAbortSignal(signal, async () => {
    const status = WorkflowStreamClient.create(
      client,
      ingestWorkflowId(documentId),
    ).topic<IngestEvent>("status");
    for await (const { data } of status.subscribe()) {
      onEvent(data);
      if (isFinalIngestEvent(data)) {
        return data;
      }
    }
    return undefined;
  });
}

/** The final state from the database, for when the workflow's stream is no longer readable. */
async function storedState(documentId: string): Promise<IngestEvent | undefined> {
  const pages = await pageCount(documentId);
  if (pages === undefined) {
    return { state: "failed", error: "unexpected" };
  }
  return pages === null ? undefined : { state: "ingested", pageCount: pages };
}

/** Reports a document's ingestion events until it's ingested or failed, or `signal` aborts. */
export async function followIngestion(
  documentId: string,
  onEvent: (event: IngestEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  while (!signal.aborted) {
    try {
      if (await readStream(documentId, onEvent, signal)) {
        return;
      }
      const stored = await storedState(documentId);
      if (stored) {
        onEvent(stored);
        return;
      }
      await sleep(RECHECK_DELAY_MS, undefined, { signal });
    } catch (error) {
      if (signal.aborted) {
        return;
      }
      console.error(`Failed to follow ingestion of ${documentId}`, error);
      await sleep(RECHECK_DELAY_MS, undefined, { signal }).catch(() => {});
    }
  }
}
