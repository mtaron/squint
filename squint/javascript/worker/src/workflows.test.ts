import { fileURLToPath } from "node:url";
import { TestWorkflowEnvironment } from "@temporalio/testing";
import { Worker } from "@temporalio/worker";
import { afterAll, beforeAll, expect, test } from "vitest";
import type { createActivities } from "./activities.ts";
import { cleanupUserResources, createUserResources } from "./workflows.ts";

const USER_ID = "0f8fad5b-d9cb-469f-a165-70867728950e";

let env: TestWorkflowEnvironment;

beforeAll(async () => {
  env = await TestWorkflowEnvironment.createTimeSkipping();
}, 120_000);

afterAll(async () => {
  await env?.teardown();
});

async function runWithActivities(
  workflow: typeof createUserResources | typeof cleanupUserResources,
): Promise<string[]> {
  const calls: string[] = [];
  const activities: ReturnType<typeof createActivities> = {
    async createUserBucket(userId) {
      calls.push(`createUserBucket ${userId}`);
    },
    async deleteUserBucket(userId) {
      calls.push(`deleteUserBucket ${userId}`);
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
      args: [{ userId: USER_ID }],
    }),
  );
  return calls;
}

test("createUserResources creates the user's bucket", async () => {
  expect(await runWithActivities(createUserResources)).toEqual([`createUserBucket ${USER_ID}`]);
}, 60_000);

test("cleanupUserResources deletes the user's bucket", async () => {
  expect(await runWithActivities(cleanupUserResources)).toEqual([`deleteUserBucket ${USER_ID}`]);
}, 60_000);
