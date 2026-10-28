import { proxyActivities } from "@temporalio/workflow";
import type { createActivities } from "./activities.ts";

type Activities = ReturnType<typeof createActivities>;

const { createUserBucket } = proxyActivities<Activities>({
  startToCloseTimeout: "1 minute",
});

const { deleteUserBucket } = proxyActivities<Activities>({
  // Emptying a large bucket takes a while, so liveness is tracked with heartbeats instead
  startToCloseTimeout: "1 hour",
  heartbeatTimeout: "1 minute",
});

export interface UserResourcesInput {
  userId: string;
}

/** Provisions what a new user needs. Started by the UI when the user is created. */
export async function createUserResources({ userId }: UserResourcesInput): Promise<void> {
  await createUserBucket(userId);
}

/** Removes what `createUserResources` provisioned. Started by the UI when the user is deleted. */
export async function cleanupUserResources({ userId }: UserResourcesInput): Promise<void> {
  await deleteUserBucket(userId);
}
