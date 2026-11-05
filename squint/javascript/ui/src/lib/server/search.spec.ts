import type { Client } from "@temporalio/client";
import { beforeEach, expect, test, vi } from "vitest";
import type { SearchEvent } from "#lib/search.ts";
import { getTemporalClient } from "#lib/server/temporal.ts";
import { followSearch, searchWorkflowId } from "./search.ts";

// Importing the real client validates the private environment variables, which tests don't set
vi.mock("#lib/server/temporal.ts", () => ({ getTemporalClient: vi.fn() }));

const streamed = vi.hoisted(() => ({ events: [] as SearchEvent[], followed: [] as string[] }));

vi.mock("@temporalio/workflow-streams/client", () => ({
  WorkflowStreamClient: {
    create: (_client: unknown, workflowId: string) => ({
      topic: () => ({
        async *subscribe() {
          streamed.followed.push(workflowId);
          for (const data of streamed.events) {
            yield { data };
          }
        },
      }),
    }),
  },
}));

const userId = "0f8fad5b-d9cb-469f-a165-70867728950e";
const request = { userId, query: "net revenue", documentId: "V3kQ9xTz2m" };

const located: SearchEvent = {
  state: "locating",
  pages: [{ documentId: "V3kQ9xTz2m", pageNumber: 3, score: 900, boxes: null }],
};
const done: SearchEvent = {
  state: "done",
  pages: [{ documentId: "V3kQ9xTz2m", pageNumber: 3, score: 900, boxes: [] }],
};

let started: unknown[][];

beforeEach(() => {
  started = [];
  streamed.events = [];
  streamed.followed = [];
  const client = {
    workflow: {
      async start(...args: unknown[]) {
        started.push(args);
      },
    },
    withAbortSignal: (_signal: AbortSignal, run: () => Promise<unknown>) => run(),
  } as unknown as Client;
  vi.mocked(getTemporalClient).mockResolvedValue(client);
});

async function follow(): Promise<SearchEvent[]> {
  const events: SearchEvent[] = [];
  await followSearch(request, (event) => events.push(event), new AbortController().signal);
  return events;
}

test("the same search has the same id, which names its user", () => {
  const id = searchWorkflowId(request);

  expect(id).toBe(searchWorkflowId({ ...request }));
  expect(id).toMatch(new RegExp(`^search-${userId}-[0-9a-f]{32}$`));
  expect(searchWorkflowId({ ...request, documentId: undefined })).not.toBe(id);
  expect(searchWorkflowId({ ...request, query: "gross revenue" })).not.toBe(id);
});

test("starts the search in the user's bucket, or follows the one already running", async () => {
  streamed.events = [done];

  await follow();

  expect(started).toEqual([
    [
      "SearchWorkflow",
      {
        taskQueue: "extract",
        workflowId: searchWorkflowId(request),
        workflowIdConflictPolicy: "USE_EXISTING",
        args: [{ ...request, bucket: `squint-u-${userId}` }],
      },
    ],
  ]);
  expect(streamed.followed).toEqual([searchWorkflowId(request)]);
});

test("reports events until the search is done", async () => {
  streamed.events = [located, done, located];

  expect(await follow()).toEqual([located, done]);
});

test("reports a failure when the stream ends early or the search can't start", async () => {
  streamed.events = [located];
  expect(await follow()).toEqual([located, { state: "failed", pages: [] }]);

  vi.mocked(getTemporalClient).mockRejectedValue(new Error("unreachable"));
  vi.spyOn(console, "error").mockImplementation(() => {});
  expect(await follow()).toEqual([{ state: "failed", pages: [] }]);
});
