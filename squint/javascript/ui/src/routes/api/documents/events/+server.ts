import { error } from "@sveltejs/kit";
import { WorkflowStreamClient } from "@temporalio/workflow-streams/client";
import { getTemporalClient } from "#lib/server/temporal.ts";
import { ensureLibrary, libraryWorkflowId, STATUS_TOPIC } from "#lib/server/uploads/ingest.ts";
import type { DocumentStatusEvent } from "#lib/uploads/documents.ts";
import type { RequestHandler } from "./$types";

// Keeps proxies from closing the connection while no documents change
const KEEPALIVE_MS = 25_000;

/**
 * Server-sent events with the status of the signed-in user's documents, relayed from their
 * library workflow's stream. Starts at the current end of the stream: clients reload the list
 * when they connect, which covers anything published earlier.
 */
export const GET: RequestHandler = async ({ locals, request }) => {
  if (!locals.user) error(401);
  const client = await getTemporalClient();
  await ensureLibrary(client, locals.user.id);
  const stream = WorkflowStreamClient.create(client, libraryWorkflowId(locals.user.id));
  const items = stream.subscribe<DocumentStatusEvent>(STATUS_TOPIC, await stream.getOffset(), {
    resultType: true,
  });
  const encoder = new TextEncoder();
  let keepalive: ReturnType<typeof setInterval> | undefined;

  const body = new ReadableStream<Uint8Array>({
    async start(controller) {
      const send = (text: string) => controller.enqueue(encoder.encode(text));
      keepalive = setInterval(() => send(": keepalive\n\n"), KEEPALIVE_MS);
      send(": connected\n\n");
      try {
        for await (const item of items) {
          if (request.signal.aborted) break;
          send(`id: ${item.offset}\ndata: ${JSON.stringify(item.data)}\n\n`);
        }
      } catch (cause) {
        if (!request.signal.aborted) console.error("document status stream failed", cause);
      } finally {
        clearInterval(keepalive);
        if (!request.signal.aborted) controller.close();
      }
    },
    cancel() {
      clearInterval(keepalive);
      void items.return(undefined);
    },
  });

  return new Response(body, {
    headers: {
      "content-type": "text/event-stream",
      "cache-control": "no-cache",
      "x-accel-buffering": "no",
    },
  });
};
