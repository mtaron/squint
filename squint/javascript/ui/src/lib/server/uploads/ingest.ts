import type { Client } from "@temporalio/client";
import { getTemporalClient } from "#lib/server/temporal.ts";

// Workflows and topics hosted by squint/python/apps/ingest
const TASK_QUEUE = "ingest";
export const STATUS_TOPIC = "document_status";

export function libraryWorkflowId(userId: string): string {
  return `library-${userId}`;
}

/** Starts the user's status stream unless it is already running. */
export async function ensureLibrary(client: Client, userId: string): Promise<void> {
  await client.workflow.start("LibraryWorkflow", {
    taskQueue: TASK_QUEUE,
    workflowId: libraryWorkflowId(userId),
    workflowIdConflictPolicy: "USE_EXISTING",
    args: [{}],
  });
}

export type IngestTarget = {
  documentId: string;
  uploadId: string;
  userId: string;
  bucket: string;
  key: string;
};

export async function startIngestion(target: IngestTarget): Promise<void> {
  const client = await getTemporalClient();
  await ensureLibrary(client, target.userId);
  await client.workflow.start("IngestDocumentWorkflow", {
    taskQueue: TASK_QUEUE,
    workflowId: `ingest-${target.documentId}-${target.uploadId}`,
    args: [
      {
        document_id: target.documentId,
        upload_id: target.uploadId,
        user_id: target.userId,
        bucket: target.bucket,
        key: target.key,
      },
    ],
  });
}
