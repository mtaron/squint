import type { BetterAuthPlugin } from "better-auth";
import type { Client, WorkflowIdConflictPolicy } from "@temporalio/client";
import { getTemporalClient } from "#lib/server/temporal.ts";

// Served by the TypeScript worker in squint/javascript/worker
const TASK_QUEUE = "lifecycle";

type UserResourcesWorkflow = "createUserResources" | "cleanupUserResources";

async function startUserResourcesWorkflow(
  getClient: () => Promise<Client>,
  workflow: UserResourcesWorkflow,
  userId: string,
  workflowIdConflictPolicy: WorkflowIdConflictPolicy,
) {
  const client = await getClient();
  // One id per user, so cleanup can supersede a creation that is still running
  await client.workflow.start(workflow, {
    taskQueue: TASK_QUEUE,
    workflowId: `user-resources-${userId}`,
    workflowIdConflictPolicy,
    args: [{ userId }],
  });
}

/** Provisions each user's resources, such as their S3 bucket, and cleans them up when the user is deleted. */
export function userResources(getClient: () => Promise<Client> = getTemporalClient) {
  return {
    id: "user-resources",
    init: () => ({
      options: {
        databaseHooks: {
          user: {
            create: {
              after: (user) =>
                startUserResourcesWorkflow(
                  getClient,
                  "createUserResources",
                  user.id,
                  "USE_EXISTING",
                ),
            },
            delete: {
              after: (user) =>
                startUserResourcesWorkflow(
                  getClient,
                  "cleanupUserResources",
                  user.id,
                  "TERMINATE_EXISTING",
                ),
            },
          },
        },
      },
    }),
  } satisfies BetterAuthPlugin;
}
