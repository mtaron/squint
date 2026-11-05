import { createHash } from "node:crypto";
import { userBucketName } from "@squint/db/storage";
import { WorkflowStreamClient } from "@temporalio/workflow-streams/client";
import { isFinalSearchEvent, type SearchEvent } from "#lib/search.ts";
import { getTemporalClient } from "#lib/server/temporal.ts";

// Served by the Python worker in squint/python/apps/extract
const EXTRACT_TASK_QUEUE = "extract";

export interface SearchRequest {
  userId: string;
  query: string;
  documentId?: string;
}

/**
 * The same search gets the same id, so a live query that reconnects follows the search it
 * started rather than starting another. The id ends with the user's, so it can't follow theirs.
 */
export function searchWorkflowId({ userId, query, documentId }: SearchRequest): string {
  const hash = createHash("sha256")
    .update(JSON.stringify([documentId ?? null, query]))
    .digest("hex")
    .slice(0, 32);
  return `search-${userId}-${hash}`;
}

/**
 * Starts the search unless the same one is still running, then reports its events until the last
 * one, or until `signal` aborts. The workflow's pages stay scoped to the user's own, since it only
 * reads their bucket and their vectors.
 */
export async function followSearch(
  request: SearchRequest,
  onEvent: (event: SearchEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  try {
    const client = await getTemporalClient();
    const workflowId = searchWorkflowId(request);
    await client.workflow.start("SearchWorkflow", {
      taskQueue: EXTRACT_TASK_QUEUE,
      workflowId,
      workflowIdConflictPolicy: "USE_EXISTING",
      args: [{ ...request, bucket: userBucketName(request.userId) }],
    });
    const final = await client.withAbortSignal(signal, async () => {
      const events = WorkflowStreamClient.create(client, workflowId).topic<SearchEvent>("search");
      for await (const { data } of events.subscribe()) {
        onEvent(data);
        if (isFinalSearchEvent(data)) {
          return data;
        }
      }
      return undefined;
    });
    if (!final) {
      onEvent({ state: "failed", pages: [] });
    }
  } catch (error) {
    if (signal.aborted) {
      return;
    }
    console.error("Failed to follow a search", error);
    onEvent({ state: "failed", pages: [] });
  }
}
