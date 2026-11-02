import { fileURLToPath } from "node:url";
import { TestWorkflowEnvironment } from "@temporalio/testing";
import { Worker } from "@temporalio/worker";
import { afterAll, beforeAll, expect, test } from "vitest";
import type { createActivities } from "./activities.ts";
import { cleanupDocuments, cleanupUserResources, createUserResources } from "./workflows.ts";

const USER_ID = "0f8fad5b-d9cb-469f-a165-70867728950e";

let env: TestWorkflowEnvironment;

beforeAll(async () => {
  env = await TestWorkflowEnvironment.createTimeSkipping();
}, 120_000);

afterAll(async () => {
  await env?.teardown();
});

async function runWithActivities<Input>(
  workflow: (input: Input) => Promise<void>,
  input: Input,
): Promise<string[]> {
  const calls: string[] = [];
  const activities: ReturnType<typeof createActivities> = {
    async createUserBucket(userId) {
      calls.push(`createUserBucket ${userId}`);
    },
    async deleteUserBucket(userId) {
      calls.push(`deleteUserBucket ${userId}`);
    },
    async deleteDocumentObjects(userId, documentIds) {
      calls.push(`deleteDocumentObjects ${userId} ${documentIds.join(" ")}`);
    },
  };
  const taskQueue = `test-${workflow.name}`;
  const worker = await Worker.create({
    connection: env.nativeConnection,
    taskQueue,
    workflowsPath: fileURLToPath(new URL("./workflows.ts", import.meta.url)),
    activities,
  });
  await worker.runUntil(
    env.client.workflow.execute(workflow, {
      taskQueue,
      workflowId: `${workflow.name}-${USER_ID}`,
      args: [input],
    }),
  );
  return calls;
}

test("createUserResources creates the user's bucket", async () => {
  expect(await runWithActivities(createUserResources, { userId: USER_ID })).toEqual([
    `createUserBucket ${USER_ID}`,
  ]);
}, 60_000);

test("cleanupUserResources deletes the user's bucket", async () => {
  expect(await runWithActivities(cleanupUserResources, { userId: USER_ID })).toEqual([
    `deleteUserBucket ${USER_ID}`,
  ]);
}, 60_000);

test("cleanupDocuments deletes the documents' objects", async () => {
  const input = { userId: USER_ID, documentIds: ["first", "second"] };
  expect(await runWithActivities(cleanupDocuments, input)).toEqual([
    `deleteDocumentObjects ${USER_ID} first second`,
  ]);
}, 60_000);
