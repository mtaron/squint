import { proxyActivities } from "@temporalio/workflow";
import type { createActivities } from "./activities.ts";

type Activities = ReturnType<typeof createActivities>;

const { createUserBucket } = proxyActivities<Activities>({
  startToCloseTimeout: "1 minute",
});

const { deleteDocumentObjects, deleteUserBucket } = proxyActivities<Activities>({
  // Emptying a large bucket takes a while, so liveness is tracked with heartbeats instead
  startToCloseTimeout: "1 hour",
  heartbeatTimeout: "1 minute",
});

/** Served by the Python worker in squint/python/apps/embed, the only one that talks to Milvus. */
interface VectorActivities {
  deleteDocumentVectors(documentIds: string[]): Promise<void>;
  deleteUserVectors(userId: string): Promise<void>;
}

const { deleteDocumentVectors, deleteUserVectors } = proxyActivities<VectorActivities>({
  taskQueue: "embed",
  startToCloseTimeout: "1 minute",
});

export interface UserResourcesInput {
  userId: string;
}

export interface CleanupDocumentsInput {
  userId: string;
  documentIds: string[];
}

/** Provisions what a new user needs. Started by the UI when the user is created. */
export async function createUserResources({ userId }: UserResourcesInput): Promise<void> {
  await createUserBucket(userId);
}

/** Removes what `createUserResources` provisioned. Started by the UI when the user is deleted. */
export async function cleanupUserResources({ userId }: UserResourcesInput): Promise<void> {
  await deleteUserBucket(userId);
  await deleteUserVectors(userId);
}

/** Removes what's stored for ingested documents. Started by the UI as it deletes their rows. */
export async function cleanupDocuments({
  userId,
  documentIds,
}: CleanupDocumentsInput): Promise<void> {
  await deleteDocumentObjects(userId, documentIds);
  await deleteDocumentVectors(documentIds);
}
