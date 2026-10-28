import type { Client } from "@temporalio/client";
import { expect, test, vi } from "vitest";
import { userResources } from "./user-resources.ts";

// Importing the real client validates the private environment variables, which tests don't set
vi.mock("#lib/server/temporal.ts", () => ({ getTemporalClient: vi.fn() }));

const user = {
  id: "0f8fad5b-d9cb-469f-a165-70867728950e",
  name: "Ada",
  email: "ada@example.com",
  emailVerified: false,
  createdAt: new Date(),
  updatedAt: new Date(),
};

function userHooks() {
  const started: unknown[][] = [];
  const client = {
    workflow: {
      async start(...args: unknown[]) {
        started.push(args);
      },
    },
  } as unknown as Client;
  const hooks = userResources(async () => client).init().options.databaseHooks.user;
  return { hooks, started };
}

test("creating a user starts createUserResources", async () => {
  const { hooks, started } = userHooks();
  await hooks.create.after(user);
  expect(started).toEqual([
    [
      "createUserResources",
      {
        taskQueue: "lifecycle",
        workflowId: `user-resources-${user.id}`,
        workflowIdConflictPolicy: "USE_EXISTING",
        args: [{ userId: user.id }],
      },
    ],
  ]);
});

test("deleting a user starts cleanupUserResources, superseding a running creation", async () => {
  const { hooks, started } = userHooks();
  await hooks.delete.after(user);
  expect(started).toEqual([
    [
      "cleanupUserResources",
      {
        taskQueue: "lifecycle",
        workflowId: `user-resources-${user.id}`,
        workflowIdConflictPolicy: "TERMINATE_EXISTING",
        args: [{ userId: user.id }],
      },
    ],
  ]);
});
